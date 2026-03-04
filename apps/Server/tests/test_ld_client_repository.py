"""Unit tests for LdClientRepository."""

from unittest.mock import MagicMock, patch

import pytest

from src.repository.ld_client_repository import LdClientRepository


@pytest.fixture
def repo():
    """Create a fresh LdClientRepository instance."""
    return LdClientRepository()


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
    client.created_at = "2026-01-01T00:00:00"
    return client


class TestCreateClient:
    """Tests for LdClientRepository.create."""

    def test_create_client(self, repo, mock_db):
        """Verify db.add, db.commit, db.refresh are called."""
        data = {"name": "Acme Corp", "client_type": "company"}
        result = repo.create(mock_db, data)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert result is not None


class TestGetById:
    """Tests for LdClientRepository.get_by_id."""

    def test_get_by_id_found(self, repo, mock_db, mock_client):
        """Should return client when found."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_client
        result = repo.get_by_id(mock_db, 1)

        assert result == mock_client
        mock_db.query.assert_called_once()

    def test_get_by_id_not_found(self, repo, mock_db):
        """Should return None when not found."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = repo.get_by_id(mock_db, 999)

        assert result is None


class TestListAll:
    """Tests for LdClientRepository.list_all."""

    def test_list_all(self, repo, mock_db, mock_client):
        """Should return list of clients ordered by created_at desc."""
        mock_db.query.return_value.order_by.return_value.all.return_value = [mock_client]
        result = repo.list_all(mock_db)

        assert len(result) == 1
        assert result[0] == mock_client

    def test_list_all_empty(self, repo, mock_db):
        """Should return empty list when no clients exist."""
        mock_db.query.return_value.order_by.return_value.all.return_value = []
        result = repo.list_all(mock_db)

        assert result == []


class TestUpdateClient:
    """Tests for LdClientRepository.update."""

    def test_update_client(self, repo, mock_db, mock_client):
        """Verify fields updated via setattr."""
        mock_db.query.return_value.filter.return_value.first.return_value = mock_client
        data = {"name": "Acme Corp Updated", "contact_email": "new@acme.com"}

        result = repo.update(mock_db, 1, data)

        assert result is not None
        mock_db.commit.assert_called()
        mock_db.refresh.assert_called()

    def test_update_client_not_found(self, repo, mock_db):
        """Should return None when client not found."""
        mock_db.query.return_value.filter.return_value.first.return_value = None
        result = repo.update(mock_db, 999, {"name": "Updated"})

        assert result is None


class TestSearchByName:
    """Tests for LdClientRepository.search_by_name."""

    def test_search_by_name(self, repo, mock_db, mock_client):
        """Verify ilike filter is applied."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_client]
        result = repo.search_by_name(mock_db, "Acme")

        assert len(result) == 1
        mock_db.query.assert_called()

    def test_search_by_name_no_results(self, repo, mock_db):
        """Should return empty list when no matches."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        result = repo.search_by_name(mock_db, "NonExistent")

        assert result == []

    def test_search_by_name_empty_query(self, repo, mock_db, mock_client):
        """Empty string should still work (returns all via ilike %%)."""
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_client]
        result = repo.search_by_name(mock_db, "")

        assert len(result) == 1
