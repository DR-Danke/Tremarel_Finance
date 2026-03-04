"""Tests for person API endpoints."""

from typing import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from main import app
from src.adapter.rest.dependencies import get_db
from src.models.person import Person
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


def create_mock_person(
    name: str = "Test Person",
    role: str = "chef",
    email: str = "person@restaurant.com",
    whatsapp: str = "+52 555 123 4567",
    person_type: str = "employee",
    restaurant_id=None,
) -> Person:
    """Create a mock person."""
    person = MagicMock(spec=Person)
    person.id = uuid4()
    person.restaurant_id = restaurant_id or uuid4()
    person.name = name
    person.role = role
    person.email = email
    person.whatsapp = whatsapp
    person.push_token = None
    person.type = person_type
    person.created_at = MagicMock()
    person.updated_at = None
    return person


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
# Person Creation Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_person_success() -> None:
    """Test that valid person creation returns 201."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_person = create_mock_person(restaurant_id=restaurant_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.person_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.person_service.person_repository"
    ) as mock_person_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_person_repo.create.return_value = mock_person

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                "/api/persons",
                json={
                    "restaurant_id": str(restaurant_id),
                    "name": "Juan Pérez",
                    "role": "chef",
                    "email": "juan@restaurant.com",
                    "type": "employee",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Person"
        print("INFO [TestPersonAPI]: test_create_person_success - PASSED")


@pytest.mark.asyncio
async def test_create_person_unauthenticated() -> None:
    """Test that unauthenticated request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/persons",
            json={
                "restaurant_id": str(uuid4()),
                "name": "Test",
                "role": "chef",
            },
        )

    assert response.status_code == 401
    print("INFO [TestPersonAPI]: test_create_person_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_create_person_no_restaurant_access() -> None:
    """Test that user without restaurant access gets 403."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.person_service.restaurant_repository"
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
                "/api/persons",
                json={
                    "restaurant_id": str(restaurant_id),
                    "name": "Test Person",
                    "role": "chef",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestPersonAPI]: test_create_person_no_restaurant_access - PASSED")


@pytest.mark.asyncio
async def test_create_person_invalid_data() -> None:
    """Test that POST with invalid data returns 422."""
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
                "/api/persons",
                json={
                    "restaurant_id": str(uuid4()),
                    "name": "",  # Empty name should fail
                    "role": "chef",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        print("INFO [TestPersonAPI]: test_create_person_invalid_data - PASSED")


# ============================================================================
# List Persons Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_persons_success() -> None:
    """Test that listing persons returns restaurant's persons."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_p1 = create_mock_person(name="Person A", restaurant_id=restaurant_id)
    mock_p2 = create_mock_person(name="Person B", restaurant_id=restaurant_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.person_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.person_service.person_repository"
    ) as mock_person_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_person_repo.get_by_restaurant.return_value = [mock_p1, mock_p2]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/persons?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        print("INFO [TestPersonAPI]: test_list_persons_success - PASSED")


@pytest.mark.asyncio
async def test_list_persons_with_type_filter() -> None:
    """Test that type filter works correctly."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_supplier = create_mock_person(name="Supplier", person_type="supplier", restaurant_id=restaurant_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.person_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.person_service.person_repository"
    ) as mock_person_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_person_repo.get_by_restaurant.return_value = [mock_supplier]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/persons?restaurant_id={restaurant_id}&type=supplier",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        print("INFO [TestPersonAPI]: test_list_persons_with_type_filter - PASSED")


@pytest.mark.asyncio
async def test_list_persons_empty() -> None:
    """Test that empty person list returns empty array."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.person_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.person_service.person_repository"
    ) as mock_person_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_person_repo.get_by_restaurant.return_value = []

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/persons?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        print("INFO [TestPersonAPI]: test_list_persons_empty - PASSED")


# ============================================================================
# Get Person Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_person_success() -> None:
    """Test that getting person works for authorized users."""
    mock_user = create_mock_user()
    mock_person = create_mock_person()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.person_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.person_service.person_repository"
    ) as mock_person_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_person_repo.get_by_id.return_value = mock_person
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/persons/{mock_person.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == mock_person.name
        print("INFO [TestPersonAPI]: test_get_person_success - PASSED")


@pytest.mark.asyncio
async def test_get_person_not_found() -> None:
    """Test that getting nonexistent person returns 404."""
    mock_user = create_mock_user()
    person_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.person_service.person_repository"
    ) as mock_person_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_person_repo.get_by_id.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/persons/{person_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        print("INFO [TestPersonAPI]: test_get_person_not_found - PASSED")


@pytest.mark.asyncio
async def test_get_person_no_access() -> None:
    """Test that user without restaurant access gets 403."""
    mock_user = create_mock_user()
    mock_person = create_mock_person()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.person_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.person_service.person_repository"
    ) as mock_person_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_person_repo.get_by_id.return_value = mock_person
        mock_restaurant_repo.get_user_restaurant_role.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/persons/{mock_person.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestPersonAPI]: test_get_person_no_access - PASSED")


# ============================================================================
# Update Person Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_person_success() -> None:
    """Test that authorized user can update person."""
    mock_user = create_mock_user()
    mock_person = create_mock_person()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.person_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.person_service.person_repository"
    ) as mock_person_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_person_repo.get_by_id.return_value = mock_person
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_person_repo.update.return_value = mock_person

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.put(
                f"/api/persons/{mock_person.id}",
                json={"name": "Updated Person"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        print("INFO [TestPersonAPI]: test_update_person_success - PASSED")


@pytest.mark.asyncio
async def test_update_person_no_access() -> None:
    """Test that user without restaurant access cannot update."""
    mock_user = create_mock_user()
    mock_person = create_mock_person()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.person_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.person_service.person_repository"
    ) as mock_person_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_person_repo.get_by_id.return_value = mock_person
        mock_restaurant_repo.get_user_restaurant_role.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.put(
                f"/api/persons/{mock_person.id}",
                json={"name": "Updated Person"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestPersonAPI]: test_update_person_no_access - PASSED")


# ============================================================================
# Delete Person Tests
# ============================================================================


@pytest.mark.asyncio
async def test_delete_person_success() -> None:
    """Test that authorized user can delete person."""
    mock_user = create_mock_user()
    mock_person = create_mock_person()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.person_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.person_service.person_repository"
    ) as mock_person_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_person_repo.get_by_id.return_value = mock_person
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_person_repo.delete.return_value = True

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.delete(
                f"/api/persons/{mock_person.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 204
        print("INFO [TestPersonAPI]: test_delete_person_success - PASSED")


@pytest.mark.asyncio
async def test_delete_person_no_access() -> None:
    """Test that user without restaurant access cannot delete."""
    mock_user = create_mock_user()
    mock_person = create_mock_person()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.person_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.person_service.person_repository"
    ) as mock_person_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_person_repo.get_by_id.return_value = mock_person
        mock_restaurant_repo.get_user_restaurant_role.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.delete(
                f"/api/persons/{mock_person.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestPersonAPI]: test_delete_person_no_access - PASSED")


# ============================================================================
# Search Persons Tests
# ============================================================================


@pytest.mark.asyncio
async def test_search_persons_success() -> None:
    """Test that search returns matching persons."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_person = create_mock_person(name="Juan Pérez", restaurant_id=restaurant_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.person_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.person_service.person_repository"
    ) as mock_person_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_person_repo.search.return_value = [mock_person]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/persons/search?restaurant_id={restaurant_id}&query=Juan",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        print("INFO [TestPersonAPI]: test_search_persons_success - PASSED")


@pytest.mark.asyncio
async def test_search_persons_no_results() -> None:
    """Test that search with no matches returns empty array."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.person_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.person_service.person_repository"
    ) as mock_person_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_person_repo.search.return_value = []

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/persons/search?restaurant_id={restaurant_id}&query=nonexistent",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        print("INFO [TestPersonAPI]: test_search_persons_no_results - PASSED")
