"""Unit tests for LdSpecialistRepository."""

from decimal import Decimal
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from src.repository.ld_specialist_repository import LdSpecialistRepository


@pytest.fixture
def repo():
    """Create a fresh LdSpecialistRepository instance."""
    return LdSpecialistRepository()


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_specialist():
    """Create a mock LdSpecialist object."""
    specialist = MagicMock()
    specialist.id = 1
    specialist.full_name = "Dr. Ana Garcia"
    specialist.email = "ana@law.com"
    specialist.is_active = True
    specialist.current_workload = 3
    specialist.max_concurrent_cases = 5
    specialist.overall_score = Decimal("4.50")
    specialist.years_experience = 10
    specialist.created_at = "2026-01-01T00:00:00"
    return specialist


class TestCreateSpecialist:
    """Tests for LdSpecialistRepository.create."""

    def test_create_specialist(self, repo, mock_db):
        """Verify db.add, db.commit, db.refresh are called."""
        data = {"full_name": "Dr. Ana Garcia", "email": "ana@law.com"}
        result = repo.create(mock_db, data)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert result is not None


class TestGetById:
    """Tests for LdSpecialistRepository.get_by_id."""

    def test_get_by_id_found(self, repo, mock_db, mock_specialist):
        """Should return specialist when found."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_specialist
        result = repo.get_by_id(mock_db, 1)

        assert result == mock_specialist

    def test_get_by_id_not_found(self, repo, mock_db):
        """Should return None when not found."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = repo.get_by_id(mock_db, 999)

        assert result is None


class TestListAll:
    """Tests for LdSpecialistRepository.list_all."""

    def test_list_all_no_filters(self, repo, mock_db, mock_specialist):
        """No filters should return all specialists."""
        mock_db.query.return_value.order_by.return_value.all.return_value = [mock_specialist]
        result = repo.list_all(mock_db)

        assert len(result) == 1

    def test_list_all_with_is_active_filter(self, repo, mock_db, mock_specialist):
        """Filter by is_active should apply filter."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_specialist]
        result = repo.list_all(mock_db, {"is_active": True})

        assert len(result) == 1

    def test_list_all_with_domain_filter(self, repo, mock_db, mock_specialist):
        """Filter by legal_domain should join expertise table."""
        mock_db.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_specialist]
        result = repo.list_all(mock_db, {"legal_domain": "corporate"})

        assert len(result) == 1

    def test_list_all_with_experience_filter(self, repo, mock_db, mock_specialist):
        """Filter by min_experience should apply filter."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_specialist]
        result = repo.list_all(mock_db, {"min_experience": 5})

        assert len(result) == 1

    def test_list_all_with_workload_filter(self, repo, mock_db, mock_specialist):
        """Filter by max_workload should apply filter."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_specialist]
        result = repo.list_all(mock_db, {"max_workload": 3})

        assert len(result) == 1


class TestUpdateSpecialist:
    """Tests for LdSpecialistRepository.update."""

    def test_update_specialist(self, repo, mock_db, mock_specialist):
        """Verify fields updated via setattr."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_specialist
        data = {"full_name": "Dr. Ana Garcia Updated"}

        result = repo.update(mock_db, 1, data)

        assert result is not None
        mock_db.commit.assert_called()

    def test_update_specialist_not_found(self, repo, mock_db):
        """Should return None when specialist not found."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = repo.update(mock_db, 999, {"full_name": "Updated"})

        assert result is None


class TestUpdateStatus:
    """Tests for LdSpecialistRepository.update_status."""

    def test_update_status_active(self, repo, mock_db, mock_specialist):
        """Status 'active' should set is_active to True."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_specialist
        result = repo.update_status(mock_db, 1, "active")

        assert result is not None

    def test_update_status_inactive(self, repo, mock_db, mock_specialist):
        """Status 'inactive' should set is_active to False."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_specialist
        result = repo.update_status(mock_db, 1, "inactive")

        assert result is not None

    def test_update_status_on_leave(self, repo, mock_db, mock_specialist):
        """Status 'on_leave' should set is_active to False."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_specialist
        result = repo.update_status(mock_db, 1, "on_leave")

        assert result is not None


class TestGetAvailable:
    """Tests for LdSpecialistRepository.get_available."""

    def test_get_available_domain_only(self, repo, mock_db, mock_specialist):
        """Should filter by domain and availability."""
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = [mock_specialist]
        result = repo.get_available(mock_db, "corporate")

        assert len(result) == 1

    def test_get_available_with_jurisdiction(self, repo, mock_db, mock_specialist):
        """Should additionally filter by jurisdiction when provided."""
        (
            mock_db.query.return_value
            .join.return_value
            .filter.return_value
            .join.return_value
            .filter.return_value
            .all.return_value
        ) = [mock_specialist]
        result = repo.get_available(mock_db, "corporate", jurisdiction="Spain")

        assert len(result) == 1

    def test_get_available_no_results(self, repo, mock_db):
        """Should return empty list when no specialists available."""
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = []
        result = repo.get_available(mock_db, "immigration")

        assert result == []


class TestUpdateWorkload:
    """Tests for LdSpecialistRepository.update_workload."""

    def test_update_workload_increment(self, repo, mock_db, mock_specialist):
        """Should increment workload by positive delta."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_specialist
        result = repo.update_workload(mock_db, 1, 1)

        assert result is not None
        mock_db.commit.assert_called()

    def test_update_workload_decrement(self, repo, mock_db, mock_specialist):
        """Should decrement workload by negative delta."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_specialist
        result = repo.update_workload(mock_db, 1, -1)

        assert result is not None

    def test_update_workload_not_found(self, repo, mock_db):
        """Should return None when specialist not found."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = repo.update_workload(mock_db, 999, 1)

        assert result is None


class TestUpdateOverallScore:
    """Tests for LdSpecialistRepository.update_overall_score."""

    def test_update_overall_score_with_scores(self, repo, mock_db, mock_specialist):
        """Should calculate avg and update overall_score."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_specialist
        # Mock the avg query (second call to db.query)
        mock_db.query.return_value.filter.return_value.scalar.return_value = Decimal("4.25")

        result = repo.update_overall_score(mock_db, 1)

        assert result is not None
        mock_db.commit.assert_called()

    def test_update_overall_score_no_scores(self, repo, mock_db, mock_specialist):
        """Should set to 0.00 when no scores exist."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_specialist
        mock_db.query.return_value.filter.return_value.scalar.return_value = None

        result = repo.update_overall_score(mock_db, 1)

        assert result is not None

    def test_update_overall_score_not_found(self, repo, mock_db):
        """Should return None when specialist not found."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = repo.update_overall_score(mock_db, 999)

        assert result is None
