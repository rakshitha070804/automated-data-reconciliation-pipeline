"""Write machine-readable and human-inspectable outputs."""
from pathlib import Path
import json
import pandas as pd

def write_csv(df: pd.DataFrame, path: Path):
    df.to_csv(path, index=False)

def write_report(report: dict, path: Path):
    path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
