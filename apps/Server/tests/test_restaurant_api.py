"""Tests for restaurant API endpoints."""

from typing import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from main import app
from src.adapter.rest.dependencies import get_db
from src.models.restaurant import Restaurant
from src.models.user import User
from src.models.user_restaurant import UserRestaurant


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


def create_mock_restaurant(
    name: str = "Test Restaurant",
    address: str = "123 Main St",
    owner_id=None,
) -> Restaurant:
    """Create a mock restaurant."""
    restaurant = MagicMock(spec=Restaurant)
    restaurant.id = uuid4()
    restaurant.name = name
    restaurant.address = address
    restaurant.owner_id = owner_id or uuid4()
    restaurant.created_at = MagicMock()
    restaurant.updated_at = None
    return restaurant


def create_mock_user_restaurant(
    user_id,
    restaurant_id,
    role: str = "admin",
) -> UserRestaurant:
    """Create a mock user-restaurant membership."""
    user_restaurant = MagicMock(spec=UserRestaurant)
    user_restaurant.id = uuid4()
    user_restaurant.user_id = user_id
    user_restaurant.restaurant_id = restaurant_id
    user_restaurant.role = role
    user_restaurant.created_at = MagicMock()
    return user_restaurant


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
# Restaurant Creation Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_restaurant_success() -> None:
    """Test that valid restaurant creation returns 201."""
    mock_user = create_mock_user()
    mock_restaurant = create_mock_restaurant(owner_id=mock_user.id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.restaurant_service.restaurant_repository"
    ) as mock_restaurant_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.create_restaurant.return_value = mock_restaurant

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                "/api/restaurants",
                json={
                    "name": "My Restaurant",
                    "address": "123 Main St",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Restaurant"
        print("INFO [TestRestaurantAPI]: test_create_restaurant_success - PASSED")


@pytest.mark.asyncio
async def test_create_restaurant_unauthenticated() -> None:
    """Test that unauthenticated request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/restaurants",
            json={"name": "My Restaurant"},
        )

    assert response.status_code == 401
    print("INFO [TestRestaurantAPI]: test_create_restaurant_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_create_restaurant_invalid_name() -> None:
    """Test that POST with empty name returns 422."""
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
                "/api/restaurants",
                json={"name": ""},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        print("INFO [TestRestaurantAPI]: test_create_restaurant_invalid_name - PASSED")


# ============================================================================
# List Restaurants Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_restaurants_success() -> None:
    """Test that listing restaurants returns user's restaurants."""
    mock_user = create_mock_user()
    mock_r1 = create_mock_restaurant(name="Restaurant A")
    mock_r2 = create_mock_restaurant(name="Restaurant B")

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.restaurant_service.restaurant_repository"
    ) as mock_restaurant_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_restaurants_by_user.return_value = [mock_r1, mock_r2]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                "/api/restaurants",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        print("INFO [TestRestaurantAPI]: test_list_restaurants_success - PASSED")


@pytest.mark.asyncio
async def test_list_restaurants_empty() -> None:
    """Test that user with no restaurants gets empty list."""
    mock_user = create_mock_user()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.restaurant_service.restaurant_repository"
    ) as mock_restaurant_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_restaurants_by_user.return_value = []

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                "/api/restaurants",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        print("INFO [TestRestaurantAPI]: test_list_restaurants_empty - PASSED")


# ============================================================================
# Get Restaurant Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_restaurant_success() -> None:
    """Test that getting restaurant works for members."""
    mock_user = create_mock_user()
    mock_restaurant = create_mock_restaurant()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.restaurant_service.restaurant_repository"
    ) as mock_restaurant_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_restaurant_repo.get_restaurant_by_id.return_value = mock_restaurant

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/restaurants/{mock_restaurant.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == mock_restaurant.name
        print("INFO [TestRestaurantAPI]: test_get_restaurant_success - PASSED")


@pytest.mark.asyncio
async def test_get_restaurant_no_access() -> None:
    """Test that non-members cannot access restaurant."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.restaurant_service.restaurant_repository"
    ) as mock_restaurant_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = None  # No access

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/restaurants/{restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestRestaurantAPI]: test_get_restaurant_no_access - PASSED")


@pytest.mark.asyncio
async def test_get_restaurant_not_found() -> None:
    """Test that getting nonexistent restaurant returns 404."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.restaurant_service.restaurant_repository"
    ) as mock_restaurant_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_restaurant_repo.get_restaurant_by_id.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/restaurants/{restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        print("INFO [TestRestaurantAPI]: test_get_restaurant_not_found - PASSED")


# ============================================================================
# Update Restaurant Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_restaurant_success() -> None:
    """Test that admin can update restaurant."""
    mock_user = create_mock_user()
    mock_restaurant = create_mock_restaurant(owner_id=mock_user.id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.restaurant_service.restaurant_repository"
    ) as mock_restaurant_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_restaurant_repo.get_restaurant_by_id.return_value = mock_restaurant
        mock_restaurant_repo.update_restaurant.return_value = mock_restaurant

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.put(
                f"/api/restaurants/{mock_restaurant.id}",
                json={"name": "Updated Restaurant"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        print("INFO [TestRestaurantAPI]: test_update_restaurant_success - PASSED")


@pytest.mark.asyncio
async def test_update_restaurant_no_permission() -> None:
    """Test that non-admin cannot update restaurant."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.restaurant_service.restaurant_repository"
    ) as mock_restaurant_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "user"  # Regular user role

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.put(
                f"/api/restaurants/{restaurant_id}",
                json={"name": "Updated Restaurant"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestRestaurantAPI]: test_update_restaurant_no_permission - PASSED")


# ============================================================================
# Delete Restaurant Tests
# ============================================================================


@pytest.mark.asyncio
async def test_delete_restaurant_success() -> None:
    """Test that admin can delete restaurant."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.restaurant_service.restaurant_repository"
    ) as mock_restaurant_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_restaurant_repo.delete_restaurant.return_value = True

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.delete(
                f"/api/restaurants/{restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 204
        print("INFO [TestRestaurantAPI]: test_delete_restaurant_success - PASSED")


@pytest.mark.asyncio
async def test_delete_restaurant_no_permission() -> None:
    """Test that non-admin cannot delete restaurant."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.restaurant_service.restaurant_repository"
    ) as mock_restaurant_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "user"  # Regular user role

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.delete(
                f"/api/restaurants/{restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestRestaurantAPI]: test_delete_restaurant_no_permission - PASSED")
