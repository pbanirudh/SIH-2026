from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.models import ExtractedRecord, Document, OCRResult
from app.services.export.csv_exporter import CSVExporterService

router = APIRouter()

@router.get("/csv")
async def export_all_csv(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ExtractedRecord))
    records = result.scalars().all()
    
    docs_res = await db.execute(select(Document))
    docs_map = {d.id: d.original_filename for d in docs_res.scalars().all()}

    rec_dicts = []
    for r in records:
        d_dict = {
            "record_id": r.id,
            "document_id": r.document_id,
            "document_name": docs_map.get(r.document_id, "Unknown"),
            "document_type": r.document_type,
            "state": r.state,
            "district": r.district,
            "tehsil": r.tehsil,
            "taluk": r.taluk,
            "village": r.village,
            "ward": r.ward,
            "owner_name": r.owner_name,
            "co_owner_names": r.co_owner_names,
            "parent_name": r.parent_name,
            "ownership_type": r.ownership_type,
            "ownership_share": r.ownership_share,
            "survey_number": r.survey_number,
            "sub_survey_number": r.sub_survey_number,
            "khasra_number": r.khasra_number,
            "khata_number": r.khata_number,
            "plot_number": r.plot_number,
            "patta_number": r.patta_number,
            "parcel_id": r.parcel_id,
            "area": r.area,
            "area_unit": r.area_unit,
            "land_classification": r.land_classification,
            "land_type": r.land_type,
            "irrigation_status": r.irrigation_status,
            "land_use": r.land_use,
            "mutation_number": r.mutation_number,
            "mutation_date": r.mutation_date,
            "mutation_type": r.mutation_type,
            "previous_owner": r.previous_owner,
            "new_owner": r.new_owner,
            "registration_number": r.registration_number,
            "registration_date": r.registration_date,
            "deed_number": r.deed_number,
            "transaction_type": r.transaction_type,
            "record_date": r.record_date,
            "source_department": r.source_department,
            "language": r.language,
            "ocr_engine": r.ocr_engine,
            "ocr_confidence": r.ocr_confidence,
            "extraction_confidence": r.extraction_confidence,
            "validation_status": r.validation_status,
            "verification_status": r.verification_status,
            "remarks": r.remarks
        }
        rec_dicts.append(d_dict)

    csv_bytes = CSVExporterService.generate_records_csv(rec_dicts)
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=land_records_all.csv"}
    )

@router.get("/verified-csv")
async def export_verified_csv(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ExtractedRecord).where(ExtractedRecord.verification_status == "VERIFIED"))
    records = result.scalars().all()
    
    docs_res = await db.execute(select(Document))
    docs_map = {d.id: d.original_filename for d in docs_res.scalars().all()}

    rec_dicts = []
    for r in records:
        d_dict = {
            "record_id": r.id,
            "document_id": r.document_id,
            "document_name": docs_map.get(r.document_id, "Unknown"),
            "document_type": r.document_type,
            "state": r.state,
            "district": r.district,
            "tehsil": r.tehsil,
            "taluk": r.taluk,
            "village": r.village,
            "ward": r.ward,
            "owner_name": r.owner_name,
            "co_owner_names": r.co_owner_names,
            "parent_name": r.parent_name,
            "ownership_type": r.ownership_type,
            "ownership_share": r.ownership_share,
            "survey_number": r.survey_number,
            "sub_survey_number": r.sub_survey_number,
            "khasra_number": r.khasra_number,
            "khata_number": r.khata_number,
            "plot_number": r.plot_number,
            "patta_number": r.patta_number,
            "parcel_id": r.parcel_id,
            "area": r.area,
            "area_unit": r.area_unit,
            "land_classification": r.land_classification,
            "land_type": r.land_type,
            "irrigation_status": r.irrigation_status,
            "land_use": r.land_use,
            "mutation_number": r.mutation_number,
            "mutation_date": r.mutation_date,
            "mutation_type": r.mutation_type,
            "previous_owner": r.previous_owner,
            "new_owner": r.new_owner,
            "registration_number": r.registration_number,
            "registration_date": r.registration_date,
            "deed_number": r.deed_number,
            "transaction_type": r.transaction_type,
            "record_date": r.record_date,
            "source_department": r.source_department,
            "language": r.language,
            "ocr_engine": r.ocr_engine,
            "ocr_confidence": r.ocr_confidence,
            "extraction_confidence": r.extraction_confidence,
            "validation_status": r.validation_status,
            "verification_status": r.verification_status,
            "remarks": r.remarks
        }
        rec_dicts.append(d_dict)

    csv_bytes = CSVExporterService.generate_records_csv(rec_dicts)
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=land_records_verified.csv"}
    )

@router.get("/errors-csv")
async def export_errors_csv(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ExtractedRecord).where(ExtractedRecord.validation_status.in_(["INVALID", "WARNING"])))
    records = result.scalars().all()
    
    docs_res = await db.execute(select(Document))
    docs_map = {d.id: d.original_filename for d in docs_res.scalars().all()}

    rec_dicts = []
    for r in records:
        d_dict = {
            "record_id": r.id,
            "document_id": r.document_id,
            "document_name": docs_map.get(r.document_id, "Unknown"),
            "document_type": r.document_type,
            "state": r.state,
            "district": r.district,
            "tehsil": r.tehsil,
            "taluk": r.taluk,
            "village": r.village,
            "ward": r.ward,
            "owner_name": r.owner_name,
            "co_owner_names": r.co_owner_names,
            "parent_name": r.parent_name,
            "ownership_type": r.ownership_type,
            "ownership_share": r.ownership_share,
            "survey_number": r.survey_number,
            "sub_survey_number": r.sub_survey_number,
            "khasra_number": r.khasra_number,
            "khata_number": r.khata_number,
            "plot_number": r.plot_number,
            "patta_number": r.patta_number,
            "parcel_id": r.parcel_id,
            "area": r.area,
            "area_unit": r.area_unit,
            "land_classification": r.land_classification,
            "land_type": r.land_type,
            "irrigation_status": r.irrigation_status,
            "land_use": r.land_use,
            "mutation_number": r.mutation_number,
            "mutation_date": r.mutation_date,
            "mutation_type": r.mutation_type,
            "previous_owner": r.previous_owner,
            "new_owner": r.new_owner,
            "registration_number": r.registration_number,
            "registration_date": r.registration_date,
            "deed_number": r.deed_number,
            "transaction_type": r.transaction_type,
            "record_date": r.record_date,
            "source_department": r.source_department,
            "language": r.language,
            "ocr_engine": r.ocr_engine,
            "ocr_confidence": r.ocr_confidence,
            "extraction_confidence": r.extraction_confidence,
            "validation_status": r.validation_status,
            "verification_status": r.verification_status,
            "remarks": r.remarks
        }
        rec_dicts.append(d_dict)

    csv_bytes = CSVExporterService.generate_records_csv(rec_dicts)
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=land_records_validation_errors.csv"}
    )

@router.get("/ocr-csv")
async def export_ocr_csv(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OCRResult))
    ocr_list = result.scalars().all()
    ocr_dicts = [
        {
            "document_id": o.document_id,
            "page_number": o.page_number,
            "engine_used": o.engine_used,
            "language": o.language,
            "detected_text": o.detected_text,
            "confidence": o.confidence,
            "is_handwritten": o.is_handwritten,
            "bounding_boxes_json": o.bounding_boxes_json
        }
        for o in ocr_list
    ]
    csv_bytes = CSVExporterService.generate_ocr_csv(ocr_dicts)
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=land_records_raw_ocr.csv"}
    )
