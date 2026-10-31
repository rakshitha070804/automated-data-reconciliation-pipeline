from config import SOURCE_PATH, TARGET_PATH, OUTPUT_DIR
from src.pipeline import run_pipeline

if __name__ == "__main__":
    result = run_pipeline(SOURCE_PATH, TARGET_PATH, OUTPUT_DIR)
    print("Pipeline status:", result["status"])
    print("Report:", OUTPUT_DIR / "reconciliation_report.json")
