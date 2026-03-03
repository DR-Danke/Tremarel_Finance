"""SQLAlchemy UserRestaurant model for user-restaurant membership."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from src.config.database import Base


class UserRestaurant(Base):
    """
    UserRestaurant model for many-to-many relationship between users and restaurants.

    Each user can belong to multiple restaurants with different roles per restaurant.
    Maps to the user_restaurants table in PostgreSQL database.
    """

    __tablename__ = "user_restaurants"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: uuid.UUID = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    restaurant_id: uuid.UUID = Column(
        UUID(as_uuid=True),
        ForeignKey("restaurant.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: str = Column(String(50), nullable=False, default="user")
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "restaurant_id", name="user_restaurants_unique"),
    )

    def __repr__(self) -> str:
        """String representation of UserRestaurant."""
        return f"<UserRestaurant(id={self.id}, user_id={self.user_id}, restaurant_id={self.restaurant_id}, role={self.role})>"
