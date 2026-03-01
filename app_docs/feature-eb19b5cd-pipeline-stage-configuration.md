# Pipeline Stage Configuration & Stage Transition History

**ADW ID:** eb19b5cd
**Date:** 2026-02-28
**Specification:** specs/issue-48-adw-eb19b5cd-sdlc_planner-pipeline-stage-configuration.md

## Overview

Adds configurable pipeline stages for CRM prospect tracking and an immutable stage transition history for audit trails. Pipeline stages define Kanban board columns per entity (e.g., Lead -> Contacted -> Qualified -> Proposal -> Negotiation -> Won -> Lost). Stage transitions record every prospect movement between stages with timestamps, actor, and optional notes.

This is a foundational backend-only feature (Wave 1, CRM-002) that CRM-004 will consume to update prospect stages via PATCH and record transitions automatically.

## What Was Built

- **`pipeline_stages` database table** — Entity-scoped configurable stages with ordering, colors, default flag, and soft-delete support
- **`stage_transitions` database table** — Immutable audit trail of prospect stage changes with from/to stages, actor, and notes
- **SQLAlchemy models** — `PipelineStage` and `StageTransition` with full type annotations and unique constraints
- **Pydantic DTOs** — Create, Update, Response, and List DTOs for both pipeline stages and stage transitions
- **Repositories** — CRUD for pipeline stages; read/create-only for stage transitions (immutable)
- **Service layer** — Business logic with entity ownership validation, default stage seeding, and transition recording
- **REST API endpoints** — Full CRUD for stages, seed endpoint for defaults, and transition history retrieval
- **Comprehensive tests** — 16 unit tests for models/DTOs and 12 API integration tests

## Technical Implementation

### Files Modified

- `apps/Server/database/schema.sql`: Added `pipeline_stages` and `stage_transitions` table definitions with constraints, indexes, and triggers
- `apps/Server/main.py`: Registered `pipeline_stage_router` and added startup log
- `apps/Server/src/models/__init__.py`: Registered `PipelineStage` and `StageTransition` model imports

### Files Created

- `apps/Server/src/models/pipeline_stage.py`: SQLAlchemy model with UUID PK, entity FK (CASCADE), unique constraints on `(entity_id, name)` and `(entity_id, order_index)`
- `apps/Server/src/models/stage_transition.py`: SQLAlchemy model with prospect/entity/stage FKs (SET NULL for stages/user to preserve audit trail on deletion)
- `apps/Server/src/interface/pipeline_stage_dto.py`: `PipelineStageCreateDTO`, `PipelineStageUpdateDTO`, `PipelineStageResponseDTO`, `PipelineStageListResponseDTO`
- `apps/Server/src/interface/stage_transition_dto.py`: `StageTransitionCreateDTO`, `StageTransitionResponseDTO`, `StageTransitionListResponseDTO`
- `apps/Server/src/repository/pipeline_stage_repository.py`: Full CRUD with entity-scoped queries ordered by `order_index`
- `apps/Server/src/repository/stage_transition_repository.py`: Create and read-only (no update/delete — transitions are immutable)
- `apps/Server/src/core/services/pipeline_stage_service.py`: Business logic including `seed_default_stages` for the seven standard stages
- `apps/Server/src/adapter/rest/pipeline_stage_routes.py`: Seven API endpoints under `/api/pipeline-stages`
- `apps/Server/tests/test_pipeline_stage_model.py`: 16 unit tests for models and DTOs
- `apps/Server/tests/test_pipeline_stage_api.py`: 12 API integration tests

### Key Changes

- **Entity-scoped stages**: Each entity has its own set of pipeline stages, enabling different organizations to customize their sales pipeline independently
- **Immutable audit trail**: `stage_transitions` has no `updated_at` column or update/delete repository methods — records are write-once for compliance
- **FK preservation**: Stage and user FKs in transitions use `SET NULL` on delete so audit history is never lost when stages or users are removed
- **Default seeding**: `seed_default_stages` creates seven standard stages (lead, contacted, qualified, proposal, negotiation, won, lost) with colors and ordering, but skips if the entity already has stages
- **RBAC enforcement**: Delete and seed endpoints require `admin` or `manager` roles; all other endpoints require authentication

## How to Use

### API Endpoints

1. **Seed default stages** for an entity:
   ```
   POST /api/pipeline-stages/seed
   Body: { "entity_id": "<uuid>" }
   Requires: admin or manager role
   ```

2. **List stages** for an entity (ordered by `order_index` for Kanban display):
   ```
   GET /api/pipeline-stages/?entity_id=<uuid>&active_only=true
   ```

3. **Create a custom stage**:
   ```
   POST /api/pipeline-stages/
   Body: { "entity_id": "<uuid>", "name": "demo", "display_name": "Demo", "order_index": 7, "color": "#B39DDB" }
   ```

4. **Update a stage** (e.g., change color or display name):
   ```
   PUT /api/pipeline-stages/<stage_id>?entity_id=<uuid>
   Body: { "display_name": "New Name", "color": "#FFFFFF" }
   ```

5. **Delete a stage** (admin/manager only):
   ```
   DELETE /api/pipeline-stages/<stage_id>?entity_id=<uuid>
   ```

6. **Get a single stage**:
   ```
   GET /api/pipeline-stages/<stage_id>?entity_id=<uuid>
   ```

7. **Get stage transition history** for a prospect:
   ```
   GET /api/pipeline-stages/transitions/<prospect_id>?entity_id=<uuid>&skip=0&limit=100
   ```

## Configuration

No additional environment variables or configuration required. The feature uses existing database connection and JWT auth infrastructure.

### Default Stages (seeded via `/seed`)

| Order | Name         | Display Name | Color   | Default |
|-------|-------------|--------------|---------|---------|
| 0     | lead        | Lead         | #90CAF9 | Yes     |
| 1     | contacted   | Contacted    | #80DEEA | No      |
| 2     | qualified   | Qualified    | #A5D6A7 | No      |
| 3     | proposal    | Proposal     | #FFE082 | No      |
| 4     | negotiation | Negotiation  | #FFAB91 | No      |
| 5     | won         | Won          | #66BB6A | No      |
| 6     | lost        | Lost         | #EF5350 | No      |

## Testing

```bash
# Unit tests for models and DTOs
cd apps/Server && uv run pytest tests/test_pipeline_stage_model.py -v

# API integration tests
cd apps/Server && uv run pytest tests/test_pipeline_stage_api.py -v

# Full test suite (zero regressions)
cd apps/Server && uv run pytest
```

## Notes

- This is a **backend-only** feature — no frontend UI components are included. CRM-004 will add the PATCH endpoint for prospect stage updates that creates transitions automatically.
- The seven default stages match the existing `prospects.stage` CHECK constraint values, providing backward compatibility during migration to configurable stages.
- Stage transitions support `from_stage_id = NULL` for initial prospect assignment and `transitioned_by = NULL` for system-initiated transitions.
- Unique constraints on `(entity_id, name)` and `(entity_id, order_index)` prevent duplicate stage names and ordering conflicts within an entity.
