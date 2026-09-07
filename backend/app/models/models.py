import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="officer")  # admin, officer, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, png, jpg, tiff, webp
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String(512), nullable=False)
    mime_type = Column(String(100), nullable=True)
    file_hash = Column(String(64), nullable=True, index=True)
    expected_language = Column(String(20), default="en")
    detected_language = Column(String(20), nullable=True)
    status = Column(String(50), default="uploaded")  # uploaded, preprocessing, ocr_processing, nlp_extracting, validating, completed, failed
    total_pages = Column(Integer, default=1)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    records = relationship("ExtractedRecord", back_populates="document", cascade="all, delete-orphan")
    jobs = relationship("ProcessingJob", back_populates="document", cascade="all, delete-orphan")

class DocumentPage(Base):
    __tablename__ = "document_pages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    image_path = Column(String(512), nullable=False)
    has_selectable_text = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="pages")

class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False)
    engine_used = Column(String(50), default="PaddleOCR")  # PaddleOCR, Indic-TrOCR, Fallback
    language = Column(String(20), default="en")
    detected_text = Column(Text, nullable=True)
    confidence = Column(Float, default=0.0)
    bounding_boxes_json = Column(JSON, nullable=True)  # list of {text, confidence, box: [[x,y],...]}
    is_handwritten = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ExtractedRecord(Base):
    __tablename__ = "extracted_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    record_identifier = Column(String(100), nullable=True)
    document_type = Column(String(100), nullable=True)  # RoR, 7/12 Extract, Khasra, Khata, Deed
    
    # Location
    state = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    tehsil = Column(String(100), nullable=True)
    taluk = Column(String(100), nullable=True)
    village = Column(String(100), nullable=True)
    ward = Column(String(100), nullable=True)
    
    # Ownership
    owner_name = Column(String(255), nullable=True)
    co_owner_names = Column(Text, nullable=True)
    parent_name = Column(String(255), nullable=True)
    ownership_type = Column(String(100), nullable=True)
    ownership_share = Column(String(50), nullable=True)
    
    # Land Identification
    survey_number = Column(String(100), nullable=True)
    sub_survey_number = Column(String(100), nullable=True)
    khasra_number = Column(String(100), nullable=True)
    khata_number = Column(String(100), nullable=True)
    plot_number = Column(String(100), nullable=True)
    patta_number = Column(String(100), nullable=True)
    parcel_id = Column(String(100), nullable=True)
    
    # Land Details
    area = Column(Float, nullable=True)
    area_unit = Column(String(50), nullable=True)
    land_classification = Column(String(100), nullable=True)
    land_type = Column(String(100), nullable=True)
    irrigation_status = Column(String(100), nullable=True)
    land_use = Column(String(100), nullable=True)
    
    # Transaction / Mutation
    mutation_number = Column(String(100), nullable=True)
    mutation_date = Column(String(50), nullable=True)
    mutation_type = Column(String(100), nullable=True)
    previous_owner = Column(String(255), nullable=True)
    new_owner = Column(String(255), nullable=True)
    registration_number = Column(String(100), nullable=True)
    registration_date = Column(String(50), nullable=True)
    deed_number = Column(String(100), nullable=True)
    transaction_type = Column(String(100), nullable=True)
    
    # Additional
    record_date = Column(String(50), nullable=True)
    source_department = Column(String(255), nullable=True)
    language = Column(String(20), default="en")
    ocr_engine = Column(String(50), default="PaddleOCR")
    ocr_confidence = Column(Float, default=0.0)
    extraction_confidence = Column(Float, default=0.0)
    validation_status = Column(String(50), default="UNVERIFIED")  # VALID, WARNING, INVALID, UNVERIFIED
    verification_status = Column(String(50), default="UNVERIFIED")  # UNVERIFIED, VERIFIED, REJECTED
    remarks = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    document = relationship("Document", back_populates="records")
    fields = relationship("ExtractedField", back_populates="record", cascade="all, delete-orphan")
    validations = relationship("ValidationResult", back_populates="record", cascade="all, delete-orphan")

class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    record_id = Column(String(36), ForeignKey("extracted_records.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(100), nullable=False)
    field_value = Column(Text, nullable=True)
    source_page = Column(Integer, default=1)
    bounding_box_json = Column(JSON, nullable=True)
    raw_ocr_text = Column(Text, nullable=True)
    ocr_confidence = Column(Float, default=0.0)
    nlp_confidence = Column(Float, default=0.0)
    final_confidence = Column(Float, default=0.0)
    confidence_category = Column(String(20), default="LOW")  # HIGH, MEDIUM, LOW
    validation_status = Column(String(20), default="UNVERIFIED")  # VALID, WARNING, INVALID, UNVERIFIED
    original_ai_value = Column(Text, nullable=True)
    verified_value = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    record = relationship("ExtractedRecord", back_populates="fields")

class ValidationResult(Base):
    __tablename__ = "validation_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    record_id = Column(String(36), ForeignKey("extracted_records.id", ondelete="CASCADE"), nullable=False)
    field_name = Column(String(100), nullable=True)
    rule_name = Column(String(100), nullable=False)
    validation_type = Column(String(50), nullable=False)  # format, logical, duplicate, cross_field
    status = Column(String(20), nullable=False)  # VALID, WARNING, INVALID
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    record = relationship("ExtractedRecord", back_populates="validations")

class VerificationAction(Base):
    __tablename__ = "verification_actions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    record_id = Column(String(36), nullable=False)
    field_id = Column(String(36), nullable=True)
    field_name = Column(String(100), nullable=False)
    user_id = Column(String(36), nullable=True)
    user_email = Column(String(255), nullable=True)
    action = Column(String(50), nullable=False)  # accepted, edited, rejected, marked_unavailable
    original_value = Column(Text, nullable=True)
    corrected_value = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    stage = Column(String(50), nullable=False)  # upload, preprocessing, classification, ocr, layout, nlp, validation, verification, export
    status = Column(String(50), default="pending")  # pending, in_progress, completed, failed
    progress_pct = Column(Float, default=0.0)
    message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    document = relationship("Document", back_populates="jobs")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=True)
    user_email = Column(String(255), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(100), nullable=True)
    details_json = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class FeedbackItem(Base):
    __tablename__ = "feedback_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), nullable=False)
    record_id = Column(String(36), nullable=False)
    field_name = Column(String(100), nullable=False)
    original_image_crop_path = Column(String(512), nullable=True)
    ocr_raw_text = Column(Text, nullable=True)
    ai_predicted_value = Column(Text, nullable=True)
    human_corrected_value = Column(Text, nullable=True)
    user_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
