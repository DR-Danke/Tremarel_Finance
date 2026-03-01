"""Tests for prospect API endpoints."""

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
from src.models.pipeline_stage import PipelineStage
from src.models.prospect import Prospect
from src.models.stage_transition import StageTransition
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


def create_mock_prospect(
    entity_id=None,
    company_name="Acme Corp",
    contact_name="John Doe",
    contact_email="john@acme.com",
    contact_phone="+1234567890",
    stage="lead",
    estimated_value=Decimal("10000.00"),
    source="website",
    notes="Potential client",
    is_active=True,
):
    """Create a mock prospect for testing."""
    mock_prospect = MagicMock(spec=Prospect)
    mock_prospect.id = uuid4()
    mock_prospect.entity_id = entity_id or uuid4()
    mock_prospect.company_name = company_name
    mock_prospect.contact_name = contact_name
    mock_prospect.contact_email = contact_email
    mock_prospect.contact_phone = contact_phone
    mock_prospect.stage = stage
    mock_prospect.estimated_value = estimated_value
    mock_prospect.source = source
    mock_prospect.notes = notes
    mock_prospect.is_active = is_active
    mock_prospect.created_at = datetime(2026, 2, 1, 12, 0, 0)
    mock_prospect.updated_at = None
    return mock_prospect


def create_mock_pipeline_stage(entity_id=None, name="lead"):
    """Create a mock pipeline stage for testing."""
    mock_stage = MagicMock(spec=PipelineStage)
    mock_stage.id = uuid4()
    mock_stage.entity_id = entity_id or uuid4()
    mock_stage.name = name
    return mock_stage


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
# Create Prospect Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_prospect_success() -> None:
    """Test successful prospect creation."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_prospect = create_mock_prospect(entity_id=entity_id)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.prospect_service.prospect_repository"
        ) as mock_prospect_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_prospect_repo.create_prospect.return_value = mock_prospect

            token = await get_auth_token(client, mock_user)

            response = await client.post(
                "/api/prospects/",
                json={
                    "entity_id": str(entity_id),
                    "company_name": "Acme Corp",
                    "contact_name": "John Doe",
                    "contact_email": "john@acme.com",
                    "contact_phone": "+1234567890",
                    "stage": "lead",
                    "estimated_value": "10000.00",
                    "source": "website",
                    "notes": "Potential client",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["company_name"] == "Acme Corp"
    assert data["stage"] == "lead"
    print("INFO [TestProspectAPI]: test_create_prospect_success - PASSED")


@pytest.mark.asyncio
async def test_create_prospect_validation_error() -> None:
    """Test that missing required fields returns 422."""
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
                "/api/prospects/",
                json={
                    "entity_id": str(uuid4()),
                    # Missing company_name (required)
                },
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 422
    print("INFO [TestProspectAPI]: test_create_prospect_validation_error - PASSED")


# ============================================================================
# List Prospects Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_prospects_success() -> None:
    """Test list prospects for an entity."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_prospect = create_mock_prospect(entity_id=entity_id)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.prospect_service.prospect_repository"
        ) as mock_prospect_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_prospect_repo.get_prospects_by_entity.return_value = [mock_prospect]
            mock_prospect_repo.count_prospects_by_entity.return_value = 1

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/prospects/?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert len(data["prospects"]) == 1
    assert data["total"] == 1
    print("INFO [TestProspectAPI]: test_list_prospects_success - PASSED")


@pytest.mark.asyncio
async def test_list_prospects_with_filters() -> None:
    """Test list prospects with stage, is_active, and source filters."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_prospect = create_mock_prospect(entity_id=entity_id, stage="qualified", source="referral")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.prospect_service.prospect_repository"
        ) as mock_prospect_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_prospect_repo.get_prospects_by_entity.return_value = [mock_prospect]
            mock_prospect_repo.count_prospects_by_entity.return_value = 1

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/prospects/?entity_id={entity_id}&stage=qualified&is_active=true&source=referral",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert len(data["prospects"]) == 1
    assert data["prospects"][0]["stage"] == "qualified"
    print("INFO [TestProspectAPI]: test_list_prospects_with_filters - PASSED")


# ============================================================================
# Get Single Prospect Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_prospect_success() -> None:
    """Test get a single prospect by ID."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_prospect = create_mock_prospect(entity_id=entity_id)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.prospect_service.prospect_repository"
        ) as mock_prospect_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_prospect_repo.get_prospect_by_id.return_value = mock_prospect

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/prospects/{mock_prospect.id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["company_name"] == "Acme Corp"
    print("INFO [TestProspectAPI]: test_get_prospect_success - PASSED")


@pytest.mark.asyncio
async def test_get_prospect_not_found() -> None:
    """Test 404 for non-existent prospect."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    prospect_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.prospect_service.prospect_repository"
        ) as mock_prospect_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_prospect_repo.get_prospect_by_id.return_value = None

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/prospects/{prospect_id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 404
    print("INFO [TestProspectAPI]: test_get_prospect_not_found - PASSED")


# ============================================================================
# Update Prospect Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_prospect_success() -> None:
    """Test update existing prospect."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_prospect = create_mock_prospect(entity_id=entity_id)
    updated_prospect = create_mock_prospect(
        entity_id=entity_id, company_name="Acme Corp Updated", stage="contacted"
    )
    updated_prospect.id = mock_prospect.id

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.prospect_service.prospect_repository"
        ) as mock_prospect_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_prospect_repo.get_prospect_by_id.return_value = mock_prospect
            mock_prospect_repo.update_prospect.return_value = updated_prospect

            token = await get_auth_token(client, mock_user)

            response = await client.put(
                f"/api/prospects/{mock_prospect.id}?entity_id={entity_id}",
                json={"company_name": "Acme Corp Updated", "stage": "contacted"},
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    print("INFO [TestProspectAPI]: test_update_prospect_success - PASSED")


@pytest.mark.asyncio
async def test_update_prospect_not_found() -> None:
    """Test 404 for updating non-existent prospect."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    prospect_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.prospect_service.prospect_repository"
        ) as mock_prospect_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_prospect_repo.get_prospect_by_id.return_value = None

            token = await get_auth_token(client, mock_user)

            response = await client.put(
                f"/api/prospects/{prospect_id}?entity_id={entity_id}",
                json={"company_name": "Updated"},
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 404
    print("INFO [TestProspectAPI]: test_update_prospect_not_found - PASSED")


# ============================================================================
# Stage Update Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_prospect_stage_success() -> None:
    """Test updating prospect stage with audit trail."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_prospect = create_mock_prospect(entity_id=entity_id, stage="lead")
    updated_prospect = create_mock_prospect(entity_id=entity_id, stage="qualified")
    updated_prospect.id = mock_prospect.id

    old_stage = create_mock_pipeline_stage(entity_id=entity_id, name="lead")
    new_stage = create_mock_pipeline_stage(entity_id=entity_id, name="qualified")

    mock_transition = MagicMock(spec=StageTransition)
    mock_transition.id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.prospect_service.prospect_repository"
        ) as mock_prospect_repo, patch(
            "src.core.services.prospect_service.pipeline_stage_repository"
        ) as mock_stage_repo, patch(
            "src.core.services.prospect_service.stage_transition_repository"
        ) as mock_trans_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_prospect_repo.get_prospect_by_id.return_value = mock_prospect
            mock_prospect_repo.update_prospect.return_value = updated_prospect
            mock_stage_repo.get_stage_by_name.side_effect = [old_stage, new_stage]
            mock_trans_repo.create_transition.return_value = mock_transition

            token = await get_auth_token(client, mock_user)

            response = await client.patch(
                f"/api/prospects/{mock_prospect.id}/stage?entity_id={entity_id}",
                json={"new_stage": "qualified", "notes": "Moving to qualified"},
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["stage"] == "qualified"
    mock_trans_repo.create_transition.assert_called_once()
    print("INFO [TestProspectAPI]: test_update_prospect_stage_success - PASSED")


@pytest.mark.asyncio
async def test_update_prospect_stage_not_found() -> None:
    """Test 404 for updating stage of non-existent prospect."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    prospect_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.prospect_service.prospect_repository"
        ) as mock_prospect_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_prospect_repo.get_prospect_by_id.return_value = None

            token = await get_auth_token(client, mock_user)

            response = await client.patch(
                f"/api/prospects/{prospect_id}/stage?entity_id={entity_id}",
                json={"new_stage": "qualified"},
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 404
    print("INFO [TestProspectAPI]: test_update_prospect_stage_not_found - PASSED")


# ============================================================================
# Delete Prospect Tests
# ============================================================================


@pytest.mark.asyncio
async def test_delete_prospect_success() -> None:
    """Test delete prospect as admin."""
    mock_admin = create_mock_user(email="admin@example.com", role="admin")
    entity_id = uuid4()
    mock_prospect = create_mock_prospect(entity_id=entity_id)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.prospect_service.prospect_repository"
        ) as mock_prospect_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_admin
            mock_auth_repo.get_user_by_id.return_value = mock_admin
            mock_bcrypt.checkpw.return_value = True

            mock_prospect_repo.get_prospect_by_id.return_value = mock_prospect
            mock_prospect_repo.delete_prospect.return_value = None

            token = await get_auth_token(client, mock_admin)

            response = await client.delete(
                f"/api/prospects/{mock_prospect.id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 204
    print("INFO [TestProspectAPI]: test_delete_prospect_success - PASSED")


@pytest.mark.asyncio
async def test_delete_prospect_not_found() -> None:
    """Test 404 for deleting non-existent prospect."""
    mock_admin = create_mock_user(email="admin@example.com", role="admin")
    entity_id = uuid4()
    prospect_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.prospect_service.prospect_repository"
        ) as mock_prospect_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_admin
            mock_auth_repo.get_user_by_id.return_value = mock_admin
            mock_bcrypt.checkpw.return_value = True

            mock_prospect_repo.get_prospect_by_id.return_value = None

            token = await get_auth_token(client, mock_admin)

            response = await client.delete(
                f"/api/prospects/{prospect_id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 404
    print("INFO [TestProspectAPI]: test_delete_prospect_not_found - PASSED")


@pytest.mark.asyncio
async def test_delete_prospect_forbidden() -> None:
    """Test 403 for non-admin/manager user trying to delete."""
    mock_user = create_mock_user(email="viewer@example.com", role="viewer")
    entity_id = uuid4()
    prospect_id = uuid4()

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
                f"/api/prospects/{prospect_id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 403
    print("INFO [TestProspectAPI]: test_delete_prospect_forbidden - PASSED")


# ============================================================================
# Authentication Tests
# ============================================================================


@pytest.mark.asyncio
async def test_unauthenticated_request() -> None:
    """Test that unauthenticated request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/prospects/",
            json={
                "entity_id": str(uuid4()),
                "company_name": "Test Corp",
            },
        )

    assert response.status_code in (401, 403)
    print("INFO [TestProspectAPI]: test_unauthenticated_request - PASSED")
