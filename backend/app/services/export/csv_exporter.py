import io
import csv
from typing import List, Dict, Any, Optional

class CSVExporterService:
    COLUMNS = [
        "record_id", "document_id", "document_name", "document_type",
        "state", "district", "tehsil", "taluk", "village", "ward",
        "owner_name", "co_owner_names", "parent_name", "ownership_type", "ownership_share",
        "survey_number", "sub_survey_number", "khasra_number", "khata_number",
        "plot_number", "patta_number", "parcel_id",
        "area", "area_unit", "land_classification", "land_type", "irrigation_status", "land_use",
        "mutation_number", "mutation_date", "mutation_type", "previous_owner", "new_owner",
        "registration_number", "registration_date", "deed_number", "transaction_type",
        "record_date", "source_department", "language", "ocr_engine",
        "ocr_confidence", "extraction_confidence", "validation_status", "verification_status", "remarks"
    ]

    @staticmethod
    def generate_records_csv(records: List[Dict[str, Any]]) -> bytes:
        """
        Generates CSV byte stream formatted with UTF-8 BOM (utf-8-sig) for Microsoft Excel Indian script support.
        """
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=CSVExporterService.COLUMNS, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()

        for rec in records:
            row = {}
            for col in CSVExporterService.COLUMNS:
                val = rec.get(col)
                if val is None:
                    row[col] = ""
                elif isinstance(val, float):
                    row[col] = f"{val:.4f}".rstrip("0").rstrip(".") if val != 0 else "0"
                else:
                    row[col] = str(val)
            writer.writerow(row)

        csv_str = output.getvalue()
        # Encode as UTF-8 BOM
        return csv_str.encode("utf-8-sig")

    @staticmethod
    def generate_ocr_csv(ocr_results: List[Dict[str, Any]]) -> bytes:
        """Exports document page OCR bounding boxes and raw text."""
        output = io.StringIO()
        fieldnames = ["document_id", "page_number", "engine_used", "language", "box_text", "confidence", "is_handwritten", "box_coordinates"]
        writer = csv.DictWriter(output, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()

        for res in ocr_results:
            boxes = res.get("bounding_boxes_json") or []
            doc_id = res.get("document_id", "")
            page_num = res.get("page_number", 1)
            engine = res.get("engine_used", "")
            lang = res.get("language", "en")

            if not boxes and res.get("detected_text"):
                writer.writerow({
                    "document_id": doc_id,
                    "page_number": page_num,
                    "engine_used": engine,
                    "language": lang,
                    "box_text": res.get("detected_text"),
                    "confidence": res.get("confidence", 0.0),
                    "is_handwritten": res.get("is_handwritten", False),
                    "box_coordinates": ""
                })
            else:
                for b in boxes:
                    writer.writerow({
                        "document_id": doc_id,
                        "page_number": page_num,
                        "engine_used": engine,
                        "language": lang,
                        "box_text": b.get("text", ""),
                        "confidence": b.get("confidence", 0.0),
                        "is_handwritten": b.get("is_handwritten", False),
                        "box_coordinates": str(b.get("box", ""))
                    })

        return output.getvalue().encode("utf-8-sig")
