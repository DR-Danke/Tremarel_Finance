"""Tests for pipeline stage API endpoints."""

from datetime import datetime
from typing import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from main import app
from src.adapter.rest.dependencies import get_db
from src.models.pipeline_stage import PipelineStage
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


def create_mock_pipeline_stage(
    entity_id=None,
    name="lead",
    display_name="Lead",
    order_index=0,
    color="#90CAF9",
    is_default=True,
    is_active=True,
):
    """Create a mock pipeline stage for testing."""
    mock_stage = MagicMock(spec=PipelineStage)
    mock_stage.id = uuid4()
    mock_stage.entity_id = entity_id or uuid4()
    mock_stage.name = name
    mock_stage.display_name = display_name
    mock_stage.order_index = order_index
    mock_stage.color = color
    mock_stage.is_default = is_default
    mock_stage.is_active = is_active
    mock_stage.created_at = datetime(2026, 2, 1, 12, 0, 0)
    mock_stage.updated_at = None
    return mock_stage


def create_mock_transition(
    prospect_id=None,
    entity_id=None,
    from_stage_id=None,
    to_stage_id=None,
    transitioned_by=None,
    notes=None,
):
    """Create a mock stage transition for testing."""
    mock_transition = MagicMock(spec=StageTransition)
    mock_transition.id = uuid4()
    mock_transition.prospect_id = prospect_id or uuid4()
    mock_transition.entity_id = entity_id or uuid4()
    mock_transition.from_stage_id = from_stage_id
    mock_transition.to_stage_id = to_stage_id or uuid4()
    mock_transition.transitioned_by = transitioned_by
    mock_transition.notes = notes
    mock_transition.created_at = datetime(2026, 2, 1, 12, 0, 0)
    return mock_transition


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
# Create Pipeline Stage Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_pipeline_stage_success() -> None:
    """Test successful pipeline stage creation."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_stage = create_mock_pipeline_stage(entity_id=entity_id)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.pipeline_stage_service.pipeline_stage_repository"
        ) as mock_stage_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_stage_repo.create_stage.return_value = mock_stage

            token = await get_auth_token(client, mock_user)

            response = await client.post(
                "/api/pipeline-stages/",
                json={
                    "entity_id": str(entity_id),
                    "name": "lead",
                    "display_name": "Lead",
                    "order_index": 0,
                    "color": "#90CAF9",
                    "is_default": True,
                },
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "lead"
    assert data["display_name"] == "Lead"
    print("INFO [TestPipelineStageAPI]: test_create_pipeline_stage_success - PASSED")


@pytest.mark.asyncio
async def test_create_pipeline_stage_validation_error() -> None:
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
                "/api/pipeline-stages/",
                json={
                    "entity_id": str(uuid4()),
                    # Missing name, display_name, order_index
                },
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 422
    print("INFO [TestPipelineStageAPI]: test_create_pipeline_stage_validation_error - PASSED")


# ============================================================================
# List Pipeline Stages Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_pipeline_stages_success() -> None:
    """Test list pipeline stages for an entity."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_stage = create_mock_pipeline_stage(entity_id=entity_id)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.pipeline_stage_service.pipeline_stage_repository"
        ) as mock_stage_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_stage_repo.get_stages_by_entity.return_value = [mock_stage]
            mock_stage_repo.count_stages_by_entity.return_value = 1

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/pipeline-stages/?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert len(data["stages"]) == 1
    assert data["total"] == 1
    print("INFO [TestPipelineStageAPI]: test_list_pipeline_stages_success - PASSED")


# ============================================================================
# Get Single Pipeline Stage Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_pipeline_stage_success() -> None:
    """Test get a single pipeline stage by ID."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_stage = create_mock_pipeline_stage(entity_id=entity_id)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.pipeline_stage_service.pipeline_stage_repository"
        ) as mock_stage_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_stage_repo.get_stage_by_id.return_value = mock_stage

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/pipeline-stages/{mock_stage.id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "lead"
    print("INFO [TestPipelineStageAPI]: test_get_pipeline_stage_success - PASSED")


@pytest.mark.asyncio
async def test_get_pipeline_stage_not_found() -> None:
    """Test 404 for non-existent pipeline stage."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    stage_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.pipeline_stage_service.pipeline_stage_repository"
        ) as mock_stage_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_stage_repo.get_stage_by_id.return_value = None

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/pipeline-stages/{stage_id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 404
    print("INFO [TestPipelineStageAPI]: test_get_pipeline_stage_not_found - PASSED")


# ============================================================================
# Update Pipeline Stage Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_pipeline_stage_success() -> None:
    """Test update existing pipeline stage."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_stage = create_mock_pipeline_stage(entity_id=entity_id)
    updated_stage = create_mock_pipeline_stage(
        entity_id=entity_id,
        display_name="Updated Lead",
        color="#FF0000",
    )
    updated_stage.id = mock_stage.id

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.pipeline_stage_service.pipeline_stage_repository"
        ) as mock_stage_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_stage_repo.get_stage_by_id.return_value = mock_stage
            mock_stage_repo.update_stage.return_value = updated_stage

            token = await get_auth_token(client, mock_user)

            response = await client.put(
                f"/api/pipeline-stages/{mock_stage.id}?entity_id={entity_id}",
                json={"display_name": "Updated Lead", "color": "#FF0000"},
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    print("INFO [TestPipelineStageAPI]: test_update_pipeline_stage_success - PASSED")


@pytest.mark.asyncio
async def test_update_pipeline_stage_not_found() -> None:
    """Test 404 for updating non-existent pipeline stage."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    stage_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.pipeline_stage_service.pipeline_stage_repository"
        ) as mock_stage_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_stage_repo.get_stage_by_id.return_value = None

            token = await get_auth_token(client, mock_user)

            response = await client.put(
                f"/api/pipeline-stages/{stage_id}?entity_id={entity_id}",
                json={"display_name": "Updated"},
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 404
    print("INFO [TestPipelineStageAPI]: test_update_pipeline_stage_not_found - PASSED")


# ============================================================================
# Delete Pipeline Stage Tests
# ============================================================================


@pytest.mark.asyncio
async def test_delete_pipeline_stage_success() -> None:
    """Test delete pipeline stage as admin."""
    mock_admin = create_mock_user(email="admin@example.com", role="admin")
    entity_id = uuid4()
    mock_stage = create_mock_pipeline_stage(entity_id=entity_id)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.pipeline_stage_service.pipeline_stage_repository"
        ) as mock_stage_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_admin
            mock_auth_repo.get_user_by_id.return_value = mock_admin
            mock_bcrypt.checkpw.return_value = True

            mock_stage_repo.get_stage_by_id.return_value = mock_stage
            mock_stage_repo.delete_stage.return_value = None

            token = await get_auth_token(client, mock_admin)

            response = await client.delete(
                f"/api/pipeline-stages/{mock_stage.id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 204
    print("INFO [TestPipelineStageAPI]: test_delete_pipeline_stage_success - PASSED")


@pytest.mark.asyncio
async def test_delete_pipeline_stage_not_found() -> None:
    """Test 404 for deleting non-existent pipeline stage."""
    mock_admin = create_mock_user(email="admin@example.com", role="admin")
    entity_id = uuid4()
    stage_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.pipeline_stage_service.pipeline_stage_repository"
        ) as mock_stage_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_admin
            mock_auth_repo.get_user_by_id.return_value = mock_admin
            mock_bcrypt.checkpw.return_value = True

            mock_stage_repo.get_stage_by_id.return_value = None

            token = await get_auth_token(client, mock_admin)

            response = await client.delete(
                f"/api/pipeline-stages/{stage_id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 404
    print("INFO [TestPipelineStageAPI]: test_delete_pipeline_stage_not_found - PASSED")


# ============================================================================
# Seed Default Stages Tests
# ============================================================================


@pytest.mark.asyncio
async def test_seed_default_stages_success() -> None:
    """Test seeding default stages for an entity."""
    mock_admin = create_mock_user(email="admin@example.com", role="admin")
    entity_id = uuid4()

    # Create 7 mock stages for the seed response
    default_names = ["lead", "contacted", "qualified", "proposal", "negotiation", "won", "lost"]
    mock_stages = [
        create_mock_pipeline_stage(entity_id=entity_id, name=name, display_name=name.title(), order_index=i)
        for i, name in enumerate(default_names)
    ]

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.pipeline_stage_service.pipeline_stage_repository"
        ) as mock_stage_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_admin
            mock_auth_repo.get_user_by_id.return_value = mock_admin
            mock_bcrypt.checkpw.return_value = True

            # count returns 0 so seed proceeds
            mock_stage_repo.count_stages_by_entity.return_value = 0
            mock_stage_repo.create_stage.side_effect = mock_stages

            token = await get_auth_token(client, mock_admin)

            response = await client.post(
                "/api/pipeline-stages/seed",
                json={"entity_id": str(entity_id)},
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 201
    data = response.json()
    assert len(data) == 7
    print("INFO [TestPipelineStageAPI]: test_seed_default_stages_success - PASSED")


# ============================================================================
# Get Prospect Transitions Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_prospect_transitions_success() -> None:
    """Test getting stage transition history for a prospect."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    prospect_id = uuid4()
    mock_transition = create_mock_transition(
        prospect_id=prospect_id,
        entity_id=entity_id,
        notes="Moved to qualified",
    )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.pipeline_stage_service.stage_transition_repository"
        ) as mock_trans_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_trans_repo.get_transitions_by_prospect.return_value = [mock_transition]
            mock_trans_repo.count_transitions_by_prospect.return_value = 1

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/pipeline-stages/transitions/{prospect_id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert len(data["transitions"]) == 1
    assert data["total"] == 1
    print("INFO [TestPipelineStageAPI]: test_get_prospect_transitions_success - PASSED")


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
            "/api/pipeline-stages/",
            json={
                "entity_id": str(uuid4()),
                "name": "lead",
                "display_name": "Lead",
                "order_index": 0,
            },
        )

    assert response.status_code in (401, 403)
    print("INFO [TestPipelineStageAPI]: test_unauthenticated_request - PASSED")
