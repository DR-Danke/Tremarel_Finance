# Database Schema for Finance Tracker

**ADW ID:** db5f36c7
**Date:** 2026-01-12
**Specification:** specs/issue-3-adw-db5f36c7-sdlc_planner-database-schema-tables.md

## Overview

Complete PostgreSQL database schema implementation for the Finance Tracker application. This schema provides the data foundation for multi-entity income/expense tracking, including custom JWT authentication, hierarchical categories, transactions, and budget management. Deployed to Supabase PostgreSQL.

## What Was Built

- **users** table - Custom authentication with password_hash, email, roles (admin, manager, user, viewer)
- **entities** table - Separate financial tracking contexts (family, startup)
- **user_entities** table - Many-to-many relationship with per-entity role assignments
- **categories** table - Hierarchical income/expense categories with parent_id for tree structure
- **transactions** table - Income and expense records with full metadata
- **budgets** table - Period-based budget tracking per category per entity
- **Backend foundation** - FastAPI application structure with health check endpoint

## Technical Implementation

### Files Modified

- `apps/Server/database/schema.sql`: Complete PostgreSQL schema (230 lines) with 6 tables, indexes, triggers, and constraints
- `apps/Server/main.py`: FastAPI entry point with CORS configuration and health check endpoint
- `apps/Server/pyproject.toml`: Python project configuration with dependencies (FastAPI, SQLAlchemy, psycopg2, python-jose, passlib)
- `apps/Server/tests/test_health.py`: Health endpoint test
- `apps/Server/src/` directory structure: Clean Architecture layer scaffolding (adapter, core, repository, interface, models, config)

### Key Changes

- **UUID Primary Keys**: All tables use `uuid_generate_v4()` for auto-generated UUIDs
- **Automatic Timestamps**: `update_updated_at_column()` trigger function automatically maintains `updated_at` columns
- **CHECK Constraints**: Data validation for roles, entity types, category types, transaction types, and positive amounts
- **Foreign Key Cascades**: Proper ON DELETE behavior (CASCADE for entity/user deletions, RESTRICT for categories with transactions/budgets, SET NULL for optional references)
- **Performance Indexes**: Strategic indexes on frequently queried columns (entity_id, user_id, category_id, date, type)

### Database Schema Summary

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| users | Authentication | email, password_hash, role |
| entities | Multi-entity support | name, type (family/startup) |
| user_entities | User-Entity junction | user_id, entity_id, role |
| categories | Hierarchical categories | entity_id, name, type, parent_id |
| transactions | Financial records | entity_id, category_id, amount, type, date |
| budgets | Budget tracking | entity_id, category_id, amount, period_type |

## How to Use

1. **Deploy Schema**: Execute `apps/Server/database/schema.sql` against a PostgreSQL database (Supabase)
2. **Configure Connection**: Set `DATABASE_URL` environment variable in backend
3. **Start Backend**: Run `python -m uvicorn main:app --reload --port 8000` from `apps/Server/` directory
4. **Verify Health**: Check `GET /api/health` returns `{"status": "healthy"}`

## Configuration

### Environment Variables (Backend)

```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
CORS_ORIGINS=["http://localhost:5173"]
```

### Dependencies (pyproject.toml)

- fastapi>=0.104.0
- uvicorn>=0.24.0
- pydantic>=2.0.0
- python-jose>=3.3.0
- passlib>=1.7.4
- bcrypt>=4.0.0
- psycopg2-binary>=2.9.0
- sqlalchemy>=2.0.0

## Testing

```bash
cd backend
pytest tests/ -v
```

Validates:
- Health endpoint returns 200 with correct JSON structure

## Notes

- This is Wave 1 (Foundation) of the Finance Tracker implementation
- Schema uses VARCHAR with CHECK constraints instead of PostgreSQL ENUM types for easier future modifications
- DECIMAL(15,2) supports amounts up to 9,999,999,999,999.99
- Hierarchical categories support unlimited depth via self-referential parent_id
- Wave 2 will implement authentication using this schema (FT-004 Backend Auth, FT-005 Frontend Auth)
