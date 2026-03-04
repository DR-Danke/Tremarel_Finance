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
from src.models.person import Person
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
    event.related_resource_id = None
    event.parent_event_id = parent_event_id
    event.completed_at = None
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
    """Test that authorized user can update event status from pending to completed."""
    mock_user = create_mock_user()
    mock_event = create_mock_event(status="pending")

    def mock_update(db, event):
        event.status = "completed"
        return event

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
        mock_event_repo.update.side_effect = mock_update

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


# ============================================================================
# Task Creation Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_task_success() -> None:
    """Test that valid task creation returns 201 with type=tarea."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    responsible_id = uuid4()
    mock_event = create_mock_event(
        event_type="tarea", restaurant_id=restaurant_id, responsible_id=responsible_id
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
        mock_event_repo.create.return_value = mock_event

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                "/api/events/tasks",
                json={
                    "restaurant_id": str(restaurant_id),
                    "date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                    "description": "Daily cleaning task",
                    "responsible_id": str(responsible_id),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "tarea"
        print("INFO [TestEventAPI]: test_create_task_success - PASSED")


@pytest.mark.asyncio
async def test_create_task_missing_responsible_id() -> None:
    """Test that task without responsible_id returns 422 (Pydantic validation)."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

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
                "/api/events/tasks",
                json={
                    "restaurant_id": str(restaurant_id),
                    "date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                    "description": "Task without responsible",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 422
        print("INFO [TestEventAPI]: test_create_task_missing_responsible_id - PASSED")


@pytest.mark.asyncio
async def test_create_task_past_date() -> None:
    """Test that task with past date returns 400."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    responsible_id = uuid4()

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
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                "/api/events/tasks",
                json={
                    "restaurant_id": str(restaurant_id),
                    "date": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                    "description": "Past date task",
                    "responsible_id": str(responsible_id),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 400
        assert "past" in response.json()["detail"].lower()
        print("INFO [TestEventAPI]: test_create_task_past_date - PASSED")


@pytest.mark.asyncio
async def test_create_task_with_recurrence() -> None:
    """Test that task with frequency=daily generates recurring instances."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    responsible_id = uuid4()
    mock_event = create_mock_event(
        event_type="tarea", restaurant_id=restaurant_id,
        responsible_id=responsible_id, frequency="daily",
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
        mock_event_repo.create.return_value = mock_event
        mock_event_repo.get_by_id.return_value = mock_event
        mock_event_repo.bulk_create.return_value = []

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                "/api/events/tasks",
                json={
                    "restaurant_id": str(restaurant_id),
                    "date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                    "description": "Daily cleaning",
                    "frequency": "daily",
                    "responsible_id": str(responsible_id),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        mock_event_repo.bulk_create.assert_called_once()
        print("INFO [TestEventAPI]: test_create_task_with_recurrence - PASSED")


@pytest.mark.asyncio
async def test_create_task_unauthenticated() -> None:
    """Test that unauthenticated task creation returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/events/tasks",
            json={
                "restaurant_id": str(uuid4()),
                "date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                "responsible_id": str(uuid4()),
            },
        )

    assert response.status_code == 401
    print("INFO [TestEventAPI]: test_create_task_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_create_task_no_access() -> None:
    """Test that user without restaurant access gets 403 on task creation."""
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
                "/api/events/tasks",
                json={
                    "restaurant_id": str(restaurant_id),
                    "date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                    "responsible_id": str(uuid4()),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestEventAPI]: test_create_task_no_access - PASSED")


# ============================================================================
# Task Query Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_tasks_success() -> None:
    """Test that get tasks returns only tarea-type events."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_task = create_mock_event(event_type="tarea", restaurant_id=restaurant_id)

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
        mock_event_repo.get_by_restaurant.return_value = [mock_task]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/events/tasks?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["type"] == "tarea"
        mock_event_repo.get_by_restaurant.assert_called_once()
        call_args = mock_event_repo.get_by_restaurant.call_args
        assert call_args[0][1] == restaurant_id
        assert call_args.kwargs.get("type_filter") == "tarea" or call_args[0][2] == "tarea"
        print("INFO [TestEventAPI]: test_get_tasks_success - PASSED")


@pytest.mark.asyncio
async def test_get_tasks_filter_by_responsible() -> None:
    """Test that get tasks filters by responsible_id."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    responsible_id = uuid4()
    mock_task = create_mock_event(
        event_type="tarea", restaurant_id=restaurant_id, responsible_id=responsible_id
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
        mock_event_repo.get_by_restaurant.return_value = [mock_task]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/events/tasks?restaurant_id={restaurant_id}&responsible_id={responsible_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        print("INFO [TestEventAPI]: test_get_tasks_filter_by_responsible - PASSED")


@pytest.mark.asyncio
async def test_get_tasks_filter_by_status() -> None:
    """Test that get tasks filters by status."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_task = create_mock_event(
        event_type="tarea", restaurant_id=restaurant_id, status="completed"
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
        mock_event_repo.get_by_restaurant.return_value = [mock_task]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/events/tasks?restaurant_id={restaurant_id}&status=completed",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "completed"
        print("INFO [TestEventAPI]: test_get_tasks_filter_by_status - PASSED")


@pytest.mark.asyncio
async def test_get_tasks_unauthenticated() -> None:
    """Test that unauthenticated task list returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"/api/events/tasks?restaurant_id={uuid4()}",
        )

    assert response.status_code == 401
    print("INFO [TestEventAPI]: test_get_tasks_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_get_tasks_no_access() -> None:
    """Test that user without restaurant access gets 403 on task list."""
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
                f"/api/events/tasks?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestEventAPI]: test_get_tasks_no_access - PASSED")


# ============================================================================
# Flag Overdue Tests
# ============================================================================


@pytest.mark.asyncio
async def test_flag_overdue_events_success() -> None:
    """Test that flag overdue returns flagged_count."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

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
        mock_event_repo.update_overdue.return_value = 3

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                f"/api/events/tasks/flag-overdue?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["flagged_count"] == 3
        print("INFO [TestEventAPI]: test_flag_overdue_events_success - PASSED")


@pytest.mark.asyncio
async def test_flag_overdue_events_unauthenticated() -> None:
    """Test that unauthenticated flag overdue returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"/api/events/tasks/flag-overdue?restaurant_id={uuid4()}",
        )

    assert response.status_code == 401
    print("INFO [TestEventAPI]: test_flag_overdue_events_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_flag_overdue_events_no_access() -> None:
    """Test that user without restaurant access gets 403 on flag overdue."""
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
                f"/api/events/tasks/flag-overdue?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestEventAPI]: test_flag_overdue_events_no_access - PASSED")


# ============================================================================
# Task Completion Enhancement Tests
# ============================================================================


@pytest.mark.asyncio
async def test_complete_task_sets_completed_at() -> None:
    """Test that completing a task sets completed_at timestamp."""
    mock_user = create_mock_user()
    mock_event = create_mock_event(status="pending")

    def mock_update(db, event):
        return event

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
        mock_event_repo.update.side_effect = mock_update

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
        assert data["completed_at"] is not None
        print("INFO [TestEventAPI]: test_complete_task_sets_completed_at - PASSED")


@pytest.mark.asyncio
async def test_complete_already_completed_task_fails() -> None:
    """Test that completing an already completed task returns 400."""
    mock_user = create_mock_user()
    mock_event = create_mock_event(status="completed")

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
            response = await client.patch(
                f"/api/events/{mock_event.id}/status",
                json={"status": "completed"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 400
        assert "completed" in response.json()["detail"].lower()
        print("INFO [TestEventAPI]: test_complete_already_completed_task_fails - PASSED")


@pytest.mark.asyncio
async def test_overdue_task_can_be_completed() -> None:
    """Test that an overdue task can be completed (overdue -> completed)."""
    mock_user = create_mock_user()
    mock_event = create_mock_event(status="overdue")

    def mock_update(db, event):
        return event

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
        mock_event_repo.update.side_effect = mock_update

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
        assert data["completed_at"] is not None
        print("INFO [TestEventAPI]: test_overdue_task_can_be_completed - PASSED")


# ============================================================================
# Daily Task Summary Tests
# ============================================================================


def create_mock_person(
    name: str = "Test Person",
    role: str = "chef",
    email: str = "person@restaurant.com",
    whatsapp: str = "+52 555 123 4567",
    person_type: str = "employee",
    restaurant_id=None,
) -> Person:
    """Create a mock person."""
    person = MagicMock(spec=Person)
    person.id = uuid4()
    person.restaurant_id = restaurant_id or uuid4()
    person.name = name
    person.role = role
    person.email = email
    person.whatsapp = whatsapp
    person.push_token = None
    person.type = person_type
    person.created_at = MagicMock()
    person.updated_at = None
    return person


@pytest.mark.asyncio
async def test_get_daily_task_summary_success() -> None:
    """Test that daily task summary returns correct structure and counts."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    person = create_mock_person(name="John Chef", restaurant_id=restaurant_id)
    summary_date = "2026-03-03"

    task1 = create_mock_event(
        event_type="tarea", description="Prep salads", status="pending",
        responsible_id=person.id, restaurant_id=restaurant_id,
        event_date=datetime(2026, 3, 3, 9, 0),
    )
    task2 = create_mock_event(
        event_type="tarea", description="Clean kitchen", status="overdue",
        responsible_id=person.id, restaurant_id=restaurant_id,
        event_date=datetime(2026, 3, 3, 14, 30),
    )

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo, patch(
        "src.core.services.event_service.person_repository"
    ) as mock_person_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_person_repo.get_by_id.return_value = person
        mock_event_repo.get_by_restaurant.return_value = [task1, task2]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                "/api/events/tasks/daily-summary",
                params={
                    "restaurant_id": str(restaurant_id),
                    "person_id": str(person.id),
                    "summary_date": summary_date,
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["person_id"] == str(person.id)
        assert data["person_name"] == "John Chef"
        assert data["date"] == summary_date
        assert data["total_tasks"] == 2
        assert data["overdue_count"] == 1
        assert len(data["tasks"]) == 2
        assert data["tasks"][0]["description"] == "Prep salads"
        assert data["tasks"][0]["time"] == "09:00"
        assert data["tasks"][0]["status"] == "pending"
        assert data["tasks"][0]["is_overdue"] is False
        assert data["tasks"][1]["status"] == "overdue"
        assert data["tasks"][1]["is_overdue"] is True
        print("INFO [TestEventAPI]: test_get_daily_task_summary_success - PASSED")


@pytest.mark.asyncio
async def test_get_daily_task_summary_no_tasks() -> None:
    """Test that daily task summary returns zero counts when no tasks exist."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    person = create_mock_person(name="Jane Waiter", restaurant_id=restaurant_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo, patch(
        "src.core.services.event_service.person_repository"
    ) as mock_person_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_person_repo.get_by_id.return_value = person
        mock_event_repo.get_by_restaurant.return_value = []

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                "/api/events/tasks/daily-summary",
                params={
                    "restaurant_id": str(restaurant_id),
                    "person_id": str(person.id),
                    "summary_date": "2026-03-03",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total_tasks"] == 0
        assert data["overdue_count"] == 0
        assert data["tasks"] == []
        print("INFO [TestEventAPI]: test_get_daily_task_summary_no_tasks - PASSED")


@pytest.mark.asyncio
async def test_get_daily_task_summary_mixed_statuses() -> None:
    """Test that completed tasks are excluded from the summary."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    person = create_mock_person(name="Mike Bartender", restaurant_id=restaurant_id)

    pending_task = create_mock_event(
        event_type="tarea", description="Restock bar", status="pending",
        responsible_id=person.id, restaurant_id=restaurant_id,
        event_date=datetime(2026, 3, 3, 10, 0),
    )
    completed_task = create_mock_event(
        event_type="tarea", description="Open bar", status="completed",
        responsible_id=person.id, restaurant_id=restaurant_id,
        event_date=datetime(2026, 3, 3, 8, 0),
    )
    overdue_task = create_mock_event(
        event_type="tarea", description="Inventory check", status="overdue",
        responsible_id=person.id, restaurant_id=restaurant_id,
        event_date=datetime(2026, 3, 3, 7, 0),
    )

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo, patch(
        "src.core.services.event_service.person_repository"
    ) as mock_person_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_person_repo.get_by_id.return_value = person
        mock_event_repo.get_by_restaurant.return_value = [pending_task, completed_task, overdue_task]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                "/api/events/tasks/daily-summary",
                params={
                    "restaurant_id": str(restaurant_id),
                    "person_id": str(person.id),
                    "summary_date": "2026-03-03",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total_tasks"] == 2
        assert data["overdue_count"] == 1
        assert len(data["tasks"]) == 2
        statuses = [t["status"] for t in data["tasks"]]
        assert "completed" not in statuses
        assert "pending" in statuses
        assert "overdue" in statuses
        print("INFO [TestEventAPI]: test_get_daily_task_summary_mixed_statuses - PASSED")


@pytest.mark.asyncio
async def test_get_daily_task_summary_overdue_count() -> None:
    """Test that overdue_count accurately reflects overdue tasks."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    person = create_mock_person(name="Sara Cook", restaurant_id=restaurant_id)

    overdue1 = create_mock_event(
        event_type="tarea", description="Morning prep", status="overdue",
        responsible_id=person.id, restaurant_id=restaurant_id,
        event_date=datetime(2026, 3, 3, 6, 0),
    )
    overdue2 = create_mock_event(
        event_type="tarea", description="Check deliveries", status="overdue",
        responsible_id=person.id, restaurant_id=restaurant_id,
        event_date=datetime(2026, 3, 3, 7, 0),
    )
    pending1 = create_mock_event(
        event_type="tarea", description="Lunch service", status="pending",
        responsible_id=person.id, restaurant_id=restaurant_id,
        event_date=datetime(2026, 3, 3, 12, 0),
    )

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo, patch(
        "src.core.services.event_service.person_repository"
    ) as mock_person_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_person_repo.get_by_id.return_value = person
        mock_event_repo.get_by_restaurant.return_value = [overdue1, overdue2, pending1]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                "/api/events/tasks/daily-summary",
                params={
                    "restaurant_id": str(restaurant_id),
                    "person_id": str(person.id),
                    "summary_date": "2026-03-03",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["total_tasks"] == 3
        assert data["overdue_count"] == 2
        print("INFO [TestEventAPI]: test_get_daily_task_summary_overdue_count - PASSED")


@pytest.mark.asyncio
async def test_get_all_daily_summaries_success() -> None:
    """Test batch summary for multiple employees with tasks."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    emp1 = create_mock_person(name="Chef A", restaurant_id=restaurant_id)
    emp2 = create_mock_person(name="Chef B", restaurant_id=restaurant_id)

    task_emp1 = create_mock_event(
        event_type="tarea", description="Task for A", status="pending",
        responsible_id=emp1.id, restaurant_id=restaurant_id,
        event_date=datetime(2026, 3, 3, 10, 0),
    )
    task_emp2 = create_mock_event(
        event_type="tarea", description="Task for B", status="overdue",
        responsible_id=emp2.id, restaurant_id=restaurant_id,
        event_date=datetime(2026, 3, 3, 11, 0),
    )

    def mock_get_by_restaurant(db, rid, type_filter=None, status_filter=None,
                                date_from=None, date_to=None, responsible_id_filter=None):
        if responsible_id_filter == emp1.id:
            return [task_emp1]
        elif responsible_id_filter == emp2.id:
            return [task_emp2]
        return []

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo, patch(
        "src.core.services.event_service.person_repository"
    ) as mock_person_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_person_repo.get_by_restaurant.return_value = [emp1, emp2]
        mock_event_repo.get_by_restaurant.side_effect = mock_get_by_restaurant

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                "/api/events/tasks/daily-summary/all",
                params={
                    "restaurant_id": str(restaurant_id),
                    "summary_date": "2026-03-03",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = {s["person_name"] for s in data}
        assert "Chef A" in names
        assert "Chef B" in names
        print("INFO [TestEventAPI]: test_get_all_daily_summaries_success - PASSED")


@pytest.mark.asyncio
async def test_get_all_daily_summaries_excludes_zero_tasks() -> None:
    """Test that employees with no tasks are excluded from batch summary."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    emp_with_tasks = create_mock_person(name="Busy Chef", restaurant_id=restaurant_id)
    emp_no_tasks = create_mock_person(name="Idle Chef", restaurant_id=restaurant_id)

    task1 = create_mock_event(
        event_type="tarea", description="Cook lunch", status="pending",
        responsible_id=emp_with_tasks.id, restaurant_id=restaurant_id,
        event_date=datetime(2026, 3, 3, 12, 0),
    )

    def mock_get_by_restaurant(db, rid, type_filter=None, status_filter=None,
                                date_from=None, date_to=None, responsible_id_filter=None):
        if responsible_id_filter == emp_with_tasks.id:
            return [task1]
        return []

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo, patch(
        "src.core.services.event_service.person_repository"
    ) as mock_person_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_person_repo.get_by_restaurant.return_value = [emp_with_tasks, emp_no_tasks]
        mock_event_repo.get_by_restaurant.side_effect = mock_get_by_restaurant

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                "/api/events/tasks/daily-summary/all",
                params={
                    "restaurant_id": str(restaurant_id),
                    "summary_date": "2026-03-03",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["person_name"] == "Busy Chef"
        print("INFO [TestEventAPI]: test_get_all_daily_summaries_excludes_zero_tasks - PASSED")


@pytest.mark.asyncio
async def test_get_daily_task_summary_unauthorized() -> None:
    """Test that user without restaurant access gets 403."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    person_id = uuid4()

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
                "/api/events/tasks/daily-summary",
                params={
                    "restaurant_id": str(restaurant_id),
                    "person_id": str(person_id),
                    "summary_date": "2026-03-03",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestEventAPI]: test_get_daily_task_summary_unauthorized - PASSED")
