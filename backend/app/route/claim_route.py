from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schema.claim_schema import ClaimSchema
from app.service.claim_service import process_claim

router = APIRouter(prefix="/claims", tags=["Claims"])


@router.post("/process")
async def process_claim_route(
    claim_data: ClaimSchema, db: AsyncSession = Depends(get_db)
):
    # Process the claim using the provided data
    await process_claim(db, claim_data)
    return {"message": "Claim processed successfully", "claim": claim_data}
