"""SQLAlchemy Resource model for RestaurantOS entity."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID

from src.config.database import Base


class Resource(Base):
    """
    Resource model for RestaurantOS.

    Represents products (ingredients), assets (equipment), or services
    within a restaurant. Tracks current stock levels and minimum thresholds.
    Scoped to a restaurant via restaurant_id for multi-tenant isolation.
    Maps to the resource table in PostgreSQL database.
    """

    __tablename__ = "resource"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("restaurant.id"), nullable=False
    )
    type: str = Column(String(50), nullable=False, default="producto")
    name: str = Column(String(255), nullable=False)
    unit: str = Column(String(50), nullable=False)
    current_stock: Decimal = Column(Numeric(12, 4), nullable=False, default=0)
    minimum_stock: Decimal = Column(Numeric(12, 4), nullable=False, default=0)
    last_unit_cost: Decimal = Column(Numeric(12, 4), default=0)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of Resource."""
        return f"<Resource(id={self.id}, name={self.name}, type={self.type}, restaurant_id={self.restaurant_id})>"
