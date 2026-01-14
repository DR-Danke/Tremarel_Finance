"""Tests for transaction endpoints."""

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
from src.models.transaction import Transaction
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


def create_mock_transaction(
    entity_id=None,
    category_id=None,
    user_id=None,
    recurring_template_id=None,
    amount=Decimal("100.00"),
    transaction_type="expense",
    description="Test transaction",
    transaction_date=None,
    notes=None,
):
    """Create a mock transaction for testing."""
    mock_transaction = MagicMock(spec=Transaction)
    mock_transaction.id = uuid4()
    mock_transaction.entity_id = entity_id or uuid4()
    mock_transaction.category_id = category_id or uuid4()
    mock_transaction.user_id = user_id
    mock_transaction.recurring_template_id = recurring_template_id
    mock_transaction.amount = amount
    mock_transaction.type = transaction_type
    mock_transaction.description = description
    mock_transaction.date = transaction_date or date.today()
    mock_transaction.notes = notes
    mock_transaction.created_at = "2024-01-01T00:00:00Z"
    mock_transaction.updated_at = None
    return mock_transaction


async def get_auth_token(client: AsyncClient, mock_user: User) -> str:
    """Helper to get auth token for a mocked user."""
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
# Create Transaction Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_transaction_success() -> None:
    """Test successful transaction creation."""
    from datetime import datetime

    mock_user = create_mock_user()
    entity_id = uuid4()
    category_id = uuid4()
    transaction_id = uuid4()
    mock_transaction = create_mock_transaction(
        entity_id=entity_id,
        category_id=category_id,
        user_id=mock_user.id,
    )
    # Ensure created_at is a proper datetime object
    mock_transaction.id = transaction_id
    mock_transaction.created_at = datetime.now()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.transaction_service.transaction_repository"
        ) as mock_trans_repo:
            # Setup auth mocks
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            # Setup transaction repository mock
            mock_trans_repo.create_transaction.return_value = mock_transaction

            # Login to get token
            token = await get_auth_token(client, mock_user)

            # Create transaction
            response = await client.post(
                "/api/transactions/",
                json={
                    "entity_id": str(entity_id),
                    "category_id": str(category_id),
                    "amount": "50.00",
                    "type": "expense",
                    "description": "Test expense",
                    "date": str(date.today()),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["type"] == "expense"
    print("INFO [TestTransactions]: test_create_transaction_success - PASSED")


@pytest.mark.asyncio
async def test_create_transaction_invalid_type() -> None:
    """Test that invalid transaction type returns 422."""
    mock_user = create_mock_user()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            token = await get_auth_token(client, mock_user)

            response = await client.post(
                "/api/transactions/",
                json={
                    "entity_id": str(uuid4()),
                    "category_id": str(uuid4()),
                    "amount": "50.00",
                    "type": "invalid_type",  # Invalid type
                    "description": "Test",
                    "date": str(date.today()),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 422
    print("INFO [TestTransactions]: test_create_transaction_invalid_type - PASSED")


@pytest.mark.asyncio
async def test_create_transaction_negative_amount() -> None:
    """Test that negative amount returns 422."""
    mock_user = create_mock_user()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            token = await get_auth_token(client, mock_user)

            response = await client.post(
                "/api/transactions/",
                json={
                    "entity_id": str(uuid4()),
                    "category_id": str(uuid4()),
                    "amount": "-50.00",  # Negative amount
                    "type": "expense",
                    "description": "Test",
                    "date": str(date.today()),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 422
    print("INFO [TestTransactions]: test_create_transaction_negative_amount - PASSED")


# ============================================================================
# List Transaction Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_transactions_empty() -> None:
    """Test list returns empty for new entity."""
    mock_user = create_mock_user()
    entity_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.transaction_service.transaction_repository"
        ) as mock_trans_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_trans_repo.get_transactions_by_entity.return_value = []
            mock_trans_repo.count_transactions_by_entity.return_value = 0

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/transactions/?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["transactions"] == []
    assert data["total"] == 0
    print("INFO [TestTransactions]: test_list_transactions_empty - PASSED")


@pytest.mark.asyncio
async def test_list_transactions_with_filters() -> None:
    """Test list with date and type filtering."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_transaction = create_mock_transaction(
        entity_id=entity_id,
        transaction_type="income",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.transaction_service.transaction_repository"
        ) as mock_trans_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_trans_repo.get_transactions_by_entity.return_value = [mock_transaction]
            mock_trans_repo.count_transactions_by_entity.return_value = 1

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/transactions/?entity_id={entity_id}&type=income&start_date=2024-01-01",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert len(data["transactions"]) == 1
    assert data["total"] == 1
    print("INFO [TestTransactions]: test_list_transactions_with_filters - PASSED")


# ============================================================================
# Get Single Transaction Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_transaction_not_found() -> None:
    """Test 404 for non-existent transaction."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    transaction_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.transaction_service.transaction_repository"
        ) as mock_trans_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_trans_repo.get_transaction_by_id.return_value = None

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/transactions/{transaction_id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 404
    print("INFO [TestTransactions]: test_get_transaction_not_found - PASSED")


# ============================================================================
# Update Transaction Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_transaction_success() -> None:
    """Test update existing transaction."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_transaction = create_mock_transaction(
        entity_id=entity_id,
        amount=Decimal("100.00"),
    )
    updated_transaction = create_mock_transaction(
        entity_id=entity_id,
        amount=Decimal("75.00"),
    )
    updated_transaction.id = mock_transaction.id

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.transaction_service.transaction_repository"
        ) as mock_trans_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_trans_repo.get_transaction_by_id.return_value = mock_transaction
            mock_trans_repo.update_transaction.return_value = updated_transaction

            token = await get_auth_token(client, mock_user)

            response = await client.put(
                f"/api/transactions/{mock_transaction.id}?entity_id={entity_id}",
                json={"amount": "75.00"},
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    print("INFO [TestTransactions]: test_update_transaction_success - PASSED")


# ============================================================================
# Delete Transaction Tests
# ============================================================================


@pytest.mark.asyncio
async def test_delete_transaction_success() -> None:
    """Test delete transaction as admin."""
    mock_admin = create_mock_user(email="admin@example.com", role="admin")
    entity_id = uuid4()
    mock_transaction = create_mock_transaction(entity_id=entity_id)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.transaction_service.transaction_repository"
        ) as mock_trans_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_admin
            mock_auth_repo.get_user_by_id.return_value = mock_admin
            mock_bcrypt.checkpw.return_value = True

            mock_trans_repo.get_transaction_by_id.return_value = mock_transaction
            mock_trans_repo.delete_transaction.return_value = None

            token = await get_auth_token(client, mock_admin)

            response = await client.delete(
                f"/api/transactions/{mock_transaction.id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 204
    print("INFO [TestTransactions]: test_delete_transaction_success - PASSED")


@pytest.mark.asyncio
async def test_delete_transaction_forbidden() -> None:
    """Test 403 for regular user delete."""
    mock_user = create_mock_user(role="user")  # Regular user, not admin/manager
    entity_id = uuid4()
    transaction_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            token = await get_auth_token(client, mock_user)

            response = await client.delete(
                f"/api/transactions/{transaction_id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 403
    print("INFO [TestTransactions]: test_delete_transaction_forbidden - PASSED")


# ============================================================================
# Authentication Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_transaction_no_auth() -> None:
    """Test that unauthenticated request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/transactions/",
            json={
                "entity_id": str(uuid4()),
                "category_id": str(uuid4()),
                "amount": "50.00",
                "type": "expense",
                "description": "Test",
                "date": str(date.today()),
            },
        )

    assert response.status_code == 401
    print("INFO [TestTransactions]: test_create_transaction_no_auth - PASSED")
