"""Tests for Recipe model and DTOs."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.interface.recipe_dto import (
    RecipeCreateDTO,
    RecipeItemCreateDTO,
    RecipeItemResponseDTO,
    RecipeResponseDTO,
    RecipeUpdateDTO,
)
from src.models.recipe import Recipe, RecipeItem


# ============================================================================
# RecipeItemCreateDTO Tests
# ============================================================================


def test_recipe_item_create_dto_valid() -> None:
    """Test valid recipe item creation DTO."""
    dto = RecipeItemCreateDTO(
        resource_id=uuid4(),
        quantity=Decimal("2.5"),
        unit="kg",
    )
    assert dto.quantity == Decimal("2.5")
    assert dto.unit == "kg"
    print("INFO [TestRecipe]: test_recipe_item_create_dto_valid - PASSED")


def test_recipe_item_create_dto_quantity_zero_rejected() -> None:
    """Test that quantity = 0 is rejected (gt=0)."""
    with pytest.raises(ValidationError) as exc_info:
        RecipeItemCreateDTO(
            resource_id=uuid4(),
            quantity=Decimal("0"),
            unit="kg",
        )
    assert "quantity" in str(exc_info.value)
    print("INFO [TestRecipe]: test_recipe_item_create_dto_quantity_zero_rejected - PASSED")


def test_recipe_item_create_dto_negative_quantity_rejected() -> None:
    """Test that negative quantity is rejected (gt=0)."""
    with pytest.raises(ValidationError) as exc_info:
        RecipeItemCreateDTO(
            resource_id=uuid4(),
            quantity=Decimal("-1"),
            unit="kg",
        )
    assert "quantity" in str(exc_info.value)
    print("INFO [TestRecipe]: test_recipe_item_create_dto_negative_quantity_rejected - PASSED")


def test_recipe_item_create_dto_missing_fields() -> None:
    """Test that missing required fields are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        RecipeItemCreateDTO()
    errors = str(exc_info.value)
    assert "resource_id" in errors
    assert "quantity" in errors
    assert "unit" in errors
    print("INFO [TestRecipe]: test_recipe_item_create_dto_missing_fields - PASSED")


def test_recipe_item_create_dto_empty_unit_rejected() -> None:
    """Test that empty unit is rejected (min_length=1)."""
    with pytest.raises(ValidationError) as exc_info:
        RecipeItemCreateDTO(
            resource_id=uuid4(),
            quantity=Decimal("1"),
            unit="",
        )
    assert "unit" in str(exc_info.value)
    print("INFO [TestRecipe]: test_recipe_item_create_dto_empty_unit_rejected - PASSED")


# ============================================================================
# RecipeCreateDTO Tests
# ============================================================================


def test_recipe_create_dto_all_fields() -> None:
    """Test valid creation DTO with all fields."""
    restaurant_id = uuid4()
    resource_id = uuid4()
    dto = RecipeCreateDTO(
        restaurant_id=restaurant_id,
        name="Pasta Carbonara",
        sale_price=Decimal("25.00"),
        is_active=True,
        items=[
            RecipeItemCreateDTO(resource_id=resource_id, quantity=Decimal("0.5"), unit="kg"),
        ],
    )
    assert dto.name == "Pasta Carbonara"
    assert dto.sale_price == Decimal("25.00")
    assert dto.is_active is True
    assert len(dto.items) == 1
    assert dto.restaurant_id == restaurant_id
    print("INFO [TestRecipe]: test_recipe_create_dto_all_fields - PASSED")


def test_recipe_create_dto_required_only() -> None:
    """Test valid creation DTO with required fields only (is_active defaults)."""
    dto = RecipeCreateDTO(
        restaurant_id=uuid4(),
        name="Pizza",
        sale_price=Decimal("15.00"),
        items=[
            RecipeItemCreateDTO(resource_id=uuid4(), quantity=Decimal("1"), unit="unidad"),
        ],
    )
    assert dto.is_active is True  # Default
    print("INFO [TestRecipe]: test_recipe_create_dto_required_only - PASSED")


def test_recipe_create_dto_name_too_long() -> None:
    """Test that name exceeding 255 chars is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        RecipeCreateDTO(
            restaurant_id=uuid4(),
            name="A" * 256,
            sale_price=Decimal("10.00"),
            items=[
                RecipeItemCreateDTO(resource_id=uuid4(), quantity=Decimal("1"), unit="kg"),
            ],
        )
    assert "name" in str(exc_info.value)
    print("INFO [TestRecipe]: test_recipe_create_dto_name_too_long - PASSED")


def test_recipe_create_dto_empty_name_rejected() -> None:
    """Test that empty name is rejected (min_length=1)."""
    with pytest.raises(ValidationError) as exc_info:
        RecipeCreateDTO(
            restaurant_id=uuid4(),
            name="",
            sale_price=Decimal("10.00"),
            items=[
                RecipeItemCreateDTO(resource_id=uuid4(), quantity=Decimal("1"), unit="kg"),
            ],
        )
    assert "name" in str(exc_info.value)
    print("INFO [TestRecipe]: test_recipe_create_dto_empty_name_rejected - PASSED")


def test_recipe_create_dto_sale_price_zero_rejected() -> None:
    """Test that sale_price = 0 is rejected (gt=0)."""
    with pytest.raises(ValidationError) as exc_info:
        RecipeCreateDTO(
            restaurant_id=uuid4(),
            name="Test",
            sale_price=Decimal("0"),
            items=[
                RecipeItemCreateDTO(resource_id=uuid4(), quantity=Decimal("1"), unit="kg"),
            ],
        )
    assert "sale_price" in str(exc_info.value)
    print("INFO [TestRecipe]: test_recipe_create_dto_sale_price_zero_rejected - PASSED")


def test_recipe_create_dto_negative_sale_price_rejected() -> None:
    """Test that negative sale_price is rejected (gt=0)."""
    with pytest.raises(ValidationError) as exc_info:
        RecipeCreateDTO(
            restaurant_id=uuid4(),
            name="Test",
            sale_price=Decimal("-5"),
            items=[
                RecipeItemCreateDTO(resource_id=uuid4(), quantity=Decimal("1"), unit="kg"),
            ],
        )
    assert "sale_price" in str(exc_info.value)
    print("INFO [TestRecipe]: test_recipe_create_dto_negative_sale_price_rejected - PASSED")


def test_recipe_create_dto_empty_items_rejected() -> None:
    """Test that empty items list is rejected (min_length=1)."""
    with pytest.raises(ValidationError) as exc_info:
        RecipeCreateDTO(
            restaurant_id=uuid4(),
            name="Test",
            sale_price=Decimal("10.00"),
            items=[],
        )
    assert "items" in str(exc_info.value)
    print("INFO [TestRecipe]: test_recipe_create_dto_empty_items_rejected - PASSED")


def test_recipe_create_dto_missing_items_rejected() -> None:
    """Test that missing items field is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        RecipeCreateDTO(
            restaurant_id=uuid4(),
            name="Test",
            sale_price=Decimal("10.00"),
        )
    assert "items" in str(exc_info.value)
    print("INFO [TestRecipe]: test_recipe_create_dto_missing_items_rejected - PASSED")


def test_recipe_create_dto_multiple_items() -> None:
    """Test recipe with multiple items."""
    dto = RecipeCreateDTO(
        restaurant_id=uuid4(),
        name="Salad",
        sale_price=Decimal("12.00"),
        items=[
            RecipeItemCreateDTO(resource_id=uuid4(), quantity=Decimal("0.3"), unit="kg"),
            RecipeItemCreateDTO(resource_id=uuid4(), quantity=Decimal("0.1"), unit="litros"),
            RecipeItemCreateDTO(resource_id=uuid4(), quantity=Decimal("2"), unit="unidad"),
        ],
    )
    assert len(dto.items) == 3
    print("INFO [TestRecipe]: test_recipe_create_dto_multiple_items - PASSED")


# ============================================================================
# RecipeUpdateDTO Tests
# ============================================================================


def test_recipe_update_dto_partial() -> None:
    """Test partial update with a single field."""
    dto = RecipeUpdateDTO(name="Updated Name")
    assert dto.name == "Updated Name"
    assert dto.sale_price is None
    assert dto.is_active is None
    assert dto.items is None
    print("INFO [TestRecipe]: test_recipe_update_dto_partial - PASSED")


def test_recipe_update_dto_all_none() -> None:
    """Test update DTO with no fields set (all optional)."""
    dto = RecipeUpdateDTO()
    assert dto.name is None
    assert dto.sale_price is None
    assert dto.is_active is None
    assert dto.items is None
    print("INFO [TestRecipe]: test_recipe_update_dto_all_none - PASSED")


def test_recipe_update_dto_with_items() -> None:
    """Test update DTO with replacement items."""
    dto = RecipeUpdateDTO(
        items=[
            RecipeItemCreateDTO(resource_id=uuid4(), quantity=Decimal("1"), unit="kg"),
        ],
    )
    assert dto.items is not None
    assert len(dto.items) == 1
    print("INFO [TestRecipe]: test_recipe_update_dto_with_items - PASSED")


def test_recipe_update_dto_sale_price_zero_rejected() -> None:
    """Test that sale_price = 0 is rejected in update."""
    with pytest.raises(ValidationError) as exc_info:
        RecipeUpdateDTO(sale_price=Decimal("0"))
    assert "sale_price" in str(exc_info.value)
    print("INFO [TestRecipe]: test_recipe_update_dto_sale_price_zero_rejected - PASSED")


# ============================================================================
# RecipeResponseDTO Tests
# ============================================================================


def test_recipe_response_dto_from_dict() -> None:
    """Test response DTO construction from dict values."""
    recipe_id = uuid4()
    restaurant_id = uuid4()
    item_id = uuid4()
    resource_id = uuid4()
    now = datetime(2026, 1, 15, 10, 30, 0)

    dto = RecipeResponseDTO(
        id=recipe_id,
        restaurant_id=restaurant_id,
        name="Test Recipe",
        sale_price=Decimal("25.00"),
        current_cost=Decimal("8.00"),
        margin_percent=Decimal("68.00"),
        is_profitable=True,
        is_active=True,
        items=[
            RecipeItemResponseDTO(
                id=item_id,
                resource_id=resource_id,
                quantity=Decimal("2.0"),
                unit="kg",
                created_at=now,
            )
        ],
        created_at=now,
        updated_at=None,
    )
    assert dto.id == recipe_id
    assert dto.restaurant_id == restaurant_id
    assert dto.name == "Test Recipe"
    assert dto.sale_price == Decimal("25.00")
    assert dto.current_cost == Decimal("8.00")
    assert dto.margin_percent == Decimal("68.00")
    assert dto.is_profitable is True
    assert dto.is_active is True
    assert len(dto.items) == 1
    assert dto.items[0].resource_id == resource_id
    assert dto.updated_at is None
    print("INFO [TestRecipe]: test_recipe_response_dto_from_dict - PASSED")


def test_recipe_response_dto_empty_items() -> None:
    """Test response DTO with empty items list."""
    dto = RecipeResponseDTO(
        id=uuid4(),
        restaurant_id=uuid4(),
        name="Empty Recipe",
        sale_price=Decimal("10.00"),
        current_cost=Decimal("0"),
        margin_percent=Decimal("100.00"),
        is_profitable=True,
        is_active=True,
        items=[],
        created_at=datetime(2026, 1, 15, 10, 30, 0),
        updated_at=None,
    )
    assert len(dto.items) == 0
    print("INFO [TestRecipe]: test_recipe_response_dto_empty_items - PASSED")


# ============================================================================
# RecipeItemResponseDTO Tests
# ============================================================================


def test_recipe_item_response_dto_from_attributes() -> None:
    """Test recipe item response DTO from mock model."""
    mock_item = MagicMock(spec=RecipeItem)
    mock_item.id = uuid4()
    mock_item.resource_id = uuid4()
    mock_item.quantity = Decimal("1.5")
    mock_item.unit = "kg"
    mock_item.created_at = datetime(2026, 1, 15, 10, 30, 0)

    dto = RecipeItemResponseDTO.model_validate(mock_item, from_attributes=True)
    assert dto.id == mock_item.id
    assert dto.resource_id == mock_item.resource_id
    assert dto.quantity == Decimal("1.5")
    assert dto.unit == "kg"
    print("INFO [TestRecipe]: test_recipe_item_response_dto_from_attributes - PASSED")


# ============================================================================
# Recipe Model Tests
# ============================================================================


def test_recipe_model_repr() -> None:
    """Test Recipe model __repr__ method."""
    recipe = Recipe()
    recipe.id = uuid4()
    recipe.name = "Test Recipe"
    recipe.sale_price = Decimal("25.00")
    recipe.restaurant_id = uuid4()

    repr_str = repr(recipe)
    assert "Test Recipe" in repr_str
    assert "Recipe" in repr_str
    print("INFO [TestRecipe]: test_recipe_model_repr - PASSED")


def test_recipe_model_tablename() -> None:
    """Test Recipe model has correct table name."""
    assert Recipe.__tablename__ == "recipe"
    print("INFO [TestRecipe]: test_recipe_model_tablename - PASSED")


def test_recipe_model_defaults() -> None:
    """Test Recipe model default values."""
    recipe = Recipe()
    assert recipe.is_active is None or recipe.is_active is True
    assert recipe.is_profitable is None or recipe.is_profitable is True
    print("INFO [TestRecipe]: test_recipe_model_defaults - PASSED")


# ============================================================================
# RecipeItem Model Tests
# ============================================================================


def test_recipe_item_model_repr() -> None:
    """Test RecipeItem model __repr__ method."""
    item = RecipeItem()
    item.id = uuid4()
    item.recipe_id = uuid4()
    item.resource_id = uuid4()
    item.quantity = Decimal("2.0")

    repr_str = repr(item)
    assert "RecipeItem" in repr_str
    print("INFO [TestRecipe]: test_recipe_item_model_repr - PASSED")


def test_recipe_item_model_tablename() -> None:
    """Test RecipeItem model has correct table name."""
    assert RecipeItem.__tablename__ == "recipe_item"
    print("INFO [TestRecipe]: test_recipe_item_model_tablename - PASSED")
