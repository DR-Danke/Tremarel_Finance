"""Pydantic DTOs for budget requests and responses."""

from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BudgetCreateDTO(BaseModel):
    """DTO for creating a new budget."""

    entity_id: UUID = Field(..., description="Entity ID this budget belongs to")
    category_id: UUID = Field(..., description="Category ID for the budget (must be expense type)")
    amount: Decimal = Field(..., gt=0, description="Budget amount (must be positive)")
    period_type: Literal["monthly", "quarterly", "yearly"] = Field(
        ..., description="Budget period type"
    )
    start_date: date_type = Field(..., description="Budget start date")


class BudgetUpdateDTO(BaseModel):
    """DTO for updating an existing budget."""

    amount: Optional[Decimal] = Field(None, gt=0, description="Budget amount (must be positive)")
    period_type: Optional[Literal["monthly", "quarterly", "yearly"]] = Field(
        None, description="Budget period type"
    )
    start_date: Optional[date_type] = Field(None, description="Budget start date")
    is_active: Optional[bool] = Field(None, description="Whether the budget is active")


class BudgetResponseDTO(BaseModel):
    """DTO for budget response."""

    id: UUID = Field(..., description="Budget unique identifier")
    entity_id: UUID = Field(..., description="Entity ID this budget belongs to")
    category_id: UUID = Field(..., description="Category ID for the budget")
    amount: Decimal = Field(..., description="Budget amount")
    period_type: str = Field(..., description="Budget period type (monthly, quarterly, yearly)")
    start_date: date_type = Field(..., description="Budget start date")
    end_date: Optional[date_type] = Field(None, description="Budget end date (calculated)")
    is_active: bool = Field(..., description="Whether the budget is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {"from_attributes": True}


class BudgetWithSpendingDTO(BaseModel):
    """DTO for budget response with spending information."""

    id: UUID = Field(..., description="Budget unique identifier")
    entity_id: UUID = Field(..., description="Entity ID this budget belongs to")
    category_id: UUID = Field(..., description="Category ID for the budget")
    category_name: Optional[str] = Field(None, description="Category name for display")
    amount: Decimal = Field(..., description="Budget amount")
    period_type: str = Field(..., description="Budget period type (monthly, quarterly, yearly)")
    start_date: date_type = Field(..., description="Budget start date")
    end_date: Optional[date_type] = Field(None, description="Budget end date (calculated)")
    is_active: bool = Field(..., description="Whether the budget is active")
    spent_amount: Decimal = Field(default=Decimal("0.00"), description="Amount spent in this period")
    spent_percentage: Decimal = Field(
        default=Decimal("0.00"), description="Percentage of budget spent"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {"from_attributes": True}


class BudgetListResponseDTO(BaseModel):
    """DTO for paginated budget list response."""

    budgets: List[BudgetWithSpendingDTO] = Field(..., description="List of budgets with spending")
    total: int = Field(..., description="Total number of budgets")
