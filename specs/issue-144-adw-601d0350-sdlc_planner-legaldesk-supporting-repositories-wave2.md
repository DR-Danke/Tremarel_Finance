# Feature: Legal Desk Wave 2 — Supporting Repositories (Assignment, Deliverable, Message, Analytics)

## Metadata
issue_number: `144`
adw_id: `601d0350`
issue_json: ``

## Feature Description
Implement four supporting repository classes for the Legal Desk case management module: Assignment Repository (case-specialist links with fee negotiation), Deliverable Repository (milestone tracking with status transitions), Message Repository (case communication threads with internal/external filtering), and Analytics Repository (dashboard aggregations for cases, revenue, and specialist performance). These repositories complete the data access layer (Wave 2) and will be consumed by Wave 3 service classes.

## User Story
As a Faroo Legal Desk platform operator
I want a complete data access layer for assignments, deliverables, messages, and analytics
So that Wave 3 services can orchestrate business logic for case management, specialist assignment, milestone tracking, communication, and dashboard reporting

## Problem Statement
The Legal Desk module has ORM models (Wave 1, LD-003) and DTOs (LD-004) defined, but no repository layer to perform database CRUD and aggregation operations. Without repositories, services cannot persist or query assignment records, track deliverable status transitions, store case messages with internal/external filtering, or compute analytics aggregations for the dashboard.

## Solution Statement
Create four repository files following the established singleton-class pattern used by `EntityRepository` and other existing repositories. Each repository encapsulates all database operations for its domain entity, accepts `db: Session` as the first parameter, includes comprehensive logging, and exports a singleton instance. The Analytics repository uses raw SQLAlchemy aggregation queries (func.count, func.sum, func.avg) to produce dashboard statistics without loading full ORM objects.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/src/repository/entity_repository.py` — Reference pattern for repository class structure, logging, singleton export
- `apps/Server/src/repository/__init__.py` — Must be updated to export new repository singletons
- `apps/Server/src/models/ld_case_specialist.py` — ORM model for LdCaseSpecialist (assignment junction table)
- `apps/Server/src/models/ld_case_deliverable.py` — ORM model for LdCaseDeliverable
- `apps/Server/src/models/ld_case_message.py` — ORM model for LdCaseMessage
- `apps/Server/src/models/ld_case.py` — ORM model for LdCase (needed by analytics queries)
- `apps/Server/src/models/ld_specialist.py` — ORM model for LdSpecialist (needed by analytics rankings)
- `apps/Server/src/models/ld_specialist_score.py` — ORM model for LdSpecialistScore (needed by analytics rankings)
- `apps/Server/src/interface/legaldesk_dto.py` — DTOs and enums (AssignmentStatus, DeliverableStatus, CaseStatus)
- `apps/Server/src/config/database.py` — Database session/Base configuration
- `app_docs/feature-40f52fef-legaldesk-sqlalchemy-orm-models.md` — ORM model documentation
- `app_docs/feature-cbc09752-legaldesk-pydantic-dtos-enums.md` — DTO and enum documentation
- `app_docs/feature-de0cefbe-legaldesk-database-schema.md` — Database schema reference

### New Files
- `apps/Server/src/repository/ld_assignment_repository.py` — Assignment (case-specialist) repository
- `apps/Server/src/repository/ld_deliverable_repository.py` — Deliverable repository
- `apps/Server/src/repository/ld_message_repository.py` — Message repository
- `apps/Server/src/repository/ld_analytics_repository.py` — Analytics aggregation repository
- `apps/Server/tests/test_ld_assignment_repository.py` — Unit tests for assignment repository
- `apps/Server/tests/test_ld_deliverable_repository.py` — Unit tests for deliverable repository
- `apps/Server/tests/test_ld_message_repository.py` — Unit tests for message repository
- `apps/Server/tests/test_ld_analytics_repository.py` — Unit tests for analytics repository

## Implementation Plan
### Phase 1: Foundation
- Read and understand the existing repository pattern from `entity_repository.py` (singleton class, `db: Session` parameter, logging with `print(f"INFO [ClassName]: ...")`)
- Read ORM models (`ld_case_specialist.py`, `ld_case_deliverable.py`, `ld_case_message.py`, `ld_case.py`, `ld_specialist.py`) to understand column names, relationships, and types
- Read DTOs (`legaldesk_dto.py`) to understand status enums and response shapes

### Phase 2: Core Implementation
- Create all four repository files with the specified methods
- Each repository follows the same structure: imports, class with methods, singleton instance at bottom
- Assignment repository handles fee updates with Decimal types
- Deliverable repository handles status transitions with timestamp updates (completed_at)
- Message repository implements internal message filtering via `is_internal` flag
- Analytics repository uses SQLAlchemy `func` for GROUP BY, SUM, AVG aggregations

### Phase 3: Integration
- Update `apps/Server/src/repository/__init__.py` to export all four new repository singletons
- Create unit tests for all four repositories using mock `Session` objects following existing test patterns
- Validate all tests pass and no regressions in existing tests

## Step by Step Tasks

### Step 1: Read reference files
- Read `apps/Server/src/repository/entity_repository.py` for the repository pattern
- Read `apps/Server/src/models/ld_case_specialist.py`, `ld_case_deliverable.py`, `ld_case_message.py`, `ld_case.py`, `ld_specialist.py`, `ld_specialist_score.py` for ORM column names
- Read `apps/Server/src/interface/legaldesk_dto.py` for status enums (AssignmentStatus, DeliverableStatus, CaseStatus)

### Step 2: Create Assignment Repository
- Create `apps/Server/src/repository/ld_assignment_repository.py`
- Implement class `LdAssignmentRepository` with methods:
  - `create_assignment(self, db: Session, data: dict) -> LdCaseSpecialist` — Create a new assignment record from dict fields (case_id, specialist_id, role, proposed_fee, fee_currency, status defaults to "pending")
  - `get_case_specialists(self, db: Session, case_id: int) -> list[LdCaseSpecialist]` — Query all assignments for a case, ordered by assigned_at DESC
  - `get_specialist_cases(self, db: Session, specialist_id: int) -> list[LdCaseSpecialist]` — Query all assignments for a specialist, ordered by assigned_at DESC
  - `update_assignment_status(self, db: Session, assignment_id: int, status: str) -> Optional[LdCaseSpecialist]` — Update status field; set responded_at=now when status changes from pending
  - `update_fees(self, db: Session, assignment_id: int, proposed_fee: Decimal, agreed_fee: Decimal, fee_type: str) -> Optional[LdCaseSpecialist]` — Update proposed_fee, agreed_fee, and fee_currency fields
- Export singleton: `ld_assignment_repository = LdAssignmentRepository()`
- Include logging on every method entry and exit

### Step 3: Create Deliverable Repository
- Create `apps/Server/src/repository/ld_deliverable_repository.py`
- Implement class `LdDeliverableRepository` with methods:
  - `create(self, db: Session, data: dict) -> LdCaseDeliverable` — Create deliverable from dict (case_id, title, description, specialist_id, due_date, status defaults to "pending")
  - `get_by_case(self, db: Session, case_id: int) -> list[LdCaseDeliverable]` — Query all deliverables for a case, ordered by created_at ASC
  - `update(self, db: Session, deliverable_id: int, data: dict) -> Optional[LdCaseDeliverable]` — Partial update from dict; only set fields present in data
  - `update_status(self, db: Session, deliverable_id: int, status: str) -> Optional[LdCaseDeliverable]` — Update status; when status is "completed", set completed_at=now; valid transitions: pending->in_progress->review->completed/cancelled
- Export singleton: `ld_deliverable_repository = LdDeliverableRepository()`

### Step 4: Create Message Repository
- Create `apps/Server/src/repository/ld_message_repository.py`
- Implement class `LdMessageRepository` with methods:
  - `create(self, db: Session, data: dict) -> LdCaseMessage` — Create message from dict (case_id, sender_type, sender_name, message, is_internal)
  - `get_by_case(self, db: Session, case_id: int, include_internal: bool = False) -> list[LdCaseMessage]` — Query messages for a case ordered by created_at ASC; when include_internal=False, filter out records where is_internal=True
- Export singleton: `ld_message_repository = LdMessageRepository()`

### Step 5: Create Analytics Repository
- Create `apps/Server/src/repository/ld_analytics_repository.py`
- Implement class `LdAnalyticsRepository` with methods:
  - `count_cases_by_status(self, db: Session) -> dict[str, int]` — `SELECT status, COUNT(*) FROM ld_cases GROUP BY status` using `func.count`
  - `count_cases_by_domain(self, db: Session) -> dict[str, int]` — `SELECT legal_domain, COUNT(*) FROM ld_cases GROUP BY legal_domain`
  - `revenue_pipeline(self, db: Session) -> dict` — Sum estimated_cost and final_quote for active cases (status IN active, in_progress, review, negotiating); return dict with `total_estimated_cost`, `total_final_quote`, `active_case_count`
  - `specialist_performance_rankings(self, db: Session) -> list[dict]` — Query LdSpecialist ordered by overall_score DESC, is_active=True; return list of dicts with id, full_name, overall_score, current_workload
  - `avg_case_duration(self, db: Session) -> Optional[float]` — AVG of (updated_at - created_at) for completed cases (status='completed'); return None if no completed cases
- Export singleton: `ld_analytics_repository = LdAnalyticsRepository()`
- Import `func` from `sqlalchemy` for aggregation functions

### Step 6: Update repository __init__.py
- Add imports for all four new repository singletons to `apps/Server/src/repository/__init__.py`
- Add them to the `__all__` list

### Step 7: Create unit tests for Assignment Repository
- Create `apps/Server/tests/test_ld_assignment_repository.py`
- Mock `db: Session` using `MagicMock`
- Test `create_assignment` — verify model fields are set correctly, db.add/commit/refresh called
- Test `get_case_specialists` — verify correct filter and order_by
- Test `get_specialist_cases` — verify correct filter and order_by
- Test `update_assignment_status` — verify status update, responded_at set when transitioning from pending
- Test `update_fees` — verify Decimal fee fields are correctly persisted
- Test not-found cases return None

### Step 8: Create unit tests for Deliverable Repository
- Create `apps/Server/tests/test_ld_deliverable_repository.py`
- Test `create` — verify default status is "pending"
- Test `get_by_case` — verify filter and ordering
- Test `update` — verify partial update only sets provided fields
- Test `update_status` — verify completed_at is set when status="completed"; verify it is not set for other statuses
- Test not-found cases return None

### Step 9: Create unit tests for Message Repository
- Create `apps/Server/tests/test_ld_message_repository.py`
- Test `create` — verify all fields including is_internal
- Test `get_by_case` with `include_internal=False` — verify is_internal=True messages are excluded
- Test `get_by_case` with `include_internal=True` — verify all messages returned

### Step 10: Create unit tests for Analytics Repository
- Create `apps/Server/tests/test_ld_analytics_repository.py`
- Test `count_cases_by_status` — mock query to return grouped results, verify dict output
- Test `count_cases_by_domain` — similar grouped result test
- Test `revenue_pipeline` — verify sum aggregation with active case filter
- Test `specialist_performance_rankings` — verify ordering and dict structure
- Test `avg_case_duration` — verify average calculation; test None return when no completed cases

### Step 11: Run validation commands
- Run `cd apps/Server && python -m pytest tests/` to validate all tests pass with zero regressions
- Run `cd apps/Client && npx tsc --noEmit` to verify no frontend type regressions
- Run `cd apps/Client && npm run build` to verify frontend build succeeds

## Testing Strategy
### Unit Tests
- All four repositories get dedicated test files using `unittest.mock.MagicMock` for the SQLAlchemy Session
- Tests verify: correct model instantiation, correct query filters, correct method calls on session (add, commit, refresh, delete)
- Tests verify return types match ORM model types or dict/list/float as specified
- Tests verify logging output (optional — can use capsys or mock print)

### Edge Cases
- **Assignment: Not found** — `update_assignment_status` and `update_fees` with non-existent assignment_id should return None
- **Deliverable: Not found** — `update` and `update_status` with non-existent deliverable_id should return None
- **Deliverable: Status transition to completed** — `completed_at` must be set to current UTC time
- **Deliverable: Status transition to non-completed** — `completed_at` must NOT be set
- **Message: Internal filtering** — `get_by_case(include_internal=False)` must exclude is_internal=True messages
- **Message: Include internal** — `get_by_case(include_internal=True)` must return ALL messages
- **Analytics: No completed cases** — `avg_case_duration` returns None (not 0, not error)
- **Analytics: No active cases** — `revenue_pipeline` returns zeroed dict
- **Analytics: Empty tables** — All analytics methods handle empty result sets gracefully
- **Assignment: Fee update with Decimal precision** — Verify Decimal values are passed through without float conversion

## Acceptance Criteria
- All four repository files exist at the specified paths under `apps/Server/src/repository/`
- Each repository class follows the established pattern: class with methods, `db: Session` parameter, logging, singleton export
- Assignment repository correctly creates, queries by case/specialist, updates status (with responded_at), and updates fees
- Deliverable repository correctly creates, queries by case, partially updates, and transitions status (with completed_at on completion)
- Message repository correctly creates messages and filters internal messages via `include_internal` parameter
- Analytics repository returns correct aggregated dicts for cases by status/domain, revenue pipeline, specialist rankings, and average case duration
- `apps/Server/src/repository/__init__.py` exports all four new singletons
- All unit tests pass (`python -m pytest tests/`)
- No regressions in existing test suite
- No frontend type or build regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/ -v` — Run all Server tests to validate new repository tests pass and no regressions
- `cd apps/Server && python -c "from src.repository import ld_assignment_repository, ld_deliverable_repository, ld_message_repository, ld_analytics_repository; print('All repositories imported successfully')"` — Verify repository module exports work
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate no frontend regressions
- `cd apps/Client && npm run build` — Run Client build to validate no frontend regressions

## Notes
- This issue runs in parallel with LD-006 (Core Repositories: Client, Specialist, Case). Both contribute to Wave 2 (Backend Data Access).
- No new libraries are needed — all functionality uses SQLAlchemy core (already in requirements.txt).
- The Analytics repository uses `sqlalchemy.func` for aggregations — no raw SQL strings.
- The `fee_type` parameter in `update_fees` maps to the `fee_currency` column on LdCaseSpecialist model.
- Status transition validation (e.g., preventing invalid deliverable transitions) is intentionally left to the service layer (Wave 3). Repositories just persist the data.
- The `avg_case_duration` method uses `updated_at` (set on status change to completed) minus `created_at` since the ORM model does not have a dedicated `completed_at` column on LdCase. Alternatively, filter by status="completed" and compute from timestamps.
