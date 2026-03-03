"""Tests for inventory movement API endpoints."""

from datetime import datetime
from decimal import Decimal
from typing import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from main import app
from src.adapter.rest.dependencies import get_db
from src.models.inventory_movement import InventoryMovement
from src.models.resource import Resource
from src.models.user import User


# Mock database session for tests
def get_mock_db() -> Generator[MagicMock, None, None]:
    """Get a mock database session for testing."""
    mock_db = MagicMock(spec=Session)
    yield mock_db


# Override the get_db dependency for all tests
app.dependency_overrides[get_db] = get_mock_db


# Pre-computed bcrypt hash for "password123"
PASSWORD_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4Y1L.VIxMfp2r2Ve"


def create_mock_user(
    email: str = "test@example.com",
    role: str = "user",
    is_active: bool = True,
    first_name: str = "Test",
    last_name: str = "User",
) -> User:
    """Create a mock user with pre-computed password hash."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.email = email
    user.password_hash = PASSWORD_HASH
    user.first_name = first_name
    user.last_name = last_name
    user.role = role
    user.is_active = is_active
    return user


def create_mock_resource(
    name: str = "Test Resource",
    unit: str = "kg",
    resource_type: str = "producto",
    current_stock: Decimal = Decimal("10.0"),
    minimum_stock: Decimal = Decimal("5.0"),
    last_unit_cost: Decimal = Decimal("2.50"),
    restaurant_id=None,
) -> Resource:
    """Create a mock resource."""
    resource = MagicMock(spec=Resource)
    resource.id = uuid4()
    resource.restaurant_id = restaurant_id or uuid4()
    resource.type = resource_type
    resource.name = name
    resource.unit = unit
    resource.current_stock = current_stock
    resource.minimum_stock = minimum_stock
    resource.last_unit_cost = last_unit_cost
    resource.created_at = MagicMock()
    resource.updated_at = None
    return resource


def create_mock_movement(
    resource_id=None,
    restaurant_id=None,
    movement_type: str = "entry",
    quantity: Decimal = Decimal("5.0"),
    reason: str = "compra",
    person_id=None,
    notes: str = None,
) -> InventoryMovement:
    """Create a mock inventory movement."""
    movement = MagicMock(spec=InventoryMovement)
    movement.id = uuid4()
    movement.resource_id = resource_id or uuid4()
    movement.restaurant_id = restaurant_id or uuid4()
    movement.type = movement_type
    movement.quantity = quantity
    movement.reason = reason
    movement.date = datetime(2026, 3, 1, 12, 0, 0)
    movement.person_id = person_id
    movement.notes = notes
    movement.created_at = datetime(2026, 3, 1, 12, 0, 0)
    return movement


async def get_auth_token(client: AsyncClient, mock_user: User) -> str:
    """Get an auth token for testing."""
    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt:
        mock_repo.get_user_by_email.return_value = mock_user
        mock_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True

        login_response = await client.post(
            "/api/auth/login",
            json={"email": mock_user.email, "password": "password123"},
        )
        return login_response.json()["access_token"]


# ============================================================================
# Create Movement Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_entry_movement_success() -> None:
    """Test that valid entry movement returns 201 and increases stock."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_resource = create_mock_resource(
        current_stock=Decimal("10.0"),
        minimum_stock=Decimal("5.0"),
        restaurant_id=restaurant_id,
    )
    mock_movement = create_mock_movement(
        resource_id=mock_resource.id,
        restaurant_id=restaurant_id,
        movement_type="entry",
        quantity=Decimal("5.0"),
        reason="compra",
    )

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.inventory_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.inventory_service.resource_repository"
    ) as mock_resource_repo, patch(
        "src.core.services.inventory_service.inventory_movement_repository"
    ) as mock_movement_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.get_by_id.return_value = mock_resource
        mock_resource_repo.update.return_value = mock_resource
        mock_movement_repo.create.return_value = mock_movement

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                "/api/inventory-movements",
                json={
                    "resource_id": str(mock_resource.id),
                    "type": "entry",
                    "quantity": "5.0",
                    "reason": "compra",
                    "restaurant_id": str(restaurant_id),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "entry"
        assert data["reason"] == "compra"
        print("INFO [TestInventoryMovementAPI]: test_create_entry_movement_success - PASSED")


@pytest.mark.asyncio
async def test_create_exit_movement_success() -> None:
    """Test that valid exit movement returns 201 and decreases stock."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_resource = create_mock_resource(
        current_stock=Decimal("10.0"),
        minimum_stock=Decimal("5.0"),
        restaurant_id=restaurant_id,
    )
    mock_movement = create_mock_movement(
        resource_id=mock_resource.id,
        restaurant_id=restaurant_id,
        movement_type="exit",
        quantity=Decimal("3.0"),
        reason="uso",
    )

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.inventory_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.inventory_service.resource_repository"
    ) as mock_resource_repo, patch(
        "src.core.services.inventory_service.inventory_movement_repository"
    ) as mock_movement_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.get_by_id.return_value = mock_resource
        mock_resource_repo.update.return_value = mock_resource
        mock_movement_repo.create.return_value = mock_movement

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                "/api/inventory-movements",
                json={
                    "resource_id": str(mock_resource.id),
                    "type": "exit",
                    "quantity": "3.0",
                    "reason": "uso",
                    "restaurant_id": str(restaurant_id),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "exit"
        assert data["reason"] == "uso"
        print("INFO [TestInventoryMovementAPI]: test_create_exit_movement_success - PASSED")


@pytest.mark.asyncio
async def test_create_exit_movement_insufficient_stock() -> None:
    """Test that exit movement with insufficient stock returns 400."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_resource = create_mock_resource(
        current_stock=Decimal("3.0"),
        restaurant_id=restaurant_id,
    )

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.inventory_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.inventory_service.resource_repository"
    ) as mock_resource_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.get_by_id.return_value = mock_resource

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                "/api/inventory-movements",
                json={
                    "resource_id": str(mock_resource.id),
                    "type": "exit",
                    "quantity": "10.0",
                    "reason": "uso",
                    "restaurant_id": str(restaurant_id),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 400
        assert "Insufficient stock" in response.json()["detail"]
        print("INFO [TestInventoryMovementAPI]: test_create_exit_movement_insufficient_stock - PASSED")


@pytest.mark.asyncio
async def test_create_movement_resource_not_found() -> None:
    """Test that movement with invalid resource_id returns 404."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.inventory_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.inventory_service.resource_repository"
    ) as mock_resource_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.get_by_id.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                "/api/inventory-movements",
                json={
                    "resource_id": str(uuid4()),
                    "type": "entry",
                    "quantity": "5.0",
                    "reason": "compra",
                    "restaurant_id": str(restaurant_id),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        assert "Resource not found" in response.json()["detail"]
        print("INFO [TestInventoryMovementAPI]: test_create_movement_resource_not_found - PASSED")


@pytest.mark.asyncio
async def test_create_movement_unauthenticated() -> None:
    """Test that unauthenticated request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/inventory-movements",
            json={
                "resource_id": str(uuid4()),
                "type": "entry",
                "quantity": "5.0",
                "reason": "compra",
                "restaurant_id": str(uuid4()),
            },
        )

    assert response.status_code == 401
    print("INFO [TestInventoryMovementAPI]: test_create_movement_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_create_movement_no_restaurant_access() -> None:
    """Test that user without restaurant access gets 403."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.inventory_service.restaurant_repository"
    ) as mock_restaurant_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                "/api/inventory-movements",
                json={
                    "resource_id": str(uuid4()),
                    "type": "entry",
                    "quantity": "5.0",
                    "reason": "compra",
                    "restaurant_id": str(restaurant_id),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestInventoryMovementAPI]: test_create_movement_no_restaurant_access - PASSED")


@pytest.mark.asyncio
async def test_create_movement_invalid_quantity_zero() -> None:
    """Test that quantity of 0 returns 422."""
    mock_user = create_mock_user()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                "/api/inventory-movements",
                json={
                    "resource_id": str(uuid4()),
                    "type": "entry",
                    "quantity": "0",
                    "reason": "compra",
                    "restaurant_id": str(uuid4()),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        print("INFO [TestInventoryMovementAPI]: test_create_movement_invalid_quantity_zero - PASSED")


@pytest.mark.asyncio
async def test_create_movement_invalid_quantity_negative() -> None:
    """Test that negative quantity returns 422."""
    mock_user = create_mock_user()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                "/api/inventory-movements",
                json={
                    "resource_id": str(uuid4()),
                    "type": "entry",
                    "quantity": "-5",
                    "reason": "compra",
                    "restaurant_id": str(uuid4()),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        print("INFO [TestInventoryMovementAPI]: test_create_movement_invalid_quantity_negative - PASSED")


# ============================================================================
# List Movements Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_movements_by_resource_success() -> None:
    """Test that listing movements by resource returns 200."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    resource_id = uuid4()
    mock_resource = create_mock_resource(restaurant_id=restaurant_id)
    mock_resource.id = resource_id
    mock_m1 = create_mock_movement(resource_id=resource_id, restaurant_id=restaurant_id)
    mock_m2 = create_mock_movement(resource_id=resource_id, restaurant_id=restaurant_id, movement_type="exit")

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.inventory_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.inventory_service.resource_repository"
    ) as mock_resource_repo, patch(
        "src.core.services.inventory_service.inventory_movement_repository"
    ) as mock_movement_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.get_by_id.return_value = mock_resource
        mock_movement_repo.get_by_resource.return_value = [mock_m1, mock_m2]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/inventory-movements?resource_id={resource_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        print("INFO [TestInventoryMovementAPI]: test_list_movements_by_resource_success - PASSED")


@pytest.mark.asyncio
async def test_list_movements_by_restaurant_success() -> None:
    """Test that listing movements by restaurant returns 200."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_m1 = create_mock_movement(restaurant_id=restaurant_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.inventory_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.inventory_service.inventory_movement_repository"
    ) as mock_movement_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_movement_repo.get_by_restaurant.return_value = [mock_m1]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/inventory-movements?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        print("INFO [TestInventoryMovementAPI]: test_list_movements_by_restaurant_success - PASSED")


@pytest.mark.asyncio
async def test_list_movements_missing_filter() -> None:
    """Test that listing without resource_id or restaurant_id returns 400."""
    mock_user = create_mock_user()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                "/api/inventory-movements",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 400
        assert "resource_id or restaurant_id" in response.json()["detail"]
        print("INFO [TestInventoryMovementAPI]: test_list_movements_missing_filter - PASSED")


@pytest.mark.asyncio
async def test_list_movements_no_restaurant_access() -> None:
    """Test that user without restaurant access gets 403 when listing."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.inventory_service.restaurant_repository"
    ) as mock_restaurant_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/inventory-movements?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestInventoryMovementAPI]: test_list_movements_no_restaurant_access - PASSED")
