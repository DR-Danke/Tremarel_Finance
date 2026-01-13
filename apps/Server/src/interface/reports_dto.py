"""Pydantic DTOs for reports requests and responses."""

from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class ReportFilterDTO(BaseModel):
    """DTO for report filter parameters."""

    start_date: date = Field(..., description="Start date for the report period")
    end_date: date = Field(..., description="End date for the report period")
    type: Optional[str] = Field(None, description="Filter by transaction type (income/expense)")
    category_ids: Optional[List[str]] = Field(None, description="Filter by specific category IDs")


class IncomeExpenseComparisonDTO(BaseModel):
    """DTO for period income vs expense comparison."""

    period: str = Field(..., description="Period label (e.g., 'Jan 2024')")
    month: int = Field(..., description="Month number (1-12)")
    year: int = Field(..., description="Year")
    income: Decimal = Field(..., description="Total income for the period")
    expenses: Decimal = Field(..., description="Total expenses for the period")


class CategorySummaryDTO(BaseModel):
    """DTO for category breakdown with totals and percentages."""

    category_id: str = Field(..., description="Category UUID")
    category_name: str = Field(..., description="Category display name")
    amount: Decimal = Field(..., description="Total amount for the category")
    percentage: float = Field(..., description="Percentage of total (income or expense)")
    type: str = Field(..., description="Transaction type (income/expense)")
    color: Optional[str] = Field(None, description="Category color for display")


class ReportSummaryDTO(BaseModel):
    """DTO for overall report totals."""

    total_income: Decimal = Field(..., description="Total income for the report period")
    total_expenses: Decimal = Field(..., description="Total expenses for the report period")
    net_balance: Decimal = Field(..., description="Net balance (income - expenses)")
    transaction_count: int = Field(..., description="Total number of transactions")


class ReportDataResponseDTO(BaseModel):
    """DTO for complete report data response."""

    summary: ReportSummaryDTO = Field(..., description="Overall report summary")
    income_expense_comparison: List[IncomeExpenseComparisonDTO] = Field(
        ..., description="Monthly income vs expense comparison"
    )
    category_breakdown: List[CategorySummaryDTO] = Field(
        ..., description="Category breakdown with totals and percentages"
    )
