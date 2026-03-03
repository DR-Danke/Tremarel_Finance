"""SQLAlchemy Document model for RestaurantOS entity."""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Column, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.config.database import Base


class Document(Base):
    """
    Document model for RestaurantOS.

    Represents legal or administrative artifacts — contracts, permits,
    invoices, licenses. Can be linked to a person via person_id FK.
    Has expiration tracking with automatic status calculation.
    Scoped to a restaurant via restaurant_id for multi-tenant isolation.
    Maps to the document table in PostgreSQL database.
    """

    __tablename__ = "document"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("restaurant.id"), nullable=False
    )
    type: str = Column(String(100), nullable=False)
    file_url: Optional[str] = Column(Text, nullable=True)
    issue_date: Optional[date] = Column(Date, nullable=True)
    expiration_date: Optional[date] = Column(Date, nullable=True)
    person_id: Optional[uuid.UUID] = Column(
        UUID(as_uuid=True), ForeignKey("person.id"), nullable=True
    )
    description: Optional[str] = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of Document."""
        return f"<Document(id={self.id}, type={self.type}, restaurant_id={self.restaurant_id})>"
