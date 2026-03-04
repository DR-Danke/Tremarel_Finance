"""Tests for permit type presets API and preset-based alert creation."""

from datetime import date, datetime, time, timedelta
from typing import Generator
from unittest.mock import MagicMock, patch
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
# Permit Presets Endpoint
# ============================================================================


@pytest.mark.asyncio
async def test_get_permit_presets_returns_all_presets() -> None:
    """Test GET /api/documents/permit-presets returns 5 presets with correct structure."""
    mock_user = create_mock_user()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        token = await get_auth_token(client, mock_user)
        response = await client.get(
            "/api/documents/permit-presets",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200
    presets = response.json()
    assert len(presets) == 5

    type_keys = [p["type_key"] for p in presets]
    assert "manipulacion_alimentos" in type_keys
    assert "bomberos" in type_keys
    assert "camara_comercio" in type_keys
    assert "extintor" in type_keys
    assert "sanidad" in type_keys

    for preset in presets:
        assert "type_key" in preset
        assert "name" in preset
        assert "alert_windows" in preset
        assert "notification_channel" in preset
        assert isinstance(preset["alert_windows"], list)

    print("INFO [TestPermitPresets]: test_get_permit_presets_returns_all_presets - PASSED")


@pytest.mark.asyncio
async def test_get_permit_presets_requires_auth() -> None:
    """Test GET /api/documents/permit-presets returns 401 without token."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/documents/permit-presets")

    assert response.status_code == 401

    print("INFO [TestPermitPresets]: test_get_permit_presets_requires_auth - PASSED")


# ============================================================================
# Preset-Based Alert Creation
# ============================================================================


@pytest.mark.asyncio
async def test_create_document_with_preset_type_uses_preset_windows() -> None:
    """Test creating a document with type 'sanidad' creates 3 events at 30, 14, 7 days."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    expiration_date = date.today() + timedelta(days=60)
    mock_document = create_mock_document(
        doc_type="sanidad",
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
                    "type": "sanidad",
                    "expiration_date": str(expiration_date),
                    "description": "Certificado sanitario",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        # sanidad preset: [30, 14, 7] — 3 events, all in future for 60-day expiration
        assert mock_event_repo.create.call_count == 3

        # Verify descriptions use preset name
        descriptions = [
            call.kwargs["description"]
            for call in mock_event_repo.create.call_args_list
        ]
        assert "Certificado de Inspección Sanitaria vence en 30 dias" in descriptions
        assert "Certificado de Inspección Sanitaria vence en 14 dias" in descriptions
        assert "Certificado de Inspección Sanitaria vence en 7 dias" in descriptions

    print("INFO [TestPermitPresets]: test_create_document_with_preset_type_uses_preset_windows - PASSED")


@pytest.mark.asyncio
async def test_create_document_with_preset_type_uses_preset_notification_channel() -> None:
    """Test that 'camara_comercio' preset uses 'email' notification_channel."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    expiration_date = date.today() + timedelta(days=60)
    mock_document = create_mock_document(
        doc_type="camara_comercio",
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
                    "type": "camara_comercio",
                    "expiration_date": str(expiration_date),
                    "description": "Registro camara",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        # camara_comercio preset: [30, 14] — 2 events
        assert mock_event_repo.create.call_count == 2

        # Verify notification_channel is "email"
        for call_args in mock_event_repo.create.call_args_list:
            assert call_args.kwargs["notification_channel"] == "email"

    print("INFO [TestPermitPresets]: test_create_document_with_preset_type_uses_preset_notification_channel - PASSED")


@pytest.mark.asyncio
async def test_create_document_with_custom_alert_windows_overrides_preset() -> None:
    """Test custom_alert_windows=[45, 15] on a preset type creates exactly 2 events."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    expiration_date = date.today() + timedelta(days=60)
    mock_document = create_mock_document(
        doc_type="sanidad",
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
            import json
            response = await client.post(
                "/api/documents",
                data={
                    "restaurant_id": str(restaurant_id),
                    "type": "sanidad",
                    "expiration_date": str(expiration_date),
                    "description": "Custom alert windows",
                    "custom_alert_windows": json.dumps([45, 15]),
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        # Custom windows [45, 15] — 2 events instead of preset [30, 14, 7]
        assert mock_event_repo.create.call_count == 2

        descriptions = [
            call.kwargs["description"]
            for call in mock_event_repo.create.call_args_list
        ]
        assert "Certificado de Inspección Sanitaria vence en 45 dias" in descriptions
        assert "Certificado de Inspección Sanitaria vence en 15 dias" in descriptions

    print("INFO [TestPermitPresets]: test_create_document_with_custom_alert_windows_overrides_preset - PASSED")


@pytest.mark.asyncio
async def test_create_document_with_non_preset_type_uses_defaults() -> None:
    """Test that a non-preset type like 'contrato' uses DEFAULT_ALERT_WINDOWS."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    expiration_date = date.today() + timedelta(days=60)
    mock_document = create_mock_document(
        doc_type="contrato",
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
                    "type": "contrato",
                    "expiration_date": str(expiration_date),
                    "description": "Standard contract",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        # Default windows [30, 7, 0] — 3 events
        assert mock_event_repo.create.call_count == 3

        # Verify descriptions use generic "Documento" (not a preset name)
        descriptions = [
            call.kwargs["description"]
            for call in mock_event_repo.create.call_args_list
        ]
        assert "Documento vence en 30 dias" in descriptions
        assert "Documento vence en 7 dias" in descriptions
        assert "Documento vence hoy" in descriptions

        # Verify notification_channel is default "whatsapp"
        for call_args in mock_event_repo.create.call_args_list:
            assert call_args.kwargs["notification_channel"] == "whatsapp"

    print("INFO [TestPermitPresets]: test_create_document_with_non_preset_type_uses_defaults - PASSED")


@pytest.mark.asyncio
async def test_preset_event_descriptions_use_preset_name() -> None:
    """Test that event descriptions include the preset display name."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    expiration_date = date.today() + timedelta(days=60)
    mock_document = create_mock_document(
        doc_type="bomberos",
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
                    "type": "bomberos",
                    "expiration_date": str(expiration_date),
                    "description": "Permiso bomberos",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        # bomberos preset: [0] — only day-of alert
        assert mock_event_repo.create.call_count == 1

        call_kwargs = mock_event_repo.create.call_args.kwargs
        assert call_kwargs["description"] == "Permiso de Bomberos vence hoy"

    print("INFO [TestPermitPresets]: test_preset_event_descriptions_use_preset_name - PASSED")
