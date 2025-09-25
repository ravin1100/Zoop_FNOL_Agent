from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.schema.risk_schema import RiskCategory
from app.db.database import Base


class ClaimRisk(Base):
    __tablename__ = "claim_risks"

    id = Column(Integer, primary_key=True)

    # foreign key to Claim
    claim_id = Column(Integer, ForeignKey("claims.id"), unique=True, nullable=False)
    risk_score = Column(Integer, nullable=False)
    risk_category = Column(Enum(RiskCategory), nullable=False)
    fraud_indicators = Column(String, nullable=True)  # Comma-separated list
    processing_score = Column(Integer, nullable=False)

    claim = relationship("Claim", back_populates="claim_risks")
