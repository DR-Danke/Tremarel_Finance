"""SQLAlchemy Prospect model for CRM pipeline tracking."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.config.database import Base


class Prospect(Base):
    """
    Prospect model for CRM pipeline companies/contacts.

    Maps to the prospects table in PostgreSQL database.
    Entity-scoped via entity_id foreign key.
    """

    __tablename__ = "prospects"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: uuid.UUID = Column(
        UUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_name: str = Column(String(255), nullable=False)
    contact_name: Optional[str] = Column(String(255), nullable=True)
    contact_email: Optional[str] = Column(String(255), nullable=True)
    contact_phone: Optional[str] = Column(String(100), nullable=True)
    stage: str = Column(String(50), nullable=False, default="lead", index=True)
    estimated_value: Optional[Decimal] = Column(Numeric(15, 2), nullable=True)
    source: Optional[str] = Column(String(100), nullable=True)
    notes: Optional[str] = Column(Text, nullable=True)
    is_active: bool = Column(Boolean, default=True, index=True)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of Prospect."""
        return f"<Prospect(id={self.id}, company_name={self.company_name}, stage={self.stage})>"
