"""Tests for document expiration alert automation."""

from datetime import date, datetime, time, timedelta
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from main import app
from src.adapter.rest.dependencies import get_db
from src.models.document import Document
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


def create_mock_document(
    doc_type: str = "permiso",
    expiration_date: date = None,
    person_id=None,
    description: str = "Test document",
    restaurant_id=None,
) -> Document:
    """Create a mock document."""
    document = MagicMock(spec=Document)
    document.id = uuid4()
    document.restaurant_id = restaurant_id or uuid4()
    document.type = doc_type
    document.file_url = None
    document.issue_date = None
    document.expiration_date = expiration_date
    document.person_id = person_id
    document.description = description
    document.processing_status = None
    document.processing_result = None
    document.created_at = MagicMock()
    document.updated_at = None
    return document


def create_mock_event(
    event_type: str = "vencimiento",
    description: str = "Documento vence en 30 dias",
    related_document_id=None,
    restaurant_id=None,
    responsible_id=None,
) -> Event:
    """Create a mock event."""
    event = MagicMock(spec=Event)
    event.id = uuid4()
    event.restaurant_id = restaurant_id or uuid4()
    event.type = event_type
    event.description = description
    event.date = datetime.combine(date.today(), time(8, 0))
    event.frequency = "none"
    event.responsible_id = responsible_id
    event.notification_channel = "whatsapp"
    event.status = "pending"
    event.related_document_id = related_document_id
    event.parent_event_id = None
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
# Document Create Triggers Alert Events
# ============================================================================


@pytest.mark.asyncio
async def test_create_document_with_expiration_creates_alerts() -> None:
    """Test that creating a document with expiration_date 60 days ahead creates 3 alert events."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    person_id = uuid4()
    expiration_date = date.today() + timedelta(days=60)
    mock_document = create_mock_document(
        expiration_date=expiration_date,
        person_id=person_id,
        restaurant_id=restaurant_id,
    )

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.document_service.document_repository"
    ) as mock_document_repo, patch(
        "src.core.services.document_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_document_repo.create.return_value = mock_document
        mock_event_repo.create.return_value = create_mock_event()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                "/api/documents",
                data={
                    "restaurant_id": str(restaurant_id),
                    "type": "permiso",
                    "expiration_date": str(expiration_date),
                    "person_id": str(person_id),
                    "description": "Permiso sanitario",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        assert mock_event_repo.create.call_count == 3

        # Verify all created events are vencimiento type
        for call_args in mock_event_repo.create.call_args_list:
            assert call_args.kwargs["event_type"] == "vencimiento"
            assert call_args.kwargs["frequency"] == "none"
            assert call_args.kwargs["notification_channel"] == "whatsapp"
            assert call_args.kwargs["related_document_id"] == mock_document.id

    print("INFO [TestDocumentExpirationAlert]: test_create_document_with_expiration_creates_alerts - PASSED")


@pytest.mark.asyncio
async def test_create_document_without_expiration_skips_alerts() -> None:
    """Test that creating a document without expiration_date creates no events."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_document = create_mock_document(
        expiration_date=None,
        restaurant_id=restaurant_id,
    )

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.document_service.document_repository"
    ) as mock_document_repo, patch(
        "src.core.services.document_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_document_repo.create.return_value = mock_document

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                "/api/documents",
                data={
                    "restaurant_id": str(restaurant_id),
                    "type": "contrato",
                    "description": "Contract without expiration",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        mock_event_repo.create.assert_not_called()

    print("INFO [TestDocumentExpirationAlert]: test_create_document_without_expiration_skips_alerts - PASSED")


@pytest.mark.asyncio
async def test_create_document_with_near_expiration_skips_past_alerts() -> None:
    """Test that creating a document with expiration 5 days ahead creates only 1 event (day-of)."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    expiration_date = date.today() + timedelta(days=5)
    mock_document = create_mock_document(
        expiration_date=expiration_date,
        restaurant_id=restaurant_id,
    )

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.document_service.document_repository"
    ) as mock_document_repo, patch(
        "src.core.services.document_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_document_repo.create.return_value = mock_document
        mock_event_repo.create.return_value = create_mock_event()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                "/api/documents",
                data={
                    "restaurant_id": str(restaurant_id),
                    "type": "licencia",
                    "expiration_date": str(expiration_date),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        # 30-day alert: 5-30 = -25 days (past, skipped)
        # 7-day alert: 5-7 = -2 days (past, skipped)
        # 0-day alert: 5-0 = 5 days (future, created)
        assert mock_event_repo.create.call_count == 1
        call_kwargs = mock_event_repo.create.call_args.kwargs
        assert call_kwargs["description"] == "Documento vence hoy"

    print("INFO [TestDocumentExpirationAlert]: test_create_document_with_near_expiration_skips_past_alerts - PASSED")


# ============================================================================
# Document Update Replaces Alert Events
# ============================================================================


@pytest.mark.asyncio
async def test_update_document_expiration_replaces_alerts() -> None:
    """Test that updating expiration_date deletes old events and creates new ones."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    old_expiration = date.today() + timedelta(days=60)
    new_expiration = date.today() + timedelta(days=40)

    mock_document = create_mock_document(
        expiration_date=old_expiration,
        restaurant_id=restaurant_id,
    )

    updated_mock = create_mock_document(
        expiration_date=new_expiration,
        restaurant_id=restaurant_id,
    )
    updated_mock.id = mock_document.id

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.document_service.document_repository"
    ) as mock_document_repo, patch(
        "src.core.services.document_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_document_repo.get_by_id.return_value = mock_document
        mock_document_repo.update.return_value = updated_mock
        mock_event_repo.delete_by_related_document.return_value = 3
        mock_event_repo.create.return_value = create_mock_event()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.put(
                f"/api/documents/{mock_document.id}",
                json={"expiration_date": str(new_expiration)},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        # Old alerts deleted
        mock_event_repo.delete_by_related_document.assert_called_once()
        # New alerts created (all 3 should be in the future for 40 days)
        assert mock_event_repo.create.call_count == 3

    print("INFO [TestDocumentExpirationAlert]: test_update_document_expiration_replaces_alerts - PASSED")


@pytest.mark.asyncio
async def test_update_document_without_changing_expiration_no_alert_change() -> None:
    """Test that updating description only does not trigger alert changes."""
    mock_user = create_mock_user()
    expiration_date = date.today() + timedelta(days=60)
    mock_document = create_mock_document(expiration_date=expiration_date)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.document_service.document_repository"
    ) as mock_document_repo, patch(
        "src.core.services.document_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_document_repo.get_by_id.return_value = mock_document
        mock_document_repo.update.return_value = mock_document

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.put(
                f"/api/documents/{mock_document.id}",
                json={"description": "Updated description only"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        mock_event_repo.delete_by_related_document.assert_not_called()
        mock_event_repo.create.assert_not_called()

    print("INFO [TestDocumentExpirationAlert]: test_update_document_without_changing_expiration_no_alert_change - PASSED")


# ============================================================================
# Document Delete Cleans Up Alert Events
# ============================================================================


@pytest.mark.asyncio
async def test_delete_document_cleans_up_alerts() -> None:
    """Test that deleting a document calls delete_by_related_document."""
    mock_user = create_mock_user()
    mock_document = create_mock_document(
        expiration_date=date.today() + timedelta(days=60),
    )

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.document_service.document_repository"
    ) as mock_document_repo, patch(
        "src.core.services.document_service.event_repository"
    ) as mock_event_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_document_repo.get_by_id.return_value = mock_document
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_document_repo.delete.return_value = True
        mock_event_repo.delete_by_related_document.return_value = 3

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.delete(
                f"/api/documents/{mock_document.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 204
        mock_event_repo.delete_by_related_document.assert_called_once()

    print("INFO [TestDocumentExpirationAlert]: test_delete_document_cleans_up_alerts - PASSED")


# ============================================================================
# Process Expiration Alerts Endpoint
# ============================================================================


@pytest.mark.asyncio
async def test_process_expiration_alerts_endpoint() -> None:
    """Test POST /api/notifications/process-expiration-alerts calls scheduler and returns result."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    trigger_result = {
        "processed": 2,
        "sent": 1,
        "skipped": 1,
        "failed": 0,
    }

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.adapter.rest.notification_routes.process_document_expiration_alerts",
        new_callable=AsyncMock,
    ) as mock_process:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_process.return_value = trigger_result

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                f"/api/notifications/process-expiration-alerts?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["processed"] == 2
    assert data["sent"] == 1
    assert data["skipped"] == 1
    assert data["failed"] == 0
    print("INFO [TestDocumentExpirationAlert]: test_process_expiration_alerts_endpoint - PASSED")
