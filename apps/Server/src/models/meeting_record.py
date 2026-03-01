"""SQLAlchemy MeetingRecord model for CRM meeting tracking."""

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.config.database import Base


class MeetingRecord(Base):
    """
    MeetingRecord model for processed meeting records linked to prospects.

    Maps to the meeting_records table in PostgreSQL database.
    Entity-scoped via entity_id, linked to prospect via prospect_id.
    """

    __tablename__ = "meeting_records"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: uuid.UUID = Column(
        UUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    prospect_id: uuid.UUID = Column(
        UUID(as_uuid=True),
        ForeignKey("prospects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: str = Column(String(500), nullable=False)
    transcript_ref: Optional[str] = Column(String(1000), nullable=True)
    summary: Optional[str] = Column(Text, nullable=True)
    action_items: Optional[str] = Column(Text, nullable=True)
    participants: Optional[str] = Column(Text, nullable=True)
    html_output: Optional[str] = Column(Text, nullable=True)
    meeting_date: Optional[date] = Column(Date, nullable=True)
    is_active: bool = Column(Boolean, default=True, index=True)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of MeetingRecord."""
        return f"<MeetingRecord(id={self.id}, title={self.title}, prospect_id={self.prospect_id})>"
