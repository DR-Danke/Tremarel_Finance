"""Tests for recipe API endpoints."""

from decimal import Decimal
from typing import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from main import app
from src.adapter.rest.dependencies import get_db
from src.models.recipe import Recipe, RecipeItem
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


def create_mock_recipe(
    name: str = "Test Recipe",
    sale_price: Decimal = Decimal("25.00"),
    current_cost: Decimal = Decimal("8.00"),
    margin_percent: Decimal = Decimal("68.00"),
    is_profitable: bool = True,
    is_active: bool = True,
    restaurant_id=None,
) -> Recipe:
    """Create a mock recipe."""
    recipe = MagicMock(spec=Recipe)
    recipe.id = uuid4()
    recipe.restaurant_id = restaurant_id or uuid4()
    recipe.name = name
    recipe.sale_price = sale_price
    recipe.current_cost = current_cost
    recipe.margin_percent = margin_percent
    recipe.is_profitable = is_profitable
    recipe.is_active = is_active
    recipe.created_at = MagicMock()
    recipe.updated_at = None
    return recipe


def create_mock_recipe_item(
    recipe_id=None,
    resource_id=None,
    quantity: Decimal = Decimal("2.0"),
    unit: str = "kg",
) -> RecipeItem:
    """Create a mock recipe item."""
    item = MagicMock(spec=RecipeItem)
    item.id = uuid4()
    item.recipe_id = recipe_id or uuid4()
    item.resource_id = resource_id or uuid4()
    item.quantity = quantity
    item.unit = unit
    item.created_at = MagicMock()
    return item


def create_mock_resource(
    name: str = "Ingredient",
    last_unit_cost: Decimal = Decimal("4.00"),
) -> Resource:
    """Create a mock resource for cost lookups."""
    resource = MagicMock(spec=Resource)
    resource.id = uuid4()
    resource.name = name
    resource.last_unit_cost = last_unit_cost
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
# Recipe Creation Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_recipe_success() -> None:
    """Test that valid recipe creation returns 201."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    resource_id = uuid4()
    mock_recipe = create_mock_recipe(restaurant_id=restaurant_id)
    mock_item = create_mock_recipe_item(recipe_id=mock_recipe.id, resource_id=resource_id)
    mock_resource = create_mock_resource()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.recipe_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.recipe_service.recipe_repository"
    ) as mock_recipe_repo, patch(
        "src.core.services.recipe_service.resource_repository"
    ) as mock_resource_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_recipe_repo.create.return_value = mock_recipe
        mock_recipe_repo.get_by_id.return_value = mock_recipe
        mock_recipe_repo.get_items.return_value = [mock_item]
        mock_resource_repo.get_by_id.return_value = mock_resource

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                "/api/recipes",
                json={
                    "restaurant_id": str(restaurant_id),
                    "name": "Pasta Carbonara",
                    "sale_price": "25.00",
                    "items": [
                        {
                            "resource_id": str(resource_id),
                            "quantity": "2.0",
                            "unit": "kg",
                        }
                    ],
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Recipe"
        assert "items" in data
        assert len(data["items"]) == 1
        print("INFO [TestRecipeAPI]: test_create_recipe_success - PASSED")


@pytest.mark.asyncio
async def test_create_recipe_unauthenticated() -> None:
    """Test that unauthenticated request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/recipes",
            json={
                "restaurant_id": str(uuid4()),
                "name": "Test",
                "sale_price": "10.00",
                "items": [
                    {"resource_id": str(uuid4()), "quantity": "1", "unit": "kg"}
                ],
            },
        )

    assert response.status_code == 401
    print("INFO [TestRecipeAPI]: test_create_recipe_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_create_recipe_no_restaurant_access() -> None:
    """Test that user without restaurant access gets 403."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.recipe_service.restaurant_repository"
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
                "/api/recipes",
                json={
                    "restaurant_id": str(restaurant_id),
                    "name": "Test",
                    "sale_price": "10.00",
                    "items": [
                        {"resource_id": str(uuid4()), "quantity": "1", "unit": "kg"}
                    ],
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestRecipeAPI]: test_create_recipe_no_restaurant_access - PASSED")


@pytest.mark.asyncio
async def test_create_recipe_validation_missing_name() -> None:
    """Test that POST with missing name returns 422."""
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
                "/api/recipes",
                json={
                    "restaurant_id": str(uuid4()),
                    "sale_price": "10.00",
                    "items": [
                        {"resource_id": str(uuid4()), "quantity": "1", "unit": "kg"}
                    ],
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        print("INFO [TestRecipeAPI]: test_create_recipe_validation_missing_name - PASSED")


@pytest.mark.asyncio
async def test_create_recipe_validation_sale_price_zero() -> None:
    """Test that POST with sale_price = 0 returns 422."""
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
                "/api/recipes",
                json={
                    "restaurant_id": str(uuid4()),
                    "name": "Test",
                    "sale_price": "0",
                    "items": [
                        {"resource_id": str(uuid4()), "quantity": "1", "unit": "kg"}
                    ],
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        print("INFO [TestRecipeAPI]: test_create_recipe_validation_sale_price_zero - PASSED")


@pytest.mark.asyncio
async def test_create_recipe_validation_empty_items() -> None:
    """Test that POST with empty items returns 422."""
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
                "/api/recipes",
                json={
                    "restaurant_id": str(uuid4()),
                    "name": "Test",
                    "sale_price": "10.00",
                    "items": [],
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        print("INFO [TestRecipeAPI]: test_create_recipe_validation_empty_items - PASSED")


# ============================================================================
# List Recipes Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_recipes_success() -> None:
    """Test that listing recipes returns restaurant's recipes."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_recipe1 = create_mock_recipe(name="Recipe A", restaurant_id=restaurant_id)
    mock_recipe2 = create_mock_recipe(name="Recipe B", restaurant_id=restaurant_id)
    mock_item1 = create_mock_recipe_item(recipe_id=mock_recipe1.id)
    mock_item2 = create_mock_recipe_item(recipe_id=mock_recipe2.id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.recipe_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.recipe_service.recipe_repository"
    ) as mock_recipe_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_recipe_repo.get_by_restaurant.return_value = [mock_recipe1, mock_recipe2]
        mock_recipe_repo.get_items.side_effect = [[mock_item1], [mock_item2]]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/recipes?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        print("INFO [TestRecipeAPI]: test_list_recipes_success - PASSED")


@pytest.mark.asyncio
async def test_list_recipes_empty() -> None:
    """Test that empty recipe list returns empty array."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.recipe_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.recipe_service.recipe_repository"
    ) as mock_recipe_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_recipe_repo.get_by_restaurant.return_value = []

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/recipes?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
        print("INFO [TestRecipeAPI]: test_list_recipes_empty - PASSED")


@pytest.mark.asyncio
async def test_list_recipes_unauthenticated() -> None:
    """Test that unauthenticated list request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"/api/recipes?restaurant_id={uuid4()}",
        )

    assert response.status_code == 401
    print("INFO [TestRecipeAPI]: test_list_recipes_unauthenticated - PASSED")


# ============================================================================
# Get Recipe Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_recipe_success() -> None:
    """Test that getting recipe works for authorized users."""
    mock_user = create_mock_user()
    mock_recipe = create_mock_recipe()
    mock_item = create_mock_recipe_item(recipe_id=mock_recipe.id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.recipe_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.recipe_service.recipe_repository"
    ) as mock_recipe_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_recipe_repo.get_by_id.return_value = mock_recipe
        mock_recipe_repo.get_items.return_value = [mock_item]
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/recipes/{mock_recipe.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == mock_recipe.name
        assert "items" in data
        assert len(data["items"]) == 1
        print("INFO [TestRecipeAPI]: test_get_recipe_success - PASSED")


@pytest.mark.asyncio
async def test_get_recipe_not_found() -> None:
    """Test that getting nonexistent recipe returns 404."""
    mock_user = create_mock_user()
    recipe_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.recipe_service.recipe_repository"
    ) as mock_recipe_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_recipe_repo.get_by_id.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/recipes/{recipe_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        print("INFO [TestRecipeAPI]: test_get_recipe_not_found - PASSED")


@pytest.mark.asyncio
async def test_get_recipe_no_access() -> None:
    """Test that user without restaurant access gets 403."""
    mock_user = create_mock_user()
    mock_recipe = create_mock_recipe()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.recipe_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.recipe_service.recipe_repository"
    ) as mock_recipe_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_recipe_repo.get_by_id.return_value = mock_recipe
        mock_restaurant_repo.get_user_restaurant_role.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/recipes/{mock_recipe.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestRecipeAPI]: test_get_recipe_no_access - PASSED")


# ============================================================================
# Update Recipe Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_recipe_success() -> None:
    """Test that authorized user can update recipe."""
    mock_user = create_mock_user()
    mock_recipe = create_mock_recipe()
    mock_item = create_mock_recipe_item(recipe_id=mock_recipe.id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.recipe_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.recipe_service.recipe_repository"
    ) as mock_recipe_repo, patch(
        "src.core.services.recipe_service.resource_repository"
    ) as mock_resource_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_recipe_repo.get_by_id.return_value = mock_recipe
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_recipe_repo.update.return_value = mock_recipe
        mock_recipe_repo.get_items.return_value = [mock_item]
        mock_resource_repo.get_by_id.return_value = create_mock_resource()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.put(
                f"/api/recipes/{mock_recipe.id}",
                json={"name": "Updated Recipe"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        print("INFO [TestRecipeAPI]: test_update_recipe_success - PASSED")


@pytest.mark.asyncio
async def test_update_recipe_with_items() -> None:
    """Test that updating recipe items replaces existing items."""
    mock_user = create_mock_user()
    mock_recipe = create_mock_recipe()
    new_resource_id = uuid4()
    mock_item = create_mock_recipe_item(recipe_id=mock_recipe.id, resource_id=new_resource_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.recipe_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.recipe_service.recipe_repository"
    ) as mock_recipe_repo, patch(
        "src.core.services.recipe_service.resource_repository"
    ) as mock_resource_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_recipe_repo.get_by_id.return_value = mock_recipe
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_recipe_repo.update.return_value = mock_recipe
        mock_recipe_repo.replace_items.return_value = [mock_item]
        mock_recipe_repo.get_items.return_value = [mock_item]
        mock_resource_repo.get_by_id.return_value = create_mock_resource()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.put(
                f"/api/recipes/{mock_recipe.id}",
                json={
                    "items": [
                        {
                            "resource_id": str(new_resource_id),
                            "quantity": "3.0",
                            "unit": "litros",
                        }
                    ],
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        mock_recipe_repo.replace_items.assert_called_once()
        print("INFO [TestRecipeAPI]: test_update_recipe_with_items - PASSED")


@pytest.mark.asyncio
async def test_update_recipe_not_found() -> None:
    """Test that updating nonexistent recipe returns 404."""
    mock_user = create_mock_user()
    recipe_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.recipe_service.recipe_repository"
    ) as mock_recipe_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_recipe_repo.get_by_id.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.put(
                f"/api/recipes/{recipe_id}",
                json={"name": "Updated"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        print("INFO [TestRecipeAPI]: test_update_recipe_not_found - PASSED")


# ============================================================================
# Delete Recipe Tests
# ============================================================================


@pytest.mark.asyncio
async def test_delete_recipe_success() -> None:
    """Test that authorized user can delete recipe."""
    mock_user = create_mock_user()
    mock_recipe = create_mock_recipe()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.recipe_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.recipe_service.recipe_repository"
    ) as mock_recipe_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_recipe_repo.get_by_id.return_value = mock_recipe
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_recipe_repo.delete.return_value = True

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.delete(
                f"/api/recipes/{mock_recipe.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 204
        print("INFO [TestRecipeAPI]: test_delete_recipe_success - PASSED")


@pytest.mark.asyncio
async def test_delete_recipe_not_found() -> None:
    """Test that deleting nonexistent recipe returns 404."""
    mock_user = create_mock_user()
    recipe_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.recipe_service.recipe_repository"
    ) as mock_recipe_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_recipe_repo.get_by_id.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.delete(
                f"/api/recipes/{recipe_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        print("INFO [TestRecipeAPI]: test_delete_recipe_not_found - PASSED")


# ============================================================================
# Recalculate Cost Tests
# ============================================================================


@pytest.mark.asyncio
async def test_recalculate_cost_success() -> None:
    """Test that recalculate endpoint returns correct cost computation."""
    mock_user = create_mock_user()
    mock_recipe = create_mock_recipe(sale_price=Decimal("25.00"))
    resource_id = uuid4()
    mock_item = create_mock_recipe_item(
        recipe_id=mock_recipe.id,
        resource_id=resource_id,
        quantity=Decimal("2.0"),
    )
    mock_resource = create_mock_resource(last_unit_cost=Decimal("4.00"))
    mock_resource.id = resource_id

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.recipe_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.recipe_service.recipe_repository"
    ) as mock_recipe_repo, patch(
        "src.core.services.recipe_service.resource_repository"
    ) as mock_resource_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_recipe_repo.get_by_id.return_value = mock_recipe
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_recipe_repo.get_items.return_value = [mock_item]
        mock_resource_repo.get_by_id.return_value = mock_resource

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                f"/api/recipes/{mock_recipe.id}/recalculate",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert "current_cost" in data
        assert "margin_percent" in data
        assert "is_profitable" in data
        print("INFO [TestRecipeAPI]: test_recalculate_cost_success - PASSED")


@pytest.mark.asyncio
async def test_recalculate_cost_not_found() -> None:
    """Test that recalculating nonexistent recipe returns 404."""
    mock_user = create_mock_user()
    recipe_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.recipe_service.recipe_repository"
    ) as mock_recipe_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_recipe_repo.get_by_id.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                f"/api/recipes/{recipe_id}/recalculate",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        print("INFO [TestRecipeAPI]: test_recalculate_cost_not_found - PASSED")
