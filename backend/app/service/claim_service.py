from sqlalchemy import select

from fastapi import HTTPException
from app.agents.intake_agent import parse_claim_key_fields
from app.agents.risk_assessment_agent import assess_claim_risk
from app.agents.routing_agent import decide_routing
from app.model.claim_assessment import ClaimAssessment
from app.model.claims import Claim
from app.schema.claim_assessment_schema import (
    ClaimAssessmentListSchema,
    ClaimAssessmentSimpleSchema,
)
from app.schema.claim_schema import ClaimSchema
from app.schema.risk_schema import RiskAssessmentLLMSchema
from app.schema.routing_decision_schema import RoutingDecisionLLMSchema
from app.db.database import AsyncSession


async def process_claim(db: AsyncSession, raw_data: ClaimSchema) -> ClaimSchema:
    """
    Async wrapper to process claim data in a single transaction.
    """
    async with db.begin():
        # Parse claim
        claim_data = parse_claim_key_fields(raw_data)

        # Save claim
        saved_claim = await save_claim_to_db(db, claim_data, commit=False)

        # Assess risk
        risk_assessment = assess_claim_risk(claim_data)

        # Decide routing
        routing_decision = decide_routing(claim_data, risk_assessment)

        # Save combined assessment (risk + routing)
        await save_claim_assessment_to_db(
            db, saved_claim.id, risk_assessment, routing_decision, commit=False
        )

    # After exiting the context, transaction is committed automatically
    return raw_data


# Save claim
async def save_claim_to_db(
    db: AsyncSession, claim_data: ClaimSchema, commit: bool = True
) -> Claim:
    """
    Save the claim data to the database.

    """
    new_claim = Claim(**claim_data.model_dump())
    db.add(new_claim)

    if commit:
        await db.commit()
    else:
        await db.flush()  # ensures INSERT and populates PK without committing

    await db.refresh(new_claim)
    return new_claim


# save claim assessment
async def save_claim_assessment_to_db(
    db: AsyncSession,
    claim_id: int,
    risk_data: RiskAssessmentLLMSchema,
    route_data: RoutingDecisionLLMSchema,
    commit: bool = True,
) -> ClaimAssessment:
    """
    Save the claim assessment data to the database for a given claim.

    """
    fraud_indicators_str = ", ".join(risk_data.fraud_indicators)

    new_claim_assessment = ClaimAssessment(
        claim_id=claim_id,
        risk_score=risk_data.risk_score,
        risk_category=risk_data.risk_category,
        fraud_indicators=fraud_indicators_str,
        processing_score=risk_data.processing_score,
        priority=route_data.priority,
        adjuster_tier=route_data.adjuster_tier,
    )

    db.add(new_claim_assessment)

    if commit:
        await db.commit()
    else:
        await db.flush()  # writes SQL but doesn’t commit

    await db.refresh(new_claim_assessment)
    return new_claim_assessment


async def get_claim_assessment_by_claim_id(
    db: AsyncSession, claim_id: str
) -> ClaimAssessment | None:
    """
    Retrieve the claim assessment by claim ID.
    """
    result = await db.execute(
        select(ClaimAssessment)
        .join(Claim, ClaimAssessment.claim_id == Claim.id)
        .where(Claim.claim_id == claim_id)
    )
    claim_assessment = result.scalars().first()
    if not claim_assessment:
        raise HTTPException(status_code=404, detail="Claim assessment not found")
    return claim_assessment


# --- Function to list and serialize ---
async def list_claim_assessments_paginated(
    db: AsyncSession, page_no: int = 1, page_size: int = 10
) -> ClaimAssessmentListSchema:
    """
    List claim assessments with pagination and return as ClaimAssessmentListSchema.
    """
    skip = (page_no - 1) * page_size

    result = await db.execute(select(ClaimAssessment).offset(skip).limit(page_size))
    assessments: list[ClaimAssessment] = result.scalars().all()

    # Convert DB models to simple schema
    data = []
    for a in assessments:
        data.append(
            ClaimAssessmentSimpleSchema(
                claim_id=a.claim.claim_id,  # from Claim relationship
                risk_level=a.risk_category.value if a.risk_category else "UNKNOWN",
                priority=a.priority.value if a.priority else "normal",
                adjuster_tier=[a.adjuster_tier],  # wrap string in list
                validation_errors=None,  # populate if you store validation errors somewhere
            )
        )

    return ClaimAssessmentListSchema(page_no=page_no, page_size=page_size, data=data)
