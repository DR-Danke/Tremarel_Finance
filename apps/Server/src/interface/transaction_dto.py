"""Pydantic DTOs for transaction requests and responses."""

from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TransactionCreateDTO(BaseModel):
    """DTO for creating a new transaction."""

    entity_id: UUID = Field(..., description="Entity ID this transaction belongs to")
    category_id: UUID = Field(..., description="Category ID for the transaction")
    amount: Decimal = Field(..., gt=0, description="Transaction amount (must be positive)")
    type: Literal["income", "expense"] = Field(..., description="Transaction type")
    description: Optional[str] = Field(None, max_length=500, description="Transaction description")
    date: date_type = Field(..., description="Transaction date")
    notes: Optional[str] = Field(None, description="Additional notes")
    recurring_template_id: Optional[UUID] = Field(
        None, description="Recurring template ID if generated from template"
    )


class TransactionUpdateDTO(BaseModel):
    """DTO for updating an existing transaction."""

    category_id: Optional[UUID] = Field(None, description="Category ID for the transaction")
    amount: Optional[Decimal] = Field(None, gt=0, description="Transaction amount (must be positive)")
    type: Optional[Literal["income", "expense"]] = Field(None, description="Transaction type")
    description: Optional[str] = Field(None, max_length=500, description="Transaction description")
    date: Optional[date_type] = Field(None, description="Transaction date")
    notes: Optional[str] = Field(None, description="Additional notes")


class TransactionResponseDTO(BaseModel):
    """DTO for transaction response."""

    id: UUID = Field(..., description="Transaction unique identifier")
    entity_id: UUID = Field(..., description="Entity ID this transaction belongs to")
    category_id: UUID = Field(..., description="Category ID for the transaction")
    user_id: Optional[UUID] = Field(None, description="User ID who created the transaction")
    recurring_template_id: Optional[UUID] = Field(
        None, description="Recurring template ID if generated from template"
    )
    amount: Decimal = Field(..., description="Transaction amount")
    type: str = Field(..., description="Transaction type (income or expense)")
    description: Optional[str] = Field(None, description="Transaction description")
    date: date_type = Field(..., description="Transaction date")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {"from_attributes": True}


class TransactionListResponseDTO(BaseModel):
    """DTO for paginated transaction list response."""

    transactions: List[TransactionResponseDTO] = Field(..., description="List of transactions")
    total: int = Field(..., description="Total number of transactions matching filters")


class TransactionFilterDTO(BaseModel):
    """DTO for filtering transactions."""

    start_date: Optional[date_type] = Field(None, description="Filter transactions from this date")
    end_date: Optional[date_type] = Field(None, description="Filter transactions until this date")
    category_id: Optional[UUID] = Field(None, description="Filter by category ID")
    type: Optional[Literal["income", "expense"]] = Field(None, description="Filter by transaction type")
