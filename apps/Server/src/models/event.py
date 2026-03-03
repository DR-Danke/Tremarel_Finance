"""SQLAlchemy Event model for RestaurantOS entity."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.config.database import Base


class Event(Base):
    """
    Event model for RestaurantOS.

    Represents tasks, deadlines, payments, shifts, checklists, and alerts.
    Events can be recurring (daily, weekly, monthly, yearly) and auto-generate
    individual instances linked to a parent event via parent_event_id.
    Scoped to a restaurant via restaurant_id for multi-tenant isolation.
    Maps to the event table in PostgreSQL database.
    """

    __tablename__ = "event"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("restaurant.id", ondelete="CASCADE"), nullable=False
    )
    type: str = Column(String(100), nullable=False)
    description: Optional[str] = Column(Text, nullable=True)
    date: datetime = Column(DateTime, nullable=False)
    frequency: str = Column(String(50), default="none")
    responsible_id: Optional[uuid.UUID] = Column(
        UUID(as_uuid=True), ForeignKey("person.id", ondelete="SET NULL"), nullable=True
    )
    notification_channel: str = Column(String(50), default="email")
    status: str = Column(String(50), default="pending")
    related_document_id: Optional[uuid.UUID] = Column(UUID(as_uuid=True), nullable=True)
    parent_event_id: Optional[uuid.UUID] = Column(
        UUID(as_uuid=True), ForeignKey("event.id", ondelete="CASCADE"), nullable=True
    )
    completed_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of Event."""
        return f"<Event(id={self.id}, type={self.type}, restaurant_id={self.restaurant_id})>"
