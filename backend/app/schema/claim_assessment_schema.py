# final schema for claim assessment
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schema.claim_schema import ClaimSchema
from app.schema.risk_schema import RiskAssessmentLLMSchema
from app.schema.routing_decision_schema import RoutingDecisionLLMSchema


class ClaimAssessmentSimpleSchema(BaseModel):
    """Simplified schema for combined claim assessment results
        "CLM-2024-003": {
      "risk_level": "HIGH",
      "priority": "urgent",
      "adjuster_tier": "fraud_specialist"
    }
    """

    claim_id: str = Field(..., description="Unique identifier for the claim")
    risk_level: RiskAssessmentLLMSchema = Field(..., description="Risk level")
    adjuster_tier: List[str] = Field(..., description="Adjuster tier details")


class ClaimAssessmentSimpleSchema(BaseModel):
    """Schema for Claim Assessment Details"""

    claim_id: str
    risk_level: str
    priority: str
    adjuster_tier: List[str]
    validation_errors: Optional[List[str]] = None


class ClaimAssessmentListSchema(BaseModel):
    page_no: int
    page_size: int
    data: List[ClaimAssessmentSimpleSchema]


class ClaimAssessmentDetailedSchema(BaseModel):
    """Schema for combined claim assessment results"""

    claim: ClaimSchema = Field(..., description="Claim details")

    risk_assessment: RiskAssessmentLLMSchema = Field(
        ..., description="Risk assessment details"
    )
    routing_decision: RoutingDecisionLLMSchema = Field(
        ..., description="Routing decision details"
    )
