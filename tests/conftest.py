import pandas as pd
import pytest

@pytest.fixture
def sample():
    return pd.DataFrame([
        [101, 1, "Laptop", 1, 50000.0, "2026-10-01"],
        [102, 2, "Mobile", 2, 30000.0, "2026-10-02"],
        [103, 3, "Keyboard", 1, 2000.0, "2026-10-03"],
    ], columns=["order_id","customer_id","product_name","quantity","amount","order_date"])
