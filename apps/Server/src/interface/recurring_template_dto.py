"""Pydantic DTOs for recurring template requests and responses."""

from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class RecurringTemplateCreateDTO(BaseModel):
    """DTO for creating a new recurring template."""

    entity_id: UUID = Field(..., description="Entity ID this template belongs to")
    category_id: UUID = Field(..., description="Category ID for the template")
    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    amount: Decimal = Field(..., gt=0, description="Template amount (must be positive)")
    type: Literal["income", "expense"] = Field(..., description="Transaction type")
    description: Optional[str] = Field(None, max_length=500, description="Template description")
    notes: Optional[str] = Field(None, description="Additional notes")
    frequency: Literal["daily", "weekly", "monthly", "yearly"] = Field(
        ..., description="Recurrence frequency"
    )
    start_date: date_type = Field(..., description="Start date for recurrence")
    end_date: Optional[date_type] = Field(None, description="End date for recurrence (optional)")

    @field_validator("end_date")
    @classmethod
    def end_date_must_be_after_start_date(
        cls, v: Optional[date_type], info
    ) -> Optional[date_type]:
        """Validate that end_date is after start_date if provided."""
        if v is not None:
            start_date = info.data.get("start_date")
            if start_date and v < start_date:
                raise ValueError("end_date must be after start_date")
        return v


class RecurringTemplateUpdateDTO(BaseModel):
    """DTO for updating an existing recurring template."""

    category_id: Optional[UUID] = Field(None, description="Category ID for the template")
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Template name")
    amount: Optional[Decimal] = Field(None, gt=0, description="Template amount (must be positive)")
    type: Optional[Literal["income", "expense"]] = Field(None, description="Transaction type")
    description: Optional[str] = Field(None, max_length=500, description="Template description")
    notes: Optional[str] = Field(None, description="Additional notes")
    frequency: Optional[Literal["daily", "weekly", "monthly", "yearly"]] = Field(
        None, description="Recurrence frequency"
    )
    start_date: Optional[date_type] = Field(None, description="Start date for recurrence")
    end_date: Optional[date_type] = Field(None, description="End date for recurrence (optional)")
    is_active: Optional[bool] = Field(None, description="Whether the template is active")


class RecurringTemplateResponseDTO(BaseModel):
    """DTO for recurring template response."""

    id: UUID = Field(..., description="Template unique identifier")
    entity_id: UUID = Field(..., description="Entity ID this template belongs to")
    category_id: UUID = Field(..., description="Category ID for the template")
    name: str = Field(..., description="Template name")
    amount: Decimal = Field(..., description="Template amount")
    type: str = Field(..., description="Transaction type (income or expense)")
    description: Optional[str] = Field(None, description="Template description")
    notes: Optional[str] = Field(None, description="Additional notes")
    frequency: str = Field(..., description="Recurrence frequency")
    start_date: date_type = Field(..., description="Start date for recurrence")
    end_date: Optional[date_type] = Field(None, description="End date for recurrence")
    is_active: bool = Field(..., description="Whether the template is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {"from_attributes": True}


class RecurringTemplateListResponseDTO(BaseModel):
    """DTO for recurring template list response."""

    templates: List[RecurringTemplateResponseDTO] = Field(
        ..., description="List of recurring templates"
    )
    total: int = Field(..., description="Total number of templates matching filters")
