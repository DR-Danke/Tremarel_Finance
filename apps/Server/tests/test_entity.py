"""Tests for entity endpoints."""

from typing import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from main import app
from src.adapter.rest.dependencies import get_db
from src.models.entity import Entity
from src.models.user import User
from src.models.user_entity import UserEntity


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


def create_mock_entity(
    name: str = "Test Entity",
    entity_type: str = "family",
    description: str = "A test entity",
) -> Entity:
    """Create a mock entity."""
    entity = MagicMock(spec=Entity)
    entity.id = uuid4()
    entity.name = name
    entity.type = entity_type
    entity.description = description
    entity.created_at = MagicMock()
    entity.updated_at = None
    return entity


def create_mock_user_entity(
    user_id: uuid4,
    entity_id: uuid4,
    role: str = "admin",
) -> UserEntity:
    """Create a mock user-entity membership."""
    user_entity = MagicMock(spec=UserEntity)
    user_entity.id = uuid4()
    user_entity.user_id = user_id
    user_entity.entity_id = entity_id
    user_entity.role = role
    user_entity.created_at = MagicMock()
    return user_entity


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
# Entity Creation Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_entity_success() -> None:
    """Test that valid entity creation returns 201."""
    mock_user = create_mock_user()
    mock_entity = create_mock_entity()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.entity_service.entity_repository"
    ) as mock_entity_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_entity_repo.create_entity.return_value = mock_entity
        mock_entity_repo.add_user_to_entity.return_value = create_mock_user_entity(
            mock_user.id, mock_entity.id
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                "/api/entities",
                json={
                    "name": "My Family",
                    "type": "family",
                    "description": "Family finances",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Entity"
        assert data["type"] == "family"
        print("INFO [TestEntity]: test_create_entity_success - PASSED")


@pytest.mark.asyncio
async def test_create_entity_invalid_type() -> None:
    """Test that invalid entity type returns 422."""
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
                "/api/entities",
                json={
                    "name": "Invalid Entity",
                    "type": "invalid_type",
                    "description": "Should fail",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        print("INFO [TestEntity]: test_create_entity_invalid_type - PASSED")


@pytest.mark.asyncio
async def test_create_entity_unauthenticated() -> None:
    """Test that unauthenticated request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/entities",
            json={
                "name": "My Family",
                "type": "family",
            },
        )

    assert response.status_code == 401
    print("INFO [TestEntity]: test_create_entity_unauthenticated - PASSED")


# ============================================================================
# List Entities Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_entities_success() -> None:
    """Test that listing entities returns user's entities."""
    mock_user = create_mock_user()
    mock_entity1 = create_mock_entity(name="Family", entity_type="family")
    mock_entity2 = create_mock_entity(name="Startup", entity_type="startup")

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.entity_service.entity_repository"
    ) as mock_entity_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_entity_repo.get_entities_by_user_id.return_value = [mock_entity1, mock_entity2]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                "/api/entities",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        print("INFO [TestEntity]: test_list_entities_success - PASSED")


@pytest.mark.asyncio
async def test_list_entities_empty() -> None:
    """Test that new user has no entities."""
    mock_user = create_mock_user()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.entity_service.entity_repository"
    ) as mock_entity_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_entity_repo.get_entities_by_user_id.return_value = []

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                "/api/entities",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        print("INFO [TestEntity]: test_list_entities_empty - PASSED")


# ============================================================================
# Get Entity Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_entity_success() -> None:
    """Test that getting entity works for members."""
    mock_user = create_mock_user()
    mock_entity = create_mock_entity()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.entity_service.entity_repository"
    ) as mock_entity_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_entity_repo.get_user_entity_role.return_value = "admin"
        mock_entity_repo.get_entity_by_id.return_value = mock_entity

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/entities/{mock_entity.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == mock_entity.name
        print("INFO [TestEntity]: test_get_entity_success - PASSED")


@pytest.mark.asyncio
async def test_get_entity_no_access() -> None:
    """Test that non-members cannot access entity."""
    mock_user = create_mock_user()
    entity_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.entity_service.entity_repository"
    ) as mock_entity_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_entity_repo.get_user_entity_role.return_value = None  # No access

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/entities/{entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestEntity]: test_get_entity_no_access - PASSED")


# ============================================================================
# Update Entity Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_entity_admin_success() -> None:
    """Test that admin can update entity."""
    mock_user = create_mock_user()
    mock_entity = create_mock_entity()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.entity_service.entity_repository"
    ) as mock_entity_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_entity_repo.get_user_entity_role.return_value = "admin"
        mock_entity_repo.get_entity_by_id.return_value = mock_entity
        mock_entity_repo.update_entity.return_value = mock_entity

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.put(
                f"/api/entities/{mock_entity.id}",
                json={"name": "Updated Family"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        print("INFO [TestEntity]: test_update_entity_admin_success - PASSED")


@pytest.mark.asyncio
async def test_update_entity_user_forbidden() -> None:
    """Test that regular user cannot update entity."""
    mock_user = create_mock_user()
    entity_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.entity_service.entity_repository"
    ) as mock_entity_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_entity_repo.get_user_entity_role.return_value = "user"  # Regular user role

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.put(
                f"/api/entities/{entity_id}",
                json={"name": "Updated Family"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestEntity]: test_update_entity_user_forbidden - PASSED")


# ============================================================================
# Delete Entity Tests
# ============================================================================


@pytest.mark.asyncio
async def test_delete_entity_admin_success() -> None:
    """Test that admin can delete entity."""
    mock_user = create_mock_user()
    entity_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.entity_service.entity_repository"
    ) as mock_entity_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_entity_repo.get_user_entity_role.return_value = "admin"
        mock_entity_repo.delete_entity.return_value = True

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.delete(
                f"/api/entities/{entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 204
        print("INFO [TestEntity]: test_delete_entity_admin_success - PASSED")


@pytest.mark.asyncio
async def test_delete_entity_manager_forbidden() -> None:
    """Test that manager cannot delete entity."""
    mock_user = create_mock_user()
    entity_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.entity_service.entity_repository"
    ) as mock_entity_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_entity_repo.get_user_entity_role.return_value = "manager"  # Manager role

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.delete(
                f"/api/entities/{entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestEntity]: test_delete_entity_manager_forbidden - PASSED")


# ============================================================================
# Add Member Tests
# ============================================================================


@pytest.mark.asyncio
async def test_add_member_admin_success() -> None:
    """Test that admin can add members."""
    mock_user = create_mock_user()
    target_user_id = uuid4()
    entity_id = uuid4()
    mock_user_entity = create_mock_user_entity(target_user_id, entity_id, "user")

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.entity_service.entity_repository"
    ) as mock_entity_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True

        # First call for auth check (admin), second call for target user check (None = not member)
        mock_entity_repo.get_user_entity_role.side_effect = ["admin", None]
        mock_entity_repo.add_user_to_entity.return_value = mock_user_entity

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                f"/api/entities/{entity_id}/members",
                json={"user_id": str(target_user_id), "role": "user"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        print("INFO [TestEntity]: test_add_member_admin_success - PASSED")


@pytest.mark.asyncio
async def test_add_member_already_member() -> None:
    """Test that adding existing member returns 400."""
    mock_user = create_mock_user()
    target_user_id = uuid4()
    entity_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.entity_service.entity_repository"
    ) as mock_entity_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True

        # First call for auth check (admin), second call for target user check (already member)
        mock_entity_repo.get_user_entity_role.side_effect = ["admin", "user"]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                f"/api/entities/{entity_id}/members",
                json={"user_id": str(target_user_id), "role": "user"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 400
        assert "already a member" in response.json()["detail"]
        print("INFO [TestEntity]: test_add_member_already_member - PASSED")


# ============================================================================
# Remove Member Tests
# ============================================================================


@pytest.mark.asyncio
async def test_remove_member_admin_success() -> None:
    """Test that admin can remove members."""
    mock_user = create_mock_user()
    target_user_id = uuid4()
    entity_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.entity_service.entity_repository"
    ) as mock_entity_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True

        # First call for auth check, second for target user check
        mock_entity_repo.get_user_entity_role.side_effect = ["admin", "user"]
        mock_entity_repo.remove_user_from_entity.return_value = True

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.delete(
                f"/api/entities/{entity_id}/members/{target_user_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 204
        print("INFO [TestEntity]: test_remove_member_admin_success - PASSED")


@pytest.mark.asyncio
async def test_remove_last_admin_forbidden() -> None:
    """Test that removing last admin returns 400."""
    mock_user = create_mock_user()
    entity_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.entity_service.entity_repository"
    ) as mock_entity_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True

        # Both calls return admin (self-removal attempt)
        mock_entity_repo.get_user_entity_role.side_effect = ["admin", "admin"]
        mock_entity_repo.count_entity_admins.return_value = 1  # Last admin

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.delete(
                f"/api/entities/{entity_id}/members/{mock_user.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 400
        assert "last admin" in response.json()["detail"]
        print("INFO [TestEntity]: test_remove_last_admin_forbidden - PASSED")


# ============================================================================
# Get User Role Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_members_success() -> None:
    """Test that members can list entity members."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    members = [
        {
            "id": uuid4(),
            "user_id": mock_user.id,
            "email": mock_user.email,
            "first_name": mock_user.first_name,
            "last_name": mock_user.last_name,
            "role": "admin",
            "created_at": MagicMock(),
        }
    ]

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.entity_service.entity_repository"
    ) as mock_entity_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_entity_repo.get_user_entity_role.return_value = "admin"
        mock_entity_repo.get_entity_members.return_value = members

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/entities/{entity_id}/members",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["email"] == mock_user.email
        print("INFO [TestEntity]: test_list_members_success - PASSED")
