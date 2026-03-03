"""SQLAlchemy Restaurant model for RestaurantOS multi-tenant entity."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.config.database import Base


class Restaurant(Base):
    """
    Restaurant model for RestaurantOS multi-tenant scoping.

    Each restaurant represents a single restaurant location/business.
    All RestaurantOS entities are scoped to a restaurant via restaurant_id.
    Maps to the restaurant table in PostgreSQL database.
    """

    __tablename__ = "restaurant"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = Column(String(255), nullable=False)
    address: Optional[str] = Column(Text, nullable=True)
    owner_id: Optional[uuid.UUID] = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of Restaurant."""
        return f"<Restaurant(id={self.id}, name={self.name}, owner_id={self.owner_id})>"
