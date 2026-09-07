import pytest
from app.services.export.csv_exporter import CSVExporterService

def test_csv_export_utf8_bom():
    sample_records = [
        {
            "record_id": "rec-101",
            "document_id": "doc-1",
            "document_name": "sample_record.png",
            "owner_name": "रमेश कुमार",  # Hindi name
            "survey_number": "123/4A",
            "area": 2.35,
            "state": "Maharashtra",
            "district": "Pune",
            "village": "Wagholi",
            "validation_status": "VALID",
            "verification_status": "VERIFIED"
        }
    ]

    csv_bytes = CSVExporterService.generate_records_csv(sample_records)
    
    # Verify UTF-8 BOM prefix
    assert csv_bytes.startswith(b'\xef\xbb\xbf')
    
    # Decode string and verify headers and Indian Unicode content
    decoded = csv_bytes.decode("utf-8-sig")
    assert "record_id" in decoded
    assert "owner_name" in decoded
    assert "रमेश कुमार" in decoded
    assert "123/4A" in decoded
