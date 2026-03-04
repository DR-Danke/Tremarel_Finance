"""Unit tests for LdPricingRepository."""

from unittest.mock import MagicMock

import pytest

from src.repository.ld_pricing_repository import LdPricingRepository


@pytest.fixture
def repo():
    """Create a fresh LdPricingRepository instance."""
    return LdPricingRepository()


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_pricing_entry():
    """Create a mock LdPricingHistory object."""
    entry = MagicMock()
    entry.id = 1
    entry.case_id = 1
    entry.action = "proposal"
    entry.previous_amount = 800
    entry.new_amount = 1000
    entry.currency = "EUR"
    entry.changed_by = "admin@faroo.com"
    entry.notes = "Initial proposal"
    entry.created_at = "2026-03-01T00:00:00"
    return entry


class TestCreatePricingEntry:
    """Tests for LdPricingRepository.create."""

    def test_create_pricing_entry(self, repo, mock_db):
        """Verify db.add, db.commit, db.refresh are called."""
        data = {
            "case_id": 1,
            "action": "proposal",
            "previous_amount": 800,
            "new_amount": 1000,
            "currency": "EUR",
            "changed_by": "admin@faroo.com",
            "notes": "Initial proposal",
        }
        result = repo.create(mock_db, data)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert result is not None


class TestGetByCase:
    """Tests for LdPricingRepository.get_by_case."""

    def test_get_by_case_returns_list(self, repo, mock_db, mock_pricing_entry):
        """Should return list of pricing entries."""
        (
            mock_db.query.return_value
            .filter.return_value
            .order_by.return_value
            .all.return_value
        ) = [mock_pricing_entry]
        result = repo.get_by_case(mock_db, 1)

        assert len(result) == 1
        assert result[0] == mock_pricing_entry

    def test_get_by_case_empty(self, repo, mock_db):
        """Should return empty list for unknown case_id."""
        (
            mock_db.query.return_value
            .filter.return_value
            .order_by.return_value
            .all.return_value
        ) = []
        result = repo.get_by_case(mock_db, 999)

        assert result == []


class TestGetLatest:
    """Tests for LdPricingRepository.get_latest."""

    def test_get_latest_returns_entry(self, repo, mock_db, mock_pricing_entry):
        """Should return single most recent entry."""
        (
            mock_db.query.return_value
            .filter.return_value
            .order_by.return_value
            .first.return_value
        ) = mock_pricing_entry
        result = repo.get_latest(mock_db, 1)

        assert result == mock_pricing_entry

    def test_get_latest_returns_none(self, repo, mock_db):
        """Should return None for unknown case_id."""
        (
            mock_db.query.return_value
            .filter.return_value
            .order_by.return_value
            .first.return_value
        ) = None
        result = repo.get_latest(mock_db, 999)

        assert result is None
