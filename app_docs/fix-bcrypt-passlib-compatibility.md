# Fix: Bcrypt-Passlib Compatibility Issue

## Problem

The authentication service was failing with the following error when attempting to verify passwords:

```
ValueError: password cannot be longer than 72 bytes, truncate manually if necessary
```

This occurred due to a compatibility issue between the `passlib` library and newer versions of the `bcrypt` library. The `passlib.context.CryptContext` wrapper was having trouble interfacing with `bcrypt.__about__.__version__`, causing password hashing and verification to fail.

## Root Cause

The `passlib` library uses an internal detection mechanism to check for bcrypt bugs and version compatibility. With newer versions of the `bcrypt` library (4.x+), the internal structure changed:
- `bcrypt.__about__` module no longer exists
- The wrap bug detection mechanism was failing during initialization

## Solution

Replaced `passlib.context.CryptContext` with direct `bcrypt` library calls in `src/core/services/auth_service.py`:

### Before (using passlib)
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(self, password: str) -> str:
    return pwd_context.hash(password)

def verify_password(self, plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### After (using bcrypt directly)
```python
import bcrypt

def hash_password(self, password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(self, plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
```

## Files Changed

- `apps/Server/src/core/services/auth_service.py` - Replaced passlib with direct bcrypt usage

## Additional Dependencies Installed

During troubleshooting, the following missing dependencies were also installed:
- `email-validator` - Required by Pydantic for email field validation
- `python-dateutil` - Required by dashboard service for date calculations

## Testing

After the fix, login was verified to work correctly:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"danke@method.ai","password":"Tremarel2026*"}'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "a7be46f2-a220-438a-842a-bdeb1ec365b9",
    "email": "danke@method.ai",
    "first_name": "Danke",
    "last_name": "Admin",
    "role": "admin",
    "is_active": true
  }
}
```

## Date

2026-01-14
