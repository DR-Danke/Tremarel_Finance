"""SQLAlchemy LdCaseSpecialist model for case-specialist assignment junction."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String

from src.config.database import Base


class LdCaseSpecialist(Base):
    """
    Legal Desk case-specialist assignment model.

    Junction table for case-specialist assignments with role and fee negotiation.
    Maps to the ld_case_specialists table in PostgreSQL database.
    """

    __tablename__ = "ld_case_specialists"

    id: int = Column(Integer, primary_key=True)
    case_id: int = Column(
        Integer, ForeignKey("ld_cases.id", ondelete="CASCADE"), nullable=False
    )
    specialist_id: int = Column(
        Integer, ForeignKey("ld_specialists.id", ondelete="CASCADE"), nullable=False
    )
    role: str = Column(String(50), default="assigned")
    status: str = Column(String(50), default="pending")
    proposed_fee: Optional[Decimal] = Column(Numeric(15, 2), nullable=True)
    agreed_fee: Optional[Decimal] = Column(Numeric(15, 2), nullable=True)
    fee_currency: str = Column(String(10), default="EUR")
    assigned_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    responded_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        """String representation of LdCaseSpecialist."""
        return f"<LdCaseSpecialist(id={self.id}, case_id={self.case_id}, specialist_id={self.specialist_id})>"
