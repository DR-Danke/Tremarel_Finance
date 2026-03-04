"""Repository for Legal Desk analytics aggregation operations."""

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.ld_case import LdCase
from src.models.ld_specialist import LdSpecialist


class LdAnalyticsRepository:
    """Repository for Legal Desk analytics and dashboard aggregations."""

    def count_cases_by_status(self, db: Session) -> dict[str, int]:
        """
        Count cases grouped by status.

        Args:
            db: Database session

        Returns:
            Dict mapping status to count
        """
        print("INFO [LdAnalyticsRepository]: Counting cases by status")
        results = (
            db.query(LdCase.status, func.count(LdCase.id))
            .group_by(LdCase.status)
            .all()
        )
        counts = {status: count for status, count in results}
        print(f"INFO [LdAnalyticsRepository]: Cases by status: {counts}")
        return counts

    def count_cases_by_domain(self, db: Session) -> dict[str, int]:
        """
        Count cases grouped by legal domain.

        Args:
            db: Database session

        Returns:
            Dict mapping legal_domain to count
        """
        print("INFO [LdAnalyticsRepository]: Counting cases by domain")
        results = (
            db.query(LdCase.legal_domain, func.count(LdCase.id))
            .group_by(LdCase.legal_domain)
            .all()
        )
        counts = {domain: count for domain, count in results}
        print(f"INFO [LdAnalyticsRepository]: Cases by domain: {counts}")
        return counts

    def revenue_pipeline(self, db: Session) -> dict:
        """
        Sum estimated_cost and final_quote for active cases.

        Active statuses: active, in_progress, review, negotiating.

        Args:
            db: Database session

        Returns:
            Dict with total_estimated_cost, total_final_quote, active_case_count
        """
        print("INFO [LdAnalyticsRepository]: Computing revenue pipeline")
        active_statuses = ["active", "in_progress", "review", "negotiating"]
        result = (
            db.query(
                func.coalesce(func.sum(LdCase.estimated_cost), 0),
                func.coalesce(func.sum(LdCase.final_quote), 0),
                func.count(LdCase.id),
            )
            .filter(LdCase.status.in_(active_statuses))
            .first()
        )
        pipeline = {
            "total_estimated_cost": result[0],
            "total_final_quote": result[1],
            "active_case_count": result[2],
        }
        print(f"INFO [LdAnalyticsRepository]: Revenue pipeline: {pipeline}")
        return pipeline

    def specialist_performance_rankings(self, db: Session) -> list[dict]:
        """
        Get active specialists ranked by overall_score DESC.

        Args:
            db: Database session

        Returns:
            List of dicts with id, full_name, overall_score, current_workload
        """
        print("INFO [LdAnalyticsRepository]: Getting specialist performance rankings")
        results = (
            db.query(LdSpecialist)
            .filter(LdSpecialist.is_active == True)  # noqa: E712
            .order_by(LdSpecialist.overall_score.desc())
            .all()
        )
        rankings = [
            {
                "id": s.id,
                "full_name": s.full_name,
                "overall_score": s.overall_score,
                "current_workload": s.current_workload,
            }
            for s in results
        ]
        print(f"INFO [LdAnalyticsRepository]: Found {len(rankings)} active specialists")
        return rankings

    def avg_case_duration(self, db: Session) -> Optional[float]:
        """
        Compute average case duration in days for completed cases.

        Uses (updated_at - created_at) for cases with status='completed'.

        Args:
            db: Database session

        Returns:
            Average duration in days, or None if no completed cases
        """
        print("INFO [LdAnalyticsRepository]: Computing average case duration")
        completed_cases = (
            db.query(LdCase.created_at, LdCase.updated_at)
            .filter(LdCase.status == "completed")
            .filter(LdCase.updated_at.isnot(None))
            .all()
        )
        if not completed_cases:
            print("INFO [LdAnalyticsRepository]: No completed cases found")
            return None
        total_days = 0.0
        for created_at, updated_at in completed_cases:
            delta = updated_at - created_at
            total_days += delta.total_seconds() / 86400
        avg_days = total_days / len(completed_cases)
        print(f"INFO [LdAnalyticsRepository]: Average case duration: {avg_days:.2f} days")
        return avg_days


# Singleton instance
ld_analytics_repository = LdAnalyticsRepository()
