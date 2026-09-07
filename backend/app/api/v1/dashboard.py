from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.models import Document, ExtractedRecord, ExtractedField, ValidationResult
from app.schemas.schemas import DashboardStatsResponse

router = APIRouter()

@router.get("/statistics", response_model=DashboardStatsResponse)
async def get_dashboard_statistics(db: AsyncSession = Depends(get_db)):
    # Total documents
    doc_res = await db.execute(select(Document))
    docs = doc_res.scalars().all()
    
    total_docs = len(docs)
    processed_docs = sum(1 for d in docs if d.status in ["completed", "failed"])
    success_docs = sum(1 for d in docs if d.status == "completed")
    failed_docs = sum(1 for d in docs if d.status == "failed")

    # Records
    rec_res = await db.execute(select(ExtractedRecord))
    records = rec_res.scalars().all()
    
    total_recs = len(records)
    high_conf_recs = sum(1 for r in records if (r.extraction_confidence or 0.0) >= 0.90)
    low_conf_recs = sum(1 for r in records if (r.extraction_confidence or 0.0) < 0.70)
    needing_verification = sum(1 for r in records if r.verification_status == "UNVERIFIED")
    verified_recs = sum(1 for r in records if r.verification_status == "VERIFIED")

    # Validation Errors
    val_res = await db.execute(select(ValidationResult))
    val_issues = val_res.scalars().all()
    val_errors_count = sum(1 for v in val_issues if v.status in ["INVALID", "WARNING"])

    # Distributions
    states_dict = {}
    districts_dict = {}
    langs_dict = {}
    val_status_dict = {}
    conf_dict = {"HIGH (>=0.90)": 0, "MEDIUM (0.70-0.89)": 0, "LOW (<0.70)": 0}
    error_types_dict = {}

    for r in records:
        st = r.state or "Unspecified State"
        states_dict[st] = states_dict.get(st, 0) + 1

        dt = r.district or "Unspecified District"
        districts_dict[dt] = districts_dict.get(dt, 0) + 1

        lg = r.language or "en"
        langs_dict[lg] = langs_dict.get(lg, 0) + 1

        vs = r.validation_status or "UNVERIFIED"
        val_status_dict[vs] = val_status_dict.get(vs, 0) + 1

        conf = r.extraction_confidence or 0.0
        if conf >= 0.90:
            conf_dict["HIGH (>=0.90)"] += 1
        elif conf >= 0.70:
            conf_dict["MEDIUM (0.70-0.89)"] += 1
        else:
            conf_dict["LOW (<0.70)"] += 1

    for v in val_issues:
        tp = v.validation_type or "general"
        error_types_dict[tp] = error_types_dict.get(tp, 0) + 1

    return DashboardStatsResponse(
        total_documents=total_docs,
        documents_processed=processed_docs,
        documents_success=success_docs,
        documents_failed=failed_docs,
        total_records=total_recs,
        high_confidence_records=high_conf_recs,
        low_confidence_records=low_conf_recs,
        records_needing_verification=needing_verification,
        validation_errors_count=val_errors_count,
        verified_records_count=verified_recs,
        exported_records_count=verified_recs,
        state_distribution=states_dict,
        district_distribution=districts_dict,
        language_distribution=langs_dict,
        validation_status_distribution=val_status_dict,
        confidence_distribution=conf_dict,
        error_types=error_types_dict
    )
