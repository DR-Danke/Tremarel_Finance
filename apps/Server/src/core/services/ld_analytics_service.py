"""Legal Desk analytics service for dashboard statistics aggregation."""

from decimal import Decimal
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.interface.legaldesk_dto import DashboardStatsDTO
from src.models.ld_case import LdCase
from src.models.ld_specialist import LdSpecialist
from src.repository.ld_analytics_repository import ld_analytics_repository

# Statuses considered "active" for dashboard counting
ACTIVE_STATUSES = {"active", "in_progress", "review", "negotiating"}


class LdAnalyticsService:
    """Service for Legal Desk dashboard analytics aggregation."""

    def get_dashboard_stats(self, db: Session) -> DashboardStatsDTO:
        """
        Aggregate dashboard statistics from repository data.

        Args:
            db: Database session

        Returns:
            DashboardStatsDTO with all aggregated metrics
        """
        print("INFO [LdAnalyticsService]: Building dashboard statistics")

        # Aggregate from analytics repository
        cases_by_status = ld_analytics_repository.count_cases_by_status(db)
        cases_by_domain = ld_analytics_repository.count_cases_by_domain(db)
        revenue_data = ld_analytics_repository.revenue_pipeline(db)
        avg_duration = ld_analytics_repository.avg_case_duration(db)

        # Compute derived metrics
        total_cases = sum(cases_by_status.values())
        active_cases = sum(
            count for status, count in cases_by_status.items()
            if status in ACTIVE_STATUSES
        )
        completed_cases = cases_by_status.get("completed", 0)

        # Specialist count
        total_specialists = db.query(func.count(LdSpecialist.id)).scalar() or 0
        print(f"INFO [LdAnalyticsService]: Total specialists: {total_specialists}")

        # Revenue from pipeline
        total_revenue: Optional[Decimal] = revenue_data.get("total_final_quote")

        # Cases by priority
        priority_results = (
            db.query(LdCase.priority, func.count(LdCase.id))
            .group_by(LdCase.priority)
            .all()
        )
        cases_by_priority = {priority: count for priority, count in priority_results}

        # Convert avg_duration to Decimal if present
        avg_duration_decimal: Optional[Decimal] = (
            Decimal(str(round(avg_duration, 2))) if avg_duration is not None else None
        )

        stats = DashboardStatsDTO(
            total_cases=total_cases,
            active_cases=active_cases,
            completed_cases=completed_cases,
            total_specialists=total_specialists,
            avg_case_duration_days=avg_duration_decimal,
            total_revenue=total_revenue,
            cases_by_status=cases_by_status,
            cases_by_domain=cases_by_domain,
            cases_by_priority=cases_by_priority,
        )

        print(
            f"INFO [LdAnalyticsService]: Dashboard stats — "
            f"total={total_cases}, active={active_cases}, "
            f"completed={completed_cases}, specialists={total_specialists}"
        )
        return stats


# Singleton instance
ld_analytics_service = LdAnalyticsService()
