# Feature: Legal Desk Core Services (Case, Client, Specialist)

## Metadata
issue_number: `145`
adw_id: `cb46b16c`
issue_json: `{"number":145,"title":"[Legal Desk] Wave 3: Core Services (Case, Client, Specialist)","body":"..."}`

## Feature Description
Implement three core business service classes for the Legal Desk module: **LdCaseService** (case lifecycle management with status transition validation), **LdClientService** (client CRUD + search), and **LdSpecialistService** (specialist CRUD with expertise/jurisdiction management and performance scoring). These services sit in the Clean Architecture `core/services/` layer, orchestrating repository calls and enforcing business rules. They are consumed by Wave 4 API routes.

## User Story
As a Legal Desk system administrator
I want core business logic services that manage cases, clients, and specialists with proper validation and state management
So that API routes can expose reliable, validated operations for case lifecycle, client management, and specialist assignment workflows

## Problem Statement
The Legal Desk module has completed its foundation layers (database schema, ORM models, DTOs/enums, repositories) but lacks the business logic layer. Without services, there is no enforcement of case status transition rules, no specialist scoring aggregation, and no orchestration layer for the API routes to consume.

## Solution Statement
Create three service files following the established project service patterns (class-based, repository-delegating, INFO-logged). The Case service enforces `CASE_STATUS_TRANSITIONS` validation. The Specialist service manages expertise/jurisdiction sub-entities and recalculates overall scores. The Client service provides standard CRUD with search. All services return ORM model objects (route layer handles DTO conversion).

## Relevant Files
Use these files to implement the feature:

**Documentation (read for context):**
- `app_docs/feature-444abca2-legaldesk-core-repositories.md` — Repository method signatures and usage patterns
- `app_docs/feature-601d0350-legaldesk-supporting-repositories-wave2.md` — Wave 2 repository methods (assignment, deliverable, message, analytics)
- `app_docs/feature-cbc09752-legaldesk-pydantic-dtos-enums.md` — DTO definitions and CASE_STATUS_TRANSITIONS map
- `app_docs/feature-40f52fef-legaldesk-sqlalchemy-orm-models.md` — ORM model relationships and columns

**Source dependencies (read to understand interfaces):**
- `apps/Server/src/interface/legaldesk_dto.py` — All DTOs, enums, and `CASE_STATUS_TRANSITIONS`
- `apps/Server/src/repository/ld_case_repository.py` — `LdCaseRepository` with `generate_case_number`, `update_status`, `list_cases`
- `apps/Server/src/repository/ld_client_repository.py` — `LdClientRepository` with `search_by_name`
- `apps/Server/src/repository/ld_specialist_repository.py` — `LdSpecialistRepository` with `update_overall_score`, `update_workload`
- `apps/Server/src/repository/ld_assignment_repository.py` — `LdAssignmentRepository` for case specialist queries
- `apps/Server/src/repository/ld_deliverable_repository.py` — `LdDeliverableRepository` for case deliverables
- `apps/Server/src/repository/ld_message_repository.py` — `LdMessageRepository` for case messages
- `apps/Server/src/models/ld_case.py` — `LdCase` model with relationships (specialists, deliverables, messages, documents, pricing_history, scores)
- `apps/Server/src/models/ld_specialist.py` — `LdSpecialist` model with relationships (expertise, jurisdictions, scores)
- `apps/Server/src/models/ld_specialist_expertise.py` — `LdSpecialistExpertise` model
- `apps/Server/src/models/ld_specialist_jurisdiction.py` — `LdSpecialistJurisdiction` model
- `apps/Server/src/models/ld_specialist_score.py` — `LdSpecialistScore` model
- `apps/Server/src/models/ld_client.py` — `LdClient` model

**Pattern reference (read to match service conventions):**
- `apps/Server/src/core/services/prospect_service.py` — Service pattern: class-based, docstrings, print logging, repository delegation, singleton export

**Existing tests (read to match test conventions):**
- `apps/Server/tests/test_ld_case_repository.py` — Repository test patterns for LD
- `apps/Server/tests/test_ld_specialist_repository.py` — Specialist test patterns
- `apps/Server/tests/test_ld_client_repository.py` — Client test patterns

### New Files
- `apps/Server/src/core/services/ld_case_service.py` — Case lifecycle service
- `apps/Server/src/core/services/ld_client_service.py` — Client CRUD service
- `apps/Server/src/core/services/ld_specialist_service.py` — Specialist management service
- `apps/Server/tests/test_ld_case_service.py` — Case service unit tests
- `apps/Server/tests/test_ld_client_service.py` — Client service unit tests
- `apps/Server/tests/test_ld_specialist_service.py` — Specialist service unit tests

## Implementation Plan
### Phase 1: Foundation
Read all dependency files (DTOs, repositories, models) to understand exact method signatures, return types, and field names. Understand `CASE_STATUS_TRANSITIONS` state machine. Review the prospect_service.py pattern for class structure, logging format, docstring style, and singleton export.

### Phase 2: Core Implementation
Create three service files in order of dependency:
1. **LdClientService** — Simplest, no dependencies on other LD services. Standard CRUD + search.
2. **LdSpecialistService** — Manages sub-entities (expertise, jurisdictions) and score recalculation. Uses specialist repository + direct ORM for sub-entity creation.
3. **LdCaseService** — Most complex. Uses case repository for CRUD, validates status transitions against `CASE_STATUS_TRANSITIONS`, assembles detail views by loading related entities via ORM relationships.

### Phase 3: Integration
Write comprehensive unit tests for each service, mocking repository calls. Validate all test pass. Ensure existing tests still pass (zero regressions).

## Step by Step Tasks

### Step 1: Read dependency files
- Read `apps/Server/src/interface/legaldesk_dto.py` to understand all DTOs and `CASE_STATUS_TRANSITIONS`
- Read `apps/Server/src/repository/ld_case_repository.py`, `ld_client_repository.py`, `ld_specialist_repository.py` to understand repository method signatures
- Read `apps/Server/src/core/services/prospect_service.py` (full file) to understand exact service patterns
- Read `apps/Server/src/models/ld_case.py`, `ld_specialist.py`, `ld_specialist_expertise.py`, `ld_specialist_jurisdiction.py`, `ld_specialist_score.py` to understand ORM relationships

### Step 2: Create LdClientService
- Create `apps/Server/src/core/services/ld_client_service.py`
- Class `LdClientService` with methods:
  - `create(self, db: Session, data: ClientCreateDTO) -> LdClient` — Delegates to `ld_client_repository.create(db, data.model_dump())`
  - `update(self, db: Session, client_id: int, data: ClientUpdateDTO) -> Optional[LdClient]` — Gets client first (404 guard), then delegates `ld_client_repository.update(db, client_id, data.model_dump(exclude_unset=True))`
  - `get(self, db: Session, client_id: int) -> Optional[LdClient]` — Delegates to `ld_client_repository.get_by_id(db, client_id)`
  - `list_all(self, db: Session) -> list[LdClient]` — Delegates to `ld_client_repository.list_all(db)`
  - `search(self, db: Session, query: str) -> list[LdClient]` — Delegates to `ld_client_repository.search_by_name(db, query)`
- INFO-level print logging on every method entry and result
- Module-level singleton: `ld_client_service = LdClientService()`

### Step 3: Create LdSpecialistService
- Create `apps/Server/src/core/services/ld_specialist_service.py`
- Class `LdSpecialistService` with methods:
  - `create(self, db: Session, data: SpecialistCreateDTO) -> LdSpecialist` — Creates specialist via repository, then creates expertise and jurisdiction sub-entities from `data.expertise[]` and `data.jurisdictions[]` using direct ORM (db.add + db.flush)
  - `update(self, db: Session, specialist_id: int, data: SpecialistUpdateDTO) -> Optional[LdSpecialist]` — Gets specialist first, then delegates update with `data.model_dump(exclude_unset=True)`
  - `get_specialist_detail(self, db: Session, specialist_id: int) -> Optional[LdSpecialist]` — Gets specialist by ID; the ORM relationships on LdSpecialist already eager-load expertise[], jurisdictions[], scores[]
  - `list_all(self, db: Session, filters: Optional[dict] = None) -> list[LdSpecialist]` — Delegates to `ld_specialist_repository.list_all(db, filters)`
  - `add_expertise(self, db: Session, specialist_id: int, domain: str, proficiency: str) -> LdSpecialistExpertise` — Creates `LdSpecialistExpertise` record directly via ORM
  - `add_jurisdiction(self, db: Session, specialist_id: int, country: str, region: Optional[str], is_primary: bool) -> LdSpecialistJurisdiction` — Creates `LdSpecialistJurisdiction` record directly via ORM
  - `submit_score(self, db: Session, specialist_id: int, case_id: int, scores: ScoreSubmitDTO) -> LdSpecialistScore` — Creates `LdSpecialistScore` record, calculates `overall_score` as average of the four score fields, then calls `ld_specialist_repository.update_overall_score(db, specialist_id)` to recalculate the specialist's aggregate score
- Module-level singleton: `ld_specialist_service = LdSpecialistService()`

### Step 4: Create LdCaseService
- Create `apps/Server/src/core/services/ld_case_service.py`
- Class `LdCaseService` with methods:
  - `create_case(self, db: Session, data: CaseCreateDTO, current_user: dict) -> LdCase` — Generates case_number via `ld_case_repository.generate_case_number(db)`, creates case with all fields from DTO plus generated case_number and default status "new"
  - `update_case(self, db: Session, case_id: int, data: CaseUpdateDTO) -> Optional[LdCase]` — Gets case first (404 guard), delegates to `ld_case_repository.update(db, case_id, data.model_dump(exclude_unset=True))`
  - `update_case_status(self, db: Session, case_id: int, new_status: str) -> Optional[LdCase]` — Gets case, validates current_status → new_status against `CASE_STATUS_TRANSITIONS`, raises `ValueError` if invalid transition, delegates to `ld_case_repository.update_status(db, case_id, new_status)`
  - `get_case_with_details(self, db: Session, case_id: int) -> Optional[LdCase]` — Gets case by ID; ORM relationships provide specialists, deliverables, messages, documents, pricing_history. Also loads client via `ld_client_repository.get_by_id(db, case.client_id)` for the `CaseDetailDTO` assembly (done by route layer)
  - `list_cases(self, db: Session, filters: CaseFilterDTO) -> list[LdCase]` — Delegates to `ld_case_repository.list_cases(db, filters)`
- Module-level singleton: `ld_case_service = LdCaseService()`

### Step 5: Create unit tests for LdClientService
- Create `apps/Server/tests/test_ld_client_service.py`
- Test class `TestLdClientService` with tests:
  - `test_create_client` — Mock repository.create, verify delegation
  - `test_update_client_success` — Mock get_by_id returns client, mock update
  - `test_update_client_not_found` — Mock get_by_id returns None, verify returns None
  - `test_get_client` — Mock get_by_id
  - `test_list_all` — Mock list_all
  - `test_search` — Mock search_by_name
- Use `unittest.mock.patch` or `MagicMock` for repository mocking
- Follow existing test patterns from `test_ld_client_repository.py`

### Step 6: Create unit tests for LdSpecialistService
- Create `apps/Server/tests/test_ld_specialist_service.py`
- Test class `TestLdSpecialistService` with tests:
  - `test_create_specialist_with_expertise_and_jurisdictions` — Verify sub-entities created
  - `test_update_specialist_success`
  - `test_update_specialist_not_found`
  - `test_get_specialist_detail` — Verify relationships loaded
  - `test_list_all_with_filters`
  - `test_add_expertise` — Verify LdSpecialistExpertise created
  - `test_add_jurisdiction` — Verify LdSpecialistJurisdiction created
  - `test_submit_score` — Verify score created, overall calculated as average, repository update_overall_score called

### Step 7: Create unit tests for LdCaseService
- Create `apps/Server/tests/test_ld_case_service.py`
- Test class `TestLdCaseService` with tests:
  - `test_create_case` — Verify case_number generated, case created with default status
  - `test_update_case_success`
  - `test_update_case_not_found`
  - `test_update_case_status_valid_transition` — e.g., "new" → "classifying" (valid per CASE_STATUS_TRANSITIONS)
  - `test_update_case_status_invalid_transition` — e.g., "closed" → "active" (invalid), verify ValueError raised
  - `test_update_case_status_archived_no_transitions` — "archived" has no valid transitions
  - `test_get_case_with_details` — Verify case returned with relationships
  - `test_list_cases` — Verify filter delegation

### Step 8: Run validation commands
- Run `cd apps/Server && python -m pytest tests/ -v` to validate all tests pass
- Run `cd apps/Server && python -m pytest tests/test_ld_case_service.py tests/test_ld_client_service.py tests/test_ld_specialist_service.py -v` to validate new tests specifically

## Testing Strategy
### Unit Tests
- **LdClientService**: 6 tests covering CRUD + search, including not-found handling
- **LdSpecialistService**: 8 tests covering CRUD, sub-entity management (expertise, jurisdiction), and score submission with average calculation
- **LdCaseService**: 8 tests covering CRUD, status transition validation (valid + invalid + edge cases), and detail assembly

All tests mock repository dependencies using `unittest.mock.patch` to isolate service logic.

### Edge Cases
- **Invalid status transitions**: Verify `update_case_status` raises `ValueError` for transitions not in `CASE_STATUS_TRANSITIONS` (e.g., "archived" → anything, "closed" → "active")
- **Update non-existent entity**: All update methods return `None` when entity not found
- **Score calculation**: `submit_score` correctly averages four score fields (quality, teamwork, delivery, satisfaction)
- **Specialist creation with empty expertise/jurisdictions**: Should create specialist without sub-entities
- **Case creation generates unique case_number**: Verify `generate_case_number` is called and result is used
- **CaseFilterDTO with no filters set**: Should return all cases
- **Client search with empty query**: Should return empty list or all (depends on repository behavior)

## Acceptance Criteria
- Three new service files created: `ld_case_service.py`, `ld_client_service.py`, `ld_specialist_service.py`
- Each service follows the established class-based pattern with singleton export
- All methods have type hints, docstrings, and INFO-level print logging
- `update_case_status` validates transitions against `CASE_STATUS_TRANSITIONS` and raises `ValueError` for invalid transitions
- `submit_score` calculates `overall_score` as the average of quality, teamwork, delivery, and satisfaction scores
- All new unit tests pass (22+ tests across 3 test files)
- All existing tests continue to pass (zero regressions)
- No `any` types used in Python code
- Clean Architecture maintained: services only call repositories, never direct DB queries (except for sub-entity creation on specialist where no dedicated repository exists)

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/test_ld_case_service.py tests/test_ld_client_service.py tests/test_ld_specialist_service.py -v` — Run new service tests
- `cd apps/Server && python -m pytest tests/ -v` — Run ALL Server tests to validate zero regressions

## Notes
- This issue runs in parallel with LD-009, LD-010, LD-011 (other Wave 3 services: assignment, analytics, classification). No cross-dependencies between parallel issues.
- Wave 4 (API routes) will consume these services. The route layer handles DTO conversion via `SomeResponseDTO.model_validate(orm_object)`.
- The services return ORM model objects, not DTOs. This follows the established project pattern where the route layer converts to DTOs.
- For specialist sub-entity creation (expertise, jurisdictions), direct ORM is used since there are no dedicated repositories for these tables. This is acceptable as the operations are simple inserts.
- No new libraries required.
