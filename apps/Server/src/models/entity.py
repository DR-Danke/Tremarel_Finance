"""SQLAlchemy Entity model for financial tracking contexts."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.config.database import Base


class Entity(Base):
    """
    Entity model for separate financial tracking contexts.

    Each entity represents a separate financial tracking context (family, startup)
    with its own transactions, categories, and budgets.
    Maps to the entities table in PostgreSQL database.
    """

    __tablename__ = "entities"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = Column(String(255), nullable=False)
    type: str = Column(String(50), nullable=False)
    description: Optional[str] = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of Entity."""
        return f"<Entity(id={self.id}, name={self.name}, type={self.type})>"
