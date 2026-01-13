"""Tests for budget endpoints."""

from datetime import date
from decimal import Decimal
from typing import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from main import app
from src.adapter.rest.dependencies import get_db
from src.models.budget import Budget
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
    entity_id=None,
    name="Test Category",
    category_type="expense",
    is_active=True,
) -> Category:
    """Create a mock category for testing."""
    mock_category = MagicMock(spec=Category)
    mock_category.id = uuid4()
    mock_category.entity_id = entity_id or uuid4()
    mock_category.name = name
    mock_category.type = category_type
    mock_category.is_active = is_active
    mock_category.parent_id = None
    mock_category.description = None
    mock_category.color = None
    mock_category.icon = None
    mock_category.created_at = "2024-01-01T00:00:00Z"
    mock_category.updated_at = None
    return mock_category


def create_mock_budget(
    entity_id=None,
    category_id=None,
    amount=Decimal("500.00"),
    period_type="monthly",
    start_date=None,
    end_date=None,
    is_active=True,
) -> Budget:
    """Create a mock budget for testing."""
    mock_budget = MagicMock(spec=Budget)
    mock_budget.id = uuid4()
    mock_budget.entity_id = entity_id or uuid4()
    mock_budget.category_id = category_id or uuid4()
    mock_budget.amount = amount
    mock_budget.period_type = period_type
    mock_budget.start_date = start_date or date.today().replace(day=1)
    mock_budget.end_date = end_date or date.today().replace(day=28)
    mock_budget.is_active = is_active
    mock_budget.created_at = "2024-01-01T00:00:00Z"
    mock_budget.updated_at = None
    return mock_budget


async def get_auth_token(client: AsyncClient, mock_user: User) -> str:
    """Helper to get auth token for a mocked user."""
    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_repo, patch(
        "src.core.services.auth_service.pwd_context"
    ) as mock_pwd_context:
        mock_repo.get_user_by_email.return_value = mock_user
        mock_pwd_context.verify.return_value = True

        response = await client.post(
            "/api/auth/login",
            json={"email": mock_user.email, "password": "password123"},
        )
        return response.json()["access_token"]


# ============================================================================
# Create Budget Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_budget_success() -> None:
    """Test successful budget creation."""
    from datetime import datetime

    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_category = create_mock_category(entity_id=entity_id, category_type="expense")
    mock_budget = create_mock_budget(
        entity_id=entity_id,
        category_id=mock_category.id,
    )
    mock_budget.created_at = datetime.now()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context, patch(
            "src.core.services.budget_service.category_repository"
        ) as mock_cat_repo, patch(
            "src.core.services.budget_service.budget_repository"
        ) as mock_budget_repo:
            # Setup auth mocks
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            # Setup category and budget mocks
            mock_cat_repo.get_category_by_id.return_value = mock_category
            mock_budget_repo.check_duplicate_budget.return_value = False
            mock_budget_repo.create_budget.return_value = mock_budget

            # Login to get token
            token = await get_auth_token(client, mock_user)

            # Create budget
            response = await client.post(
                "/api/budgets/",
                json={
                    "entity_id": str(entity_id),
                    "category_id": str(mock_category.id),
                    "amount": "500.00",
                    "period_type": "monthly",
                    "start_date": str(date.today().replace(day=1)),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["period_type"] == "monthly"
    print("INFO [TestBudgets]: test_create_budget_success - PASSED")


@pytest.mark.asyncio
async def test_create_budget_invalid_category_type() -> None:
    """Test that budget creation fails for income category."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_category = create_mock_category(entity_id=entity_id, category_type="income")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context, patch(
            "src.core.services.budget_service.category_repository"
        ) as mock_cat_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True
            mock_cat_repo.get_category_by_id.return_value = mock_category

            token = await get_auth_token(client, mock_user)

            response = await client.post(
                "/api/budgets/",
                json={
                    "entity_id": str(entity_id),
                    "category_id": str(mock_category.id),
                    "amount": "500.00",
                    "period_type": "monthly",
                    "start_date": str(date.today().replace(day=1)),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 400
    assert "expense" in response.json()["detail"].lower()
    print("INFO [TestBudgets]: test_create_budget_invalid_category_type - PASSED")


@pytest.mark.asyncio
async def test_create_budget_duplicate() -> None:
    """Test that duplicate budget creation fails."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_category = create_mock_category(entity_id=entity_id, category_type="expense")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context, patch(
            "src.core.services.budget_service.category_repository"
        ) as mock_cat_repo, patch(
            "src.core.services.budget_service.budget_repository"
        ) as mock_budget_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True
            mock_cat_repo.get_category_by_id.return_value = mock_category
            mock_budget_repo.check_duplicate_budget.return_value = True

            token = await get_auth_token(client, mock_user)

            response = await client.post(
                "/api/budgets/",
                json={
                    "entity_id": str(entity_id),
                    "category_id": str(mock_category.id),
                    "amount": "500.00",
                    "period_type": "monthly",
                    "start_date": str(date.today().replace(day=1)),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()
    print("INFO [TestBudgets]: test_create_budget_duplicate - PASSED")


@pytest.mark.asyncio
async def test_create_budget_negative_amount() -> None:
    """Test that negative amount returns 422."""
    mock_user = create_mock_user()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            token = await get_auth_token(client, mock_user)

            response = await client.post(
                "/api/budgets/",
                json={
                    "entity_id": str(uuid4()),
                    "category_id": str(uuid4()),
                    "amount": "-500.00",
                    "period_type": "monthly",
                    "start_date": str(date.today().replace(day=1)),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 422
    print("INFO [TestBudgets]: test_create_budget_negative_amount - PASSED")


@pytest.mark.asyncio
async def test_create_budget_invalid_period_type() -> None:
    """Test that invalid period type returns 422."""
    mock_user = create_mock_user()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            token = await get_auth_token(client, mock_user)

            response = await client.post(
                "/api/budgets/",
                json={
                    "entity_id": str(uuid4()),
                    "category_id": str(uuid4()),
                    "amount": "500.00",
                    "period_type": "weekly",  # Invalid
                    "start_date": str(date.today().replace(day=1)),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 422
    print("INFO [TestBudgets]: test_create_budget_invalid_period_type - PASSED")


# ============================================================================
# List Budget Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_budgets_empty() -> None:
    """Test list returns empty for new entity."""
    mock_user = create_mock_user()
    entity_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context, patch(
            "src.core.services.budget_service.budget_repository"
        ) as mock_budget_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            mock_budget_repo.get_budgets_by_entity.return_value = []
            mock_budget_repo.count_budgets_by_entity.return_value = 0

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/budgets/?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["budgets"] == []
    assert data["total"] == 0
    print("INFO [TestBudgets]: test_list_budgets_empty - PASSED")


@pytest.mark.asyncio
async def test_list_budgets_with_spending() -> None:
    """Test list returns budgets with spending calculation."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    category_id = uuid4()
    mock_budget = create_mock_budget(entity_id=entity_id, category_id=category_id)
    mock_category = create_mock_category(entity_id=entity_id, name="Food")
    mock_category.id = category_id

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context, patch(
            "src.core.services.budget_service.budget_repository"
        ) as mock_budget_repo, patch(
            "src.core.services.budget_service.category_repository"
        ) as mock_cat_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            mock_budget_repo.get_budgets_by_entity.return_value = [mock_budget]
            mock_budget_repo.count_budgets_by_entity.return_value = 1
            mock_budget_repo.calculate_spending.return_value = Decimal("150.00")
            mock_cat_repo.get_category_by_id.return_value = mock_category

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/budgets/?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert len(data["budgets"]) == 1
    assert data["total"] == 1
    print("INFO [TestBudgets]: test_list_budgets_with_spending - PASSED")


# ============================================================================
# Get Single Budget Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_budget_not_found() -> None:
    """Test 404 for non-existent budget."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    budget_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context, patch(
            "src.core.services.budget_service.budget_repository"
        ) as mock_budget_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            mock_budget_repo.get_budget_by_id.return_value = None

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/budgets/{budget_id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 404
    print("INFO [TestBudgets]: test_get_budget_not_found - PASSED")


# ============================================================================
# Update Budget Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_budget_success() -> None:
    """Test update existing budget."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_budget = create_mock_budget(
        entity_id=entity_id,
        amount=Decimal("500.00"),
    )
    updated_budget = create_mock_budget(
        entity_id=entity_id,
        amount=Decimal("600.00"),
    )
    updated_budget.id = mock_budget.id

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context, patch(
            "src.core.services.budget_service.budget_repository"
        ) as mock_budget_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            mock_budget_repo.get_budget_by_id.return_value = mock_budget
            mock_budget_repo.update_budget.return_value = updated_budget

            token = await get_auth_token(client, mock_user)

            response = await client.put(
                f"/api/budgets/{mock_budget.id}?entity_id={entity_id}",
                json={"amount": "600.00"},
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    print("INFO [TestBudgets]: test_update_budget_success - PASSED")


@pytest.mark.asyncio
async def test_update_budget_wrong_entity() -> None:
    """Test 404 when budget belongs to different entity."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    other_entity_id = uuid4()
    mock_budget = create_mock_budget(entity_id=other_entity_id)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context, patch(
            "src.core.services.budget_service.budget_repository"
        ) as mock_budget_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            mock_budget_repo.get_budget_by_id.return_value = mock_budget

            token = await get_auth_token(client, mock_user)

            response = await client.put(
                f"/api/budgets/{mock_budget.id}?entity_id={entity_id}",
                json={"amount": "600.00"},
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 404
    print("INFO [TestBudgets]: test_update_budget_wrong_entity - PASSED")


# ============================================================================
# Delete Budget Tests
# ============================================================================


@pytest.mark.asyncio
async def test_delete_budget_success() -> None:
    """Test delete budget as admin."""
    mock_admin = create_mock_user(email="admin@example.com", role="admin")
    entity_id = uuid4()
    mock_budget = create_mock_budget(entity_id=entity_id)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context, patch(
            "src.core.services.budget_service.budget_repository"
        ) as mock_budget_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_admin
            mock_auth_repo.get_user_by_id.return_value = mock_admin
            mock_pwd_context.verify.return_value = True

            mock_budget_repo.get_budget_by_id.return_value = mock_budget
            mock_budget_repo.delete_budget.return_value = None

            token = await get_auth_token(client, mock_admin)

            response = await client.delete(
                f"/api/budgets/{mock_budget.id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 204
    print("INFO [TestBudgets]: test_delete_budget_success - PASSED")


@pytest.mark.asyncio
async def test_delete_budget_as_manager() -> None:
    """Test delete budget as manager."""
    mock_manager = create_mock_user(email="manager@example.com", role="manager")
    entity_id = uuid4()
    mock_budget = create_mock_budget(entity_id=entity_id)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context, patch(
            "src.core.services.budget_service.budget_repository"
        ) as mock_budget_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_manager
            mock_auth_repo.get_user_by_id.return_value = mock_manager
            mock_pwd_context.verify.return_value = True

            mock_budget_repo.get_budget_by_id.return_value = mock_budget
            mock_budget_repo.delete_budget.return_value = None

            token = await get_auth_token(client, mock_manager)

            response = await client.delete(
                f"/api/budgets/{mock_budget.id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 204
    print("INFO [TestBudgets]: test_delete_budget_as_manager - PASSED")


@pytest.mark.asyncio
async def test_delete_budget_forbidden() -> None:
    """Test 403 for regular user delete."""
    mock_user = create_mock_user(role="user")
    entity_id = uuid4()
    budget_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.pwd_context"
        ) as mock_pwd_context:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_pwd_context.verify.return_value = True

            token = await get_auth_token(client, mock_user)

            response = await client.delete(
                f"/api/budgets/{budget_id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 403
    print("INFO [TestBudgets]: test_delete_budget_forbidden - PASSED")


# ============================================================================
# Authentication Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_budget_no_auth() -> None:
    """Test that unauthenticated request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/budgets/",
            json={
                "entity_id": str(uuid4()),
                "category_id": str(uuid4()),
                "amount": "500.00",
                "period_type": "monthly",
                "start_date": str(date.today().replace(day=1)),
            },
        )

    assert response.status_code == 401
    print("INFO [TestBudgets]: test_create_budget_no_auth - PASSED")
