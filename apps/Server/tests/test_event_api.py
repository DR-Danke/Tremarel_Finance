"""Tests for event API endpoints."""

from datetime import datetime, timedelta
from typing import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from main import app
from src.adapter.rest.dependencies import get_db
from src.models.event import Event
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


def create_mock_event(
    event_type: str = "tarea",
    description: str = "Test event",
    event_date: datetime = None,
    frequency: str = "none",
    responsible_id=None,
    notification_channel: str = "email",
    status: str = "pending",
    related_document_id=None,
    parent_event_id=None,
    restaurant_id=None,
) -> Event:
    """Create a mock event."""
    event = MagicMock(spec=Event)
    event.id = uuid4()
    event.restaurant_id = restaurant_id or uuid4()
    event.type = event_type
    event.description = description
    event.date = event_date or (datetime.utcnow() + timedelta(days=1))
    event.frequency = frequency
    event.responsible_id = responsible_id
    event.notification_channel = notification_channel
    event.status = status
    event.related_document_id = related_document_id
    event.parent_event_id = parent_event_id
    event.created_at = MagicMock()
    event.updated_at = None
    return event


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
# Event Creation Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_event_success() -> None:
    """Test that valid event creation returns 201."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_event = create_mock_event(restaurant_id=restaurant_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_event_repo.create.return_value = mock_event

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                "/api/events",
                json={
                    "restaurant_id": str(restaurant_id),
                    "type": "tarea",
                    "date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                    "description": "Test task",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "tarea"
        assert "is_overdue" in data
        print("INFO [TestEventAPI]: test_create_event_success - PASSED")


@pytest.mark.asyncio
async def test_create_event_unauthenticated() -> None:
    """Test that unauthenticated request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/events",
            json={
                "restaurant_id": str(uuid4()),
                "type": "tarea",
                "date": datetime.utcnow().isoformat(),
            },
        )

    assert response.status_code == 401
    print("INFO [TestEventAPI]: test_create_event_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_create_event_no_restaurant_access() -> None:
    """Test that user without restaurant access gets 403."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
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
                "/api/events",
                json={
                    "restaurant_id": str(restaurant_id),
                    "type": "tarea",
                    "date": datetime.utcnow().isoformat(),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestEventAPI]: test_create_event_no_restaurant_access - PASSED")


# ============================================================================
# List Events Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_events_success() -> None:
    """Test that listing events returns restaurant's events."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_e1 = create_mock_event(event_type="tarea", restaurant_id=restaurant_id)
    mock_e2 = create_mock_event(event_type="pago", restaurant_id=restaurant_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_event_repo.get_by_restaurant.return_value = [mock_e1, mock_e2]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/events?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        print("INFO [TestEventAPI]: test_list_events_success - PASSED")


@pytest.mark.asyncio
async def test_list_events_unauthenticated() -> None:
    """Test that unauthenticated list request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"/api/events?restaurant_id={uuid4()}",
        )

    assert response.status_code == 401
    print("INFO [TestEventAPI]: test_list_events_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_list_events_no_access() -> None:
    """Test that user without restaurant access gets 403 on list."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/events?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestEventAPI]: test_list_events_no_access - PASSED")


@pytest.mark.asyncio
async def test_list_events_with_type_filter() -> None:
    """Test that type filter works correctly."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_event = create_mock_event(event_type="pago", restaurant_id=restaurant_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_event_repo.get_by_restaurant.return_value = [mock_event]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/events?restaurant_id={restaurant_id}&type=pago",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "pago"
        print("INFO [TestEventAPI]: test_list_events_with_type_filter - PASSED")


@pytest.mark.asyncio
async def test_list_events_with_status_filter() -> None:
    """Test that status filter works correctly."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_event = create_mock_event(status="completed", restaurant_id=restaurant_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_event_repo.get_by_restaurant.return_value = [mock_event]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/events?restaurant_id={restaurant_id}&status=completed",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "completed"
        print("INFO [TestEventAPI]: test_list_events_with_status_filter - PASSED")


# ============================================================================
# Get Event Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_event_success() -> None:
    """Test that getting event works for authorized users."""
    mock_user = create_mock_user()
    mock_event = create_mock_event()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_event_repo.get_by_id.return_value = mock_event
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/events/{mock_event.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == mock_event.type
        assert "is_overdue" in data
        print("INFO [TestEventAPI]: test_get_event_success - PASSED")


@pytest.mark.asyncio
async def test_get_event_not_found() -> None:
    """Test that getting nonexistent event returns 404."""
    mock_user = create_mock_user()
    event_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_event_repo.get_by_id.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/events/{event_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        print("INFO [TestEventAPI]: test_get_event_not_found - PASSED")


@pytest.mark.asyncio
async def test_get_event_unauthenticated() -> None:
    """Test that unauthenticated get returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"/api/events/{uuid4()}",
        )

    assert response.status_code == 401
    print("INFO [TestEventAPI]: test_get_event_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_get_event_no_access() -> None:
    """Test that user without restaurant access gets 403."""
    mock_user = create_mock_user()
    mock_event = create_mock_event()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_event_repo.get_by_id.return_value = mock_event
        mock_restaurant_repo.get_user_restaurant_role.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/events/{mock_event.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestEventAPI]: test_get_event_no_access - PASSED")


# ============================================================================
# Update Event Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_event_success() -> None:
    """Test that authorized user can update event."""
    mock_user = create_mock_user()
    mock_event = create_mock_event()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_event_repo.get_by_id.return_value = mock_event
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_event_repo.update.return_value = mock_event

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.put(
                f"/api/events/{mock_event.id}",
                json={"type": "pago", "description": "Updated description"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        print("INFO [TestEventAPI]: test_update_event_success - PASSED")


@pytest.mark.asyncio
async def test_update_event_not_found() -> None:
    """Test that updating nonexistent event returns 404."""
    mock_user = create_mock_user()
    event_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_event_repo.get_by_id.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.put(
                f"/api/events/{event_id}",
                json={"type": "pago"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        print("INFO [TestEventAPI]: test_update_event_not_found - PASSED")


@pytest.mark.asyncio
async def test_update_event_unauthenticated() -> None:
    """Test that unauthenticated update returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.put(
            f"/api/events/{uuid4()}",
            json={"type": "pago"},
        )

    assert response.status_code == 401
    print("INFO [TestEventAPI]: test_update_event_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_update_event_no_access() -> None:
    """Test that user without restaurant access cannot update."""
    mock_user = create_mock_user()
    mock_event = create_mock_event()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_event_repo.get_by_id.return_value = mock_event
        mock_restaurant_repo.get_user_restaurant_role.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.put(
                f"/api/events/{mock_event.id}",
                json={"description": "Updated"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestEventAPI]: test_update_event_no_access - PASSED")


# ============================================================================
# Status Update Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_event_status_success() -> None:
    """Test that authorized user can update event status."""
    mock_user = create_mock_user()
    mock_event = create_mock_event()
    mock_event.status = "completed"

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_event_repo.get_by_id.return_value = mock_event
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_event_repo.update.return_value = mock_event

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.patch(
                f"/api/events/{mock_event.id}/status",
                json={"status": "completed"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        print("INFO [TestEventAPI]: test_update_event_status_success - PASSED")


@pytest.mark.asyncio
async def test_update_event_status_not_found() -> None:
    """Test that updating status of nonexistent event returns 404."""
    mock_user = create_mock_user()
    event_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_event_repo.get_by_id.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.patch(
                f"/api/events/{event_id}/status",
                json={"status": "completed"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        print("INFO [TestEventAPI]: test_update_event_status_not_found - PASSED")


@pytest.mark.asyncio
async def test_update_event_status_unauthenticated() -> None:
    """Test that unauthenticated status update returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.patch(
            f"/api/events/{uuid4()}/status",
            json={"status": "completed"},
        )

    assert response.status_code == 401
    print("INFO [TestEventAPI]: test_update_event_status_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_update_event_status_no_access() -> None:
    """Test that user without restaurant access cannot update status."""
    mock_user = create_mock_user()
    mock_event = create_mock_event()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_event_repo.get_by_id.return_value = mock_event
        mock_restaurant_repo.get_user_restaurant_role.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.patch(
                f"/api/events/{mock_event.id}/status",
                json={"status": "completed"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestEventAPI]: test_update_event_status_no_access - PASSED")


# ============================================================================
# Delete Event Tests
# ============================================================================


@pytest.mark.asyncio
async def test_delete_event_success() -> None:
    """Test that authorized user can delete event."""
    mock_user = create_mock_user()
    mock_event = create_mock_event()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_event_repo.get_by_id.return_value = mock_event
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_event_repo.delete.return_value = True

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.delete(
                f"/api/events/{mock_event.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 204
        print("INFO [TestEventAPI]: test_delete_event_success - PASSED")


@pytest.mark.asyncio
async def test_delete_event_not_found() -> None:
    """Test that deleting nonexistent event returns 404."""
    mock_user = create_mock_user()
    event_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_event_repo.get_by_id.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.delete(
                f"/api/events/{event_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        print("INFO [TestEventAPI]: test_delete_event_not_found - PASSED")


@pytest.mark.asyncio
async def test_delete_event_unauthenticated() -> None:
    """Test that unauthenticated delete returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.delete(
            f"/api/events/{uuid4()}",
        )

    assert response.status_code == 401
    print("INFO [TestEventAPI]: test_delete_event_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_delete_event_no_access() -> None:
    """Test that user without restaurant access cannot delete."""
    mock_user = create_mock_user()
    mock_event = create_mock_event()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_event_repo.get_by_id.return_value = mock_event
        mock_restaurant_repo.get_user_restaurant_role.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.delete(
                f"/api/events/{mock_event.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestEventAPI]: test_delete_event_no_access - PASSED")


# ============================================================================
# Due Events Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_due_events_success() -> None:
    """Test that due events endpoint returns events for the target date."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    target_date = datetime.utcnow().date()
    mock_due_event = create_mock_event(
        event_type="vencimiento",
        event_date=datetime.utcnow(),
        restaurant_id=restaurant_id,
    )

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_event_repo.get_due_events.return_value = [mock_due_event]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/events/due?restaurant_id={restaurant_id}&target_date={target_date.isoformat()}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        print("INFO [TestEventAPI]: test_get_due_events_success - PASSED")


@pytest.mark.asyncio
async def test_get_due_events_unauthenticated() -> None:
    """Test that unauthenticated due events request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"/api/events/due?restaurant_id={uuid4()}&target_date=2026-03-03",
        )

    assert response.status_code == 401
    print("INFO [TestEventAPI]: test_get_due_events_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_get_due_events_no_access() -> None:
    """Test that user without restaurant access gets 403 on due events."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/events/due?restaurant_id={restaurant_id}&target_date=2026-03-03",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestEventAPI]: test_get_due_events_no_access - PASSED")


# ============================================================================
# is_overdue Computed Field Tests
# ============================================================================


@pytest.mark.asyncio
async def test_is_overdue_pending_past_date() -> None:
    """Test that is_overdue is True for pending event with past date."""
    mock_user = create_mock_user()
    mock_event = create_mock_event(
        status="pending",
        event_date=datetime.utcnow() - timedelta(days=5),
    )

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_event_repo.get_by_id.return_value = mock_event
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/events/{mock_event.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["is_overdue"] is True
        print("INFO [TestEventAPI]: test_is_overdue_pending_past_date - PASSED")


@pytest.mark.asyncio
async def test_is_overdue_completed_past_date() -> None:
    """Test that is_overdue is False for completed event even with past date."""
    mock_user = create_mock_user()
    mock_event = create_mock_event(
        status="completed",
        event_date=datetime.utcnow() - timedelta(days=5),
    )

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_event_repo.get_by_id.return_value = mock_event
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/events/{mock_event.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["is_overdue"] is False
        print("INFO [TestEventAPI]: test_is_overdue_completed_past_date - PASSED")
