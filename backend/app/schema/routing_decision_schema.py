from enum import Enum
from pydantic import BaseModel


class Priority(str, Enum):
    """Priority levels for claim processing"""

    MEDIUM = "medium"
    URGENT = "urgent"


class AdjusterTier(str, Enum):
    """Adjuster tiers for claim assignment"""

    STANDARD = "standard"
    JUNIOR = "junior"
    SENIOR = "senior"
    FRAUD_SPECIALIST = "fraud_specialist"


# RoutingDecision Schema
class RoutingDecisionLLMSchema(BaseModel):
    """Schema for routing decision results from LLM"""

    priority: Priority
    adjuster_tier: AdjusterTier
