# Feature: Backend JWT Authentication with RBAC

## Metadata
issue_number: `9`
adw_id: `ed4cef49`
issue_json: `{"number":9,"title":"[FinanceTracker] Wave 2: Backend Authentication","body":"..."}`

## Feature Description
Implement complete backend authentication system for the Finance Tracker application using custom JWT tokens with role-based access control (RBAC). This includes user registration and login endpoints, password hashing with bcrypt, JWT token generation and validation using python-jose, and middleware dependencies for protecting routes. The system supports four user roles: admin, manager, user, and viewer, each with different permission levels.

## User Story
As a Finance Tracker user
I want to securely register and login to the application
So that my financial data is protected and I can access features appropriate to my role

## Problem Statement
The Finance Tracker application currently has no authentication mechanism. Users cannot register, login, or have their API requests validated. Protected endpoints cannot distinguish between different user roles, leaving the application vulnerable and preventing proper access control to sensitive financial data.

## Solution Statement
Implement a complete JWT-based authentication system following Clean Architecture principles:
1. Create a UserRepository for database operations on the users table
2. Create an AuthService for business logic (password hashing, JWT generation/validation)
3. Create auth routes for registration and login endpoints
4. Implement JWT validation middleware via FastAPI dependencies
5. Create RBAC dependencies for role-based route protection
6. Add comprehensive tests for all auth functionality

## Relevant Files
Use these files to implement the feature:

- `apps/Server/main.py` - Entry point where auth router will be registered
- `apps/Server/src/config/settings.py` - Contains JWT configuration (JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES)
- `apps/Server/src/config/database.py` - Database session configuration for repository layer
- `apps/Server/src/adapter/rest/dependencies.py` - Contains placeholder `get_current_user` that needs full implementation
- `apps/Server/src/adapter/rest/health_routes.py` - Reference for route patterns and Pydantic models
- `apps/Server/database/schema.sql` - Reference for users table structure (email, password_hash, role, etc.)
- `apps/Server/requirements.txt` - Already contains python-jose and passlib[bcrypt] dependencies
- `apps/Server/tests/test_health.py` - Reference for testing patterns with httpx and pytest-asyncio
- `app_docs/feature-0f0d4c36-fastapi-backend-setup.md` - Reference for backend setup patterns
- `app_docs/feature-db5f36c7-database-schema-tables.md` - Reference for database schema details

### New Files
- `apps/Server/src/models/user.py` - SQLAlchemy User model
- `apps/Server/src/interface/auth_dto.py` - Pydantic DTOs for auth requests/responses
- `apps/Server/src/repository/user_repository.py` - User data access layer
- `apps/Server/src/core/services/auth_service.py` - Authentication business logic
- `apps/Server/src/adapter/rest/auth_routes.py` - Registration and login endpoints
- `apps/Server/src/adapter/rest/rbac_dependencies.py` - Role-based access control dependencies
- `apps/Server/tests/test_auth.py` - Unit tests for auth endpoints

## Implementation Plan

### Phase 1: Foundation
Set up the data layer components needed for authentication:
1. Create the SQLAlchemy User model matching the database schema
2. Create Pydantic DTOs for registration, login requests, and token responses
3. Implement the UserRepository with methods for creating users and finding by email

### Phase 2: Core Implementation
Build the authentication business logic and token handling:
1. Implement AuthService with password hashing (bcrypt) and JWT token management (python-jose)
2. Update the `get_current_user` dependency to decode and validate JWT tokens
3. Create RBAC dependencies (`require_roles`) for role-based route protection

### Phase 3: Integration
Create endpoints and register with the FastAPI application:
1. Implement auth routes: POST /api/auth/register and POST /api/auth/login
2. Add GET /api/auth/me endpoint to return current user info
3. Register auth router in main.py
4. Add comprehensive unit tests for all auth functionality

## Step by Step Tasks

### Step 1: Create User Model
- Create `apps/Server/src/models/user.py`
- Define SQLAlchemy User model with fields: id (UUID), email, password_hash, first_name, last_name, role, is_active, created_at, updated_at
- Use UUID as primary key matching PostgreSQL schema
- Add `__tablename__ = "users"`
- Import Base from config/database.py

### Step 2: Create Auth DTOs
- Create `apps/Server/src/interface/auth_dto.py`
- Define `UserRegisterDTO` with fields: email (EmailStr), password, first_name (optional), last_name (optional)
- Define `UserLoginDTO` with fields: email, password
- Define `TokenResponseDTO` with fields: access_token, token_type, user (UserResponseDTO)
- Define `UserResponseDTO` with fields: id, email, first_name, last_name, role, is_active
- Use Pydantic BaseModel for all DTOs
- Add proper field validators (email format, password min length of 8 characters)

### Step 3: Create User Repository
- Create `apps/Server/src/repository/user_repository.py`
- Implement `UserRepository` class with methods:
  - `create_user(db: Session, email: str, password_hash: str, first_name: str, last_name: str, role: str) -> User`
  - `get_user_by_email(db: Session, email: str) -> Optional[User]`
  - `get_user_by_id(db: Session, user_id: UUID) -> Optional[User]`
  - `update_user(db: Session, user: User) -> User`
- Follow existing logging pattern: `print(f"INFO [UserRepository]: ...")`

### Step 4: Create Auth Service
- Create `apps/Server/src/core/services/auth_service.py`
- Implement `AuthService` class with methods:
  - `hash_password(password: str) -> str` - Use passlib bcrypt context
  - `verify_password(plain_password: str, hashed_password: str) -> bool`
  - `create_access_token(data: dict) -> str` - Use python-jose to create JWT
  - `decode_access_token(token: str) -> Optional[dict]` - Validate and decode JWT
  - `register_user(db: Session, user_data: UserRegisterDTO) -> User` - Create new user
  - `authenticate_user(db: Session, email: str, password: str) -> Optional[User]` - Validate credentials
- Get JWT settings from config/settings.py (JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES)
- Handle token expiration with exp claim
- Include user_id and email in JWT payload

### Step 5: Update get_current_user Dependency
- Modify `apps/Server/src/adapter/rest/dependencies.py`
- Replace placeholder implementation with full JWT validation:
  - Extract token from HTTPAuthorizationCredentials
  - Use AuthService to decode and validate token
  - Fetch user from database using UserRepository
  - Return user dict with id, email, role, etc.
  - Raise HTTPException 401 if token invalid or user not found
  - Raise HTTPException 401 if user is_active is False

### Step 6: Create RBAC Dependencies
- Create `apps/Server/src/adapter/rest/rbac_dependencies.py`
- Implement `require_roles(allowed_roles: List[str])` dependency factory
  - Returns a dependency function that:
    - Gets current user via get_current_user
    - Checks if user role is in allowed_roles
    - Raises HTTPException 403 if role not authorized
    - Returns current user dict if authorized
- Example usage: `Depends(require_roles(['admin', 'manager']))`

### Step 7: Create Auth Routes
- Create `apps/Server/src/adapter/rest/auth_routes.py`
- Create router with prefix `/api/auth` and tag "Authentication"
- Implement endpoints:
  - `POST /api/auth/register` - Register new user, returns TokenResponseDTO
  - `POST /api/auth/login` - Login existing user, returns TokenResponseDTO
  - `GET /api/auth/me` - Get current user info (protected), returns UserResponseDTO
- Use proper HTTP status codes: 201 for register, 200 for login/me, 400 for bad request, 401 for unauthorized
- Log all operations following project patterns

### Step 8: Register Auth Router
- Update `apps/Server/main.py`
- Import auth_router from auth_routes
- Register with `app.include_router(auth_router)`
- Add logging for auth router registration

### Step 9: Create Auth Tests
- Create `apps/Server/tests/test_auth.py`
- Follow testing patterns from test_health.py
- Test cases:
  - `test_register_success` - Valid registration returns 201 and token
  - `test_register_duplicate_email` - Duplicate email returns 400
  - `test_register_invalid_email` - Invalid email format returns 422
  - `test_register_weak_password` - Password < 8 chars returns 422
  - `test_login_success` - Valid credentials return 200 and token
  - `test_login_invalid_credentials` - Wrong password returns 401
  - `test_login_nonexistent_user` - Unknown email returns 401
  - `test_me_authenticated` - Valid token returns user info
  - `test_me_invalid_token` - Invalid token returns 401
  - `test_me_no_token` - Missing token returns 403
- Use httpx AsyncClient with ASGITransport pattern
- Mock database session for isolated tests

### Step 10: Run Validation Commands
- Execute all validation commands to ensure zero regressions
- Fix any test failures or linting errors

## Testing Strategy

### Unit Tests
- Test password hashing and verification with known values
- Test JWT token creation with expected payload
- Test JWT token decoding with valid and invalid tokens
- Test JWT expiration handling
- Test user registration with valid and invalid data
- Test user login with correct and incorrect credentials
- Test protected endpoint access with and without valid tokens
- Test RBAC with different user roles

### Edge Cases
- Registration with existing email should fail with 400
- Login with inactive user (is_active=False) should fail with 401
- Expired JWT tokens should fail with 401
- Malformed JWT tokens should fail with 401
- Missing Authorization header should fail with 403
- User with 'viewer' role attempting admin action should fail with 403
- Empty password or email should fail with 422
- SQL injection attempts in email field should be handled safely

## Acceptance Criteria
- [ ] POST /api/auth/register creates a new user and returns JWT token
- [ ] POST /api/auth/login validates credentials and returns JWT token
- [ ] GET /api/auth/me returns current user info when authenticated
- [ ] Passwords are hashed with bcrypt, never stored in plain text
- [ ] JWT tokens include user_id, email, and exp (expiration) claims
- [ ] JWT tokens expire after JWT_EXPIRE_MINUTES (default 1440 = 24 hours)
- [ ] get_current_user dependency validates JWT and returns user dict
- [ ] require_roles dependency enforces role-based access control
- [ ] All auth operations produce visible log output
- [ ] All existing tests continue to pass
- [ ] New auth tests pass with at least 90% code coverage on auth code

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && pip install -r requirements.txt` - Ensure all dependencies are installed
- `cd apps/Server && python -m pytest tests/ -v` - Run all Server tests including new auth tests
- `cd apps/Server && python -m pytest tests/test_auth.py -v` - Run auth tests specifically
- `cd apps/Server && python -c "from main import app; print('App imports successfully')"` - Verify app starts without errors
- `cd apps/Server && python -c "from src.core.services.auth_service import AuthService; print('AuthService imports successfully')"` - Verify auth service imports

## Notes
- The users table already exists in the database schema (apps/Server/database/schema.sql) with the correct structure
- Dependencies python-jose and passlib[bcrypt] are already in requirements.txt
- The JWT settings (JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES) are already configured in settings.py
- Follow the existing logging pattern: `print(f"INFO [ModuleName]: message")`
- Do not use decorators for the service or repository classes - keep it simple
- All type hints are required per project standards
- This implementation is for Wave 2 and is a prerequisite for Wave 2's FT-005 (Frontend Authentication)
- The user's global role (from users table) is separate from entity-specific roles (from user_entities table) - this implementation handles the global role only
