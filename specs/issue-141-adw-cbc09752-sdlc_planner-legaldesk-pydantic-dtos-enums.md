# Feature: Legal Desk Pydantic DTOs & Enums

## Metadata
issue_number: `141`
adw_id: `cbc09752`
issue_json: ``

## Feature Description
Create the comprehensive Pydantic DTO and enum file for the Faroo Legal Desk module. This single file (`apps/Server/src/interface/legaldesk_dto.py`) contains 14 string enums, a case status transition map constant, and ~40 Pydantic v2 models covering CRUD operations, filtering, responses, and specialized DTOs for the assignment engine, AI classification, pricing negotiation, and analytics dashboard. This is Wave 1 (Foundation) issue LD-004 of the Legal Desk implementation, running in parallel with LD-001 through LD-005, and has no dependencies. Wave 2 repositories and Wave 3 services will import these DTOs for input validation and response serialization.

## User Story
As a Legal Desk backend developer
I want a complete set of validated Pydantic DTOs and enums for all Legal Desk API operations
So that Wave 2 repositories and Wave 3 services can use them for type-safe input validation, response serialization, and consistent API contracts across the case management and specialist assignment system

## Problem Statement
The Legal Desk module requires a comprehensive set of data transfer objects to define the API contract between the REST adapter layer, the service layer, and the repository layer. Without these DTOs, no API endpoints can accept validated input or return structured responses for cases, specialists, clients, assignments, deliverables, messages, documents, pricing, scoring, or analytics. The 11 database tables created in LD-001 need corresponding Pydantic models that enforce validation rules, type safety, and serialization standards consistent with the existing codebase patterns.

## Solution Statement
Create a single `legaldesk_dto.py` file in the existing `apps/Server/src/interface/` directory containing all 14 enums (using `str, Enum` pattern), the `CASE_STATUS_TRANSITIONS` constant dictionary, and ~40 Pydantic v2 `BaseModel` subclasses. Each DTO uses `Field(...)` with descriptions, validation constraints (`min_length`, `max_length`, `ge`, `gt`), and proper type hints (no `any` types). Response DTOs include `model_config = {"from_attributes": True}` for ORM compatibility. All DTOs map directly to the `ld_*` database tables defined in `create_legaldesk_tables.sql`. A comprehensive test file validates all enums, DTOs, validation rules, and edge cases.

## Relevant Files
Use these files to implement the feature:

- `CLAUDE.md` — Clean Architecture principles, naming conventions, Python standards (type hints, docstrings), logging format
- `apps/Server/src/interface/event_dto.py` — Reference for enum + DTO pattern in a single file (EventType, EventStatus, EventFrequency enums with Create/Update/Response DTOs)
- `apps/Server/src/interface/prospect_dto.py` — Reference for Filter DTO pattern (ProspectFilterDTO with Optional fields) and List Response pattern
- `apps/Server/src/interface/person_dto.py` — Reference for enum with default value, Create/Update/Response DTO structure
- `apps/Server/src/interface/resource_dto.py` — Reference for Decimal field patterns with `ge=0`, `gt=0` constraints
- `apps/Server/src/interface/__init__.py` — Interface package init (check if exports need updating)
- `apps/Server/database/create_legaldesk_tables.sql` — Database schema defining all 11 `ld_*` tables; DTOs must match these column types and constraints exactly
- `app_docs/feature-de0cefbe-legaldesk-database-schema.md` — Legal Desk database schema documentation
- `apps/Server/tests/test_person_model.py` — Reference for DTO/enum test patterns (validation tests, enum value tests, response DTO from_attributes tests)

### New Files
- `apps/Server/src/interface/legaldesk_dto.py` — All 14 enums, status transition map, and ~40 Pydantic DTOs for Legal Desk
- `apps/Server/tests/test_legaldesk_dto.py` — Comprehensive tests for all enums, DTOs, validation rules, and edge cases

## Implementation Plan
### Phase 1: Foundation
- Review existing DTO files (`event_dto.py`, `prospect_dto.py`, `person_dto.py`, `resource_dto.py`) to confirm conventions for enum definition, Field constraints, Optional patterns, and `model_config`
- Review `create_legaldesk_tables.sql` to map every column type, constraint, and relationship to DTO fields
- Confirm the `interface/__init__.py` does not require explicit exports (existing DTOs are imported directly from their modules)

### Phase 2: Core Implementation
- Create `legaldesk_dto.py` with all 14 enums following `(str, Enum)` pattern with docstrings
- Add `CASE_STATUS_TRANSITIONS` constant dictionary
- Implement all ~40 DTOs organized by domain entity:
  - Client DTOs (Create, Update, Response) — maps to `ld_clients`
  - Specialist DTOs (Create, Update, Response, Detail, Filter) + ExpertiseDTO + JurisdictionDTO — maps to `ld_specialists`, `ld_specialist_expertise`, `ld_specialist_jurisdictions`
  - Case DTOs (Create, Update, Response, Detail, Filter, ListItem) — maps to `ld_cases`
  - Assignment DTOs (Create, Response) — maps to `ld_case_specialists`
  - Deliverable DTOs (Create, Update, Response) — maps to `ld_case_deliverables`
  - Message DTOs (Create, Response) — maps to `ld_case_messages`
  - Document DTOs (Create, Response) — maps to `ld_case_documents`
  - Pricing DTOs (PricingProposalDTO, PricingHistoryResponseDTO) — maps to `ld_pricing_history`
  - Scoring DTOs (ScoreSubmitDTO, ScoreResponseDTO) — maps to `ld_specialist_scores`
  - Engine DTOs (SpecialistCandidateDTO, SuggestionResponseDTO) — virtual DTOs for assignment engine
  - Classification DTO (ClassificationResultDTO) — virtual DTO for AI classification
  - Analytics DTO (DashboardStatsDTO) — virtual DTO for dashboard aggregation

### Phase 3: Integration
- Create comprehensive test file `test_legaldesk_dto.py` covering all enums, DTOs, and validation rules
- Run full test suite to ensure zero regressions

## Step by Step Tasks

### Step 1: Review existing patterns and database schema
- Read `apps/Server/src/interface/event_dto.py` for enum + DTO file structure
- Read `apps/Server/src/interface/prospect_dto.py` for FilterDTO and ListResponse patterns
- Read `apps/Server/src/interface/resource_dto.py` for Decimal field constraint patterns
- Read `apps/Server/database/create_legaldesk_tables.sql` for exact column types and constraints
- Read `apps/Server/tests/test_person_model.py` for DTO test patterns

### Step 2: Create `apps/Server/src/interface/legaldesk_dto.py` with enums and transition map
- Add module docstring: `"""Pydantic DTOs and enums for Legal Desk case management operations."""`
- Import: `from datetime import date, datetime`, `from decimal import Decimal`, `from enum import Enum`, `from typing import Any, List, Optional`, `from pydantic import BaseModel, Field`
- Define all 14 enums with docstrings, each inheriting from `(str, Enum)`:
  - `CaseStatus` — 11 values: new, classifying, open, assigning, active, in_progress, review, negotiating, completed, closed, archived
  - `CaseType` — 2 values: advisory, litigation
  - `LegalDomain` — 10 values: corporate, ip, labor, tax, litigation, real_estate, immigration, regulatory, data_privacy, commercial
  - `CaseComplexity` — 4 values: low, medium, high, critical
  - `CasePriority` — 4 values: low, medium, high, urgent
  - `OriginationChannel` — 2 values: direct, referral
  - `SpecialistStatus` — 3 values: active, inactive, on_leave
  - `SpecialistType` — 2 values: individual, boutique_firm
  - `ProficiencyLevel` — 3 values: junior, intermediate, expert
  - `AssignmentRole` — 4 values: lead, support, reviewer, consultant
  - `AssignmentStatus` — 5 values: proposed, accepted, rejected, active, completed
  - `DeliverableStatus` — 5 values: pending, in_progress, review, completed, cancelled
  - `PricingAction` — 6 values: proposal, counter, accept, reject, adjust, final
  - `ClientType` — 2 values: company, individual
- Define `CASE_STATUS_TRANSITIONS: dict[str, list[str]]` constant with all valid transitions

### Step 3: Add Client DTOs
- `ClientCreateDTO` — Required: `name` (str, min_length=1, max_length=255), `client_type` (ClientType, default=COMPANY). Optional: `contact_email`, `contact_phone`, `country`, `industry`, `notes`
- `ClientUpdateDTO` — All fields Optional for partial updates, same constraints as Create
- `ClientResponseDTO` — All fields from `ld_clients` table including `id` (int), `is_active` (bool), `created_at`, `updated_at`. Include `model_config = {"from_attributes": True}`

### Step 4: Add Specialist DTOs
- `ExpertiseDTO` — `legal_domain` (LegalDomain), `proficiency_level` (ProficiencyLevel, default=INTERMEDIATE), `years_in_domain` (int, ge=0, default=0)
- `JurisdictionDTO` — `country` (str, min_length=1, max_length=100), `region` (Optional[str], max_length=100), `is_primary` (bool, default=False)
- `SpecialistCreateDTO` — Required: `full_name` (str, min_length=1, max_length=255), `email` (str, max_length=255). Optional: `phone`, `years_experience` (int, ge=0), `hourly_rate` (Decimal, gt=0), `currency` (str, default="EUR"), `max_concurrent_cases` (int, ge=1, default=5), `expertise` (List[ExpertiseDTO]), `jurisdictions` (List[JurisdictionDTO])
- `SpecialistUpdateDTO` — All fields Optional for partial updates
- `SpecialistResponseDTO` — All `ld_specialists` columns including `id` (int), `current_workload`, `overall_score`, `is_active`, `created_at`, `updated_at`. Include `model_config`
- `SpecialistDetailDTO` — Extends SpecialistResponseDTO fields plus `expertise: List[ExpertiseDTO]`, `jurisdictions: List[JurisdictionDTO]`. Include `model_config`
- `SpecialistFilterDTO` — Optional filters: `legal_domain` (LegalDomain), `proficiency_level` (ProficiencyLevel), `is_active` (bool), `min_experience` (int), `max_workload` (int)

### Step 5: Add Case DTOs
- `CaseCreateDTO` — Required: `title` (str, min_length=1, max_length=500), `client_id` (int), `legal_domain` (LegalDomain). Optional: `description`, `case_type` (CaseType), `complexity` (CaseComplexity, default=MEDIUM), `priority` (CasePriority, default=MEDIUM), `budget` (Decimal, ge=0), `deadline` (date)
- `CaseUpdateDTO` — All fields Optional for partial updates. Include `status` (CaseStatus) for status transitions
- `CaseResponseDTO` — All `ld_cases` columns: `id` (int), `case_number` (str), `title`, `description`, `client_id`, `legal_domain`, `complexity`, `priority`, `status`, `budget`, `estimated_cost`, `final_quote`, `margin_percentage`, `deadline`, `ai_classification` (Optional[dict]), `created_at`, `updated_at`. Include `model_config`
- `CaseDetailDTO` — CaseResponseDTO fields plus `client: Optional[ClientResponseDTO]`, `specialists: List[AssignmentResponseDTO]`, `deliverables: List[DeliverableResponseDTO]`. Include `model_config`
- `CaseFilterDTO` — Optional filters: `status` (CaseStatus), `legal_domain` (LegalDomain), `priority` (CasePriority), `case_type` (CaseType), `client_id` (int), `complexity` (CaseComplexity)
- `CaseListItemDTO` — Lightweight DTO for list views: `id`, `case_number`, `title`, `client_id`, `legal_domain`, `priority`, `status`, `deadline`, `created_at`. Include `model_config`

### Step 6: Add Assignment DTOs
- `AssignmentCreateDTO` — Required: `case_id` (int), `specialist_id` (int). Optional: `role` (AssignmentRole, default=LEAD), `proposed_fee` (Decimal, ge=0), `fee_currency` (str, default="EUR")
- `AssignmentResponseDTO` — All `ld_case_specialists` columns: `id` (int), `case_id`, `specialist_id`, `role`, `status`, `proposed_fee`, `agreed_fee`, `fee_currency`, `assigned_at`, `responded_at`. Include `model_config`

### Step 7: Add Deliverable DTOs
- `DeliverableCreateDTO` — Required: `case_id` (int), `title` (str, min_length=1, max_length=500). Optional: `specialist_id` (int), `description`, `due_date` (date)
- `DeliverableUpdateDTO` — All fields Optional: `title`, `description`, `status` (DeliverableStatus), `due_date`, `specialist_id`
- `DeliverableResponseDTO` — All `ld_case_deliverables` columns: `id` (int), `case_id`, `specialist_id`, `title`, `description`, `status`, `due_date`, `completed_at`, `created_at`, `updated_at`. Include `model_config`

### Step 8: Add Message DTOs
- `MessageCreateDTO` — Required: `case_id` (int), `message` (str, min_length=1). Optional: `sender_type` (str, default="system"), `sender_name` (str), `is_internal` (bool, default=False)
- `MessageResponseDTO` — All `ld_case_messages` columns: `id` (int), `case_id`, `sender_type`, `sender_name`, `message`, `is_internal`, `created_at`. Include `model_config`

### Step 9: Add Document DTOs
- `DocumentCreateDTO` — Required: `case_id` (int), `file_name` (str, min_length=1, max_length=500), `file_url` (str, min_length=1, max_length=1000). Optional: `file_type` (str), `file_size_bytes` (int, ge=0), `uploaded_by` (str)
- `DocumentResponseDTO` — All `ld_case_documents` columns: `id` (int), `case_id`, `file_name`, `file_url`, `file_type`, `file_size_bytes`, `uploaded_by`, `created_at`. Include `model_config`

### Step 10: Add Pricing DTOs
- `PricingProposalDTO` — Required: `case_id` (int), `action` (PricingAction), `new_amount` (Decimal, ge=0). Optional: `previous_amount` (Decimal, ge=0), `currency` (str, default="EUR"), `changed_by` (str), `notes` (str)
- `PricingHistoryResponseDTO` — All `ld_pricing_history` columns: `id` (int), `case_id`, `action`, `previous_amount`, `new_amount`, `currency`, `changed_by`, `notes`, `created_at`. Include `model_config`

### Step 11: Add Scoring DTOs
- `ScoreSubmitDTO` — Required: `specialist_id` (int), `case_id` (int). All score fields Optional[Decimal] with `ge=0, le=5`: `quality_score`, `teamwork_score`, `delivery_score`, `satisfaction_score`, `overall_score`. Optional: `feedback` (str)
- `ScoreResponseDTO` — All `ld_specialist_scores` columns: `id` (int), `specialist_id`, `case_id`, all score fields, `feedback`, `scored_at`. Include `model_config`

### Step 12: Add Assignment Engine DTOs
- `SpecialistCandidateDTO` — Virtual DTO for engine output: `specialist_id` (int), `full_name` (str), `email` (str), `match_score` (Decimal, ge=0, le=1), `hourly_rate` (Optional[Decimal]), `currency` (str), `current_workload` (int), `max_concurrent_cases` (int), `expertise_match` (List[str]), `jurisdiction_match` (List[str])
- `SuggestionResponseDTO` — `case_id` (int), `legal_domain` (str), `candidates` (List[SpecialistCandidateDTO]), `generated_at` (datetime)

### Step 13: Add Classification and Analytics DTOs
- `ClassificationResultDTO` — `legal_domain` (LegalDomain), `complexity` (CaseComplexity), `case_type` (CaseType), `confidence` (Decimal, ge=0, le=1), `suggested_tags` (List[str], default_factory=list)
- `DashboardStatsDTO` — `total_cases` (int), `active_cases` (int), `completed_cases` (int), `total_specialists` (int), `avg_case_duration_days` (Optional[Decimal]), `total_revenue` (Optional[Decimal]), `cases_by_status` (dict[str, int]), `cases_by_domain` (dict[str, int]), `cases_by_priority` (dict[str, int])

### Step 14: Create `apps/Server/tests/test_legaldesk_dto.py`
- Test all 14 enums: verify member count, verify each value string, verify `str` inheritance
- Test `CASE_STATUS_TRANSITIONS`: verify all CaseStatus values have entries, verify archived has empty list, verify known transitions
- Test all Create DTOs with valid data (all fields, required only)
- Test all Create DTOs with invalid data (empty required strings, negative amounts, out-of-range scores)
- Test all Update DTOs with partial data (single field, all None)
- Test all Response DTOs with `model_config` from_attributes using mock objects
- Test Filter DTOs with various filter combinations
- Test virtual DTOs (SpecialistCandidateDTO, SuggestionResponseDTO, ClassificationResultDTO, DashboardStatsDTO)
- Test edge cases: score boundary values (0.00, 5.00, 5.01), empty lists, None optionals
- Follow test naming and logging patterns from `test_person_model.py`

### Step 15: Run validation commands
- Run `cd apps/Server && python -m pytest tests/test_legaldesk_dto.py -v` to validate new tests pass
- Run `cd apps/Server && python -m pytest` to validate zero regressions across all tests

## Testing Strategy
### Unit Tests
- **Enum tests**: Verify each of the 14 enums has the correct number of members and correct string values
- **Transition map tests**: Verify `CASE_STATUS_TRANSITIONS` covers all `CaseStatus` members and each transition list contains only valid status values
- **Create DTO tests**: Valid construction with all fields, valid with required-only, invalid with missing required fields, invalid with constraint violations (empty strings, negative numbers, out-of-range decimals)
- **Update DTO tests**: Valid partial updates with single fields, all-None construction (valid for partial updates)
- **Response DTO tests**: Construction from dict, `from_attributes=True` with mock ORM objects
- **Filter DTO tests**: Valid filter combinations, all-None (no filters)
- **Virtual DTO tests**: SpecialistCandidateDTO match_score boundaries, ClassificationResultDTO confidence boundaries, DashboardStatsDTO with empty dicts
- **Score DTO tests**: Boundary values 0.00 and 5.00 accepted, values > 5.00 rejected

### Edge Cases
- `CaseCreateDTO` with `budget=0` (valid, zero budget allowed)
- `ScoreSubmitDTO` with all scores at boundary values (0.00, 5.00)
- `ScoreSubmitDTO` with score exceeding maximum (5.01, should reject)
- `SpecialistCandidateDTO` with `match_score=0` and `match_score=1` (both valid boundaries)
- `ClassificationResultDTO` with `confidence=0` and `confidence=1` (both valid boundaries)
- `CaseFilterDTO` with all fields None (valid, means no filtering)
- `SpecialistCreateDTO` with empty `expertise` and `jurisdictions` lists (valid)
- `ClientCreateDTO` with `name` at max_length=255 (valid boundary)
- `ClientCreateDTO` with `name` at 256 chars (should reject)
- `CASE_STATUS_TRANSITIONS["archived"]` returns empty list (no transitions from archived)

## Acceptance Criteria
- `apps/Server/src/interface/legaldesk_dto.py` exists with all 14 enums, the transition map, and ~40 DTOs
- All enums inherit from `(str, Enum)` and have docstrings
- All DTOs use Pydantic v2 `BaseModel` with `Field(...)` descriptions
- All Response DTOs include `model_config = {"from_attributes": True}`
- No `any` types anywhere in the file — all fields have explicit type hints
- All DTOs match the `ld_*` database schema column types (int PKs, Decimal for money, Optional for nullable columns, datetime for timestamps)
- `CASE_STATUS_TRANSITIONS` covers all 11 `CaseStatus` members
- `apps/Server/tests/test_legaldesk_dto.py` exists with comprehensive tests
- All tests pass with `python -m pytest tests/test_legaldesk_dto.py -v`
- Full test suite passes with zero regressions: `python -m pytest`

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/test_legaldesk_dto.py -v` — Run Legal Desk DTO tests to verify all enums, DTOs, and validation rules
- `cd apps/Server && python -m pytest` — Run full Server test suite to validate zero regressions

## Notes
- This is a backend-only feature (no UI, no frontend changes, no E2E tests needed)
- The database uses `SERIAL` integer primary keys (not UUID), so all `id` fields in DTOs are `int`, not `UUID`
- The `ai_classification` column in `ld_cases` is JSONB — represented as `Optional[dict]` in DTOs (using `dict` not `Any`)
- `CaseDetailDTO` references other Response DTOs (`ClientResponseDTO`, `AssignmentResponseDTO`, `DeliverableResponseDTO`) — these must be defined before `CaseDetailDTO` in the file to avoid forward reference issues
- Virtual DTOs (SpecialistCandidateDTO, SuggestionResponseDTO, ClassificationResultDTO, DashboardStatsDTO) do not map directly to database tables but serve the assignment engine, AI classification service, and analytics service in later waves
- The `case_number` field is auto-generated by the service layer (not provided in `CaseCreateDTO`), but returned in `CaseResponseDTO`
- Score values use `DECIMAL(3,2)` in the database, meaning range 0.00–9.99, but business logic constrains scores to 0.00–5.00 via DTO validation (`ge=0, le=5`)
- No new dependencies required — uses only `pydantic`, `datetime`, `decimal`, `enum` from stdlib/existing requirements
