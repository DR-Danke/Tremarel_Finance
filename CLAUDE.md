# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Finance Tracker** is a full-stack income/expense tracking application for family and startup company management. Built with React frontend and FastAPI backend, deployed on Vercel/Render with PostgreSQL on Supabase.

**Deployment:**
- Frontend: Vercel (folder: `Client`)
- Backend: Render (folder: `Server`)
- Database: Supabase PostgreSQL (direct connection)

## Core Architecture Principles

**CRITICAL**: All code MUST follow Clean Architecture and SOLID principles. Never violate these - refactoring will be required if not followed.

### Clean Architecture Layers

```
Frontend:  pages/ → components/ → services/ → api/
           (UI)     (Reusable)   (Logic)    (HTTP)

Backend:   adapter/rest/ → core/services/ → repository/ → database
           (Controllers)   (Business Logic)  (Data Access)
```

### Agentic Code Architecture

Design for AI agent navigation and autonomous operation:

1. **Clear Entry Points**: `main.py` (backend), `main.tsx` (frontend)
2. **Information-Dense Keywords (IDKs)**: Use meaningful, searchable names
   - Good: `TransactionService`, `CategoryRepository`, `FKBudgetForm`
   - Bad: `DataHandler`, `Utils`, `Manager`
3. **File Size Limits**: Soft limit of 1000 lines per file
4. **Consistent Patterns**: Same folder structure, naming, and code style throughout
5. **Test Structure**: Mirrors application structure (`src/core/` → `tests/core/`)

### Logging Standards

All operations must produce visible output for agent debugging:

```python
# Python - Good logging
print(f"INFO [TransactionService]: Creating transaction for entity {entity_id}")
print(f"ERROR [TransactionService]: Failed to create transaction: {str(e)}")
```

```typescript
// TypeScript - Good logging
console.log(`INFO [TransactionService]: Fetching transactions for entity ${entityId}`);
console.error(`ERROR [TransactionService]: API call failed:`, error);
```

## Technology Stack

### Frontend (Client/)
- **React**: 19.2.3 + **TypeScript**: 5.x
- **Build Tool**: Vite 5.x
- **UI Library**: Material-UI 5.x
- **Routing**: React Router 6.x
- **Forms**: react-hook-form (mandatory)
- **HTTP**: Axios with JWT interceptor
- **Charts**: Recharts

### Backend (Server/)
- **Python**: 3.11.9 (CRITICAL for Render)
- **FastAPI**: 0.104+
- **Server**: Uvicorn
- **Validation**: Pydantic 2.x
- **Database**: PostgreSQL via psycopg2/asyncpg
- **Auth**: python-jose (JWT), passlib (bcrypt)

### Infrastructure
- **Database**: PostgreSQL on Supabase (direct connection, NO Supabase Auth)
- **Auth**: Custom JWT with role-based access control
- **Frontend Hosting**: Vercel
- **Backend Hosting**: Render

## Development Commands

### Frontend

```bash
cd Client

# Install dependencies
npm install

# Development server (http://localhost:5173)
npm run dev

# Production build
npm run build

# Lint
npm run lint

# Type check
npm run typecheck
```

### Backend

```bash
cd Server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Development server (http://localhost:8000)
python -m uvicorn main:app --reload --port 8000

# Run tests
pytest tests/
```

### Key URLs
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

## Project Structure

### Frontend (Client/)

```
Client/src/
├── main.tsx                 # ENTRY POINT
├── App.tsx                  # Root with routing
├── api/clients/             # HTTP clients with JWT
├── components/
│   ├── layout/              # FKMainLayout, FKCollapsibleSidebar, FKTopNavbar
│   ├── forms/               # FK-prefixed form components
│   ├── ui/                  # FK-prefixed reusable UI
│   └── auth/                # ProtectedRoute, RoleProtectedRoute
├── contexts/                # AuthContext, EntityContext
├── hooks/                   # useAuth, useTransactions, etc.
├── pages/                   # Route pages
├── services/                # Business logic (API calls)
├── types/                   # TypeScript interfaces
├── theme/                   # MUI theme
└── utils/                   # Formatters, validators
```

### Backend (Server/)

```
Server/
├── main.py                  # ENTRY POINT
├── src/
│   ├── adapter/rest/        # FastAPI routes
│   ├── core/services/       # Business logic
│   ├── repository/          # Data access
│   ├── interface/           # DTOs
│   ├── models/              # Database models
│   └── config/              # Settings, database
├── tests/                   # Mirrors src/ structure
├── database/                # Schema and migrations
└── requirements.txt
```

## Code Standards

### Component Naming
- **FK Prefix**: All business/form components MUST use FK prefix
  - `FKTransactionForm.tsx`, `FKBudgetCard.tsx`, `FKCollapsibleSidebar.tsx`
- **Standard Components**: Layout and utility components use descriptive names
  - `ProtectedRoute.tsx`, `TransactionList.tsx`

### TypeScript Standards
- 100% TypeScript, NO `any` types
- Use `@/` path alias for imports
- All props must be typed with interfaces

### Python Standards
- Type hints on ALL functions
- Docstrings for public APIs
- Clean Architecture layer separation

### Forms
- ALWAYS use react-hook-form with Material-UI
- Validation rules in form registration
- Error display via MUI helperText

## Authentication

### JWT Flow (No Supabase Auth)

```
1. User submits credentials to POST /api/auth/login
2. Backend validates against users table (bcrypt)
3. Backend returns JWT token with user data
4. Frontend stores token in localStorage
5. All API requests include Authorization: Bearer <token>
6. Backend validates JWT on protected routes
```

### Roles
- **admin**: Full access, user management
- **manager**: Full entity access, no user management
- **user**: Add/edit own transactions
- **viewer**: Read-only access

### Frontend Auth Pattern

```typescript
// Use AuthContext
const { user, isAuthenticated, login, logout } = useAuth();

// Protected routes
<ProtectedRoute>
  <DashboardPage />
</ProtectedRoute>

<RoleProtectedRoute allowedRoles={['admin', 'manager']}>
  <SettingsPage />
</RoleProtectedRoute>
```

### Backend Auth Pattern

```python
from src.adapter.rest.dependencies import get_current_user
from src.adapter.rest.rbac_dependencies import require_roles

@router.get("/transactions")
async def get_transactions(current_user: dict = Depends(get_current_user)):
    # Authenticated users only
    pass

@router.delete("/transactions/{id}")
async def delete_transaction(
    current_user: dict = Depends(require_roles(['admin', 'manager']))
):
    # Admin or manager only
    pass
```

## Database

### Direct PostgreSQL Connection

```python
# config/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
```

### Key Tables
- `users` - Custom auth (email, password_hash, role)
- `entities` - Family/Startup separation
- `user_entities` - User-Entity membership with roles
- `categories` - Hierarchical income/expense categories
- `transactions` - Income and expenses
- `budgets` - Budget tracking per category

## Environment Variables

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Finance Tracker
```

### Backend (.env)
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
CORS_ORIGINS=["http://localhost:5173"]
PYTHON_VERSION=3.11.9
```

## Deployment

### Vercel (Frontend)
- Root Directory: `Client`
- Framework: Vite
- Build Command: `npm run build`
- Output Directory: `dist`

### Render (Backend)
- Root Directory: `Server`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **CRITICAL**: Set `PYTHON_VERSION=3.11.9` in environment

### CORS Configuration
Backend `CORS_ORIGINS` MUST be JSON array format:
```bash
CORS_ORIGINS=["http://localhost:5173","https://your-app.vercel.app"]
```

## Multi-Entity Support

Users can belong to multiple entities (family, startup) with different roles per entity:

```typescript
// EntityContext provides current entity
const { currentEntity, switchEntity, entities } = useEntity();

// All data queries filter by currentEntity.id
const transactions = await transactionService.getAll(currentEntity.id);
```

## Quick Reference

### Creating a Transaction Form
```typescript
// Client/src/components/forms/FKTransactionForm.tsx
import { useForm } from 'react-hook-form';
import { TextField, Button, MenuItem } from '@mui/material';

export const FKTransactionForm: React.FC<Props> = ({ onSubmit }) => {
  const { register, handleSubmit, formState: { errors } } = useForm();

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <TextField
        {...register('amount', { required: 'Amount is required' })}
        type="number"
        error={!!errors.amount}
        helperText={errors.amount?.message}
      />
      {/* ... */}
    </form>
  );
};
```

### Adding a Backend Endpoint
```python
# Server/src/adapter/rest/transaction_routes.py
from fastapi import APIRouter, Depends
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

@router.post("/")
async def create_transaction(
    data: TransactionCreateDTO,
    current_user: dict = Depends(get_current_user)
):
    print(f"INFO [TransactionRoutes]: Creating transaction for user {current_user['id']}")
    result = await transaction_service.create(data, current_user)
    print(f"INFO [TransactionRoutes]: Transaction created: {result.id}")
    return result
```

## Language Guidelines

- **UI Text**: English (or Spanish if preferred)
- **Code**: English (variables, functions, comments)
- **Documentation**: English for technical docs
