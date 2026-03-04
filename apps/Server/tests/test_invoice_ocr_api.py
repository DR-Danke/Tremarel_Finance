"""API integration tests for invoice OCR processing endpoints."""

from decimal import Decimal
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from main import app
from src.adapter.rest.dependencies import get_db
from src.models.document import Document
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


def create_mock_document(
    doc_type: str = "factura_proveedor",
    file_url: str = "uploads/documents/invoice.pdf",
    restaurant_id=None,
    processing_status=None,
    processing_result=None,
) -> Document:
    """Create a mock document for invoice OCR tests."""
    document = MagicMock(spec=Document)
    document.id = uuid4()
    document.restaurant_id = restaurant_id or uuid4()
    document.type = doc_type
    document.file_url = file_url
    document.issue_date = None
    document.expiration_date = None
    document.person_id = None
    document.description = "Test supplier invoice"
    document.processing_status = processing_status
    document.processing_result = processing_result
    document.created_at = MagicMock()
    document.updated_at = None
    return document


def create_mock_resource(
    name: str = "Tomate",
    restaurant_id=None,
    current_stock: Decimal = Decimal("50.0"),
    last_unit_cost: Decimal = Decimal("2.00"),
) -> Resource:
    """Create a mock resource."""
    resource = MagicMock(spec=Resource)
    resource.id = uuid4()
    resource.restaurant_id = restaurant_id or uuid4()
    resource.type = "producto"
    resource.name = name
    resource.unit = "kg"
    resource.current_stock = current_stock
    resource.minimum_stock = Decimal("5.0")
    resource.last_unit_cost = last_unit_cost
    return resource


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
# POST /api/documents/{id}/process-invoice Tests
# ============================================================================


@pytest.mark.asyncio
async def test_process_invoice_success() -> None:
    """Test successful invoice OCR processing with matched and unmatched items."""
    mock_user = create_mock_user()
    restaurant_id = uuid4()
    mock_document = create_mock_document(restaurant_id=restaurant_id)
    mock_resource = create_mock_resource(name="Tomate", restaurant_id=restaurant_id)

    result_dict = {
        "document_id": str(mock_document.id),
        "matched_count": 1,
        "unmatched_count": 1,
        "matched_items": [
            {
                "item": {
                    "product_name": "Tomate",
                    "quantity": "10.0",
                    "unit": "kg",
                    "unit_price": "2.50",
                    "supplier_name": "Distribuidora ABC",
                },
                "resource_id": str(mock_resource.id),
            }
        ],
        "unmatched_items": [
            {
                "product_name": "Salsa BBQ Especial",
                "quantity": "3.0",
                "unit": "litro",
                "unit_price": "12.00",
                "supplier_name": "Distribuidora ABC",
            }
        ],
        "processing_status": "completed",
    }

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.adapter.rest.document_routes.invoice_processor"
    ) as mock_processor:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_processor.process_invoice_document.return_value = result_dict

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                f"/api/documents/{mock_document.id}/process-invoice",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["matched_count"] == 1
        assert data["unmatched_count"] == 1
        assert data["processing_status"] == "completed"
        assert len(data["matched_items"]) == 1
        assert len(data["unmatched_items"]) == 1
        print("INFO [TestInvoiceOCRAPI]: test_process_invoice_success - PASSED")


@pytest.mark.asyncio
async def test_process_invoice_document_not_found() -> None:
    """Test that processing a non-existent document returns 404."""
    mock_user = create_mock_user()
    document_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.adapter.rest.document_routes.invoice_processor"
    ) as mock_processor:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_processor.process_invoice_document.side_effect = ValueError("Document not found")

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                f"/api/documents/{document_id}/process-invoice",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        print("INFO [TestInvoiceOCRAPI]: test_process_invoice_document_not_found - PASSED")


@pytest.mark.asyncio
async def test_process_invoice_wrong_type() -> None:
    """Test that processing a non-factura_proveedor document returns 400."""
    mock_user = create_mock_user()
    document_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.adapter.rest.document_routes.invoice_processor"
    ) as mock_processor:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_processor.process_invoice_document.side_effect = ValueError(
            "Only documents of type 'factura_proveedor' can be processed"
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                f"/api/documents/{document_id}/process-invoice",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 400
        print("INFO [TestInvoiceOCRAPI]: test_process_invoice_wrong_type - PASSED")


@pytest.mark.asyncio
async def test_process_invoice_no_file_url() -> None:
    """Test that processing a document without file_url returns 400."""
    mock_user = create_mock_user()
    document_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.adapter.rest.document_routes.invoice_processor"
    ) as mock_processor:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_processor.process_invoice_document.side_effect = ValueError(
            "Document has no file attached for OCR processing"
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                f"/api/documents/{document_id}/process-invoice",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 400
        print("INFO [TestInvoiceOCRAPI]: test_process_invoice_no_file_url - PASSED")


@pytest.mark.asyncio
async def test_process_invoice_no_restaurant_access() -> None:
    """Test that user without restaurant access gets 403."""
    mock_user = create_mock_user()
    document_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_auth_repo, patch(
        "src.core.services.auth_service.bcrypt"
    ) as mock_bcrypt, patch(
        "src.adapter.rest.document_routes.invoice_processor"
    ) as mock_processor:
        mock_auth_repo.get_user_by_email.return_value = mock_user
        mock_auth_repo.get_user_by_id.return_value = mock_user
        mock_bcrypt.checkpw.return_value = True
        mock_processor.process_invoice_document.side_effect = PermissionError(
            "User doesn't have access to this restaurant"
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.post(
                f"/api/documents/{document_id}/process-invoice",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestInvoiceOCRAPI]: test_process_invoice_no_restaurant_access - PASSED")


@pytest.mark.asyncio
async def test_process_invoice_unauthenticated() -> None:
    """Test that unauthenticated request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            f"/api/documents/{uuid4()}/process-invoice",
        )

    assert response.status_code == 401
    print("INFO [TestInvoiceOCRAPI]: test_process_invoice_unauthenticated - PASSED")


# ============================================================================
# GET /api/documents/{id}/processing-result Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_processing_result_success() -> None:
    """Test retrieving processing results for a processed document."""
    mock_user = create_mock_user()
    mock_document = create_mock_document(
        processing_status="completed",
        processing_result={
            "matched_count": 2,
            "unmatched_count": 1,
            "matched_items": [],
            "unmatched_items": [],
        },
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
        mock_document_repo.get_by_id.return_value = mock_document
        mock_restaurant_repo.get_user_restaurant_role.return_value = "admin"

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            token = await get_auth_token(client, mock_user)
            response = await client.get(
                f"/api/documents/{mock_document.id}/processing-result",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["processing_status"] == "completed"
        assert data["processing_result"]["matched_count"] == 2
        print("INFO [TestInvoiceOCRAPI]: test_get_processing_result_success - PASSED")


@pytest.mark.asyncio
async def test_get_processing_result_not_found() -> None:
    """Test that getting processing result for non-existent document returns 404."""
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
                f"/api/documents/{document_id}/processing-result",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 404
        print("INFO [TestInvoiceOCRAPI]: test_get_processing_result_not_found - PASSED")


@pytest.mark.asyncio
async def test_get_processing_result_no_access() -> None:
    """Test that user without restaurant access gets 403 on processing result."""
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
                f"/api/documents/{mock_document.id}/processing-result",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 403
        print("INFO [TestInvoiceOCRAPI]: test_get_processing_result_no_access - PASSED")


@pytest.mark.asyncio
async def test_get_processing_result_unauthenticated() -> None:
    """Test that unauthenticated request returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            f"/api/documents/{uuid4()}/processing-result",
        )

    assert response.status_code == 401
    print("INFO [TestInvoiceOCRAPI]: test_get_processing_result_unauthenticated - PASSED")
