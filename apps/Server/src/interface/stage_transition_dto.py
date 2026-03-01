"""Pydantic DTOs for stage transition requests and responses."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class StageTransitionCreateDTO(BaseModel):
    """DTO for creating a new stage transition record."""

    prospect_id: UUID = Field(..., description="Prospect being transitioned")
    entity_id: UUID = Field(..., description="Entity ID for scoping")
    from_stage_id: Optional[UUID] = Field(None, description="Previous stage (null for initial assignment)")
    to_stage_id: UUID = Field(..., description="Target stage")
    transitioned_by: Optional[UUID] = Field(None, description="User who triggered the change")
    notes: Optional[str] = Field(None, description="Optional transition notes")


class StageTransitionResponseDTO(BaseModel):
    """DTO for stage transition response."""

    id: UUID = Field(..., description="Transition unique identifier")
    prospect_id: UUID = Field(..., description="Prospect being transitioned")
    entity_id: UUID = Field(..., description="Entity ID for scoping")
    from_stage_id: Optional[UUID] = Field(None, description="Previous stage")
    to_stage_id: UUID = Field(..., description="Target stage")
    transitioned_by: Optional[UUID] = Field(None, description="User who triggered the change")
    notes: Optional[str] = Field(None, description="Transition notes")
    created_at: datetime = Field(..., description="When the transition occurred")

    model_config = {"from_attributes": True}


class StageTransitionListResponseDTO(BaseModel):
    """DTO for stage transition list response."""

    transitions: List[StageTransitionResponseDTO] = Field(..., description="List of stage transitions")
    total: int = Field(..., description="Total number of transitions")
