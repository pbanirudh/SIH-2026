import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Land Record Digitization and Validation System"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "super-secret-key-change-in-production-land-record-digitization-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    DATABASE_URL: str = "sqlite+aiosqlite:///./land_records.db"
    SYNC_DATABASE_URL: str = "sqlite:///./land_records.db"

    UPLOAD_DIR: str = "./storage/uploads"
    PROCESSED_DIR: str = "./storage/processed"
    EXPORT_DIR: str = "./storage/exports"
    FEEDBACK_DIR: str = "./storage/feedback"

    MAX_FILE_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".webp"]

    CONFIDENCE_THRESHOLD_HIGH: float = 0.90
    CONFIDENCE_THRESHOLD_MEDIUM: float = 0.70

    DEFAULT_OCR_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: List[str] = [
        "en", "hi", "ta", "te", "kn", "ml", "mr", "bn", "gu", "pa", "or", "as"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Ensure storage directories exist
for folder in [settings.UPLOAD_DIR, settings.PROCESSED_DIR, settings.EXPORT_DIR, settings.FEEDBACK_DIR]:
    os.makedirs(folder, exist_ok=True)
