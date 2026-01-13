"""FastAPI dependency injection utilities."""

from typing import Any, Dict, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.config.database import SessionLocal

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

    This is a placeholder implementation. Full JWT validation will be
    implemented in Wave 2 (Authentication).

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        Dict containing user information from token

    Raises:
        HTTPException: If token is invalid or missing
    """
    print("INFO [Dependencies]: Validating user token")

    # Placeholder: In Wave 2, this will decode and validate the JWT token
    # For now, raise an error indicating auth is not yet implemented
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not yet implemented. Coming in Wave 2.",
    )
