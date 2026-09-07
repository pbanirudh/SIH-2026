import os
import hashlib
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.config import settings
from app.core.database import get_db
from app.models.models import Document, DocumentPage, OCRResult, ExtractedRecord, ProcessingJob, User, AuditLog
from app.schemas.schemas import DocumentResponse, OCRResultResponse, ProcessingJobResponse, ExtractedRecordResponse
from app.services.pipeline import DigitizationPipelineService
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/upload", response_model=List[DocumentResponse])
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    expected_language: str = Form("en"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    uploaded_docs = []
    
    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"File extension '{ext}' is not supported. Allowed: {settings.ALLOWED_EXTENSIONS}")

        content = await file.read()
        file_size = len(content)

        if file_size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE_MB}MB")

        file_hash = hashlib.sha256(content).hexdigest()

        # Save to disk
        doc_filename = f"{file_hash[:16]}_{file.filename}"
        storage_path = os.path.join(settings.UPLOAD_DIR, doc_filename)
        
        with open(storage_path, "wb") as f:
            f.write(content)

        doc = Document(
            filename=doc_filename,
            original_filename=file.filename,
            file_type=ext.replace(".", ""),
            file_size=file_size,
            storage_path=storage_path,
            mime_type=file.content_type,
            file_hash=file_hash,
            expected_language=expected_language,
            status="uploaded"
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        uploaded_docs.append(doc)

        # Audit log
        audit = AuditLog(
            user_id=current_user.id,
            user_email=current_user.email,
            action="upload_document",
            resource_type="document",
            resource_id=doc.id,
            details_json={"filename": file.filename, "size": file_size, "language": expected_language}
        )
        db.add(audit)

        # Launch pipeline in background
        background_tasks.add_task(DigitizationPipelineService.process_document_pipeline, doc.id, db)

    await db.commit()
    return uploaded_docs

@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Document)
    if status:
        query = query.where(Document.status == status)
    if search:
        query = query.where(Document.original_filename.ilike(f"%{search}%"))
    
    query = query.order_by(desc(Document.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, db: AsyncSession = Depends(get_db)):
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.post("/{document_id}/process", response_model=DocumentResponse)
async def trigger_process_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    background_tasks.add_task(DigitizationPipelineService.process_document_pipeline, doc.id, db)
    return doc

@router.get("/{document_id}/status", response_model=List[ProcessingJobResponse])
async def get_document_status(document_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProcessingJob)
        .where(ProcessingJob.document_id == document_id)
        .order_by(desc(ProcessingJob.started_at))
    )
    return result.scalars().all()

@router.get("/{document_id}/ocr", response_model=List[OCRResultResponse])
async def get_document_ocr(document_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(OCRResult)
        .where(OCRResult.document_id == document_id)
        .order_by(OCRResult.page_number)
    )
    return result.scalars().all()

@router.get("/{document_id}/records", response_model=List[ExtractedRecordResponse])
async def get_document_records(document_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ExtractedRecord)
        .where(ExtractedRecord.document_id == document_id)
    )
    return result.scalars().all()
