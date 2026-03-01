"""SQLAlchemy StageTransition model for CRM stage transition audit trail."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID

from src.config.database import Base


class StageTransition(Base):
    """
    StageTransition model for immutable audit records of prospect stage changes.

    Maps to the stage_transitions table in PostgreSQL database.
    Transitions are write-once — no updated_at column.
    """

    __tablename__ = "stage_transitions"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prospect_id: uuid.UUID = Column(
        UUID(as_uuid=True),
        ForeignKey("prospects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entity_id: uuid.UUID = Column(
        UUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_stage_id: Optional[uuid.UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("pipeline_stages.id", ondelete="SET NULL"),
        nullable=True,
    )
    to_stage_id: uuid.UUID = Column(
        UUID(as_uuid=True),
        ForeignKey("pipeline_stages.id", ondelete="SET NULL"),
        nullable=False,
    )
    transitioned_by: Optional[uuid.UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    notes: Optional[str] = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of StageTransition."""
        return f"<StageTransition(id={self.id}, prospect_id={self.prospect_id}, from_stage_id={self.from_stage_id}, to_stage_id={self.to_stage_id})>"
