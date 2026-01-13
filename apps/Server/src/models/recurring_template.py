"""SQLAlchemy RecurringTemplate model for recurring transaction templates."""

import uuid
from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.config.database import Base


class RecurringTemplate(Base):
    """
    RecurringTemplate model for recurring transaction templates.

    Maps to the recurring_templates table in PostgreSQL database.
    Stores templates for recurring income/expense transactions with
    frequency patterns (daily, weekly, monthly, yearly).
    """

    __tablename__ = "recurring_templates"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: uuid.UUID = Column(
        UUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: uuid.UUID = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: str = Column(String(255), nullable=False)
    amount: Decimal = Column(Numeric(15, 2), nullable=False)
    type: str = Column(String(50), nullable=False)
    description: Optional[str] = Column(Text, nullable=True)
    notes: Optional[str] = Column(Text, nullable=True)
    frequency: str = Column(String(50), nullable=False)
    start_date: date_type = Column(Date, nullable=False)
    end_date: Optional[date_type] = Column(Date, nullable=True)
    is_active: bool = Column(Boolean, default=True, index=True)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of RecurringTemplate."""
        return f"<RecurringTemplate(id={self.id}, name={self.name}, frequency={self.frequency})>"
