"""Pydantic DTOs for dashboard requests and responses."""

from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field


class CurrentMonthSummaryDTO(BaseModel):
    """DTO for current month financial summary."""

    total_income: Decimal = Field(..., description="Total income for current month")
    total_expenses: Decimal = Field(..., description="Total expenses for current month")
    net_balance: Decimal = Field(..., description="Net balance (income - expenses)")


class MonthlyTotalDTO(BaseModel):
    """DTO for monthly income/expense totals."""

    month: str = Field(..., description="Month label (e.g., 'Jan 2024')")
    year: int = Field(..., description="Year")
    month_number: int = Field(..., description="Month number (1-12)")
    income: Decimal = Field(..., description="Total income for the month")
    expenses: Decimal = Field(..., description="Total expenses for the month")


class CategoryBreakdownDTO(BaseModel):
    """DTO for expense breakdown by category."""

    category_id: str = Field(..., description="Category UUID")
    category_name: str = Field(..., description="Category display name")
    amount: Decimal = Field(..., description="Total amount spent in category")
    percentage: float = Field(..., description="Percentage of total expenses")
    color: str | None = Field(None, description="Category color for chart display")


class DashboardStatsResponseDTO(BaseModel):
    """DTO for complete dashboard statistics response."""

    current_month_summary: CurrentMonthSummaryDTO = Field(
        ..., description="Current month financial summary"
    )
    monthly_trends: List[MonthlyTotalDTO] = Field(
        ..., description="Monthly income/expense trends (last 6 months)"
    )
    expense_breakdown: List[CategoryBreakdownDTO] = Field(
        ..., description="Expense breakdown by category for current month"
    )
