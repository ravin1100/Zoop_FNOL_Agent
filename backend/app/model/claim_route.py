from sqlalchemy import Column, ForeignKey, Integer, String
from app.db.database import Base
from sqlalchemy.orm import relationship


class ClaimRoute(Base):
    __tablename__ = "claim_routes"

    id = Column(Integer, primary_key=True)

    claim_id = Column(Integer, ForeignKey("claims.id"))
    adjuster_tier = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    adjuster_tier = Column(String, nullable=False)

    # --- Relationships ---
    claim = relationship("Claim", back_populates="claim_routes")
