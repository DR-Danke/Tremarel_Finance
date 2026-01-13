"""SQLAlchemy UserEntity model for user-entity membership."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from src.config.database import Base


class UserEntity(Base):
    """
    UserEntity model for many-to-many relationship between users and entities.

    Each user can belong to multiple entities with different roles per entity.
    Maps to the user_entities table in PostgreSQL database.
    """

    __tablename__ = "user_entities"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: uuid.UUID = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    entity_id: uuid.UUID = Column(
        UUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: str = Column(String(50), nullable=False, default="user")
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "entity_id", name="user_entities_unique"),
    )

    def __repr__(self) -> str:
        """String representation of UserEntity."""
        return f"<UserEntity(id={self.id}, user_id={self.user_id}, entity_id={self.entity_id}, role={self.role})>"
