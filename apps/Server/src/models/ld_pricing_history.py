"""SQLAlchemy LdPricingHistory model for case pricing audit trail."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text

from src.config.database import Base


class LdPricingHistory(Base):
    """
    Legal Desk pricing history model.

    Tracks pricing negotiation changes per case for audit purposes.
    Maps to the ld_pricing_history table in PostgreSQL database.
    """

    __tablename__ = "ld_pricing_history"

    id: int = Column(Integer, primary_key=True)
    case_id: int = Column(
        Integer, ForeignKey("ld_cases.id", ondelete="CASCADE"), nullable=False
    )
    action: str = Column(String(100), nullable=False)
    previous_amount: Optional[Decimal] = Column(Numeric(15, 2), nullable=True)
    new_amount: Optional[Decimal] = Column(Numeric(15, 2), nullable=True)
    currency: str = Column(String(10), default="EUR")
    changed_by: Optional[str] = Column(String(255), nullable=True)
    notes: Optional[str] = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of LdPricingHistory."""
        return f"<LdPricingHistory(id={self.id}, case_id={self.case_id}, action={self.action})>"
