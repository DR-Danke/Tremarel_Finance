"""SQLAlchemy LdCaseDeliverable model for case deliverables."""

from datetime import date as date_type
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.config.database import Base


class LdCaseDeliverable(Base):
    """
    Legal Desk case deliverable model.

    Tracks deliverables for a case with status and completion timestamps.
    Maps to the ld_case_deliverables table in PostgreSQL database.
    """

    __tablename__ = "ld_case_deliverables"

    id: int = Column(Integer, primary_key=True)
    case_id: int = Column(
        Integer, ForeignKey("ld_cases.id", ondelete="CASCADE"), nullable=False
    )
    specialist_id: Optional[int] = Column(
        Integer, ForeignKey("ld_specialists.id", ondelete="SET NULL"), nullable=True
    )
    title: str = Column(String(500), nullable=False)
    description: Optional[str] = Column(Text, nullable=True)
    status: str = Column(String(50), default="pending")
    due_date: Optional[date_type] = Column(Date, nullable=True)
    completed_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    specialist = relationship("LdSpecialist")

    def __repr__(self) -> str:
        """String representation of LdCaseDeliverable."""
        return f"<LdCaseDeliverable(id={self.id}, case_id={self.case_id}, title={self.title})>"
