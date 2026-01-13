# Feature: FastAPI Backend Project Setup

## Metadata
issue_number: `1`
adw_id: `0f0d4c36`
issue_json: `{"number":1,"title":"[FinanceTracker] Wave 1: Backend Project Setup","body":"..."}`

## Feature Description
Create the foundational FastAPI backend structure for the Finance Tracker application. This involves setting up the Server folder with a complete project structure following Clean Architecture principles, including folders for routes (adapter/rest), services (core/services), repositories (repository), models, and configuration (config). The backend will serve as the API layer for the full-stack income/expense tracking application.

## User Story
As a developer
I want to have a properly structured FastAPI backend
So that I can build the Finance Tracker API with clean separation of concerns and maintainable code

## Problem Statement
The Finance Tracker application requires a backend API to handle authentication, transactions, categories, budgets, and entities. Currently, no backend structure exists. We need to create a foundational FastAPI project that follows Clean Architecture and is ready for Render deployment.

## Solution Statement
Create the Server folder with a complete FastAPI project structure including:
- Main entry point (main.py) with CORS configuration
- Clean Architecture folder structure (adapter/rest, core/services, repository, models, config, interface)
- Health check endpoint at /api/health
- Requirements.txt with all necessary dependencies (FastAPI, uvicorn, psycopg2-binary, SQLAlchemy, python-jose, passlib, pydantic)
- Environment variable configuration
- Ready to run with uvicorn on port 8000

## Relevant Files
Use these files to implement the feature:

- `CLAUDE.md` - Contains the project architecture guidelines, code standards, backend structure requirements, and technology stack specifications
- `ai_docs/finance_tracker_implementation_prompts.md` - Contains the overall implementation plan and context for the Finance Tracker project

### New Files
- `apps/Server/main.py` - FastAPI application entry point with CORS configuration and router includes
- `apps/Server/requirements.txt` - Python dependencies for the backend
- `apps/Server/.env.sample` - Sample environment variables documentation
- `apps/Server/src/__init__.py` - Package init file
- `apps/Server/src/adapter/__init__.py` - Adapter layer init
- `apps/Server/src/adapter/rest/__init__.py` - REST adapter init
- `apps/Server/src/adapter/rest/health_routes.py` - Health check endpoint routes
- `apps/Server/src/adapter/rest/dependencies.py` - FastAPI dependency injection (placeholder for auth)
- `apps/Server/src/core/__init__.py` - Core layer init
- `apps/Server/src/core/services/__init__.py` - Services layer init
- `apps/Server/src/repository/__init__.py` - Repository layer init
- `apps/Server/src/interface/__init__.py` - Interface (DTOs) layer init
- `apps/Server/src/models/__init__.py` - Models layer init
- `apps/Server/src/config/__init__.py` - Config layer init
- `apps/Server/src/config/settings.py` - Application settings using environment variables
- `apps/Server/src/config/database.py` - Database connection configuration (placeholder)
- `apps/Server/tests/__init__.py` - Tests package init
- `apps/Server/tests/test_health.py` - Health check endpoint tests

## Implementation Plan
### Phase 1: Foundation
Set up the Server folder structure with all necessary directories and init files following Clean Architecture principles. Create the requirements.txt with all dependencies specified in CLAUDE.md.

### Phase 2: Core Implementation
Implement the main.py entry point with FastAPI app configuration, CORS middleware, and router registration. Create the health check endpoint and configuration modules for environment variables and database connection placeholders.

### Phase 3: Integration
Verify the server starts correctly with uvicorn, the health check endpoint responds, and the structure is ready for subsequent features (authentication, entities, transactions).

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Create Server Directory Structure
- Create the Server folder at the root level
- Create all subdirectories following Clean Architecture:
  - `apps/Server/src/adapter/rest/`
  - `apps/Server/src/core/services/`
  - `apps/Server/src/repository/`
  - `apps/Server/src/interface/`
  - `apps/Server/src/models/`
  - `apps/Server/src/config/`
  - `apps/Server/tests/`
  - `apps/Server/database/`
- Create all `__init__.py` files for Python package structure

### 2. Create Requirements File
- Create `apps/Server/requirements.txt` with dependencies:
  - fastapi>=0.104.0
  - uvicorn[standard]>=0.24.0
  - pydantic>=2.0.0
  - pydantic-settings>=2.0.0
  - python-jose[cryptography]>=3.3.0
  - passlib[bcrypt]>=1.7.4
  - psycopg2-binary>=2.9.9
  - asyncpg>=0.29.0
  - sqlalchemy>=2.0.0
  - python-multipart>=0.0.6
  - httpx>=0.25.0 (for testing)
  - pytest>=7.4.0
  - pytest-asyncio>=0.21.0

### 3. Create Configuration Module
- Create `apps/Server/src/config/settings.py` with Pydantic Settings class
- Include settings for:
  - DATABASE_URL
  - JWT_SECRET_KEY
  - JWT_ALGORITHM (default: HS256)
  - JWT_EXPIRE_MINUTES (default: 1440)
  - CORS_ORIGINS (as JSON string)
- Create `apps/Server/src/config/database.py` with SQLAlchemy engine and session setup (placeholder)
- Create `apps/Server/.env.sample` documenting all required environment variables

### 4. Create Health Check Endpoint
- Create `apps/Server/src/adapter/rest/health_routes.py` with APIRouter
- Implement GET /api/health endpoint returning:
  - status: "healthy"
  - timestamp: current datetime
  - version: "1.0.0"
- Add appropriate logging following project standards

### 5. Create Dependencies Module
- Create `apps/Server/src/adapter/rest/dependencies.py`
- Add placeholder function for `get_current_user` (to be implemented in auth wave)
- Add database session dependency `get_db`

### 6. Create Main Entry Point
- Create `apps/Server/main.py` as the FastAPI application entry point
- Configure CORS middleware with settings from config
- Register health routes with /api prefix
- Add startup/shutdown events for logging
- Include uvicorn runner for direct execution

### 7. Write Tests for Health Endpoint
- Create `apps/Server/tests/test_health.py`
- Test that /api/health returns 200 status
- Test response contains status, timestamp, and version fields
- Use pytest and httpx for async testing

### 8. Validate Implementation
- Run validation commands to ensure everything works correctly with zero regressions

## Testing Strategy
### Unit Tests
- Test health endpoint returns correct JSON structure
- Test health endpoint returns 200 status code
- Test configuration loads environment variables correctly

### Edge Cases
- Server starts with missing optional environment variables
- CORS handles requests from allowed and disallowed origins
- Health endpoint responds under load

## Acceptance Criteria
- Server folder exists with complete Clean Architecture structure
- All `__init__.py` files are in place for Python packaging
- `requirements.txt` contains all specified dependencies
- `main.py` starts the FastAPI application on port 8000
- Health check endpoint at `/api/health` returns JSON with status, timestamp, and version
- CORS is configured and ready for frontend integration
- `.env.sample` documents all required environment variables
- Tests pass for health endpoint
- Server can be started with `python -m uvicorn main:app --reload --port 8000`
- API documentation available at `/docs`

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `ls -la apps/Server/` - Verify Server folder exists with expected structure
- `ls -la apps/Server/src/adapter/rest/` - Verify REST adapter folder structure
- `ls -la apps/Server/src/core/services/` - Verify core services folder structure
- `ls -la apps/Server/src/config/` - Verify config folder structure
- `cd apps/Server && pip install -r requirements.txt` - Install dependencies (or use venv first)
- `cd apps/Server && python -c "from main import app; print('FastAPI app imports successfully')"` - Test import
- `cd apps/Server && python -m pytest tests/ -v` - Run tests to validate health endpoint

## Notes
- This is Wave 1 of 6, running in parallel with FT-002 (Frontend Setup) and FT-003 (Database Schema)
- Python version must be 3.11.9 for Render compatibility
- The database configuration is a placeholder - actual connection will be configured in FT-003/FT-004
- Authentication dependencies are placeholders - will be implemented in Wave 2 (FT-004)
- Follow project logging standards: `print(f"INFO [ModuleName]: message")`
- All files should have type hints as per Python standards in CLAUDE.md
