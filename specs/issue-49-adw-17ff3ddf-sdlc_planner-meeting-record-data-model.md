# Feature: Meeting Record Data Model

## Metadata
issue_number: `49`
adw_id: `17ff3ddf`
issue_json: ``

## Feature Description
Create the data model for storing processed meeting records linked to CRM prospects. Each meeting record stores the original transcript reference, a structured summary, extracted action items, participant list, and a downloadable formatted HTML output. Multiple meetings can be linked to a single prospect, enabling a complete interaction history. This is CRM-003 in Wave 1 (Foundation — Data Models & Backend API), running in parallel with CRM-001 (Prospect Data Model) and CRM-002 (Pipeline Stage Configuration).

## User Story
As a CRM user
I want meeting records stored and linked to prospects
So that I can track all meeting interactions, summaries, action items, and participants for each prospect in my pipeline

## Problem Statement
The CRM pipeline currently has prospect tracking and pipeline stage management but no way to store processed meeting data. Meeting transcripts need to be processed into structured records (summary, action items, participants) and linked to prospects. Without this data model, the transcript processing pipeline (Wave 3) has no storage target, and CRUD API endpoints (CRM-005) have no model to operate on.

## Solution Statement
Create a `meeting_records` PostgreSQL table, a `MeetingRecord` SQLAlchemy model, and Pydantic DTOs (Create, Update, Response, ListResponse, Filter) following the exact patterns established by the Prospect and StageTransition models. The meeting record will be entity-scoped via `entity_id` and linked to a prospect via `prospect_id`. It stores:
- `transcript_ref`: reference to the original transcript file/URL
- `summary`: structured text summary of the meeting
- `action_items`: JSON array of extracted action items (stored as Text, serialized/deserialized as JSON in the DTO layer)
- `participants`: JSON array of participant names/roles (stored as Text, serialized/deserialized as JSON in the DTO layer)
- `html_output`: formatted HTML content ready for download
- `meeting_date`: when the meeting occurred
- `title`: human-readable meeting title
- Standard audit columns (`created_at`, `updated_at`, `is_active`)

## Relevant Files
Use these files to implement the feature:

- `apps/Server/database/schema.sql` — Append the `meeting_records` table definition following the existing table pattern (constraints, indexes, trigger)
- `apps/Server/src/models/prospect.py` — Reference for entity-scoped model pattern with typed columns and `__repr__`
- `apps/Server/src/models/stage_transition.py` — Reference for prospect-linked model pattern with FK cascade rules
- `apps/Server/src/models/__init__.py` — Register the new `MeetingRecord` model export
- `apps/Server/src/interface/prospect_dto.py` — Reference for the 5-DTO pattern (Create, Update, Response, ListResponse, Filter)
- `apps/Server/src/interface/stage_transition_dto.py` — Reference for prospect-linked DTO pattern
- `apps/Server/tests/test_prospect_model.py` — Reference for unit test pattern (DTO validation, model repr, MagicMock for ResponseDTO)
- `apps/Server/src/config/database.py` — Base class import for SQLAlchemy model
- `app_docs/feature-57f962c3-prospect-data-model.md` — Prospect data model documentation (conditional doc: read when adding meeting records or other prospect-related entities)
- `app_docs/feature-eb19b5cd-pipeline-stage-configuration.md` — Pipeline stage configuration documentation (conditional doc: read when working with stage-related tables)

### New Files
- `apps/Server/src/models/meeting_record.py` — SQLAlchemy model for the `meeting_records` table
- `apps/Server/src/interface/meeting_record_dto.py` — Pydantic DTOs (Create, Update, Response, ListResponse, Filter)
- `apps/Server/tests/test_meeting_record_model.py` — Unit tests for MeetingRecord model and DTOs

## Implementation Plan
### Phase 1: Foundation
Define the database schema for the `meeting_records` table in `schema.sql`, including all columns, constraints, foreign keys, indexes, and the `updated_at` trigger. This establishes the storage layer that the SQLAlchemy model maps to.

### Phase 2: Core Implementation
Create the SQLAlchemy `MeetingRecord` model mirroring the DB schema, and the Pydantic DTOs for API request/response validation. The model follows the Prospect pattern (entity-scoped, prospect-linked, soft-deletable). Action items and participants are stored as `Text` columns (JSON strings) in the database, with the DTOs accepting/returning Python list types and handling serialization.

### Phase 3: Integration
Register the model in `src/models/__init__.py` so it is available throughout the application. Write comprehensive unit tests validating DTO field constraints, model table name, and ORM-to-DTO mapping. Run the full test suite to confirm zero regressions.

## Step by Step Tasks

### Step 1: Add `meeting_records` table to database schema
- Open `apps/Server/database/schema.sql`
- Append a new section at the end for `meeting_records` table
- Define columns:
  - `id UUID PRIMARY KEY DEFAULT uuid_generate_v4()`
  - `entity_id UUID NOT NULL` — FK to `entities(id)` ON DELETE CASCADE
  - `prospect_id UUID NOT NULL` — FK to `prospects(id)` ON DELETE CASCADE
  - `title VARCHAR(500) NOT NULL` — human-readable meeting title
  - `transcript_ref VARCHAR(1000)` — nullable reference to original transcript file/URL
  - `summary TEXT` — nullable structured summary of the meeting
  - `action_items TEXT` — nullable JSON-serialized array of action items
  - `participants TEXT` — nullable JSON-serialized array of participant names/roles
  - `html_output TEXT` — nullable formatted HTML for download
  - `meeting_date DATE` — nullable date of the meeting
  - `is_active BOOLEAN DEFAULT TRUE` — soft delete flag
  - `created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()`
  - `updated_at TIMESTAMP WITH TIME ZONE`
- Add constraints: FK constraints with named `CONSTRAINT fk_meeting_records_*` format
- Add indexes: `entity_id`, `prospect_id`, `is_active`, composite `(entity_id, prospect_id)`
- Add `updated_at` trigger using the existing `update_updated_at_column()` function

### Step 2: Create SQLAlchemy `MeetingRecord` model
- Create `apps/Server/src/models/meeting_record.py`
- Import pattern: `uuid`, `datetime`, `Optional`, `sqlalchemy` types, `UUID` dialect, `Base`
- Define `MeetingRecord(Base)` class with `__tablename__ = "meeting_records"`
- Map all columns with Python type annotations matching the schema
- Use `ForeignKey("entities.id", ondelete="CASCADE")` for `entity_id`
- Use `ForeignKey("prospects.id", ondelete="CASCADE")` for `prospect_id`
- Index `entity_id`, `prospect_id`, and `is_active`
- Add `__repr__` returning `<MeetingRecord(id=..., title=..., prospect_id=...)>`

### Step 3: Register model in `__init__.py`
- Edit `apps/Server/src/models/__init__.py`
- Add `from src.models.meeting_record import MeetingRecord`
- Add `"MeetingRecord"` to `__all__` list

### Step 4: Create Pydantic DTOs
- Create `apps/Server/src/interface/meeting_record_dto.py`
- Define 5 DTOs:
  - `MeetingRecordCreateDTO` — required: `entity_id`, `prospect_id`, `title`; optional: `transcript_ref`, `summary`, `action_items` (List[str]), `participants` (List[str]), `html_output`, `meeting_date`
  - `MeetingRecordUpdateDTO` — all fields optional (no `entity_id`, no `prospect_id`); includes `title`, `transcript_ref`, `summary`, `action_items`, `participants`, `html_output`, `meeting_date`, `is_active`
  - `MeetingRecordResponseDTO` — all fields with `model_config = {"from_attributes": True}`; `action_items` and `participants` as `Optional[str]` (raw JSON text from DB, client parses)
  - `MeetingRecordListResponseDTO` — `meeting_records: List[MeetingRecordResponseDTO]` + `total: int`
  - `MeetingRecordFilterDTO` — optional filters: `prospect_id`, `is_active`, `meeting_date_from`, `meeting_date_to`
- Use `Field(...)` for required fields, `Field(None, ...)` for optional
- Add `min_length=1, max_length=500` on `title`
- Add `max_length=1000` on `transcript_ref`

### Step 5: Write unit tests for model and DTOs
- Create `apps/Server/tests/test_meeting_record_model.py`
- Follow `test_prospect_model.py` pattern with `print("INFO [TestMeetingRecord]: ... - PASSED")` on each test
- Test categories:
  - **MeetingRecordCreateDTO**: valid with all fields, valid minimal (only required), empty title rejected, title too long rejected
  - **MeetingRecordUpdateDTO**: partial update, empty (all None)
  - **MeetingRecordResponseDTO**: from mock model via `model_validate` with `from_attributes=True`
  - **MeetingRecordFilterDTO**: defaults all None, with specific values
  - **MeetingRecordListResponseDTO**: list with total count
  - **MeetingRecord model**: `__tablename__` check, `__repr__` check

### Step 6: Run validation commands
- Run full server test suite to confirm zero regressions
- Verify all new tests pass

## Testing Strategy
### Unit Tests
- DTO field validation: required fields, optional defaults, string length constraints, type enforcement
- DTO `model_validate` from mock ORM objects (tests `from_attributes=True` config)
- Model `__tablename__` and `__repr__` correctness
- Create, Update, Response, Filter, and ListResponse DTOs all covered

### Edge Cases
- Empty `title` string rejected by `min_length=1`
- `title` exceeding 500 characters rejected by `max_length=500`
- `transcript_ref` exceeding 1000 characters rejected by `max_length=1000`
- `action_items` and `participants` as empty lists accepted in CreateDTO
- `MeetingRecordUpdateDTO` with no fields set (all None) accepted for partial updates
- `meeting_date` as None accepted (meeting date may be unknown at creation time)
- `MeetingRecordFilterDTO` with all None defaults (no filtering)
- Response DTO handles `updated_at=None` (new records not yet updated)

## Acceptance Criteria
- `meeting_records` table definition exists in `schema.sql` with all columns, constraints, indexes, and trigger
- `MeetingRecord` SQLAlchemy model exists in `src/models/meeting_record.py` with correct column mappings and foreign keys
- `MeetingRecord` is exported from `src/models/__init__.py`
- Five Pydantic DTOs exist in `src/interface/meeting_record_dto.py`: Create, Update, Response, ListResponse, Filter
- All DTOs follow established patterns (Field validators, from_attributes config, description strings)
- Unit tests cover all DTOs and model basics with 100% pass rate
- Full server test suite passes with zero regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest tests/test_meeting_record_model.py -v` — Run meeting record unit tests to validate DTOs and model
- `cd apps/Server && uv run pytest` — Run full Server test suite to validate zero regressions

## Notes
- This is a **backend-only data model** feature — no UI components, no API endpoints, no service/repository layer. CRM-005 will add the CRUD API endpoints that consume this model and DTOs.
- `action_items` and `participants` are stored as `Text` (JSON strings) in the database rather than using PostgreSQL JSONB. This keeps the model simple and avoids SQLAlchemy JSON dialect complexity. The CreateDTO accepts `List[str]` for ergonomic API input; the service layer (CRM-005) will handle JSON serialization before persisting. The ResponseDTO returns the raw `str` as stored.
- `transcript_ref` is intentionally a string reference (file path or URL) rather than storing the full transcript text, keeping the table lean. The transcript pipeline (Wave 3) will populate this field.
- `html_output` stores the complete formatted HTML so it can be served directly for download without re-rendering.
- `meeting_date` is `DATE` (not `DATETIME`) since meeting-level precision (not minute-level) is sufficient for tracking.
- No new libraries are required.
