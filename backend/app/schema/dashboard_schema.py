from typing import Dict, List
from pydantic import BaseModel, Field
from datetime import date


class RiskDistribution(BaseModel):
    """Risk level distribution data"""

    low: int = Field(0, description="Number of low risk claims")
    medium: int = Field(0, description="Number of medium risk claims")
    high: int = Field(0, description="Number of high risk claims")


class PriorityDistribution(BaseModel):
    """Priority level distribution data"""

    normal: int = Field(0, description="Number of normal priority claims")
    high: int = Field(0, description="Number of high priority claims")
    urgent: int = Field(0, description="Number of urgent priority claims")


class AdjusterTierDistribution(BaseModel):
    """Adjuster tier distribution data"""

    tier_1: int = Field(0, description="Number of tier 1 adjuster assignments")
    tier_2: int = Field(0, description="Number of tier 2 adjuster assignments")
    tier_3: int = Field(0, description="Number of tier 3 adjuster assignments")


class ClaimTypeDistribution(BaseModel):
    """Claim type distribution data"""

    auto: int = Field(0, description="Number of auto claims")
    property: int = Field(0, description="Number of property claims")
    health: int = Field(0, description="Number of health claims")
    other: int = Field(0, description="Number of other claim types")


class RecentClaimsMetrics(BaseModel):
    """Recent claims activity metrics"""

    today: int = Field(0, description="Claims processed today")
    this_week: int = Field(0, description="Claims processed this week")
    this_month: int = Field(0, description="Claims processed this month")


class AmountMetrics(BaseModel):
    """Claim amount statistics"""

    total_amount: float = Field(0.0, description="Total claim amount")
    average_amount: float = Field(0.0, description="Average claim amount")
    highest_amount: float = Field(0.0, description="Highest single claim amount")
    lowest_amount: float = Field(0.0, description="Lowest single claim amount")


class ProcessingStats(BaseModel):
    """Processing efficiency statistics"""

    total_processed: int = Field(0, description="Total claims processed")
    fraud_detected: int = Field(
        0, description="Number of potential fraud cases detected"
    )
    fraud_rate: float = Field(0.0, description="Fraud detection rate as percentage")
    avg_risk_score: float = Field(
        0.0, description="Average risk score across all claims"
    )


class RecentActivity(BaseModel):
    """Recent claim activity item"""

    claim_id: str = Field(..., description="Claim identifier")
    type: str = Field(..., description="Claim type")
    amount: float = Field(..., description="Claim amount")
    risk_level: str = Field(..., description="Risk assessment level")
    priority: str = Field(..., description="Processing priority")
    submitted_date: date = Field(..., description="Date submitted")


class DashboardDataSchema(BaseModel):
    """Comprehensive dashboard data schema"""

    # Summary metrics
    total_claims: int = Field(0, description="Total number of claims")
    processing_stats: ProcessingStats = Field(default_factory=ProcessingStats)

    # Distribution metrics
    risk_distribution: RiskDistribution = Field(default_factory=RiskDistribution)
    priority_distribution: PriorityDistribution = Field(
        default_factory=PriorityDistribution
    )
    adjuster_distribution: AdjusterTierDistribution = Field(
        default_factory=AdjusterTierDistribution
    )
    claim_type_distribution: ClaimTypeDistribution = Field(
        default_factory=ClaimTypeDistribution
    )

    # Time-based metrics
    recent_claims: RecentClaimsMetrics = Field(default_factory=RecentClaimsMetrics)

    # Financial metrics
    amount_metrics: AmountMetrics = Field(default_factory=AmountMetrics)

    # Recent activity
    recent_activity: List[RecentActivity] = Field(default_factory=list, max_items=10)

    # Additional insights
    top_claim_types: Dict[str, int] = Field(
        default_factory=dict, description="Top claim types with counts"
    )
    high_risk_locations: List[str] = Field(
        default_factory=list, max_items=5, description="Locations with high risk claims"
    )
