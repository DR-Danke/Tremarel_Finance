"""SQLAlchemy LdSpecialist model for Legal Desk specialist entities."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String
from sqlalchemy.orm import relationship

from src.config.database import Base


class LdSpecialist(Base):
    """
    Legal Desk specialist model.

    Represents a legal specialist with experience, rates, and workload tracking.
    Maps to the ld_specialists table in PostgreSQL database.
    """

    __tablename__ = "ld_specialists"

    id: int = Column(Integer, primary_key=True)
    full_name: str = Column(String(255), nullable=False)
    email: str = Column(String(255), unique=True, nullable=False)
    phone: Optional[str] = Column(String(100), nullable=True)
    years_experience: int = Column(Integer, default=0)
    hourly_rate: Optional[Decimal] = Column(Numeric(10, 2), nullable=True)
    currency: str = Column(String(10), default="EUR")
    max_concurrent_cases: int = Column(Integer, default=5)
    current_workload: int = Column(Integer, default=0)
    overall_score: Decimal = Column(Numeric(3, 2), default=0.00)
    is_active: bool = Column(Boolean, default=True)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    expertise = relationship("LdSpecialistExpertise", backref="specialist")
    jurisdictions = relationship("LdSpecialistJurisdiction", backref="specialist")
    case_assignments = relationship("LdCaseSpecialist", backref="specialist")
    scores = relationship("LdSpecialistScore", backref="specialist")

    def __repr__(self) -> str:
        """String representation of LdSpecialist."""
        return f"<LdSpecialist(id={self.id}, full_name={self.full_name}, email={self.email})>"
