import pytest
from app.services.validation.validation_engine import ValidationEngine

def test_area_format_validation():
    valid_record = {"area": 2.35, "village": "Wagholi"}
    status, issues = ValidationEngine.validate_record(valid_record)
    assert any(i["rule_name"] == "positive_numeric_area" and i["status"] == "VALID" for i in issues)

    invalid_record = {"area": -5.0}
    status, issues = ValidationEngine.validate_record(invalid_record)
    assert status == "INVALID"
    assert any(i["rule_name"] == "positive_numeric_area" and i["status"] == "INVALID" for i in issues)

def test_date_format_validation():
    rec = {"mutation_date": "15/04/2024"}
    status, issues = ValidationEngine.validate_record(rec)
    assert not any(i["rule_name"] == "date_format_check" for i in issues)

    bad_date_rec = {"mutation_date": "invalid_date_str"}
    status, issues = ValidationEngine.validate_record(bad_date_rec)
    assert any(i["rule_name"] == "date_format_check" and i["status"] == "WARNING" for i in issues)

def test_duplicate_record_detection():
    existing = [{"survey_number": "123/4", "khasra_number": None, "village": "wagholi"}]
    new_dup = {"survey_number": "123/4", "village": "Wagholi"}
    status, issues = ValidationEngine.validate_record(new_dup, existing_records=existing)
    assert any(i["rule_name"] == "duplicate_record_check" and i["status"] == "WARNING" for i in issues)
