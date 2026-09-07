import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import auth, documents, records, validation, dashboard, export, audit

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    await init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-grade AI Land Record Digitization, Validation and Human Verification Web Application.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount preprocessed page images for front-end visual canvas
if not os.path.exists(settings.PROCESSED_DIR):
    os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
app.mount("/storage", StaticFiles(directory="./storage"), name="storage")

# Mount API Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(documents.router, prefix=f"{settings.API_V1_STR}/documents", tags=["Documents"])
app.include_router(records.router, prefix=f"{settings.API_V1_STR}/records", tags=["Land Records & Verification"])
app.include_router(validation.router, prefix=f"{settings.API_V1_STR}/validation", tags=["Validation Engine"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard Statistics"])
app.include_router(export.router, prefix=f"{settings.API_V1_STR}/export", tags=["CSV Exporter"])
app.include_router(audit.router, prefix=f"{settings.API_V1_STR}/audit", tags=["Audit Logs"])

@app.get("/health")
async def health_check():
    return {"status": "online", "system": settings.PROJECT_NAME}
