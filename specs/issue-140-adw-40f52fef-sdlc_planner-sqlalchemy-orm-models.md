# Feature: Legal Desk SQLAlchemy ORM Models (11 Models)

## Metadata
issue_number: `140`
adw_id: `40f52fef`
issue_json: ``

## Feature Description
Create 11 SQLAlchemy ORM model files mapping to the Legal Desk `ld_` database tables. These models define the Python-level data access interface that Wave 2 repositories will use for database queries. Each model inherits from the shared `Base` class, declares an explicit `__tablename__`, typed columns matching the SQL schema, and relationship definitions connecting related models. This is Wave 1 (Foundation) of the Legal Desk module — Issue LD-003.

## User Story
As a developer building the Legal Desk module
I want SQLAlchemy ORM models for all 11 `ld_` tables
So that Wave 2 repositories can query, create, and relate Legal Desk entities through Python objects

## Problem Statement
The Legal Desk database schema (11 `ld_` tables) exists in SQL but has no corresponding Python ORM layer. Without models, repositories cannot perform typed queries, enforce relationships, or leverage SQLAlchemy's ORM capabilities for case management, specialist assignment, and pricing workflows.

## Solution Statement
Create 11 individual model files in `apps/Server/src/models/` following the existing project pattern (one class per file, `Base` inheritance, typed columns, `__repr__`). Each model maps 1:1 to its `ld_` table with columns matching the SQL schema exactly. Add `relationship()` definitions to enable navigation between related models (e.g., `LdCase.client` → `LdClient`). Register all models in `__init__.py`.

**Key difference from existing models:** Legal Desk uses `Integer` primary keys (SERIAL) instead of UUIDs, matching the SQL schema in `create_legaldesk_tables.sql`.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/src/config/database.py` — Provides the `Base` class and `get_db` dependency that all models inherit from
- `apps/Server/src/models/__init__.py` — Model registry; must be updated to import and export all 11 new models
- `apps/Server/src/models/event.py` — Reference pattern for model structure (Base inheritance, typed columns, `__repr__`)
- `apps/Server/src/models/category.py` — Reference pattern for Boolean columns and nullable fields
- `apps/Server/src/models/transaction.py` — Reference pattern for Numeric/Decimal columns and ForeignKey definitions
- `apps/Server/database/create_legaldesk_tables.sql` — The SQL schema defining all 11 `ld_` tables with exact column names, types, constraints, and foreign keys
- `app_docs/feature-de0cefbe-legaldesk-database-schema.md` — Legal Desk schema documentation for understanding table relationships

### New Files
- `apps/Server/src/models/ld_client.py` — `LdClient` model mapping to `ld_clients`
- `apps/Server/src/models/ld_specialist.py` — `LdSpecialist` model mapping to `ld_specialists`
- `apps/Server/src/models/ld_specialist_expertise.py` — `LdSpecialistExpertise` mapping to `ld_specialist_expertise`
- `apps/Server/src/models/ld_specialist_jurisdiction.py` — `LdSpecialistJurisdiction` mapping to `ld_specialist_jurisdictions`
- `apps/Server/src/models/ld_case.py` — `LdCase` mapping to `ld_cases`
- `apps/Server/src/models/ld_case_specialist.py` — `LdCaseSpecialist` mapping to `ld_case_specialists`
- `apps/Server/src/models/ld_case_deliverable.py` — `LdCaseDeliverable` mapping to `ld_case_deliverables`
- `apps/Server/src/models/ld_case_message.py` — `LdCaseMessage` mapping to `ld_case_messages`
- `apps/Server/src/models/ld_case_document.py` — `LdCaseDocument` mapping to `ld_case_documents`
- `apps/Server/src/models/ld_pricing_history.py` — `LdPricingHistory` mapping to `ld_pricing_history`
- `apps/Server/src/models/ld_specialist_score.py` — `LdSpecialistScore` mapping to `ld_specialist_scores`

## Implementation Plan
### Phase 1: Foundation
Create the two root entity models (`LdClient`, `LdSpecialist`) that have no foreign key dependencies on other Legal Desk tables. These are referenced by all downstream models.

### Phase 2: Core Implementation
Create the remaining 9 models in dependency order:
1. Specialist junction tables (`LdSpecialistExpertise`, `LdSpecialistJurisdiction`) — depend on `LdSpecialist`
2. `LdCase` — depends on `LdClient`
3. Case-related tables (`LdCaseSpecialist`, `LdCaseDeliverable`, `LdCaseMessage`, `LdCaseDocument`, `LdPricingHistory`, `LdSpecialistScore`) — depend on `LdCase` and/or `LdSpecialist`

### Phase 3: Integration
Register all 11 models in `__init__.py` and validate with import tests and pytest.

## Step by Step Tasks

### Step 1: Create LdClient model
- Create `apps/Server/src/models/ld_client.py`
- Map to `ld_clients` table
- Columns: `id` (Integer PK), `name` (String(255), NOT NULL), `client_type` (String(50), NOT NULL, default='company'), `contact_email` (String(255)), `contact_phone` (String(100)), `country` (String(100)), `industry` (String(100)), `notes` (Text), `is_active` (Boolean, default=True), `created_at` (DateTime(timezone=True)), `updated_at` (DateTime(timezone=True))
- Relationships: `cases` → list of `LdCase`
- Add `__repr__` method

### Step 2: Create LdSpecialist model
- Create `apps/Server/src/models/ld_specialist.py`
- Map to `ld_specialists` table
- Columns: `id` (Integer PK), `full_name` (String(255), NOT NULL), `email` (String(255), unique, NOT NULL), `phone` (String(100)), `years_experience` (Integer, default=0), `hourly_rate` (Numeric(10,2)), `currency` (String(10), default='EUR'), `max_concurrent_cases` (Integer, default=5), `current_workload` (Integer, default=0), `overall_score` (Numeric(3,2), default=0.00), `is_active` (Boolean, default=True), `created_at`, `updated_at`
- Relationships: `expertise` → list of `LdSpecialistExpertise`, `jurisdictions` → list of `LdSpecialistJurisdiction`, `case_assignments` → list of `LdCaseSpecialist`, `scores` → list of `LdSpecialistScore`
- Add `__repr__` method

### Step 3: Create LdSpecialistExpertise model
- Create `apps/Server/src/models/ld_specialist_expertise.py`
- Map to `ld_specialist_expertise` table
- Columns: `id` (Integer PK), `specialist_id` (Integer, FK → ld_specialists.id, CASCADE, NOT NULL), `legal_domain` (String(100), NOT NULL), `proficiency_level` (String(50), default='intermediate'), `years_in_domain` (Integer, default=0), `created_at`
- UniqueConstraint on `(specialist_id, legal_domain)`
- Add `__repr__` method

### Step 4: Create LdSpecialistJurisdiction model
- Create `apps/Server/src/models/ld_specialist_jurisdiction.py`
- Map to `ld_specialist_jurisdictions` table
- Columns: `id` (Integer PK), `specialist_id` (Integer, FK → ld_specialists.id, CASCADE, NOT NULL), `country` (String(100), NOT NULL), `region` (String(100)), `is_primary` (Boolean, default=False), `created_at`
- UniqueConstraint on `(specialist_id, country, region)`
- Add `__repr__` method

### Step 5: Create LdCase model
- Create `apps/Server/src/models/ld_case.py`
- Map to `ld_cases` table
- Columns: `id` (Integer PK), `case_number` (String(20), unique, NOT NULL), `title` (String(500), NOT NULL), `description` (Text), `client_id` (Integer, FK → ld_clients.id, CASCADE, NOT NULL), `legal_domain` (String(100), NOT NULL), `complexity` (String(50), default='medium'), `priority` (String(50), default='medium'), `status` (String(50), default='new'), `budget` (Numeric(15,2)), `estimated_cost` (Numeric(15,2)), `final_quote` (Numeric(15,2)), `margin_percentage` (Numeric(5,2)), `deadline` (Date), `ai_classification` (JSONB), `created_at`, `updated_at`
- Relationships: `client` → `LdClient`, `specialists` → list of `LdCaseSpecialist`, `deliverables` → list of `LdCaseDeliverable`, `messages` → list of `LdCaseMessage`, `documents` → list of `LdCaseDocument`, `pricing_history` → list of `LdPricingHistory`, `scores` → list of `LdSpecialistScore`
- Add `__repr__` method

### Step 6: Create LdCaseSpecialist model
- Create `apps/Server/src/models/ld_case_specialist.py`
- Map to `ld_case_specialists` table
- Columns: `id` (Integer PK), `case_id` (Integer, FK → ld_cases.id, CASCADE, NOT NULL), `specialist_id` (Integer, FK → ld_specialists.id, CASCADE, NOT NULL), `role` (String(50), default='assigned'), `status` (String(50), default='pending'), `proposed_fee` (Numeric(15,2)), `agreed_fee` (Numeric(15,2)), `fee_currency` (String(10), default='EUR'), `assigned_at` (DateTime(timezone=True)), `responded_at` (DateTime(timezone=True))
- Relationships: `specialist` → `LdSpecialist`
- Add `__repr__` method

### Step 7: Create LdCaseDeliverable model
- Create `apps/Server/src/models/ld_case_deliverable.py`
- Map to `ld_case_deliverables` table
- Columns: `id` (Integer PK), `case_id` (Integer, FK → ld_cases.id, CASCADE, NOT NULL), `specialist_id` (Integer, FK → ld_specialists.id, SET NULL), `title` (String(500), NOT NULL), `description` (Text), `status` (String(50), default='pending'), `due_date` (Date), `completed_at` (DateTime(timezone=True)), `created_at`, `updated_at`
- Relationships: `specialist` → `LdSpecialist`
- Add `__repr__` method

### Step 8: Create LdCaseMessage model
- Create `apps/Server/src/models/ld_case_message.py`
- Map to `ld_case_messages` table
- Columns: `id` (Integer PK), `case_id` (Integer, FK → ld_cases.id, CASCADE, NOT NULL), `sender_type` (String(50), NOT NULL), `sender_name` (String(255)), `message` (Text, NOT NULL), `is_internal` (Boolean, default=False), `created_at`
- Add `__repr__` method

### Step 9: Create LdCaseDocument model
- Create `apps/Server/src/models/ld_case_document.py`
- Map to `ld_case_documents` table
- Columns: `id` (Integer PK), `case_id` (Integer, FK → ld_cases.id, CASCADE, NOT NULL), `file_name` (String(500), NOT NULL), `file_url` (String(1000), NOT NULL), `file_type` (String(100)), `file_size_bytes` (BigInteger), `uploaded_by` (String(255)), `created_at`
- Add `__repr__` method

### Step 10: Create LdPricingHistory model
- Create `apps/Server/src/models/ld_pricing_history.py`
- Map to `ld_pricing_history` table
- Columns: `id` (Integer PK), `case_id` (Integer, FK → ld_cases.id, CASCADE, NOT NULL), `action` (String(100), NOT NULL), `previous_amount` (Numeric(15,2)), `new_amount` (Numeric(15,2)), `currency` (String(10), default='EUR'), `changed_by` (String(255)), `notes` (Text), `created_at`
- Add `__repr__` method

### Step 11: Create LdSpecialistScore model
- Create `apps/Server/src/models/ld_specialist_score.py`
- Map to `ld_specialist_scores` table
- Columns: `id` (Integer PK), `specialist_id` (Integer, FK → ld_specialists.id, CASCADE, NOT NULL), `case_id` (Integer, FK → ld_cases.id, CASCADE, NOT NULL), `quality_score` (Numeric(3,2)), `teamwork_score` (Numeric(3,2)), `delivery_score` (Numeric(3,2)), `satisfaction_score` (Numeric(3,2)), `overall_score` (Numeric(3,2)), `feedback` (Text), `scored_at` (DateTime(timezone=True))
- Add `__repr__` method

### Step 12: Register all models in __init__.py
- Update `apps/Server/src/models/__init__.py` to import all 11 new models
- Add all model names to the `__all__` list
- Group Legal Desk imports together with a comment separator

### Step 13: Run validation commands
- Run pytest to confirm all models import without errors and no regressions
- Verify Python can import all models successfully

## Testing Strategy
### Unit Tests
- Import validation: Verify all 11 models can be imported from `src.models`
- Column validation: Spot-check that key columns exist with correct types (e.g., `LdCase.ai_classification` is JSONB, `LdSpecialist.hourly_rate` is Numeric)
- Relationship validation: Verify relationship attributes are defined on models
- `__repr__` validation: Ensure repr methods return expected format strings

### Edge Cases
- Models with no `updated_at` column (e.g., `LdCaseMessage`, `LdCaseDocument`, `LdPricingHistory`, `LdSpecialistScore`) should not define `onupdate`
- `LdSpecialistExpertise` unique constraint on `(specialist_id, legal_domain)` must be defined
- `LdSpecialistJurisdiction` unique constraint on `(specialist_id, country, region)` must be defined
- `LdCase.ai_classification` must use `JSONB` from `sqlalchemy.dialects.postgresql`
- `LdCaseDocument.file_size_bytes` must use `BigInteger` (not Integer) to match SQL `BIGINT`
- Foreign key `ondelete` actions must match SQL schema exactly (CASCADE vs SET NULL)

## Acceptance Criteria
- All 11 model files exist in `apps/Server/src/models/` with `ld_` prefix
- Each model class inherits from `Base` and sets `__tablename__` matching the SQL table name
- All columns match the SQL schema in `create_legaldesk_tables.sql` (names, types, nullability, defaults)
- Foreign keys reference correct tables with correct `ondelete` behavior
- Unique constraints match SQL schema (specialist_expertise, specialist_jurisdictions)
- Relationships are defined for navigating between related models
- All 11 models are registered in `__init__.py`
- `pytest` passes with zero failures
- All models can be imported via `from src.models import LdClient, LdCase, ...`

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -c "from src.models import LdClient, LdSpecialist, LdSpecialistExpertise, LdSpecialistJurisdiction, LdCase, LdCaseSpecialist, LdCaseDeliverable, LdCaseMessage, LdCaseDocument, LdPricingHistory, LdSpecialistScore; print('All 11 Legal Desk models imported successfully')"` — Verify all models import correctly
- `cd apps/Server && python -c "from src.models.ld_case import LdCase; assert LdCase.__tablename__ == 'ld_cases'; print('LdCase tablename OK')"` — Verify tablename mapping
- `cd apps/Server && python -c "from src.models.ld_case import LdCase; from sqlalchemy.dialects.postgresql import JSONB; assert isinstance(LdCase.ai_classification.type, JSONB); print('JSONB column OK')"` — Verify JSONB column type
- `cd apps/Server && uv run pytest` — Run Server tests to validate the feature works with zero regressions

## Notes
- Legal Desk models use `Integer` primary keys (SQL SERIAL) unlike existing models that use `UUID`. This matches the `create_legaldesk_tables.sql` schema.
- Relationships use `backref` for simple bidirectional navigation as shown in the issue example. The parent side (e.g., `LdCase`) defines `relationship()` with `backref` to auto-create the reverse attribute on the child (e.g., `LdCaseSpecialist.case`).
- No new libraries are needed — all imports (`Column`, `Integer`, `String`, `Numeric`, `JSONB`, `relationship`, etc.) are already available from SQLAlchemy which is in `requirements.txt`.
- This issue runs in parallel with LD-001 (schema SQL), LD-002, LD-004, LD-005. No blocking dependencies.
- Wave 2 repositories will import these models directly for database queries.
