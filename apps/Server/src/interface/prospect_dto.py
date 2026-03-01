"""Pydantic DTOs for prospect requests and responses."""

from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProspectCreateDTO(BaseModel):
    """DTO for creating a new prospect."""

    entity_id: UUID = Field(..., description="Entity ID this prospect belongs to")
    company_name: str = Field(
        ..., min_length=1, max_length=255, description="Prospect company/organization name"
    )
    contact_name: Optional[str] = Field(None, max_length=255, description="Primary contact person name")
    contact_email: Optional[str] = Field(None, max_length=255, description="Primary contact email")
    contact_phone: Optional[str] = Field(None, max_length=100, description="Primary contact phone")
    stage: Literal["lead", "contacted", "qualified", "proposal", "negotiation", "won", "lost"] = Field(
        "lead", description="Pipeline stage"
    )
    estimated_value: Optional[Decimal] = Field(None, ge=0, description="Estimated deal value")
    source: Optional[str] = Field(None, max_length=100, description="Where the prospect came from")
    notes: Optional[str] = Field(None, description="Free-form notes about the prospect")


class ProspectUpdateDTO(BaseModel):
    """DTO for updating an existing prospect."""

    company_name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Prospect company/organization name"
    )
    contact_name: Optional[str] = Field(None, max_length=255, description="Primary contact person name")
    contact_email: Optional[str] = Field(None, max_length=255, description="Primary contact email")
    contact_phone: Optional[str] = Field(None, max_length=100, description="Primary contact phone")
    stage: Optional[
        Literal["lead", "contacted", "qualified", "proposal", "negotiation", "won", "lost"]
    ] = Field(None, description="Pipeline stage")
    estimated_value: Optional[Decimal] = Field(None, ge=0, description="Estimated deal value")
    source: Optional[str] = Field(None, max_length=100, description="Where the prospect came from")
    notes: Optional[str] = Field(None, description="Free-form notes about the prospect")
    is_active: Optional[bool] = Field(None, description="Active status (soft delete flag)")


class ProspectResponseDTO(BaseModel):
    """DTO for prospect response."""

    id: UUID = Field(..., description="Prospect unique identifier")
    entity_id: UUID = Field(..., description="Entity ID this prospect belongs to")
    company_name: str = Field(..., description="Prospect company/organization name")
    contact_name: Optional[str] = Field(None, description="Primary contact person name")
    contact_email: Optional[str] = Field(None, description="Primary contact email")
    contact_phone: Optional[str] = Field(None, description="Primary contact phone")
    stage: str = Field(..., description="Pipeline stage")
    estimated_value: Optional[Decimal] = Field(None, description="Estimated deal value")
    source: Optional[str] = Field(None, description="Where the prospect came from")
    notes: Optional[str] = Field(None, description="Free-form notes about the prospect")
    is_active: bool = Field(..., description="Active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {"from_attributes": True}


class ProspectListResponseDTO(BaseModel):
    """DTO for prospect list response."""

    prospects: List[ProspectResponseDTO] = Field(..., description="List of prospects")
    total: int = Field(..., description="Total number of prospects matching filters")


class ProspectFilterDTO(BaseModel):
    """DTO for filtering prospects."""

    stage: Optional[
        Literal["lead", "contacted", "qualified", "proposal", "negotiation", "won", "lost"]
    ] = Field(None, description="Filter by pipeline stage")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    source: Optional[str] = Field(None, description="Filter by prospect source")
