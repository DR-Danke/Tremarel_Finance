"""Tests for recurring template endpoints."""

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
from src.models.recurring_template import RecurringTemplate
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


def create_mock_recurring_template(
    entity_id=None,
    category_id=None,
    name="Test Template",
    amount=Decimal("100.00"),
    template_type="expense",
    frequency="monthly",
    start_date=None,
    end_date=None,
    is_active=True,
    description="Test template description",
    notes=None,
):
    """Create a mock recurring template for testing."""
    mock_template = MagicMock(spec=RecurringTemplate)
    mock_template.id = uuid4()
    mock_template.entity_id = entity_id or uuid4()
    mock_template.category_id = category_id or uuid4()
    mock_template.name = name
    mock_template.amount = amount
    mock_template.type = template_type
    mock_template.frequency = frequency
    mock_template.start_date = start_date or date.today()
    mock_template.end_date = end_date
    mock_template.is_active = is_active
    mock_template.description = description
    mock_template.notes = notes
    mock_template.created_at = "2024-01-01T00:00:00Z"
    mock_template.updated_at = None
    return mock_template


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
# Create Recurring Template Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_recurring_template_success() -> None:
    """Test successful recurring template creation."""
    from datetime import datetime

    mock_user = create_mock_user()
    entity_id = uuid4()
    category_id = uuid4()
    template_id = uuid4()
    mock_template = create_mock_recurring_template(
        entity_id=entity_id,
        category_id=category_id,
    )
    mock_template.id = template_id
    mock_template.created_at = datetime.now()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.recurring_template_service.recurring_template_repository"
        ) as mock_template_repo:
            # Setup auth mocks
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            # Setup template repository mock
            mock_template_repo.create_template.return_value = mock_template

            # Login to get token
            token = await get_auth_token(client, mock_user)

            # Create template
            response = await client.post(
                "/api/recurring-templates/",
                json={
                    "entity_id": str(entity_id),
                    "category_id": str(category_id),
                    "name": "Netflix Subscription",
                    "amount": "15.99",
                    "type": "expense",
                    "frequency": "monthly",
                    "start_date": str(date.today()),
                    "description": "Monthly streaming service",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["type"] == "expense"
    assert data["frequency"] == "monthly"
    print("INFO [TestRecurringTemplates]: test_create_recurring_template_success - PASSED")


@pytest.mark.asyncio
async def test_create_recurring_template_invalid_frequency() -> None:
    """Test that invalid frequency returns 422."""
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
                "/api/recurring-templates/",
                json={
                    "entity_id": str(uuid4()),
                    "category_id": str(uuid4()),
                    "name": "Test Template",
                    "amount": "50.00",
                    "type": "expense",
                    "frequency": "biweekly",  # Invalid frequency
                    "start_date": str(date.today()),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 422
    print("INFO [TestRecurringTemplates]: test_create_recurring_template_invalid_frequency - PASSED")


@pytest.mark.asyncio
async def test_create_recurring_template_negative_amount() -> None:
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
                "/api/recurring-templates/",
                json={
                    "entity_id": str(uuid4()),
                    "category_id": str(uuid4()),
                    "name": "Test Template",
                    "amount": "-50.00",  # Negative amount
                    "type": "expense",
                    "frequency": "monthly",
                    "start_date": str(date.today()),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 422
    print("INFO [TestRecurringTemplates]: test_create_recurring_template_negative_amount - PASSED")


# ============================================================================
# List Recurring Template Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_recurring_templates_empty() -> None:
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
            "src.core.services.recurring_template_service.recurring_template_repository"
        ) as mock_template_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_template_repo.get_templates_by_entity.return_value = []
            mock_template_repo.count_templates_by_entity.return_value = 0

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/recurring-templates/?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["templates"] == []
    assert data["total"] == 0
    print("INFO [TestRecurringTemplates]: test_list_recurring_templates_empty - PASSED")


@pytest.mark.asyncio
async def test_list_recurring_templates_with_data() -> None:
    """Test list returns templates for entity."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_template = create_mock_recurring_template(
        entity_id=entity_id,
        name="Monthly Rent",
        frequency="monthly",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.recurring_template_service.recurring_template_repository"
        ) as mock_template_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_template_repo.get_templates_by_entity.return_value = [mock_template]
            mock_template_repo.count_templates_by_entity.return_value = 1

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/recurring-templates/?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert len(data["templates"]) == 1
    assert data["total"] == 1
    print("INFO [TestRecurringTemplates]: test_list_recurring_templates_with_data - PASSED")


# ============================================================================
# Get Single Recurring Template Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_recurring_template_not_found() -> None:
    """Test 404 for non-existent template."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    template_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.recurring_template_service.recurring_template_repository"
        ) as mock_template_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_template_repo.get_template_by_id.return_value = None

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/recurring-templates/{template_id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 404
    print("INFO [TestRecurringTemplates]: test_get_recurring_template_not_found - PASSED")


# ============================================================================
# Update Recurring Template Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_recurring_template_success() -> None:
    """Test update existing recurring template."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_template = create_mock_recurring_template(
        entity_id=entity_id,
        amount=Decimal("100.00"),
    )
    updated_template = create_mock_recurring_template(
        entity_id=entity_id,
        amount=Decimal("75.00"),
    )
    updated_template.id = mock_template.id

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.recurring_template_service.recurring_template_repository"
        ) as mock_template_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_template_repo.get_template_by_id.return_value = mock_template
            mock_template_repo.update_template.return_value = updated_template

            token = await get_auth_token(client, mock_user)

            response = await client.put(
                f"/api/recurring-templates/{mock_template.id}?entity_id={entity_id}",
                json={"amount": "75.00"},
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    print("INFO [TestRecurringTemplates]: test_update_recurring_template_success - PASSED")


# ============================================================================
# Deactivate Recurring Template Tests
# ============================================================================


@pytest.mark.asyncio
async def test_deactivate_recurring_template_success() -> None:
    """Test deactivate (soft delete) recurring template."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_template = create_mock_recurring_template(
        entity_id=entity_id,
        is_active=True,
    )
    deactivated_template = create_mock_recurring_template(
        entity_id=entity_id,
        is_active=False,
    )
    deactivated_template.id = mock_template.id

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.recurring_template_service.recurring_template_repository"
        ) as mock_template_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_template_repo.get_template_by_id.return_value = mock_template
            mock_template_repo.deactivate_template.return_value = deactivated_template

            token = await get_auth_token(client, mock_user)

            response = await client.post(
                f"/api/recurring-templates/{mock_template.id}/deactivate?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False
    print("INFO [TestRecurringTemplates]: test_deactivate_recurring_template_success - PASSED")


# ============================================================================
# Delete Recurring Template Tests
# ============================================================================


@pytest.mark.asyncio
async def test_delete_recurring_template_success() -> None:
    """Test delete recurring template as admin."""
    mock_admin = create_mock_user(email="admin@example.com", role="admin")
    entity_id = uuid4()
    mock_template = create_mock_recurring_template(entity_id=entity_id)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.recurring_template_service.recurring_template_repository"
        ) as mock_template_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_admin
            mock_auth_repo.get_user_by_id.return_value = mock_admin
            mock_bcrypt.checkpw.return_value = True

            mock_template_repo.get_template_by_id.return_value = mock_template
            mock_template_repo.delete_template.return_value = None

            token = await get_auth_token(client, mock_admin)

            response = await client.delete(
                f"/api/recurring-templates/{mock_template.id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 204
    print("INFO [TestRecurringTemplates]: test_delete_recurring_template_success - PASSED")


@pytest.mark.asyncio
async def test_delete_recurring_template_forbidden() -> None:
    """Test 403 for regular user delete."""
    mock_user = create_mock_user(role="user")  # Regular user, not admin/manager
    entity_id = uuid4()
    template_id = uuid4()

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
                f"/api/recurring-templates/{template_id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 403
    print("INFO [TestRecurringTemplates]: test_delete_recurring_template_forbidden - PASSED")


# ============================================================================
# Authentication Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_recurring_template_no_auth() -> None:
    """Test that unauthenticated request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/recurring-templates/",
            json={
                "entity_id": str(uuid4()),
                "category_id": str(uuid4()),
                "name": "Test Template",
                "amount": "50.00",
                "type": "expense",
                "frequency": "monthly",
                "start_date": str(date.today()),
            },
        )

    assert response.status_code == 401
    print("INFO [TestRecurringTemplates]: test_create_recurring_template_no_auth - PASSED")
