"""SQLAlchemy LdCase model for Legal Desk case entities."""

from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.config.database import Base


class LdCase(Base):
    """
    Legal Desk case model.

    Core case entity with case number, legal domain, financials, and AI classification.
    Maps to the ld_cases table in PostgreSQL database.
    """

    __tablename__ = "ld_cases"

    id: int = Column(Integer, primary_key=True)
    case_number: str = Column(String(20), unique=True, nullable=False)
    title: str = Column(String(500), nullable=False)
    description: Optional[str] = Column(Text, nullable=True)
    client_id: int = Column(
        Integer, ForeignKey("ld_clients.id", ondelete="CASCADE"), nullable=False
    )
    legal_domain: str = Column(String(100), nullable=False)
    complexity: str = Column(String(50), default="medium")
    priority: str = Column(String(50), default="medium")
    status: str = Column(String(50), default="new")
    budget: Optional[Decimal] = Column(Numeric(15, 2), nullable=True)
    estimated_cost: Optional[Decimal] = Column(Numeric(15, 2), nullable=True)
    final_quote: Optional[Decimal] = Column(Numeric(15, 2), nullable=True)
    margin_percentage: Optional[Decimal] = Column(Numeric(5, 2), nullable=True)
    deadline: Optional[date_type] = Column(Date, nullable=True)
    ai_classification = Column(JSONB, nullable=True)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    specialists = relationship("LdCaseSpecialist", backref="case")
    deliverables = relationship("LdCaseDeliverable", backref="case")
    messages = relationship("LdCaseMessage", backref="case")
    documents = relationship("LdCaseDocument", backref="case")
    pricing_history = relationship("LdPricingHistory", backref="case")
    scores = relationship("LdSpecialistScore", backref="case")

    def __repr__(self) -> str:
        """String representation of LdCase."""
        return f"<LdCase(id={self.id}, case_number={self.case_number}, status={self.status})>"
