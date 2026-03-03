"""Pydantic DTOs for inventory movement requests and responses."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MovementType(str, Enum):
    """Enum for inventory movement types."""

    ENTRY = "entry"
    EXIT = "exit"


class MovementReason(str, Enum):
    """Enum for inventory movement reasons."""

    COMPRA = "compra"
    USO = "uso"
    PRODUCCION = "produccion"
    MERMA = "merma"
    RECETA = "receta"
    AJUSTE = "ajuste"


class InventoryMovementCreateDTO(BaseModel):
    """DTO for inventory movement creation request."""

    resource_id: UUID = Field(..., description="Resource UUID affected by this movement")
    type: MovementType = Field(..., description="Movement type: entry or exit")
    quantity: Decimal = Field(..., gt=0, description="Quantity moved (must be greater than 0)")
    reason: MovementReason = Field(..., description="Reason for the movement")
    date: Optional[datetime] = Field(None, description="Movement date (defaults to now)")
    person_id: Optional[UUID] = Field(None, description="Person UUID who performed the movement")
    restaurant_id: UUID = Field(..., description="Restaurant UUID this movement belongs to")
    notes: Optional[str] = Field(None, description="Additional notes about the movement")


class InventoryMovementResponseDTO(BaseModel):
    """DTO for inventory movement information in responses."""

    id: UUID = Field(..., description="Movement unique identifier")
    resource_id: UUID = Field(..., description="Resource UUID")
    type: str = Field(..., description="Movement type (entry/exit)")
    quantity: Decimal = Field(..., description="Quantity moved")
    reason: str = Field(..., description="Reason for the movement")
    date: Optional[datetime] = Field(None, description="Movement date")
    person_id: Optional[UUID] = Field(None, description="Person UUID")
    restaurant_id: UUID = Field(..., description="Restaurant UUID")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: datetime = Field(..., description="Record creation timestamp")

    model_config = {"from_attributes": True}
