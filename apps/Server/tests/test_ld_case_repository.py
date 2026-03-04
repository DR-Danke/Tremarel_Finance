"""Unit tests for LdCaseRepository."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.interface.legaldesk_dto import (
    CaseComplexity,
    CaseFilterDTO,
    CasePriority,
    CaseStatus,
    CaseType,
    LegalDomain,
)
from src.repository.ld_case_repository import LdCaseRepository


@pytest.fixture
def repo():
    """Create a fresh LdCaseRepository instance."""
    return LdCaseRepository()


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_case():
    """Create a mock LdCase object."""
    case = MagicMock()
    case.id = 1
    case.case_number = "LD-202603-0001"
    case.title = "Corporate Merger Review"
    case.status = "new"
    case.client_id = 10
    case.legal_domain = "corporate"
    case.priority = "high"
    case.complexity = "medium"
    case.created_at = "2026-03-01T00:00:00"
    return case


@pytest.fixture
def empty_filters():
    """Create a CaseFilterDTO with no filters."""
    return CaseFilterDTO()


class TestCreateCase:
    """Tests for LdCaseRepository.create."""

    def test_create_case(self, repo, mock_db):
        """Verify db.add, db.commit, db.refresh are called."""
        data = {
            "case_number": "LD-202603-0001",
            "title": "Test Case",
            "client_id": 1,
            "legal_domain": "corporate",
        }
        result = repo.create(mock_db, data)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert result is not None


class TestGetById:
    """Tests for LdCaseRepository.get_by_id."""

    def test_get_by_id_found(self, repo, mock_db, mock_case):
        """Should return case when found."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_case
        result = repo.get_by_id(mock_db, 1)

        assert result == mock_case

    def test_get_by_id_not_found(self, repo, mock_db):
        """Should return None when not found."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = repo.get_by_id(mock_db, 999)

        assert result is None


class TestListCases:
    """Tests for LdCaseRepository.list_cases."""

    def test_list_cases_no_filters(self, repo, mock_db, mock_case, empty_filters):
        """Empty filter DTO should return all cases."""
        (
            mock_db.query.return_value
            .order_by.return_value
            .offset.return_value
            .limit.return_value
            .all.return_value
        ) = [mock_case]
        result = repo.list_cases(mock_db, empty_filters)

        assert len(result) == 1

    def test_list_cases_with_status_filter(self, repo, mock_db, mock_case):
        """Status filter should be applied."""
        filters = CaseFilterDTO(status=CaseStatus.NEW)
        (
            mock_db.query.return_value
            .filter.return_value
            .order_by.return_value
            .offset.return_value
            .limit.return_value
            .all.return_value
        ) = [mock_case]
        result = repo.list_cases(mock_db, filters)

        assert len(result) == 1

    def test_list_cases_with_domain_filter(self, repo, mock_db, mock_case):
        """Legal domain filter should be applied."""
        filters = CaseFilterDTO(legal_domain=LegalDomain.CORPORATE)
        (
            mock_db.query.return_value
            .filter.return_value
            .order_by.return_value
            .offset.return_value
            .limit.return_value
            .all.return_value
        ) = [mock_case]
        result = repo.list_cases(mock_db, filters)

        assert len(result) == 1

    def test_list_cases_with_priority_filter(self, repo, mock_db, mock_case):
        """Priority filter should be applied."""
        filters = CaseFilterDTO(priority=CasePriority.HIGH)
        (
            mock_db.query.return_value
            .filter.return_value
            .order_by.return_value
            .offset.return_value
            .limit.return_value
            .all.return_value
        ) = [mock_case]
        result = repo.list_cases(mock_db, filters)

        assert len(result) == 1

    def test_list_cases_with_client_filter(self, repo, mock_db, mock_case):
        """Client ID filter should be applied."""
        filters = CaseFilterDTO(client_id=10)
        (
            mock_db.query.return_value
            .filter.return_value
            .order_by.return_value
            .offset.return_value
            .limit.return_value
            .all.return_value
        ) = [mock_case]
        result = repo.list_cases(mock_db, filters)

        assert len(result) == 1

    def test_list_cases_with_complexity_filter(self, repo, mock_db, mock_case):
        """Complexity filter should be applied."""
        filters = CaseFilterDTO(complexity=CaseComplexity.MEDIUM)
        (
            mock_db.query.return_value
            .filter.return_value
            .order_by.return_value
            .offset.return_value
            .limit.return_value
            .all.return_value
        ) = [mock_case]
        result = repo.list_cases(mock_db, filters)

        assert len(result) == 1

    def test_list_cases_with_pagination(self, repo, mock_db, empty_filters):
        """Should respect limit and offset."""
        (
            mock_db.query.return_value
            .order_by.return_value
            .offset.return_value
            .limit.return_value
            .all.return_value
        ) = []
        result = repo.list_cases(mock_db, empty_filters, limit=10, offset=20)

        assert result == []


class TestUpdateCase:
    """Tests for LdCaseRepository.update."""

    def test_update_case(self, repo, mock_db, mock_case):
        """Verify fields updated via setattr."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_case
        data = {"title": "Updated Title", "priority": "urgent"}

        result = repo.update(mock_db, 1, data)

        assert result is not None
        mock_db.commit.assert_called()

    def test_update_case_not_found(self, repo, mock_db):
        """Should return None when case not found."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = repo.update(mock_db, 999, {"title": "Updated"})

        assert result is None


class TestUpdateStatus:
    """Tests for LdCaseRepository.update_status."""

    def test_update_status(self, repo, mock_db, mock_case):
        """Should update only the status field."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_case
        result = repo.update_status(mock_db, 1, "active")

        assert result is not None
        mock_db.commit.assert_called()


class TestGenerateCaseNumber:
    """Tests for LdCaseRepository.generate_case_number."""

    @patch("src.repository.ld_case_repository.datetime")
    def test_generate_case_number_first_of_month(self, mock_datetime, repo, mock_db):
        """First case of the month should return LD-YYYYMM-0001."""
        mock_datetime.utcnow.return_value = datetime(2026, 3, 4)
        mock_db.query.return_value.filter.return_value.scalar.return_value = 0

        result = repo.generate_case_number(mock_db)

        assert result == "LD-202603-0001"

    @patch("src.repository.ld_case_repository.datetime")
    def test_generate_case_number_sequential(self, mock_datetime, repo, mock_db):
        """Should increment based on existing count."""
        mock_datetime.utcnow.return_value = datetime(2026, 3, 4)
        mock_db.query.return_value.filter.return_value.scalar.return_value = 5

        result = repo.generate_case_number(mock_db)

        assert result == "LD-202603-0006"

    @patch("src.repository.ld_case_repository.datetime")
    def test_generate_case_number_new_month(self, mock_datetime, repo, mock_db):
        """New month should start at 0001."""
        mock_datetime.utcnow.return_value = datetime(2026, 4, 1)
        mock_db.query.return_value.filter.return_value.scalar.return_value = 0

        result = repo.generate_case_number(mock_db)

        assert result == "LD-202604-0001"


class TestGetByClient:
    """Tests for LdCaseRepository.get_by_client."""

    def test_get_by_client(self, repo, mock_db, mock_case):
        """Should filter by client_id."""
        (
            mock_db.query.return_value
            .filter.return_value
            .order_by.return_value
            .all.return_value
        ) = [mock_case]
        result = repo.get_by_client(mock_db, 10)

        assert len(result) == 1

    def test_get_by_client_no_results(self, repo, mock_db):
        """Should return empty list when no cases for client."""
        (
            mock_db.query.return_value
            .filter.return_value
            .order_by.return_value
            .all.return_value
        ) = []
        result = repo.get_by_client(mock_db, 999)

        assert result == []


class TestCountByStatus:
    """Tests for LdCaseRepository.count_by_status."""

    def test_count_by_status(self, repo, mock_db):
        """Should return dict of {status: count}."""
        mock_db.query.return_value.group_by.return_value.all.return_value = [
            ("new", 5),
            ("active", 3),
            ("completed", 10),
        ]
        result = repo.count_by_status(mock_db)

        assert result == {"new": 5, "active": 3, "completed": 10}

    def test_count_by_status_empty(self, repo, mock_db):
        """Should return empty dict when no cases."""
        mock_db.query.return_value.group_by.return_value.all.return_value = []
        result = repo.count_by_status(mock_db)

        assert result == {}
