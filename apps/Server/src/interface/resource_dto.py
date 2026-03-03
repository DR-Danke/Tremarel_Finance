"""Pydantic DTOs for resource requests and responses."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class ResourceType(str, Enum):
    """Enum for resource types within a restaurant."""

    PRODUCTO = "producto"
    ACTIVO = "activo"
    SERVICIO = "servicio"


class ResourceCreateDTO(BaseModel):
    """DTO for resource creation request."""

    restaurant_id: UUID = Field(..., description="Restaurant UUID this resource belongs to")
    type: ResourceType = Field(ResourceType.PRODUCTO, description="Resource type: producto, activo, or servicio")
    name: str = Field(..., min_length=1, max_length=255, description="Resource name")
    unit: str = Field(..., min_length=1, max_length=50, description="Unit of measurement (e.g., kg, litros, unidad)")
    current_stock: Decimal = Field(default=Decimal("0"), ge=0, description="Current stock quantity")
    minimum_stock: Decimal = Field(default=Decimal("0"), ge=0, description="Minimum stock threshold")
    last_unit_cost: Decimal = Field(default=Decimal("0"), ge=0, description="Last unit cost")


class ResourceUpdateDTO(BaseModel):
    """DTO for resource update request (partial update)."""

    type: Optional[ResourceType] = Field(None, description="Resource type")
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Resource name")
    unit: Optional[str] = Field(None, min_length=1, max_length=50, description="Unit of measurement")
    current_stock: Optional[Decimal] = Field(None, ge=0, description="Current stock quantity")
    minimum_stock: Optional[Decimal] = Field(None, ge=0, description="Minimum stock threshold")
    last_unit_cost: Optional[Decimal] = Field(None, ge=0, description="Last unit cost")


class ResourceResponseDTO(BaseModel):
    """DTO for resource information in responses."""

    id: UUID = Field(..., description="Resource unique identifier")
    restaurant_id: UUID = Field(..., description="Restaurant UUID")
    type: str = Field(..., description="Resource type")
    name: str = Field(..., description="Resource name")
    unit: str = Field(..., description="Unit of measurement")
    current_stock: Decimal = Field(..., description="Current stock quantity")
    minimum_stock: Decimal = Field(..., description="Minimum stock threshold")
    last_unit_cost: Decimal = Field(..., description="Last unit cost")
    is_low_stock: bool = Field(False, description="Whether current stock is below minimum")
    created_at: datetime = Field(..., description="Resource creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Resource last update timestamp")

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def compute_is_low_stock(cls, data: object) -> object:
        """Compute is_low_stock from current_stock and minimum_stock."""
        if hasattr(data, "current_stock") and hasattr(data, "minimum_stock"):
            # ORM model object
            current = data.current_stock or Decimal("0")
            minimum = data.minimum_stock or Decimal("0")
            # We need to set is_low_stock as an attribute-like value
            # Convert to dict for modification
            obj_dict = {
                "id": data.id,
                "restaurant_id": data.restaurant_id,
                "type": data.type,
                "name": data.name,
                "unit": data.unit,
                "current_stock": current,
                "minimum_stock": minimum,
                "last_unit_cost": data.last_unit_cost or Decimal("0"),
                "is_low_stock": current < minimum,
                "created_at": data.created_at,
                "updated_at": getattr(data, "updated_at", None),
            }
            return obj_dict
        elif isinstance(data, dict):
            current = data.get("current_stock", Decimal("0")) or Decimal("0")
            minimum = data.get("minimum_stock", Decimal("0")) or Decimal("0")
            data["is_low_stock"] = current < minimum
        return data
