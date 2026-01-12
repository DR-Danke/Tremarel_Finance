"""Application settings using Pydantic Settings for environment variable management."""

import json
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/finance_tracker"

    # JWT Authentication
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS - JSON array format: ["http://localhost:5173"]
    CORS_ORIGINS: str = '["http://localhost:5173"]'

    # Application
    APP_NAME: str = "Finance Tracker API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    def get_cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS JSON string into list."""
        try:
            origins = json.loads(self.CORS_ORIGINS)
            if isinstance(origins, list):
                return origins
            return [self.CORS_ORIGINS]
        except json.JSONDecodeError:
            print("WARN [Settings]: Invalid CORS_ORIGINS format, using default")
            return ["http://localhost:5173"]


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    print("INFO [Settings]: Loading application settings")
    return Settings()
