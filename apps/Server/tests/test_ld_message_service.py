"""Unit tests for LdMessageService."""

from unittest.mock import MagicMock, patch

import pytest

from src.core.services.ld_message_service import LdMessageService
from src.interface.legaldesk_dto import MessageCreateDTO


@pytest.fixture
def service():
    """Create a fresh LdMessageService instance."""
    return LdMessageService()


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_message():
    """Create a mock LdCaseMessage object."""
    message = MagicMock()
    message.id = 1
    message.case_id = 10
    message.sender_type = "system"
    message.message = "Case opened"
    message.is_internal = False
    return message


class TestCreateMessage:
    """Tests for LdMessageService.create_message."""

    @patch("src.core.services.ld_message_service.ld_message_repository")
    def test_create_message(self, mock_repo, service, mock_db, mock_message):
        """Should build dict with case_id, delegate to repository, and return created message."""
        mock_repo.create.return_value = mock_message
        data = MessageCreateDTO(case_id=0, message="Case opened", sender_type="system")

        result = service.create_message(mock_db, 10, data)

        expected_data = data.model_dump()
        expected_data["case_id"] = 10
        mock_repo.create.assert_called_once_with(mock_db, expected_data)
        assert result == mock_message
        assert result.id == 1


class TestGetCaseMessages:
    """Tests for LdMessageService.get_case_messages."""

    @patch("src.core.services.ld_message_service.ld_message_repository")
    def test_get_case_messages_default(self, mock_repo, service, mock_db, mock_message):
        """Should delegate to repository with include_internal=False by default."""
        mock_repo.get_by_case.return_value = [mock_message]

        result = service.get_case_messages(mock_db, 10)

        mock_repo.get_by_case.assert_called_once_with(mock_db, 10, include_internal=False)
        assert len(result) == 1
        assert result[0] == mock_message

    @patch("src.core.services.ld_message_service.ld_message_repository")
    def test_get_case_messages_include_internal(self, mock_repo, service, mock_db, mock_message):
        """Should pass include_internal=True to repository."""
        mock_repo.get_by_case.return_value = [mock_message]

        result = service.get_case_messages(mock_db, 10, include_internal=True)

        mock_repo.get_by_case.assert_called_once_with(mock_db, 10, include_internal=True)
        assert len(result) == 1
