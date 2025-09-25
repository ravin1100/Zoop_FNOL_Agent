from sqlalchemy import Column, ForeignKey, Integer, String, Enum
from app.db.database import Base
from sqlalchemy.orm import relationship

from app.schema.risk_schema import RiskCategory
from app.schema.routing_decision_schema import Priority


class ClaimAssessment(Base):
    __tablename__ = "claim_assessments"

    id = Column(Integer(), primary_key=True)

    # --- Relationships ---
    claim_id = Column(Integer, ForeignKey("claims.id"), unique=True, nullable=False)
    claim = relationship(
        "Claim", back_populates="assessment", lazy="joined"
    )  # eager load using JOIN

    # --- Risk fields ---
    risk_score = Column(Integer, nullable=False)
    risk_category = Column(Enum(RiskCategory), nullable=False)
    fraud_indicators = Column(String, nullable=True)
    processing_score = Column(Integer, nullable=False)

    # --- Routing fields ---
    priority = Column(Enum(Priority), nullable=False)
    adjuster_tier = Column(String, nullable=False)
