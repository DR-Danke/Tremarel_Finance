"""SQLAlchemy LdSpecialistScore model for specialist performance scoring."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, Text

from src.config.database import Base


class LdSpecialistScore(Base):
    """
    Legal Desk specialist score model.

    Tracks performance scores per specialist per case.
    Maps to the ld_specialist_scores table in PostgreSQL database.
    """

    __tablename__ = "ld_specialist_scores"

    id: int = Column(Integer, primary_key=True)
    specialist_id: int = Column(
        Integer, ForeignKey("ld_specialists.id", ondelete="CASCADE"), nullable=False
    )
    case_id: int = Column(
        Integer, ForeignKey("ld_cases.id", ondelete="CASCADE"), nullable=False
    )
    quality_score: Optional[Decimal] = Column(Numeric(3, 2), nullable=True)
    teamwork_score: Optional[Decimal] = Column(Numeric(3, 2), nullable=True)
    delivery_score: Optional[Decimal] = Column(Numeric(3, 2), nullable=True)
    satisfaction_score: Optional[Decimal] = Column(Numeric(3, 2), nullable=True)
    overall_score: Optional[Decimal] = Column(Numeric(3, 2), nullable=True)
    feedback: Optional[str] = Column(Text, nullable=True)
    scored_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of LdSpecialistScore."""
        return f"<LdSpecialistScore(id={self.id}, specialist_id={self.specialist_id}, case_id={self.case_id})>"
