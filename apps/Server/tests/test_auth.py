"""Tests for authentication endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import MagicMock, patch
from uuid import uuid4

from main import app


class MockUser:
    """Mock user object for testing."""

    def __init__(
        self,
        email: str = "test@example.com",
        password_hash: str = "$2b$12$test",
        role: str = "user",
        is_active: bool = True,
    ):
        self.id = uuid4()
        self.email = email
        self.password_hash = password_hash
        self.first_name = "Test"
        self.last_name = "User"
        self.role = role
        self.is_active = is_active
        self.created_at = "2024-01-01T00:00:00Z"


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock()


@pytest.mark.asyncio
async def test_register_new_user() -> None:
    """Test that registration returns 201 with token for new user."""
    mock_user = MockUser()

    with patch(
        "src.adapter.rest.auth_routes.auth_service.register_user"
    ) as mock_register:
        mock_register.return_value = mock_user

        with patch(
            "src.adapter.rest.auth_routes.auth_service.create_access_token"
        ) as mock_token:
            mock_token.return_value = "test.jwt.token"

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/auth/register",
                    json={
                        "email": "newuser@example.com",
                        "password": "testpass123",
                        "first_name": "New",
                        "last_name": "User",
                    },
                )

    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    print("INFO [TestAuth]: test_register_new_user - PASSED")


@pytest.mark.asyncio
async def test_register_duplicate_email() -> None:
    """Test that registration returns 409 for duplicate email."""
    with patch(
        "src.adapter.rest.auth_routes.auth_service.register_user"
    ) as mock_register:
        mock_register.return_value = None  # Indicates email already exists

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/auth/register",
                json={
                    "email": "existing@example.com",
                    "password": "testpass123",
                },
            )

    assert response.status_code == 409
    data = response.json()
    assert "already registered" in data["detail"].lower()
    print("INFO [TestAuth]: test_register_duplicate_email - PASSED")


@pytest.mark.asyncio
async def test_register_invalid_email() -> None:
    """Test that registration returns 422 for invalid email format."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",
                "password": "testpass123",
            },
        )

    assert response.status_code == 422
    print("INFO [TestAuth]: test_register_invalid_email - PASSED")


@pytest.mark.asyncio
async def test_register_short_password() -> None:
    """Test that registration returns 422 for password less than 8 characters."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "short",
            },
        )

    assert response.status_code == 422
    print("INFO [TestAuth]: test_register_short_password - PASSED")


@pytest.mark.asyncio
async def test_login_valid_credentials() -> None:
    """Test that login returns 200 with token for valid credentials."""
    mock_user = MockUser()

    with patch(
        "src.adapter.rest.auth_routes.auth_service.authenticate_user"
    ) as mock_auth:
        mock_auth.return_value = mock_user

        with patch(
            "src.adapter.rest.auth_routes.auth_service.create_access_token"
        ) as mock_token:
            mock_token.return_value = "test.jwt.token"

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/auth/login",
                    json={
                        "email": "test@example.com",
                        "password": "testpass123",
                    },
                )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    print("INFO [TestAuth]: test_login_valid_credentials - PASSED")


@pytest.mark.asyncio
async def test_login_invalid_password() -> None:
    """Test that login returns 401 for invalid password."""
    with patch(
        "src.adapter.rest.auth_routes.auth_service.authenticate_user"
    ) as mock_auth:
        mock_auth.return_value = None  # Invalid credentials

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "wrongpassword",
                },
            )

    assert response.status_code == 401
    data = response.json()
    assert "invalid" in data["detail"].lower()
    print("INFO [TestAuth]: test_login_invalid_password - PASSED")


@pytest.mark.asyncio
async def test_login_nonexistent_user() -> None:
    """Test that login returns 401 for non-existent user."""
    with patch(
        "src.adapter.rest.auth_routes.auth_service.authenticate_user"
    ) as mock_auth:
        mock_auth.return_value = None  # User not found

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/auth/login",
                json={
                    "email": "nonexistent@example.com",
                    "password": "testpass123",
                },
            )

    assert response.status_code == 401
    data = response.json()
    # Should not reveal that user doesn't exist (security best practice)
    assert "invalid" in data["detail"].lower()
    print("INFO [TestAuth]: test_login_nonexistent_user - PASSED")


@pytest.mark.asyncio
async def test_get_me_with_valid_token() -> None:
    """Test that /me returns user data with valid token."""
    from datetime import datetime

    mock_user = MockUser()
    mock_user.created_at = datetime.utcnow()

    with patch(
        "src.adapter.rest.dependencies.auth_service.decode_token"
    ) as mock_decode:
        mock_decode.return_value = {
            "id": str(mock_user.id),
            "email": mock_user.email,
            "role": mock_user.role,
        }

        with patch(
            "src.repository.user_repository.UserRepository.get_by_id"
        ) as mock_get:
            mock_get.return_value = mock_user

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(
                    "/api/auth/me",
                    headers={"Authorization": "Bearer valid.jwt.token"},
                )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == mock_user.email
    assert data["role"] == mock_user.role
    print("INFO [TestAuth]: test_get_me_with_valid_token - PASSED")


@pytest.mark.asyncio
async def test_get_me_without_token() -> None:
    """Test that /me returns 401 or 403 without token (auth required)."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/auth/me")

    # HTTPBearer returns 401 or 403 when no credentials provided
    assert response.status_code in [401, 403]
    print("INFO [TestAuth]: test_get_me_without_token - PASSED")


@pytest.mark.asyncio
async def test_get_me_with_invalid_token() -> None:
    """Test that /me returns 401 with invalid token."""
    with patch(
        "src.adapter.rest.dependencies.auth_service.decode_token"
    ) as mock_decode:
        mock_decode.return_value = None  # Invalid token

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/auth/me",
                headers={"Authorization": "Bearer invalid.jwt.token"},
            )

    assert response.status_code == 401
    data = response.json()
    assert "invalid" in data["detail"].lower() or "expired" in data["detail"].lower()
    print("INFO [TestAuth]: test_get_me_with_invalid_token - PASSED")


@pytest.mark.asyncio
async def test_rbac_role_check_admin_allowed() -> None:
    """Test that admin role passes role check for admin-required endpoints."""
    from src.adapter.rest.rbac_dependencies import require_roles

    mock_user = {"id": str(uuid4()), "email": "admin@example.com", "role": "admin"}

    role_checker = require_roles(["admin"])

    # Should not raise exception
    result = await role_checker(mock_user)
    assert result["role"] == "admin"
    print("INFO [TestAuth]: test_rbac_role_check_admin_allowed - PASSED")


@pytest.mark.asyncio
async def test_rbac_role_check_user_denied() -> None:
    """Test that user role is denied for admin-only endpoints."""
    from fastapi import HTTPException
    from src.adapter.rest.rbac_dependencies import require_roles

    mock_user = {"id": str(uuid4()), "email": "user@example.com", "role": "user"}

    role_checker = require_roles(["admin"])

    with pytest.raises(HTTPException) as exc_info:
        await role_checker(mock_user)

    assert exc_info.value.status_code == 403
    print("INFO [TestAuth]: test_rbac_role_check_user_denied - PASSED")


@pytest.mark.asyncio
async def test_rbac_multiple_roles_allowed() -> None:
    """Test that manager role passes when admin or manager allowed."""
    from src.adapter.rest.rbac_dependencies import require_roles

    mock_user = {"id": str(uuid4()), "email": "manager@example.com", "role": "manager"}

    role_checker = require_roles(["admin", "manager"])

    # Should not raise exception
    result = await role_checker(mock_user)
    assert result["role"] == "manager"
    print("INFO [TestAuth]: test_rbac_multiple_roles_allowed - PASSED")


print("INFO [TestAuth]: Auth tests module loaded")
