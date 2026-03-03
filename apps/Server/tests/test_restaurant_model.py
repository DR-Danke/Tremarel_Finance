"""Tests for Restaurant model and DTOs."""

from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.interface.restaurant_dto import (
    RestaurantCreateDTO,
    RestaurantListDTO,
    RestaurantResponseDTO,
    RestaurantUpdateDTO,
)
from src.models.restaurant import Restaurant


# ============================================================================
# RestaurantCreateDTO Tests
# ============================================================================


def test_restaurant_create_dto_name_only() -> None:
    """Test valid creation DTO with name only."""
    dto = RestaurantCreateDTO(name="My Restaurant")
    assert dto.name == "My Restaurant"
    assert dto.address is None
    print("INFO [TestRestaurant]: test_restaurant_create_dto_name_only - PASSED")


def test_restaurant_create_dto_name_and_address() -> None:
    """Test valid creation DTO with name and address."""
    dto = RestaurantCreateDTO(
        name="My Restaurant",
        address="123 Main St, City, State 12345",
    )
    assert dto.name == "My Restaurant"
    assert dto.address == "123 Main St, City, State 12345"
    print("INFO [TestRestaurant]: test_restaurant_create_dto_name_and_address - PASSED")


def test_restaurant_create_dto_empty_name() -> None:
    """Test that empty name is rejected (min_length=1)."""
    with pytest.raises(ValidationError) as exc_info:
        RestaurantCreateDTO(name="")
    assert "name" in str(exc_info.value)
    print("INFO [TestRestaurant]: test_restaurant_create_dto_empty_name - PASSED")


def test_restaurant_create_dto_name_too_long() -> None:
    """Test that name exceeding 255 chars is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        RestaurantCreateDTO(name="A" * 256)
    assert "name" in str(exc_info.value)
    print("INFO [TestRestaurant]: test_restaurant_create_dto_name_too_long - PASSED")


def test_restaurant_create_dto_missing_name() -> None:
    """Test that missing name is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        RestaurantCreateDTO()
    assert "name" in str(exc_info.value)
    print("INFO [TestRestaurant]: test_restaurant_create_dto_missing_name - PASSED")


def test_restaurant_create_dto_max_length_name() -> None:
    """Test that name at exactly 255 chars is accepted."""
    dto = RestaurantCreateDTO(name="A" * 255)
    assert len(dto.name) == 255
    print("INFO [TestRestaurant]: test_restaurant_create_dto_max_length_name - PASSED")


# ============================================================================
# RestaurantUpdateDTO Tests
# ============================================================================


def test_restaurant_update_dto_name_only() -> None:
    """Test partial update with name only."""
    dto = RestaurantUpdateDTO(name="Updated Name")
    assert dto.name == "Updated Name"
    assert dto.address is None
    print("INFO [TestRestaurant]: test_restaurant_update_dto_name_only - PASSED")


def test_restaurant_update_dto_address_only() -> None:
    """Test partial update with address only."""
    dto = RestaurantUpdateDTO(address="456 Oak Ave")
    assert dto.name is None
    assert dto.address == "456 Oak Ave"
    print("INFO [TestRestaurant]: test_restaurant_update_dto_address_only - PASSED")


def test_restaurant_update_dto_both() -> None:
    """Test update with both fields."""
    dto = RestaurantUpdateDTO(name="New Name", address="New Address")
    assert dto.name == "New Name"
    assert dto.address == "New Address"
    print("INFO [TestRestaurant]: test_restaurant_update_dto_both - PASSED")


def test_restaurant_update_dto_empty() -> None:
    """Test update DTO with no fields set (all optional)."""
    dto = RestaurantUpdateDTO()
    assert dto.name is None
    assert dto.address is None
    print("INFO [TestRestaurant]: test_restaurant_update_dto_empty - PASSED")


# ============================================================================
# RestaurantResponseDTO Tests
# ============================================================================


def test_restaurant_response_dto_from_attributes() -> None:
    """Test response DTO from mock model object."""
    mock_restaurant = MagicMock(spec=Restaurant)
    mock_restaurant.id = uuid4()
    mock_restaurant.name = "Test Restaurant"
    mock_restaurant.address = "123 Main St"
    mock_restaurant.owner_id = uuid4()
    mock_restaurant.created_at = datetime(2026, 1, 15, 10, 30, 0)
    mock_restaurant.updated_at = None

    dto = RestaurantResponseDTO.model_validate(mock_restaurant, from_attributes=True)
    assert dto.id == mock_restaurant.id
    assert dto.name == "Test Restaurant"
    assert dto.address == "123 Main St"
    assert dto.owner_id == mock_restaurant.owner_id
    assert dto.updated_at is None
    print("INFO [TestRestaurant]: test_restaurant_response_dto_from_attributes - PASSED")


def test_restaurant_response_dto_no_address() -> None:
    """Test response DTO with no address."""
    mock_restaurant = MagicMock(spec=Restaurant)
    mock_restaurant.id = uuid4()
    mock_restaurant.name = "No Address Restaurant"
    mock_restaurant.address = None
    mock_restaurant.owner_id = uuid4()
    mock_restaurant.created_at = datetime(2026, 2, 1, 12, 0, 0)
    mock_restaurant.updated_at = None

    dto = RestaurantResponseDTO.model_validate(mock_restaurant, from_attributes=True)
    assert dto.address is None
    print("INFO [TestRestaurant]: test_restaurant_response_dto_no_address - PASSED")


# ============================================================================
# RestaurantListDTO Tests
# ============================================================================


def test_restaurant_list_dto() -> None:
    """Test list DTO with multiple restaurants."""
    now = datetime(2026, 2, 1, 12, 0, 0)
    r1 = RestaurantResponseDTO(
        id=uuid4(),
        name="Restaurant A",
        address="Address A",
        owner_id=uuid4(),
        created_at=now,
        updated_at=None,
    )
    r2 = RestaurantResponseDTO(
        id=uuid4(),
        name="Restaurant B",
        address=None,
        owner_id=uuid4(),
        created_at=now,
        updated_at=None,
    )
    list_dto = RestaurantListDTO(restaurants=[r1, r2])
    assert len(list_dto.restaurants) == 2
    assert list_dto.restaurants[0].name == "Restaurant A"
    assert list_dto.restaurants[1].name == "Restaurant B"
    print("INFO [TestRestaurant]: test_restaurant_list_dto - PASSED")


def test_restaurant_list_dto_empty() -> None:
    """Test list DTO with empty list."""
    list_dto = RestaurantListDTO(restaurants=[])
    assert len(list_dto.restaurants) == 0
    print("INFO [TestRestaurant]: test_restaurant_list_dto_empty - PASSED")


# ============================================================================
# Restaurant Model Tests
# ============================================================================


def test_restaurant_model_repr() -> None:
    """Test Restaurant model __repr__ method."""
    restaurant = Restaurant()
    restaurant.id = uuid4()
    restaurant.name = "Repr Restaurant"
    restaurant.owner_id = uuid4()

    repr_str = repr(restaurant)
    assert "Repr Restaurant" in repr_str
    assert "Restaurant" in repr_str
    print("INFO [TestRestaurant]: test_restaurant_model_repr - PASSED")


def test_restaurant_model_tablename() -> None:
    """Test Restaurant model has correct table name."""
    assert Restaurant.__tablename__ == "restaurant"
    print("INFO [TestRestaurant]: test_restaurant_model_tablename - PASSED")
