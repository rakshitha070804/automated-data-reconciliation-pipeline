"""Record-level validation. Invalid rows are returned for quarantine."""
import pandas as pd

def validate_records(df: pd.DataFrame, source_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    work = df.copy()
    work["_source_dataset"] = source_name
    work["_reject_reason"] = ""

    required = ["order_id", "customer_id", "product_name", "quantity", "amount", "order_date"]
    for col in required:
        bad = work[col].isna() | work[col].astype("string").str.strip().eq("")
        work.loc[bad, "_reject_reason"] += f"missing_{col};"

    for col in ["order_id", "customer_id", "quantity"]:
        numeric = pd.to_numeric(work[col], errors="coerce")
        bad = numeric.isna() | (numeric % 1 != 0)
        work.loc[bad & work["_reject_reason"].eq(""), "_reject_reason"] += f"invalid_{col};"
        work[col] = numeric

    amount = pd.to_numeric(work["amount"], errors="coerce")
    bad_amount = amount.isna() | (amount < 0)
    work.loc[bad_amount & work["_reject_reason"].eq(""), "_reject_reason"] += "invalid_amount;"
    work["amount"] = amount

    bad_quantity = pd.to_numeric(work["quantity"], errors="coerce").fillna(0) <= 0
    work.loc[bad_quantity & work["_reject_reason"].eq(""), "_reject_reason"] += "quantity_must_be_positive;"

    dates = pd.to_datetime(work["order_date"], errors="coerce", format="%Y-%m-%d")
    work.loc[dates.isna() & work["_reject_reason"].eq(""), "_reject_reason"] += "invalid_order_date;"
    work["order_date"] = dates.dt.strftime("%Y-%m-%d")

    # A customer reference must be a positive integer.
    bad_customer = pd.to_numeric(work["customer_id"], errors="coerce").fillna(0) <= 0
    work.loc[bad_customer & work["_reject_reason"].eq(""), "_reject_reason"] += "invalid_customer_reference;"

    rejected = work[work["_reject_reason"].ne("")].copy()
    valid = work[work["_reject_reason"].eq("")].drop(columns=["_reject_reason"]).copy()
    rejected["_reject_reason"] = rejected["_reject_reason"].str.rstrip(";")
    return valid, rejected
