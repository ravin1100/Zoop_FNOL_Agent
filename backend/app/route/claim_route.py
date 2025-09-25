from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schema.claim_assessment_schema import ClaimAssessmentListSchema
from app.schema.claim_schema import ClaimSchema
from app.schema.dashboard_schema import DashboardDataSchema
from app.service.claim_service import (
    claim_processing_sse,
    get_claim_assessment_by_claim_id,
    process_claim,
    list_claim_assessments_paginated,
    get_dashboard_data,
)

router = APIRouter(prefix="/claims", tags=["Claims"])


@router.post("/process")
async def process_claim_route(
    claim_data: ClaimSchema, db: AsyncSession = Depends(get_db)
):
    """Endpoint to process a new claim"""
    await process_claim(db, claim_data)
    return {"message": "Claim processed successfully", "claim": claim_data}


@router.post("/process-claim-live")
async def process_claim_live(
    claim_data: ClaimSchema, db: AsyncSession = Depends(get_db)
):
    """
    Process a claim and stream live updates via SSE
    for Parsing, Assessing Risk, and Deciding Routing.
    """
    return StreamingResponse(
        claim_processing_sse(claim_data, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        },
    )


@router.get("/assessments", response_model=ClaimAssessmentListSchema)
async def list_claim_assessments(
    page_no: int = 1, page_size: int = 10, db: AsyncSession = Depends(get_db)
):
    """List claim assessments with pagination"""
    return await list_claim_assessments_paginated(db, page_no, page_size)


@router.get("/dashboard", response_model=DashboardDataSchema)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    """Get comprehensive dashboard data with metrics and analytics"""
    return await get_dashboard_data(db)


@router.get("/processed/{claim_id}")
async def get_claim_assessment(claim_id: str, db: AsyncSession = Depends(get_db)):
    """Get claim assessment by claim ID"""
    return await get_claim_assessment_by_claim_id(db, claim_id)
