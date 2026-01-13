# Feature: Backend Authentication with JWT and RBAC

## Metadata
issue_number: `9`
adw_id: `16559deb`
issue_json: `{"number":9,"title":"[FinanceTracker] Wave 2: Backend Authentication","body":"..."}`

## Feature Description
Implement complete user authentication for the Finance Tracker backend API. This includes user registration, login endpoints, password hashing with bcrypt, JWT token generation and validation using python-jose, and role-based access control (RBAC) for protecting API endpoints. The authentication system supports four roles: admin, manager, user, and viewer, each with different permission levels.

## User Story
As a Finance Tracker user
I want to register an account, login with my credentials, and have my identity verified on protected endpoints
So that my financial data is secure and I can only access features appropriate to my role

## Problem Statement
The Finance Tracker backend currently has placeholder authentication that always returns a 501 Not Implemented error. Without proper authentication, the API cannot protect sensitive financial data or enforce role-based permissions. The frontend (FT-005) depends on these auth endpoints to implement login UI and auth context.

## Solution Statement
Implement a complete authentication system following Clean Architecture:
1. **AuthService** - Core business logic for registration, login, and token management
2. **UserRepository** - Data access layer for user CRUD operations
3. **Auth Routes** - FastAPI endpoints for `/api/auth/register` and `/api/auth/login`
4. **JWT Middleware** - Token validation dependency that extracts user from Bearer tokens
5. **RBAC Dependencies** - Role-checking dependencies for protecting endpoints by role
6. **DTOs** - Pydantic models for auth requests/responses

## Relevant Files
Use these files to implement the feature:

- `CLAUDE.md` - Contains authentication flow documentation, role definitions, and backend patterns
- `apps/Server/main.py` - Entry point where auth router will be registered
- `apps/Server/src/adapter/rest/dependencies.py` - Contains placeholder `get_current_user` to be implemented
- `apps/Server/src/adapter/rest/health_routes.py` - Example of route structure to follow
- `apps/Server/src/config/settings.py` - JWT configuration (JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_MINUTES)
- `apps/Server/src/config/database.py` - Database session configuration
- `apps/Server/database/schema.sql` - Users table schema with password_hash, role, email
- `apps/Server/tests/test_health.py` - Test patterns to follow for auth tests
- `apps/Server/requirements.txt` - Already includes python-jose and passlib dependencies
- `app_docs/feature-db5f36c7-database-schema-tables.md` - Database schema documentation

### New Files
- `apps/Server/src/models/user_model.py` - SQLAlchemy User model
- `apps/Server/src/repository/user_repository.py` - User data access layer
- `apps/Server/src/core/services/auth_service.py` - Authentication business logic
- `apps/Server/src/interface/auth_dto.py` - Pydantic DTOs for auth endpoints
- `apps/Server/src/adapter/rest/auth_routes.py` - Auth API endpoints
- `apps/Server/src/adapter/rest/rbac_dependencies.py` - RBAC middleware functions
- `apps/Server/tests/test_auth.py` - Authentication endpoint tests

## Implementation Plan
### Phase 1: Foundation
- Create the SQLAlchemy User model matching the database schema
- Implement the UserRepository for database operations (create, get_by_email, get_by_id)
- Create auth DTOs for registration, login, and token responses

### Phase 2: Core Implementation
- Implement AuthService with password hashing (bcrypt) and JWT generation (python-jose)
- Create auth routes for POST /api/auth/register and POST /api/auth/login
- Implement the `get_current_user` dependency with actual JWT token validation
- Create RBAC dependencies for role-based endpoint protection

### Phase 3: Integration
- Register auth router in main.py
- Write comprehensive tests for all auth endpoints
- Validate the complete auth flow works end-to-end

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Create User Model
- Create `apps/Server/src/models/user_model.py`
- Define SQLAlchemy User model with columns matching `database/schema.sql`:
  - id (UUID, primary key)
  - email (String, unique, not null)
  - password_hash (String, not null)
  - first_name (String, nullable)
  - last_name (String, nullable)
  - role (String, default 'user')
  - is_active (Boolean, default True)
  - created_at (DateTime, default now)
  - updated_at (DateTime, auto-update)
- Add logging per project standards

### 2. Create Auth DTOs
- Create `apps/Server/src/interface/auth_dto.py`
- Define Pydantic models:
  - `UserRegisterRequest` - email, password, first_name (optional), last_name (optional)
  - `UserLoginRequest` - email, password
  - `TokenResponse` - access_token, token_type
  - `UserResponse` - id, email, first_name, last_name, role, is_active, created_at
- Add field validators for email format and password strength (min 8 chars)

### 3. Create User Repository
- Create `apps/Server/src/repository/user_repository.py`
- Implement UserRepository class with methods:
  - `create(db: Session, email: str, password_hash: str, first_name: str | None, last_name: str | None) -> User`
  - `get_by_email(db: Session, email: str) -> User | None`
  - `get_by_id(db: Session, user_id: UUID) -> User | None`
  - `email_exists(db: Session, email: str) -> bool`
- Follow Clean Architecture patterns (repository only handles data access)
- Add logging for all database operations

### 4. Create Auth Service
- Create `apps/Server/src/core/services/auth_service.py`
- Implement AuthService class with methods:
  - `hash_password(password: str) -> str` - Use passlib with bcrypt
  - `verify_password(plain_password: str, hashed_password: str) -> bool`
  - `create_access_token(user_id: str, email: str, role: str) -> str` - JWT with python-jose
  - `decode_token(token: str) -> dict | None` - Decode and validate JWT
  - `register_user(db: Session, email: str, password: str, first_name: str | None, last_name: str | None) -> User`
  - `authenticate_user(db: Session, email: str, password: str) -> User | None`
- Use settings from `get_settings()` for JWT configuration
- Include proper error handling and logging

### 5. Implement get_current_user Dependency
- Update `apps/Server/src/adapter/rest/dependencies.py`
- Replace placeholder `get_current_user` with actual implementation:
  - Extract Bearer token from Authorization header
  - Decode JWT using AuthService
  - Validate token expiration and structure
  - Return user dict with id, email, role
  - Raise HTTPException 401 for invalid/expired tokens
- Keep `get_db` dependency as-is

### 6. Create RBAC Dependencies
- Create `apps/Server/src/adapter/rest/rbac_dependencies.py`
- Implement role-checking dependencies:
  - `require_roles(allowed_roles: list[str])` - Factory function returning a dependency
  - The returned dependency checks if current user's role is in allowed_roles
  - Raise HTTPException 403 if role not permitted
- Support all four roles: admin, manager, user, viewer
- Add logging for role checks

### 7. Create Auth Routes
- Create `apps/Server/src/adapter/rest/auth_routes.py`
- Create router with prefix `/api/auth` and tag `Authentication`
- Implement endpoints:
  - `POST /api/auth/register` - Create new user, return TokenResponse
  - `POST /api/auth/login` - Authenticate user, return TokenResponse
  - `GET /api/auth/me` - Get current user (protected, requires valid token)
- Use proper HTTP status codes (201 for register, 200 for login, 401 for invalid credentials)
- Return appropriate error messages (409 for duplicate email, 401 for bad credentials)
- Add comprehensive logging

### 8. Register Auth Router
- Update `apps/Server/main.py`
- Import auth_router from auth_routes
- Register with `app.include_router(auth_router)`
- Add startup log message for authentication initialization

### 9. Create Auth Tests
- Create `apps/Server/tests/test_auth.py`
- Follow patterns from `test_health.py` (use httpx AsyncClient)
- Write tests for:
  - `test_register_new_user` - Returns 201 with token
  - `test_register_duplicate_email` - Returns 409
  - `test_login_valid_credentials` - Returns 200 with token
  - `test_login_invalid_password` - Returns 401
  - `test_login_nonexistent_user` - Returns 401
  - `test_get_me_with_valid_token` - Returns user data
  - `test_get_me_without_token` - Returns 401/403
  - `test_get_me_with_invalid_token` - Returns 401
- Use pytest fixtures for test database session
- Include logging in tests per project standards

### 10. Run Validation Commands
- Execute all validation commands to ensure zero regressions
- Verify all tests pass
- Confirm the auth flow works end-to-end

## Testing Strategy
### Unit Tests
- Test password hashing and verification (bcrypt)
- Test JWT token generation and decoding
- Test user registration with valid/invalid data
- Test login with valid/invalid credentials
- Test token validation and extraction of user info
- Test role-based access control

### Edge Cases
- Registration with existing email (should return 409 Conflict)
- Login with incorrect password (should return 401)
- Login with non-existent email (should return 401 - same message as wrong password for security)
- Expired JWT token (should return 401)
- Malformed JWT token (should return 401)
- Missing Authorization header (should return 401/403)
- User with is_active=False attempting login (should return 401)
- Access to role-protected endpoint without required role (should return 403)

## Acceptance Criteria
- [ ] User can register with email and password via POST /api/auth/register
- [ ] User can login with credentials via POST /api/auth/login
- [ ] Both endpoints return JWT access_token on success
- [ ] Passwords are hashed with bcrypt before storage
- [ ] JWT tokens include user_id, email, and role claims
- [ ] JWT tokens expire after JWT_EXPIRE_MINUTES (configurable)
- [ ] GET /api/auth/me returns current user when valid token provided
- [ ] Invalid/expired tokens return 401 Unauthorized
- [ ] Duplicate email registration returns 409 Conflict
- [ ] Invalid login credentials return 401 Unauthorized
- [ ] RBAC dependencies can protect endpoints by role
- [ ] All tests pass with zero regressions
- [ ] All code follows Clean Architecture and logging standards

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/ -v` - Run all Server tests to validate auth and health endpoints work
- `cd apps/Server && python -c "from src.models.user_model import User; print('User model OK')"` - Verify User model imports correctly
- `cd apps/Server && python -c "from src.core.services.auth_service import AuthService; print('AuthService OK')"` - Verify AuthService imports correctly
- `cd apps/Server && python -c "from src.adapter.rest.auth_routes import router; print('Auth routes OK')"` - Verify auth routes import correctly
- `cd apps/Server && python -c "from src.adapter.rest.rbac_dependencies import require_roles; print('RBAC OK')"` - Verify RBAC dependencies import correctly
- `cd apps/Server && python -m uvicorn main:app --host 0.0.0.0 --port 8000 &` - Start server in background
- `sleep 3 && curl -X GET http://localhost:8000/api/health` - Verify server is running
- `curl -X POST http://localhost:8000/api/auth/register -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"testpass123"}'` - Test registration endpoint
- `curl -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"testpass123"}'` - Test login endpoint

## Notes
- This is Wave 2 (Authentication) of the Finance Tracker implementation
- FT-005 (Frontend Authentication) depends on this issue completing first
- The JWT token payload includes: sub (user_id), email, role, exp (expiration)
- Password validation requires minimum 8 characters
- Error messages for login should not reveal whether email exists (security best practice)
- The is_active flag on users can be used to disable accounts without deletion
- Future enhancements may include: refresh tokens, password reset, email verification
- All dependencies (python-jose, passlib, bcrypt) are already in requirements.txt
