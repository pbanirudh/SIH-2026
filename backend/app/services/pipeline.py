import os
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Document, DocumentPage, OCRResult, ExtractedRecord, ExtractedField, ValidationResult, ProcessingJob
from app.services.preprocessing import PreprocessingService
from app.services.ocr.paddle_engine import PaddleOCREngine
from app.services.ocr.trocr_engine import IndicTrOCREngine
from app.services.ocr.layout_parser import LayoutParserService
from app.services.nlp.entity_extractor import EntityExtractor
from app.services.scoring.confidence import ConfidenceScoringEngine
from app.services.validation.validation_engine import ValidationEngine

paddle_ocr = PaddleOCREngine()
trocr_engine = IndicTrOCREngine()

class DigitizationPipelineService:

    @staticmethod
    async def process_document_pipeline(document_id: str, db: AsyncSession):
        """
        Executes complete 12-stage land record processing pipeline.
        """
        doc = await db.get(Document, document_id)
        if not doc:
            return

        try:
            # Stage 1: Update status to preprocessing
            doc.status = "preprocessing"
            await DigitizationPipelineService._update_job(db, document_id, "preprocessing", "in_progress", 10.0, "Preprocessing image/PDF pages")
            await db.commit()

            processed_image_paths, has_selectable_text, direct_pages = PreprocessingService.process_document(
                doc.storage_path, doc.id
            )

            doc.total_pages = len(processed_image_paths)
            
            # Save pages
            for idx, img_p in enumerate(processed_image_paths):
                dp = DocumentPage(
                    document_id=doc.id,
                    page_number=idx + 1,
                    image_path=img_p,
                    has_selectable_text=has_selectable_text
                )
                db.add(dp)
            await db.commit()

            # Stage 2: OCR & Layout Parsing
            doc.status = "ocr_processing"
            await DigitizationPipelineService._update_job(db, document_id, "ocr", "in_progress", 40.0, "Performing PaddleOCR and handwriting recognition")
            await db.commit()

            all_page_ocr_texts = []
            all_page_boxes = []
            overall_ocr_conf = 0.0

            for idx, img_p in enumerate(processed_image_paths):
                if has_selectable_text and idx < len(direct_pages):
                    ocr_res = {
                        "engine": "PyMuPDF-DirectText",
                        "language": doc.expected_language or "en",
                        "full_text": direct_pages[idx]["text"],
                        "confidence": 0.98,
                        "bounding_boxes": []
                    }
                else:
                    ocr_res = paddle_ocr.process_image(img_p, doc.expected_language or "en")

                ocr_db = OCRResult(
                    document_id=doc.id,
                    page_number=idx + 1,
                    engine_used=ocr_res["engine"],
                    language=ocr_res["language"],
                    detected_text=ocr_res["full_text"],
                    confidence=ocr_res["confidence"],
                    bounding_boxes_json=ocr_res["bounding_boxes"]
                )
                db.add(ocr_db)

                all_page_ocr_texts.append(ocr_res["full_text"])
                all_page_boxes.extend(ocr_res["bounding_boxes"])
                overall_ocr_conf += ocr_res["confidence"]

            combined_ocr_text = "\n".join(all_page_ocr_texts)
            avg_ocr_conf = round(overall_ocr_conf / max(len(processed_image_paths), 1), 4)
            await db.commit()

            # Stage 3: Layout Analysis
            await DigitizationPipelineService._update_job(db, document_id, "layout", "in_progress", 60.0, "Analyzing layout and label-value pairs")
            layout_data = LayoutParserService.analyze_layout(combined_ocr_text, all_page_boxes)

            # Stage 4: NLP Entity Extraction & Mapping
            doc.status = "nlp_extracting"
            await DigitizationPipelineService._update_job(db, document_id, "nlp", "in_progress", 75.0, "Extracting land record entities")
            extracted_entities = EntityExtractor.extract_entities(
                combined_ocr_text, layout_data["label_value_pairs"], all_page_boxes
            )

            # Build record fields dictionary
            record_dict = {
                "document_id": doc.id,
                "document_type": extracted_entities["document_type"][0],
                "language": doc.expected_language or "en",
                "ocr_engine": "PaddleOCR",
                "ocr_confidence": avg_ocr_conf,
            }

            for field_key, (val, nlp_conf) in extracted_entities.items():
                if field_key != "document_type":
                    record_dict[field_key] = val

            # Stage 5: Validation Engine
            doc.status = "validating"
            await DigitizationPipelineService._update_job(db, document_id, "validation", "in_progress", 88.0, "Running format and logical validation")
            
            # Fetch existing records for duplicate check
            existing_res = await db.execute(select(ExtractedRecord))
            existing_records = [
                {"survey_number": r.survey_number, "khasra_number": r.khasra_number, "village": r.village}
                for r in existing_res.scalars().all()
            ]

            val_status, val_issues = ValidationEngine.validate_record(record_dict, existing_records)
            record_dict["validation_status"] = val_status
            record_dict["verification_status"] = "UNVERIFIED"

            # Compute overall extraction confidence
            field_confs = [nlp_conf for _, (_, nlp_conf) in extracted_entities.items() if nlp_conf > 0]
            avg_extraction_conf = round(sum(field_confs) / max(len(field_confs), 1), 4) if field_confs else 0.5
            record_dict["extraction_confidence"] = avg_extraction_conf

            # Save Extracted Record
            record_obj = ExtractedRecord(**record_dict)
            db.add(record_obj)
            await db.flush()

            # Save Extracted Fields with confidence scoring
            for field_name, (val, nlp_conf) in extracted_entities.items():
                if field_name == "document_type":
                    continue
                
                final_conf, conf_cat = ConfidenceScoringEngine.calculate_field_confidence(
                    avg_ocr_conf, nlp_conf, is_format_valid=True
                )

                # raw_ocr_text: use layout pair if available, else snippet of combined OCR text
                layout_pair_val = layout_data["label_value_pairs"].get(field_name, "")
                if val is not None and not layout_pair_val:
                    # Extract a snippet around the value from combined OCR text
                    val_str = str(val)
                    idx_in_text = combined_ocr_text.find(val_str)
                    if idx_in_text >= 0:
                        start = max(0, idx_in_text - 20)
                        end = min(len(combined_ocr_text), idx_in_text + len(val_str) + 20)
                        raw_ctx = f"…{combined_ocr_text[start:end].strip()}…"
                    else:
                        raw_ctx = f"OCR detected: {val_str}"
                else:
                    raw_ctx = layout_pair_val

                field_obj = ExtractedField(
                    record_id=record_obj.id,
                    field_name=field_name,
                    field_value=str(val) if val is not None else None,
                    source_page=1,
                    raw_ocr_text=raw_ctx,
                    ocr_confidence=avg_ocr_conf,
                    nlp_confidence=nlp_conf,
                    final_confidence=final_conf,
                    confidence_category=conf_cat if val is not None else "LOW",
                    validation_status="VALID" if val is not None else "UNVERIFIED",
                    original_ai_value=str(val) if val is not None else None,
                    is_verified=False
                )
                db.add(field_obj)

            # Save Validation Issues
            for issue in val_issues:
                v_res = ValidationResult(
                    record_id=record_obj.id,
                    field_name=issue.get("field_name"),
                    rule_name=issue["rule_name"],
                    validation_type=issue["validation_type"],
                    status=issue["status"],
                    message=issue["message"]
                )
                db.add(v_res)

            # Stage 6: Completion
            doc.status = "completed"
            await DigitizationPipelineService._update_job(db, document_id, "export", "completed", 100.0, "Document processing completed successfully")
            await db.commit()

        except Exception as e:
            await db.rollback()
            doc.status = "failed"
            doc.error_message = str(e)
            await DigitizationPipelineService._update_job(db, document_id, "failed", "failed", 0.0, f"Error: {str(e)}")
            await db.commit()

    @staticmethod
    async def _update_job(db: AsyncSession, doc_id: str, stage: str, status: str, progress: float, msg: str):
        job = ProcessingJob(
            document_id=doc_id,
            stage=stage,
            status=status,
            progress_pct=progress,
            message=msg,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow() if status == "completed" else None
        )
        db.add(job)
