"""Pydantic DTOs for person requests and responses."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class PersonType(str, Enum):
    """Enum for person types within a restaurant."""

    EMPLOYEE = "employee"
    SUPPLIER = "supplier"
    OWNER = "owner"


class PersonCreateDTO(BaseModel):
    """DTO for person creation request."""

    restaurant_id: UUID = Field(..., description="Restaurant UUID this person belongs to")
    name: str = Field(..., min_length=1, max_length=255, description="Person full name")
    role: str = Field(..., min_length=1, max_length=100, description="Person role (e.g., chef, mesero)")
    email: Optional[EmailStr] = Field(None, description="Person email address")
    whatsapp: Optional[str] = Field(None, max_length=50, description="WhatsApp number (international format)")
    type: PersonType = Field(PersonType.EMPLOYEE, description="Person type: employee, supplier, or owner")


class PersonUpdateDTO(BaseModel):
    """DTO for person update request (partial update)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Person full name")
    role: Optional[str] = Field(None, min_length=1, max_length=100, description="Person role")
    email: Optional[EmailStr] = Field(None, description="Person email address")
    whatsapp: Optional[str] = Field(None, max_length=50, description="WhatsApp number")
    type: Optional[PersonType] = Field(None, description="Person type")


class PersonResponseDTO(BaseModel):
    """DTO for person information in responses."""

    id: UUID = Field(..., description="Person unique identifier")
    restaurant_id: UUID = Field(..., description="Restaurant UUID")
    name: str = Field(..., description="Person full name")
    role: str = Field(..., description="Person role")
    email: Optional[str] = Field(None, description="Person email address")
    whatsapp: Optional[str] = Field(None, description="WhatsApp number")
    type: str = Field(..., description="Person type")
    created_at: datetime = Field(..., description="Person creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Person last update timestamp")

    model_config = {"from_attributes": True}
