"""Unit tests for Legal Desk analytics service."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from src.core.services.ld_analytics_service import LdAnalyticsService


@pytest.fixture
def service():
    """Analytics service instance."""
    return LdAnalyticsService()


@pytest.fixture
def mock_db():
    """Mock database session."""
    return MagicMock()


class TestGetDashboardStats:
    """Tests for get_dashboard_stats aggregation method."""

    @patch("src.core.services.ld_analytics_service.ld_analytics_repository")
    def test_dashboard_stats_with_data(self, mock_repo, service, mock_db):
        """Dashboard stats computed correctly from repository data."""
        mock_repo.count_cases_by_status.return_value = {
            "active": 5,
            "in_progress": 3,
            "review": 2,
            "negotiating": 1,
            "completed": 10,
            "closed": 4,
        }
        mock_repo.count_cases_by_domain.return_value = {
            "corporate": 12,
            "labor": 8,
            "tax": 5,
        }
        mock_repo.revenue_pipeline.return_value = {
            "total_estimated_cost": Decimal("50000.00"),
            "total_final_quote": Decimal("75000.00"),
            "active_case_count": 11,
        }
        mock_repo.avg_case_duration.return_value = 15.5

        # Mock specialist count query
        mock_db.query.return_value.scalar.return_value = 8

        # Mock cases_by_priority query
        mock_db.query.return_value.group_by.return_value.all.return_value = [
            ("high", 7),
            ("medium", 12),
            ("low", 6),
        ]

        result = service.get_dashboard_stats(mock_db)

        assert result.total_cases == 25
        assert result.active_cases == 11
        assert result.completed_cases == 10
        assert result.total_specialists == 8
        assert result.avg_case_duration_days == Decimal("15.5")
        assert result.total_revenue == Decimal("75000.00")
        assert result.cases_by_status["active"] == 5
        assert result.cases_by_domain["corporate"] == 12
        assert result.cases_by_priority == {"high": 7, "medium": 12, "low": 6}

    @patch("src.core.services.ld_analytics_service.ld_analytics_repository")
    def test_dashboard_stats_empty_database(self, mock_repo, service, mock_db):
        """Empty database returns zero/empty values."""
        mock_repo.count_cases_by_status.return_value = {}
        mock_repo.count_cases_by_domain.return_value = {}
        mock_repo.revenue_pipeline.return_value = {
            "total_estimated_cost": Decimal("0"),
            "total_final_quote": Decimal("0"),
            "active_case_count": 0,
        }
        mock_repo.avg_case_duration.return_value = None

        mock_db.query.return_value.scalar.return_value = 0
        mock_db.query.return_value.group_by.return_value.all.return_value = []

        result = service.get_dashboard_stats(mock_db)

        assert result.total_cases == 0
        assert result.active_cases == 0
        assert result.completed_cases == 0
        assert result.total_specialists == 0
        assert result.avg_case_duration_days is None
        assert result.total_revenue == Decimal("0")
        assert result.cases_by_status == {}
        assert result.cases_by_domain == {}
        assert result.cases_by_priority == {}

    @patch("src.core.services.ld_analytics_service.ld_analytics_repository")
    def test_active_cases_counted_correctly(self, mock_repo, service, mock_db):
        """Only active, in_progress, review, negotiating statuses counted as active."""
        mock_repo.count_cases_by_status.return_value = {
            "active": 2,
            "in_progress": 3,
            "review": 1,
            "negotiating": 1,
            "new": 5,
            "completed": 10,
            "closed": 4,
            "archived": 2,
        }
        mock_repo.count_cases_by_domain.return_value = {}
        mock_repo.revenue_pipeline.return_value = {
            "total_estimated_cost": Decimal("0"),
            "total_final_quote": Decimal("0"),
            "active_case_count": 0,
        }
        mock_repo.avg_case_duration.return_value = None

        mock_db.query.return_value.scalar.return_value = 0
        mock_db.query.return_value.group_by.return_value.all.return_value = []

        result = service.get_dashboard_stats(mock_db)

        assert result.active_cases == 7  # 2 + 3 + 1 + 1
        assert result.total_cases == 28

    @patch("src.core.services.ld_analytics_service.ld_analytics_repository")
    def test_total_revenue_from_pipeline(self, mock_repo, service, mock_db):
        """Total revenue comes from revenue_pipeline total_final_quote."""
        mock_repo.count_cases_by_status.return_value = {}
        mock_repo.count_cases_by_domain.return_value = {}
        mock_repo.revenue_pipeline.return_value = {
            "total_estimated_cost": Decimal("100000.00"),
            "total_final_quote": Decimal("125000.00"),
            "active_case_count": 5,
        }
        mock_repo.avg_case_duration.return_value = None

        mock_db.query.return_value.scalar.return_value = 0
        mock_db.query.return_value.group_by.return_value.all.return_value = []

        result = service.get_dashboard_stats(mock_db)

        assert result.total_revenue == Decimal("125000.00")
