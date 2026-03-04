# Legal Desk Pydantic DTOs & Enums

**ADW ID:** cbc09752
**Date:** 2026-03-04
**Specification:** specs/issue-141-adw-cbc09752-sdlc_planner-legaldesk-pydantic-dtos-enums.md

## Overview

Comprehensive Pydantic DTO and enum definitions for the Faroo Legal Desk module. This Wave 1 (Foundation) issue provides 14 string enums, a case status transition map, and ~40 Pydantic v2 models covering CRUD operations, filtering, responses, and specialized DTOs for the assignment engine, AI classification, pricing negotiation, and analytics dashboard. All DTOs map to the `ld_*` database tables defined in the Legal Desk schema.

## What Was Built

- 14 string enums (`CaseStatus`, `CaseType`, `LegalDomain`, `CaseComplexity`, `CasePriority`, `OriginationChannel`, `SpecialistStatus`, `SpecialistType`, `ProficiencyLevel`, `AssignmentRole`, `AssignmentStatus`, `DeliverableStatus`, `PricingAction`, `ClientType`)
- `CASE_STATUS_TRANSITIONS` constant defining valid status transitions for all 11 case statuses
- ~40 Pydantic v2 DTOs organized by domain entity: Client, Specialist, Case, Assignment, Deliverable, Message, Document, Pricing, Scoring, Engine, Classification, Analytics
- Comprehensive test suite with 1286 lines covering all enums, DTOs, validation rules, and edge cases

## Technical Implementation

### Files Modified

- `apps/Server/src/interface/legaldesk_dto.py` (721 lines): All 14 enums, transition map, and ~40 Pydantic DTOs
- `apps/Server/tests/test_legaldesk_dto.py` (1286 lines): Comprehensive tests for all enums, DTOs, validation, and edge cases

### Key Changes

- All enums inherit from `(str, Enum)` with docstrings, matching the existing codebase pattern from `event_dto.py`
- All DTOs use Pydantic v2 `BaseModel` with `Field(...)` descriptions and validation constraints (`min_length`, `max_length`, `ge`, `gt`, `le`)
- Response DTOs include `model_config = {"from_attributes": True}` for ORM compatibility
- No `any` types — all fields use explicit type hints (e.g., `Optional[dict]` for JSONB columns)
- DTOs map directly to `ld_*` database tables; virtual DTOs (SpecialistCandidateDTO, SuggestionResponseDTO, ClassificationResultDTO, DashboardStatsDTO) serve Wave 2+ services

### DTO Categories

| Category | DTOs | Database Table |
|----------|------|----------------|
| Client | Create, Update, Response | `ld_clients` |
| Specialist | Create, Update, Response, Detail, Filter + ExpertiseDTO, JurisdictionDTO | `ld_specialists`, `ld_specialist_expertise`, `ld_specialist_jurisdictions` |
| Case | Create, Update, Response, Detail, Filter, ListItem | `ld_cases` |
| Assignment | Create, Response | `ld_case_specialists` |
| Deliverable | Create, Update, Response | `ld_case_deliverables` |
| Message | Create, Response | `ld_case_messages` |
| Document | Create, Response | `ld_case_documents` |
| Pricing | PricingProposalDTO, PricingHistoryResponseDTO | `ld_pricing_history` |
| Scoring | ScoreSubmitDTO, ScoreResponseDTO | `ld_specialist_scores` |
| Engine | SpecialistCandidateDTO, SuggestionResponseDTO | Virtual (assignment engine) |
| Classification | ClassificationResultDTO | Virtual (AI classification) |
| Analytics | DashboardStatsDTO | Virtual (dashboard aggregation) |

## How to Use

1. **Import DTOs** directly from the module:
   ```python
   from src.interface.legaldesk_dto import (
       CaseCreateDTO, CaseResponseDTO, CaseStatus, LegalDomain
   )
   ```

2. **Create DTOs** for input validation in API endpoints:
   ```python
   @router.post("/api/legaldesk/cases")
   async def create_case(data: CaseCreateDTO):
       # Pydantic validates all fields automatically
       pass
   ```

3. **Response DTOs** for ORM serialization:
   ```python
   case_response = CaseResponseDTO.model_validate(case_orm_object)
   ```

4. **Filter DTOs** for query parameter validation:
   ```python
   @router.get("/api/legaldesk/cases")
   async def list_cases(filters: CaseFilterDTO = Depends()):
       pass
   ```

5. **Status transitions** for workflow validation:
   ```python
   from src.interface.legaldesk_dto import CASE_STATUS_TRANSITIONS, CaseStatus

   allowed = CASE_STATUS_TRANSITIONS[CaseStatus.NEW]
   # Returns: ["classifying", "open"]
   ```

## Configuration

No additional configuration required. Uses only `pydantic`, `datetime`, `decimal`, and `enum` from stdlib/existing requirements.

## Testing

```bash
# Run Legal Desk DTO tests
cd apps/Server && python -m pytest tests/test_legaldesk_dto.py -v

# Run full test suite for regression check
cd apps/Server && python -m pytest
```

Tests cover:
- All 14 enums: member count, value verification, `str` inheritance
- `CASE_STATUS_TRANSITIONS`: coverage of all statuses, valid transitions, archived has empty list
- Create DTOs: valid data (all fields, required only), invalid data (empty strings, negative amounts, out-of-range scores)
- Update DTOs: partial updates, all-None construction
- Response DTOs: `from_attributes` with mock ORM objects
- Filter DTOs: various filter combinations
- Virtual DTOs: boundary values for match_score, confidence
- Edge cases: score boundaries (0.00, 5.00, 5.01), max_length boundaries, empty lists

## Notes

- This is a backend-only feature — no UI, no frontend changes, no E2E tests needed
- Database uses `SERIAL` integer primary keys (not UUID), so all `id` fields are `int`
- The `ai_classification` column in `ld_cases` is JSONB, represented as `Optional[dict]`
- `case_number` is auto-generated by the service layer (not in `CaseCreateDTO`, but in `CaseResponseDTO`)
- Score values constrained to 0.00–5.00 via DTO validation despite DB column allowing 0.00–9.99
- Wave 2 repositories and Wave 3 services will import these DTOs for input validation and response serialization
