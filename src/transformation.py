"""Deterministic type normalization and duplicate-key handling."""
import pandas as pd

def normalize_records(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    if result.empty:
        return result
    result["order_id"] = pd.to_numeric(result["order_id"]).astype("int64")
    result["customer_id"] = pd.to_numeric(result["customer_id"]).astype("int64")
    result["quantity"] = pd.to_numeric(result["quantity"]).astype("int64")
    result["amount"] = pd.to_numeric(result["amount"]).round(2)
    result["product_name"] = result["product_name"].astype("string").str.strip()
    result["order_date"] = pd.to_datetime(result["order_date"]).dt.strftime("%Y-%m-%d")
    return result.sort_values("order_id").reset_index(drop=True)

def split_duplicates(df: pd.DataFrame, key: str = "order_id"):
    duplicates = df[df.duplicated(subset=[key], keep="first")].copy()
    unique = df.drop_duplicates(subset=[key], keep="first").copy()
    if not duplicates.empty:
        duplicates["reject_reason"] = f"duplicate_{key}"
    return unique, duplicates
