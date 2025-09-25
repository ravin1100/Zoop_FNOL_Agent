from sqlalchemy import select, func, case, desc

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
from app.schema.dashboard_schema import (
    DashboardDataSchema,
    RiskDistribution,
    PriorityDistribution,
    AdjusterTierDistribution,
    ClaimTypeDistribution,
    RecentClaimsMetrics,
    AmountMetrics,
    ProcessingStats,
    RecentActivity,
)
from app.db.database import AsyncSession


import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
from collections import Counter
from sqlalchemy.ext.asyncio import AsyncSession


async def claim_processing_sse(claim_data: ClaimSchema, db: AsyncSession):
    """Generator yielding live status updates for claim processing"""

    try:
        # Stage 1: Parsing
        yield f"data: {json.dumps({'stage': 'Parsing claim', 'status': 'in_progress'})}\n\n"
        await asyncio.sleep(1)
        claim_data_parsed = parse_claim_key_fields(claim_data)
        yield f"data: {json.dumps({'stage': 'Parsing claim', 'status': 'done'})}\n\n"

        # Stage 2: Assessing Risk
        yield f"data: {json.dumps({'stage': 'Assessing risk', 'status': 'in_progress'})}\n\n"
        await asyncio.sleep(1)
        risk_assessment = assess_claim_risk(claim_data_parsed)
        yield f"data: {json.dumps({'stage': 'Assessing risk', 'status': 'done'})}\n\n"

        # Stage 3: Deciding Routing
        yield f"data: {json.dumps({'stage': 'Deciding routing', 'status': 'in_progress'})}\n\n"
        await asyncio.sleep(1)
        routing_decision = decide_routing(claim_data_parsed, risk_assessment)
        yield f"data: {json.dumps({'stage': 'Deciding routing', 'status': 'done'})}\n\n"

        # Final message
        yield f"data: {json.dumps({'stage': 'completed', 'claim_id': claim_data.claim_id})}\n\n"

    except Exception as e:
        # Catch errors and send as SSE instead of crashing
        error_message = {"stage": "error", "detail": str(e)}
        yield f"data: {json.dumps(error_message)}\n\n"


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


async def get_dashboard_data(db: AsyncSession) -> DashboardDataSchema:
    """
    Aggregate dashboard data from the database with comprehensive metrics.
    """

    # Get total claims count
    total_claims_result = await db.execute(select(func.count(Claim.id)))
    total_claims = total_claims_result.scalar() or 0

    # Get risk distribution
    risk_dist_result = await db.execute(
        select(
            ClaimAssessment.risk_category, func.count(ClaimAssessment.id).label("count")
        ).group_by(ClaimAssessment.risk_category)
    )
    risk_data = dict(risk_dist_result.fetchall())

    risk_distribution = RiskDistribution(
        low=risk_data.get("low", 0),
        medium=risk_data.get("medium", 0),
        high=risk_data.get("high", 0),
    )

    # Get priority distribution
    priority_dist_result = await db.execute(
        select(
            ClaimAssessment.priority, func.count(ClaimAssessment.id).label("count")
        ).group_by(ClaimAssessment.priority)
    )
    priority_data = dict(priority_dist_result.fetchall())

    priority_distribution = PriorityDistribution(
        normal=priority_data.get("normal", 0),
        high=priority_data.get("high", 0),
        urgent=priority_data.get("urgent", 0),
    )

    # Get adjuster tier distribution
    adjuster_dist_result = await db.execute(
        select(
            ClaimAssessment.adjuster_tier, func.count(ClaimAssessment.id).label("count")
        ).group_by(ClaimAssessment.adjuster_tier)
    )
    adjuster_data = dict(adjuster_dist_result.fetchall())

    adjuster_distribution = AdjusterTierDistribution(
        tier_1=adjuster_data.get("standard", 0) + adjuster_data.get("junior", 0),
        tier_2=adjuster_data.get("senior", 0),
        tier_3=adjuster_data.get("fraud_specialist", 0),
    )

    # Get claim type distribution
    claim_type_result = await db.execute(
        select(Claim.type, func.count(Claim.id).label("count")).group_by(Claim.type)
    )
    claim_type_data = dict(claim_type_result.fetchall())

    claim_type_distribution = ClaimTypeDistribution(
        auto=claim_type_data.get("auto", 0) + claim_type_data.get("vehicle", 0),
        property=claim_type_data.get("property", 0) + claim_type_data.get("home", 0),
        health=claim_type_data.get("health", 0) + claim_type_data.get("medical", 0),
        other=sum(
            v
            for k, v in claim_type_data.items()
            if k not in ["auto", "vehicle", "property", "home", "health", "medical"]
        ),
    )

    # Get time-based metrics
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    # Claims today
    today_result = await db.execute(
        select(func.count(Claim.id)).where(
            func.date(Claim.timestamp_submitted) == today
        )
    )
    claims_today = today_result.scalar() or 0

    # Claims this week
    week_result = await db.execute(
        select(func.count(Claim.id)).where(
            func.date(Claim.timestamp_submitted) >= week_start
        )
    )
    claims_week = week_result.scalar() or 0

    # Claims this month
    month_result = await db.execute(
        select(func.count(Claim.id)).where(
            func.date(Claim.timestamp_submitted) >= month_start
        )
    )
    claims_month = month_result.scalar() or 0

    recent_claims = RecentClaimsMetrics(
        today=claims_today, this_week=claims_week, this_month=claims_month
    )

    # Get amount metrics
    amount_stats_result = await db.execute(
        select(
            func.sum(Claim.amount).label("total"),
            func.avg(Claim.amount).label("average"),
            func.max(Claim.amount).label("highest"),
            func.min(Claim.amount).label("lowest"),
        )
    )
    amount_stats = amount_stats_result.first()

    amount_metrics = AmountMetrics(
        total_amount=float(amount_stats.total or 0),
        average_amount=float(amount_stats.average or 0),
        highest_amount=float(amount_stats.highest or 0),
        lowest_amount=float(amount_stats.lowest or 0),
    )

    # Get processing stats
    assessments_count_result = await db.execute(select(func.count(ClaimAssessment.id)))
    total_processed = assessments_count_result.scalar() or 0

    high_risk_result = await db.execute(
        select(func.count(ClaimAssessment.id)).where(
            ClaimAssessment.risk_category == "high"
        )
    )
    fraud_detected = high_risk_result.scalar() or 0

    fraud_rate = (
        (fraud_detected / total_processed * 100) if total_processed > 0 else 0.0
    )

    avg_risk_result = await db.execute(select(func.avg(ClaimAssessment.risk_score)))
    avg_risk_score = float(avg_risk_result.scalar() or 0)

    processing_stats = ProcessingStats(
        total_processed=total_processed,
        fraud_detected=fraud_detected,
        fraud_rate=fraud_rate,
        avg_risk_score=avg_risk_score,
    )

    # Get recent activity (last 10 claims with assessments)
    recent_activity_result = await db.execute(
        select(
            Claim.claim_id,
            Claim.type,
            Claim.amount,
            Claim.date,
            ClaimAssessment.risk_category,
            ClaimAssessment.priority,
        )
        .join(ClaimAssessment, Claim.id == ClaimAssessment.claim_id)
        .order_by(desc(Claim.timestamp_submitted))
        .limit(10)
    )

    recent_activity = []
    for row in recent_activity_result.fetchall():
        recent_activity.append(
            RecentActivity(
                claim_id=row.claim_id,
                type=row.type,
                amount=row.amount,
                risk_level=row.risk_category.value if row.risk_category else "unknown",
                priority=row.priority.value if row.priority else "normal",
                submitted_date=row.date,
            )
        )

    # Get top claim types
    top_claim_types = dict(claim_type_data)

    # Get high risk locations
    high_risk_locations_result = await db.execute(
        select(Claim.incident_location)
        .join(ClaimAssessment, Claim.id == ClaimAssessment.claim_id)
        .where(ClaimAssessment.risk_category == "high")
        .group_by(Claim.incident_location)
        .order_by(desc(func.count(Claim.id)))
        .limit(5)
    )
    high_risk_locations = [row[0] for row in high_risk_locations_result.fetchall()]

    return DashboardDataSchema(
        total_claims=total_claims,
        processing_stats=processing_stats,
        risk_distribution=risk_distribution,
        priority_distribution=priority_distribution,
        adjuster_distribution=adjuster_distribution,
        claim_type_distribution=claim_type_distribution,
        recent_claims=recent_claims,
        amount_metrics=amount_metrics,
        recent_activity=recent_activity,
        top_claim_types=top_claim_types,
        high_risk_locations=high_risk_locations,
    )
