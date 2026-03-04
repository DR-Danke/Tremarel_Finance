"""Tests for restaurant dashboard API endpoint."""

from datetime import date, datetime
from decimal import Decimal
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
from src.models.inventory_movement import InventoryMovement
from src.models.resource import Resource
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


def create_mock_event(restaurant_id=None, event_type: str = "tarea") -> Event:
    """Create a mock event."""
    event = MagicMock(spec=Event)
    event.id = uuid4()
    event.restaurant_id = restaurant_id or uuid4()
    event.type = event_type
    event.description = "Test task"
    event.date = datetime.utcnow()
    event.frequency = "none"
    event.responsible_id = uuid4()
    event.notification_channel = "email"
    event.status = "pending"
    event.related_document_id = None
    event.related_resource_id = None
    event.parent_event_id = None
    event.completed_at = None
    event.created_at = datetime.utcnow()
    event.updated_at = None
    return event


def create_mock_document(restaurant_id=None) -> Document:
    """Create a mock document."""
    doc = MagicMock(spec=Document)
    doc.id = uuid4()
    doc.restaurant_id = restaurant_id or uuid4()
    doc.type = "permiso"
    doc.file_url = None
    doc.issue_date = date.today()
    doc.expiration_date = date.today()
    doc.person_id = None
    doc.description = "Test document"
    doc.processing_status = None
    doc.processing_result = None
    doc.created_at = datetime.utcnow()
    doc.updated_at = None
    return doc


def create_mock_resource(restaurant_id=None) -> Resource:
    """Create a mock resource."""
    resource = MagicMock(spec=Resource)
    resource.id = uuid4()
    resource.restaurant_id = restaurant_id or uuid4()
    resource.type = "producto"
    resource.name = "Tomate"
    resource.unit = "kg"
    resource.current_stock = Decimal("3.0")
    resource.minimum_stock = Decimal("5.0")
    resource.last_unit_cost = Decimal("2.50")
    resource.created_at = datetime.utcnow()
    resource.updated_at = None
    return resource


def create_mock_movement(restaurant_id=None) -> InventoryMovement:
    """Create a mock inventory movement."""
    movement = MagicMock(spec=InventoryMovement)
    movement.id = uuid4()
    movement.resource_id = uuid4()
    movement.type = "entry"
    movement.quantity = Decimal("10.0")
    movement.reason = "compra"
    movement.date = datetime.utcnow()
    movement.person_id = None
    movement.restaurant_id = restaurant_id or uuid4()
    movement.notes = None
    movement.created_at = datetime.utcnow()
    return movement


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
# Dashboard Overview Tests
# ============================================================================


@pytest.mark.asyncio
async def test_dashboard_overview_success() -> None:
    """Test that dashboard overview returns 200 with expected structure."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    mock_task = create_mock_event(restaurant_id, "tarea")
    mock_doc = create_mock_document(restaurant_id)
    mock_resource = create_mock_resource(restaurant_id)
    mock_movement = create_mock_movement(restaurant_id)
    mock_alert = create_mock_event(restaurant_id, "alerta_stock")

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.restaurant_dashboard_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_event_restaurant_repo, patch(
        "src.core.services.document_service.restaurant_repository"
    ) as mock_doc_restaurant_repo, patch(
        "src.core.services.resource_service.restaurant_repository"
    ) as mock_resource_restaurant_repo, patch(
        "src.core.services.inventory_service.restaurant_repository"
    ) as mock_inv_restaurant_repo, patch(
        "src.core.services.person_service.restaurant_repository"
    ) as mock_person_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo, patch(
        "src.core.services.document_service.document_repository"
    ) as mock_doc_repo, patch(
        "src.core.services.resource_service.resource_repository"
    ) as mock_resource_repo, patch(
        "src.core.services.inventory_service.inventory_movement_repository"
    ) as mock_inv_repo, patch(
        "src.core.services.person_service.person_repository"
    ) as mock_person_repo:
        # Auth mocks
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True

        # Restaurant access mocks
        for repo in [
            mock_restaurant_repo, mock_event_restaurant_repo,
            mock_doc_restaurant_repo, mock_resource_restaurant_repo,
            mock_inv_restaurant_repo, mock_person_restaurant_repo,
        ]:
            repo.get_user_restaurant_role.return_value = "admin"

        # Service data mocks
        mock_event_repo.get_tasks_by_date.return_value = [mock_task]
        mock_event_repo.get_pending_alerts.return_value = [mock_alert]
        mock_event_repo.count_completed_tasks.return_value = 3
        mock_doc_repo.get_expiring.return_value = [mock_doc]
        mock_doc_repo.count_active.return_value = 5
        mock_resource_repo.get_low_stock.return_value = [mock_resource]
        mock_resource_repo.count.return_value = 12
        mock_inv_repo.get_recent.return_value = [mock_movement]
        mock_person_repo.count_by_type.return_value = 8

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/restaurant-dashboard/{restaurant_id}/overview",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert "today_tasks" in data
        assert "upcoming_expirations" in data
        assert "low_stock_items" in data
        assert "recent_movements" in data
        assert "pending_alerts" in data
        assert "stats" in data

        stats = data["stats"]
        assert stats["total_employees"] == 8
        assert stats["total_resources"] == 12
        assert stats["active_documents"] == 5
        assert stats["tasks_completed_today"] == 3

        assert len(data["today_tasks"]) == 1
        assert len(data["upcoming_expirations"]) == 1
        assert len(data["low_stock_items"]) == 1
        assert len(data["recent_movements"]) == 1
        assert len(data["pending_alerts"]) == 1

        print("INFO [TestRestaurantDashboard]: test_dashboard_overview_success - PASSED")


@pytest.mark.asyncio
async def test_dashboard_overview_unauthenticated() -> None:
    """Test that unauthenticated request returns 401."""
    restaurant_id = uuid4()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"/api/restaurant-dashboard/{restaurant_id}/overview",
        )

    assert response.status_code == 401
    print("INFO [TestRestaurantDashboard]: test_dashboard_overview_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_dashboard_overview_access_denied() -> None:
    """Test that user without restaurant access gets 403."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.restaurant_dashboard_service.restaurant_repository"
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
                f"/api/restaurant-dashboard/{restaurant_id}/overview",
                headers={"Authorization": f"Bearer {token}"},
            )

    assert response.status_code == 403
    print("INFO [TestRestaurantDashboard]: test_dashboard_overview_access_denied - PASSED")


@pytest.mark.asyncio
async def test_dashboard_overview_empty_restaurant() -> None:
    """Test that dashboard with empty restaurant returns zero stats and empty lists."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.restaurant_dashboard_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.event_service.restaurant_repository"
    ) as mock_event_restaurant_repo, patch(
        "src.core.services.document_service.restaurant_repository"
    ) as mock_doc_restaurant_repo, patch(
        "src.core.services.resource_service.restaurant_repository"
    ) as mock_resource_restaurant_repo, patch(
        "src.core.services.inventory_service.restaurant_repository"
    ) as mock_inv_restaurant_repo, patch(
        "src.core.services.person_service.restaurant_repository"
    ) as mock_person_restaurant_repo, patch(
        "src.core.services.event_service.event_repository"
    ) as mock_event_repo, patch(
        "src.core.services.document_service.document_repository"
    ) as mock_doc_repo, patch(
        "src.core.services.resource_service.resource_repository"
    ) as mock_resource_repo, patch(
        "src.core.services.inventory_service.inventory_movement_repository"
    ) as mock_inv_repo, patch(
        "src.core.services.person_service.person_repository"
    ) as mock_person_repo:
        # Auth mocks
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True

        # Restaurant access mocks
        for repo in [
            mock_restaurant_repo, mock_event_restaurant_repo,
            mock_doc_restaurant_repo, mock_resource_restaurant_repo,
            mock_inv_restaurant_repo, mock_person_restaurant_repo,
        ]:
            repo.get_user_restaurant_role.return_value = "admin"

        # All empty/zero
        mock_event_repo.get_tasks_by_date.return_value = []
        mock_event_repo.get_pending_alerts.return_value = []
        mock_event_repo.count_completed_tasks.return_value = 0
        mock_doc_repo.get_expiring.return_value = []
        mock_doc_repo.count_active.return_value = 0
        mock_resource_repo.get_low_stock.return_value = []
        mock_resource_repo.count.return_value = 0
        mock_inv_repo.get_recent.return_value = []
        mock_person_repo.count_by_type.return_value = 0

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/restaurant-dashboard/{restaurant_id}/overview",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data["today_tasks"]) == 0
        assert len(data["upcoming_expirations"]) == 0
        assert len(data["low_stock_items"]) == 0
        assert len(data["recent_movements"]) == 0
        assert len(data["pending_alerts"]) == 0
        assert data["stats"]["total_employees"] == 0
        assert data["stats"]["total_resources"] == 0
        assert data["stats"]["active_documents"] == 0
        assert data["stats"]["tasks_completed_today"] == 0

        print("INFO [TestRestaurantDashboard]: test_dashboard_overview_empty_restaurant - PASSED")
