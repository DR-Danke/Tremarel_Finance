# Meeting Record API Endpoints

**ADW ID:** d1b26544
**Date:** 2026-03-01
**Specification:** specs/issue-51-adw-d1b26544-sdlc_planner-meeting-record-api-endpoints.md

## Overview

Implements the complete backend API stack for meeting records: REST routes, business logic service, and data access repository. Meeting records are entity-scoped records linked to prospects that store processed meeting transcripts, summaries, action items, participants, and formatted HTML output. This builds on the MeetingRecord data model created in Issue #49.

## What Was Built

- **MeetingRecordRepository** — CRUD + filtered/paginated queries against the `meeting_records` table with JSON serialization for list fields
- **MeetingRecordService** — Business logic layer with entity-scoping validation, field-by-field updates, and JSON serialization for `action_items`/`participants`
- **MeetingRecordRoutes** — Full REST API with 6 endpoints: Create, List, Get, Get HTML, Update, Delete
- **Router registration** in `main.py`
- **Comprehensive API tests** — 12 test cases covering all endpoints, error cases, and auth

## Technical Implementation

### Files Modified

- `apps/Server/src/repository/meeting_record_repository.py`: New repository with `create`, `get_by_id`, `get_by_entity` (filtered + paginated), `count_by_entity`, `update`, and `delete` methods. Serializes `action_items` and `participants` from `List[str]` to JSON string via `json.dumps()`.
- `apps/Server/src/core/services/meeting_record_service.py`: New service with entity-scoping validation on get/update/delete, field-by-field updates, and JSON serialization on update.
- `apps/Server/src/adapter/rest/meeting_record_routes.py`: New REST routes at `/api/meeting-records` with full CRUD + HTML download endpoint.
- `apps/Server/main.py`: Added meeting record router import and registration.
- `apps/Server/tests/test_meeting_record_api.py`: 12 API test cases following the `test_pipeline_stage_api.py` pattern.

### Key Changes

- **Entity-scoping**: All get/update/delete operations validate that the record's `entity_id` matches the requested entity, returning 404 on mismatch to avoid leaking existence.
- **HTML download endpoint**: `GET /{id}/html` returns the `html_output` field directly as `text/html` content type for browser rendering or download. Returns 404 if record has no HTML output.
- **JSON field handling**: `action_items` and `participants` arrive as `List[str]` in DTOs, are serialized to JSON strings via `json.dumps()` in the repository (create) and service (update) layers, and returned as raw `Optional[str]` in responses.
- **Pagination and filtering**: List endpoint supports `prospect_id`, `is_active` (defaults to True), `meeting_date_from`, and `meeting_date_to` filters with `skip`/`limit` pagination (max 500). Results ordered by `meeting_date DESC NULLS LAST, created_at DESC`.
- **RBAC on delete**: Only admin and manager roles can delete meeting records, enforced via `require_roles(["admin", "manager"])`.

## How to Use

1. **Create a meeting record**: `POST /api/meeting-records/` with `MeetingRecordCreateDTO` body (requires `entity_id`, `prospect_id`, `title`; optional `transcript_ref`, `summary`, `action_items`, `participants`, `html_output`, `meeting_date`). Returns 201.
2. **List meeting records**: `GET /api/meeting-records/?entity_id=<uuid>` with optional filters `prospect_id`, `is_active`, `meeting_date_from`, `meeting_date_to`, `skip`, `limit`. Returns paginated list with total count.
3. **Get a single record**: `GET /api/meeting-records/{id}?entity_id=<uuid>`. Returns 200 or 404.
4. **Download HTML output**: `GET /api/meeting-records/{id}/html?entity_id=<uuid>`. Returns `text/html` response or 404.
5. **Update a record**: `PUT /api/meeting-records/{id}?entity_id=<uuid>` with `MeetingRecordUpdateDTO` body. Returns 200 or 404.
6. **Delete a record**: `DELETE /api/meeting-records/{id}?entity_id=<uuid>`. Requires admin/manager role. Returns 204 or 404.

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

## Configuration

No new environment variables or configuration needed. All required packages are already in `requirements.txt`.

## Testing

Run the meeting record API tests:

```bash
cd apps/Server && python -m pytest tests/test_meeting_record_api.py -v
```

Run all server tests to verify zero regressions:

```bash
cd apps/Server && python -m pytest tests/ -v
```

Verify module imports:

```bash
cd apps/Server && python -c "from src.adapter.rest.meeting_record_routes import router; print('Routes import OK')"
cd apps/Server && python -c "from src.core.services.meeting_record_service import meeting_record_service; print('Service import OK')"
cd apps/Server && python -c "from src.repository.meeting_record_repository import meeting_record_repository; print('Repository import OK')"
```

## Notes

- This is a backend-only feature (no UI components). Frontend will be added in Wave 2.
- The `action_items` and `participants` fields use `Text` column type (not JSONB) storing JSON strings. Client-side parsing is expected.
- The `html_output` field can be large (full formatted meeting report). The dedicated `/html` endpoint returns it directly for browser rendering.
- Follows the same Clean Architecture patterns established by the pipeline stage feature (`pipeline_stage_routes.py`, `pipeline_stage_service.py`, `pipeline_stage_repository.py`).
