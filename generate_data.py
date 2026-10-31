"""Create reproducible sample data or a scalable synthetic batch."""
import argparse
from pathlib import Path
import random
import pandas as pd

COLUMNS = ["order_id", "customer_id", "product_name", "quantity", "amount", "order_date"]
PRODUCTS = ["Laptop", "Mobile", "Keyboard", "Mouse", "Monitor"]

def generate(rows: int, output: Path, seed: int = 42):
    random.seed(seed)
    records = []
    for i in range(rows):
        quantity = random.randint(1, 5)
        unit_price = random.choice([500, 1000, 2000, 15000, 50000])
        records.append([i + 1, random.randint(1, max(2, rows // 3)), random.choice(PRODUCTS),
                        quantity, round(quantity * unit_price, 2),
                        f"2026-{random.randint(1,12):02d}-{random.randint(1,28):02d}"])
    df = pd.DataFrame(records, columns=COLUMNS)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    return df

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=100)
    parser.add_argument("--output", default="data/source.csv")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    generate(args.rows, Path(args.output), args.seed)

if __name__ == "__main__":
    main()
