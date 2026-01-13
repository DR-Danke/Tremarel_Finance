"""
Finance Tracker API - FastAPI Application Entry Point

This is the main entry point for the Finance Tracker backend API.
Run with: python -m uvicorn main:app --reload --port 8000
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.adapter.rest.auth_routes import router as auth_router
from src.adapter.rest.entity_routes import router as entity_router
from src.adapter.rest.category_routes import router as category_router
from src.adapter.rest.transaction_routes import router as transaction_router
from src.adapter.rest.dashboard_routes import router as dashboard_router
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

# Register routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(entity_router)
app.include_router(category_router)
app.include_router(transaction_router)
app.include_router(dashboard_router)

print("INFO [Main]: Auth router registered")
print("INFO [Main]: Entity router registered")
print("INFO [Main]: Category router registered")
print("INFO [Main]: Transaction router registered")
print("INFO [Main]: Dashboard router registered")
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
