from sqlalchemy import Column, String, Integer, Float, Boolean, Date, DateTime

from sqlalchemy.orm import relationship

from app.db.database import Base


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True)

    # --- Required Fields ---
    claim_id = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    customer_id = Column(String, nullable=False)
    policy_number = Column(String, nullable=False)
    incident_location = Column(String, nullable=False)
    timestamp_submitted = Column(DateTime, nullable=False)

    # --- Optional Fields ---
    police_report = Column(String, nullable=True)
    injuries_reported = Column(Boolean, nullable=True)
    other_party_involved = Column(Boolean, nullable=True)
    customer_tenure_days = Column(Integer, nullable=True)
    previous_claims_count = Column(Integer, nullable=True)

    # --- Relationships ---
    # claim_risks = relationship("ClaimRisk", back_populates="claim")
    # claim_routes = relationship("ClaimRoute", back_populates="claim")
    assessment = relationship("ClaimAssessment", back_populates="claim", uselist=False)
