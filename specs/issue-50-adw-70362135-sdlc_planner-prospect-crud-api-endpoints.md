# Feature: Prospect CRUD API Endpoints

## Metadata
issue_number: `50`
adw_id: `70362135`
issue_json: ``

## Feature Description
Create the full Prospect CRUD API stack following Clean Architecture: repository (data access), service (business logic), and routes (REST endpoints). All endpoints require JWT authentication and filter by entity_id. Includes a dedicated PATCH endpoint for stage updates that automatically records stage transitions in the audit trail via the existing StageTransitionRepository and PipelineStageRepository. The router is registered in main.py to expose `/api/prospects` endpoints.

## User Story
As an authenticated CRM user
I want to create, read, update, delete, and change the stage of prospects via REST API
So that I can manage my sales pipeline programmatically and have a full audit trail of stage changes

## Problem Statement
The Prospect model, DTOs, and database schema already exist (CRM-001), and the stage transition infrastructure exists (CRM-002/CRM-003), but there are no API endpoints to interact with prospect data. Without the repository, service, and routes layers, the frontend (Wave 2) and pipeline automation (Wave 3) cannot operate on prospects.

## Solution Statement
Build the three remaining Clean Architecture layers for prospects — ProspectRepository, ProspectService, and prospect_routes — following the exact patterns established by the PipelineStage CRUD stack. The PATCH stage-update endpoint will look up PipelineStage records by name, update the prospect's stage field, and create an immutable StageTransition audit record. Register the router in main.py.

## Relevant Files
Use these files to implement the feature:

### Existing Files (read for patterns and dependencies)
- `apps/Server/main.py` — Register the new prospect router here (follow the pipeline_stage_router pattern)
- `apps/Server/src/adapter/rest/pipeline_stage_routes.py` — Reference CRUD route patterns (POST/GET/PUT/DELETE, Query params, auth, logging)
- `apps/Server/src/core/services/pipeline_stage_service.py` — Reference service patterns (entity validation, singleton instance, transition recording)
- `apps/Server/src/repository/pipeline_stage_repository.py` — Reference repository patterns (CRUD methods, db.add/commit/refresh, singleton)
- `apps/Server/src/repository/stage_transition_repository.py` — Used by ProspectService to record stage transitions
- `apps/Server/src/models/prospect.py` — The Prospect SQLAlchemy model (already exists from CRM-001)
- `apps/Server/src/models/pipeline_stage.py` — PipelineStage model (used for stage ID lookups during PATCH)
- `apps/Server/src/models/stage_transition.py` — StageTransition model (audit trail records)
- `apps/Server/src/interface/prospect_dto.py` — All five Prospect DTOs (already exist from CRM-001)
- `apps/Server/src/interface/stage_transition_dto.py` — StageTransitionCreateDTO (used for recording transitions)
- `apps/Server/src/adapter/rest/dependencies.py` — `get_current_user`, `get_db` dependencies
- `apps/Server/src/adapter/rest/rbac_dependencies.py` — `require_roles` for admin/manager-only endpoints
- `apps/Server/tests/test_pipeline_stage_api.py` — Reference test patterns (mock setup, ASGITransport, auth token helper)
- `apps/Server/pytest.ini` — Test configuration (asyncio_mode = auto)

### Documentation Files
- `app_docs/feature-0f0d4c36-fastapi-backend-setup.md` — FastAPI backend architecture reference
- `app_docs/feature-57f962c3-prospect-data-model.md` — Prospect model and DTO specification
- `app_docs/feature-eb19b5cd-pipeline-stage-configuration.md` — Pipeline stage and transition system reference

### New Files
- `apps/Server/src/repository/prospect_repository.py` — Prospect data access layer
- `apps/Server/src/core/services/prospect_service.py` — Prospect business logic layer
- `apps/Server/src/adapter/rest/prospect_routes.py` — Prospect REST API endpoints
- `apps/Server/tests/test_prospect_api.py` — API integration tests

## Implementation Plan
### Phase 1: Foundation
Create the ProspectRepository with standard CRUD database operations. This is the data access layer that interacts directly with the Prospect model and the database session. Methods: create, get_by_id, get_by_entity (with filters + pagination), count_by_entity, update, delete.

### Phase 2: Core Implementation
Create the ProspectService with business logic. This layer validates entity ownership (prospect.entity_id must match the requested entity_id), delegates to ProspectRepository for data access, and handles the stage update flow. The stage update (PATCH) method: looks up old and new PipelineStage records by name via PipelineStageRepository, updates prospect.stage, then calls StageTransitionRepository.create_transition to record the audit trail.

### Phase 3: Integration
Create prospect_routes.py with FastAPI router (prefix `/api/prospects`). Implements 6 endpoints: POST create, GET list, GET by ID, PUT update, PATCH update-stage, DELETE. Register the router in main.py. Write comprehensive tests covering all endpoints, error cases, and auth/RBAC.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create ProspectRepository
- Create `apps/Server/src/repository/prospect_repository.py`
- Implement class `ProspectRepository` with methods:
  - `create_prospect(db, entity_id, company_name, contact_name, contact_email, contact_phone, stage, estimated_value, source, notes)` → creates and returns Prospect
  - `get_prospect_by_id(db, prospect_id)` → returns Optional[Prospect]
  - `get_prospects_by_entity(db, entity_id, stage, is_active, source, skip, limit)` → returns List[Prospect] with filter support
  - `count_prospects_by_entity(db, entity_id, stage, is_active, source)` → returns int with same filters
  - `update_prospect(db, prospect)` → commits and refreshes, returns Prospect
  - `delete_prospect(db, prospect)` → deletes from database
- Create singleton instance: `prospect_repository = ProspectRepository()`
- Follow exact patterns from `pipeline_stage_repository.py` (logging, type hints, docstrings)

### Step 2: Create ProspectService
- Create `apps/Server/src/core/services/prospect_service.py`
- Import `prospect_repository`, `pipeline_stage_repository`, `stage_transition_repository`
- Implement class `ProspectService` with methods:
  - `create_prospect(db, data: ProspectCreateDTO)` → creates via repository, returns Prospect
  - `get_prospect(db, prospect_id, entity_id)` → gets by ID, validates entity ownership, returns Optional[Prospect]
  - `list_prospects(db, entity_id, stage, is_active, source, skip, limit)` → returns Tuple[List[Prospect], int]
  - `update_prospect(db, prospect_id, entity_id, data: ProspectUpdateDTO)` → validates ownership, updates non-None fields, returns Optional[Prospect]
  - `update_prospect_stage(db, prospect_id, entity_id, new_stage, user_id)` → validates ownership, looks up old/new PipelineStage by name, updates prospect.stage, records StageTransition, returns Optional[Prospect]
  - `delete_prospect(db, prospect_id, entity_id)` → validates ownership, deletes, returns bool
- Create singleton instance: `prospect_service = ProspectService()`
- Follow exact patterns from `pipeline_stage_service.py`

### Step 3: Create Prospect Routes
- Create `apps/Server/src/adapter/rest/prospect_routes.py`
- Create router: `router = APIRouter(prefix="/api/prospects", tags=["Prospects"])`
- Create inline DTO for stage update: `ProspectStageUpdateDTO(BaseModel)` with fields `new_stage: Literal[...]` and optional `notes: str`
- Implement 6 endpoints:
  1. `POST /` → create prospect (response_model=ProspectResponseDTO, status=201, auth=get_current_user)
  2. `GET /` → list prospects (response_model=ProspectListResponseDTO, Query params: entity_id, stage, is_active, source, skip, limit, auth=get_current_user)
  3. `GET /{prospect_id}` → get single prospect (response_model=ProspectResponseDTO, Query param: entity_id, auth=get_current_user)
  4. `PUT /{prospect_id}` → update prospect (response_model=ProspectResponseDTO, Query param: entity_id, auth=get_current_user)
  5. `PATCH /{prospect_id}/stage` → update stage with transition tracking (response_model=ProspectResponseDTO, Query param: entity_id, auth=get_current_user)
  6. `DELETE /{prospect_id}` → delete prospect (status=204, Query param: entity_id, auth=require_roles(["admin", "manager"]))
- Follow exact patterns from `pipeline_stage_routes.py` (logging, error handling, HTTPException 404)

### Step 4: Register Router in main.py
- Add import: `from src.adapter.rest.prospect_routes import router as prospect_router`
- Add router: `app.include_router(prospect_router)`
- Add log: `print("INFO [Main]: Prospect router registered")`
- Place after the pipeline_stage_router registration to maintain logical ordering

### Step 5: Create API Integration Tests
- Create `apps/Server/tests/test_prospect_api.py`
- Reuse test patterns from `test_pipeline_stage_api.py` (mock DB, mock user, auth token helper)
- Create helper: `create_mock_prospect(entity_id, company_name, stage, ...)` returns MagicMock(spec=Prospect)
- Implement tests organized in sections:
  - **Create**: test_create_prospect_success, test_create_prospect_validation_error
  - **List**: test_list_prospects_success, test_list_prospects_with_filters
  - **Get**: test_get_prospect_success, test_get_prospect_not_found
  - **Update**: test_update_prospect_success, test_update_prospect_not_found
  - **Stage Update**: test_update_prospect_stage_success, test_update_prospect_stage_not_found
  - **Delete**: test_delete_prospect_success (admin), test_delete_prospect_not_found, test_delete_prospect_forbidden (non-admin user)
  - **Auth**: test_unauthenticated_request
- Patch targets:
  - `"src.core.services.prospect_service.prospect_repository"` for prospect CRUD
  - `"src.core.services.prospect_service.pipeline_stage_repository"` for stage lookups in PATCH
  - `"src.core.services.prospect_service.stage_transition_repository"` for transition recording in PATCH
  - `"src.core.services.auth_service.user_repository"` and `"src.core.services.auth_service.bcrypt"` for auth

### Step 6: Run Validation Commands
- Execute all validation commands listed below to confirm zero regressions

## Testing Strategy
### Unit Tests
- Test all 6 API endpoints for success cases (correct status codes, response shapes)
- Test 404 responses for get/update/delete/patch with non-existent prospect IDs
- Test 422 validation errors for missing required fields on create
- Test 403 forbidden when non-admin/manager tries to delete
- Test 401 for unauthenticated requests
- Test stage update endpoint records a StageTransition correctly
- Test list endpoint applies stage, is_active, and source filters

### Edge Cases
- Prospect belongs to different entity_id than requested → 404 (entity ownership validation)
- Update with all None fields → no changes, still returns 200
- Stage update with same stage as current → still succeeds and records transition
- Delete by user with "user" role → 403 forbidden
- Create with estimated_value of 0.00 → succeeds (ge=0 allows zero)
- List with no matching filters → empty list with total=0

## Acceptance Criteria
- POST `/api/prospects/` creates a prospect and returns 201 with ProspectResponseDTO
- GET `/api/prospects/?entity_id=<uuid>` returns paginated ProspectListResponseDTO filtered by entity
- GET `/api/prospects/<id>?entity_id=<uuid>` returns a single prospect or 404
- PUT `/api/prospects/<id>?entity_id=<uuid>` updates prospect fields and returns 200
- PATCH `/api/prospects/<id>/stage?entity_id=<uuid>` updates stage, records StageTransition, returns 200
- DELETE `/api/prospects/<id>?entity_id=<uuid>` deletes prospect (admin/manager only), returns 204
- All endpoints require JWT Bearer token (401 without)
- DELETE requires admin or manager role (403 for user/viewer)
- All endpoints validate entity_id ownership (prospect.entity_id must match)
- All pytest tests pass with zero failures
- TypeScript compilation succeeds (no frontend changes but verify no regressions)
- Build succeeds for both Client and Server

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest tests/test_prospect_api.py -v` — Run prospect-specific tests
- `cd apps/Server && uv run pytest` — Run all Server tests to validate zero regressions
- `cd apps/Client && npm run tsc --noEmit` — Run Client type check to validate zero regressions
- `cd apps/Client && npm run build` — Run Client build to validate zero regressions

## Notes
- This is a backend-only feature. No frontend changes required.
- This issue runs in parallel with CRM-001, CRM-002, CRM-003, CRM-005 which create independent files. The Prospect model, DTOs, PipelineStage and StageTransition infrastructure are assumed to already exist.
- The PATCH endpoint for stage updates is the key differentiator from a standard CRUD. It bridges the prospect and pipeline-stage subsystems by looking up PipelineStage records by name and creating immutable StageTransition audit records.
- Wave 2 (frontend) will consume these endpoints via a prospectService. Wave 3 (pipeline automation) will use POST and PATCH endpoints to create/update prospects from meeting transcripts.
- The `ProspectStageUpdateDTO` is defined inline in the routes file rather than in `prospect_dto.py` because it is route-specific and not part of the core prospect interface.
