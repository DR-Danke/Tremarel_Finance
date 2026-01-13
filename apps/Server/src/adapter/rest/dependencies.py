"""FastAPI dependency injection utilities."""

from typing import Any, Dict, Generator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.config.database import SessionLocal
from src.core.services.auth_service import auth_service

# HTTP Bearer token security scheme
security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    print("INFO [Dependencies]: Opening database session")
    try:
        yield db
    finally:
        db.close()
        print("INFO [Dependencies]: Closing database session")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        Dict containing user information from token

    Raises:
        HTTPException: If token is invalid, expired, or user not found
    """
    print("INFO [Dependencies]: Validating user token")

    token = credentials.credentials
    payload = auth_service.decode_access_token(token)

    if payload is None:
        print("ERROR [Dependencies]: Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user_id from payload
    user_id_str = payload.get("sub")
    if user_id_str is None:
        print("ERROR [Dependencies]: Token payload missing user_id")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        print("ERROR [Dependencies]: Invalid user_id format in token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    user = auth_service.get_user_by_id(db, user_id)
    if user is None:
        print(f"ERROR [Dependencies]: User {user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        print(f"ERROR [Dependencies]: User {user_id} is inactive")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"INFO [Dependencies]: User {user.email} authenticated successfully")
    return {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "is_active": user.is_active,
    }
