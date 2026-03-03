"""SQLAlchemy InventoryMovement model for RestaurantOS entity."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.config.database import Base


class InventoryMovement(Base):
    """
    InventoryMovement model for RestaurantOS.

    Records stock changes (entries and exits) for resources within a restaurant.
    Each movement affects a resource's current_stock and tracks who performed it,
    the reason, and any additional notes.
    Maps to the inventory_movement table in PostgreSQL database.
    """

    __tablename__ = "inventory_movement"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("resource.id", ondelete="CASCADE"), nullable=False
    )
    type: str = Column(String(20), nullable=False)
    quantity: Decimal = Column(Numeric(12, 4), nullable=False)
    reason: str = Column(String(100), nullable=False)
    date: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    person_id: Optional[uuid.UUID] = Column(
        UUID(as_uuid=True), ForeignKey("person.id", ondelete="SET NULL"), nullable=True
    )
    restaurant_id: uuid.UUID = Column(UUID(as_uuid=True), nullable=False)
    notes: Optional[str] = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of InventoryMovement."""
        return f"<InventoryMovement(id={self.id}, resource_id={self.resource_id}, type={self.type}, quantity={self.quantity})>"
