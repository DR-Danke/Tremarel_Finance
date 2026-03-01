"""Pydantic DTOs for pipeline stage requests and responses."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PipelineStageCreateDTO(BaseModel):
    """DTO for creating a new pipeline stage."""

    entity_id: UUID = Field(..., description="Entity ID this stage belongs to")
    name: str = Field(
        ..., min_length=1, max_length=100, description="Machine-readable stage identifier"
    )
    display_name: str = Field(
        ..., min_length=1, max_length=100, description="Human-readable stage label"
    )
    order_index: int = Field(..., ge=0, description="Position in Kanban display (0-based)")
    color: Optional[str] = Field(None, max_length=50, description="Hex color for UI display")
    is_default: bool = Field(False, description="Whether this is the initial stage for new prospects")


class PipelineStageUpdateDTO(BaseModel):
    """DTO for updating an existing pipeline stage."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Machine-readable stage identifier"
    )
    display_name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Human-readable stage label"
    )
    order_index: Optional[int] = Field(None, ge=0, description="Position in Kanban display (0-based)")
    color: Optional[str] = Field(None, max_length=50, description="Hex color for UI display")
    is_default: Optional[bool] = Field(None, description="Whether this is the initial stage for new prospects")
    is_active: Optional[bool] = Field(None, description="Active status (soft delete flag)")


class PipelineStageResponseDTO(BaseModel):
    """DTO for pipeline stage response."""

    id: UUID = Field(..., description="Pipeline stage unique identifier")
    entity_id: UUID = Field(..., description="Entity ID this stage belongs to")
    name: str = Field(..., description="Machine-readable stage identifier")
    display_name: str = Field(..., description="Human-readable stage label")
    order_index: int = Field(..., description="Position in Kanban display")
    color: Optional[str] = Field(None, description="Hex color for UI display")
    is_default: bool = Field(..., description="Whether this is the initial stage")
    is_active: bool = Field(..., description="Active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {"from_attributes": True}


class PipelineStageListResponseDTO(BaseModel):
    """DTO for pipeline stage list response."""

    stages: List[PipelineStageResponseDTO] = Field(..., description="List of pipeline stages")
    total: int = Field(..., description="Total number of stages matching filters")
