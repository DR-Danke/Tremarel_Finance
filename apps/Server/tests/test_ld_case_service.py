"""Unit tests for LdCaseService."""

from unittest.mock import MagicMock, patch

import pytest

from src.core.services.ld_case_service import LdCaseService
from src.interface.legaldesk_dto import (
    CaseCreateDTO,
    CaseFilterDTO,
    CaseStatus,
    CaseUpdateDTO,
    LegalDomain,
)


@pytest.fixture
def service():
    """Create a fresh LdCaseService instance."""
    return LdCaseService()


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_case():
    """Create a mock LdCase object."""
    case = MagicMock()
    case.id = 1
    case.case_number = "LD-202601-0001"
    case.title = "Corporate Advisory"
    case.status = "new"
    case.client_id = 10
    case.specialists = []
    case.deliverables = []
    case.messages = []
    case.documents = []
    return case


@pytest.fixture
def current_user():
    """Create a mock current user dict."""
    return {"id": 1, "email": "admin@example.com", "role": "admin"}


class TestCreateCase:
    """Tests for LdCaseService.create_case."""

    @patch("src.core.services.ld_case_service.ld_case_repository")
    def test_create_case(self, mock_repo, service, mock_db, mock_case, current_user):
        """Should generate case number and create case with default status."""
        mock_repo.generate_case_number.return_value = "LD-202601-0001"
        mock_repo.create.return_value = mock_case
        data = CaseCreateDTO(
            title="Corporate Advisory",
            client_id=10,
            legal_domain=LegalDomain.CORPORATE,
        )

        result = service.create_case(mock_db, data, current_user)

        mock_repo.generate_case_number.assert_called_once_with(mock_db)
        mock_repo.create.assert_called_once()
        create_args = mock_repo.create.call_args[0][1]
        assert create_args["case_number"] == "LD-202601-0001"
        assert create_args["status"] == "new"
        assert result == mock_case


class TestUpdateCase:
    """Tests for LdCaseService.update_case."""

    @patch("src.core.services.ld_case_service.ld_case_repository")
    def test_update_case_success(self, mock_repo, service, mock_db, mock_case):
        """Should update case when found."""
        mock_repo.get_by_id.return_value = mock_case
        mock_repo.update.return_value = mock_case
        data = CaseUpdateDTO(title="Updated Title")

        result = service.update_case(mock_db, 1, data)

        mock_repo.get_by_id.assert_called_once_with(mock_db, 1)
        mock_repo.update.assert_called_once()
        assert result == mock_case

    @patch("src.core.services.ld_case_service.ld_case_repository")
    def test_update_case_not_found(self, mock_repo, service, mock_db):
        """Should return None when case not found."""
        mock_repo.get_by_id.return_value = None

        result = service.update_case(mock_db, 999, CaseUpdateDTO(title="Updated"))

        mock_repo.get_by_id.assert_called_once_with(mock_db, 999)
        mock_repo.update.assert_not_called()
        assert result is None


class TestUpdateCaseStatus:
    """Tests for LdCaseService.update_case_status."""

    @patch("src.core.services.ld_case_service.ld_case_repository")
    def test_update_case_status_valid_transition(self, mock_repo, service, mock_db, mock_case):
        """Should allow valid status transition (new -> classifying)."""
        mock_case.status = CaseStatus.NEW
        mock_repo.get_by_id.return_value = mock_case
        mock_repo.update_status.return_value = mock_case

        result = service.update_case_status(mock_db, 1, CaseStatus.CLASSIFYING)

        mock_repo.update_status.assert_called_once_with(mock_db, 1, CaseStatus.CLASSIFYING)
        assert result == mock_case

    @patch("src.core.services.ld_case_service.ld_case_repository")
    def test_update_case_status_invalid_transition(self, mock_repo, service, mock_db, mock_case):
        """Should raise ValueError for invalid transition (closed -> active)."""
        mock_case.status = CaseStatus.CLOSED
        mock_repo.get_by_id.return_value = mock_case

        with pytest.raises(ValueError, match="Invalid status transition"):
            service.update_case_status(mock_db, 1, CaseStatus.ACTIVE)

        mock_repo.update_status.assert_not_called()

    @patch("src.core.services.ld_case_service.ld_case_repository")
    def test_update_case_status_archived_no_transitions(self, mock_repo, service, mock_db, mock_case):
        """Archived status has no valid transitions."""
        mock_case.status = CaseStatus.ARCHIVED
        mock_repo.get_by_id.return_value = mock_case

        with pytest.raises(ValueError, match="Invalid status transition"):
            service.update_case_status(mock_db, 1, CaseStatus.CLOSED)

        mock_repo.update_status.assert_not_called()

    @patch("src.core.services.ld_case_service.ld_case_repository")
    def test_update_case_status_not_found(self, mock_repo, service, mock_db):
        """Should return None when case not found."""
        mock_repo.get_by_id.return_value = None

        result = service.update_case_status(mock_db, 999, CaseStatus.CLASSIFYING)

        assert result is None
        mock_repo.update_status.assert_not_called()


class TestGetCaseWithDetails:
    """Tests for LdCaseService.get_case_with_details."""

    @patch("src.core.services.ld_case_service.ld_case_repository")
    def test_get_case_with_details(self, mock_repo, service, mock_db, mock_case):
        """Should return case with relationships."""
        mock_repo.get_by_id.return_value = mock_case

        result = service.get_case_with_details(mock_db, 1)

        mock_repo.get_by_id.assert_called_once_with(mock_db, 1)
        assert result == mock_case

    @patch("src.core.services.ld_case_service.ld_case_repository")
    def test_get_case_with_details_not_found(self, mock_repo, service, mock_db):
        """Should return None when case not found."""
        mock_repo.get_by_id.return_value = None

        result = service.get_case_with_details(mock_db, 999)

        assert result is None


class TestListCases:
    """Tests for LdCaseService.list_cases."""

    @patch("src.core.services.ld_case_service.ld_case_repository")
    def test_list_cases(self, mock_repo, service, mock_db, mock_case):
        """Should delegate to repository with filters."""
        mock_repo.list_cases.return_value = [mock_case]
        filters = CaseFilterDTO()

        result = service.list_cases(mock_db, filters)

        mock_repo.list_cases.assert_called_once_with(mock_db, filters)
        assert len(result) == 1
        assert result[0] == mock_case
