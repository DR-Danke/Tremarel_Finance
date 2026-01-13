"""Authentication API endpoints."""

from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.core.services.auth_service import auth_service
from src.interface.auth_dto import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from src.repository.user_repository import user_repository

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account and return a JWT access token.",
)
async def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Register a new user.

    Creates a new user account with the provided email and password.
    Returns a JWT access token for immediate authentication.

    Args:
        request: Registration data (email, password, optional first/last name)
        db: Database session

    Returns:
        TokenResponse with JWT access token

    Raises:
        HTTPException: 409 if email already registered
    """
    print(f"INFO [AuthRoutes]: Registration request for email {request.email}")

    user = auth_service.register_user(
        db=db,
        email=request.email,
        password=request.password,
        first_name=request.first_name,
        last_name=request.last_name,
    )

    if user is None:
        print(f"ERROR [AuthRoutes]: Registration failed - email already exists: {request.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Generate access token for the new user
    access_token = auth_service.create_access_token(
        user_id=str(user.id),
        email=user.email,
        role=user.role,
    )

    print(f"INFO [AuthRoutes]: User registered successfully: {user.email}")
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user with email and password, return JWT access token.",
)
async def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate a user.

    Validates user credentials and returns a JWT access token.

    Args:
        request: Login credentials (email, password)
        db: Database session

    Returns:
        TokenResponse with JWT access token

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    print(f"INFO [AuthRoutes]: Login request for email {request.email}")

    user = auth_service.authenticate_user(
        db=db,
        email=request.email,
        password=request.password,
    )

    if user is None:
        # Use generic message for security (don't reveal if email exists)
        print(f"ERROR [AuthRoutes]: Login failed for email {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate access token
    access_token = auth_service.create_access_token(
        user_id=str(user.id),
        email=user.email,
        role=user.role,
    )

    print(f"INFO [AuthRoutes]: User logged in successfully: {user.email}")
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get the currently authenticated user's information.",
)
async def get_me(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Get current authenticated user information.

    Returns the user data from the JWT token. Requires valid authentication.

    Args:
        current_user: User data from JWT token
        db: Database session

    Returns:
        UserResponse with user information

    Raises:
        HTTPException: 401 if not authenticated or token invalid
    """
    print(f"INFO [AuthRoutes]: Get me request for user {current_user['email']}")

    # Get full user data from database
    user = user_repository.get_by_id(db, UUID(current_user["id"]))

    if user is None:
        print(f"ERROR [AuthRoutes]: User not found in database: {current_user['id']}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"INFO [AuthRoutes]: Returning user data for {user.email}")
    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )


print("INFO [AuthRoutes]: Auth routes loaded")
