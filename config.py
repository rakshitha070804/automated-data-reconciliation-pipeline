from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
SOURCE_PATH = DATA_DIR / "source.csv"
TARGET_PATH = DATA_DIR / "target.csv"
BUSINESS_KEY = "order_id"
REQUIRED_COLUMNS = [
    "order_id", "customer_id", "product_name", "quantity", "amount", "order_date"
]
DATE_FORMAT = "%Y-%m-%d"
