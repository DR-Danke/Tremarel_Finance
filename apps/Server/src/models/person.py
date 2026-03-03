"""SQLAlchemy Person model for RestaurantOS entity."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from src.config.database import Base


class Person(Base):
    """
    Person model for RestaurantOS.

    Represents employees, suppliers, or owners within a restaurant.
    Scoped to a restaurant via restaurant_id for multi-tenant isolation.
    Maps to the person table in PostgreSQL database.
    """

    __tablename__ = "person"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("restaurant.id"), nullable=False
    )
    name: str = Column(String(255), nullable=False)
    role: str = Column(String(100), nullable=False)
    email: Optional[str] = Column(String(255), nullable=True)
    whatsapp: Optional[str] = Column(String(50), nullable=True)
    type: str = Column(String(50), nullable=False, default="employee")
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of Person."""
        return f"<Person(id={self.id}, name={self.name}, type={self.type}, restaurant_id={self.restaurant_id})>"
