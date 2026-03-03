"""Tests for Resource model and DTOs."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.interface.resource_dto import (
    ResourceCreateDTO,
    ResourceResponseDTO,
    ResourceType,
    ResourceUpdateDTO,
)
from src.models.resource import Resource


# ============================================================================
# ResourceCreateDTO Tests
# ============================================================================


def test_resource_create_dto_all_fields() -> None:
    """Test valid creation DTO with all fields."""
    restaurant_id = uuid4()
    dto = ResourceCreateDTO(
        restaurant_id=restaurant_id,
        type=ResourceType.PRODUCTO,
        name="Tomate",
        unit="kg",
        current_stock=Decimal("10.5"),
        minimum_stock=Decimal("5.0"),
        last_unit_cost=Decimal("2.50"),
    )
    assert dto.name == "Tomate"
    assert dto.unit == "kg"
    assert dto.type == ResourceType.PRODUCTO
    assert dto.current_stock == Decimal("10.5")
    assert dto.minimum_stock == Decimal("5.0")
    assert dto.last_unit_cost == Decimal("2.50")
    assert dto.restaurant_id == restaurant_id
    print("INFO [TestResource]: test_resource_create_dto_all_fields - PASSED")


def test_resource_create_dto_required_only() -> None:
    """Test valid creation DTO with required fields only."""
    restaurant_id = uuid4()
    dto = ResourceCreateDTO(
        restaurant_id=restaurant_id,
        name="Harina",
        unit="kg",
    )
    assert dto.name == "Harina"
    assert dto.unit == "kg"
    assert dto.type == ResourceType.PRODUCTO  # Default
    assert dto.current_stock == Decimal("0")  # Default
    assert dto.minimum_stock == Decimal("0")  # Default
    assert dto.last_unit_cost == Decimal("0")  # Default
    print("INFO [TestResource]: test_resource_create_dto_required_only - PASSED")


def test_resource_create_dto_empty_name() -> None:
    """Test that empty name is rejected (min_length=1)."""
    with pytest.raises(ValidationError) as exc_info:
        ResourceCreateDTO(
            restaurant_id=uuid4(),
            name="",
            unit="kg",
        )
    assert "name" in str(exc_info.value)
    print("INFO [TestResource]: test_resource_create_dto_empty_name - PASSED")


def test_resource_create_dto_name_too_long() -> None:
    """Test that name exceeding 255 chars is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        ResourceCreateDTO(
            restaurant_id=uuid4(),
            name="A" * 256,
            unit="kg",
        )
    assert "name" in str(exc_info.value)
    print("INFO [TestResource]: test_resource_create_dto_name_too_long - PASSED")


def test_resource_create_dto_max_length_name() -> None:
    """Test that name at exactly 255 chars is accepted."""
    dto = ResourceCreateDTO(
        restaurant_id=uuid4(),
        name="A" * 255,
        unit="kg",
    )
    assert len(dto.name) == 255
    print("INFO [TestResource]: test_resource_create_dto_max_length_name - PASSED")


def test_resource_create_dto_empty_unit() -> None:
    """Test that empty unit is rejected (min_length=1)."""
    with pytest.raises(ValidationError) as exc_info:
        ResourceCreateDTO(
            restaurant_id=uuid4(),
            name="Test Resource",
            unit="",
        )
    assert "unit" in str(exc_info.value)
    print("INFO [TestResource]: test_resource_create_dto_empty_unit - PASSED")


def test_resource_create_dto_unit_too_long() -> None:
    """Test that unit exceeding 50 chars is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        ResourceCreateDTO(
            restaurant_id=uuid4(),
            name="Test Resource",
            unit="U" * 51,
        )
    assert "unit" in str(exc_info.value)
    print("INFO [TestResource]: test_resource_create_dto_unit_too_long - PASSED")


def test_resource_create_dto_missing_required_fields() -> None:
    """Test that missing required fields are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        ResourceCreateDTO()
    errors = str(exc_info.value)
    assert "restaurant_id" in errors
    assert "name" in errors
    assert "unit" in errors
    print("INFO [TestResource]: test_resource_create_dto_missing_required_fields - PASSED")


def test_resource_create_dto_negative_current_stock() -> None:
    """Test that negative current_stock is rejected (ge=0)."""
    with pytest.raises(ValidationError) as exc_info:
        ResourceCreateDTO(
            restaurant_id=uuid4(),
            name="Test",
            unit="kg",
            current_stock=Decimal("-1"),
        )
    assert "current_stock" in str(exc_info.value)
    print("INFO [TestResource]: test_resource_create_dto_negative_current_stock - PASSED")


def test_resource_create_dto_negative_minimum_stock() -> None:
    """Test that negative minimum_stock is rejected (ge=0)."""
    with pytest.raises(ValidationError) as exc_info:
        ResourceCreateDTO(
            restaurant_id=uuid4(),
            name="Test",
            unit="kg",
            minimum_stock=Decimal("-0.5"),
        )
    assert "minimum_stock" in str(exc_info.value)
    print("INFO [TestResource]: test_resource_create_dto_negative_minimum_stock - PASSED")


def test_resource_create_dto_negative_last_unit_cost() -> None:
    """Test that negative last_unit_cost is rejected (ge=0)."""
    with pytest.raises(ValidationError) as exc_info:
        ResourceCreateDTO(
            restaurant_id=uuid4(),
            name="Test",
            unit="kg",
            last_unit_cost=Decimal("-10"),
        )
    assert "last_unit_cost" in str(exc_info.value)
    print("INFO [TestResource]: test_resource_create_dto_negative_last_unit_cost - PASSED")


def test_resource_create_dto_default_type() -> None:
    """Test that default type is PRODUCTO."""
    dto = ResourceCreateDTO(
        restaurant_id=uuid4(),
        name="Test",
        unit="kg",
    )
    assert dto.type == ResourceType.PRODUCTO
    print("INFO [TestResource]: test_resource_create_dto_default_type - PASSED")


def test_resource_create_dto_default_stock_values() -> None:
    """Test that default stock values are 0."""
    dto = ResourceCreateDTO(
        restaurant_id=uuid4(),
        name="Test",
        unit="kg",
    )
    assert dto.current_stock == Decimal("0")
    assert dto.minimum_stock == Decimal("0")
    assert dto.last_unit_cost == Decimal("0")
    print("INFO [TestResource]: test_resource_create_dto_default_stock_values - PASSED")


def test_resource_create_dto_activo_type() -> None:
    """Test activo type is accepted."""
    dto = ResourceCreateDTO(
        restaurant_id=uuid4(),
        name="Horno Industrial",
        unit="unidad",
        type=ResourceType.ACTIVO,
    )
    assert dto.type == ResourceType.ACTIVO
    print("INFO [TestResource]: test_resource_create_dto_activo_type - PASSED")


def test_resource_create_dto_servicio_type() -> None:
    """Test servicio type is accepted."""
    dto = ResourceCreateDTO(
        restaurant_id=uuid4(),
        name="Mantenimiento",
        unit="servicio",
        type=ResourceType.SERVICIO,
    )
    assert dto.type == ResourceType.SERVICIO
    print("INFO [TestResource]: test_resource_create_dto_servicio_type - PASSED")


def test_resource_create_dto_invalid_type() -> None:
    """Test that invalid type is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        ResourceCreateDTO(
            restaurant_id=uuid4(),
            name="Test",
            unit="kg",
            type="invalid",
        )
    assert "type" in str(exc_info.value)
    print("INFO [TestResource]: test_resource_create_dto_invalid_type - PASSED")


# ============================================================================
# ResourceUpdateDTO Tests
# ============================================================================


def test_resource_update_dto_single_field() -> None:
    """Test partial update with a single field."""
    dto = ResourceUpdateDTO(name="Updated Name")
    assert dto.name == "Updated Name"
    assert dto.unit is None
    assert dto.type is None
    assert dto.current_stock is None
    assert dto.minimum_stock is None
    assert dto.last_unit_cost is None
    print("INFO [TestResource]: test_resource_update_dto_single_field - PASSED")


def test_resource_update_dto_empty() -> None:
    """Test update DTO with no fields set (all optional)."""
    dto = ResourceUpdateDTO()
    assert dto.name is None
    assert dto.unit is None
    assert dto.type is None
    assert dto.current_stock is None
    assert dto.minimum_stock is None
    assert dto.last_unit_cost is None
    print("INFO [TestResource]: test_resource_update_dto_empty - PASSED")


def test_resource_update_dto_negative_stock() -> None:
    """Test that negative stock values are rejected in update."""
    with pytest.raises(ValidationError) as exc_info:
        ResourceUpdateDTO(current_stock=Decimal("-5"))
    assert "current_stock" in str(exc_info.value)
    print("INFO [TestResource]: test_resource_update_dto_negative_stock - PASSED")


# ============================================================================
# ResourceResponseDTO Tests
# ============================================================================


def test_resource_response_dto_from_attributes() -> None:
    """Test response DTO from mock model object."""
    mock_resource = MagicMock(spec=Resource)
    mock_resource.id = uuid4()
    mock_resource.restaurant_id = uuid4()
    mock_resource.type = "producto"
    mock_resource.name = "Tomate"
    mock_resource.unit = "kg"
    mock_resource.current_stock = Decimal("10.5")
    mock_resource.minimum_stock = Decimal("5.0")
    mock_resource.last_unit_cost = Decimal("2.50")
    mock_resource.created_at = datetime(2026, 1, 15, 10, 30, 0)
    mock_resource.updated_at = None

    dto = ResourceResponseDTO.model_validate(mock_resource, from_attributes=True)
    assert dto.id == mock_resource.id
    assert dto.restaurant_id == mock_resource.restaurant_id
    assert dto.name == "Tomate"
    assert dto.unit == "kg"
    assert dto.type == "producto"
    assert dto.current_stock == Decimal("10.5")
    assert dto.minimum_stock == Decimal("5.0")
    assert dto.last_unit_cost == Decimal("2.50")
    assert dto.updated_at is None
    print("INFO [TestResource]: test_resource_response_dto_from_attributes - PASSED")


def test_resource_response_dto_is_low_stock_true() -> None:
    """Test is_low_stock is True when current_stock < minimum_stock."""
    mock_resource = MagicMock(spec=Resource)
    mock_resource.id = uuid4()
    mock_resource.restaurant_id = uuid4()
    mock_resource.type = "producto"
    mock_resource.name = "Low Stock Item"
    mock_resource.unit = "kg"
    mock_resource.current_stock = Decimal("2.0")
    mock_resource.minimum_stock = Decimal("5.0")
    mock_resource.last_unit_cost = Decimal("1.00")
    mock_resource.created_at = datetime(2026, 1, 15, 10, 30, 0)
    mock_resource.updated_at = None

    dto = ResourceResponseDTO.model_validate(mock_resource, from_attributes=True)
    assert dto.is_low_stock is True
    print("INFO [TestResource]: test_resource_response_dto_is_low_stock_true - PASSED")


def test_resource_response_dto_is_low_stock_false() -> None:
    """Test is_low_stock is False when current_stock >= minimum_stock."""
    mock_resource = MagicMock(spec=Resource)
    mock_resource.id = uuid4()
    mock_resource.restaurant_id = uuid4()
    mock_resource.type = "producto"
    mock_resource.name = "Stocked Item"
    mock_resource.unit = "kg"
    mock_resource.current_stock = Decimal("10.0")
    mock_resource.minimum_stock = Decimal("5.0")
    mock_resource.last_unit_cost = Decimal("1.00")
    mock_resource.created_at = datetime(2026, 1, 15, 10, 30, 0)
    mock_resource.updated_at = None

    dto = ResourceResponseDTO.model_validate(mock_resource, from_attributes=True)
    assert dto.is_low_stock is False
    print("INFO [TestResource]: test_resource_response_dto_is_low_stock_false - PASSED")


def test_resource_response_dto_is_low_stock_equal() -> None:
    """Test is_low_stock is False when current_stock == minimum_stock."""
    mock_resource = MagicMock(spec=Resource)
    mock_resource.id = uuid4()
    mock_resource.restaurant_id = uuid4()
    mock_resource.type = "producto"
    mock_resource.name = "Equal Stock"
    mock_resource.unit = "kg"
    mock_resource.current_stock = Decimal("5.0")
    mock_resource.minimum_stock = Decimal("5.0")
    mock_resource.last_unit_cost = Decimal("1.00")
    mock_resource.created_at = datetime(2026, 1, 15, 10, 30, 0)
    mock_resource.updated_at = None

    dto = ResourceResponseDTO.model_validate(mock_resource, from_attributes=True)
    assert dto.is_low_stock is False
    print("INFO [TestResource]: test_resource_response_dto_is_low_stock_equal - PASSED")


def test_resource_response_dto_is_low_stock_both_zero() -> None:
    """Test is_low_stock is False when both are 0."""
    mock_resource = MagicMock(spec=Resource)
    mock_resource.id = uuid4()
    mock_resource.restaurant_id = uuid4()
    mock_resource.type = "producto"
    mock_resource.name = "Zero Stock"
    mock_resource.unit = "kg"
    mock_resource.current_stock = Decimal("0")
    mock_resource.minimum_stock = Decimal("0")
    mock_resource.last_unit_cost = Decimal("0")
    mock_resource.created_at = datetime(2026, 1, 15, 10, 30, 0)
    mock_resource.updated_at = None

    dto = ResourceResponseDTO.model_validate(mock_resource, from_attributes=True)
    assert dto.is_low_stock is False
    print("INFO [TestResource]: test_resource_response_dto_is_low_stock_both_zero - PASSED")


def test_resource_response_dto_zero_stock_positive_minimum() -> None:
    """Test is_low_stock is True when current_stock = 0 and minimum_stock > 0."""
    mock_resource = MagicMock(spec=Resource)
    mock_resource.id = uuid4()
    mock_resource.restaurant_id = uuid4()
    mock_resource.type = "producto"
    mock_resource.name = "Out of Stock"
    mock_resource.unit = "kg"
    mock_resource.current_stock = Decimal("0")
    mock_resource.minimum_stock = Decimal("10.0")
    mock_resource.last_unit_cost = Decimal("5.00")
    mock_resource.created_at = datetime(2026, 1, 15, 10, 30, 0)
    mock_resource.updated_at = None

    dto = ResourceResponseDTO.model_validate(mock_resource, from_attributes=True)
    assert dto.is_low_stock is True
    print("INFO [TestResource]: test_resource_response_dto_zero_stock_positive_minimum - PASSED")


# ============================================================================
# ResourceType Enum Tests
# ============================================================================


def test_resource_type_values() -> None:
    """Test ResourceType enum has exactly three values."""
    assert ResourceType.PRODUCTO == "producto"
    assert ResourceType.ACTIVO == "activo"
    assert ResourceType.SERVICIO == "servicio"
    assert len(ResourceType) == 3
    print("INFO [TestResource]: test_resource_type_values - PASSED")


# ============================================================================
# Resource Model Tests
# ============================================================================


def test_resource_model_repr() -> None:
    """Test Resource model __repr__ method."""
    resource = Resource()
    resource.id = uuid4()
    resource.name = "Repr Resource"
    resource.type = "producto"
    resource.restaurant_id = uuid4()

    repr_str = repr(resource)
    assert "Repr Resource" in repr_str
    assert "Resource" in repr_str
    print("INFO [TestResource]: test_resource_model_repr - PASSED")


def test_resource_model_tablename() -> None:
    """Test Resource model has correct table name."""
    assert Resource.__tablename__ == "resource"
    print("INFO [TestResource]: test_resource_model_tablename - PASSED")
