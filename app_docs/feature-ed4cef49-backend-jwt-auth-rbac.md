# Backend JWT Authentication with RBAC

**ADW ID:** ed4cef49
**Date:** 2026-01-12
**Specification:** specs/issue-9-adw-ed4cef49-sdlc_planner-backend-jwt-auth-rbac.md

## Overview

Complete backend authentication system for the Finance Tracker application using custom JWT tokens with role-based access control (RBAC). The system supports user registration, login, and protected routes with four user roles: admin, manager, user, and viewer.

## What Was Built

- User registration and login endpoints with JWT token generation
- Password hashing with bcrypt via passlib
- JWT token creation and validation using python-jose
- Protected route middleware via FastAPI dependencies
- Role-based access control (RBAC) dependency factory
- SQLAlchemy User model matching the existing database schema
- Comprehensive test suite with 18+ test cases

## Technical Implementation

### Files Modified

- `apps/Server/main.py`: Added auth router registration
- `apps/Server/requirements.txt`: Added email-validator dependency
- `apps/Server/src/config/settings.py`: JWT settings already present, used by auth service

### Files Created

- `apps/Server/src/models/user.py`: SQLAlchemy User model with UUID primary key
- `apps/Server/src/interface/auth_dto.py`: Pydantic DTOs for auth requests/responses
- `apps/Server/src/repository/user_repository.py`: User data access layer with CRUD operations
- `apps/Server/src/core/services/auth_service.py`: Authentication business logic (password hashing, JWT management)
- `apps/Server/src/adapter/rest/auth_routes.py`: Registration, login, and /me endpoints
- `apps/Server/src/adapter/rest/rbac_dependencies.py`: Role-based access control dependency factory
- `apps/Server/src/adapter/rest/dependencies.py`: Updated with full JWT validation in `get_current_user`
- `apps/Server/tests/test_auth.py`: Comprehensive test suite

### Key Changes

- **JWT Flow**: Tokens are created with `sub` (user UUID) and `email` claims, plus expiration. Decoded and validated on protected routes.
- **Password Security**: Uses bcrypt via passlib's CryptContext for secure password hashing and verification.
- **RBAC Pattern**: `require_roles(['admin', 'manager'])` factory returns a dependency that checks user roles and raises 403 if unauthorized.
- **Clean Architecture**: Repository layer handles database operations, service layer contains business logic, routes handle HTTP concerns.

## How to Use

### 1. Register a New User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

Response includes `access_token`, `token_type`, and `user` object.

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### 3. Access Protected Routes

```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <your_token>"
```

### 4. Protect Routes with RBAC (Backend Code)

```python
from src.adapter.rest.dependencies import get_current_user
from src.adapter.rest.rbac_dependencies import require_roles

# Any authenticated user
@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}

# Admin or manager only
@router.delete("/users/{id}")
async def delete_user(current_user: dict = Depends(require_roles(['admin', 'manager']))):
    return {"message": "User deleted"}
```

## Configuration

Environment variables (already defined in `apps/Server/src/config/settings.py`):

| Variable | Description | Default |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | Secret key for signing JWT tokens | Required |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_EXPIRE_MINUTES` | Token expiration in minutes | `1440` (24 hours) |

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login existing user | No |
| GET | `/api/auth/me` | Get current user info | Yes |

### Response Codes

- `200`: Success (login, /me)
- `201`: Created (register)
- `400`: Bad request (duplicate email)
- `401`: Unauthorized (invalid credentials, invalid/expired token)
- `403`: Forbidden (insufficient role permissions)
- `422`: Validation error (invalid email format, password too short)

## User Roles

| Role | Description |
|------|-------------|
| `admin` | Full access, user management |
| `manager` | Full entity access, no user management |
| `user` | Add/edit own transactions |
| `viewer` | Read-only access |

## Testing

Run the auth tests:

```bash
cd apps/Server
python -m pytest tests/test_auth.py -v
```

Test coverage includes:
- Registration success and validation errors
- Login success and credential failures
- Protected endpoint access with valid/invalid tokens
- JWT token creation and decoding
- Password hashing and verification
- RBAC role checking

## Notes

- Passwords are never stored in plain text; bcrypt hashing is used
- JWT tokens include user UUID in `sub` claim for database lookup
- Inactive users (is_active=False) cannot authenticate
- All auth operations produce visible log output for debugging
- The user's global role is from the `users` table; entity-specific roles from `user_entities` are separate
