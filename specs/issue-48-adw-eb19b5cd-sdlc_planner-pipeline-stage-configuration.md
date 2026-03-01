# Feature: Pipeline Stage Configuration & Stage Transition History

## Metadata
issue_number: `48`
adw_id: `eb19b5cd`
issue_json: `{"number":48,"title":"[CRM Pipeline] Wave 1: Pipeline Stage Configuration","body":"## Context\n**Project:** Meeting Processing CRM Pipeline — CRM prospect tracking and automated meeting transcript processing for Finance Tracker\n**Overview:** Define the pipeline stages for prospect tracking and create a stage transition history model. Stages are ordered for Kanban column display. Stage transitions are recorded with timestamps to provide an audit trail.\n\n**Current Wave:** Wave 1 of 3 — Foundation (Data Models & Backend API)\n**Current Issue:** CRM-002 (Issue 2 of 14)\n**Parallel Execution:** YES — This issue runs in parallel with CRM-001, CRM-003.\n\n**Dependencies:** None\n**What comes next:** CRM-004 uses stages for the PATCH endpoint that updates prospect stage and records transitions.\n\n## Request\nCreate pipeline stage configuration and stage transition history tracking."}`

## Feature Description
Add configurable pipeline stages for CRM prospect tracking and an immutable stage transition history for audit trails. Pipeline stages define the columns of a Kanban board — each entity can have its own ordered set of stages (e.g., Lead → Contacted → Qualified → Proposal → Negotiation → Won → Lost). Stage transitions record every time a prospect moves between stages, capturing who made the change, when, and optional notes.

This is a foundational data model + API feature (Wave 1, CRM-002) that CRM-004 will consume to update prospect stages via PATCH and record transitions automatically.

## User Story
As an admin or manager of an entity
I want to configure pipeline stages and track stage transitions for prospects
So that I can customize my sales pipeline workflow and maintain a complete audit trail of prospect movement through the pipeline

## Problem Statement
The existing `prospects.stage` column uses a hardcoded CHECK constraint with seven fixed values. There is no way to customize stages per entity, reorder them for Kanban display, or track the history of stage changes for audit purposes.

## Solution Statement
Create two new database tables and their full backend stack (model, DTO, repository, service, routes, tests):

1. **`pipeline_stages`** — Entity-scoped configurable stages with `order_index` for Kanban column ordering, `color` for UI display, and `is_default` to mark the initial stage for new prospects.
2. **`stage_transitions`** — Immutable audit records linking a prospect to its from/to stages with timestamps, the user who triggered the change, and optional notes. No `updated_at` column since transitions are write-once.

Seed the default seven stages (lead, contacted, qualified, proposal, negotiation, won, lost) via a service method so each entity starts with the standard pipeline.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/database/schema.sql` — Append new `pipeline_stages` and `stage_transitions` tables following existing table patterns (UUID PKs, FK constraints, indexes, triggers)
- `apps/Server/src/models/__init__.py` — Register new `PipelineStage` and `StageTransition` models
- `apps/Server/src/models/prospect.py` — Reference for entity-scoped model pattern (FK to entities, column types, `__repr__`)
- `apps/Server/src/interface/prospect_dto.py` — Reference for DTO patterns (Create, Update, Response, List, Filter DTOs)
- `apps/Server/src/repository/transaction_repository.py` — Reference for repository pattern (singleton, CRUD, filtering, logging)
- `apps/Server/src/core/services/transaction_service.py` — Reference for service pattern (entity ownership validation, business logic, logging)
- `apps/Server/src/adapter/rest/transaction_routes.py` — Reference for route pattern (async endpoints, Query params, Depends, HTTPException, RBAC)
- `apps/Server/src/adapter/rest/dependencies.py` — `get_current_user`, `get_db` dependency injection
- `apps/Server/src/adapter/rest/rbac_dependencies.py` — `require_roles` for admin/manager-only endpoints
- `apps/Server/src/config/database.py` — `Base` import for SQLAlchemy models
- `apps/Server/main.py` — Router registration point
- `apps/Server/tests/test_prospect_model.py` — Reference for model/DTO unit test patterns
- `app_docs/feature-57f962c3-prospect-data-model.md` — Prospect model documentation (stage values, entity scoping)
- `app_docs/feature-0f0d4c36-fastapi-backend-setup.md` — Backend setup documentation (router registration, lifespan)
- `app_docs/feature-db5f36c7-database-schema-tables.md` — Database schema documentation (table patterns, constraints, indexes)

### New Files
- `apps/Server/src/models/pipeline_stage.py` — SQLAlchemy PipelineStage model
- `apps/Server/src/models/stage_transition.py` — SQLAlchemy StageTransition model
- `apps/Server/src/interface/pipeline_stage_dto.py` — Pipeline stage DTOs (Create, Update, Response, List)
- `apps/Server/src/interface/stage_transition_dto.py` — Stage transition DTOs (Create, Response, List)
- `apps/Server/src/repository/pipeline_stage_repository.py` — PipelineStage CRUD repository
- `apps/Server/src/repository/stage_transition_repository.py` — StageTransition read/create repository
- `apps/Server/src/core/services/pipeline_stage_service.py` — Pipeline stage business logic + default seeding
- `apps/Server/src/adapter/rest/pipeline_stage_routes.py` — Pipeline stage + transition API routes
- `apps/Server/tests/test_pipeline_stage_model.py` — Unit tests for models and DTOs
- `apps/Server/tests/test_pipeline_stage_api.py` — API integration tests for routes

## Implementation Plan
### Phase 1: Foundation
1. Define the `pipeline_stages` and `stage_transitions` database tables in `schema.sql`
2. Create SQLAlchemy models for both tables
3. Register models in `__init__.py`

### Phase 2: Core Implementation
1. Create Pydantic DTOs for pipeline stages (CRUD) and stage transitions (create + read-only)
2. Implement repositories for both tables
3. Implement service layer with business logic (entity ownership, stage ordering, default seeding)
4. Create API routes with full CRUD for stages and read/create for transitions

### Phase 3: Integration
1. Register pipeline stage router in `main.py`
2. Write comprehensive unit tests for models and DTOs
3. Write API integration tests for all endpoints
4. Validate with existing test suite to ensure zero regressions

## Step by Step Tasks

### Step 1: Add Database Tables to Schema
- Append `pipeline_stages` table to `apps/Server/database/schema.sql`:
  - `id UUID PRIMARY KEY DEFAULT uuid_generate_v4()`
  - `entity_id UUID NOT NULL` (FK → entities CASCADE)
  - `name VARCHAR(100) NOT NULL` — machine-readable stage identifier (e.g., "lead", "contacted")
  - `display_name VARCHAR(100) NOT NULL` — human-readable label (e.g., "Lead", "Contacted")
  - `order_index INTEGER NOT NULL` — position in Kanban display (0-based)
  - `color VARCHAR(50)` — optional hex color for UI
  - `is_default BOOLEAN DEFAULT FALSE` — marks the initial stage for new prospects
  - `is_active BOOLEAN DEFAULT TRUE` — soft delete
  - `created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()`
  - `updated_at TIMESTAMP WITH TIME ZONE`
  - UNIQUE constraint on `(entity_id, name)` — no duplicate stage names per entity
  - UNIQUE constraint on `(entity_id, order_index)` — no duplicate positions per entity
  - Index on `entity_id`
  - Index on `is_active`
  - Composite index on `(entity_id, order_index)` for sorted retrieval
  - `updated_at` trigger
- Append `stage_transitions` table to `apps/Server/database/schema.sql`:
  - `id UUID PRIMARY KEY DEFAULT uuid_generate_v4()`
  - `prospect_id UUID NOT NULL` (FK → prospects CASCADE)
  - `entity_id UUID NOT NULL` (FK → entities CASCADE)
  - `from_stage_id UUID` (FK → pipeline_stages SET NULL, nullable for initial assignment)
  - `to_stage_id UUID NOT NULL` (FK → pipeline_stages SET NULL)
  - `transitioned_by UUID` (FK → users SET NULL)
  - `notes TEXT` — optional transition notes
  - `created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()`
  - NO `updated_at` — transitions are immutable
  - Index on `prospect_id`
  - Index on `entity_id`
  - Composite index on `(prospect_id, created_at)` for ordered history

### Step 2: Create PipelineStage SQLAlchemy Model
- Create `apps/Server/src/models/pipeline_stage.py`
- Follow the pattern in `prospect.py`: UUID PK, entity FK with CASCADE, type annotations, `__repr__`
- Columns: `id`, `entity_id`, `name`, `display_name`, `order_index`, `color`, `is_default`, `is_active`, `created_at`, `updated_at`
- Use `Integer` for `order_index`, `Boolean` for `is_default`/`is_active`
- Add `UniqueConstraint("entity_id", "name", name="uq_pipeline_stages_entity_name")` and `UniqueConstraint("entity_id", "order_index", name="uq_pipeline_stages_entity_order")` via `__table_args__`

### Step 3: Create StageTransition SQLAlchemy Model
- Create `apps/Server/src/models/stage_transition.py`
- Columns: `id`, `prospect_id` (FK → prospects CASCADE), `entity_id` (FK → entities CASCADE), `from_stage_id` (FK → pipeline_stages SET NULL, nullable), `to_stage_id` (FK → pipeline_stages SET NULL), `transitioned_by` (FK → users SET NULL, nullable), `notes`, `created_at`
- NO `updated_at` column — transitions are immutable audit records
- `__repr__` shows prospect_id, from_stage_id, to_stage_id

### Step 4: Register Models
- Update `apps/Server/src/models/__init__.py`
- Add imports for `PipelineStage` and `StageTransition`
- Add both to `__all__`

### Step 5: Create Pipeline Stage DTOs
- Create `apps/Server/src/interface/pipeline_stage_dto.py`
- `PipelineStageCreateDTO`: `entity_id` (UUID, required), `name` (str, 1-100, required), `display_name` (str, 1-100, required), `order_index` (int, ge=0, required), `color` (Optional[str], max 50), `is_default` (bool, default False)
- `PipelineStageUpdateDTO`: All fields optional except `entity_id` — `name`, `display_name`, `order_index`, `color`, `is_default`, `is_active`
- `PipelineStageResponseDTO`: All fields + `id`, `created_at`, `updated_at` with `model_config = {"from_attributes": True}`
- `PipelineStageListResponseDTO`: `stages: List[PipelineStageResponseDTO]`, `total: int`

### Step 6: Create Stage Transition DTOs
- Create `apps/Server/src/interface/stage_transition_dto.py`
- `StageTransitionCreateDTO`: `prospect_id` (UUID), `entity_id` (UUID), `from_stage_id` (Optional[UUID]), `to_stage_id` (UUID), `transitioned_by` (Optional[UUID]), `notes` (Optional[str])
- `StageTransitionResponseDTO`: All fields + `id`, `created_at` with `model_config = {"from_attributes": True}`
- `StageTransitionListResponseDTO`: `transitions: List[StageTransitionResponseDTO]`, `total: int`

### Step 7: Create Pipeline Stage Repository
- Create `apps/Server/src/repository/pipeline_stage_repository.py`
- `PipelineStageRepository` class with methods:
  - `create_stage(db, entity_id, name, display_name, order_index, color, is_default)` → PipelineStage
  - `get_stage_by_id(db, stage_id)` → Optional[PipelineStage]
  - `get_stages_by_entity(db, entity_id, active_only=True)` → List[PipelineStage] (ordered by `order_index`)
  - `get_stage_by_name(db, entity_id, name)` → Optional[PipelineStage] (lookup by entity + name)
  - `count_stages_by_entity(db, entity_id, active_only=True)` → int
  - `update_stage(db, stage)` → PipelineStage
  - `delete_stage(db, stage)` → None
- Singleton: `pipeline_stage_repository = PipelineStageRepository()`
- Follow logging pattern: `print(f"INFO [PipelineStageRepository]: ...")`

### Step 8: Create Stage Transition Repository
- Create `apps/Server/src/repository/stage_transition_repository.py`
- `StageTransitionRepository` class with methods:
  - `create_transition(db, prospect_id, entity_id, from_stage_id, to_stage_id, transitioned_by, notes)` → StageTransition
  - `get_transitions_by_prospect(db, prospect_id, skip, limit)` → List[StageTransition] (ordered by `created_at` desc)
  - `count_transitions_by_prospect(db, prospect_id)` → int
  - `get_transitions_by_entity(db, entity_id, skip, limit)` → List[StageTransition]
  - `count_transitions_by_entity(db, entity_id)` → int
- NO update or delete methods — transitions are immutable
- Singleton: `stage_transition_repository = StageTransitionRepository()`

### Step 9: Create Pipeline Stage Service
- Create `apps/Server/src/core/services/pipeline_stage_service.py`
- `PipelineStageService` class with methods:
  - `create_stage(db, data: PipelineStageCreateDTO)` → PipelineStage
  - `get_stage(db, stage_id, entity_id)` → Optional[PipelineStage] (with entity ownership check)
  - `list_stages(db, entity_id, active_only=True)` → Tuple[List[PipelineStage], int]
  - `update_stage(db, stage_id, entity_id, data: PipelineStageUpdateDTO)` → Optional[PipelineStage]
  - `delete_stage(db, stage_id, entity_id)` → bool
  - `seed_default_stages(db, entity_id)` → List[PipelineStage] — Creates the seven default stages (lead, contacted, qualified, proposal, negotiation, won, lost) with correct order_index and "lead" as is_default. Skips if entity already has stages.
  - `record_transition(db, data: StageTransitionCreateDTO)` → StageTransition
  - `get_prospect_transitions(db, prospect_id, entity_id, skip, limit)` → Tuple[List[StageTransition], int]
- Singleton: `pipeline_stage_service = PipelineStageService()`

### Step 10: Create Pipeline Stage Routes
- Create `apps/Server/src/adapter/rest/pipeline_stage_routes.py`
- `router = APIRouter(prefix="/api/pipeline-stages", tags=["Pipeline Stages"])`
- Endpoints:
  - `POST /` → Create a pipeline stage (201). Requires auth.
  - `GET /` → List pipeline stages for entity. Query params: `entity_id` (required), `active_only` (default True), `skip`, `limit`. Requires auth.
  - `GET /{stage_id}` → Get single stage. Query param: `entity_id`. Requires auth.
  - `PUT /{stage_id}` → Update a stage. Query param: `entity_id`. Requires auth.
  - `DELETE /{stage_id}` → Delete a stage. Query param: `entity_id`. Requires `admin` or `manager` role.
  - `POST /seed` → Seed default stages for entity. Body: `entity_id`. Requires `admin` or `manager` role. Returns list of created stages.
  - `GET /transitions/{prospect_id}` → Get stage transition history for a prospect. Query params: `entity_id`, `skip`, `limit`. Requires auth.

### Step 11: Register Router in main.py
- Import `pipeline_stage_routes.router` as `pipeline_stage_router`
- Add `app.include_router(pipeline_stage_router)` after existing router registrations
- Add `print("INFO [Main]: Pipeline Stage router registered")`

### Step 12: Write Unit Tests for Models and DTOs
- Create `apps/Server/tests/test_pipeline_stage_model.py`
- Follow `test_prospect_model.py` pattern with `print("INFO [TestPipelineStage]: ... - PASSED")` in every test
- Test cases:
  - `test_pipeline_stage_create_dto_valid` — all fields
  - `test_pipeline_stage_create_dto_minimal` — only required fields
  - `test_pipeline_stage_create_dto_empty_name` — validation error
  - `test_pipeline_stage_create_dto_negative_order` — validation error
  - `test_pipeline_stage_update_dto_partial` — partial update
  - `test_pipeline_stage_update_dto_empty` — all None
  - `test_pipeline_stage_response_dto_from_attributes` — ORM to DTO via MagicMock
  - `test_pipeline_stage_list_response_dto` — list with total
  - `test_pipeline_stage_model_repr` — `__repr__`
  - `test_pipeline_stage_model_tablename` — `__tablename__`
  - `test_stage_transition_create_dto_valid` — all fields
  - `test_stage_transition_create_dto_no_from_stage` — null from_stage_id (initial assignment)
  - `test_stage_transition_response_dto_from_attributes` — ORM to DTO
  - `test_stage_transition_list_response_dto` — list with total
  - `test_stage_transition_model_repr` — `__repr__`
  - `test_stage_transition_model_tablename` — `__tablename__`

### Step 13: Write API Integration Tests
- Create `apps/Server/tests/test_pipeline_stage_api.py`
- Follow `test_transactions.py` pattern: `AsyncClient`, `patch`, mock db/auth/repository
- Test cases:
  - `test_create_pipeline_stage_success` — 201 with valid data
  - `test_create_pipeline_stage_validation_error` — 422 with missing required fields
  - `test_list_pipeline_stages_success` — 200 with entity_id query param
  - `test_get_pipeline_stage_success` — 200 with valid stage_id
  - `test_get_pipeline_stage_not_found` — 404
  - `test_update_pipeline_stage_success` — 200 with partial update
  - `test_update_pipeline_stage_not_found` — 404
  - `test_delete_pipeline_stage_success` — 204
  - `test_delete_pipeline_stage_not_found` — 404
  - `test_seed_default_stages_success` — 200/201 with list of 7 stages
  - `test_get_prospect_transitions_success` — 200 with transition history
  - `test_unauthenticated_request` — 401

### Step 14: Validate — Run All Tests and Checks
- Run full test suite to verify zero regressions
- Run type check and build for frontend (no frontend changes, but verify no breakage)

## Testing Strategy
### Unit Tests
- Model instantiation and `__repr__` for PipelineStage and StageTransition
- DTO validation for all Create/Update/Response/List DTOs with valid, minimal, and invalid inputs
- DTO `from_attributes` serialization from mock ORM objects
- `__tablename__` verification for both models

### Edge Cases
- Creating a stage with `order_index` 0 (first position)
- Stage transition with `from_stage_id = None` (initial prospect assignment)
- Stage transition with `transitioned_by = None` (system-initiated transition)
- Seeding default stages when entity already has stages (should skip/no-op)
- Updating `is_default` on a stage (only one stage per entity should be default)
- Deleting a stage that has transitions pointing to it (FK uses SET NULL)
- Empty `color` field (nullable, optional)
- Maximum length validation on `name` (100 chars) and `display_name` (100 chars)

## Acceptance Criteria
- `pipeline_stages` table defined in schema.sql with UUID PK, entity FK, unique constraints on (entity_id, name) and (entity_id, order_index), indexes, and updated_at trigger
- `stage_transitions` table defined in schema.sql with UUID PK, prospect/entity/stage FKs, NO updated_at trigger (immutable records)
- `PipelineStage` SQLAlchemy model with all columns, type annotations, and `__repr__`
- `StageTransition` SQLAlchemy model with all columns, type annotations, and `__repr__`
- Both models registered in `models/__init__.py`
- Full Pydantic DTO sets for both models with proper validation (Field constraints, Literal types)
- CRUD repository for pipeline stages with entity-scoped queries ordered by `order_index`
- Read/create-only repository for stage transitions (no update/delete)
- Service layer with entity ownership validation, default stage seeding, and transition recording
- REST API with CRUD endpoints for stages, seed endpoint, and transition history endpoint
- Router registered in `main.py`
- All unit tests pass (16+ tests for models/DTOs)
- All API integration tests pass (12+ tests for routes)
- Existing test suite passes with zero regressions
- All logging follows `print(f"INFO [ClassName]: ...")` pattern

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest tests/test_pipeline_stage_model.py -v` — Run pipeline stage model/DTO unit tests
- `cd apps/Server && uv run pytest tests/test_pipeline_stage_api.py -v` — Run pipeline stage API integration tests
- `cd apps/Server && uv run pytest` — Run full Server test suite to validate zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check (no frontend changes, verify no breakage)
- `cd apps/Client && npm run build` — Run Client build (no frontend changes, verify no breakage)

## Notes
- This feature is backend-only (no UI components), so no E2E test file is needed.
- The `pipeline_stages` table uses FK references to `entities` with CASCADE delete, matching the pattern used by `prospects`, `transactions`, `budgets`, etc.
- The `stage_transitions` table uses SET NULL for `from_stage_id`, `to_stage_id`, and `transitioned_by` FKs so that deleting a stage or user doesn't cascade-delete the audit trail.
- CRM-004 (Issue next) will add a PATCH endpoint to `prospects` that changes `stage` and automatically creates a `stage_transition` record. This issue just provides the foundation.
- The `seed_default_stages` method creates the same seven stages that are currently hardcoded in the `prospects.stage` CHECK constraint. This provides backward compatibility during the transition to configurable stages.
- Running in parallel with CRM-001 (Issue #47, already merged) and CRM-003. No merge conflicts expected since this creates entirely new files and only appends to `schema.sql` and `main.py`.
