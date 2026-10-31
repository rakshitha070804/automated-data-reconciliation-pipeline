"""Business-key and field-level comparison."""
import pandas as pd

COMPARE_COLUMNS = ["customer_id", "product_name", "quantity", "amount", "order_date"]

def reconcile(source: pd.DataFrame, target: pd.DataFrame, key: str = "order_id") -> dict:
    src = source.set_index(key, drop=False)
    tgt = target.set_index(key, drop=False)
    src_keys, tgt_keys = set(src.index), set(tgt.index)
    missing_keys = sorted(src_keys - tgt_keys)
    extra_keys = sorted(tgt_keys - src_keys)
    common_keys = sorted(src_keys & tgt_keys)

    matched_rows, mismatch_rows = [], []
    for record_id in common_keys:
        differences = {}
        for col in COMPARE_COLUMNS:
            left, right = src.loc[record_id, col], tgt.loc[record_id, col]
            if pd.isna(left) and pd.isna(right):
                continue
            if left != right:
                differences[col] = {"source": left.item() if hasattr(left, "item") else left,
                                    "target": right.item() if hasattr(right, "item") else right}
        if differences:
            mismatch_rows.append({"order_id": record_id, "mismatch_fields": ";".join(differences),
                                  "details": str(differences)})
        else:
            matched_rows.append(src.loc[record_id].to_dict())

    return {
        "matched": pd.DataFrame(matched_rows),
        "field_mismatches": pd.DataFrame(mismatch_rows, columns=["order_id", "mismatch_fields", "details"]),
        "missing_in_target": src.loc[missing_keys].reset_index(drop=True) if missing_keys else pd.DataFrame(columns=source.columns),
        "extra_in_target": tgt.loc[extra_keys].reset_index(drop=True) if extra_keys else pd.DataFrame(columns=target.columns),
        "source_count": len(source), "target_count": len(target),
        "matched_count": len(matched_rows), "field_mismatch_count": len(mismatch_rows),
        "missing_in_target_count": len(missing_keys), "extra_in_target_count": len(extra_keys),
        "source_amount_total": round(float(source["amount"].sum()), 2) if not source.empty else 0.0,
        "target_amount_total": round(float(target["amount"].sum()), 2) if not target.empty else 0.0,
    }
