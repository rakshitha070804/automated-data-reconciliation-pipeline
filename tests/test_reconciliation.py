from src.reconciliation import reconcile
from src.transformation import normalize_records, split_duplicates

def test_happy_path(sample):
    result = reconcile(normalize_records(sample), normalize_records(sample.copy()))
    assert result["matched_count"] == 3
    assert result["field_mismatch_count"] == 0

def test_field_mismatch_and_missing_extra(sample):
    target = sample.iloc[:2].copy()
    target.loc[target["order_id"] == 102, "amount"] = 999
    target.loc[len(target)] = [104, 4, "Mouse", 1, 500, "2026-10-04"]
    result = reconcile(normalize_records(sample), normalize_records(target))
    assert result["field_mismatch_count"] == 1
    assert result["missing_in_target_count"] == 1
    assert result["extra_in_target_count"] == 1

def test_duplicate_key(sample):
    duplicate = sample.iloc[[0]].copy()
    combined = __import__("pandas").concat([sample, duplicate], ignore_index=True)
    unique, dupes = split_duplicates(normalize_records(combined))
    assert len(unique) == 3
    assert len(dupes) == 1
