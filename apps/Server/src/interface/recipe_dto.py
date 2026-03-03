"""Pydantic DTOs for recipe requests and responses."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RecipeItemCreateDTO(BaseModel):
    """DTO for recipe item creation within a recipe."""

    resource_id: UUID = Field(..., description="Resource UUID (ingredient)")
    quantity: Decimal = Field(..., gt=0, description="Quantity of the resource")
    unit: str = Field(..., min_length=1, max_length=50, description="Unit of measurement")


class RecipeItemResponseDTO(BaseModel):
    """DTO for recipe item in responses."""

    id: UUID = Field(..., description="Recipe item unique identifier")
    resource_id: UUID = Field(..., description="Resource UUID")
    quantity: Decimal = Field(..., description="Quantity of the resource")
    unit: str = Field(..., description="Unit of measurement")
    created_at: datetime = Field(..., description="Recipe item creation timestamp")

    model_config = {"from_attributes": True}


class RecipeCreateDTO(BaseModel):
    """DTO for recipe creation request."""

    restaurant_id: UUID = Field(..., description="Restaurant UUID this recipe belongs to")
    name: str = Field(..., min_length=1, max_length=255, description="Recipe name")
    sale_price: Decimal = Field(..., gt=0, description="Sale price of the dish")
    is_active: bool = Field(default=True, description="Whether the recipe is active")
    items: list[RecipeItemCreateDTO] = Field(..., min_length=1, description="Recipe ingredients")


class RecipeUpdateDTO(BaseModel):
    """DTO for recipe update request (partial update)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Recipe name")
    sale_price: Optional[Decimal] = Field(None, gt=0, description="Sale price of the dish")
    is_active: Optional[bool] = Field(None, description="Whether the recipe is active")
    items: Optional[list[RecipeItemCreateDTO]] = Field(None, min_length=1, description="Recipe ingredients")


class RecipeResponseDTO(BaseModel):
    """DTO for recipe information in responses."""

    id: UUID = Field(..., description="Recipe unique identifier")
    restaurant_id: UUID = Field(..., description="Restaurant UUID")
    name: str = Field(..., description="Recipe name")
    sale_price: Decimal = Field(..., description="Sale price of the dish")
    current_cost: Decimal = Field(..., description="Computed cost from ingredients")
    margin_percent: Decimal = Field(..., description="Margin percentage")
    is_profitable: bool = Field(..., description="Whether margin >= 60%")
    is_active: bool = Field(..., description="Whether the recipe is active")
    items: list[RecipeItemResponseDTO] = Field(default_factory=list, description="Recipe ingredients")
    created_at: datetime = Field(..., description="Recipe creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Recipe last update timestamp")

    model_config = {"from_attributes": True}
