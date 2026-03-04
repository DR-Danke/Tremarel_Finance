"""Unit tests for LdAnalyticsRepository."""

from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from src.repository.ld_analytics_repository import LdAnalyticsRepository


@pytest.fixture
def repo():
    return LdAnalyticsRepository()


@pytest.fixture
def mock_db():
    return MagicMock()


class TestCountCasesByStatus:
    def test_returns_grouped_counts(self, repo, mock_db):
        mock_db.query.return_value.group_by.return_value.all.return_value = [
            ("new", 5),
            ("active", 3),
            ("completed", 2),
        ]
        result = repo.count_cases_by_status(mock_db)
        assert result == {"new": 5, "active": 3, "completed": 2}

    def test_returns_empty_dict_when_no_cases(self, repo, mock_db):
        mock_db.query.return_value.group_by.return_value.all.return_value = []
        result = repo.count_cases_by_status(mock_db)
        assert result == {}


class TestCountCasesByDomain:
    def test_returns_grouped_counts(self, repo, mock_db):
        mock_db.query.return_value.group_by.return_value.all.return_value = [
            ("corporate", 10),
            ("labor", 4),
        ]
        result = repo.count_cases_by_domain(mock_db)
        assert result == {"corporate": 10, "labor": 4}

    def test_returns_empty_dict_when_no_cases(self, repo, mock_db):
        mock_db.query.return_value.group_by.return_value.all.return_value = []
        result = repo.count_cases_by_domain(mock_db)
        assert result == {}


class TestRevenuePipeline:
    def test_returns_aggregated_values(self, repo, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = (
            Decimal("50000.00"),
            Decimal("45000.00"),
            8,
        )
        result = repo.revenue_pipeline(mock_db)
        assert result["total_estimated_cost"] == Decimal("50000.00")
        assert result["total_final_quote"] == Decimal("45000.00")
        assert result["active_case_count"] == 8

    def test_returns_zeros_when_no_active_cases(self, repo, mock_db):
        mock_db.query.return_value.filter.return_value.first.return_value = (0, 0, 0)
        result = repo.revenue_pipeline(mock_db)
        assert result["total_estimated_cost"] == 0
        assert result["total_final_quote"] == 0
        assert result["active_case_count"] == 0


class TestSpecialistPerformanceRankings:
    def test_returns_ranked_list(self, repo, mock_db):
        specialist1 = MagicMock()
        specialist1.id = 1
        specialist1.full_name = "Alice"
        specialist1.overall_score = Decimal("4.50")
        specialist1.current_workload = 3

        specialist2 = MagicMock()
        specialist2.id = 2
        specialist2.full_name = "Bob"
        specialist2.overall_score = Decimal("3.80")
        specialist2.current_workload = 5

        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            specialist1,
            specialist2,
        ]

        result = repo.specialist_performance_rankings(mock_db)

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["full_name"] == "Alice"
        assert result[0]["overall_score"] == Decimal("4.50")
        assert result[0]["current_workload"] == 3
        assert result[1]["id"] == 2

    def test_returns_empty_list_when_no_specialists(self, repo, mock_db):
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        result = repo.specialist_performance_rankings(mock_db)
        assert result == []


class TestAvgCaseDuration:
    def test_returns_average_days(self, repo, mock_db):
        now = datetime.utcnow()
        cases = [
            (now - timedelta(days=10), now),
            (now - timedelta(days=20), now),
        ]
        mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = cases

        result = repo.avg_case_duration(mock_db)

        assert result is not None
        assert abs(result - 15.0) < 0.01

    def test_returns_none_when_no_completed_cases(self, repo, mock_db):
        mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = []
        result = repo.avg_case_duration(mock_db)
        assert result is None
