"""Tests for notification API endpoints."""

from datetime import date
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from main import app
from src.adapter.rest.dependencies import get_db
from src.models.notification_log import NotificationLog
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


def create_mock_notification_log(
    restaurant_id=None,
    channel: str = "whatsapp",
    recipient: str = "+573001234567",
    message: str = "Test message",
    status: str = "sent",
    error_message=None,
    event_id=None,
) -> NotificationLog:
    """Create a mock notification log entry."""
    log = MagicMock(spec=NotificationLog)
    log.id = uuid4()
    log.restaurant_id = restaurant_id or uuid4()
    log.channel = channel
    log.recipient = recipient
    log.message = message
    log.status = status
    log.error_message = error_message
    log.event_id = event_id
    log.created_at = MagicMock()
    return log


# ============================================================================
# Send Daily Summaries Tests
# ============================================================================


@pytest.mark.asyncio
async def test_send_daily_summaries_success() -> None:
    """Test POST /api/notifications/send-daily-summaries returns results."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    trigger_result = {
        "total_employees": 2,
        "sent_count": 1,
        "skipped_count": 1,
        "results": [
            {
                "person_id": str(uuid4()),
                "person_name": "Ana Lopez",
                "recipient": "+573001234567",
                "status": "sent",
                "error_message": None,
            },
            {
                "person_id": str(uuid4()),
                "person_name": "Pedro",
                "recipient": "",
                "status": "skipped",
                "error_message": "No WhatsApp number",
            },
        ],
    }

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.adapter.rest.notification_routes.send_morning_task_summaries",
        new_callable=AsyncMock,
    ) as mock_send:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_send.return_value = trigger_result

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                f"/api/notifications/send-daily-summaries?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["total_employees"] == 2
    assert data["sent_count"] == 1
    assert data["skipped_count"] == 1
    assert len(data["results"]) == 2
    print("INFO [TestNotificationAPI]: test_send_daily_summaries_success - PASSED")


@pytest.mark.asyncio
async def test_send_daily_summaries_empty_restaurant() -> None:
    """Test POST /api/notifications/send-daily-summaries with no employees."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    trigger_result = {
        "total_employees": 0,
        "sent_count": 0,
        "skipped_count": 0,
        "results": [],
    }

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.adapter.rest.notification_routes.send_morning_task_summaries",
        new_callable=AsyncMock,
    ) as mock_send:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_send.return_value = trigger_result

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                f"/api/notifications/send-daily-summaries?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["total_employees"] == 0
    assert data["sent_count"] == 0
    print("INFO [TestNotificationAPI]: test_send_daily_summaries_empty_restaurant - PASSED")


@pytest.mark.asyncio
async def test_send_daily_summaries_permission_denied() -> None:
    """Test POST /api/notifications/send-daily-summaries returns 403 on permission error."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.adapter.rest.notification_routes.send_morning_task_summaries",
        new_callable=AsyncMock,
    ) as mock_send:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_send.side_effect = PermissionError("User doesn't have access to this restaurant")

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                f"/api/notifications/send-daily-summaries?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 403
    print("INFO [TestNotificationAPI]: test_send_daily_summaries_permission_denied - PASSED")


@pytest.mark.asyncio
async def test_send_daily_summaries_missing_restaurant_id() -> None:
    """Test POST /api/notifications/send-daily-summaries without restaurant_id returns 422."""
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
                "/api/notifications/send-daily-summaries",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 422
    print("INFO [TestNotificationAPI]: test_send_daily_summaries_missing_restaurant_id - PASSED")


# ============================================================================
# Notification Log Query Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_notification_logs_success() -> None:
    """Test GET /api/notifications/log returns log entries."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_log = create_mock_notification_log(restaurant_id=restaurant_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.adapter.rest.notification_routes.notification_log_repository"
    ) as mock_log_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_log_repo.get_by_restaurant.return_value = [mock_log]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/notifications/log?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["channel"] == "whatsapp"
    assert data[0]["recipient"] == "+573001234567"
    assert data[0]["status"] == "sent"
    print("INFO [TestNotificationAPI]: test_list_notification_logs_success - PASSED")


@pytest.mark.asyncio
async def test_list_notification_logs_filter_by_channel() -> None:
    """Test GET /api/notifications/log with channel filter."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_log = create_mock_notification_log(restaurant_id=restaurant_id, channel="whatsapp")

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.adapter.rest.notification_routes.notification_log_repository"
    ) as mock_log_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_log_repo.get_by_restaurant.return_value = [mock_log]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/notifications/log?restaurant_id={restaurant_id}&channel=whatsapp",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert all(entry["channel"] == "whatsapp" for entry in data)
    mock_log_repo.get_by_restaurant.assert_called_once()
    print("INFO [TestNotificationAPI]: test_list_notification_logs_filter_by_channel - PASSED")


@pytest.mark.asyncio
async def test_list_notification_logs_filter_by_status() -> None:
    """Test GET /api/notifications/log with status filter."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_log = create_mock_notification_log(restaurant_id=restaurant_id, status="failed", error_message="Network error")

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.adapter.rest.notification_routes.notification_log_repository"
    ) as mock_log_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_log_repo.get_by_restaurant.return_value = [mock_log]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/notifications/log?restaurant_id={restaurant_id}&status=failed",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert all(entry["status"] == "failed" for entry in data)
    print("INFO [TestNotificationAPI]: test_list_notification_logs_filter_by_status - PASSED")


@pytest.mark.asyncio
async def test_list_notification_logs_empty_results() -> None:
    """Test GET /api/notifications/log returns empty list when no logs exist."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.adapter.rest.notification_routes.notification_log_repository"
    ) as mock_log_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_log_repo.get_by_restaurant.return_value = []

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/notifications/log?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data == []
    print("INFO [TestNotificationAPI]: test_list_notification_logs_empty_results - PASSED")
