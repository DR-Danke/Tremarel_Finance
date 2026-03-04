"""Tests for Document model and DTOs."""

from datetime import date, datetime, timedelta
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.interface.document_dto import (
    DocumentCreateDTO,
    DocumentResponseDTO,
    DocumentUpdateDTO,
)
from src.models.document import Document


# ============================================================================
# DocumentCreateDTO Tests
# ============================================================================


def test_document_create_dto_all_fields() -> None:
    """Test valid creation DTO with all fields."""
    restaurant_id = uuid4()
    person_id = uuid4()
    dto = DocumentCreateDTO(
        restaurant_id=restaurant_id,
        type="contrato",
        issue_date=date(2026, 1, 1),
        expiration_date=date(2027, 1, 1),
        person_id=person_id,
        description="Employment contract",
    )
    assert dto.type == "contrato"
    assert dto.issue_date == date(2026, 1, 1)
    assert dto.expiration_date == date(2027, 1, 1)
    assert dto.person_id == person_id
    assert dto.description == "Employment contract"
    assert dto.restaurant_id == restaurant_id
    print("INFO [TestDocument]: test_document_create_dto_all_fields - PASSED")


def test_document_create_dto_required_only() -> None:
    """Test valid creation DTO with required fields only."""
    restaurant_id = uuid4()
    dto = DocumentCreateDTO(
        restaurant_id=restaurant_id,
        type="permiso",
    )
    assert dto.type == "permiso"
    assert dto.issue_date is None
    assert dto.expiration_date is None
    assert dto.person_id is None
    assert dto.description is None
    print("INFO [TestDocument]: test_document_create_dto_required_only - PASSED")


def test_document_create_dto_missing_required_fields() -> None:
    """Test that missing required fields are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        DocumentCreateDTO()
    errors = str(exc_info.value)
    assert "restaurant_id" in errors
    assert "type" in errors
    print("INFO [TestDocument]: test_document_create_dto_missing_required_fields - PASSED")


def test_document_create_dto_empty_type() -> None:
    """Test that empty type is rejected (min_length=1)."""
    with pytest.raises(ValidationError) as exc_info:
        DocumentCreateDTO(
            restaurant_id=uuid4(),
            type="",
        )
    assert "type" in str(exc_info.value)
    print("INFO [TestDocument]: test_document_create_dto_empty_type - PASSED")


def test_document_create_dto_type_too_long() -> None:
    """Test that type exceeding 100 chars is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        DocumentCreateDTO(
            restaurant_id=uuid4(),
            type="A" * 101,
        )
    assert "type" in str(exc_info.value)
    print("INFO [TestDocument]: test_document_create_dto_type_too_long - PASSED")


def test_document_create_dto_expiration_before_issue() -> None:
    """Test that expiration_date before issue_date is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        DocumentCreateDTO(
            restaurant_id=uuid4(),
            type="contrato",
            issue_date=date(2026, 6, 1),
            expiration_date=date(2026, 1, 1),
        )
    assert "expiration_date" in str(exc_info.value)
    print("INFO [TestDocument]: test_document_create_dto_expiration_before_issue - PASSED")


def test_document_create_dto_expiration_equal_issue() -> None:
    """Test that expiration_date equal to issue_date is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        DocumentCreateDTO(
            restaurant_id=uuid4(),
            type="contrato",
            issue_date=date(2026, 6, 1),
            expiration_date=date(2026, 6, 1),
        )
    assert "expiration_date" in str(exc_info.value)
    print("INFO [TestDocument]: test_document_create_dto_expiration_equal_issue - PASSED")


def test_document_create_dto_only_issue_date() -> None:
    """Test valid when only issue_date is provided."""
    dto = DocumentCreateDTO(
        restaurant_id=uuid4(),
        type="factura",
        issue_date=date(2026, 3, 1),
    )
    assert dto.issue_date == date(2026, 3, 1)
    assert dto.expiration_date is None
    print("INFO [TestDocument]: test_document_create_dto_only_issue_date - PASSED")


def test_document_create_dto_only_expiration_date() -> None:
    """Test valid when only expiration_date is provided."""
    dto = DocumentCreateDTO(
        restaurant_id=uuid4(),
        type="licencia",
        expiration_date=date(2027, 12, 31),
    )
    assert dto.issue_date is None
    assert dto.expiration_date == date(2027, 12, 31)
    print("INFO [TestDocument]: test_document_create_dto_only_expiration_date - PASSED")


# ============================================================================
# DocumentUpdateDTO Tests
# ============================================================================


def test_document_update_dto_single_field() -> None:
    """Test partial update with a single field."""
    dto = DocumentUpdateDTO(type="licencia")
    assert dto.type == "licencia"
    assert dto.issue_date is None
    assert dto.expiration_date is None
    assert dto.person_id is None
    assert dto.description is None
    print("INFO [TestDocument]: test_document_update_dto_single_field - PASSED")


def test_document_update_dto_empty() -> None:
    """Test update DTO with no fields set (all optional)."""
    dto = DocumentUpdateDTO()
    assert dto.type is None
    assert dto.issue_date is None
    assert dto.expiration_date is None
    assert dto.person_id is None
    assert dto.description is None
    print("INFO [TestDocument]: test_document_update_dto_empty - PASSED")


def test_document_update_dto_type_too_long() -> None:
    """Test that type exceeding 100 chars is rejected in update."""
    with pytest.raises(ValidationError) as exc_info:
        DocumentUpdateDTO(type="A" * 101)
    assert "type" in str(exc_info.value)
    print("INFO [TestDocument]: test_document_update_dto_type_too_long - PASSED")


# ============================================================================
# DocumentResponseDTO Tests
# ============================================================================


def test_document_response_dto_from_attributes() -> None:
    """Test response DTO from mock model object."""
    mock_document = MagicMock(spec=Document)
    mock_document.id = uuid4()
    mock_document.restaurant_id = uuid4()
    mock_document.type = "contrato"
    mock_document.file_url = "/uploads/documents/test.pdf"
    mock_document.issue_date = date(2026, 1, 1)
    mock_document.expiration_date = date(2028, 1, 1)
    mock_document.person_id = uuid4()
    mock_document.description = "Test contract"
    mock_document.processing_status = None
    mock_document.processing_result = None
    mock_document.created_at = datetime(2026, 1, 15, 10, 30, 0)
    mock_document.updated_at = None

    dto = DocumentResponseDTO.model_validate(mock_document, from_attributes=True)
    assert dto.id == mock_document.id
    assert dto.restaurant_id == mock_document.restaurant_id
    assert dto.type == "contrato"
    assert dto.file_url == "/uploads/documents/test.pdf"
    assert dto.description == "Test contract"
    assert dto.updated_at is None
    print("INFO [TestDocument]: test_document_response_dto_from_attributes - PASSED")


def test_document_response_dto_expiration_status_valid_no_date() -> None:
    """Test expiration_status is 'valid' when no expiration_date."""
    mock_document = MagicMock(spec=Document)
    mock_document.id = uuid4()
    mock_document.restaurant_id = uuid4()
    mock_document.type = "factura"
    mock_document.file_url = None
    mock_document.issue_date = None
    mock_document.expiration_date = None
    mock_document.person_id = None
    mock_document.description = None
    mock_document.processing_status = None
    mock_document.processing_result = None
    mock_document.created_at = datetime(2026, 1, 15, 10, 30, 0)
    mock_document.updated_at = None

    dto = DocumentResponseDTO.model_validate(mock_document, from_attributes=True)
    assert dto.expiration_status == "valid"
    print("INFO [TestDocument]: test_document_response_dto_expiration_status_valid_no_date - PASSED")


def test_document_response_dto_expiration_status_valid_far_future() -> None:
    """Test expiration_status is 'valid' when expiration_date > 30 days ahead."""
    mock_document = MagicMock(spec=Document)
    mock_document.id = uuid4()
    mock_document.restaurant_id = uuid4()
    mock_document.type = "licencia"
    mock_document.file_url = None
    mock_document.issue_date = None
    mock_document.expiration_date = date.today() + timedelta(days=60)
    mock_document.person_id = None
    mock_document.description = None
    mock_document.processing_status = None
    mock_document.processing_result = None
    mock_document.created_at = datetime(2026, 1, 15, 10, 30, 0)
    mock_document.updated_at = None

    dto = DocumentResponseDTO.model_validate(mock_document, from_attributes=True)
    assert dto.expiration_status == "valid"
    print("INFO [TestDocument]: test_document_response_dto_expiration_status_valid_far_future - PASSED")


def test_document_response_dto_expiration_status_expiring_soon() -> None:
    """Test expiration_status is 'expiring_soon' when expiration_date <= 30 days ahead."""
    mock_document = MagicMock(spec=Document)
    mock_document.id = uuid4()
    mock_document.restaurant_id = uuid4()
    mock_document.type = "permiso"
    mock_document.file_url = None
    mock_document.issue_date = None
    mock_document.expiration_date = date.today() + timedelta(days=15)
    mock_document.person_id = None
    mock_document.description = None
    mock_document.processing_status = None
    mock_document.processing_result = None
    mock_document.created_at = datetime(2026, 1, 15, 10, 30, 0)
    mock_document.updated_at = None

    dto = DocumentResponseDTO.model_validate(mock_document, from_attributes=True)
    assert dto.expiration_status == "expiring_soon"
    print("INFO [TestDocument]: test_document_response_dto_expiration_status_expiring_soon - PASSED")


def test_document_response_dto_expiration_status_expiring_soon_exactly_30() -> None:
    """Test expiration_status is 'expiring_soon' when expiration_date is exactly 30 days ahead."""
    mock_document = MagicMock(spec=Document)
    mock_document.id = uuid4()
    mock_document.restaurant_id = uuid4()
    mock_document.type = "permiso"
    mock_document.file_url = None
    mock_document.issue_date = None
    mock_document.expiration_date = date.today() + timedelta(days=30)
    mock_document.person_id = None
    mock_document.description = None
    mock_document.processing_status = None
    mock_document.processing_result = None
    mock_document.created_at = datetime(2026, 1, 15, 10, 30, 0)
    mock_document.updated_at = None

    dto = DocumentResponseDTO.model_validate(mock_document, from_attributes=True)
    assert dto.expiration_status == "expiring_soon"
    print("INFO [TestDocument]: test_document_response_dto_expiration_status_expiring_soon_exactly_30 - PASSED")


def test_document_response_dto_expiration_status_expiring_soon_today() -> None:
    """Test expiration_status is 'expiring_soon' when expiration_date is today."""
    mock_document = MagicMock(spec=Document)
    mock_document.id = uuid4()
    mock_document.restaurant_id = uuid4()
    mock_document.type = "contrato"
    mock_document.file_url = None
    mock_document.issue_date = None
    mock_document.expiration_date = date.today()
    mock_document.person_id = None
    mock_document.description = None
    mock_document.processing_status = None
    mock_document.processing_result = None
    mock_document.created_at = datetime(2026, 1, 15, 10, 30, 0)
    mock_document.updated_at = None

    dto = DocumentResponseDTO.model_validate(mock_document, from_attributes=True)
    assert dto.expiration_status == "expiring_soon"
    print("INFO [TestDocument]: test_document_response_dto_expiration_status_expiring_soon_today - PASSED")


def test_document_response_dto_expiration_status_expired() -> None:
    """Test expiration_status is 'expired' when expiration_date is in the past."""
    mock_document = MagicMock(spec=Document)
    mock_document.id = uuid4()
    mock_document.restaurant_id = uuid4()
    mock_document.type = "licencia"
    mock_document.file_url = None
    mock_document.issue_date = None
    mock_document.expiration_date = date.today() - timedelta(days=1)
    mock_document.person_id = None
    mock_document.description = None
    mock_document.processing_status = None
    mock_document.processing_result = None
    mock_document.created_at = datetime(2026, 1, 15, 10, 30, 0)
    mock_document.updated_at = None

    dto = DocumentResponseDTO.model_validate(mock_document, from_attributes=True)
    assert dto.expiration_status == "expired"
    print("INFO [TestDocument]: test_document_response_dto_expiration_status_expired - PASSED")


# ============================================================================
# Document Model Tests
# ============================================================================


def test_document_model_repr() -> None:
    """Test Document model __repr__ method."""
    document = Document()
    document.id = uuid4()
    document.type = "contrato"
    document.restaurant_id = uuid4()

    repr_str = repr(document)
    assert "contrato" in repr_str
    assert "Document" in repr_str
    print("INFO [TestDocument]: test_document_model_repr - PASSED")


def test_document_model_tablename() -> None:
    """Test Document model has correct table name."""
    assert Document.__tablename__ == "document"
    print("INFO [TestDocument]: test_document_model_tablename - PASSED")
