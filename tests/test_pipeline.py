import pandas as pd
from src.pipeline import run_pipeline

COLS = ["order_id","customer_id","product_name","quantity","amount","order_date"]

def test_pipeline_and_rerun(tmp_path):
    source = pd.DataFrame([[1,1,"Book",1,100,"2026-01-01"]], columns=COLS)
    target = source.copy()
    sp, tp = tmp_path/"source.csv", tmp_path/"target.csv"
    source.to_csv(sp, index=False); target.to_csv(tp, index=False)
    first = run_pipeline(sp, tp, tmp_path/"out", run_id="same_run")
    second = run_pipeline(sp, tp, tmp_path/"out", run_id="same_run")
    assert first["matched_count"] == second["matched_count"] == 1
    assert first["status"] == "PASSED"

def test_empty_files(tmp_path):
    sp, tp = tmp_path/"source.csv", tmp_path/"target.csv"
    pd.DataFrame(columns=COLS).to_csv(sp, index=False)
    pd.DataFrame(columns=COLS).to_csv(tp, index=False)
    result = run_pipeline(sp, tp, tmp_path/"out")
    assert result["source_input_count"] == 0
    assert result["status"] == "PASSED"
