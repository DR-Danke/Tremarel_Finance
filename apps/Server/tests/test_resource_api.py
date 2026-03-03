"""Tests for resource API endpoints."""

from decimal import Decimal
from typing import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from main import app
from src.adapter.rest.dependencies import get_db
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
# Resource Creation Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_resource_success() -> None:
    """Test that valid resource creation returns 201."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_resource = create_mock_resource(restaurant_id=restaurant_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.resource_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.resource_service.resource_repository"
    ) as mock_resource_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.create.return_value = mock_resource

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                "/api/resources",
                json={
                    "restaurant_id": str(restaurant_id),
                    "name": "Tomate",
                    "unit": "kg",
                    "type": "producto",
                    "current_stock": "10.0",
                    "minimum_stock": "5.0",
                    "last_unit_cost": "2.50",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Resource"
        assert "is_low_stock" in data
        print("INFO [TestResourceAPI]: test_create_resource_success - PASSED")


@pytest.mark.asyncio
async def test_create_resource_unauthenticated() -> None:
    """Test that unauthenticated request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/resources",
            json={
                "restaurant_id": str(uuid4()),
                "name": "Test",
                "unit": "kg",
            },
        )

    assert response.status_code == 401
    print("INFO [TestResourceAPI]: test_create_resource_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_create_resource_no_restaurant_access() -> None:
    """Test that user without restaurant access gets 403."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.resource_service.restaurant_repository"
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
                "/api/resources",
                json={
                    "restaurant_id": str(restaurant_id),
                    "name": "Test Resource",
                    "unit": "kg",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestResourceAPI]: test_create_resource_no_restaurant_access - PASSED")


@pytest.mark.asyncio
async def test_create_resource_invalid_data_negative_stock() -> None:
    """Test that POST with negative stock returns 422."""
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
                "/api/resources",
                json={
                    "restaurant_id": str(uuid4()),
                    "name": "Test",
                    "unit": "kg",
                    "current_stock": "-5",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        print("INFO [TestResourceAPI]: test_create_resource_invalid_data_negative_stock - PASSED")


@pytest.mark.asyncio
async def test_create_resource_invalid_data_missing_fields() -> None:
    """Test that POST with missing required fields returns 422."""
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
                "/api/resources",
                json={
                    "restaurant_id": str(uuid4()),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        print("INFO [TestResourceAPI]: test_create_resource_invalid_data_missing_fields - PASSED")


# ============================================================================
# List Resources Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_resources_success() -> None:
    """Test that listing resources returns restaurant's resources."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_r1 = create_mock_resource(name="Resource A", restaurant_id=restaurant_id)
    mock_r2 = create_mock_resource(name="Resource B", restaurant_id=restaurant_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.resource_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.resource_service.resource_repository"
    ) as mock_resource_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.get_by_restaurant.return_value = [mock_r1, mock_r2]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/resources?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        print("INFO [TestResourceAPI]: test_list_resources_success - PASSED")


@pytest.mark.asyncio
async def test_list_resources_with_type_filter() -> None:
    """Test that type filter works correctly."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_activo = create_mock_resource(name="Horno", resource_type="activo", restaurant_id=restaurant_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.resource_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.resource_service.resource_repository"
    ) as mock_resource_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.get_by_restaurant.return_value = [mock_activo]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/resources?restaurant_id={restaurant_id}&type=activo",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        print("INFO [TestResourceAPI]: test_list_resources_with_type_filter - PASSED")


@pytest.mark.asyncio
async def test_list_resources_empty() -> None:
    """Test that empty resource list returns empty array."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.resource_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.resource_service.resource_repository"
    ) as mock_resource_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.get_by_restaurant.return_value = []

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/resources?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        print("INFO [TestResourceAPI]: test_list_resources_empty - PASSED")


# ============================================================================
# Get Resource Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_resource_success() -> None:
    """Test that getting resource works for authorized users."""
    mock_user = create_mock_user()
    mock_resource = create_mock_resource()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.resource_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.resource_service.resource_repository"
    ) as mock_resource_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_resource_repo.get_by_id.return_value = mock_resource
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/resources/{mock_resource.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == mock_resource.name
        assert "is_low_stock" in data
        print("INFO [TestResourceAPI]: test_get_resource_success - PASSED")


@pytest.mark.asyncio
async def test_get_resource_not_found() -> None:
    """Test that getting nonexistent resource returns 404."""
    mock_user = create_mock_user()
    resource_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.resource_service.resource_repository"
    ) as mock_resource_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_resource_repo.get_by_id.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/resources/{resource_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        print("INFO [TestResourceAPI]: test_get_resource_not_found - PASSED")


@pytest.mark.asyncio
async def test_get_resource_no_access() -> None:
    """Test that user without restaurant access gets 403."""
    mock_user = create_mock_user()
    mock_resource = create_mock_resource()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.resource_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.resource_service.resource_repository"
    ) as mock_resource_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_resource_repo.get_by_id.return_value = mock_resource
        mock_restaurant_repo.get_user_restaurant_role.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/resources/{mock_resource.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestResourceAPI]: test_get_resource_no_access - PASSED")


# ============================================================================
# Update Resource Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_resource_success() -> None:
    """Test that authorized user can update resource."""
    mock_user = create_mock_user()
    mock_resource = create_mock_resource()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.resource_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.resource_service.resource_repository"
    ) as mock_resource_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_resource_repo.get_by_id.return_value = mock_resource
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.update.return_value = mock_resource

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.put(
                f"/api/resources/{mock_resource.id}",
                json={"current_stock": "3.0", "minimum_stock": "5.0"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        print("INFO [TestResourceAPI]: test_update_resource_success - PASSED")


@pytest.mark.asyncio
async def test_update_resource_no_access() -> None:
    """Test that user without restaurant access cannot update."""
    mock_user = create_mock_user()
    mock_resource = create_mock_resource()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.resource_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.resource_service.resource_repository"
    ) as mock_resource_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_resource_repo.get_by_id.return_value = mock_resource
        mock_restaurant_repo.get_user_restaurant_role.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.put(
                f"/api/resources/{mock_resource.id}",
                json={"name": "Updated Resource"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestResourceAPI]: test_update_resource_no_access - PASSED")


# ============================================================================
# Delete Resource Tests
# ============================================================================


@pytest.mark.asyncio
async def test_delete_resource_success() -> None:
    """Test that authorized user can delete resource."""
    mock_user = create_mock_user()
    mock_resource = create_mock_resource()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.resource_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.resource_service.resource_repository"
    ) as mock_resource_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_resource_repo.get_by_id.return_value = mock_resource
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.delete.return_value = True

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.delete(
                f"/api/resources/{mock_resource.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 204
        print("INFO [TestResourceAPI]: test_delete_resource_success - PASSED")


@pytest.mark.asyncio
async def test_delete_resource_no_access() -> None:
    """Test that user without restaurant access cannot delete."""
    mock_user = create_mock_user()
    mock_resource = create_mock_resource()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.resource_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.resource_service.resource_repository"
    ) as mock_resource_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_resource_repo.get_by_id.return_value = mock_resource
        mock_restaurant_repo.get_user_restaurant_role.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.delete(
                f"/api/resources/{mock_resource.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestResourceAPI]: test_delete_resource_no_access - PASSED")


# ============================================================================
# Low-Stock Resource Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_low_stock_resources_success() -> None:
    """Test that low-stock endpoint returns only low-stock resources."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_low = create_mock_resource(
        name="Low Stock",
        current_stock=Decimal("2.0"),
        minimum_stock=Decimal("10.0"),
        restaurant_id=restaurant_id,
    )

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.resource_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.resource_service.resource_repository"
    ) as mock_resource_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.get_low_stock.return_value = [mock_low]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/resources/low-stock?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["is_low_stock"] is True
        print("INFO [TestResourceAPI]: test_get_low_stock_resources_success - PASSED")


@pytest.mark.asyncio
async def test_get_low_stock_resources_empty() -> None:
    """Test that low-stock endpoint returns empty when no low-stock resources."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.resource_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.resource_service.resource_repository"
    ) as mock_resource_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_resource_repo.get_low_stock.return_value = []

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/resources/low-stock?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        print("INFO [TestResourceAPI]: test_get_low_stock_resources_empty - PASSED")
