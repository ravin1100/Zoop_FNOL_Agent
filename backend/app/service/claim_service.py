from app.agents.intake_agent import parse_claim_key_fields
from app.agents.risk_assessment_agent import assess_claim_risk
from app.agents.routing_agent import decide_routing
from app.model.claim_risk import ClaimRisk
from app.model.claim_route import ClaimRoute
from app.model.claims import Claim
from app.schema.claim_schema import ClaimSchema
from app.schema.risk_schema import RiskAssessmentLLMSchema
from app.schema.routing_decision_schema import RoutingDecisionLLMSchema
from app.db.database import AsyncSession


async def process_claim(db: AsyncSession, raw_data: ClaimSchema) -> ClaimSchema:
    """
    Async wrapper to process claim data.
    """

    claim_id = raw_data.claim_id
    claim_data = parse_claim_key_fields(raw_data)
    saved_claim = await save_claim_to_db(db, raw_data)
    raw_data = assess_claim_risk(raw_data)
    await save_claim_risk_to_db(db, claim_id, raw_data)
    raw_data = decide_routing(claim_data, raw_data)
    await save_claim_route_to_db(db, raw_data)
    return raw_data


# save in db
async def save_claim_to_db(db: AsyncSession, claim_data: ClaimSchema) -> None:
    """
    Save the claim data to the database.
    """
    new_claim = Claim(**claim_data.model_dump())
    db.add(new_claim)
    await db.commit()
    await db.refresh(new_claim)
    return new_claim


async def save_claim_risk_to_db(
    db: AsyncSession, claim_id: str, risk_data: RiskAssessmentLLMSchema
) -> ClaimRisk:
    """
    Save the claim risk data to the database for a given claim.
    """
    # Convert fraud_indicators list to comma-separated string
    fraud_indicators_str = ", ".join(risk_data.fraud_indicators)

    new_claim_risk = ClaimRisk(
        claim_id=claim_id,
        risk_score=risk_data.risk_score,
        risk_category=risk_data.risk_category,
        fraud_indicators=fraud_indicators_str,
        processing_score=risk_data.processing_score,
    )

    db.add(new_claim_risk)
    await db.commit()
    await db.refresh(new_claim_risk)
    return new_claim_risk


async def save_claim_route_to_db(
    db: AsyncSession, route_data: RoutingDecisionLLMSchema
) -> None:
    """
    Save the claim routing data to the database for a given claim.
    """
    new_claim_route = ClaimRoute(**route_data.model_dump())

    db.add(new_claim_route)
    await db.commit()
    await db.refresh(new_claim_route)
    return new_claim_route
