"""Tests for Person model and DTOs."""

from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.interface.person_dto import (
    PersonCreateDTO,
    PersonResponseDTO,
    PersonType,
    PersonUpdateDTO,
)
from src.models.person import Person


# ============================================================================
# PersonCreateDTO Tests
# ============================================================================


def test_person_create_dto_all_fields() -> None:
    """Test valid creation DTO with all fields."""
    restaurant_id = uuid4()
    dto = PersonCreateDTO(
        restaurant_id=restaurant_id,
        name="Juan Pérez",
        role="chef",
        email="juan@restaurant.com",
        whatsapp="+52 555 123 4567",
        type=PersonType.EMPLOYEE,
    )
    assert dto.name == "Juan Pérez"
    assert dto.role == "chef"
    assert dto.email == "juan@restaurant.com"
    assert dto.whatsapp == "+52 555 123 4567"
    assert dto.type == PersonType.EMPLOYEE
    assert dto.restaurant_id == restaurant_id
    print("INFO [TestPerson]: test_person_create_dto_all_fields - PASSED")


def test_person_create_dto_required_only() -> None:
    """Test valid creation DTO with required fields only."""
    restaurant_id = uuid4()
    dto = PersonCreateDTO(
        restaurant_id=restaurant_id,
        name="María García",
        role="mesero",
    )
    assert dto.name == "María García"
    assert dto.role == "mesero"
    assert dto.email is None
    assert dto.whatsapp is None
    assert dto.type == PersonType.EMPLOYEE  # Default
    print("INFO [TestPerson]: test_person_create_dto_required_only - PASSED")


def test_person_create_dto_empty_name() -> None:
    """Test that empty name is rejected (min_length=1)."""
    with pytest.raises(ValidationError) as exc_info:
        PersonCreateDTO(
            restaurant_id=uuid4(),
            name="",
            role="chef",
        )
    assert "name" in str(exc_info.value)
    print("INFO [TestPerson]: test_person_create_dto_empty_name - PASSED")


def test_person_create_dto_name_too_long() -> None:
    """Test that name exceeding 255 chars is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        PersonCreateDTO(
            restaurant_id=uuid4(),
            name="A" * 256,
            role="chef",
        )
    assert "name" in str(exc_info.value)
    print("INFO [TestPerson]: test_person_create_dto_name_too_long - PASSED")


def test_person_create_dto_max_length_name() -> None:
    """Test that name at exactly 255 chars is accepted."""
    dto = PersonCreateDTO(
        restaurant_id=uuid4(),
        name="A" * 255,
        role="chef",
    )
    assert len(dto.name) == 255
    print("INFO [TestPerson]: test_person_create_dto_max_length_name - PASSED")


def test_person_create_dto_empty_role() -> None:
    """Test that empty role is rejected (min_length=1)."""
    with pytest.raises(ValidationError) as exc_info:
        PersonCreateDTO(
            restaurant_id=uuid4(),
            name="Test Person",
            role="",
        )
    assert "role" in str(exc_info.value)
    print("INFO [TestPerson]: test_person_create_dto_empty_role - PASSED")


def test_person_create_dto_role_too_long() -> None:
    """Test that role exceeding 100 chars is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        PersonCreateDTO(
            restaurant_id=uuid4(),
            name="Test Person",
            role="R" * 101,
        )
    assert "role" in str(exc_info.value)
    print("INFO [TestPerson]: test_person_create_dto_role_too_long - PASSED")


def test_person_create_dto_missing_required_fields() -> None:
    """Test that missing required fields are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        PersonCreateDTO()
    errors = str(exc_info.value)
    assert "restaurant_id" in errors
    assert "name" in errors
    assert "role" in errors
    print("INFO [TestPerson]: test_person_create_dto_missing_required_fields - PASSED")


def test_person_create_dto_default_type() -> None:
    """Test that default type is EMPLOYEE."""
    dto = PersonCreateDTO(
        restaurant_id=uuid4(),
        name="Test",
        role="test",
    )
    assert dto.type == PersonType.EMPLOYEE
    print("INFO [TestPerson]: test_person_create_dto_default_type - PASSED")


def test_person_create_dto_supplier_type() -> None:
    """Test supplier type is accepted."""
    dto = PersonCreateDTO(
        restaurant_id=uuid4(),
        name="Supplier Name",
        role="proveedor",
        type=PersonType.SUPPLIER,
    )
    assert dto.type == PersonType.SUPPLIER
    print("INFO [TestPerson]: test_person_create_dto_supplier_type - PASSED")


def test_person_create_dto_owner_type() -> None:
    """Test owner type is accepted."""
    dto = PersonCreateDTO(
        restaurant_id=uuid4(),
        name="Owner Name",
        role="dueño",
        type=PersonType.OWNER,
    )
    assert dto.type == PersonType.OWNER
    print("INFO [TestPerson]: test_person_create_dto_owner_type - PASSED")


def test_person_create_dto_invalid_type() -> None:
    """Test that invalid type is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        PersonCreateDTO(
            restaurant_id=uuid4(),
            name="Test",
            role="test",
            type="invalid",
        )
    assert "type" in str(exc_info.value)
    print("INFO [TestPerson]: test_person_create_dto_invalid_type - PASSED")


def test_person_create_dto_invalid_email() -> None:
    """Test that invalid email format is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        PersonCreateDTO(
            restaurant_id=uuid4(),
            name="Test",
            role="test",
            email="not-an-email",
        )
    assert "email" in str(exc_info.value)
    print("INFO [TestPerson]: test_person_create_dto_invalid_email - PASSED")


def test_person_create_dto_whatsapp_too_long() -> None:
    """Test that whatsapp exceeding 50 chars is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        PersonCreateDTO(
            restaurant_id=uuid4(),
            name="Test",
            role="test",
            whatsapp="+" + "1" * 50,
        )
    assert "whatsapp" in str(exc_info.value)
    print("INFO [TestPerson]: test_person_create_dto_whatsapp_too_long - PASSED")


# ============================================================================
# PersonUpdateDTO Tests
# ============================================================================


def test_person_update_dto_single_field() -> None:
    """Test partial update with a single field."""
    dto = PersonUpdateDTO(name="Updated Name")
    assert dto.name == "Updated Name"
    assert dto.role is None
    assert dto.email is None
    assert dto.whatsapp is None
    assert dto.type is None
    print("INFO [TestPerson]: test_person_update_dto_single_field - PASSED")


def test_person_update_dto_empty() -> None:
    """Test update DTO with no fields set (all optional)."""
    dto = PersonUpdateDTO()
    assert dto.name is None
    assert dto.role is None
    assert dto.email is None
    assert dto.whatsapp is None
    assert dto.type is None
    print("INFO [TestPerson]: test_person_update_dto_empty - PASSED")


def test_person_update_dto_all_fields() -> None:
    """Test update with all fields."""
    dto = PersonUpdateDTO(
        name="New Name",
        role="new role",
        email="new@email.com",
        whatsapp="+1 234 567 8900",
        type=PersonType.SUPPLIER,
    )
    assert dto.name == "New Name"
    assert dto.role == "new role"
    assert dto.email == "new@email.com"
    assert dto.whatsapp == "+1 234 567 8900"
    assert dto.type == PersonType.SUPPLIER
    print("INFO [TestPerson]: test_person_update_dto_all_fields - PASSED")


# ============================================================================
# PersonResponseDTO Tests
# ============================================================================


def test_person_response_dto_from_attributes() -> None:
    """Test response DTO from mock model object."""
    mock_person = MagicMock(spec=Person)
    mock_person.id = uuid4()
    mock_person.restaurant_id = uuid4()
    mock_person.name = "Test Person"
    mock_person.role = "chef"
    mock_person.email = "test@example.com"
    mock_person.whatsapp = "+52 555 123 4567"
    mock_person.type = "employee"
    mock_person.created_at = datetime(2026, 1, 15, 10, 30, 0)
    mock_person.updated_at = None

    dto = PersonResponseDTO.model_validate(mock_person, from_attributes=True)
    assert dto.id == mock_person.id
    assert dto.restaurant_id == mock_person.restaurant_id
    assert dto.name == "Test Person"
    assert dto.role == "chef"
    assert dto.email == "test@example.com"
    assert dto.whatsapp == "+52 555 123 4567"
    assert dto.type == "employee"
    assert dto.updated_at is None
    print("INFO [TestPerson]: test_person_response_dto_from_attributes - PASSED")


def test_person_response_dto_no_optional_fields() -> None:
    """Test response DTO with no optional fields."""
    mock_person = MagicMock(spec=Person)
    mock_person.id = uuid4()
    mock_person.restaurant_id = uuid4()
    mock_person.name = "No Optionals Person"
    mock_person.role = "mesero"
    mock_person.email = None
    mock_person.whatsapp = None
    mock_person.type = "employee"
    mock_person.created_at = datetime(2026, 2, 1, 12, 0, 0)
    mock_person.updated_at = None

    dto = PersonResponseDTO.model_validate(mock_person, from_attributes=True)
    assert dto.email is None
    assert dto.whatsapp is None
    print("INFO [TestPerson]: test_person_response_dto_no_optional_fields - PASSED")


# ============================================================================
# PersonType Enum Tests
# ============================================================================


def test_person_type_values() -> None:
    """Test PersonType enum has exactly three values."""
    assert PersonType.EMPLOYEE == "employee"
    assert PersonType.SUPPLIER == "supplier"
    assert PersonType.OWNER == "owner"
    assert len(PersonType) == 3
    print("INFO [TestPerson]: test_person_type_values - PASSED")


# ============================================================================
# Person Model Tests
# ============================================================================


def test_person_model_repr() -> None:
    """Test Person model __repr__ method."""
    person = Person()
    person.id = uuid4()
    person.name = "Repr Person"
    person.type = "employee"
    person.restaurant_id = uuid4()

    repr_str = repr(person)
    assert "Repr Person" in repr_str
    assert "Person" in repr_str
    print("INFO [TestPerson]: test_person_model_repr - PASSED")


def test_person_model_tablename() -> None:
    """Test Person model has correct table name."""
    assert Person.__tablename__ == "person"
    print("INFO [TestPerson]: test_person_model_tablename - PASSED")
