# CRM Pipeline — Prospect Data Model

**ADW ID:** 57f962c3
**Date:** 2026-02-28
**Specification:** specs/issue-47-adw-57f962c3-sdlc_planner-prospect-data-model.md

## Overview

Adds the foundational Prospect data model for the CRM Pipeline feature. Prospects represent companies or contacts tracked through a sales pipeline, scoped to entities (multi-entity support) so each family/startup has its own set of prospects. This is the first issue (CRM-001) in a 14-issue CRM wave and provides the database table, SQLAlchemy model, and Pydantic DTOs that subsequent CRUD API and meeting record issues depend on.

## What Was Built

- `prospects` PostgreSQL table with full schema (columns, constraints, indexes, trigger)
- `Prospect` SQLAlchemy model with entity-scoped foreign key
- Five Pydantic DTOs: Create, Update, Response, ListResponse, Filter
- Comprehensive unit tests covering validation, edge cases, and model behavior

## Technical Implementation

### Files Modified

- `apps/Server/database/schema.sql`: Added `prospects` table definition (40 lines) with UUID PK, entity FK, stage CHECK constraint, estimated_value CHECK, 4 indexes, and `updated_at` trigger
- `apps/Server/src/models/prospect.py`: New SQLAlchemy model mapping to `prospects` table with all columns typed and indexed
- `apps/Server/src/models/__init__.py`: Registered `Prospect` in model exports
- `apps/Server/src/interface/prospect_dto.py`: Five Pydantic v2 DTOs with field validators
- `apps/Server/tests/test_prospect_model.py`: 13 unit tests for DTOs and model

### Key Changes

- **Pipeline Stages**: Seven-stage sales pipeline enforced at both DB and DTO level — `lead`, `contacted`, `qualified`, `proposal`, `negotiation`, `won`, `lost`
- **Entity Scoping**: `entity_id` FK to `entities(id)` with CASCADE delete, matching the multi-tenant pattern used by transactions and budgets
- **Estimated Value**: Uses `ge=0` (not `gt=0`) to allow $0 deals (partnerships, pro-bono), with NULL permitted for unknown values
- **Soft Delete**: `is_active` boolean flag with dedicated index for efficient filtering
- **Composite Index**: `idx_prospects_entity_stage` for efficient per-entity pipeline stage queries

### Database Schema

```sql
CREATE TABLE prospects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_id UUID NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(100),
    stage VARCHAR(50) NOT NULL DEFAULT 'lead',
    estimated_value DECIMAL(15, 2),
    source VARCHAR(100),
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### DTO Summary

| DTO | Purpose |
|-----|---------|
| `ProspectCreateDTO` | Create prospect — requires `entity_id` + `company_name`, stage defaults to `lead` |
| `ProspectUpdateDTO` | Partial update — all fields optional, `entity_id` not updatable |
| `ProspectResponseDTO` | API response — all fields, `from_attributes=True` for ORM mapping |
| `ProspectListResponseDTO` | Paginated list — array of responses + total count |
| `ProspectFilterDTO` | Query filters — stage, is_active, source (all optional) |

## How to Use

1. **Import the model**: `from src.models.prospect import Prospect`
2. **Import DTOs**: `from src.interface.prospect_dto import ProspectCreateDTO, ProspectUpdateDTO, ProspectResponseDTO, ProspectListResponseDTO, ProspectFilterDTO`
3. **Create a prospect**: Instantiate `ProspectCreateDTO` with `entity_id` and `company_name` (minimum required fields)
4. **Update a prospect**: Use `ProspectUpdateDTO` with only the fields to change
5. **Filter prospects**: Use `ProspectFilterDTO` to filter by stage, active status, or source

## Configuration

No additional configuration required. The prospect model uses the existing database connection and entity infrastructure.

## Testing

Run prospect-specific tests:
```bash
cd apps/Server && uv run pytest tests/test_prospect_model.py -v
```

Run full server test suite to check for regressions:
```bash
cd apps/Server && uv run pytest
```

## Notes

- This is a backend-only (data model layer) change — no UI components or API endpoints are included
- CRM-004 (CRUD API endpoints) and CRM-005 (meeting records) depend on the models and DTOs created here
- The `source` field is intentionally free-form (not a Literal enum) to allow flexibility without schema changes
- Future issues may add custom pipeline stages beyond the current seven
