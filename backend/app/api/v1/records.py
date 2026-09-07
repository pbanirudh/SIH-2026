from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.models import ExtractedRecord, ExtractedField, VerificationAction, FeedbackItem, AuditLog, User
from app.schemas.schemas import ExtractedRecordResponse, RecordVerificationRequest
from app.api.deps import get_current_user

router = APIRouter()

@router.get("", response_model=List[ExtractedRecordResponse])
async def list_records(
    skip: int = 0,
    limit: int = 50,
    verification_status: Optional[str] = None,
    validation_status: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(ExtractedRecord).options(
        selectinload(ExtractedRecord.fields),
        selectinload(ExtractedRecord.validations)
    )
    
    if verification_status:
        query = query.where(ExtractedRecord.verification_status == verification_status)
    if validation_status:
        query = query.where(ExtractedRecord.validation_status == validation_status)
    if search:
        query = query.where(
            (ExtractedRecord.owner_name.ilike(f"%{search}%")) |
            (ExtractedRecord.survey_number.ilike(f"%{search}%")) |
            (ExtractedRecord.khasra_number.ilike(f"%{search}%")) |
            (ExtractedRecord.village.ilike(f"%{search}%"))
        )
    
    query = query.order_by(desc(ExtractedRecord.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{record_id}", response_model=ExtractedRecordResponse)
async def get_record(record_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ExtractedRecord)
        .options(selectinload(ExtractedRecord.fields), selectinload(ExtractedRecord.validations))
        .where(ExtractedRecord.id == record_id)
    )
    rec = result.scalars().first()
    if not rec:
        raise HTTPException(status_code=404, detail="Extracted land record not found")
    return rec

@router.post("/{record_id}/verify", response_model=ExtractedRecordResponse)
async def verify_record(
    record_id: str,
    payload: RecordVerificationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(ExtractedRecord)
        .options(selectinload(ExtractedRecord.fields), selectinload(ExtractedRecord.validations))
        .where(ExtractedRecord.id == record_id)
    )
    rec = result.scalars().first()
    if not rec:
        raise HTTPException(status_code=404, detail="Extracted record not found")

    fields_map = {f.field_name: f for f in rec.fields}

    for update in payload.fields:
        field_obj = fields_map.get(update.field_name)
        original_val = field_obj.field_value if field_obj else getattr(rec, update.field_name, None)
        
        corrected_val = update.corrected_value
        if update.action == "mark_unavailable":
            corrected_val = None

        # Record action
        action_log = VerificationAction(
            record_id=rec.id,
            field_id=field_obj.id if field_obj else None,
            field_name=update.field_name,
            user_id=current_user.id,
            user_email=current_user.email,
            action=update.action,
            original_value=str(original_val) if original_val is not None else None,
            corrected_value=str(corrected_val) if corrected_val is not None else None,
            timestamp=datetime.utcnow()
        )
        db.add(action_log)

        # Update field value if edited or accepted
        if hasattr(rec, update.field_name):
            setattr(rec, update.field_name, corrected_val)

        if field_obj:
            field_obj.verified_value = corrected_val
            field_obj.is_verified = True
            if update.action == "edit":
                field_obj.field_value = corrected_val

        # Save AI Retraining Feedback Data Pair
        if update.action == "edit" and str(original_val) != str(corrected_val):
            feedback = FeedbackItem(
                document_id=rec.document_id,
                record_id=rec.id,
                field_name=update.field_name,
                ocr_raw_text=field_obj.raw_ocr_text if field_obj else None,
                ai_predicted_value=str(original_val),
                human_corrected_value=str(corrected_val),
                user_id=current_user.id
            )
            db.add(feedback)

    rec.verification_status = payload.verification_status
    if payload.remarks:
        rec.remarks = payload.remarks
    rec.updated_at = datetime.utcnow()

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        user_email=current_user.email,
        action="verify_record",
        resource_type="record",
        resource_id=rec.id,
        details_json={"status": payload.verification_status, "fields_updated": len(payload.fields)}
    )
    db.add(audit)

    await db.commit()
    await db.refresh(rec)
    return rec
