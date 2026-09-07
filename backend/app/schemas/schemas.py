from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr, Field

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "officer"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    sub: Optional[str] = None
    roles: List[str] = []

# Document Schemas
class DocumentResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    expected_language: str
    detected_language: Optional[str] = None
    status: str
    total_pages: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProcessingJobResponse(BaseModel):
    id: str
    stage: str
    status: str
    progress_pct: float
    message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# OCR Schemas
class OCRBox(BaseModel):
    text: str
    confidence: float
    box: List[List[float]]  # [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    is_handwritten: bool = False

class OCRResultResponse(BaseModel):
    id: str
    page_number: int
    engine_used: str
    language: str
    detected_text: Optional[str] = None
    confidence: float
    bounding_boxes_json: Optional[List[Dict[str, Any]]] = None
    is_handwritten: bool = False

    class Config:
        from_attributes = True

# Validation Schemas
class ValidationResultResponse(BaseModel):
    id: str
    field_name: Optional[str] = None
    rule_name: str
    validation_type: str
    status: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True

# Extracted Field & Record Schemas
class ExtractedFieldResponse(BaseModel):
    id: str
    field_name: str
    field_value: Optional[str] = None
    source_page: int = 1
    bounding_box_json: Optional[Any] = None
    raw_ocr_text: Optional[str] = None
    ocr_confidence: float = 0.0
    nlp_confidence: float = 0.0
    final_confidence: float = 0.0
    confidence_category: str = "LOW"
    validation_status: str = "UNVERIFIED"
    original_ai_value: Optional[str] = None
    verified_value: Optional[str] = None
    is_verified: bool = False

    class Config:
        from_attributes = True

class ExtractedRecordResponse(BaseModel):
    id: str
    document_id: str
    record_identifier: Optional[str] = None
    document_type: Optional[str] = None
    
    state: Optional[str] = None
    district: Optional[str] = None
    tehsil: Optional[str] = None
    taluk: Optional[str] = None
    village: Optional[str] = None
    ward: Optional[str] = None
    
    owner_name: Optional[str] = None
    co_owner_names: Optional[str] = None
    parent_name: Optional[str] = None
    ownership_type: Optional[str] = None
    ownership_share: Optional[str] = None
    
    survey_number: Optional[str] = None
    sub_survey_number: Optional[str] = None
    khasra_number: Optional[str] = None
    khata_number: Optional[str] = None
    plot_number: Optional[str] = None
    patta_number: Optional[str] = None
    parcel_id: Optional[str] = None
    
    area: Optional[float] = None
    area_unit: Optional[str] = None
    land_classification: Optional[str] = None
    land_type: Optional[str] = None
    irrigation_status: Optional[str] = None
    land_use: Optional[str] = None
    
    mutation_number: Optional[str] = None
    mutation_date: Optional[str] = None
    mutation_type: Optional[str] = None
    previous_owner: Optional[str] = None
    new_owner: Optional[str] = None
    registration_number: Optional[str] = None
    registration_date: Optional[str] = None
    deed_number: Optional[str] = None
    transaction_type: Optional[str] = None
    
    record_date: Optional[str] = None
    source_department: Optional[str] = None
    language: str = "en"
    ocr_engine: str = "PaddleOCR"
    ocr_confidence: float = 0.0
    extraction_confidence: float = 0.0
    validation_status: str = "UNVERIFIED"
    verification_status: str = "UNVERIFIED"
    remarks: Optional[str] = None
    
    fields: List[ExtractedFieldResponse] = []
    validations: List[ValidationResultResponse] = []
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Verification Request Schemas
class FieldVerificationUpdate(BaseModel):
    field_name: str
    action: str  # accept, edit, reject, mark_unavailable
    corrected_value: Optional[str] = None

class RecordVerificationRequest(BaseModel):
    fields: List[FieldVerificationUpdate]
    verification_status: str = "VERIFIED"  # VERIFIED, REJECTED
    remarks: Optional[str] = None

# Dashboard & Export Schemas
class DashboardStatsResponse(BaseModel):
    total_documents: int
    documents_processed: int
    documents_success: int
    documents_failed: int
    total_records: int
    high_confidence_records: int
    low_confidence_records: int
    records_needing_verification: int
    validation_errors_count: int
    verified_records_count: int
    exported_records_count: int
    
    state_distribution: Dict[str, int]
    district_distribution: Dict[str, int]
    language_distribution: Dict[str, int]
    validation_status_distribution: Dict[str, int]
    confidence_distribution: Dict[str, int]
    error_types: Dict[str, int]

class AuditLogResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details_json: Optional[Any] = None
    timestamp: datetime

    class Config:
        from_attributes = True
