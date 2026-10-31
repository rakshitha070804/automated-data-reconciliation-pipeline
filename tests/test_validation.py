from src.validation import validate_records

def test_valid_and_missing_required(sample):
    valid, rejected = validate_records(sample, "source")
    assert len(valid) == 3
    broken = sample.copy()
    broken.loc[0, "product_name"] = None
    valid, rejected = validate_records(broken, "source")
    assert len(rejected) == 1
    assert "missing_product_name" in rejected.iloc[0]["_reject_reason"]

def test_negative_amount_rejected(sample):
    sample.loc[0, "amount"] = -1
    valid, rejected = validate_records(sample, "source")
    assert len(rejected) == 1
