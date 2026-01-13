# Backend Authentication with JWT and RBAC

**ADW ID:** 16559deb
**Date:** 2026-01-12
**Specification:** specs/issue-9-adw-16559deb-sdlc_planner-backend-auth-jwt-rbac.md

## Overview

Complete user authentication system for the Finance Tracker backend API. Implements user registration, login endpoints, password hashing with bcrypt, JWT token generation and validation, and role-based access control (RBAC) with four permission levels: admin, manager, user, and viewer.

## What Was Built

- User registration endpoint (`POST /api/auth/register`)
- User login endpoint (`POST /api/auth/login`)
- Current user endpoint (`GET /api/auth/me`)
- JWT token generation and validation with python-jose
- Password hashing with bcrypt via passlib
- RBAC middleware for role-based endpoint protection
- Complete test suite for authentication flows

## Technical Implementation

### Files Modified

- `apps/Server/main.py`: Added auth router import and registration
- `apps/Server/requirements.txt`: Added auth dependencies (python-jose, passlib, bcrypt)
- `apps/Server/src/adapter/rest/dependencies.py`: Implemented `get_current_user` with JWT validation
- `apps/Server/src/config/settings.py`: Added JWT configuration settings

### New Files Created

- `apps/Server/src/models/user_model.py`: SQLAlchemy User model with UUID, email, password_hash, role, is_active
- `apps/Server/src/repository/user_repository.py`: User data access layer (create, get_by_email, get_by_id, email_exists)
- `apps/Server/src/core/services/auth_service.py`: Authentication business logic (hashing, JWT, registration, authentication)
- `apps/Server/src/interface/auth_dto.py`: Pydantic DTOs (UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse)
- `apps/Server/src/adapter/rest/auth_routes.py`: FastAPI auth endpoints
- `apps/Server/src/adapter/rest/rbac_dependencies.py`: RBAC middleware (require_roles, require_admin, require_manager_or_above)
- `apps/Server/tests/test_auth.py`: Comprehensive authentication tests

### Key Changes

- JWT tokens include claims: `sub` (user_id), `email`, `role`, `exp` (expiration)
- Password validation requires minimum 8 characters
- Login errors use generic messages for security (don't reveal if email exists)
- RBAC supports four roles: admin, manager, user, viewer
- Token expiration configurable via `JWT_EXPIRE_MINUTES` setting

## How to Use

### 1. Register a New User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123","first_name":"John","last_name":"Doe"}'
```

Response: `{"access_token": "eyJ...", "token_type": "bearer"}`

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

Response: `{"access_token": "eyJ...", "token_type": "bearer"}`

### 3. Access Protected Endpoints

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer eyJ..."
```

### 4. Protect Endpoints by Role (Backend Code)

```python
from src.adapter.rest.dependencies import get_current_user
from src.adapter.rest.rbac_dependencies import require_roles

# Any authenticated user
@router.get("/items")
async def get_items(current_user: dict = Depends(get_current_user)):
    pass

# Admin or manager only
@router.delete("/items/{id}")
async def delete_item(current_user: dict = Depends(require_roles(['admin', 'manager']))):
    pass

# Convenience shortcuts
from src.adapter.rest.rbac_dependencies import require_admin, require_manager_or_above

@router.post("/admin-action")
async def admin_action(current_user: dict = Depends(require_admin())):
    pass
```

## Configuration

### Environment Variables

```bash
JWT_SECRET_KEY=your-secret-key-here    # Required: Secret for JWT signing
JWT_ALGORITHM=HS256                      # Optional: Algorithm (default HS256)
JWT_EXPIRE_MINUTES=1440                  # Optional: Token expiry in minutes (default 1440 = 24h)
```

### Role Hierarchy

| Role     | Description                          |
|----------|--------------------------------------|
| admin    | Full access, user management         |
| manager  | Full entity access, no user mgmt     |
| user     | Add/edit own transactions            |
| viewer   | Read-only access                     |

## Testing

Run auth tests:

```bash
cd apps/Server
python -m pytest tests/test_auth.py -v
```

Test coverage includes:
- User registration (success, duplicate email)
- User login (valid credentials, invalid password, non-existent user)
- Get current user (valid token, no token, invalid token)
- RBAC role checking

## Notes

- New users are assigned the `user` role by default
- Inactive users (`is_active=False`) cannot login
- Token payload structure: `{"sub": "user-uuid", "email": "...", "role": "...", "exp": 123456789}`
- All auth operations produce logging output for debugging
- Future enhancements may include: refresh tokens, password reset, email verification
