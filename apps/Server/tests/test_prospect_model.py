"""Tests for Prospect model and DTOs."""

from decimal import Decimal
from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.interface.prospect_dto import (
    ProspectCreateDTO,
    ProspectFilterDTO,
    ProspectListResponseDTO,
    ProspectResponseDTO,
    ProspectUpdateDTO,
)
from src.models.prospect import Prospect


# ============================================================================
# ProspectCreateDTO Tests
# ============================================================================


def test_prospect_create_dto_valid() -> None:
    """Test valid creation DTO with all fields."""
    entity_id = uuid4()
    dto = ProspectCreateDTO(
        entity_id=entity_id,
        company_name="Acme Corp",
        contact_name="John Doe",
        contact_email="john@acme.com",
        contact_phone="+1-555-0100",
        stage="qualified",
        estimated_value=Decimal("50000.00"),
        source="referral",
        notes="Met at conference",
    )
    assert dto.entity_id == entity_id
    assert dto.company_name == "Acme Corp"
    assert dto.contact_name == "John Doe"
    assert dto.contact_email == "john@acme.com"
    assert dto.contact_phone == "+1-555-0100"
    assert dto.stage == "qualified"
    assert dto.estimated_value == Decimal("50000.00")
    assert dto.source == "referral"
    assert dto.notes == "Met at conference"
    print("INFO [TestProspect]: test_prospect_create_dto_valid - PASSED")


def test_prospect_create_dto_minimal() -> None:
    """Test valid creation DTO with only required fields."""
    entity_id = uuid4()
    dto = ProspectCreateDTO(
        entity_id=entity_id,
        company_name="Minimal Corp",
    )
    assert dto.entity_id == entity_id
    assert dto.company_name == "Minimal Corp"
    assert dto.contact_name is None
    assert dto.contact_email is None
    assert dto.contact_phone is None
    assert dto.stage == "lead"
    assert dto.estimated_value is None
    assert dto.source is None
    assert dto.notes is None
    print("INFO [TestProspect]: test_prospect_create_dto_minimal - PASSED")


def test_prospect_create_dto_invalid_stage() -> None:
    """Test that invalid stage value is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        ProspectCreateDTO(
            entity_id=uuid4(),
            company_name="Bad Stage Corp",
            stage="invalid_stage",
        )
    assert "stage" in str(exc_info.value)
    print("INFO [TestProspect]: test_prospect_create_dto_invalid_stage - PASSED")


def test_prospect_create_dto_negative_value() -> None:
    """Test that negative estimated_value is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        ProspectCreateDTO(
            entity_id=uuid4(),
            company_name="Negative Value Corp",
            estimated_value=Decimal("-100.00"),
        )
    assert "estimated_value" in str(exc_info.value)
    print("INFO [TestProspect]: test_prospect_create_dto_negative_value - PASSED")


def test_prospect_create_dto_zero_value() -> None:
    """Test that zero estimated_value is accepted (ge=0)."""
    dto = ProspectCreateDTO(
        entity_id=uuid4(),
        company_name="Zero Value Corp",
        estimated_value=Decimal("0"),
    )
    assert dto.estimated_value == Decimal("0")
    print("INFO [TestProspect]: test_prospect_create_dto_zero_value - PASSED")


def test_prospect_create_dto_empty_company_name() -> None:
    """Test that empty company_name is rejected (min_length=1)."""
    with pytest.raises(ValidationError) as exc_info:
        ProspectCreateDTO(
            entity_id=uuid4(),
            company_name="",
        )
    assert "company_name" in str(exc_info.value)
    print("INFO [TestProspect]: test_prospect_create_dto_empty_company_name - PASSED")


# ============================================================================
# ProspectUpdateDTO Tests
# ============================================================================


def test_prospect_update_dto_partial() -> None:
    """Test partial update with only some fields."""
    dto = ProspectUpdateDTO(
        stage="proposal",
        estimated_value=Decimal("75000.00"),
    )
    assert dto.stage == "proposal"
    assert dto.estimated_value == Decimal("75000.00")
    assert dto.company_name is None
    assert dto.contact_name is None
    assert dto.is_active is None
    print("INFO [TestProspect]: test_prospect_update_dto_partial - PASSED")


def test_prospect_update_dto_empty() -> None:
    """Test update DTO with no fields set (all optional)."""
    dto = ProspectUpdateDTO()
    assert dto.company_name is None
    assert dto.stage is None
    assert dto.estimated_value is None
    assert dto.is_active is None
    print("INFO [TestProspect]: test_prospect_update_dto_empty - PASSED")


# ============================================================================
# ProspectResponseDTO Tests
# ============================================================================


def test_prospect_response_dto_from_attributes() -> None:
    """Test response DTO from mock model object."""
    mock_prospect = MagicMock(spec=Prospect)
    mock_prospect.id = uuid4()
    mock_prospect.entity_id = uuid4()
    mock_prospect.company_name = "Response Corp"
    mock_prospect.contact_name = "Jane Smith"
    mock_prospect.contact_email = "jane@response.com"
    mock_prospect.contact_phone = "+1-555-0200"
    mock_prospect.stage = "negotiation"
    mock_prospect.estimated_value = Decimal("100000.00")
    mock_prospect.source = "website"
    mock_prospect.notes = "Hot lead"
    mock_prospect.is_active = True
    mock_prospect.created_at = datetime(2026, 1, 15, 10, 30, 0)
    mock_prospect.updated_at = None

    dto = ProspectResponseDTO.model_validate(mock_prospect, from_attributes=True)
    assert dto.id == mock_prospect.id
    assert dto.entity_id == mock_prospect.entity_id
    assert dto.company_name == "Response Corp"
    assert dto.stage == "negotiation"
    assert dto.estimated_value == Decimal("100000.00")
    assert dto.is_active is True
    assert dto.updated_at is None
    print("INFO [TestProspect]: test_prospect_response_dto_from_attributes - PASSED")


# ============================================================================
# ProspectFilterDTO Tests
# ============================================================================


def test_prospect_filter_dto_defaults() -> None:
    """Test filter DTO with all None defaults."""
    dto = ProspectFilterDTO()
    assert dto.stage is None
    assert dto.is_active is None
    assert dto.source is None
    print("INFO [TestProspect]: test_prospect_filter_dto_defaults - PASSED")


def test_prospect_filter_dto_with_values() -> None:
    """Test filter DTO with specific filter values."""
    dto = ProspectFilterDTO(
        stage="won",
        is_active=True,
        source="referral",
    )
    assert dto.stage == "won"
    assert dto.is_active is True
    assert dto.source == "referral"
    print("INFO [TestProspect]: test_prospect_filter_dto_with_values - PASSED")


# ============================================================================
# ProspectListResponseDTO Tests
# ============================================================================


def test_prospect_list_response_dto() -> None:
    """Test list response with total count."""
    prospect_id = uuid4()
    entity_id = uuid4()
    now = datetime(2026, 2, 1, 12, 0, 0)

    response_dto = ProspectResponseDTO(
        id=prospect_id,
        entity_id=entity_id,
        company_name="List Corp",
        contact_name=None,
        contact_email=None,
        contact_phone=None,
        stage="lead",
        estimated_value=None,
        source=None,
        notes=None,
        is_active=True,
        created_at=now,
        updated_at=None,
    )

    list_dto = ProspectListResponseDTO(
        prospects=[response_dto],
        total=1,
    )
    assert len(list_dto.prospects) == 1
    assert list_dto.total == 1
    assert list_dto.prospects[0].company_name == "List Corp"
    print("INFO [TestProspect]: test_prospect_list_response_dto - PASSED")


# ============================================================================
# Prospect Model Tests
# ============================================================================


def test_prospect_model_repr() -> None:
    """Test Prospect model __repr__ method."""
    prospect = Prospect()
    prospect.id = uuid4()
    prospect.company_name = "Repr Corp"
    prospect.stage = "lead"

    repr_str = repr(prospect)
    assert "Repr Corp" in repr_str
    assert "lead" in repr_str
    assert "Prospect" in repr_str
    print("INFO [TestProspect]: test_prospect_model_repr - PASSED")


def test_prospect_model_tablename() -> None:
    """Test Prospect model has correct table name."""
    assert Prospect.__tablename__ == "prospects"
    print("INFO [TestProspect]: test_prospect_model_tablename - PASSED")
