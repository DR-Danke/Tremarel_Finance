# Feature: CRM Pipeline — Prospect Data Model

## Metadata
issue_number: `47`
adw_id: `57f962c3`
issue_json: ``

## Feature Description
Create the foundational data model for the CRM Pipeline feature — the Prospect entity. Prospects represent companies or contacts being tracked through a sales pipeline. They are entity-scoped (multi-entity support) so each family/startup entity has its own set of prospects. This issue delivers the database table (SQL), SQLAlchemy model, and Pydantic DTOs (create, update, response, list, filter) that subsequent issues (CRM-004 CRUD API, CRM-005 meeting records) depend on.

## User Story
As a finance tracker user managing a startup entity
I want to store prospect information (company name, contact details, pipeline stage, estimated value)
So that I can track sales pipeline opportunities alongside my financial data

## Problem Statement
The Finance Tracker currently has no CRM capability. Users managing startup entities need to track companies/contacts they are prospecting, including pipeline stage, estimated deal value, and contact information. There is no database table, model, or DTO to represent this data.

## Solution Statement
Add a new `prospects` table to the database schema, a `Prospect` SQLAlchemy model, and a full set of Pydantic DTOs following the exact same patterns used by existing entities (transactions, budgets, categories, recurring_templates). The prospect is entity-scoped via a `entity_id` foreign key with CASCADE delete, matching the multi-tenant pattern used throughout the application.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/database/schema.sql` — Existing schema to append the new `prospects` table definition
- `apps/Server/src/config/database.py` — Contains `Base` declarative base used by all models
- `apps/Server/src/models/__init__.py` — Must register the new `Prospect` model export
- `apps/Server/src/models/entity.py` — Reference pattern for SQLAlchemy model with UUID PK, timestamps, entity scoping
- `apps/Server/src/models/transaction.py` — Reference pattern for entity-scoped model with ForeignKey, Numeric columns, indexes
- `apps/Server/src/interface/entity_dto.py` — Reference pattern for Pydantic DTOs (Create, Update, Response)
- `apps/Server/src/interface/transaction_dto.py` — Reference pattern for DTOs with Literal validators, filter DTOs, list response DTOs
- `apps/Server/tests/test_entity.py` — Reference pattern for unit tests with mock DB, auth token helper

- Read `app_docs/feature-db5f36c7-database-schema-tables.md` — Database schema documentation (condition: working with database tables or schema)

### New Files
- `apps/Server/src/models/prospect.py` — New SQLAlchemy model for the Prospect entity
- `apps/Server/src/interface/prospect_dto.py` — New Pydantic DTOs for prospect create, update, response, list, filter
- `apps/Server/tests/test_prospect_model.py` — Unit tests for the Prospect model and DTOs

## Implementation Plan
### Phase 1: Foundation
Define the `prospects` database table in `schema.sql` with all columns, constraints, indexes, and the `updated_at` trigger. This establishes the canonical schema that the SQLAlchemy model must mirror.

### Phase 2: Core Implementation
1. Create the `Prospect` SQLAlchemy model in `apps/Server/src/models/prospect.py` following the exact pattern of `transaction.py` and `entity.py`.
2. Create Pydantic DTOs in `apps/Server/src/interface/prospect_dto.py` following the pattern of `transaction_dto.py` (Create, Update, Response, List, Filter DTOs).
3. Register the new model in `apps/Server/src/models/__init__.py`.

### Phase 3: Integration
1. Write unit tests validating DTO creation, validation rules, and model instantiation.
2. Run the full test suite to confirm zero regressions.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Read reference documentation
- Read `app_docs/feature-db5f36c7-database-schema-tables.md` for database schema conventions
- Read `apps/Server/src/models/transaction.py` as the primary model reference
- Read `apps/Server/src/interface/transaction_dto.py` as the primary DTO reference
- Read `apps/Server/src/models/__init__.py` for model registration

### Step 2: Add prospects table to database schema
- Append the `prospects` table definition to `apps/Server/database/schema.sql`
- Table columns:
  - `id` UUID PRIMARY KEY DEFAULT uuid_generate_v4()
  - `entity_id` UUID NOT NULL — FK to entities(id) ON DELETE CASCADE
  - `company_name` VARCHAR(255) NOT NULL — the prospect company/organization name
  - `contact_name` VARCHAR(255) — primary contact person name
  - `contact_email` VARCHAR(255) — primary contact email
  - `contact_phone` VARCHAR(100) — primary contact phone
  - `stage` VARCHAR(50) NOT NULL DEFAULT 'lead' — pipeline stage
  - `estimated_value` DECIMAL(15, 2) — estimated deal value
  - `source` VARCHAR(100) — where the prospect came from (referral, website, cold call, etc.)
  - `notes` TEXT — free-form notes about the prospect
  - `is_active` BOOLEAN DEFAULT TRUE — soft delete flag
  - `created_at` TIMESTAMP WITH TIME ZONE DEFAULT NOW()
  - `updated_at` TIMESTAMP WITH TIME ZONE
- Constraints:
  - `prospects_stage_check` CHECK (stage IN ('lead', 'contacted', 'qualified', 'proposal', 'negotiation', 'won', 'lost'))
  - `prospects_estimated_value_check` CHECK (estimated_value IS NULL OR estimated_value >= 0)
  - FK `fk_prospects_entity` → entities(id) ON DELETE CASCADE
- Indexes:
  - `idx_prospects_entity_id` ON prospects(entity_id)
  - `idx_prospects_stage` ON prospects(stage)
  - `idx_prospects_is_active` ON prospects(is_active)
  - `idx_prospects_entity_stage` ON prospects(entity_id, stage)
- Trigger: `prospects_updated_at` using the existing `update_updated_at_column()` function

### Step 3: Create SQLAlchemy Prospect model
- Create `apps/Server/src/models/prospect.py`
- Follow the exact pattern of `transaction.py`:
  - Import `uuid`, `datetime`, `Decimal`, `Optional` from typing
  - Import `Column`, `DateTime`, `ForeignKey`, `Numeric`, `String`, `Text`, `Boolean` from sqlalchemy
  - Import `UUID` from `sqlalchemy.dialects.postgresql`
  - Import `Base` from `src.config.database`
  - Class `Prospect(Base)` with `__tablename__ = "prospects"`
  - All columns matching the schema.sql definition
  - Type annotations on all columns
  - `__repr__` method returning `<Prospect(id=..., company_name=..., stage=...)>`

### Step 4: Register Prospect model in __init__.py
- Add `from src.models.prospect import Prospect` to `apps/Server/src/models/__init__.py`
- Add `"Prospect"` to the `__all__` list

### Step 5: Create Pydantic DTOs for Prospect
- Create `apps/Server/src/interface/prospect_dto.py`
- Follow the pattern of `transaction_dto.py`:
  - **ProspectCreateDTO**: entity_id (UUID), company_name (str, min 1, max 255), contact_name (Optional[str], max 255), contact_email (Optional[str], max 255), contact_phone (Optional[str], max 100), stage (Literal["lead","contacted","qualified","proposal","negotiation","won","lost"], default "lead"), estimated_value (Optional[Decimal], ge=0), source (Optional[str], max 100), notes (Optional[str])
  - **ProspectUpdateDTO**: All fields optional except entity_id (not updatable). company_name (Optional[str], min 1, max 255), contact_name, contact_email, contact_phone, stage, estimated_value, source, notes, is_active (Optional[bool])
  - **ProspectResponseDTO**: All fields including id, entity_id, timestamps. `model_config = {"from_attributes": True}`
  - **ProspectListResponseDTO**: prospects (List[ProspectResponseDTO]), total (int)
  - **ProspectFilterDTO**: stage (Optional), is_active (Optional[bool]), source (Optional[str]) — for filtering prospects by stage/status/source

### Step 6: Write unit tests for Prospect model and DTOs
- Create `apps/Server/tests/test_prospect_model.py`
- Follow the pattern of `test_entity.py` for mock setup
- Tests for DTOs:
  - `test_prospect_create_dto_valid` — valid creation DTO with all fields
  - `test_prospect_create_dto_minimal` — valid creation DTO with only required fields (entity_id, company_name)
  - `test_prospect_create_dto_invalid_stage` — invalid stage value rejected
  - `test_prospect_create_dto_negative_value` — negative estimated_value rejected
  - `test_prospect_update_dto_partial` — partial update with only some fields
  - `test_prospect_response_dto_from_attributes` — response DTO from mock model object
  - `test_prospect_filter_dto_defaults` — filter DTO with all None defaults
  - `test_prospect_list_response_dto` — list response with total count

### Step 7: Run validation commands
- Run the full server test suite to confirm zero regressions
- Run client type check and build to confirm no cross-impact

## Testing Strategy
### Unit Tests
- DTO validation tests: verify all field validators (stage Literal, estimated_value ge=0, company_name min/max length)
- DTO serialization tests: verify `model_config = {"from_attributes": True}` works with mock SQLAlchemy objects
- DTO partial update tests: verify UpdateDTO accepts any subset of fields
- Filter DTO tests: verify all filter fields default to None

### Edge Cases
- ProspectCreateDTO with empty company_name (should fail — min_length=1)
- ProspectCreateDTO with estimated_value of 0 (should pass — ge=0, not gt=0 since deals can be $0)
- ProspectCreateDTO with estimated_value of None (should pass — optional field)
- ProspectUpdateDTO with no fields set (should pass — all optional)
- ProspectCreateDTO with invalid stage value (should fail Literal validation)
- ProspectFilterDTO with all None values (should pass — used for unfiltered queries)

## Acceptance Criteria
- `prospects` table definition exists in `schema.sql` with all columns, constraints, indexes, and trigger
- `Prospect` SQLAlchemy model in `src/models/prospect.py` mirrors the schema exactly
- `Prospect` is exported from `src/models/__init__.py`
- `ProspectCreateDTO`, `ProspectUpdateDTO`, `ProspectResponseDTO`, `ProspectListResponseDTO`, `ProspectFilterDTO` exist in `src/interface/prospect_dto.py`
- All DTO validators enforce correct constraints (stage values, estimated_value >= 0, company_name length)
- Unit tests pass for all DTOs covering valid inputs, invalid inputs, and edge cases
- Full server test suite passes with zero regressions
- Client type check and build pass with zero regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -c "from src.models.prospect import Prospect; print('Prospect model imported successfully')"` — Validate model imports correctly
- `cd apps/Server && python -c "from src.interface.prospect_dto import ProspectCreateDTO, ProspectUpdateDTO, ProspectResponseDTO, ProspectListResponseDTO, ProspectFilterDTO; print('All Prospect DTOs imported successfully')"` — Validate all DTOs import correctly
- `cd apps/Server && uv run pytest tests/test_prospect_model.py -v` — Run prospect-specific tests
- `cd apps/Server && uv run pytest` — Run Server tests to validate the feature works with zero regressions
- `cd apps/Client && npm run tsc --noEmit` — Run Client type check to validate the feature works with zero regressions
- `cd apps/Client && npm run build` — Run Client build to validate the feature works with zero regressions

## Notes
- This is CRM-001 (Issue 1 of 14) in Wave 1 of the CRM Pipeline feature. It runs in parallel with CRM-002 and CRM-003.
- CRM-004 (CRUD API endpoints for prospects) and CRM-005 (meeting record endpoints) depend on the models and DTOs created here.
- The `stage` pipeline values (`lead`, `contacted`, `qualified`, `proposal`, `negotiation`, `won`, `lost`) represent a standard sales pipeline. Future issues may add custom pipeline stages.
- `estimated_value` uses `ge=0` (not `gt=0`) unlike `amount` in transactions, because a prospect deal can legitimately have $0 estimated value (e.g., partnership, pro-bono).
- No UI components are created in this issue — it is backend-only (data model layer), so no E2E test is needed.
- The `source` field is a free-form string (not a Literal) to allow flexibility in tracking where prospects come from without requiring schema changes.
