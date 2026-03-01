"""Tests for meeting record API endpoints."""

from datetime import date, datetime
from typing import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from main import app
from src.adapter.rest.dependencies import get_db
from src.models.meeting_record import MeetingRecord
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


def create_mock_meeting_record(
    entity_id=None,
    prospect_id=None,
    title="Q1 Strategy Meeting",
    transcript_ref="s3://meetings/2026-02-01.txt",
    summary="Discussed Q1 goals and budget allocation.",
    action_items='["Follow up on budget", "Schedule review"]',
    participants='["John Doe", "Jane Smith"]',
    html_output="<html><body><h1>Q1 Strategy Meeting</h1></body></html>",
    meeting_date=date(2026, 2, 1),
    is_active=True,
):
    """Create a mock meeting record for testing."""
    mock_record = MagicMock(spec=MeetingRecord)
    mock_record.id = uuid4()
    mock_record.entity_id = entity_id or uuid4()
    mock_record.prospect_id = prospect_id or uuid4()
    mock_record.title = title
    mock_record.transcript_ref = transcript_ref
    mock_record.summary = summary
    mock_record.action_items = action_items
    mock_record.participants = participants
    mock_record.html_output = html_output
    mock_record.meeting_date = meeting_date
    mock_record.is_active = is_active
    mock_record.created_at = datetime(2026, 2, 1, 12, 0, 0)
    mock_record.updated_at = None
    return mock_record


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
# Create Meeting Record Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_meeting_record_success() -> None:
    """Test successful meeting record creation."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    prospect_id = uuid4()
    mock_record = create_mock_meeting_record(entity_id=entity_id, prospect_id=prospect_id)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.meeting_record_service.meeting_record_repository"
        ) as mock_record_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_record_repo.create_meeting_record.return_value = mock_record

            token = await get_auth_token(client, mock_user)

            response = await client.post(
                "/api/meeting-records/",
                json={
                    "entity_id": str(entity_id),
                    "prospect_id": str(prospect_id),
                    "title": "Q1 Strategy Meeting",
                    "summary": "Discussed Q1 goals.",
                    "action_items": ["Follow up on budget"],
                    "participants": ["John Doe"],
                    "meeting_date": "2026-02-01",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "Q1 Strategy Meeting"
    assert data["entity_id"] == str(entity_id)
    print("INFO [TestMeetingRecordAPI]: test_create_meeting_record_success - PASSED")


@pytest.mark.asyncio
async def test_create_meeting_record_validation_error() -> None:
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
                "/api/meeting-records/",
                json={
                    "entity_id": str(uuid4()),
                    # Missing prospect_id and title
                },
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 422
    print("INFO [TestMeetingRecordAPI]: test_create_meeting_record_validation_error - PASSED")


# ============================================================================
# List Meeting Records Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_meeting_records_success() -> None:
    """Test list meeting records for an entity."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_record = create_mock_meeting_record(entity_id=entity_id)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.meeting_record_service.meeting_record_repository"
        ) as mock_record_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_record_repo.get_meeting_records_by_entity.return_value = [mock_record]
            mock_record_repo.count_meeting_records_by_entity.return_value = 1

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/meeting-records/?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert len(data["meeting_records"]) == 1
    assert data["total"] == 1
    print("INFO [TestMeetingRecordAPI]: test_list_meeting_records_success - PASSED")


# ============================================================================
# Get Single Meeting Record Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_meeting_record_success() -> None:
    """Test get a single meeting record by ID."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_record = create_mock_meeting_record(entity_id=entity_id)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.meeting_record_service.meeting_record_repository"
        ) as mock_record_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_record_repo.get_meeting_record_by_id.return_value = mock_record

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/meeting-records/{mock_record.id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Q1 Strategy Meeting"
    print("INFO [TestMeetingRecordAPI]: test_get_meeting_record_success - PASSED")


@pytest.mark.asyncio
async def test_get_meeting_record_not_found() -> None:
    """Test 404 for non-existent meeting record."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    record_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.meeting_record_service.meeting_record_repository"
        ) as mock_record_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_record_repo.get_meeting_record_by_id.return_value = None

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/meeting-records/{record_id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 404
    print("INFO [TestMeetingRecordAPI]: test_get_meeting_record_not_found - PASSED")


# ============================================================================
# Get Meeting Record HTML Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_meeting_record_html_success() -> None:
    """Test downloading HTML output for a meeting record."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_record = create_mock_meeting_record(entity_id=entity_id)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.meeting_record_service.meeting_record_repository"
        ) as mock_record_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_record_repo.get_meeting_record_by_id.return_value = mock_record

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/meeting-records/{mock_record.id}/html?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<html>" in response.text
    print("INFO [TestMeetingRecordAPI]: test_get_meeting_record_html_success - PASSED")


@pytest.mark.asyncio
async def test_get_meeting_record_html_not_found() -> None:
    """Test 404 for HTML download of non-existent record."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    record_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.meeting_record_service.meeting_record_repository"
        ) as mock_record_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_record_repo.get_meeting_record_by_id.return_value = None

            token = await get_auth_token(client, mock_user)

            response = await client.get(
                f"/api/meeting-records/{record_id}/html?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 404
    print("INFO [TestMeetingRecordAPI]: test_get_meeting_record_html_not_found - PASSED")


# ============================================================================
# Update Meeting Record Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_meeting_record_success() -> None:
    """Test update existing meeting record."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    mock_record = create_mock_meeting_record(entity_id=entity_id)
    updated_record = create_mock_meeting_record(
        entity_id=entity_id,
        title="Updated Q1 Strategy Meeting",
        summary="Updated summary with new goals.",
    )
    updated_record.id = mock_record.id

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.meeting_record_service.meeting_record_repository"
        ) as mock_record_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_record_repo.get_meeting_record_by_id.return_value = mock_record
            mock_record_repo.update_meeting_record.return_value = updated_record

            token = await get_auth_token(client, mock_user)

            response = await client.put(
                f"/api/meeting-records/{mock_record.id}?entity_id={entity_id}",
                json={"title": "Updated Q1 Strategy Meeting", "summary": "Updated summary with new goals."},
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    print("INFO [TestMeetingRecordAPI]: test_update_meeting_record_success - PASSED")


@pytest.mark.asyncio
async def test_update_meeting_record_not_found() -> None:
    """Test 404 for updating non-existent meeting record."""
    mock_user = create_mock_user()
    entity_id = uuid4()
    record_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.meeting_record_service.meeting_record_repository"
        ) as mock_record_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_user
            mock_auth_repo.get_user_by_id.return_value = mock_user
            mock_bcrypt.checkpw.return_value = True

            mock_record_repo.get_meeting_record_by_id.return_value = None

            token = await get_auth_token(client, mock_user)

            response = await client.put(
                f"/api/meeting-records/{record_id}?entity_id={entity_id}",
                json={"title": "Updated"},
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 404
    print("INFO [TestMeetingRecordAPI]: test_update_meeting_record_not_found - PASSED")


# ============================================================================
# Delete Meeting Record Tests
# ============================================================================


@pytest.mark.asyncio
async def test_delete_meeting_record_success() -> None:
    """Test delete meeting record as admin."""
    mock_admin = create_mock_user(email="admin@example.com", role="admin")
    entity_id = uuid4()
    mock_record = create_mock_meeting_record(entity_id=entity_id)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.meeting_record_service.meeting_record_repository"
        ) as mock_record_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_admin
            mock_auth_repo.get_user_by_id.return_value = mock_admin
            mock_bcrypt.checkpw.return_value = True

            mock_record_repo.get_meeting_record_by_id.return_value = mock_record
            mock_record_repo.delete_meeting_record.return_value = None

            token = await get_auth_token(client, mock_admin)

            response = await client.delete(
                f"/api/meeting-records/{mock_record.id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 204
    print("INFO [TestMeetingRecordAPI]: test_delete_meeting_record_success - PASSED")


@pytest.mark.asyncio
async def test_delete_meeting_record_not_found() -> None:
    """Test 404 for deleting non-existent meeting record."""
    mock_admin = create_mock_user(email="admin@example.com", role="admin")
    entity_id = uuid4()
    record_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        with patch(
            "src.core.services.auth_service.user_repository"
        ) as mock_auth_repo, patch(
            "src.core.services.auth_service.bcrypt"
        ) as mock_bcrypt, patch(
            "src.core.services.meeting_record_service.meeting_record_repository"
        ) as mock_record_repo:
            mock_auth_repo.get_user_by_email.return_value = mock_admin
            mock_auth_repo.get_user_by_id.return_value = mock_admin
            mock_bcrypt.checkpw.return_value = True

            mock_record_repo.get_meeting_record_by_id.return_value = None

            token = await get_auth_token(client, mock_admin)

            response = await client.delete(
                f"/api/meeting-records/{record_id}?entity_id={entity_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 404
    print("INFO [TestMeetingRecordAPI]: test_delete_meeting_record_not_found - PASSED")


# ============================================================================
# Authentication Tests
# ============================================================================


@pytest.mark.asyncio
async def test_unauthenticated_request() -> None:
    """Test that unauthenticated request returns 401/403."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/meeting-records/",
            json={
                "entity_id": str(uuid4()),
                "prospect_id": str(uuid4()),
                "title": "Test Meeting",
            },
        )

    assert response.status_code in (401, 403)
    print("INFO [TestMeetingRecordAPI]: test_unauthenticated_request - PASSED")
