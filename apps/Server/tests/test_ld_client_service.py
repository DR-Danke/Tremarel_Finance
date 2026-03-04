"""Unit tests for LdClientService."""

from unittest.mock import MagicMock, patch

import pytest

from src.core.services.ld_client_service import LdClientService
from src.interface.legaldesk_dto import ClientCreateDTO, ClientUpdateDTO


@pytest.fixture
def service():
    """Create a fresh LdClientService instance."""
    return LdClientService()


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_client():
    """Create a mock LdClient object."""
    client = MagicMock()
    client.id = 1
    client.name = "Acme Corp"
    client.client_type = "company"
    client.contact_email = "info@acme.com"
    return client


class TestCreateClient:
    """Tests for LdClientService.create."""

    @patch("src.core.services.ld_client_service.ld_client_repository")
    def test_create_client(self, mock_repo, service, mock_db, mock_client):
        """Should delegate to repository and return created client."""
        mock_repo.create.return_value = mock_client
        data = ClientCreateDTO(name="Acme Corp", client_type="company")

        result = service.create(mock_db, data)

        mock_repo.create.assert_called_once_with(mock_db, data.model_dump())
        assert result == mock_client
        assert result.id == 1


class TestUpdateClient:
    """Tests for LdClientService.update."""

    @patch("src.core.services.ld_client_service.ld_client_repository")
    def test_update_client_success(self, mock_repo, service, mock_db, mock_client):
        """Should update client when found."""
        mock_repo.get_by_id.return_value = mock_client
        mock_repo.update.return_value = mock_client
        data = ClientUpdateDTO(name="Acme Corp Updated")

        result = service.update(mock_db, 1, data)

        mock_repo.get_by_id.assert_called_once_with(mock_db, 1)
        mock_repo.update.assert_called_once_with(mock_db, 1, data.model_dump(exclude_unset=True))
        assert result == mock_client

    @patch("src.core.services.ld_client_service.ld_client_repository")
    def test_update_client_not_found(self, mock_repo, service, mock_db):
        """Should return None when client not found."""
        mock_repo.get_by_id.return_value = None

        result = service.update(mock_db, 999, ClientUpdateDTO(name="Updated"))

        mock_repo.get_by_id.assert_called_once_with(mock_db, 999)
        mock_repo.update.assert_not_called()
        assert result is None


class TestGetClient:
    """Tests for LdClientService.get."""

    @patch("src.core.services.ld_client_service.ld_client_repository")
    def test_get_client(self, mock_repo, service, mock_db, mock_client):
        """Should return client when found."""
        mock_repo.get_by_id.return_value = mock_client

        result = service.get(mock_db, 1)

        mock_repo.get_by_id.assert_called_once_with(mock_db, 1)
        assert result == mock_client

    @patch("src.core.services.ld_client_service.ld_client_repository")
    def test_get_client_not_found(self, mock_repo, service, mock_db):
        """Should return None when not found."""
        mock_repo.get_by_id.return_value = None

        result = service.get(mock_db, 999)

        assert result is None


class TestListAll:
    """Tests for LdClientService.list_all."""

    @patch("src.core.services.ld_client_service.ld_client_repository")
    def test_list_all(self, mock_repo, service, mock_db, mock_client):
        """Should return list of all clients."""
        mock_repo.list_all.return_value = [mock_client]

        result = service.list_all(mock_db)

        mock_repo.list_all.assert_called_once_with(mock_db)
        assert len(result) == 1
        assert result[0] == mock_client


class TestSearchClient:
    """Tests for LdClientService.search."""

    @patch("src.core.services.ld_client_service.ld_client_repository")
    def test_search(self, mock_repo, service, mock_db, mock_client):
        """Should delegate search to repository."""
        mock_repo.search_by_name.return_value = [mock_client]

        result = service.search(mock_db, "Acme")

        mock_repo.search_by_name.assert_called_once_with(mock_db, "Acme")
        assert len(result) == 1
        assert result[0] == mock_client
