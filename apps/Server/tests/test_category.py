"""Tests for category endpoints."""

from typing import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from main import app
from src.adapter.rest.dependencies import get_db
from src.models.category import Category
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
) -> User:
    """Create a mock user with pre-computed password hash."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.email = email
    user.password_hash = PASSWORD_HASH
    user.first_name = "Test"
    user.last_name = "User"
    user.role = role
    user.is_active = is_active
    return user


def create_mock_category(
    name: str = "Test Category",
    type: str = "expense",
    entity_id=None,
    parent_id=None,
    is_active: bool = True,
) -> Category:
    """Create a mock category."""
    category = MagicMock(spec=Category)
    category.id = uuid4()
    category.entity_id = entity_id or uuid4()
    category.name = name
    category.type = type
    category.parent_id = parent_id
    category.description = None
    category.color = None
    category.icon = None
    category.is_active = is_active
    category.created_at = MagicMock()
    category.updated_at = None
    return category


async def get_auth_token(client: AsyncClient, mock_user: User) -> str:
    """Helper to get auth token for a mock user."""
    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt:
        mock_repo.get_user_by_email.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True

        response = await client.post(
            "/api/auth/login",
            json={"email": mock_user.email, "password": "password123"},
        )
        return response.json()["access_token"]


# ============================================================================
# Category Creation Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_category_success() -> None:
    """Test that valid category creation returns 201."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_category = create_mock_category(name="Food", type="expense", entity_id=entity_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.category_service.category_repository"
    ) as mock_cat_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_cat_repo.create_category.return_value = mock_category

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)

            response = await client.post(
                "/api/categories/",
                json={
                    "entity_id": str(entity_id),
                    "name": "Food",
                    "type": "expense",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Food"
        assert data["type"] == "expense"
        print("INFO [TestCategory]: test_create_category_success - PASSED")


@pytest.mark.asyncio
async def test_create_category_with_parent() -> None:
    """Test creating a subcategory with parent."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    parent_category = create_mock_category(
        name="Food", type="expense", entity_id=entity_id
    )
    child_category = create_mock_category(
        name="Groceries",
        type="expense",
        entity_id=entity_id,
        parent_id=parent_category.id,
    )

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.category_service.category_repository"
    ) as mock_cat_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_cat_repo.get_category_by_id.return_value = parent_category
        mock_cat_repo.create_category.return_value = child_category

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)

            response = await client.post(
                "/api/categories/",
                json={
                    "entity_id": str(entity_id),
                    "name": "Groceries",
                    "type": "expense",
                    "parent_id": str(parent_category.id),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Groceries"
        assert data["parent_id"] == str(parent_category.id)
        print("INFO [TestCategory]: test_create_category_with_parent - PASSED")


@pytest.mark.asyncio
async def test_create_category_invalid_type() -> None:
    """Test that invalid type returns 422."""
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
                "/api/categories/",
                json={
                    "entity_id": str(uuid4()),
                    "name": "Invalid",
                    "type": "invalid_type",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        print("INFO [TestCategory]: test_create_category_invalid_type - PASSED")


@pytest.mark.asyncio
async def test_create_category_missing_name() -> None:
    """Test that missing name returns 422."""
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
                "/api/categories/",
                json={
                    "entity_id": str(uuid4()),
                    "type": "expense",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        print("INFO [TestCategory]: test_create_category_missing_name - PASSED")


@pytest.mark.asyncio
async def test_create_category_parent_type_mismatch() -> None:
    """Test that parent type mismatch returns 400."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    parent_category = create_mock_category(
        name="Salary", type="income", entity_id=entity_id
    )

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.category_service.category_repository"
    ) as mock_cat_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_cat_repo.get_category_by_id.return_value = parent_category

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)

            # Try to create expense child under income parent
            response = await client.post(
                "/api/categories/",
                json={
                    "entity_id": str(entity_id),
                    "name": "Food",
                    "type": "expense",
                    "parent_id": str(parent_category.id),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 400
        assert "type" in response.json()["detail"].lower()
        print("INFO [TestCategory]: test_create_category_parent_type_mismatch - PASSED")


# ============================================================================
# Category Retrieval Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_categories_by_entity() -> None:
    """Test getting all categories for an entity."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_categories = [
        create_mock_category(name="Food", type="expense", entity_id=entity_id),
        create_mock_category(name="Salary", type="income", entity_id=entity_id),
    ]

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.category_service.category_repository"
    ) as mock_cat_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_cat_repo.get_categories_by_entity.return_value = mock_categories

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/categories/entity/{entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        print("INFO [TestCategory]: test_get_categories_by_entity - PASSED")


@pytest.mark.asyncio
async def test_get_category_tree() -> None:
    """Test getting hierarchical category tree."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    parent = create_mock_category(name="Food", type="expense", entity_id=entity_id)
    child = create_mock_category(
        name="Groceries",
        type="expense",
        entity_id=entity_id,
        parent_id=parent.id,
    )

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.category_service.category_repository"
    ) as mock_cat_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_cat_repo.get_categories_by_entity.return_value = [parent, child]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/categories/entity/{entity_id}/tree",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        # Should have 1 root with 1 child
        assert len(data) == 1
        assert data[0]["name"] == "Food"
        assert len(data[0]["children"]) == 1
        assert data[0]["children"][0]["name"] == "Groceries"
        print("INFO [TestCategory]: test_get_category_tree - PASSED")


@pytest.mark.asyncio
async def test_get_single_category() -> None:
    """Test getting a single category by ID."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_category = create_mock_category(name="Food", type="expense", entity_id=entity_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.category_service.category_repository"
    ) as mock_cat_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_cat_repo.get_category_by_id.return_value = mock_category

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/categories/{mock_category.id}",
                params={"entity_id": str(entity_id)},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Food"
        print("INFO [TestCategory]: test_get_single_category - PASSED")


@pytest.mark.asyncio
async def test_get_category_not_found() -> None:
    """Test getting non-existent category returns 404."""
    mock_user = create_mock_user()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.category_service.category_repository"
    ) as mock_cat_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_cat_repo.get_category_by_id.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/categories/{uuid4()}",
                params={"entity_id": str(uuid4())},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        print("INFO [TestCategory]: test_get_category_not_found - PASSED")


# ============================================================================
# Category Update Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_category_success() -> None:
    """Test updating a category."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_category = create_mock_category(name="Food", type="expense", entity_id=entity_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.category_service.category_repository"
    ) as mock_cat_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_cat_repo.get_category_by_id.return_value = mock_category

        # Update the mock to return updated name
        updated_category = create_mock_category(
            name="Groceries", type="expense", entity_id=entity_id
        )
        updated_category.id = mock_category.id
        mock_cat_repo.update_category.return_value = updated_category

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)

            response = await client.put(
                f"/api/categories/{mock_category.id}",
                params={"entity_id": str(entity_id)},
                json={"name": "Groceries"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Groceries"
        print("INFO [TestCategory]: test_update_category_success - PASSED")


# ============================================================================
# Category Delete Tests
# ============================================================================


@pytest.mark.asyncio
async def test_delete_category_success() -> None:
    """Test deleting a category without children."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_category = create_mock_category(name="Food", type="expense", entity_id=entity_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.category_service.category_repository"
    ) as mock_cat_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_cat_repo.get_category_by_id.return_value = mock_category
        mock_cat_repo.has_children.return_value = False
        mock_cat_repo.has_transactions.return_value = False
        mock_cat_repo.delete_category.return_value = True

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)

            response = await client.delete(
                f"/api/categories/{mock_category.id}",
                params={"entity_id": str(entity_id)},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 204
        print("INFO [TestCategory]: test_delete_category_success - PASSED")


@pytest.mark.asyncio
async def test_delete_category_with_children() -> None:
    """Test that deleting category with children returns 400."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_category = create_mock_category(name="Food", type="expense", entity_id=entity_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.category_service.category_repository"
    ) as mock_cat_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_cat_repo.get_category_by_id.return_value = mock_category
        mock_cat_repo.has_children.return_value = True  # Has children

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)

            response = await client.delete(
                f"/api/categories/{mock_category.id}",
                params={"entity_id": str(entity_id)},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 400
        assert "subcategories" in response.json()["detail"].lower()
        print("INFO [TestCategory]: test_delete_category_with_children - PASSED")


# ============================================================================
# Authorization Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_category_unauthorized() -> None:
    """Test that unauthenticated request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/categories/",
            json={
                "entity_id": str(uuid4()),
                "name": "Test",
                "type": "expense",
            },
        )

    assert response.status_code == 401
    print("INFO [TestCategory]: test_create_category_unauthorized - PASSED")


@pytest.mark.asyncio
async def test_get_categories_unauthorized() -> None:
    """Test that unauthenticated request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(f"/api/categories/entity/{uuid4()}")

    assert response.status_code == 401
    print("INFO [TestCategory]: test_get_categories_unauthorized - PASSED")


@pytest.mark.asyncio
async def test_access_category_from_wrong_entity() -> None:
    """Test that accessing category from wrong entity returns 404."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    different_entity_id = uuid4()
    mock_category = create_mock_category(
        name="Food", type="expense", entity_id=entity_id
    )

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.category_service.category_repository"
    ) as mock_cat_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_cat_repo.get_category_by_id.return_value = mock_category

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)

            # Try to access with different entity_id
            response = await client.get(
                f"/api/categories/{mock_category.id}",
                params={"entity_id": str(different_entity_id)},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        print("INFO [TestCategory]: test_access_category_from_wrong_entity - PASSED")
