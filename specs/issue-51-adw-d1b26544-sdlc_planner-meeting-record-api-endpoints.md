# Feature: Meeting Record API Endpoints

## Metadata
issue_number: `51`
adw_id: `d1b26544`
issue_json: ``

## Feature Description
Create the complete API stack for meeting records: REST routes, business logic service, and data access repository. Meeting records are entity-scoped records linked to prospects that store processed meeting transcripts, summaries, action items, participants, and formatted HTML output. The API supports listing meetings for a prospect, retrieving meeting detail, downloading formatted HTML output, and creating new meeting records (used by the transcript processing pipeline in Wave 3).

## User Story
As a CRM user managing prospects
I want to create, view, list, update, and delete meeting records associated with prospects
So that I can track meeting history, review summaries, and download formatted meeting output

## Problem Statement
The MeetingRecord data model (ORM model, DTOs, database schema) exists from CRM-003/Issue #49, but there are no API endpoints to interact with meeting records. Without routes, service, and repository layers, neither the frontend (Wave 2) nor the transcript processing pipeline (Wave 3) can create or retrieve meeting records.

## Solution Statement
Build the three missing Clean Architecture layers following the exact same patterns used by `pipeline_stage` (the most recent CRM-related feature):
1. **Repository** (`meeting_record_repository.py`) — CRUD + filtered queries against the `meeting_records` table
2. **Service** (`meeting_record_service.py`) — business logic with entity-scoping validation, JSON serialization for `action_items`/`participants` lists
3. **Routes** (`meeting_record_routes.py`) — REST endpoints with auth, RBAC, pagination, and filtering
4. **Registration** in `main.py` — include the new router
5. **Tests** (`test_meeting_record_api.py`) — full API test coverage following the `test_pipeline_stage_api.py` pattern

A special `GET /{id}/html` endpoint returns the `html_output` field as an `text/html` response for download.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/main.py` — Entry point where routers are registered. Must add the meeting record router import and `app.include_router()` call.
- `apps/Server/src/models/meeting_record.py` — Existing MeetingRecord ORM model (already created in CRM-003). Read-only reference for field names and types.
- `apps/Server/src/interface/meeting_record_dto.py` — Existing DTOs (Create, Update, Response, List, Filter). Read-only reference for request/response shapes.
- `apps/Server/src/adapter/rest/pipeline_stage_routes.py` — Pattern reference for route structure, auth dependencies, pagination, error handling.
- `apps/Server/src/core/services/pipeline_stage_service.py` — Pattern reference for service layer: entity scoping, singleton export, logging.
- `apps/Server/src/repository/pipeline_stage_repository.py` — Pattern reference for repository layer: CRUD methods, filtering, counting, singleton export.
- `apps/Server/src/adapter/rest/dependencies.py` — Provides `get_current_user` and `get_db` dependencies.
- `apps/Server/src/adapter/rest/rbac_dependencies.py` — Provides `require_roles` for role-based access control on delete.
- `apps/Server/tests/test_pipeline_stage_api.py` — Pattern reference for API test structure: mock DB, mock auth, async client.

### New Files
- `apps/Server/src/repository/meeting_record_repository.py` — MeetingRecord repository with CRUD + filtered queries.
- `apps/Server/src/core/services/meeting_record_service.py` — MeetingRecord service with business logic and entity scoping.
- `apps/Server/src/adapter/rest/meeting_record_routes.py` — MeetingRecord REST API routes.
- `apps/Server/tests/test_meeting_record_api.py` — API endpoint tests for meeting records.

## Implementation Plan
### Phase 1: Foundation
Create the repository layer (`meeting_record_repository.py`) that provides all data access methods needed by the service layer. This is the lowest-level new file and has no dependencies on other new files.

### Phase 2: Core Implementation
Build the service layer (`meeting_record_service.py`) on top of the repository. The service handles entity-scoping validation, JSON serialization of `action_items` and `participants` list fields, and field-by-field updates. Then build the routes layer (`meeting_record_routes.py`) with full CRUD endpoints, a special HTML download endpoint, authentication, RBAC, and pagination.

### Phase 3: Integration
Register the meeting record router in `main.py`. Create comprehensive API tests (`test_meeting_record_api.py`) following the `test_pipeline_stage_api.py` pattern. Run all validation commands to confirm zero regressions.

## Step by Step Tasks

### Step 1: Create MeetingRecord Repository
- Create `apps/Server/src/repository/meeting_record_repository.py`
- Read `apps/Server/src/repository/pipeline_stage_repository.py` as the pattern reference
- Implement `MeetingRecordRepository` class with these methods:
  - `create_meeting_record(db, entity_id, prospect_id, title, ...)` — Create a new record. `action_items` and `participants` arrive as `Optional[List[str]]` and must be serialized to JSON string via `json.dumps()` before storing. Returns the ORM object after commit+refresh.
  - `get_meeting_record_by_id(db, record_id)` — Single lookup by UUID primary key.
  - `get_meeting_records_by_entity(db, entity_id, filters, skip, limit)` — Filtered query with pagination. Apply optional `MeetingRecordFilterDTO` fields: `prospect_id`, `is_active`, `meeting_date_from`, `meeting_date_to`. Order by `meeting_date DESC NULLS LAST, created_at DESC`. Return `List[MeetingRecord]`.
  - `count_meeting_records_by_entity(db, entity_id, filters)` — Count query with same filters (no pagination). Return `int`.
  - `update_meeting_record(db, record)` — Add, commit, refresh. Return updated ORM object.
  - `delete_meeting_record(db, record)` — Delete from session, commit.
- Export singleton: `meeting_record_repository = MeetingRecordRepository()`
- All methods include `print()` logging with `[MeetingRecordRepository]` prefix

### Step 2: Create MeetingRecord Service
- Create `apps/Server/src/core/services/meeting_record_service.py`
- Read `apps/Server/src/core/services/pipeline_stage_service.py` as the pattern reference
- Implement `MeetingRecordService` class with these methods:
  - `create_meeting_record(db, data: MeetingRecordCreateDTO)` — Delegate to repository. Return created ORM object.
  - `get_meeting_record(db, record_id, entity_id)` — Get by ID, validate `entity_id` matches (return `None` if mismatch). Return `Optional[MeetingRecord]`.
  - `list_meeting_records(db, entity_id, filters, skip, limit)` — Call repository `get_meeting_records_by_entity` and `count_meeting_records_by_entity`. Return `Tuple[List[MeetingRecord], int]`.
  - `update_meeting_record(db, record_id, entity_id, data: MeetingRecordUpdateDTO)` — Get record, validate entity ownership, apply field-by-field updates (including JSON serialization for `action_items`/`participants` if provided), delegate to repository update. Return `Optional[MeetingRecord]`.
  - `delete_meeting_record(db, record_id, entity_id)` — Get record, validate entity ownership, delegate to repository delete. Return `bool`.
- Export singleton: `meeting_record_service = MeetingRecordService()`
- All methods include `print()` logging with `[MeetingRecordService]` prefix

### Step 3: Create MeetingRecord Routes
- Create `apps/Server/src/adapter/rest/meeting_record_routes.py`
- Read `apps/Server/src/adapter/rest/pipeline_stage_routes.py` as the pattern reference
- Create `router = APIRouter(prefix="/api/meeting-records", tags=["Meeting Records"])`
- Implement these endpoints:
  - `POST /` — Create meeting record. Status 201. Auth: `get_current_user`. Request body: `MeetingRecordCreateDTO`. Response: `MeetingRecordResponseDTO`.
  - `GET /` — List meeting records with pagination and filters. Auth: `get_current_user`. Query params: `entity_id` (required), `prospect_id` (optional), `is_active` (optional, default True), `meeting_date_from` (optional), `meeting_date_to` (optional), `skip` (default 0), `limit` (default 100, max 500). Response: `MeetingRecordListResponseDTO`.
  - `GET /{record_id}` — Get single meeting record. Auth: `get_current_user`. Query param: `entity_id` (required). Response: `MeetingRecordResponseDTO`. 404 if not found.
  - `GET /{record_id}/html` — Download HTML output. Auth: `get_current_user`. Query param: `entity_id` (required). Returns `Response(content=html_output, media_type="text/html")`. 404 if not found or no `html_output`.
  - `PUT /{record_id}` — Update meeting record. Auth: `get_current_user`. Query param: `entity_id` (required). Request body: `MeetingRecordUpdateDTO`. Response: `MeetingRecordResponseDTO`. 404 if not found.
  - `DELETE /{record_id}` — Delete meeting record. Status 204. Auth: `require_roles(["admin", "manager"])`. Query param: `entity_id` (required). 404 if not found.
- All endpoints include `print()` logging with `[MeetingRecordRoutes]` prefix

### Step 4: Register Router in main.py
- Add import: `from src.adapter.rest.meeting_record_routes import router as meeting_record_router`
- Add `app.include_router(meeting_record_router)` after the pipeline stage router
- Add `print("INFO [Main]: Meeting Record router registered")` after the pipeline stage print

### Step 5: Create API Tests
- Create `apps/Server/tests/test_meeting_record_api.py`
- Read `apps/Server/tests/test_pipeline_stage_api.py` as the pattern reference
- Follow the exact same test structure: mock DB, mock auth, async httpx client
- Create helper `create_mock_meeting_record()` that returns a MagicMock with spec=MeetingRecord and all fields populated
- Test cases to implement:
  - `test_create_meeting_record_success` — POST with valid data returns 201
  - `test_create_meeting_record_validation_error` — POST missing required fields returns 422
  - `test_list_meeting_records_success` — GET with entity_id returns 200 with list and total
  - `test_get_meeting_record_success` — GET /{id} returns 200
  - `test_get_meeting_record_not_found` — GET /{id} for non-existent returns 404
  - `test_get_meeting_record_html_success` — GET /{id}/html returns 200 with text/html content type
  - `test_get_meeting_record_html_not_found` — GET /{id}/html for non-existent record returns 404
  - `test_update_meeting_record_success` — PUT /{id} returns 200
  - `test_update_meeting_record_not_found` — PUT /{id} for non-existent returns 404
  - `test_delete_meeting_record_success` — DELETE /{id} as admin returns 204
  - `test_delete_meeting_record_not_found` — DELETE /{id} for non-existent returns 404
  - `test_unauthenticated_request` — Request without token returns 401/403
- Mock patches target:
  - `src.core.services.auth_service.user_repository` for auth
  - `src.core.services.auth_service.bcrypt` for password check
  - `src.core.services.meeting_record_service.meeting_record_repository` for repository methods

### Step 6: Run Validation Commands
- Run all validation commands listed below to confirm zero regressions

## Testing Strategy
### Unit Tests
- All tests mock the database session and repository layer using `unittest.mock`
- Auth is mocked via patching `user_repository` and `bcrypt` in `auth_service`
- Each CRUD endpoint has success and error test cases
- The HTML download endpoint is tested for both success (record with html_output) and not-found scenarios
- Tests verify HTTP status codes, response body structure, and DTO field presence

### Edge Cases
- **Entity scoping**: Getting/updating/deleting a record that belongs to a different entity returns 404 (not 403, to avoid leaking existence)
- **Missing html_output**: GET /{id}/html on a record with `html_output=None` returns 404
- **JSON field serialization**: `action_items` and `participants` accepted as `List[str]` in create/update, stored as JSON string, returned as raw string in response
- **Soft delete filter**: List defaults to `is_active=True` so soft-deleted records are excluded unless explicitly requested
- **Pagination boundary**: `skip=0, limit=500` max, `limit` capped at 500
- **Null meeting_date**: Records with no meeting_date sort after records with dates (NULLS LAST)

## Acceptance Criteria
- All CRUD endpoints (POST, GET list, GET single, PUT, DELETE) work with proper auth
- GET /{id}/html returns HTML content with `text/html` media type
- Entity-scoping validation prevents cross-entity access
- Delete requires admin or manager role
- List supports filtering by `prospect_id`, `is_active`, `meeting_date_from`, `meeting_date_to`
- List supports pagination via `skip` and `limit`
- `action_items` and `participants` are serialized from `List[str]` to JSON string on create/update
- All endpoints include INFO/ERROR print logging
- Router is registered in `main.py`
- All existing tests continue to pass (zero regressions)
- All new API tests pass

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/ -v` — Run all Server tests to validate the feature works with zero regressions
- `cd apps/Server && python -c "from src.adapter.rest.meeting_record_routes import router; print('Routes import OK')"` — Verify routes module imports cleanly
- `cd apps/Server && python -c "from src.core.services.meeting_record_service import meeting_record_service; print('Service import OK')"` — Verify service module imports cleanly
- `cd apps/Server && python -c "from src.repository.meeting_record_repository import meeting_record_repository; print('Repository import OK')"` — Verify repository module imports cleanly
- `cd apps/Server && python -c "from main import app; print('Main app imports OK')"` — Verify main.py imports and router registration work

## Notes
- This feature is backend-only (no UI components), so no E2E test file is needed. Wave 2 will add the frontend.
- The `action_items` and `participants` fields use `Text` column type (not JSONB) storing JSON strings. The repository must `json.dumps()` list values on write. The `MeetingRecordResponseDTO` returns these as raw `Optional[str]` — client-side parsing is expected.
- The `html_output` field can be large (full formatted meeting report). The dedicated `/html` endpoint returns it directly as `text/html` for browser rendering or download.
- This issue runs in parallel with CRM-001 through CRM-004. It depends on CRM-003 (MeetingRecordModel) and CRM-004 (prospect routes), both of which are already merged.
- No new dependencies are needed — all required packages are already in `requirements.txt`.
