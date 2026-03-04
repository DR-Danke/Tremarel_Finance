"""Tests for document API endpoints."""

from datetime import date, timedelta
from typing import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from main import app
from src.adapter.rest.dependencies import get_db
from src.models.document import Document
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
    doc_type: str = "contrato",
    file_url: str = None,
    issue_date: date = None,
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
    document.file_url = file_url
    document.issue_date = issue_date
    document.expiration_date = expiration_date
    document.person_id = person_id
    document.description = description
    document.processing_status = None
    document.processing_result = None
    document.created_at = MagicMock()
    document.updated_at = None
    return document


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
# Document Creation Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_document_success() -> None:
    """Test that valid document creation returns 201."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_document = create_mock_document(restaurant_id=restaurant_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.document_service.document_repository"
    ) as mock_document_repo:
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
                    "description": "Test contract",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "contrato"
        assert "expiration_status" in data
        print("INFO [TestDocumentAPI]: test_create_document_success - PASSED")


@pytest.mark.asyncio
async def test_create_document_unauthenticated() -> None:
    """Test that unauthenticated request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/documents",
            data={
                "restaurant_id": str(uuid4()),
                "type": "contrato",
            },
        )

    assert response.status_code == 401
    print("INFO [TestDocumentAPI]: test_create_document_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_create_document_no_restaurant_access() -> None:
    """Test that user without restaurant access gets 403."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.restaurant_repository"
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
                "/api/documents",
                data={
                    "restaurant_id": str(restaurant_id),
                    "type": "contrato",
                },
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestDocumentAPI]: test_create_document_no_restaurant_access - PASSED")


# ============================================================================
# List Documents Tests
# ============================================================================


@pytest.mark.asyncio
async def test_list_documents_success() -> None:
    """Test that listing documents returns restaurant's documents."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_d1 = create_mock_document(doc_type="contrato", restaurant_id=restaurant_id)
    mock_d2 = create_mock_document(doc_type="permiso", restaurant_id=restaurant_id)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.document_service.document_repository"
    ) as mock_document_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_document_repo.get_by_restaurant.return_value = [mock_d1, mock_d2]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/documents?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        print("INFO [TestDocumentAPI]: test_list_documents_success - PASSED")


@pytest.mark.asyncio
async def test_list_documents_unauthenticated() -> None:
    """Test that unauthenticated list request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"/api/documents?restaurant_id={uuid4()}",
        )

    assert response.status_code == 401
    print("INFO [TestDocumentAPI]: test_list_documents_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_list_documents_no_access() -> None:
    """Test that user without restaurant access gets 403 on list."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.restaurant_repository"
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
                f"/api/documents?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestDocumentAPI]: test_list_documents_no_access - PASSED")


# ============================================================================
# Get Document Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_document_success() -> None:
    """Test that getting document works for authorized users."""
    mock_user = create_mock_user()
    mock_document = create_mock_document()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.document_service.document_repository"
    ) as mock_document_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_document_repo.get_by_id.return_value = mock_document
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/documents/{mock_document.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["type"] == mock_document.type
        assert "expiration_status" in data
        print("INFO [TestDocumentAPI]: test_get_document_success - PASSED")


@pytest.mark.asyncio
async def test_get_document_not_found() -> None:
    """Test that getting nonexistent document returns 404."""
    mock_user = create_mock_user()
    document_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.document_repository"
    ) as mock_document_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_document_repo.get_by_id.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/documents/{document_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        print("INFO [TestDocumentAPI]: test_get_document_not_found - PASSED")


@pytest.mark.asyncio
async def test_get_document_unauthenticated() -> None:
    """Test that unauthenticated get returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"/api/documents/{uuid4()}",
        )

    assert response.status_code == 401
    print("INFO [TestDocumentAPI]: test_get_document_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_get_document_no_access() -> None:
    """Test that user without restaurant access gets 403."""
    mock_user = create_mock_user()
    mock_document = create_mock_document()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.document_service.document_repository"
    ) as mock_document_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_document_repo.get_by_id.return_value = mock_document
        mock_restaurant_repo.get_user_restaurant_role.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/documents/{mock_document.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestDocumentAPI]: test_get_document_no_access - PASSED")


# ============================================================================
# Update Document Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_document_success() -> None:
    """Test that authorized user can update document."""
    mock_user = create_mock_user()
    mock_document = create_mock_document()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.document_service.document_repository"
    ) as mock_document_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_document_repo.get_by_id.return_value = mock_document
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_document_repo.update.return_value = mock_document

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.put(
                f"/api/documents/{mock_document.id}",
                json={"type": "permiso", "description": "Updated description"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        print("INFO [TestDocumentAPI]: test_update_document_success - PASSED")


@pytest.mark.asyncio
async def test_update_document_not_found() -> None:
    """Test that updating nonexistent document returns 404."""
    mock_user = create_mock_user()
    document_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.document_repository"
    ) as mock_document_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_document_repo.get_by_id.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.put(
                f"/api/documents/{document_id}",
                json={"type": "licencia"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        print("INFO [TestDocumentAPI]: test_update_document_not_found - PASSED")


@pytest.mark.asyncio
async def test_update_document_unauthenticated() -> None:
    """Test that unauthenticated update returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.put(
            f"/api/documents/{uuid4()}",
            json={"type": "licencia"},
        )

    assert response.status_code == 401
    print("INFO [TestDocumentAPI]: test_update_document_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_update_document_no_access() -> None:
    """Test that user without restaurant access cannot update."""
    mock_user = create_mock_user()
    mock_document = create_mock_document()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.document_service.document_repository"
    ) as mock_document_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_document_repo.get_by_id.return_value = mock_document
        mock_restaurant_repo.get_user_restaurant_role.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.put(
                f"/api/documents/{mock_document.id}",
                json={"description": "Updated"},
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestDocumentAPI]: test_update_document_no_access - PASSED")


# ============================================================================
# Delete Document Tests
# ============================================================================


@pytest.mark.asyncio
async def test_delete_document_success() -> None:
    """Test that authorized user can delete document."""
    mock_user = create_mock_user()
    mock_document = create_mock_document()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.document_service.document_repository"
    ) as mock_document_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_document_repo.get_by_id.return_value = mock_document
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_document_repo.delete.return_value = True

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.delete(
                f"/api/documents/{mock_document.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 204
        print("INFO [TestDocumentAPI]: test_delete_document_success - PASSED")


@pytest.mark.asyncio
async def test_delete_document_not_found() -> None:
    """Test that deleting nonexistent document returns 404."""
    mock_user = create_mock_user()
    document_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.document_repository"
    ) as mock_document_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_document_repo.get_by_id.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.delete(
                f"/api/documents/{document_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        print("INFO [TestDocumentAPI]: test_delete_document_not_found - PASSED")


@pytest.mark.asyncio
async def test_delete_document_unauthenticated() -> None:
    """Test that unauthenticated delete returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.delete(
            f"/api/documents/{uuid4()}",
        )

    assert response.status_code == 401
    print("INFO [TestDocumentAPI]: test_delete_document_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_delete_document_no_access() -> None:
    """Test that user without restaurant access cannot delete."""
    mock_user = create_mock_user()
    mock_document = create_mock_document()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.restaurant_repository"
    ) as mock_restaurant_repo, patch(
        "src.core.services.document_service.document_repository"
    ) as mock_document_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_document_repo.get_by_id.return_value = mock_document
        mock_restaurant_repo.get_user_restaurant_role.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.delete(
                f"/api/documents/{mock_document.id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestDocumentAPI]: test_delete_document_no_access - PASSED")


# ============================================================================
# Expiring Documents Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_expiring_documents_success() -> None:
    """Test that expiring endpoint returns expiring documents."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_expiring = create_mock_document(
        doc_type="licencia",
        expiration_date=date.today() + timedelta(days=10),
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
    ) as mock_document_repo:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"
        mock_document_repo.get_expiring.return_value = [mock_expiring]

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/documents/expiring?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        print("INFO [TestDocumentAPI]: test_get_expiring_documents_success - PASSED")


@pytest.mark.asyncio
async def test_get_expiring_documents_unauthenticated() -> None:
    """Test that unauthenticated expiring request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"/api/documents/expiring?restaurant_id={uuid4()}",
        )

    assert response.status_code == 401
    print("INFO [TestDocumentAPI]: test_get_expiring_documents_unauthenticated - PASSED")


@pytest.mark.asyncio
async def test_get_expiring_documents_no_access() -> None:
    """Test that user without restaurant access gets 403 on expiring."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.core.services.document_service.restaurant_repository"
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
                f"/api/documents/expiring?restaurant_id={restaurant_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestDocumentAPI]: test_get_expiring_documents_no_access - PASSED")
