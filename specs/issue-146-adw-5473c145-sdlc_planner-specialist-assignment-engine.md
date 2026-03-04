# Feature: Specialist Assignment Engine

## Metadata
issue_number: `146`
adw_id: `5473c145`
issue_json: ``

## Feature Description
Implement the intelligent specialist assignment engine — the core differentiator of the Legal Desk system. The service performs multi-stage filtering (domain match, jurisdiction coverage, availability) then scores candidates on a 0-100 scale across 5 weighted factors (expertise proficiency, overall score, workload availability, jurisdiction match, years experience). Returns top 5 ranked candidates with match scores and detailed reasoning. Also handles specialist assignment lifecycle (create assignment, update status, query assignments) with proper workload management (increment on assign, decrement on completion/rejection).

This is Wave 3 of 6 — Backend Business Logic. It depends on Wave 2 repositories (LD-004 DTOs, LD-006 Case/Specialist repos, LD-007 Assignment repo) which are already implemented.

## User Story
As a legal desk operator
I want to receive intelligent specialist suggestions ranked by match quality for each case
So that I can quickly assign the best-fit specialist based on expertise, availability, jurisdiction, and track record

## Problem Statement
When a new legal case arrives, operators must manually search through specialists to find qualified matches. This is time-consuming and error-prone — operators may overlook better-qualified specialists or assign overloaded ones. There is no systematic scoring to compare candidates objectively.

## Solution Statement
Create `LdAssignmentService` that orchestrates the existing repositories (`ld_case_repository`, `ld_specialist_repository`, `ld_assignment_repository`) to:
1. Filter specialists through mandatory (domain), jurisdiction, and availability criteria
2. Score remaining candidates on a 0-100 scale across 5 weighted factors
3. Return the top 5 candidates with normalized scores (0-1) and human-readable match reasons
4. Manage the assignment lifecycle (create, update status, query) with automatic workload tracking

## Relevant Files
Use these files to implement the feature:

- `apps/Server/src/interface/legaldesk_dto.py` — Contains `SpecialistCandidateDTO`, `SuggestionResponseDTO`, `AssignmentCreateDTO`, `AssignmentResponseDTO`, and all enums. Needs `match_reasons` field added to `SpecialistCandidateDTO`.
- `apps/Server/src/repository/ld_case_repository.py` — `get_by_id(db, case_id)` to fetch case details (legal_domain, client_id)
- `apps/Server/src/repository/ld_specialist_repository.py` — `get_available(db, domain, jurisdiction)` for filtered candidates, `update_workload(db, id, delta)` for workload management, `get_by_id(db, id)` for validation
- `apps/Server/src/repository/ld_assignment_repository.py` — `create_assignment(db, data)`, `update_assignment_status(db, id, status)`, `get_case_specialists(db, case_id)` for assignment CRUD
- `apps/Server/src/repository/ld_client_repository.py` — `get_by_id(db, client_id)` to resolve case jurisdiction from client country
- `apps/Server/src/models/ld_specialist.py` — `LdSpecialist` ORM model with `expertise`, `jurisdictions` relationships for scoring access
- `apps/Server/src/models/ld_case.py` — `LdCase` ORM model (no jurisdiction field — derive from client.country)
- `apps/Server/src/models/ld_specialist_expertise.py` — `LdSpecialistExpertise` with `proficiency_level`, `legal_domain`, `years_in_domain`
- `apps/Server/src/models/ld_specialist_jurisdiction.py` — `LdSpecialistJurisdiction` with `country`, `region`, `is_primary`
- `apps/Server/src/models/ld_case_specialist.py` — `LdCaseSpecialist` ORM model for assignments
- `apps/Server/src/core/services/__init__.py` — Register the new service singleton export
- `apps/Server/tests/test_ld_assignment_repository.py` — Reference for test patterns (mock-based, class-per-method, fixtures)
- `app_docs/feature-de0cefbe-legaldesk-database-schema.md` — Legal Desk database tables reference
- `app_docs/feature-40f52fef-legaldesk-sqlalchemy-orm-models.md` — ORM models reference
- `app_docs/feature-cbc09752-legaldesk-pydantic-dtos-enums.md` — DTOs and enums reference
- `app_docs/feature-444abca2-legaldesk-core-repositories.md` — Core repositories reference
- `app_docs/feature-601d0350-legaldesk-supporting-repositories-wave2.md` — Assignment repository reference

### New Files
- `apps/Server/src/core/services/ld_assignment_service.py` — The specialist assignment engine service
- `apps/Server/tests/test_ld_assignment_service.py` — Unit tests for the assignment service

## Implementation Plan
### Phase 1: Foundation — DTO Enhancement
Add the `match_reasons` field to `SpecialistCandidateDTO` in `legaldesk_dto.py`. The existing DTO is missing this field which the scoring engine needs to explain score components. This is a non-breaking additive change (default empty list).

### Phase 2: Core Implementation — Assignment Service
Create `ld_assignment_service.py` with 4 public methods:
1. `suggest_specialists(db, case_id)` — The scoring engine: fetch case → get client for jurisdiction → call `get_available` → score each candidate → rank → return top 5
2. `assign_specialist(db, data: AssignmentCreateDTO)` — Create assignment + increment workload
3. `update_assignment_status(db, assignment_id, status)` — Update status + decrement workload on completion/rejection
4. `get_case_specialists(db, case_id)` — Delegate to assignment repository

The private `_calculate_match_score(specialist, case, expertise, client_country)` method computes the 0-100 score across 5 weighted factors:
- Expertise proficiency (30 pts): expert=30, intermediate=20, junior=10
- Overall score (25 pts): `(specialist.overall_score / 5.0) * 25`
- Workload availability (20 pts): `((max - current) / max) * 20`
- Jurisdiction match (15 pts): country+full-coverage=15, country+region-only=10, no jurisdiction=15
- Years experience (10 pts): `min(years / 20 * 10, 10)`

The 0-100 internal score is normalized to 0-1 (`score / 100`) for the `SpecialistCandidateDTO.match_score` field which has `ge=0, le=1` validation.

**Jurisdiction design decision**: The `LdCase` model has no jurisdiction field. Jurisdiction is derived from the case's client country (`ld_client_repository.get_by_id(db, case.client_id).country`). If client country is None, the case is treated as having no jurisdiction (full 15 pts awarded).

### Phase 3: Integration — Service Registration
Export the service singleton from `src/core/services/__init__.py` so it's available for future Wave 4 API routes.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add `match_reasons` field to `SpecialistCandidateDTO`
- Open `apps/Server/src/interface/legaldesk_dto.py`
- Add `match_reasons: List[str] = Field(default_factory=list, description="Detailed scoring reasons")` to `SpecialistCandidateDTO` after the `jurisdiction_match` field
- This is a non-breaking change — the default empty list ensures backward compatibility

### Step 2: Create the Assignment Service
- Create `apps/Server/src/core/services/ld_assignment_service.py`
- Import repository singletons: `ld_case_repository`, `ld_specialist_repository`, `ld_assignment_repository`, `ld_client_repository`
- Import DTOs: `SpecialistCandidateDTO`, `SuggestionResponseDTO`, `AssignmentCreateDTO`, `AssignmentResponseDTO`
- Implement `LdAssignmentService` class with all 4 public methods and the private scoring method
- Create module-level singleton: `ld_assignment_service = LdAssignmentService()`

#### `suggest_specialists(self, db: Session, case_id: int) -> SuggestionResponseDTO`
1. Fetch case via `ld_case_repository.get_by_id(db, case_id)` — raise `ValueError("Case not found")` if None
2. Fetch client via `ld_client_repository.get_by_id(db, case.client_id)` to get `client.country` as jurisdiction
3. Call `ld_specialist_repository.get_available(db, case.legal_domain, client.country if client else None)` to get filtered candidates
4. For each candidate:
   - Find matching expertise record from `specialist.expertise` where `e.legal_domain == case.legal_domain`
   - If no matching expertise found (shouldn't happen due to `get_available` filter), skip
   - Call `_calculate_match_score(specialist, case, expertise, client.country if client else None)`
   - Build `SpecialistCandidateDTO` with score normalized to 0-1 (`Decimal(str(round(score / 100, 4)))`)
5. Sort candidates by `match_score` descending, return top 5
6. Return `SuggestionResponseDTO(case_id=case_id, legal_domain=case.legal_domain, candidates=top_5, generated_at=datetime.utcnow())`

#### `_calculate_match_score(self, specialist, case, expertise, client_country) -> tuple[float, list[str]]`
Implement the 5-factor scoring exactly as specified in the issue:
- **Expertise proficiency (30 pts)**: Map proficiency_level → {"expert": 30, "intermediate": 20, "junior": 10}
- **Overall score (25 pts)**: `(float(specialist.overall_score) / 5.0) * 25`
- **Workload availability (20 pts)**: `((specialist.max_concurrent_cases - specialist.current_workload) / specialist.max_concurrent_cases) * 20`
- **Jurisdiction match (15 pts)**:
  - If `client_country` is None → 15 pts (full points, "No jurisdiction requirement")
  - Else iterate `specialist.jurisdictions`, find entries matching `client_country`:
    - If match found with `region is None` (covers whole country) → 15 pts ("Full jurisdiction coverage")
    - If match found with `region is not None` (covers specific region only) → 10 pts ("Regional jurisdiction coverage")
    - Note: The mandatory jurisdiction filter in `get_available` already ensures country match, so this branch always finds a match when client_country is set
- **Years experience (10 pts)**: `min(specialist.years_experience / 20 * 10, 10)`
- Build `reasons: list[str]` with human-readable explanations for each component
- Return `(score, reasons)`

#### `assign_specialist(self, db: Session, data: AssignmentCreateDTO) -> LdCaseSpecialist`
1. Validate case exists via `ld_case_repository.get_by_id`
2. Validate specialist exists via `ld_specialist_repository.get_by_id`
3. Create assignment via `ld_assignment_repository.create_assignment(db, {...})` with fields from DTO
4. Increment workload via `ld_specialist_repository.update_workload(db, data.specialist_id, 1)`
5. Return the created assignment

#### `update_assignment_status(self, db: Session, assignment_id: int, status: str) -> LdCaseSpecialist`
1. Update via `ld_assignment_repository.update_assignment_status(db, assignment_id, status)`
2. Raise `ValueError("Assignment not found")` if None returned
3. If status is `"completed"` or `"rejected"`, decrement workload via `ld_specialist_repository.update_workload(db, assignment.specialist_id, -1)`
4. Return updated assignment

#### `get_case_specialists(self, db: Session, case_id: int) -> list[LdCaseSpecialist]`
1. Delegate to `ld_assignment_repository.get_case_specialists(db, case_id)`

### Step 3: Register Service in `__init__.py`
- Add to `apps/Server/src/core/services/__init__.py`:
  ```python
  from src.core.services.ld_assignment_service import ld_assignment_service
  ```
- Add `"ld_assignment_service"` to `__all__`

### Step 4: Create Unit Tests
- Create `apps/Server/tests/test_ld_assignment_service.py`
- Follow the established mock-based test pattern from existing test files
- Use fixtures: `service` (fresh `LdAssignmentService()`), `mock_db` (MagicMock)
- Mock repository singletons using `@patch`

#### Test Classes:

**`TestSuggestSpecialists`:**
- `test_suggest_specialists_case_not_found` — raises ValueError when case doesn't exist
- `test_suggest_specialists_no_candidates` — returns empty candidates list when no specialists available
- `test_suggest_specialists_returns_ranked_candidates` — verify candidates sorted by match_score descending
- `test_suggest_specialists_limits_to_top_5` — verify only top 5 returned when more candidates exist
- `test_suggest_specialists_no_jurisdiction_gives_full_points` — verify 15 pts when client has no country
- `test_suggest_specialists_score_normalized_to_0_1` — verify match_score between 0 and 1

**`TestCalculateMatchScore`:**
- `test_expert_proficiency_scores_30` — expert level scores 30 pts
- `test_intermediate_proficiency_scores_20` — intermediate scores 20 pts
- `test_junior_proficiency_scores_10` — junior scores 10 pts
- `test_overall_score_calculation` — verify `(overall_score / 5.0) * 25` formula
- `test_workload_availability_calculation` — verify `((max - current) / max) * 20` formula
- `test_jurisdiction_no_requirement_gives_15` — no client_country → 15 pts
- `test_jurisdiction_full_coverage_gives_15` — country match with region=None → 15 pts
- `test_jurisdiction_regional_only_gives_10` — country match with region set → 10 pts
- `test_years_experience_capped_at_10` — 30 years experience caps at 10 pts
- `test_max_score_is_100` — perfect candidate scores 100
- `test_reasons_list_has_5_entries` — verify all 5 scoring factors produce reasons

**`TestAssignSpecialist`:**
- `test_assign_specialist_case_not_found` — raises ValueError
- `test_assign_specialist_specialist_not_found` — raises ValueError
- `test_assign_specialist_creates_and_increments_workload` — verify assignment created and workload +1
- `test_assign_specialist_passes_correct_data` — verify DTO fields passed to repository

**`TestUpdateAssignmentStatus`:**
- `test_update_status_not_found` — raises ValueError
- `test_update_status_completed_decrements_workload` — verify workload -1 on "completed"
- `test_update_status_rejected_decrements_workload` — verify workload -1 on "rejected"
- `test_update_status_active_no_workload_change` — verify no workload change on "active"

**`TestGetCaseSpecialists`:**
- `test_get_case_specialists_delegates_to_repository` — verify pass-through delegation

### Step 5: Run Validation Commands
- Run all validation commands listed below to ensure zero regressions

## Testing Strategy
### Unit Tests
- All tests use mock-based approach (no database required) following existing patterns
- Repository singletons patched with `@patch` decorator
- Mock specialists with realistic attribute values (expertise list, jurisdiction list, scores)
- Each test class covers one public method, each test method covers one scenario
- Verify both return values and side effects (repository calls, workload updates)

### Edge Cases
- Case not found (ValueError)
- Specialist not found during assignment (ValueError)
- Assignment not found during status update (ValueError)
- No available specialists for domain (empty candidates list)
- Client has no country (no jurisdiction filtering, full jurisdiction points)
- Specialist with 0 overall_score (0 points for that factor)
- Specialist at max workload (excluded by `get_available` filter)
- Years experience > 20 (capped at 10 pts)
- Years experience = 0 (0 pts)
- Specialist with multiple expertise entries (only matching domain used)
- Specialist with multiple jurisdiction entries (best match used for scoring)
- More than 5 candidates (truncated to top 5)
- Exactly 5 candidates (all returned)
- Fewer than 5 candidates (all returned)
- Workload decrement on "completed" status
- Workload decrement on "rejected" status
- No workload change on "active" or "accepted" status
- Division by zero protection if max_concurrent_cases somehow is 0 (defensive check)

## Acceptance Criteria
1. `suggest_specialists(db, case_id)` returns `SuggestionResponseDTO` with up to 5 candidates ranked by match_score descending
2. Scoring weights sum to 100: expertise_proficiency(30) + overall_score(25) + workload_availability(20) + jurisdiction_match(15) + years_experience(10) = 100
3. Each candidate includes `match_reasons: list[str]` with human-readable explanations for all 5 scoring factors
4. `match_score` in DTO is normalized to 0-1 range (Decimal, ge=0, le=1)
5. Mandatory filter: only specialists with matching `legal_domain` expertise are included
6. Jurisdiction filter: if case has jurisdiction (client country), only specialists covering that country are included
7. Availability filter: only active specialists with `current_workload < max_concurrent_cases` are included
8. `assign_specialist` creates assignment record AND increments specialist workload by 1
9. `update_assignment_status` updates status AND decrements workload by 1 when status is "completed" or "rejected"
10. `get_case_specialists` returns all assignments for a case
11. All methods raise `ValueError` with descriptive message when required entities not found
12. All operations produce `print()` log output following `INFO [LdAssignmentService]` / `ERROR [LdAssignmentService]` pattern
13. All unit tests pass with `pytest`

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/test_ld_assignment_service.py -v` — Run new service unit tests
- `cd apps/Server && python -m pytest tests/ -v` — Run all Server tests to validate zero regressions
- `cd apps/Server && python -c "from src.core.services.ld_assignment_service import ld_assignment_service; print('Service import OK')"` — Verify service imports cleanly
- `cd apps/Server && python -c "from src.core.services import ld_assignment_service; print('Init export OK')"` — Verify __init__.py export
- `cd apps/Server && python -c "from src.interface.legaldesk_dto import SpecialistCandidateDTO; assert 'match_reasons' in SpecialistCandidateDTO.model_fields; print('DTO field OK')"` — Verify DTO enhancement

## Notes
- **Jurisdiction derivation**: The `LdCase` model has no jurisdiction field. Jurisdiction is derived from `client.country` via `ld_client_repository.get_by_id(db, case.client_id)`. This is a pragmatic decision that matches real-world patterns where case jurisdiction follows client location.
- **Score normalization**: The internal scoring uses a 0-100 scale for clarity and alignment with the issue spec. The output `match_score` is normalized to 0-1 (`score / 100`) to match the existing `SpecialistCandidateDTO` validation constraint (`ge=0, le=1`).
- **Jurisdiction scoring detail**: Since the case/client model only has `country` (no `region`), jurisdiction scoring distinguishes between specialists who cover the entire country (region=None → 15 pts) vs those who cover only a specific region (region=<value> → 10 pts).
- **Repository reuse**: The service leverages `ld_specialist_repository.get_available()` which already handles the 3-stage mandatory filtering (domain match, active status, workload capacity). The service adds scoring and ranking on top.
- **No new dependencies**: This feature uses only existing libraries (Pydantic, SQLAlchemy, standard library). No `uv add` needed.
- **Wave 4 readiness**: The service singleton is exported from `__init__.py`, ready for Wave 4 API routes to expose `GET /cases/{id}/specialists/suggest`.
