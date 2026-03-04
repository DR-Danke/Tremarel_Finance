# Feature: Legal Desk Core Repositories (Case, Specialist, Client)

## Metadata
issue_number: `143`
adw_id: `444abca2`
issue_json: `{"number":143,"title":"[Legal Desk] Wave 2: Core Repositories (Case, Specialist, Client)"}`

## Feature Description
Implement three core repository classes for the Legal Desk module: `LdCaseRepository`, `LdSpecialistRepository`, and `LdClientRepository`. These repositories provide the data access layer (CRUD operations, filtering, aggregation) for cases, specialists, and clients. They follow the existing class-based singleton pattern used throughout the codebase (e.g., `restaurant_repository.py`, `prospect_repository.py`) and receive `db: Session` as a parameter for all methods. This is Wave 2 of 6 (Backend Data Access) and depends on LD-003 (ORM models) and LD-004 (DTOs) which are already implemented.

## User Story
As a Legal Desk system developer
I want data access repositories for cases, specialists, and clients
So that Wave 3 business services can perform CRUD, filtering, and aggregation without writing raw SQL

## Problem Statement
The Legal Desk module has ORM models and DTOs in place but no data access layer. Without repositories, services cannot create, read, update, or query cases, specialists, or clients. This blocks all downstream service and API development.

## Solution Statement
Create three repository files following the established singleton class pattern. Each repository provides typed methods for CRUD, filtering, and domain-specific operations (case number generation, specialist availability filtering, client name search). All methods accept `db: Session` as their first parameter and include `print()` logging for observability.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/src/config/database.py` — Database session factory and `get_db()` dependency; provides `Session` type and `Base`
- `apps/Server/src/models/ld_case.py` — `LdCase` ORM model with relationships (specialists, deliverables, messages, documents, pricing_history, scores)
- `apps/Server/src/models/ld_specialist.py` — `LdSpecialist` ORM model with relationships (expertise, jurisdictions, case_assignments, scores)
- `apps/Server/src/models/ld_client.py` — `LdClient` ORM model with `cases` relationship
- `apps/Server/src/models/ld_specialist_expertise.py` — `LdSpecialistExpertise` junction table (specialist_id, legal_domain, proficiency_level)
- `apps/Server/src/models/ld_specialist_jurisdiction.py` — `LdSpecialistJurisdiction` junction table (specialist_id, country, region, is_primary)
- `apps/Server/src/models/ld_specialist_score.py` — `LdSpecialistScore` model (quality, teamwork, delivery, satisfaction scores)
- `apps/Server/src/interface/legaldesk_dto.py` — All Legal Desk DTOs including `CaseFilterDTO`, `SpecialistFilterDTO`, enums (`CaseStatus`, `LegalDomain`, `CasePriority`, `CaseType`, `CaseComplexity`)
- `apps/Server/src/repository/restaurant_repository.py` — Reference pattern for class-based singleton repository with CRUD operations
- `apps/Server/src/repository/prospect_repository.py` — Reference pattern for advanced filtering, pagination, and counting
- `apps/Server/tests/test_legaldesk_dto.py` — Existing DTO tests; test pattern reference
- `app_docs/feature-40f52fef-legaldesk-sqlalchemy-orm-models.md` — ORM model documentation (read for relationship details)
- `app_docs/feature-cbc09752-legaldesk-pydantic-dtos-enums.md` — DTO documentation (read for validation rules)
- `app_docs/feature-de0cefbe-legaldesk-database-schema.md` — Database schema documentation (read for table structure)

### New Files
- `apps/Server/src/repository/ld_case_repository.py` — Case repository with CRUD, filtering, status updates, case number generation, dashboard aggregation
- `apps/Server/src/repository/ld_specialist_repository.py` — Specialist repository with CRUD, availability filtering, workload management, score recalculation
- `apps/Server/src/repository/ld_client_repository.py` — Client repository with CRUD and name search
- `apps/Server/tests/test_ld_case_repository.py` — Unit tests for case repository
- `apps/Server/tests/test_ld_specialist_repository.py` — Unit tests for specialist repository
- `apps/Server/tests/test_ld_client_repository.py` — Unit tests for client repository

## Implementation Plan
### Phase 1: Foundation
Read the conditional documentation files (`app_docs/feature-40f52fef-*`, `app_docs/feature-cbc09752-*`, `app_docs/feature-de0cefbe-*`) and the reference repositories (`restaurant_repository.py`, `prospect_repository.py`) to fully understand patterns, ORM relationships, and DTO structures before writing any code.

### Phase 2: Core Implementation
Implement the three repositories in order of dependency:
1. **Client Repository** (simplest, no dependencies on other LD repos) — CRUD + name search
2. **Specialist Repository** (medium complexity) — CRUD + availability filtering via joins to expertise/jurisdiction tables + workload management + score recalculation via `func.avg`
3. **Case Repository** (most complex) — CRUD + multi-field filtering via `CaseFilterDTO` + sequential case number generation + status updates + dashboard aggregation via `func.count` + `group_by`

### Phase 3: Integration
Write unit tests for all three repositories using mocked database sessions. Validate that all methods are callable with correct signatures and that filtering/aggregation logic is correct. Run existing test suite to confirm zero regressions.

## Step by Step Tasks

### Step 1: Read Conditional Documentation
- Read `app_docs/feature-40f52fef-legaldesk-sqlalchemy-orm-models.md` for ORM model relationship details
- Read `app_docs/feature-cbc09752-legaldesk-pydantic-dtos-enums.md` for DTO validation rules
- Read `app_docs/feature-de0cefbe-legaldesk-database-schema.md` for table structure and constraints

### Step 2: Create Client Repository
- Create `apps/Server/src/repository/ld_client_repository.py`
- Implement `LdClientRepository` class with these methods:
  - `create(self, db: Session, data: dict) -> LdClient` — Create new client from dict, `db.add()`, `db.commit()`, `db.refresh()`
  - `get_by_id(self, db: Session, client_id: int) -> Optional[LdClient]` — Query by primary key using `.filter(LdClient.id == client_id).first()`
  - `list_all(self, db: Session) -> list[LdClient]` — Return all clients ordered by `created_at` desc
  - `update(self, db: Session, client_id: int, data: dict) -> LdClient` — Fetch by id, update fields from dict using `setattr()`, commit
  - `search_by_name(self, db: Session, query: str) -> list[LdClient]` — Use `LdClient.name.ilike(f"%{query}%")` for case-insensitive partial match
- Add `print()` INFO logging to every method following the `[LdClientRepository]` prefix pattern
- Export singleton: `ld_client_repository = LdClientRepository()`

### Step 3: Create Specialist Repository
- Create `apps/Server/src/repository/ld_specialist_repository.py`
- Implement `LdSpecialistRepository` class with these methods:
  - `create(self, db: Session, data: dict) -> LdSpecialist` — Create specialist from dict
  - `get_by_id(self, db: Session, specialist_id: int) -> Optional[LdSpecialist]` — Get specialist; SQLAlchemy lazy loading will include expertise and jurisdictions when accessed
  - `list_all(self, db: Session, filters: dict) -> list[LdSpecialist]` — Optional filters for `is_active`, `legal_domain` (join to expertise), `min_experience`, `max_workload`
  - `update(self, db: Session, specialist_id: int, data: dict) -> LdSpecialist` — Fetch and update fields
  - `update_status(self, db: Session, specialist_id: int, status: str) -> LdSpecialist` — Update `is_active` based on status string
  - `get_available(self, db: Session, domain: str, jurisdiction: Optional[str] = None) -> list[LdSpecialist]` — Join to `LdSpecialistExpertise` filtering `legal_domain == domain`, join to `LdSpecialistJurisdiction` if jurisdiction provided, filter `is_active == True` and `current_workload < max_concurrent_cases`
  - `update_workload(self, db: Session, specialist_id: int, delta: int) -> LdSpecialist` — Increment/decrement `current_workload` by delta value
  - `update_overall_score(self, db: Session, specialist_id: int) -> LdSpecialist` — Calculate `func.avg(LdSpecialistScore.overall_score)` for the specialist and update `LdSpecialist.overall_score`
- Import `LdSpecialistExpertise`, `LdSpecialistJurisdiction`, `LdSpecialistScore` for joins
- Use `sqlalchemy.func` for `avg` aggregation
- Export singleton: `ld_specialist_repository = LdSpecialistRepository()`

### Step 4: Create Case Repository
- Create `apps/Server/src/repository/ld_case_repository.py`
- Implement `LdCaseRepository` class with these methods:
  - `create(self, db: Session, case_data: dict) -> LdCase` — Create case from dict
  - `get_by_id(self, db: Session, case_id: int) -> Optional[LdCase]` — Get case; client relationship available via lazy loading
  - `list_cases(self, db: Session, filters: CaseFilterDTO, limit: int = 100, offset: int = 0) -> list[LdCase]` — Build dynamic query checking each `CaseFilterDTO` field (status, legal_domain, priority, case_type, client_id, complexity); apply `.offset(offset).limit(limit)`, order by `created_at` desc
  - `update(self, db: Session, case_id: int, data: dict) -> LdCase` — Fetch and update fields from dict
  - `update_status(self, db: Session, case_id: int, status: str) -> LdCase` — Update only the `status` field
  - `generate_case_number(self, db: Session) -> str` — Format `LD-YYYYMM-NNNN`: get current year-month, count existing cases with `case_number.like(f"LD-{year_month}-%")`, increment by 1, zero-pad to 4 digits
  - `get_by_client(self, db: Session, client_id: int) -> list[LdCase]` — Filter by `client_id`, order by `created_at` desc
  - `count_by_status(self, db: Session) -> dict` — Use `func.count()` with `group_by(LdCase.status)` to return `{status: count}` dictionary
- Import `CaseFilterDTO` from DTOs for type hints in `list_cases`
- Use `sqlalchemy.func` for `count` aggregation and `datetime` for case number generation
- Export singleton: `ld_case_repository = LdCaseRepository()`

### Step 5: Create Client Repository Tests
- Create `apps/Server/tests/test_ld_client_repository.py`
- Test all 5 methods using mocked `Session` (use `unittest.mock.MagicMock`)
- Test cases:
  - `test_create_client` — Verify `db.add()`, `db.commit()`, `db.refresh()` called
  - `test_get_by_id_found` — Mock query chain returning a client
  - `test_get_by_id_not_found` — Mock query chain returning None
  - `test_list_all` — Verify query returns list
  - `test_update_client` — Verify fields updated via setattr
  - `test_search_by_name` — Verify ilike filter applied

### Step 6: Create Specialist Repository Tests
- Create `apps/Server/tests/test_ld_specialist_repository.py`
- Test all 8 methods using mocked `Session`
- Test cases:
  - `test_create_specialist` — Verify create flow
  - `test_get_by_id` — Found and not-found scenarios
  - `test_list_all_no_filters` — No filters applied
  - `test_list_all_with_filters` — Filters correctly applied
  - `test_update_specialist` — Fields updated
  - `test_update_status` — is_active updated
  - `test_get_available` — Verify joins to expertise/jurisdiction and workload filter
  - `test_update_workload` — Increment and decrement
  - `test_update_overall_score` — Verify avg calculation query

### Step 7: Create Case Repository Tests
- Create `apps/Server/tests/test_ld_case_repository.py`
- Test all 8 methods using mocked `Session`
- Test cases:
  - `test_create_case` — Verify create flow
  - `test_get_by_id` — Found and not-found scenarios
  - `test_list_cases_no_filters` — Empty filter DTO
  - `test_list_cases_with_filters` — Each filter field applied
  - `test_update_case` — Fields updated
  - `test_update_status` — Status field updated
  - `test_generate_case_number_first_of_month` — Returns `LD-YYYYMM-0001`
  - `test_generate_case_number_sequential` — Returns `LD-YYYYMM-NNNN` with correct increment
  - `test_get_by_client` — Filter by client_id
  - `test_count_by_status` — Verify group_by aggregation returns dict

### Step 8: Run Validation Commands
- Run `cd apps/Server && python -m pytest tests/ -v` to validate all tests pass with zero regressions
- Run `cd apps/Client && npx tsc --noEmit` to validate frontend type check (no frontend changes, but confirm no regressions)
- Run `cd apps/Client && npm run build` to validate frontend build

## Testing Strategy
### Unit Tests
- All repository methods tested with mocked database sessions (`unittest.mock.MagicMock` for `Session`)
- Mock the SQLAlchemy query chain: `db.query().filter().first()`, `db.query().filter().all()`, etc.
- Verify correct ORM methods called (`db.add`, `db.commit`, `db.refresh`, `db.delete`)
- Verify return types match expected ORM model types
- Test `generate_case_number` with both empty month (first case) and existing cases (sequential)
- Test `get_available` with and without jurisdiction parameter
- Test `update_overall_score` with scores present and no scores (edge case)

### Edge Cases
- `get_by_id` returns `None` when record not found
- `search_by_name` with empty string returns all clients
- `generate_case_number` handles month rollover correctly (new month starts at 0001)
- `generate_case_number` handles concurrent calls (sequential within same month)
- `get_available` with no matching specialists returns empty list
- `update_workload` with negative delta (decrement when case completed)
- `update_overall_score` when specialist has no scores (should handle gracefully, set to 0.00)
- `list_cases` with all filter fields as `None` returns all cases (no filters applied)
- `count_by_status` with no cases returns empty dict

## Acceptance Criteria
- Three repository files created: `ld_case_repository.py`, `ld_specialist_repository.py`, `ld_client_repository.py`
- All repositories follow the class-based singleton pattern with `db: Session` parameter
- All methods have type hints, docstrings, and `print()` INFO logging
- Case number generation produces format `LD-YYYYMM-NNNN` (sequential within month)
- Specialist availability filtering correctly joins expertise + jurisdiction tables and checks workload
- Client name search uses case-insensitive `ILIKE` partial matching
- `count_by_status` returns a dictionary of `{status_string: count}`
- All unit tests pass
- Existing test suite passes with zero regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/test_ld_client_repository.py -v` — Run client repository tests
- `cd apps/Server && python -m pytest tests/test_ld_specialist_repository.py -v` — Run specialist repository tests
- `cd apps/Server && python -m pytest tests/test_ld_case_repository.py -v` — Run case repository tests
- `cd apps/Server && python -m pytest tests/ -v` — Run all Server tests to validate zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate zero regressions
- `cd apps/Client && npm run build` — Run Client build to validate zero regressions

## Notes
- This is a backend-only feature (no UI components), so no E2E tests are needed
- The repositories are designed to be consumed by Wave 3 services (not directly by routes)
- The `CaseFilterDTO` has a `case_type` field but the `LdCase` model does not have a `case_type` column — check the model and skip this filter if the column doesn't exist, or add the filter if the model has a matching field
- `LdCase` model does not have a `case_type` field based on the ORM model. The `CaseFilterDTO.case_type` filter should be skipped in `list_cases` or mapped to an appropriate field. During implementation, confirm the model structure and decide whether to omit this filter or map it
- The `update_status` method on the specialist repository should map status strings to `is_active` boolean (e.g., "active" → True, "inactive" → False) since `LdSpecialist` uses `is_active: bool` not a `status: str` column
- No new libraries required — all functionality uses SQLAlchemy (already installed)
