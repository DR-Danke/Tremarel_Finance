"""SQLAlchemy NotificationLog model for notification audit trail."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.config.database import Base


class NotificationLog(Base):
    """
    NotificationLog model for notification audit trail.

    Stores all notification send attempts with channel, recipient, message,
    status, and optional error details. Scoped to a restaurant via restaurant_id
    for multi-tenant isolation.
    Maps to the notification_log table in PostgreSQL database.
    """

    __tablename__ = "notification_log"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("restaurant.id", ondelete="CASCADE"), nullable=False
    )
    channel: str = Column(String(50), nullable=False)
    recipient: str = Column(String(255), nullable=False)
    message: Optional[str] = Column(Text, nullable=True)
    status: str = Column(String(50), nullable=False)
    error_message: Optional[str] = Column(Text, nullable=True)
    event_id: Optional[uuid.UUID] = Column(
        UUID(as_uuid=True), ForeignKey("event.id", ondelete="SET NULL"), nullable=True
    )
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of NotificationLog."""
        return f"<NotificationLog(id={self.id}, channel={self.channel}, status={self.status})>"
