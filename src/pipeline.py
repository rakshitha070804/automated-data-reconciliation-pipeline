"""End-to-end reconciliation pipeline. Outputs are overwritten per run_id (safe rerun)."""
from pathlib import Path
from datetime import datetime, timezone
import json, logging, time, uuid
import pandas as pd
from .ingestion import read_dataset
from .validation import validate_records
from .transformation import normalize_records, split_duplicates
from .reconciliation import reconcile
from .reporting import write_csv, write_report

def run_pipeline(source_path, target_path, output_dir, run_id=None):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    log_dir = output_dir / "run_logs"
    log_dir.mkdir(exist_ok=True)
    run_id = run_id or "run_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:6]
    started = datetime.now(timezone.utc)
    start_clock = time.perf_counter()
    logger = logging.getLogger(f"reconciliation.{run_id}")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(log_dir / f"{run_id}.log", encoding="utf-8")
    logger.addHandler(handler)

    try:
        source_raw = read_dataset(source_path)
        target_raw = read_dataset(target_path)
        source_valid, source_rejects = validate_records(source_raw, "source")
        target_valid, target_rejects = validate_records(target_raw, "target")
        source_valid = normalize_records(source_valid)
        target_valid = normalize_records(target_valid)
        source_valid, source_dupes = split_duplicates(source_valid)
        target_valid, target_dupes = split_duplicates(target_valid)
        rejects = pd.concat([source_rejects, target_rejects], ignore_index=True, sort=False)
        rejects = pd.concat([rejects, source_dupes, target_dupes], ignore_index=True, sort=False)

        result = reconcile(source_valid, target_valid)
        elapsed = round(time.perf_counter() - start_clock, 4)
        finished = datetime.now(timezone.utc)
        status = "PASSED" if (result["field_mismatch_count"] == 0 and result["missing_in_target_count"] == 0
                              and result["extra_in_target_count"] == 0 and rejects.empty) else "COMPLETED_WITH_ISSUES"
        report = {
            "run_id": run_id, "status": status,
            "started_at": started.isoformat(), "finished_at": finished.isoformat(),
            "source_file": str(source_path), "target_file": str(target_path),
            "source_input_count": len(source_raw), "target_input_count": len(target_raw),
            "source_valid_count": len(source_valid), "target_valid_count": len(target_valid),
            "matched_count": result["matched_count"],
            "field_mismatch_count": result["field_mismatch_count"],
            "missing_in_target_count": result["missing_in_target_count"],
            "extra_in_target_count": result["extra_in_target_count"],
            "rejected_count": len(rejects),
            "source_amount_total": result["source_amount_total"],
            "target_amount_total": result["target_amount_total"],
            "amount_total_difference": round(result["target_amount_total"] - result["source_amount_total"], 2),
            "duration_seconds": elapsed,
            "failure_reason": None
        }
        write_csv(result["matched"], output_dir / "matched_records.csv")
        write_csv(result["field_mismatches"], output_dir / "mismatched_records.csv")
        write_csv(result["missing_in_target"], output_dir / "missing_in_target.csv")
        write_csv(result["extra_in_target"], output_dir / "extra_in_target.csv")
        write_csv(rejects, output_dir / "rejected_records.csv")
        write_report(report, output_dir / "reconciliation_report.json")
        logger.info(json.dumps(report))
        handler.close()
        return report
    except Exception as exc:
        report = {"run_id": run_id, "status": "FAILED", "failure_reason": str(exc),
                  "started_at": started.isoformat(), "finished_at": datetime.now(timezone.utc).isoformat()}
        write_report(report, output_dir / "reconciliation_report.json")
        logger.exception("Pipeline failed: %s", exc)
        handler.close()
        raise
