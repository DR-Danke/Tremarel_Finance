"""Pydantic DTOs for restaurant requests and responses."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RestaurantCreateDTO(BaseModel):
    """DTO for restaurant creation request."""

    name: str = Field(..., min_length=1, max_length=255, description="Restaurant name")
    address: Optional[str] = Field(None, description="Restaurant address")


class RestaurantUpdateDTO(BaseModel):
    """DTO for restaurant update request (partial update)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Restaurant name")
    address: Optional[str] = Field(None, description="Restaurant address")


class RestaurantResponseDTO(BaseModel):
    """DTO for restaurant information in responses."""

    id: UUID = Field(..., description="Restaurant unique identifier")
    name: str = Field(..., description="Restaurant name")
    address: Optional[str] = Field(None, description="Restaurant address")
    owner_id: Optional[UUID] = Field(None, description="Restaurant owner user identifier")
    created_at: datetime = Field(..., description="Restaurant creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Restaurant last update timestamp")

    model_config = {"from_attributes": True}


class RestaurantListDTO(BaseModel):
    """DTO for a list of restaurants."""

    restaurants: list[RestaurantResponseDTO] = Field(..., description="List of restaurants")
