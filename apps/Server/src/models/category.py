"""SQLAlchemy Category model for hierarchical income/expense categories."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.config.database import Base


class Category(Base):
    """
    Category model for hierarchical income/expense categories.

    Maps to the categories table in PostgreSQL database.
    Supports parent-child relationships via parent_id for tree structure.
    """

    __tablename__ = "categories"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_id: uuid.UUID = Column(
        UUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: str = Column(String(255), nullable=False)
    type: str = Column(String(50), nullable=False)  # 'income' or 'expense'
    parent_id: Optional[uuid.UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    description: Optional[str] = Column(Text, nullable=True)
    color: Optional[str] = Column(String(50), nullable=True)
    icon: Optional[str] = Column(String(100), nullable=True)
    is_active: bool = Column(Boolean, default=True, nullable=False, index=True)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of Category."""
        return f"<Category(id={self.id}, name={self.name}, type={self.type}, entity_id={self.entity_id})>"
