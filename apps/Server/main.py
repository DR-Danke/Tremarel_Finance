"""
Finance Tracker API - FastAPI Application Entry Point

This is the main entry point for the Finance Tracker backend API.
Run with: python -m uvicorn main:app --reload --port 8000
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.adapter.rest.auth_routes import router as auth_router
from src.adapter.rest.entity_routes import router as entity_router
from src.adapter.rest.category_routes import router as category_router
from src.adapter.rest.transaction_routes import router as transaction_router
from src.adapter.rest.budget_routes import router as budget_router
from src.adapter.rest.recurring_template_routes import router as recurring_template_router
from src.adapter.rest.dashboard_routes import router as dashboard_router
from src.adapter.rest.reports_routes import router as reports_router
from src.adapter.rest.health_routes import router as health_router
from src.config.settings import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan events handler.

    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    print(f"INFO [Main]: Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"INFO [Main]: Debug mode: {settings.DEBUG}")
    print(f"INFO [Main]: CORS origins: {settings.get_cors_origins()}")
    yield
    # Shutdown
    print(f"INFO [Main]: Shutting down {settings.APP_NAME}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Full-stack income/expense tracking application for family and startup management",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _make_serializable(obj):
    """Convert objects to JSON-serializable format."""
    from decimal import Decimal
    from uuid import UUID
    from datetime import datetime, date

    if isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_make_serializable(item) for item in obj]
    elif isinstance(obj, Decimal):
        return str(obj)
    elif isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Exception):
        return str(obj)
    return obj


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handle FastAPI request validation errors with proper CORS headers.

    Catches validation errors from request body, query params, etc.
    and returns a proper JSON response that the CORS middleware can process.
    """
    print(f"ERROR [Main]: Request validation error: {exc.errors()}")
    serializable_errors = _make_serializable(exc.errors())
    return JSONResponse(
        status_code=422,
        content={"detail": serializable_errors}
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors with proper CORS headers.

    Catches validation errors from Pydantic model validation
    and returns a proper JSON response that the CORS middleware can process.
    """
    print(f"ERROR [Main]: Pydantic validation error: {exc.errors()}")
    serializable_errors = _make_serializable(exc.errors())
    return JSONResponse(
        status_code=422,
        content={"detail": serializable_errors}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler to ensure CORS headers are always added.

    Catches all unhandled exceptions and returns a proper JSON response
    that the CORS middleware can process.
    """
    print(f"ERROR [Main]: Unhandled exception: {type(exc).__name__}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Register routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(entity_router)
app.include_router(category_router)
app.include_router(transaction_router)
app.include_router(budget_router)
app.include_router(recurring_template_router)
app.include_router(dashboard_router)
app.include_router(reports_router)

print("INFO [Main]: Auth router registered")
print("INFO [Main]: Entity router registered")
print("INFO [Main]: Category router registered")
print("INFO [Main]: Transaction router registered")
print("INFO [Main]: Budget router registered")
print("INFO [Main]: Recurring Template router registered")
print("INFO [Main]: Dashboard router registered")
print("INFO [Main]: Reports router registered")
print(f"INFO [Main]: {settings.APP_NAME} initialized")


if __name__ == "__main__":
    import uvicorn

    print("INFO [Main]: Starting uvicorn server directly")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
