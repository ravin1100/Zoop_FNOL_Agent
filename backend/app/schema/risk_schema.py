from enum import Enum
from typing import List
from pydantic import BaseModel, Field


class RiskCategory(str, Enum):
    """Risk categories for claims"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# --- Pydantic schema for structured output ---
class RiskAssessmentLLMSchema(BaseModel):
    """Schema for risk assessment results from LLM"""

    fraud_indicators: List[str] = Field(
        ..., description="List of fraud indicators triggered"
    )
    risk_score: int = Field(..., ge=0, le=10, description="Risk score from 1 to 10")
    risk_category: RiskCategory = Field(
        ..., description="Risk category: low, medium, or high"
    )
    processing_score: int = Field(
        ..., ge=1, le=10, description="Processing readiness score from 1 to 10"
    )
