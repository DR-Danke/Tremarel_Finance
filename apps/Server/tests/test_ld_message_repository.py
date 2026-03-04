"""Unit tests for LdMessageRepository."""

from unittest.mock import MagicMock

import pytest

from src.models.ld_case_message import LdCaseMessage
from src.repository.ld_message_repository import LdMessageRepository


@pytest.fixture
def repo():
    return LdMessageRepository()


@pytest.fixture
def mock_db():
    return MagicMock()


class TestCreate:
    def test_create_sets_all_fields(self, repo, mock_db):
        data = {
            "case_id": 1,
            "sender_type": "specialist",
            "sender_name": "John Doe",
            "message": "Please review the document.",
            "is_internal": True,
        }
        repo.create(mock_db, data)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        created = mock_db.add.call_args[0][0]
        assert isinstance(created, LdCaseMessage)
        assert created.case_id == 1
        assert created.sender_type == "specialist"
        assert created.sender_name == "John Doe"
        assert created.message == "Please review the document."
        assert created.is_internal is True

    def test_create_defaults_is_internal_false(self, repo, mock_db):
        data = {
            "case_id": 2,
            "sender_type": "client",
            "message": "Hello",
        }
        repo.create(mock_db, data)
        created = mock_db.add.call_args[0][0]
        assert created.is_internal is False
        assert created.sender_name is None


class TestGetByCase:
    def test_get_by_case_exclude_internal(self, repo, mock_db):
        mock_query = mock_db.query.return_value
        mock_filter1 = mock_query.filter.return_value
        mock_filter2 = mock_filter1.filter.return_value
        mock_order = mock_filter2.order_by.return_value
        mock_order.all.return_value = [MagicMock()]

        result = repo.get_by_case(mock_db, case_id=1, include_internal=False)

        mock_db.query.assert_called_once_with(LdCaseMessage)
        assert len(result) == 1

    def test_get_by_case_include_internal(self, repo, mock_db):
        mock_query = mock_db.query.return_value
        mock_filter = mock_query.filter.return_value
        mock_order = mock_filter.order_by.return_value
        mock_order.all.return_value = [MagicMock(), MagicMock(), MagicMock()]

        result = repo.get_by_case(mock_db, case_id=1, include_internal=True)

        assert len(result) == 3
