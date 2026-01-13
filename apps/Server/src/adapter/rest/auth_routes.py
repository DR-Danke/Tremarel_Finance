"""Authentication endpoint routes."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.core.services.auth_service import auth_service
from src.interface.auth_dto import (
    TokenResponseDTO,
    UserLoginDTO,
    UserRegisterDTO,
    UserResponseDTO,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponseDTO, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegisterDTO,
    db: Session = Depends(get_db),
) -> TokenResponseDTO:
    """
    Register a new user.

    Creates a new user account and returns a JWT token.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        TokenResponseDTO: JWT token and user information

    Raises:
        HTTPException: 400 if email already registered
    """
    print(f"INFO [AuthRoutes]: Registration request for email {user_data.email}")

    try:
        user = auth_service.register_user(db, user_data)
    except ValueError as e:
        print(f"ERROR [AuthRoutes]: Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    print(f"INFO [AuthRoutes]: User {user.id} registered successfully")
    return TokenResponseDTO(
        access_token=access_token,
        token_type="bearer",
        user=UserResponseDTO.model_validate(user),
    )


@router.post("/login", response_model=TokenResponseDTO)
async def login(
    credentials: UserLoginDTO,
    db: Session = Depends(get_db),
) -> TokenResponseDTO:
    """
    Login an existing user.

    Validates credentials and returns a JWT token.

    Args:
        credentials: User login credentials
        db: Database session

    Returns:
        TokenResponseDTO: JWT token and user information

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    print(f"INFO [AuthRoutes]: Login request for email {credentials.email}")

    user = auth_service.authenticate_user(db, credentials.email, credentials.password)
    if user is None:
        print(f"ERROR [AuthRoutes]: Login failed for email {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "email": user.email}
    )

    print(f"INFO [AuthRoutes]: User {user.id} logged in successfully")
    return TokenResponseDTO(
        access_token=access_token,
        token_type="bearer",
        user=UserResponseDTO.model_validate(user),
    )


@router.get("/me", response_model=UserResponseDTO)
async def get_me(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> UserResponseDTO:
    """
    Get current user information.

    Returns information about the currently authenticated user.

    Args:
        current_user: Current authenticated user from JWT token

    Returns:
        UserResponseDTO: Current user information
    """
    print(f"INFO [AuthRoutes]: Get current user request for {current_user['email']}")

    return UserResponseDTO(
        id=current_user["id"],
        email=current_user["email"],
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
        role=current_user["role"],
        is_active=current_user["is_active"],
    )
