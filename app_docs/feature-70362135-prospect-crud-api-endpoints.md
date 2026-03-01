# Prospect CRUD API Endpoints

**ADW ID:** 70362135
**Date:** 2026-03-01
**Specification:** specs/issue-50-adw-70362135-sdlc_planner-prospect-crud-api-endpoints.md

## Overview

Full CRUD REST API for managing CRM prospects, built following Clean Architecture with repository, service, and routes layers. All endpoints require JWT authentication, filter by entity_id for multi-entity isolation, and include a dedicated PATCH endpoint for stage updates that automatically records transitions in the audit trail via StageTransitionRepository.

## What Was Built

- **ProspectRepository** — Data access layer with CRUD operations, filtered listing, and counting
- **ProspectService** — Business logic layer with entity ownership validation and stage transition recording
- **Prospect Routes** — 6 REST API endpoints under `/api/prospects` with JWT auth and RBAC
- **Router Registration** — Prospect router registered in `main.py`
- **API Integration Tests** — 647-line test suite covering all endpoints, error cases, auth, and RBAC

## Technical Implementation

### Files Modified

- `apps/Server/main.py`: Imported and registered `prospect_router`, added startup log
- `apps/Server/src/repository/prospect_repository.py`: New — ProspectRepository class with create, get_by_id, get_by_entity (filtered + paginated), count_by_entity, update, delete
- `apps/Server/src/core/services/prospect_service.py`: New — ProspectService class with entity ownership validation, stage transition audit trail via PipelineStageRepository and StageTransitionRepository
- `apps/Server/src/adapter/rest/prospect_routes.py`: New — FastAPI router with 6 endpoints and inline ProspectStageUpdateDTO
- `apps/Server/tests/test_prospect_api.py`: New — Comprehensive test suite with mock DB, auth token helper, and full endpoint coverage

### Key Changes

- **6 API Endpoints**: POST (create, 201), GET list (paginated with filters), GET by ID, PUT (update), PATCH stage (with audit trail), DELETE (admin/manager only, 204)
- **Entity Ownership Validation**: All read/write operations verify `prospect.entity_id` matches the requested `entity_id`, returning 404 if mismatched
- **Stage Transition Audit Trail**: PATCH endpoint looks up old/new PipelineStage records by name, updates the prospect's stage, and creates an immutable StageTransition record
- **RBAC on Delete**: Only admin/manager roles can delete prospects via `require_roles(["admin", "manager"])`
- **Inline Route DTO**: `ProspectStageUpdateDTO` defined in routes file with `Literal` type for valid stage values (lead, contacted, qualified, proposal, negotiation, won, lost)

## API Endpoints

| Method | Path | Description | Auth | Status |
|--------|------|-------------|------|--------|
| POST | `/api/prospects/` | Create prospect | JWT | 201 |
| GET | `/api/prospects/` | List prospects (paginated, filtered) | JWT | 200 |
| GET | `/api/prospects/{id}` | Get single prospect | JWT | 200 |
| PUT | `/api/prospects/{id}` | Update prospect | JWT | 200 |
| PATCH | `/api/prospects/{id}/stage` | Update stage + audit trail | JWT | 200 |
| DELETE | `/api/prospects/{id}` | Delete prospect | JWT (admin/manager) | 204 |

### Query Parameters

- **entity_id** (required on all endpoints): UUID — filters by entity ownership
- **stage** (optional, GET list): Filter by pipeline stage
- **is_active** (optional, GET list): Filter by active status
- **source** (optional, GET list): Filter by prospect source
- **skip/limit** (optional, GET list): Pagination (default: skip=0, limit=100, max limit=500)

## How to Use

1. Authenticate via `POST /api/auth/login` to obtain a JWT token
2. Include the token as `Authorization: Bearer <token>` in all requests
3. Create a prospect: `POST /api/prospects/` with `ProspectCreateDTO` body (must include `entity_id` and `company_name`)
4. List prospects: `GET /api/prospects/?entity_id=<uuid>` with optional `stage`, `is_active`, `source` filters
5. Get a prospect: `GET /api/prospects/<id>?entity_id=<uuid>`
6. Update fields: `PUT /api/prospects/<id>?entity_id=<uuid>` with `ProspectUpdateDTO` body
7. Change stage with audit: `PATCH /api/prospects/<id>/stage?entity_id=<uuid>` with `{"new_stage": "qualified", "notes": "..."}`
8. Delete (admin/manager): `DELETE /api/prospects/<id>?entity_id=<uuid>`

## Configuration

No additional environment variables or configuration required. The feature uses existing JWT auth, database connection, and pipeline stage infrastructure.

## Testing

Run prospect-specific tests:
```bash
cd apps/Server && uv run pytest tests/test_prospect_api.py -v
```

Run all server tests to verify zero regressions:
```bash
cd apps/Server && uv run pytest
```

Test coverage includes:
- Success cases for all 6 endpoints
- 404 responses for non-existent prospects
- Entity ownership validation (cross-entity access returns 404)
- 403 forbidden for non-admin/manager delete attempts
- 401 for unauthenticated requests
- Stage transition audit trail recording

## Notes

- Backend-only feature — no frontend changes required
- The PATCH stage endpoint bridges the prospect and pipeline-stage subsystems by looking up PipelineStage records by name and creating immutable StageTransition audit records
- Wave 2 (frontend) will consume these endpoints via a prospectService; Wave 3 (pipeline automation) will use POST and PATCH for meeting transcript processing
- Follows the same patterns established by the PipelineStage CRUD stack
