from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.models.models import ValidationResult
from app.schemas.schemas import ValidationResultResponse

router = APIRouter()

@router.get("/errors", response_model=List[ValidationResultResponse])
async def get_validation_errors(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(ValidationResult)
    if status:
        query = query.where(ValidationResult.status == status)
    else:
        query = query.where(ValidationResult.status.in_(["INVALID", "WARNING"]))
        
    query = query.order_by(desc(ValidationResult.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
