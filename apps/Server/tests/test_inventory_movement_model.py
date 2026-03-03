"""Tests for InventoryMovement model and DTOs."""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.interface.inventory_movement_dto import (
    InventoryMovementCreateDTO,
    InventoryMovementResponseDTO,
    MovementReason,
    MovementType,
)
from src.models.inventory_movement import InventoryMovement


# ============================================================================
# MovementType Enum Tests
# ============================================================================


def test_movement_type_values() -> None:
    """Test MovementType enum has exactly two values."""
    assert MovementType.ENTRY == "entry"
    assert MovementType.EXIT == "exit"
    assert len(MovementType) == 2
    print("INFO [TestInventoryMovement]: test_movement_type_values - PASSED")


# ============================================================================
# MovementReason Enum Tests
# ============================================================================


def test_movement_reason_values() -> None:
    """Test MovementReason enum has exactly six values."""
    assert MovementReason.COMPRA == "compra"
    assert MovementReason.USO == "uso"
    assert MovementReason.PRODUCCION == "produccion"
    assert MovementReason.MERMA == "merma"
    assert MovementReason.RECETA == "receta"
    assert MovementReason.AJUSTE == "ajuste"
    assert len(MovementReason) == 6
    print("INFO [TestInventoryMovement]: test_movement_reason_values - PASSED")


# ============================================================================
# InventoryMovementCreateDTO Tests
# ============================================================================


def test_create_dto_all_fields() -> None:
    """Test valid creation DTO with all fields."""
    resource_id = uuid4()
    restaurant_id = uuid4()
    person_id = uuid4()
    now = datetime(2026, 3, 1, 12, 0, 0)

    dto = InventoryMovementCreateDTO(
        resource_id=resource_id,
        type=MovementType.ENTRY,
        quantity=Decimal("10.5"),
        reason=MovementReason.COMPRA,
        date=now,
        person_id=person_id,
        restaurant_id=restaurant_id,
        notes="Bulk purchase",
    )
    assert dto.resource_id == resource_id
    assert dto.type == MovementType.ENTRY
    assert dto.quantity == Decimal("10.5")
    assert dto.reason == MovementReason.COMPRA
    assert dto.date == now
    assert dto.person_id == person_id
    assert dto.restaurant_id == restaurant_id
    assert dto.notes == "Bulk purchase"
    print("INFO [TestInventoryMovement]: test_create_dto_all_fields - PASSED")


def test_create_dto_required_only() -> None:
    """Test valid creation DTO with required fields only."""
    dto = InventoryMovementCreateDTO(
        resource_id=uuid4(),
        type=MovementType.EXIT,
        quantity=Decimal("5.0"),
        reason=MovementReason.USO,
        restaurant_id=uuid4(),
    )
    assert dto.date is None
    assert dto.person_id is None
    assert dto.notes is None
    print("INFO [TestInventoryMovement]: test_create_dto_required_only - PASSED")


def test_create_dto_quantity_zero_rejected() -> None:
    """Test that quantity of 0 is rejected (gt=0)."""
    with pytest.raises(ValidationError) as exc_info:
        InventoryMovementCreateDTO(
            resource_id=uuid4(),
            type=MovementType.ENTRY,
            quantity=Decimal("0"),
            reason=MovementReason.COMPRA,
            restaurant_id=uuid4(),
        )
    assert "quantity" in str(exc_info.value)
    print("INFO [TestInventoryMovement]: test_create_dto_quantity_zero_rejected - PASSED")


def test_create_dto_quantity_negative_rejected() -> None:
    """Test that negative quantity is rejected (gt=0)."""
    with pytest.raises(ValidationError) as exc_info:
        InventoryMovementCreateDTO(
            resource_id=uuid4(),
            type=MovementType.ENTRY,
            quantity=Decimal("-5"),
            reason=MovementReason.COMPRA,
            restaurant_id=uuid4(),
        )
    assert "quantity" in str(exc_info.value)
    print("INFO [TestInventoryMovement]: test_create_dto_quantity_negative_rejected - PASSED")


def test_create_dto_invalid_type_rejected() -> None:
    """Test that invalid movement type is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        InventoryMovementCreateDTO(
            resource_id=uuid4(),
            type="invalid",
            quantity=Decimal("5"),
            reason=MovementReason.COMPRA,
            restaurant_id=uuid4(),
        )
    assert "type" in str(exc_info.value)
    print("INFO [TestInventoryMovement]: test_create_dto_invalid_type_rejected - PASSED")


def test_create_dto_invalid_reason_rejected() -> None:
    """Test that invalid movement reason is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        InventoryMovementCreateDTO(
            resource_id=uuid4(),
            type=MovementType.ENTRY,
            quantity=Decimal("5"),
            reason="invalid_reason",
            restaurant_id=uuid4(),
        )
    assert "reason" in str(exc_info.value)
    print("INFO [TestInventoryMovement]: test_create_dto_invalid_reason_rejected - PASSED")


def test_create_dto_missing_required_fields() -> None:
    """Test that missing required fields are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        InventoryMovementCreateDTO()
    errors = str(exc_info.value)
    assert "resource_id" in errors
    assert "type" in errors
    assert "quantity" in errors
    assert "reason" in errors
    assert "restaurant_id" in errors
    print("INFO [TestInventoryMovement]: test_create_dto_missing_required_fields - PASSED")


# ============================================================================
# InventoryMovementResponseDTO Tests
# ============================================================================


def test_response_dto_from_dict() -> None:
    """Test response DTO from dictionary."""
    movement_id = uuid4()
    resource_id = uuid4()
    restaurant_id = uuid4()
    now = datetime(2026, 3, 1, 12, 0, 0)

    dto = InventoryMovementResponseDTO(
        id=movement_id,
        resource_id=resource_id,
        type="entry",
        quantity=Decimal("10.5"),
        reason="compra",
        date=now,
        person_id=None,
        restaurant_id=restaurant_id,
        notes=None,
        created_at=now,
    )
    assert dto.id == movement_id
    assert dto.resource_id == resource_id
    assert dto.type == "entry"
    assert dto.quantity == Decimal("10.5")
    assert dto.reason == "compra"
    assert dto.date == now
    assert dto.person_id is None
    assert dto.restaurant_id == restaurant_id
    assert dto.notes is None
    assert dto.created_at == now
    print("INFO [TestInventoryMovement]: test_response_dto_from_dict - PASSED")


# ============================================================================
# InventoryMovement Model Tests
# ============================================================================


def test_inventory_movement_model_repr() -> None:
    """Test InventoryMovement model __repr__ method."""
    movement = InventoryMovement()
    movement.id = uuid4()
    movement.resource_id = uuid4()
    movement.type = "entry"
    movement.quantity = Decimal("10.0")

    repr_str = repr(movement)
    assert "InventoryMovement" in repr_str
    assert "entry" in repr_str
    print("INFO [TestInventoryMovement]: test_inventory_movement_model_repr - PASSED")


def test_inventory_movement_model_tablename() -> None:
    """Test InventoryMovement model has correct table name."""
    assert InventoryMovement.__tablename__ == "inventory_movement"
    print("INFO [TestInventoryMovement]: test_inventory_movement_model_tablename - PASSED")


def test_inventory_movement_model_instantiation() -> None:
    """Test InventoryMovement model can be instantiated with all fields."""
    movement = InventoryMovement()
    movement.id = uuid4()
    movement.resource_id = uuid4()
    movement.type = "exit"
    movement.quantity = Decimal("3.5")
    movement.reason = "uso"
    movement.person_id = uuid4()
    movement.restaurant_id = uuid4()
    movement.notes = "Used in recipe"

    assert movement.type == "exit"
    assert movement.quantity == Decimal("3.5")
    assert movement.reason == "uso"
    assert movement.notes == "Used in recipe"
    print("INFO [TestInventoryMovement]: test_inventory_movement_model_instantiation - PASSED")


def test_inventory_movement_model_nullable_fields() -> None:
    """Test InventoryMovement model nullable fields accept None."""
    movement = InventoryMovement()
    movement.id = uuid4()
    movement.resource_id = uuid4()
    movement.type = "entry"
    movement.quantity = Decimal("5.0")
    movement.reason = "compra"
    movement.restaurant_id = uuid4()
    movement.person_id = None
    movement.notes = None

    assert movement.person_id is None
    assert movement.notes is None
    print("INFO [TestInventoryMovement]: test_inventory_movement_model_nullable_fields - PASSED")
