from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schema.claim_assessment_schema import ClaimAssessmentListSchema
from app.schema.claim_schema import ClaimSchema
from app.service.claim_service import (
    get_claim_assessment_by_claim_id,
    process_claim,
    list_claim_assessments_paginated,
)

router = APIRouter(prefix="/claims", tags=["Claims"])


@router.post("/process")
async def process_claim_route(
    claim_data: ClaimSchema, db: AsyncSession = Depends(get_db)
):
    """Endpoint to process a new claim"""
    await process_claim(db, claim_data)
    return {"message": "Claim processed successfully", "claim": claim_data}


@router.get("/assessments", response_model=ClaimAssessmentListSchema)
async def list_claim_assessments(
    page_no: int = 1, page_size: int = 10, db: AsyncSession = Depends(get_db)
):
    """List claim assessments with pagination"""
    return await list_claim_assessments_paginated(db, page_no, page_size)


@router.get("/{claim_id}")
async def get_claim_assessment(claim_id: int, db: AsyncSession = Depends(get_db)):
    """Get claim assessment by claim ID"""
    return await get_claim_assessment_by_claim_id(db, claim_id)
