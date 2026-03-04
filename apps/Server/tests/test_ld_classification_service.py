"""Unit tests for Legal Desk AI classification service."""

import json
import sys
from decimal import Decimal
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

# Create a mock openai module so tests work without openai installed
_mock_openai_module = ModuleType("openai")
_mock_openai_module.OpenAI = MagicMock  # type: ignore[attr-defined]
sys.modules.setdefault("openai", _mock_openai_module)

from src.core.services.ld_classification_service import LdClassificationService  # noqa: E402
from src.interface.legaldesk_dto import (  # noqa: E402
    CaseComplexity,
    CaseType,
    ClassificationResultDTO,
    LegalDomain,
)


@pytest.fixture
def service():
    """Classification service instance."""
    return LdClassificationService()


@pytest.fixture
def mock_db():
    """Mock database session."""
    return MagicMock()


@pytest.fixture
def mock_case():
    """Mock LdCase with title and description."""
    case = MagicMock()
    case.id = 1
    case.title = "Shareholder merger acquisition dispute"
    case.description = "Board meeting about corporate restructuring"
    return case


class TestClassifyCase:
    """Tests for classify_case orchestration method."""

    @patch("src.core.services.ld_classification_service.get_settings")
    @patch("src.core.services.ld_classification_service.ld_case_repository")
    def test_classify_case_with_openai_success(self, mock_repo, mock_settings, service, mock_db, mock_case):
        """OpenAI classification stores result and returns DTO."""
        mock_repo.get_by_id.return_value = mock_case
        mock_settings.return_value.OPENAI_API_KEY = "sk-test-key"

        expected_dto = ClassificationResultDTO(
            legal_domain=LegalDomain.CORPORATE,
            complexity=CaseComplexity.HIGH,
            case_type=CaseType.ADVISORY,
            confidence=Decimal("0.9"),
            suggested_tags=["corporate restructuring"],
        )

        with patch.object(service, "_classify_with_openai", return_value=expected_dto):
            result = service.classify_case(mock_db, 1)

        assert result.legal_domain == LegalDomain.CORPORATE
        assert result.confidence == Decimal("0.9")
        mock_repo.update.assert_called_once()
        update_data = mock_repo.update.call_args[0][2]
        assert "ai_classification" in update_data

    @patch("src.core.services.ld_classification_service.get_settings")
    @patch("src.core.services.ld_classification_service.ld_case_repository")
    def test_classify_case_falls_back_on_missing_api_key(self, mock_repo, mock_settings, service, mock_db, mock_case):
        """Empty OPENAI_API_KEY triggers keyword fallback."""
        mock_repo.get_by_id.return_value = mock_case
        mock_settings.return_value.OPENAI_API_KEY = ""

        result = service.classify_case(mock_db, 1)

        assert isinstance(result, ClassificationResultDTO)
        assert result.confidence == Decimal("0.5")
        mock_repo.update.assert_called_once()

    @patch("src.core.services.ld_classification_service.get_settings")
    @patch("src.core.services.ld_classification_service.ld_case_repository")
    def test_classify_case_falls_back_on_openai_error(self, mock_repo, mock_settings, service, mock_db, mock_case):
        """OpenAI error triggers keyword fallback."""
        mock_repo.get_by_id.return_value = mock_case
        mock_settings.return_value.OPENAI_API_KEY = "sk-test-key"

        with patch.object(service, "_classify_with_openai", side_effect=Exception("API timeout")):
            result = service.classify_case(mock_db, 1)

        assert isinstance(result, ClassificationResultDTO)
        assert result.confidence == Decimal("0.5")

    @patch("src.core.services.ld_classification_service.ld_case_repository")
    def test_classify_case_not_found(self, mock_repo, service, mock_db):
        """ValueError raised when case does not exist."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Case with id 999 not found"):
            service.classify_case(mock_db, 999)


class TestClassifyWithKeywords:
    """Tests for keyword-based classification fallback."""

    def test_corporate_domain_detected(self, service):
        """Text with corporate keywords classified as corporate."""
        text = "merger and shareholder agreement for the board"
        result = service._classify_with_keywords(text)

        assert result.legal_domain == LegalDomain.CORPORATE
        assert result.case_type == CaseType.ADVISORY

    def test_litigation_domain_detected(self, service):
        """Text with litigation keywords classified as litigation with litigation type."""
        text = "filing a lawsuit in court for damages"
        result = service._classify_with_keywords(text)

        assert result.legal_domain == LegalDomain.LITIGATION
        assert result.case_type == CaseType.LITIGATION

    def test_default_domain_when_no_keywords_match(self, service):
        """Generic text with no keyword matches defaults to commercial."""
        text = "general inquiry about some matter"
        result = service._classify_with_keywords(text)

        assert result.legal_domain == LegalDomain.COMMERCIAL

    def test_confidence_is_half_for_keywords(self, service):
        """Keyword-based classification always returns 0.5 confidence."""
        text = "patent infringement case"
        result = service._classify_with_keywords(text)

        assert result.confidence == Decimal("0.5")

    def test_case_type_advisory_for_non_litigation(self, service):
        """Non-litigation domains get advisory case type."""
        text = "tax filing and fiscal deduction review"
        result = service._classify_with_keywords(text)

        assert result.legal_domain == LegalDomain.TAX
        assert result.case_type == CaseType.ADVISORY


class TestClassifyWithOpenai:
    """Tests for OpenAI-based classification."""

    @patch("src.core.services.ld_classification_service.get_settings")
    def test_successful_openai_classification(self, mock_settings, service):
        """Valid OpenAI JSON response parsed into ClassificationResultDTO."""
        mock_settings.return_value.OPENAI_API_KEY = "sk-test-key"

        openai_response = {
            "legal_domain": "corporate",
            "case_type": "advisory",
            "complexity": "high",
            "confidence": 0.92,
            "reasoning": "Corporate restructuring case",
        }

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = json.dumps(openai_response)

        with patch("openai.OpenAI") as MockOpenAI:
            mock_client = MagicMock()
            MockOpenAI.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_completion

            result = service._classify_with_openai("shareholder merger corporate")

        assert result.legal_domain == LegalDomain.CORPORATE
        assert result.complexity == CaseComplexity.HIGH
        assert result.case_type == CaseType.ADVISORY
        assert result.confidence == Decimal("0.92")
        assert "Corporate restructuring case" in result.suggested_tags

    @patch("src.core.services.ld_classification_service.get_settings")
    def test_openai_returns_invalid_json(self, mock_settings, service):
        """Malformed OpenAI response raises exception."""
        mock_settings.return_value.OPENAI_API_KEY = "sk-test-key"

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "not valid json"

        with patch("openai.OpenAI") as MockOpenAI:
            mock_client = MagicMock()
            MockOpenAI.return_value = mock_client
            mock_client.chat.completions.create.return_value = mock_completion

            with pytest.raises(json.JSONDecodeError):
                service._classify_with_openai("some case text")
