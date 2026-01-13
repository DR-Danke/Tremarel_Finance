"""SQLAlchemy Budget model for budget tracking per category."""

import uuid
from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID

from src.config.database import Base


class Budget(Base):
    """
    Budget model for tracking spending limits per category.

    Maps to the budgets table in PostgreSQL database.
    """

    __tablename__ = "budgets"

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
    amount: Decimal = Column(Numeric(15, 2), nullable=False)
    period_type: str = Column(String(50), nullable=False)
    start_date: date_type = Column(Date, nullable=False)
    end_date: Optional[date_type] = Column(Date, nullable=True)
    is_active: bool = Column(Boolean, default=True, index=True)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of Budget."""
        return f"<Budget(id={self.id}, category_id={self.category_id}, amount={self.amount}, period={self.period_type})>"
