"""Pydantic DTOs for entity requests and responses."""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class EntityCreateDTO(BaseModel):
    """DTO for entity creation request."""

    name: str = Field(..., min_length=1, max_length=255, description="Entity name")
    type: Literal["family", "startup"] = Field(..., description="Entity type")
    description: Optional[str] = Field(None, description="Entity description")


class EntityUpdateDTO(BaseModel):
    """DTO for entity update request (partial update)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Entity name")
    description: Optional[str] = Field(None, description="Entity description")


class EntityResponseDTO(BaseModel):
    """DTO for entity information in responses."""

    id: UUID = Field(..., description="Entity unique identifier")
    name: str = Field(..., description="Entity name")
    type: str = Field(..., description="Entity type (family or startup)")
    description: Optional[str] = Field(None, description="Entity description")
    created_at: datetime = Field(..., description="Entity creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Entity last update timestamp")

    model_config = {"from_attributes": True}


class UserEntityCreateDTO(BaseModel):
    """DTO for adding a user to an entity."""

    user_id: UUID = Field(..., description="User unique identifier")
    role: Literal["admin", "manager", "user", "viewer"] = Field(
        default="user",
        description="User role in the entity",
    )


class UserEntityResponseDTO(BaseModel):
    """DTO for user-entity membership in responses."""

    id: UUID = Field(..., description="UserEntity unique identifier")
    user_id: UUID = Field(..., description="User unique identifier")
    entity_id: UUID = Field(..., description="Entity unique identifier")
    role: str = Field(..., description="User role in the entity")
    created_at: datetime = Field(..., description="Membership creation timestamp")

    model_config = {"from_attributes": True}


class EntityMemberDTO(BaseModel):
    """DTO for entity member information with user details."""

    id: UUID = Field(..., description="UserEntity unique identifier")
    user_id: UUID = Field(..., description="User unique identifier")
    email: str = Field(..., description="User email address")
    first_name: Optional[str] = Field(None, description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    role: str = Field(..., description="User role in the entity")
    created_at: datetime = Field(..., description="Membership creation timestamp")
