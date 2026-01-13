"""Pydantic DTOs for category requests and responses."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CategoryCreateDTO(BaseModel):
    """DTO for category creation request."""

    entity_id: UUID = Field(..., description="Entity ID the category belongs to")
    name: str = Field(..., min_length=1, max_length=255, description="Category name")
    type: str = Field(..., description="Category type: 'income' or 'expense'")
    parent_id: Optional[UUID] = Field(None, description="Parent category ID for subcategories")
    description: Optional[str] = Field(None, description="Category description")
    color: Optional[str] = Field(None, max_length=50, description="Category color for UI display")
    icon: Optional[str] = Field(None, max_length=100, description="Category icon identifier")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate that type is either 'income' or 'expense'."""
        if v not in ("income", "expense"):
            raise ValueError("Type must be 'income' or 'expense'")
        return v


class CategoryUpdateDTO(BaseModel):
    """DTO for category update request."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Category name")
    parent_id: Optional[UUID] = Field(None, description="Parent category ID for subcategories")
    description: Optional[str] = Field(None, description="Category description")
    color: Optional[str] = Field(None, max_length=50, description="Category color for UI display")
    icon: Optional[str] = Field(None, max_length=100, description="Category icon identifier")
    is_active: Optional[bool] = Field(None, description="Whether the category is active")


class CategoryResponseDTO(BaseModel):
    """DTO for category response."""

    id: UUID = Field(..., description="Category unique identifier")
    entity_id: UUID = Field(..., description="Entity ID the category belongs to")
    name: str = Field(..., description="Category name")
    type: str = Field(..., description="Category type: 'income' or 'expense'")
    parent_id: Optional[UUID] = Field(None, description="Parent category ID")
    description: Optional[str] = Field(None, description="Category description")
    color: Optional[str] = Field(None, description="Category color for UI display")
    icon: Optional[str] = Field(None, description="Category icon identifier")
    is_active: bool = Field(..., description="Whether the category is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {"from_attributes": True}


class CategoryTreeDTO(BaseModel):
    """DTO for category with nested children for tree display."""

    id: UUID = Field(..., description="Category unique identifier")
    entity_id: UUID = Field(..., description="Entity ID the category belongs to")
    name: str = Field(..., description="Category name")
    type: str = Field(..., description="Category type: 'income' or 'expense'")
    parent_id: Optional[UUID] = Field(None, description="Parent category ID")
    description: Optional[str] = Field(None, description="Category description")
    color: Optional[str] = Field(None, description="Category color for UI display")
    icon: Optional[str] = Field(None, description="Category icon identifier")
    is_active: bool = Field(..., description="Whether the category is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    children: List["CategoryTreeDTO"] = Field(default_factory=list, description="Child categories")

    model_config = {"from_attributes": True}


# Rebuild model to resolve forward reference for children
CategoryTreeDTO.model_rebuild()
