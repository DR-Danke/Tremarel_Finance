"""Reports service for generating financial reports and exports."""

import csv
import io
from calendar import month_abbr
from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from dateutil.relativedelta import relativedelta
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from src.interface.reports_dto import (
    CategorySummaryDTO,
    IncomeExpenseComparisonDTO,
    ReportDataResponseDTO,
    ReportSummaryDTO,
)
from src.models.category import Category
from src.models.transaction import Transaction


class ReportsService:
    """Service for generating financial reports and data exports."""

    def get_income_expense_comparison(
        self,
        db: Session,
        entity_id: UUID,
        start_date: date,
        end_date: date,
    ) -> List[IncomeExpenseComparisonDTO]:
        """
        Get income vs expense comparison by month for the given date range.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            start_date: Start date for the report period
            end_date: End date for the report period

        Returns:
            List of IncomeExpenseComparisonDTO sorted by date ascending
        """
        print(
            f"INFO [ReportsService]: Getting income/expense comparison for entity "
            f"{entity_id} from {start_date} to {end_date}"
        )

        # Query for monthly aggregates within date range
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
                Transaction.date <= end_date,
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
        comparison: List[IncomeExpenseComparisonDTO] = []
        current = date(start_date.year, start_date.month, 1)
        end_month = date(end_date.year, end_date.month, 1)

        while current <= end_month:
            key = (current.year, current.month)
            month_data = results_dict.get(
                key, {"income": Decimal("0"), "expenses": Decimal("0")}
            )

            period_label = f"{month_abbr[current.month]} {current.year}"
            comparison.append(
                IncomeExpenseComparisonDTO(
                    period=period_label,
                    month=current.month,
                    year=current.year,
                    income=month_data["income"],
                    expenses=month_data["expenses"],
                )
            )
            current = current + relativedelta(months=1)

        print(
            f"INFO [ReportsService]: Generated {len(comparison)} monthly comparison entries"
        )
        return comparison

    def get_category_summary(
        self,
        db: Session,
        entity_id: UUID,
        start_date: date,
        end_date: date,
        transaction_type: Optional[str] = None,
    ) -> List[CategorySummaryDTO]:
        """
        Get category breakdown with totals and percentages.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            start_date: Start date for the report period
            end_date: End date for the report period
            transaction_type: Optional filter for income or expense

        Returns:
            List of CategorySummaryDTO sorted by amount descending
        """
        print(
            f"INFO [ReportsService]: Getting category summary for entity "
            f"{entity_id} from {start_date} to {end_date}"
        )

        # Build base query
        query = (
            db.query(
                Transaction.category_id,
                Category.name.label("category_name"),
                Category.color.label("category_color"),
                Transaction.type,
                func.sum(Transaction.amount).label("total"),
            )
            .join(Category, Transaction.category_id == Category.id)
            .filter(
                Transaction.entity_id == entity_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
            )
        )

        # Apply type filter if specified
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)

        breakdown_data = (
            query.group_by(
                Transaction.category_id,
                Category.name,
                Category.color,
                Transaction.type,
            )
            .order_by(func.sum(Transaction.amount).desc())
            .all()
        )

        # Calculate totals for percentages (by type)
        income_total = sum(
            Decimal(str(row.total))
            for row in breakdown_data
            if row.type == "income"
        )
        expense_total = sum(
            Decimal(str(row.total))
            for row in breakdown_data
            if row.type == "expense"
        )

        summary: List[CategorySummaryDTO] = []
        for row in breakdown_data:
            amount = Decimal(str(row.total))
            type_total = income_total if row.type == "income" else expense_total
            percentage = float(amount / type_total * 100) if type_total > 0 else 0.0

            summary.append(
                CategorySummaryDTO(
                    category_id=str(row.category_id),
                    category_name=row.category_name,
                    amount=amount,
                    percentage=round(percentage, 1),
                    type=row.type,
                    color=row.category_color,
                )
            )

        print(f"INFO [ReportsService]: Found {len(summary)} category entries")
        return summary

    def get_report_summary(
        self,
        db: Session,
        entity_id: UUID,
        start_date: date,
        end_date: date,
    ) -> ReportSummaryDTO:
        """
        Get overall report summary totals.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            start_date: Start date for the report period
            end_date: End date for the report period

        Returns:
            ReportSummaryDTO with overall totals
        """
        print(
            f"INFO [ReportsService]: Getting report summary for entity "
            f"{entity_id} from {start_date} to {end_date}"
        )

        # Get total income
        income_result = (
            db.query(func.coalesce(func.sum(Transaction.amount), Decimal("0")))
            .filter(
                Transaction.entity_id == entity_id,
                Transaction.type == "income",
                Transaction.date >= start_date,
                Transaction.date <= end_date,
            )
            .scalar()
        )
        total_income = Decimal(str(income_result)) if income_result else Decimal("0")

        # Get total expenses
        expense_result = (
            db.query(func.coalesce(func.sum(Transaction.amount), Decimal("0")))
            .filter(
                Transaction.entity_id == entity_id,
                Transaction.type == "expense",
                Transaction.date >= start_date,
                Transaction.date <= end_date,
            )
            .scalar()
        )
        total_expenses = (
            Decimal(str(expense_result)) if expense_result else Decimal("0")
        )

        # Get transaction count
        transaction_count = (
            db.query(func.count(Transaction.id))
            .filter(
                Transaction.entity_id == entity_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
            )
            .scalar()
        ) or 0

        net_balance = total_income - total_expenses

        print(
            f"INFO [ReportsService]: Summary - Income: {total_income}, "
            f"Expenses: {total_expenses}, Net: {net_balance}, "
            f"Count: {transaction_count}"
        )

        return ReportSummaryDTO(
            total_income=total_income,
            total_expenses=total_expenses,
            net_balance=net_balance,
            transaction_count=transaction_count,
        )

    def get_report_data(
        self,
        db: Session,
        entity_id: UUID,
        start_date: date,
        end_date: date,
    ) -> ReportDataResponseDTO:
        """
        Get complete report data including summary, comparison, and breakdown.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            start_date: Start date for the report period
            end_date: End date for the report period

        Returns:
            ReportDataResponseDTO with all report data
        """
        print(
            f"INFO [ReportsService]: Fetching complete report data for entity "
            f"{entity_id} from {start_date} to {end_date}"
        )

        summary = self.get_report_summary(db, entity_id, start_date, end_date)
        income_expense_comparison = self.get_income_expense_comparison(
            db, entity_id, start_date, end_date
        )
        category_breakdown = self.get_category_summary(
            db, entity_id, start_date, end_date
        )

        print("INFO [ReportsService]: Report data assembled successfully")

        return ReportDataResponseDTO(
            summary=summary,
            income_expense_comparison=income_expense_comparison,
            category_breakdown=category_breakdown,
        )

    def export_transactions_csv(
        self,
        db: Session,
        entity_id: UUID,
        start_date: date,
        end_date: date,
    ) -> str:
        """
        Export transactions to CSV format.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            start_date: Start date for the export period
            end_date: End date for the export period

        Returns:
            CSV content as string
        """
        print(
            f"INFO [ReportsService]: Exporting transactions to CSV for entity "
            f"{entity_id} from {start_date} to {end_date}"
        )

        # Query transactions with category names
        transactions = (
            db.query(
                Transaction.date,
                Transaction.type,
                Category.name.label("category_name"),
                Transaction.amount,
                Transaction.description,
                Transaction.notes,
            )
            .join(Category, Transaction.category_id == Category.id)
            .filter(
                Transaction.entity_id == entity_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
            )
            .order_by(Transaction.date.desc())
            .all()
        )

        # Generate CSV content
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Date", "Type", "Category", "Amount", "Description", "Notes"])

        # Write data rows
        for t in transactions:
            writer.writerow(
                [
                    t.date.isoformat() if t.date else "",
                    t.type or "",
                    t.category_name or "",
                    str(t.amount) if t.amount else "0",
                    t.description or "",
                    t.notes or "",
                ]
            )

        csv_content = output.getvalue()
        output.close()

        print(
            f"INFO [ReportsService]: Exported {len(transactions)} transactions to CSV"
        )

        return csv_content


# Singleton instance
reports_service = ReportsService()
