"""SQLAlchemy Recipe and RecipeItem models for RestaurantOS entity."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID

from src.config.database import Base


class Recipe(Base):
    """
    Recipe model for RestaurantOS.

    Represents a menu dish with a sale price and computed cost/margin fields.
    Contains RecipeItems that link to Resource ingredients with quantities.
    Scoped to a restaurant via restaurant_id for multi-tenant isolation.
    Maps to the recipe table in PostgreSQL database.
    """

    __tablename__ = "recipe"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    restaurant_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("restaurant.id"), nullable=False
    )
    name: str = Column(String(255), nullable=False)
    sale_price: Decimal = Column(Numeric(12, 2), nullable=False)
    current_cost: Decimal = Column(Numeric(12, 2), nullable=False, default=0)
    margin_percent: Decimal = Column(Numeric(5, 2), nullable=False, default=0)
    is_profitable: bool = Column(Boolean, nullable=False, default=True)
    is_active: bool = Column(Boolean, nullable=False, default=True)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of Recipe."""
        return f"<Recipe(id={self.id}, name={self.name}, sale_price={self.sale_price}, restaurant_id={self.restaurant_id})>"


class RecipeItem(Base):
    """
    RecipeItem model for RestaurantOS.

    Represents an ingredient line in a recipe, linking to a Resource with a quantity.
    Uses ON DELETE CASCADE from recipe and ON DELETE RESTRICT from resource.
    Maps to the recipe_item table in PostgreSQL database.
    """

    __tablename__ = "recipe_item"

    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("recipe.id", ondelete="CASCADE"), nullable=False
    )
    resource_id: uuid.UUID = Column(
        UUID(as_uuid=True), ForeignKey("resource.id", ondelete="RESTRICT"), nullable=False
    )
    quantity: Decimal = Column(Numeric(12, 4), nullable=False)
    unit: str = Column(String(50), nullable=False)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of RecipeItem."""
        return f"<RecipeItem(id={self.id}, recipe_id={self.recipe_id}, resource_id={self.resource_id}, quantity={self.quantity})>"
