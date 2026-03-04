# Legal Desk Core Repositories (Case, Specialist, Client)

**ADW ID:** 444abca2
**Date:** 2026-03-04
**Specification:** specs/issue-143-adw-444abca2-sdlc_planner-core-repositories-case-specialist-client.md

## Overview

Implements three core repository classes (`LdCaseRepository`, `LdSpecialistRepository`, `LdClientRepository`) for the Legal Desk module. These repositories provide the data access layer (CRUD, filtering, aggregation) following the class-based singleton pattern, enabling Wave 3 business services to operate without raw SQL.

## What Was Built

- **LdClientRepository** — CRUD operations and case-insensitive name search for Legal Desk clients
- **LdSpecialistRepository** — CRUD, availability filtering (domain + jurisdiction joins), workload management, and score recalculation for specialists
- **LdCaseRepository** — CRUD, multi-field filtering via `CaseFilterDTO`, sequential case number generation (`LD-YYYYMM-NNNN`), status updates, and dashboard aggregation (`count_by_status`)
- **Unit tests** — Full test coverage for all three repositories using mocked database sessions

## Technical Implementation

### Files Modified

- `apps/Server/src/repository/ld_client_repository.py`: New file — `LdClientRepository` with `create`, `get_by_id`, `list_all`, `update`, `search_by_name` methods
- `apps/Server/src/repository/ld_specialist_repository.py`: New file — `LdSpecialistRepository` with `create`, `get_by_id`, `list_all`, `update`, `update_status`, `get_available`, `update_workload`, `update_overall_score` methods
- `apps/Server/src/repository/ld_case_repository.py`: New file — `LdCaseRepository` with `create`, `get_by_id`, `list_cases`, `update`, `update_status`, `generate_case_number`, `get_by_client`, `count_by_status` methods
- `apps/Server/tests/test_ld_client_repository.py`: New file — 6 unit tests covering all client repository methods
- `apps/Server/tests/test_ld_specialist_repository.py`: New file — 10 unit tests covering all specialist repository methods including edge cases
- `apps/Server/tests/test_ld_case_repository.py`: New file — 11 unit tests covering all case repository methods including edge cases

### Key Changes

- **Singleton pattern**: Each repository exports a module-level singleton instance (`ld_client_repository`, `ld_specialist_repository`, `ld_case_repository`) matching the established codebase pattern
- **Session-per-call**: All methods accept `db: Session` as their first parameter, consistent with the existing repository pattern (no session ownership)
- **Specialist availability**: `get_available()` joins `LdSpecialistExpertise` and optionally `LdSpecialistJurisdiction` tables, filtering by `is_active`, domain match, and `current_workload < max_concurrent_cases`
- **Case number generation**: `generate_case_number()` produces `LD-YYYYMM-NNNN` format by counting existing cases with matching prefix and incrementing
- **Score recalculation**: `update_overall_score()` uses `func.avg(LdSpecialistScore.overall_score)` with graceful fallback to `Decimal("0.00")` when no scores exist
- **CaseFilterDTO integration**: `list_cases()` dynamically applies filters for status, legal_domain, priority, client_id, and complexity; `case_type` filter is intentionally skipped as `LdCase` model has no `case_type` column
- **Status mapping**: Specialist `update_status()` maps string values ("active" → `True`, others → `False`) to the `is_active` boolean field

## How to Use

1. Import the singleton instance from the repository module:
   ```python
   from src.repository.ld_client_repository import ld_client_repository
   from src.repository.ld_specialist_repository import ld_specialist_repository
   from src.repository.ld_case_repository import ld_case_repository
   ```

2. Pass a database session to any repository method:
   ```python
   # Create a client
   client = ld_client_repository.create(db, {"name": "Acme Corp", "contact_email": "acme@example.com"})

   # Find available specialists for a domain
   specialists = ld_specialist_repository.get_available(db, domain="civil", jurisdiction="Mexico")

   # Generate a case number and create a case
   case_number = ld_case_repository.generate_case_number(db)
   case = ld_case_repository.create(db, {"case_number": case_number, "client_id": client.id, ...})

   # Dashboard aggregation
   status_counts = ld_case_repository.count_by_status(db)
   ```

3. These repositories are designed to be consumed by Wave 3 services (not directly by API routes).

## Configuration

No additional configuration required. All functionality uses SQLAlchemy (already installed). The repositories connect to the existing PostgreSQL database via the `Session` object provided by `src/config/database.py`.

## Testing

Run repository tests:
```bash
cd apps/Server
python -m pytest tests/test_ld_client_repository.py -v
python -m pytest tests/test_ld_specialist_repository.py -v
python -m pytest tests/test_ld_case_repository.py -v
```

Run all server tests to verify zero regressions:
```bash
cd apps/Server && python -m pytest tests/ -v
```

## Notes

- This is a backend-only feature (Wave 2 of 6) — no UI components or E2E tests
- The `CaseFilterDTO.case_type` filter is intentionally skipped because the `LdCase` ORM model does not have a `case_type` column
- The specialist `update_status` maps status strings to `is_active` boolean since `LdSpecialist` uses `is_active: bool`, not a `status: str` column
- All methods include `print()` INFO logging with `[RepositoryName]` prefix for agent observability
