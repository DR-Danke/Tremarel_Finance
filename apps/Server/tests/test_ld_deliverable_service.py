"""Unit tests for LdDeliverableService."""

from unittest.mock import MagicMock, patch

import pytest

from src.core.services.ld_deliverable_service import LdDeliverableService
from src.interface.legaldesk_dto import DeliverableCreateDTO, DeliverableUpdateDTO


@pytest.fixture
def service():
    """Create a fresh LdDeliverableService instance."""
    return LdDeliverableService()


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_deliverable():
    """Create a mock LdCaseDeliverable object."""
    deliverable = MagicMock()
    deliverable.id = 1
    deliverable.case_id = 10
    deliverable.title = "Draft Contract"
    deliverable.status = "pending"
    return deliverable


class TestCreateDeliverable:
    """Tests for LdDeliverableService.create_deliverable."""

    @patch("src.core.services.ld_deliverable_service.ld_deliverable_repository")
    def test_create_deliverable(self, mock_repo, service, mock_db, mock_deliverable):
        """Should set case_id on data, delegate to repository, and return created deliverable."""
        mock_repo.create.return_value = mock_deliverable
        data = DeliverableCreateDTO(case_id=0, title="Draft Contract")

        result = service.create_deliverable(mock_db, 10, data)

        assert data.case_id == 10
        mock_repo.create.assert_called_once_with(mock_db, data.model_dump())
        assert result == mock_deliverable
        assert result.id == 1


class TestGetCaseDeliverables:
    """Tests for LdDeliverableService.get_case_deliverables."""

    @patch("src.core.services.ld_deliverable_service.ld_deliverable_repository")
    def test_get_case_deliverables(self, mock_repo, service, mock_db, mock_deliverable):
        """Should delegate to repository get_by_case."""
        mock_repo.get_by_case.return_value = [mock_deliverable]

        result = service.get_case_deliverables(mock_db, 10)

        mock_repo.get_by_case.assert_called_once_with(mock_db, 10)
        assert len(result) == 1
        assert result[0] == mock_deliverable


class TestUpdateDeliverable:
    """Tests for LdDeliverableService.update_deliverable."""

    @patch("src.core.services.ld_deliverable_service.ld_deliverable_repository")
    def test_update_deliverable_success(self, mock_repo, service, mock_db, mock_deliverable):
        """Should delegate to repository update with model_dump(exclude_unset=True)."""
        mock_repo.update.return_value = mock_deliverable
        data = DeliverableUpdateDTO(title="Updated Contract")

        result = service.update_deliverable(mock_db, 1, data)

        mock_repo.update.assert_called_once_with(mock_db, 1, data.model_dump(exclude_unset=True))
        assert result == mock_deliverable

    @patch("src.core.services.ld_deliverable_service.ld_deliverable_repository")
    def test_update_deliverable_not_found(self, mock_repo, service, mock_db):
        """Should return None when deliverable not found."""
        mock_repo.update.return_value = None
        data = DeliverableUpdateDTO(title="Updated Contract")

        result = service.update_deliverable(mock_db, 999, data)

        mock_repo.update.assert_called_once_with(mock_db, 999, data.model_dump(exclude_unset=True))
        assert result is None


class TestUpdateDeliverableStatus:
    """Tests for LdDeliverableService.update_deliverable_status."""

    @patch("src.core.services.ld_deliverable_service.ld_deliverable_repository")
    def test_update_deliverable_status_success(self, mock_repo, service, mock_db, mock_deliverable):
        """Should delegate to repository update_status."""
        mock_repo.update_status.return_value = mock_deliverable

        result = service.update_deliverable_status(mock_db, 1, "completed")

        mock_repo.update_status.assert_called_once_with(mock_db, 1, "completed")
        assert result == mock_deliverable

    @patch("src.core.services.ld_deliverable_service.ld_deliverable_repository")
    def test_update_deliverable_status_not_found(self, mock_repo, service, mock_db):
        """Should return None when deliverable not found."""
        mock_repo.update_status.return_value = None

        result = service.update_deliverable_status(mock_db, 999, "completed")

        mock_repo.update_status.assert_called_once_with(mock_db, 999, "completed")
        assert result is None
