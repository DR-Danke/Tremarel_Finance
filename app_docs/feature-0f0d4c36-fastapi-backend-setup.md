# FastAPI Backend Project Setup

**ADW ID:** 0f0d4c36
**Date:** 2026-01-12
**Specification:** specs/issue-1-adw-0f0d4c36-sdlc_planner-fastapi-backend-project-setup.md

## Overview

This feature establishes the foundational FastAPI backend structure for the Finance Tracker application. It creates a complete project skeleton following Clean Architecture principles, ready for building authentication, transactions, and other API features in subsequent waves.

## What Was Built

- Complete Server folder structure following Clean Architecture
- FastAPI application entry point with CORS configuration
- Health check endpoint at `/api/health`
- Pydantic-based settings management
- Database connection placeholder using SQLAlchemy
- Authentication dependency placeholders
- Comprehensive test suite for health endpoint
- All required Python dependencies

## Technical Implementation

### Files Modified

- `apps/Server/main.py`: FastAPI application entry point with lifespan events, CORS middleware, and router registration
- `apps/Server/requirements.txt`: Python dependencies (FastAPI, uvicorn, SQLAlchemy, pydantic, JWT, bcrypt, etc.)
- `apps/Server/.env.sample`: Environment variables documentation
- `apps/Server/src/config/settings.py`: Pydantic Settings class for environment variable management
- `apps/Server/src/config/database.py`: SQLAlchemy engine and session configuration placeholder
- `apps/Server/src/adapter/rest/health_routes.py`: Health check endpoint returning status, timestamp, version
- `apps/Server/src/adapter/rest/dependencies.py`: Placeholder for `get_current_user` and `get_db` dependencies
- `apps/Server/tests/test_health.py`: Pytest tests for health endpoint validation

### Key Changes

- **Clean Architecture Structure**: Created `adapter/rest`, `core/services`, `repository`, `interface`, `models`, and `config` folders with proper `__init__.py` files
- **CORS Configuration**: Supports JSON array format for `CORS_ORIGINS` environment variable, with safe parsing and fallback
- **Lifespan Events**: Uses modern FastAPI `asynccontextmanager` pattern for startup/shutdown logging
- **Settings Caching**: Uses `@lru_cache()` to cache settings and avoid redundant environment parsing
- **Type Hints**: All functions include proper type annotations per project standards

## How to Use

1. Navigate to the Server directory:
   ```bash
   cd apps/Server
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.sample` to `.env` and configure environment variables

5. Start the development server:
   ```bash
   python -m uvicorn main:app --reload --port 8000
   ```

6. Access the API:
   - Health check: http://localhost:8000/api/health
   - API documentation: http://localhost:8000/docs
   - OpenAPI schema: http://localhost:8000/openapi.json

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://user:password@localhost:5432/finance_tracker` | PostgreSQL connection string |
| `JWT_SECRET_KEY` | `your-secret-key-change-in-production` | Secret key for JWT signing |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `JWT_EXPIRE_MINUTES` | `1440` | JWT token expiration (24 hours) |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | JSON array of allowed origins |
| `APP_NAME` | `Finance Tracker API` | Application name |
| `APP_VERSION` | `1.0.0` | Application version |
| `DEBUG` | `false` | Debug mode flag |

## Testing

Run the test suite:
```bash
cd apps/Server
python -m pytest tests/ -v
```

Tests validate:
- Health endpoint returns 200 status code
- Response contains `status`, `timestamp`, and `version` fields
- Status field equals "healthy"
- Timestamp is valid ISO format
- Version matches expected format

## Notes

- Python version must be 3.11.9 for Render deployment compatibility
- Database configuration is a placeholder - actual connection will be configured in subsequent waves
- Authentication dependencies (`get_current_user`) are placeholders for Wave 2 implementation
- All logging follows project standards: `print(f"INFO [ModuleName]: message")`
