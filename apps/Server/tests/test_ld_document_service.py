"""Unit tests for LdDocumentService."""

from unittest.mock import MagicMock, patch

import pytest

from src.core.services.ld_document_service import LdDocumentService
from src.interface.legaldesk_dto import DocumentCreateDTO


@pytest.fixture
def service():
    """Create a fresh LdDocumentService instance."""
    return LdDocumentService()


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def mock_document():
    """Create a mock LdCaseDocument object."""
    document = MagicMock()
    document.id = 1
    document.case_id = 10
    document.file_name = "contract.pdf"
    document.file_url = "https://storage.example.com/contract.pdf"
    return document


class TestCreateDocument:
    """Tests for LdDocumentService.create_document."""

    @patch("src.core.services.ld_document_service.ld_document_repository")
    def test_create_document(self, mock_repo, service, mock_db, mock_document):
        """Should build dict with case_id, delegate to repository, and return created document."""
        mock_repo.create.return_value = mock_document
        data = DocumentCreateDTO(
            case_id=0,
            file_name="contract.pdf",
            file_url="https://storage.example.com/contract.pdf",
        )

        result = service.create_document(mock_db, 10, data)

        expected_data = data.model_dump()
        expected_data["case_id"] = 10
        mock_repo.create.assert_called_once_with(mock_db, expected_data)
        assert result == mock_document
        assert result.id == 1


class TestGetCaseDocuments:
    """Tests for LdDocumentService.get_case_documents."""

    @patch("src.core.services.ld_document_service.ld_document_repository")
    def test_get_case_documents(self, mock_repo, service, mock_db, mock_document):
        """Should delegate to repository get_by_case."""
        mock_repo.get_by_case.return_value = [mock_document]

        result = service.get_case_documents(mock_db, 10)

        mock_repo.get_by_case.assert_called_once_with(mock_db, 10)
        assert len(result) == 1
        assert result[0] == mock_document
