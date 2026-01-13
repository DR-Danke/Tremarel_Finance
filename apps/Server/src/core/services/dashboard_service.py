"""Dashboard service for aggregating financial statistics."""

from calendar import month_abbr
from datetime import date
from decimal import Decimal
from typing import List
from uuid import UUID

from dateutil.relativedelta import relativedelta
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from src.interface.dashboard_dto import (
    CategoryBreakdownDTO,
    CurrentMonthSummaryDTO,
    DashboardStatsResponseDTO,
    MonthlyTotalDTO,
)
from src.models.category import Category
from src.models.transaction import Transaction


class DashboardService:
    """Service for dashboard data aggregation."""

    def get_current_month_summary(
        self, db: Session, entity_id: UUID
    ) -> CurrentMonthSummaryDTO:
        """
        Get current month financial summary.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by

        Returns:
            CurrentMonthSummaryDTO with income, expenses, and net balance
        """
        print(f"INFO [DashboardService]: Getting current month summary for entity {entity_id}")

        today = date.today()
        first_day = date(today.year, today.month, 1)

        # Get total income for current month
        income_result = (
            db.query(func.coalesce(func.sum(Transaction.amount), Decimal("0")))
            .filter(
                Transaction.entity_id == entity_id,
                Transaction.type == "income",
                Transaction.date >= first_day,
                Transaction.date <= today,
            )
            .scalar()
        )
        total_income = Decimal(str(income_result)) if income_result else Decimal("0")

        # Get total expenses for current month
        expense_result = (
            db.query(func.coalesce(func.sum(Transaction.amount), Decimal("0")))
            .filter(
                Transaction.entity_id == entity_id,
                Transaction.type == "expense",
                Transaction.date >= first_day,
                Transaction.date <= today,
            )
            .scalar()
        )
        total_expenses = Decimal(str(expense_result)) if expense_result else Decimal("0")

        net_balance = total_income - total_expenses

        print(
            f"INFO [DashboardService]: Current month - Income: {total_income}, "
            f"Expenses: {total_expenses}, Net: {net_balance}"
        )

        return CurrentMonthSummaryDTO(
            total_income=total_income,
            total_expenses=total_expenses,
            net_balance=net_balance,
        )

    def get_monthly_trends(
        self, db: Session, entity_id: UUID, months: int = 6
    ) -> List[MonthlyTotalDTO]:
        """
        Get monthly income/expense trends for the last N months.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            months: Number of months to include (default 6)

        Returns:
            List of MonthlyTotalDTO sorted by date ascending
        """
        print(f"INFO [DashboardService]: Getting monthly trends for entity {entity_id} ({months} months)")

        today = date.today()
        # Start from N months ago
        start_date = today - relativedelta(months=months - 1)
        start_date = date(start_date.year, start_date.month, 1)

        # Query for monthly aggregates
        monthly_data = (
            db.query(
                extract("year", Transaction.date).label("year"),
                extract("month", Transaction.date).label("month"),
                Transaction.type,
                func.sum(Transaction.amount).label("total"),
            )
            .filter(
                Transaction.entity_id == entity_id,
                Transaction.date >= start_date,
            )
            .group_by(
                extract("year", Transaction.date),
                extract("month", Transaction.date),
                Transaction.type,
            )
            .all()
        )

        # Build a dict of results
        results_dict: dict[tuple[int, int], dict[str, Decimal]] = {}
        for row in monthly_data:
            key = (int(row.year), int(row.month))
            if key not in results_dict:
                results_dict[key] = {"income": Decimal("0"), "expenses": Decimal("0")}
            if row.type == "income":
                results_dict[key]["income"] = Decimal(str(row.total))
            else:
                results_dict[key]["expenses"] = Decimal(str(row.total))

        # Generate all months in range (including those with zero transactions)
        trends: List[MonthlyTotalDTO] = []
        current = start_date
        while current <= today:
            key = (current.year, current.month)
            month_data = results_dict.get(key, {"income": Decimal("0"), "expenses": Decimal("0")})

            month_label = f"{month_abbr[current.month]} {current.year}"
            trends.append(
                MonthlyTotalDTO(
                    month=month_label,
                    year=current.year,
                    month_number=current.month,
                    income=month_data["income"],
                    expenses=month_data["expenses"],
                )
            )
            current = current + relativedelta(months=1)

        print(f"INFO [DashboardService]: Generated {len(trends)} monthly trend entries")
        return trends

    def get_expense_breakdown(
        self, db: Session, entity_id: UUID
    ) -> List[CategoryBreakdownDTO]:
        """
        Get expense breakdown by category for the current month.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by

        Returns:
            List of CategoryBreakdownDTO sorted by amount descending
        """
        print(f"INFO [DashboardService]: Getting expense breakdown for entity {entity_id}")

        today = date.today()
        first_day = date(today.year, today.month, 1)

        # Query expenses grouped by category with join to get category name
        breakdown_data = (
            db.query(
                Transaction.category_id,
                Category.name.label("category_name"),
                Category.color.label("category_color"),
                func.sum(Transaction.amount).label("total"),
            )
            .join(Category, Transaction.category_id == Category.id)
            .filter(
                Transaction.entity_id == entity_id,
                Transaction.type == "expense",
                Transaction.date >= first_day,
                Transaction.date <= today,
            )
            .group_by(Transaction.category_id, Category.name, Category.color)
            .order_by(func.sum(Transaction.amount).desc())
            .all()
        )

        # Calculate total for percentages
        total_expenses = sum(Decimal(str(row.total)) for row in breakdown_data)

        breakdown: List[CategoryBreakdownDTO] = []
        for row in breakdown_data:
            amount = Decimal(str(row.total))
            percentage = float(amount / total_expenses * 100) if total_expenses > 0 else 0.0

            breakdown.append(
                CategoryBreakdownDTO(
                    category_id=str(row.category_id),
                    category_name=row.category_name,
                    amount=amount,
                    percentage=round(percentage, 1),
                    color=row.category_color,
                )
            )

        print(f"INFO [DashboardService]: Found {len(breakdown)} expense categories")
        return breakdown

    def get_dashboard_stats(
        self, db: Session, entity_id: UUID
    ) -> DashboardStatsResponseDTO:
        """
        Get complete dashboard statistics.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by

        Returns:
            DashboardStatsResponseDTO with all dashboard data
        """
        print(f"INFO [DashboardService]: Fetching dashboard stats for entity {entity_id}")

        current_month_summary = self.get_current_month_summary(db, entity_id)
        monthly_trends = self.get_monthly_trends(db, entity_id)
        expense_breakdown = self.get_expense_breakdown(db, entity_id)

        print(f"INFO [DashboardService]: Dashboard stats assembled successfully")

        return DashboardStatsResponseDTO(
            current_month_summary=current_month_summary,
            monthly_trends=monthly_trends,
            expense_breakdown=expense_breakdown,
        )


# Singleton instance
dashboard_service = DashboardService()
