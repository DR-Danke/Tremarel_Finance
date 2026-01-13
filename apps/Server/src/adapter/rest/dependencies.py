"""FastAPI dependency injection utilities."""

from typing import Any, Dict, Generator

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
) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user from JWT token.

    Extracts and validates the Bearer token from the Authorization header,
    decodes the JWT, and returns the user information.

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        Dict containing user information from token (id, email, role)

    Raises:
        HTTPException: 401 if token is invalid, expired, or missing
    """
    print("INFO [Dependencies]: Validating user token")

    token = credentials.credentials
    user_data = auth_service.decode_token(token)

    if user_data is None:
        print("ERROR [Dependencies]: Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"INFO [Dependencies]: Token validated for user {user_data['email']}")
    return user_data
