"""CSV ingestion with explicit schema checks."""
from pathlib import Path
import pandas as pd

EXPECTED_COLUMNS = ["order_id", "customer_id", "product_name", "quantity", "amount", "order_date"]

class SchemaError(ValueError):
    pass

def read_dataset(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    try:
        df = pd.read_csv(path, dtype={"product_name": "string", "order_date": "string"})
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)
    missing = sorted(set(EXPECTED_COLUMNS) - set(df.columns))
    unexpected = sorted(set(df.columns) - set(EXPECTED_COLUMNS))
    if missing or unexpected:
        raise SchemaError(f"Schema mismatch. Missing columns={missing}; unexpected columns={unexpected}")
    return df[EXPECTED_COLUMNS]
