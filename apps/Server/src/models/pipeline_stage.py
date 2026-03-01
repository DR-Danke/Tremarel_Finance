"""SQLAlchemy PipelineStage model for CRM pipeline stage configuration."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from src.config.database import Base


class PipelineStage(Base):
    """
    PipelineStage model for configurable pipeline stages per entity.

    Maps to the pipeline_stages table in PostgreSQL database.
    Entity-scoped via entity_id foreign key. Ordered by order_index for Kanban display.
    """

    __tablename__ = "pipeline_stages"
    __table_args__ = (
        UniqueConstraint("entity_id", "name", name="uq_pipeline_stages_entity_name"),
        UniqueConstraint("entity_id", "order_index", name="uq_pipeline_stages_entity_order"),
    )

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: uuid.UUID = Column(
        UUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: str = Column(String(100), nullable=False)
    display_name: str = Column(String(100), nullable=False)
    order_index: int = Column(Integer, nullable=False)
    color: Optional[str] = Column(String(50), nullable=True)
    is_default: bool = Column(Boolean, default=False)
    is_active: bool = Column(Boolean, default=True, index=True)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of PipelineStage."""
        return f"<PipelineStage(id={self.id}, name={self.name}, order_index={self.order_index})>"
