"""Health check endpoint routes."""

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["Health"])


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    timestamp: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns the current health status of the API.

    Returns:
        HealthResponse: API health status with timestamp and version
    """
    print("INFO [HealthRoutes]: Health check requested")
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
    )
