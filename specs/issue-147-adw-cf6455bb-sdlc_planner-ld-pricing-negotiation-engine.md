# Feature: Legal Desk Pricing Negotiation Engine

## Metadata
issue_number: `147`
adw_id: `cf6455bb`
issue_json: `{"number":147,"title":"[Legal Desk] Wave 3: Pricing Negotiation Engine","body":"..."}`

## Feature Description
Implements the pricing negotiation service for the Legal Desk module. This service manages the full pricing lifecycle between Faroo Legal, specialists, and clients — tracking proposals, counter-offers, acceptance, and rejection with a complete audit trail stored in `ld_pricing_history`. When pricing is accepted, the service locks `final_quote` and `margin_percentage` on the case record. The margin formula is: `margin_pct = ((client_price - specialist_cost) / client_price) * 100`.

This is Wave 3 (Backend Business Logic) of the Legal Desk module. It builds on Wave 1 (database schema, models, DTOs) and Wave 2 (repositories). Wave 4 will expose API routes and Wave 6 will build the frontend.

## User Story
As a Faroo Legal case manager
I want to create pricing proposals, submit counter-offers, accept or reject pricing for cases
So that the pricing negotiation lifecycle is tracked with full audit trail and accepted pricing locks financial terms on the case

## Problem Statement
The Legal Desk module has the data layer (models, DTOs, repositories) but no business logic service to orchestrate pricing negotiations. Without this service, there is no way to create proposals, handle counter-offers, accept/reject pricing, or maintain the audit trail required for the pricing negotiation workflow.

## Solution Statement
Create an `LdPricingService` that orchestrates pricing operations by:
1. Creating a lightweight `LdPricingRepository` for `ld_pricing_history` table CRUD operations (following Clean Architecture — service must not access DB directly)
2. Implementing the `LdPricingService` with methods for `create_proposal`, `submit_counter`, `accept_pricing`, `reject_pricing`, and `get_pricing_history`
3. Using the existing `LdCaseRepository` to update case financial fields (`estimated_cost`, `final_quote`, `margin_percentage`)
4. Mapping service parameters to the existing data model: `specialist_cost` → `previous_amount`, `client_price` → `new_amount`

## Relevant Files
Use these files to implement the feature:

- `apps/Server/src/models/ld_pricing_history.py` — LdPricingHistory SQLAlchemy model with columns: id, case_id, action, previous_amount, new_amount, currency, changed_by, notes, created_at
- `apps/Server/src/models/ld_case.py` — LdCase model with financial fields: estimated_cost, final_quote, margin_percentage
- `apps/Server/src/interface/legaldesk_dto.py` — Contains PricingAction enum (PROPOSAL, COUNTER, ACCEPT, REJECT, ADJUST, FINAL), PricingProposalDTO, PricingHistoryResponseDTO
- `apps/Server/src/repository/ld_case_repository.py` — LdCaseRepository with update() method for modifying case fields. Singleton: `ld_case_repository`
- `apps/Server/src/core/services/budget_service.py` — Reference for service class pattern (singleton instance, logging, docstrings, type hints)
- `apps/Server/tests/test_ld_case_repository.py` — Reference for test pattern (pytest fixtures, MagicMock, class-based test organization)
- `apps/Server/src/config/database.py` — Database session and Base
- `app_docs/feature-de0cefbe-legaldesk-database-schema.md` — Legal Desk database schema documentation
- `app_docs/feature-cbc09752-legaldesk-pydantic-dtos-enums.md` — Legal Desk DTOs and enums documentation
- `app_docs/feature-444abca2-legaldesk-core-repositories.md` — Legal Desk core repositories documentation
- `app_docs/feature-601d0350-legaldesk-supporting-repositories-wave2.md` — Legal Desk Wave 2 repositories documentation

### New Files
- `apps/Server/src/repository/ld_pricing_repository.py` — New repository for ld_pricing_history table operations
- `apps/Server/src/core/services/ld_pricing_service.py` — New pricing negotiation service with business logic
- `apps/Server/tests/test_ld_pricing_repository.py` — Unit tests for pricing repository
- `apps/Server/tests/test_ld_pricing_service.py` — Unit tests for pricing service

## Implementation Plan
### Phase 1: Foundation
Create the `LdPricingRepository` data access layer for the `ld_pricing_history` table. This follows Clean Architecture by separating data access from business logic. The repository provides CRUD operations that the service will consume.

### Phase 2: Core Implementation
Implement the `LdPricingService` with all five methods specified in the issue. The service coordinates between the pricing repository (for audit trail) and the case repository (for updating case financial fields). Key business logic includes margin calculation, case field locking on acceptance, and comprehensive logging.

### Phase 3: Integration
Write comprehensive unit tests for both the repository and service layers. Tests use MagicMock to isolate from the database, following the established test patterns in the codebase.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Read reference documentation
- Read `app_docs/feature-de0cefbe-legaldesk-database-schema.md` to understand the ld_pricing_history table schema
- Read `app_docs/feature-cbc09752-legaldesk-pydantic-dtos-enums.md` to understand PricingAction enum and PricingHistoryResponseDTO
- Read `app_docs/feature-444abca2-legaldesk-core-repositories.md` to understand repository patterns
- Read `app_docs/feature-601d0350-legaldesk-supporting-repositories-wave2.md` to understand Wave 2 repository patterns (especially LdAssignmentRepository for fee-related operations)

### Step 2: Create LdPricingRepository
- Create `apps/Server/src/repository/ld_pricing_repository.py`
- Follow the singleton pattern used in `ld_case_repository.py`
- Implement the following methods:
  - `create(self, db: Session, data: dict) -> LdPricingHistory` — Insert a new pricing history record. Log: `INFO [LdPricingRepository]: Creating pricing entry for case {case_id}, action={action}`
  - `get_by_case(self, db: Session, case_id: int) -> list[LdPricingHistory]` — Return all pricing history for a case, ordered by created_at ascending (chronological). Log: `INFO [LdPricingRepository]: Getting pricing history for case {case_id}`
  - `get_latest(self, db: Session, case_id: int) -> Optional[LdPricingHistory]` — Return the most recent pricing entry for a case (ordered by created_at descending, limit 1). Log: `INFO [LdPricingRepository]: Getting latest pricing entry for case {case_id}`
- Import from `src.models.ld_pricing_history` and `src.config.database`
- Export singleton instance: `ld_pricing_repository = LdPricingRepository()`

### Step 3: Create unit tests for LdPricingRepository
- Create `apps/Server/tests/test_ld_pricing_repository.py`
- Follow the test pattern in `tests/test_ld_case_repository.py`
- Create fixtures: `repo`, `mock_db`, `mock_pricing_entry`
- Test classes:
  - `TestCreatePricingEntry` — Verify db.add, db.commit, db.refresh are called
  - `TestGetByCase` — Test returns list of entries, test empty list for unknown case_id
  - `TestGetLatest` — Test returns single entry, test returns None for unknown case_id
- Run tests to verify they pass

### Step 4: Create LdPricingService
- Create `apps/Server/src/core/services/ld_pricing_service.py`
- Follow the service pattern in `budget_service.py`
- Import repositories: `ld_pricing_repository` and `ld_case_repository`
- Import DTOs: `PricingAction`, `PricingHistoryResponseDTO` from `src.interface.legaldesk_dto`
- Import model: `LdPricingHistory` from `src.models.ld_pricing_history`
- Implement the following methods:

#### `create_proposal(self, db: Session, case_id: int, specialist_cost: Decimal, client_price: Decimal, notes: Optional[str], created_by: Optional[str]) -> LdPricingHistory`
  - Validate case exists via `ld_case_repository.get_by_id(db, case_id)` — raise ValueError if not found
  - Validate `client_price > 0` to prevent division by zero in margin calculation
  - Calculate margin: `margin_pct = ((client_price - specialist_cost) / client_price) * 100`
  - Create pricing history entry via `ld_pricing_repository.create()` with:
    - `case_id=case_id`
    - `action=PricingAction.PROPOSAL.value`
    - `previous_amount=specialist_cost` (specialist cost is the base/previous amount)
    - `new_amount=client_price` (client price is the proposed new amount)
    - `currency="EUR"` (default)
    - `changed_by=created_by`
    - `notes=notes`
  - Update case `estimated_cost = specialist_cost` via `ld_case_repository.update()`
  - Log: `INFO [LdPricingService]: Proposal for case {case_id}: specialist_cost={specialist_cost}, client_price={client_price}, margin={margin_pct:.1f}%`
  - Return the created pricing history entry

#### `submit_counter(self, db: Session, case_id: int, specialist_cost: Decimal, client_price: Decimal, notes: Optional[str], created_by: Optional[str]) -> LdPricingHistory`
  - Validate case exists — raise ValueError if not found
  - Validate `client_price > 0`
  - Calculate margin: `margin_pct = ((client_price - specialist_cost) / client_price) * 100`
  - Create pricing history entry with `action=PricingAction.COUNTER.value`, mapping `specialist_cost` → `previous_amount`, `client_price` → `new_amount`
  - Log: `INFO [LdPricingService]: Counter-offer for case {case_id}: specialist_cost={specialist_cost}, client_price={client_price}, margin={margin_pct:.1f}%`
  - Return the created pricing history entry

#### `accept_pricing(self, db: Session, case_id: int, created_by: Optional[str]) -> LdPricingHistory`
  - Validate case exists — raise ValueError if not found
  - Get latest pricing entry via `ld_pricing_repository.get_latest(db, case_id)` — raise ValueError if no pricing history exists
  - Extract `client_price = latest.new_amount` and `specialist_cost = latest.previous_amount`
  - Calculate margin: `margin_pct = ((client_price - specialist_cost) / client_price) * 100`
  - Lock case financial fields via `ld_case_repository.update()`:
    - `final_quote = client_price`
    - `margin_percentage = margin_pct`
  - Create pricing history entry with `action=PricingAction.ACCEPT.value`, using same `previous_amount` and `new_amount` from latest entry
  - Log: `INFO [LdPricingService]: Pricing accepted for case {case_id}: final_quote={client_price}, margin={margin_pct:.1f}%`
  - Return the created pricing history entry

#### `reject_pricing(self, db: Session, case_id: int, notes: Optional[str], created_by: Optional[str]) -> LdPricingHistory`
  - Validate case exists — raise ValueError if not found
  - Create pricing history entry with `action=PricingAction.REJECT.value`, `notes=notes`, `changed_by=created_by`
  - Log: `INFO [LdPricingService]: Pricing rejected for case {case_id}: {notes}`
  - Return the created pricing history entry

#### `get_pricing_history(self, db: Session, case_id: int) -> list[PricingHistoryResponseDTO]`
  - Get all pricing entries via `ld_pricing_repository.get_by_case(db, case_id)`
  - Convert each to `PricingHistoryResponseDTO` using `PricingHistoryResponseDTO.model_validate(entry)`
  - Log: `INFO [LdPricingService]: Retrieved {count} pricing entries for case {case_id}`
  - Return the list of DTOs

- Export singleton instance: `ld_pricing_service = LdPricingService()`

### Step 5: Create unit tests for LdPricingService
- Create `apps/Server/tests/test_ld_pricing_service.py`
- Follow the test pattern in `tests/test_ld_case_repository.py`
- Use `unittest.mock.patch` to mock `ld_pricing_repository` and `ld_case_repository`
- Create fixtures:
  - `service` — `LdPricingService()` instance
  - `mock_db` — `MagicMock()` database session
  - `mock_case` — Mock LdCase with id=1, case_number="LD-202603-0001"
  - `mock_pricing_entry` — Mock LdPricingHistory with test data
- Test classes:

  - `TestCreateProposal`:
    - `test_create_proposal_calculates_margin` — Given specialist_cost=800, client_price=1000, verify margin=20.0%, verify pricing entry created, verify case estimated_cost updated
    - `test_create_proposal_case_not_found` — Verify raises ValueError when case doesn't exist
    - `test_create_proposal_zero_client_price` — Verify raises ValueError when client_price is 0

  - `TestSubmitCounter`:
    - `test_submit_counter_calculates_margin` — Given specialist_cost=900, client_price=1200, verify margin=25.0%, verify pricing entry created with action=counter
    - `test_submit_counter_case_not_found` — Verify raises ValueError

  - `TestAcceptPricing`:
    - `test_accept_pricing_locks_case` — Verify final_quote and margin_percentage are set on case, verify pricing entry with action=accept created
    - `test_accept_pricing_no_history` — Verify raises ValueError when no pricing history exists
    - `test_accept_pricing_case_not_found` — Verify raises ValueError

  - `TestRejectPricing`:
    - `test_reject_pricing_stores_notes` — Verify pricing entry with action=reject and notes created
    - `test_reject_pricing_case_not_found` — Verify raises ValueError

  - `TestGetPricingHistory`:
    - `test_get_pricing_history_returns_dtos` — Verify returns list of PricingHistoryResponseDTO
    - `test_get_pricing_history_empty` — Verify returns empty list when no entries

### Step 6: Run validation commands
- Run all tests to verify zero regressions
- Run type check and build commands

## Testing Strategy
### Unit Tests
- **Repository tests** (`test_ld_pricing_repository.py`): Verify database operations (add, commit, refresh, query) are called correctly using MagicMock. No actual database needed.
- **Service tests** (`test_ld_pricing_service.py`): Mock both repositories to test business logic in isolation. Verify margin calculation, case field updates, error handling, and correct action types.

### Edge Cases
- `client_price = 0` — Division by zero in margin calculation. Service must validate and raise ValueError.
- `specialist_cost > client_price` — Negative margin. This is valid (loss scenario) and should be allowed.
- `specialist_cost = 0` — Free specialist. Margin should be 100%. This is valid.
- `accept_pricing` with no prior pricing history — Must raise ValueError.
- `accept_pricing` where latest entry has `previous_amount = None` — Handle gracefully (use Decimal(0) fallback).
- Case not found for any operation — Must raise ValueError.

## Acceptance Criteria
- `LdPricingRepository` provides create, get_by_case, and get_latest methods with logging
- `LdPricingService.create_proposal` calculates margin correctly and updates case `estimated_cost`
- `LdPricingService.submit_counter` calculates margin and creates counter-offer audit record
- `LdPricingService.accept_pricing` locks `final_quote` and `margin_percentage` on the case from latest pricing entry
- `LdPricingService.reject_pricing` creates rejection audit record with notes
- `LdPricingService.get_pricing_history` returns chronological list of `PricingHistoryResponseDTO`
- Margin formula is correct: `((client_price - specialist_cost) / client_price) * 100`
- All methods validate case existence and raise ValueError for invalid operations
- All methods produce INFO-level log output following the `[ClassName]` pattern
- All unit tests pass with zero regressions
- Both repository and service follow singleton pattern with module-level instances

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/test_ld_pricing_repository.py -v` — Run pricing repository tests
- `cd apps/Server && python -m pytest tests/test_ld_pricing_service.py -v` — Run pricing service tests
- `cd apps/Server && python -m pytest tests/ -v` — Run all Server tests to validate zero regressions

## Notes
- **Field Mapping**: The issue uses `specialist_cost` and `client_price` as separate parameters, but the existing `LdPricingHistory` model has `previous_amount` and `new_amount`. The mapping is: `specialist_cost` → `previous_amount`, `client_price` → `new_amount`. This is semantically coherent since `previous_amount` represents the base cost and `new_amount` represents the proposed client-facing price.
- **Case Model Mapping**: The issue references `faroo_margin_pct` which maps to `margin_percentage` on the `LdCase` model. Similarly, `final_quote` maps directly to the `final_quote` column.
- **No API Routes**: This is Wave 3 (service layer only). API routes will be added in Wave 4. No REST endpoints or frontend work is needed.
- **No Frontend**: No UI components or E2E tests are needed for this backend-only service implementation.
- **Parallel Execution**: This issue runs in parallel with LD-008, LD-009, LD-011. No conflicts expected since this service creates a new file and only reads/updates cases via the existing repository.
- **Currency Default**: All pricing entries default to EUR currency. Future waves may add multi-currency support.
