"""Tests for authentication endpoints."""

from typing import Generator
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import Session

from main import app
from src.adapter.rest.dependencies import get_db
from src.models.user import User


# Mock database session for tests
def get_mock_db() -> Generator[MagicMock, None, None]:
    """Get a mock database session for testing."""
    mock_db = MagicMock(spec=Session)
    yield mock_db


# Override the get_db dependency for all tests
app.dependency_overrides[get_db] = get_mock_db


# Pre-computed bcrypt hash for "password123" - generated offline
# This avoids running bcrypt during test fixture creation
PASSWORD_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4Y1L.VIxMfp2r2Ve"
ADMIN_PASSWORD_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4Y1L.VIxMfp2r2Ve"


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


# ============================================================================
# Registration Tests
# ============================================================================


@pytest.mark.asyncio
async def test_register_success() -> None:
    """Test that valid registration returns 201 and token."""
    new_user_id = uuid4()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_repo, patch(
        "src.core.services.auth_service.pwd_context"
    ) as mock_pwd_context:
        # Mock repository to return None (no existing user)
        mock_repo.get_user_by_email.return_value = None

        # Mock password hashing
        mock_pwd_context.hash.return_value = PASSWORD_HASH

        # Create a proper mock user object for the return
        mock_user = MagicMock(spec=User)
        mock_user.id = new_user_id
        mock_user.email = "newuser@example.com"
        mock_user.password_hash = PASSWORD_HASH
        mock_user.first_name = "New"
        mock_user.last_name = "User"
        mock_user.role = "user"
        mock_user.is_active = True

        mock_repo.create_user.return_value = mock_user

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/auth/register",
                json={
                    "email": "newuser@example.com",
                    "password": "password123",
                    "first_name": "New",
                    "last_name": "User",
                },
            )

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "newuser@example.com"
        print("INFO [TestAuth]: test_register_success - PASSED")


@pytest.mark.asyncio
async def test_register_duplicate_email() -> None:
    """Test that duplicate email returns 400."""
    with patch("src.core.services.auth_service.user_repository") as mock_repo:
        # Mock repository to return existing user
        existing_user = create_mock_user(email="existing@example.com")
        mock_repo.get_user_by_email.return_value = existing_user

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/auth/register",
                json={
                    "email": "existing@example.com",
                    "password": "password123",
                },
            )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
        print("INFO [TestAuth]: test_register_duplicate_email - PASSED")


@pytest.mark.asyncio
async def test_register_invalid_email() -> None:
    """Test that invalid email format returns 422."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "not-an-email",
                "password": "password123",
            },
        )

    assert response.status_code == 422
    print("INFO [TestAuth]: test_register_invalid_email - PASSED")


@pytest.mark.asyncio
async def test_register_weak_password() -> None:
    """Test that password < 8 chars returns 422."""
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
    print("INFO [TestAuth]: test_register_weak_password - PASSED")


# ============================================================================
# Login Tests
# ============================================================================


@pytest.mark.asyncio
async def test_login_success() -> None:
    """Test that valid credentials return 200 and token."""
    mock_user = create_mock_user()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_repo, patch(
        "src.core.services.auth_service.pwd_context"
    ) as mock_pwd_context:
        mock_repo.get_user_by_email.return_value = mock_user
        mock_pwd_context.verify.return_value = True

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "password123",
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"
        print("INFO [TestAuth]: test_login_success - PASSED")


@pytest.mark.asyncio
async def test_login_invalid_credentials() -> None:
    """Test that wrong password returns 401."""
    mock_user = create_mock_user()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_repo, patch(
        "src.core.services.auth_service.pwd_context"
    ) as mock_pwd_context:
        mock_repo.get_user_by_email.return_value = mock_user
        mock_pwd_context.verify.return_value = False  # Wrong password

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
        assert "Invalid email or password" in response.json()["detail"]
        print("INFO [TestAuth]: test_login_invalid_credentials - PASSED")


@pytest.mark.asyncio
async def test_login_nonexistent_user() -> None:
    """Test that unknown email returns 401."""
    with patch("src.core.services.auth_service.user_repository") as mock_repo:
        mock_repo.get_user_by_email.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/auth/login",
                json={
                    "email": "nonexistent@example.com",
                    "password": "password123",
                },
            )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
        print("INFO [TestAuth]: test_login_nonexistent_user - PASSED")


@pytest.mark.asyncio
async def test_login_inactive_user() -> None:
    """Test that inactive user cannot login."""
    mock_user = create_mock_user(is_active=False)

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_repo, patch(
        "src.core.services.auth_service.pwd_context"
    ) as mock_pwd_context:
        mock_repo.get_user_by_email.return_value = mock_user
        mock_pwd_context.verify.return_value = True  # Password is correct

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "password123",
                },
            )

        assert response.status_code == 401
        print("INFO [TestAuth]: test_login_inactive_user - PASSED")


# ============================================================================
# /me Endpoint Tests
# ============================================================================


@pytest.mark.asyncio
async def test_me_authenticated() -> None:
    """Test that valid token returns user info."""
    mock_user = create_mock_user()

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_repo, patch(
        "src.core.services.auth_service.pwd_context"
    ) as mock_pwd_context:
        # Mock for login
        mock_repo.get_user_by_email.return_value = mock_user
        mock_repo.get_user_by_id.return_value = mock_user
        mock_pwd_context.verify.return_value = True

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Login to get token
            login_response = await client.post(
                "/api/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "password123",
                },
            )
            token = login_response.json()["access_token"]

            # Use token to get /me
            response = await client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["role"] == "user"
        print("INFO [TestAuth]: test_me_authenticated - PASSED")


@pytest.mark.asyncio
async def test_me_invalid_token() -> None:
    """Test that invalid token returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

    assert response.status_code == 401
    print("INFO [TestAuth]: test_me_invalid_token - PASSED")


@pytest.mark.asyncio
async def test_me_no_token() -> None:
    """Test that missing token returns 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/auth/me")

    # HTTPBearer returns 401 when credentials are not provided
    assert response.status_code == 401
    print("INFO [TestAuth]: test_me_no_token - PASSED")


# ============================================================================
# Auth Service Unit Tests
# ============================================================================


def test_jwt_token_creation() -> None:
    """Test JWT token creation."""
    from src.core.services.auth_service import auth_service

    data = {"sub": str(uuid4()), "email": "test@example.com"}
    token = auth_service.create_access_token(data)

    # Token should be a non-empty string
    assert isinstance(token, str)
    assert len(token) > 0
    print("INFO [TestAuth]: test_jwt_token_creation - PASSED")


def test_jwt_token_decoding() -> None:
    """Test JWT token decoding with valid token."""
    from src.core.services.auth_service import auth_service

    user_id = str(uuid4())
    data = {"sub": user_id, "email": "test@example.com"}
    token = auth_service.create_access_token(data)

    payload = auth_service.decode_access_token(token)

    assert payload is not None
    assert payload["sub"] == user_id
    assert payload["email"] == "test@example.com"
    assert "exp" in payload
    print("INFO [TestAuth]: test_jwt_token_decoding - PASSED")


def test_jwt_invalid_token() -> None:
    """Test JWT decoding with invalid token."""
    from src.core.services.auth_service import auth_service

    payload = auth_service.decode_access_token("invalid.token.here")
    assert payload is None
    print("INFO [TestAuth]: test_jwt_invalid_token - PASSED")


def test_jwt_malformed_token() -> None:
    """Test JWT decoding with malformed token."""
    from src.core.services.auth_service import auth_service

    payload = auth_service.decode_access_token("notavalidtoken")
    assert payload is None
    print("INFO [TestAuth]: test_jwt_malformed_token - PASSED")


# ============================================================================
# Password Hashing Tests (with mocking)
# ============================================================================


def test_password_hashing_with_mock() -> None:
    """Test password hashing and verification with mocking."""
    from src.core.services.auth_service import AuthService

    with patch("src.core.services.auth_service.pwd_context") as mock_pwd_context:
        mock_pwd_context.hash.return_value = PASSWORD_HASH
        mock_pwd_context.verify.return_value = True

        service = AuthService()
        password = "testpassword123"

        # Test hashing
        hashed = service.hash_password(password)
        assert hashed == PASSWORD_HASH

        # Test verification (returns True per mock)
        assert service.verify_password(password, hashed) is True
        print("INFO [TestAuth]: test_password_hashing_with_mock - PASSED")


def test_password_verification_failure_with_mock() -> None:
    """Test password verification failure with mocking."""
    from src.core.services.auth_service import AuthService

    with patch("src.core.services.auth_service.pwd_context") as mock_pwd_context:
        mock_pwd_context.verify.return_value = False

        service = AuthService()

        # Test verification failure
        assert service.verify_password("wrongpassword", PASSWORD_HASH) is False
        print("INFO [TestAuth]: test_password_verification_failure_with_mock - PASSED")


# ============================================================================
# RBAC Tests
# ============================================================================


@pytest.mark.asyncio
async def test_rbac_admin_access() -> None:
    """Test that admin can authenticate and get user info."""
    mock_admin = create_mock_user(email="admin@example.com", role="admin")

    with patch(
        "src.core.services.auth_service.user_repository"
    ) as mock_repo, patch(
        "src.core.services.auth_service.pwd_context"
    ) as mock_pwd_context:
        mock_repo.get_user_by_email.return_value = mock_admin
        mock_pwd_context.verify.return_value = True

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Login as admin
            login_response = await client.post(
                "/api/auth/login",
                json={
                    "email": "admin@example.com",
                    "password": "adminpassword",
                },
            )
            assert login_response.status_code == 200
            data = login_response.json()
            assert data["user"]["role"] == "admin"
            print("INFO [TestAuth]: test_rbac_admin_access - PASSED")
