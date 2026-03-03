# Feature: Document Entity CRUD Backend

## Metadata
issue_number: `81`
adw_id: `95deee5d`
issue_json: ``

## Feature Description
Create the Document entity with full backend CRUD and file upload support for RestaurantOS. A Document represents any legal or administrative artifact — contracts, permits, invoices, licenses. Documents can be linked to a person (person_id FK) and have expiration dates with automatic status calculation (valid, expiring_soon, expired). File upload support is required via multipart/form-data. This entity is part of Wave 2 (Foundation Extended Entities) and is a building block for composed modules: Contracts = Person + Document + Event, Permits = Document + Event, Payments = Event + Document.

## User Story
As a restaurant administrator
I want to manage documents (contracts, permits, invoices, licenses) with file uploads and expiration tracking
So that I can keep all legal and administrative artifacts organized, linked to relevant persons, and be alerted when documents are expiring

## Problem Statement
Restaurants need to track legal and administrative documents (contracts, permits, licenses, invoices) with metadata including issue dates, expiration dates, and linked persons. There is currently no way to store document records, upload files, or track expiration status in the RestaurantOS system.

## Solution Statement
Implement a full backend CRUD for the Document entity following the established RestaurantOS Clean Architecture pattern (model → DTO → repository → service → routes). The solution includes: SQL migration for the `document` table with person FK, SQLAlchemy model, Pydantic DTOs with computed `expiration_status` field, repository with expiring-documents query, service with business logic for expiration status calculation and file upload handling, and REST routes with JWT authentication. File upload uses FastAPI's `UploadFile` with `multipart/form-data` for the create endpoint. The document entity uses `ON DELETE SET NULL` for person_id (unlike other entities that use CASCADE on restaurant_id) because deleting a person should not delete their associated documents.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/main.py` — Register the document router here (add import and `app.include_router`)
- `apps/Server/src/models/__init__.py` — Add `Document` to model exports
- `apps/Server/src/models/resource.py` — Reference for SQLAlchemy model pattern (UUID PK, restaurant_id FK, timestamps)
- `apps/Server/src/interface/resource_dto.py` — Reference for DTO pattern with computed fields (`model_validator` for `is_low_stock` → same pattern for `expiration_status`)
- `apps/Server/src/repository/resource_repository.py` — Reference for repository pattern (CRUD, type filter, specialized query)
- `apps/Server/src/core/services/resource_service.py` — Reference for service pattern (restaurant access check, business logic, singleton)
- `apps/Server/src/adapter/rest/resource_routes.py` — Reference for routes pattern (error handling, `_to_response` helper, specialized endpoints before parameterized ones)
- `apps/Server/src/adapter/rest/dependencies.py` — `get_current_user` and `get_db` dependency injection
- `apps/Server/src/repository/restaurant_repository.py` — `get_user_restaurant_role` for authorization checks
- `apps/Server/src/config/database.py` — `Base` for SQLAlchemy model inheritance
- `apps/Server/tests/test_resource_model.py` — Reference for DTO/model unit test patterns
- `apps/Server/tests/test_resource_api.py` — Reference for API endpoint test patterns
- `apps/Server/database/create_person_table.sql` — Reference for SQL migration pattern
- `apps/Server/requirements.txt` — Verify `python-multipart` is already installed (it is)
- `app_docs/feature-a692d2db-restaurant-multi-tenant-entity.md` — Restaurant multi-tenant scoping docs
- `app_docs/feature-14633eae-person-entity-crud-backend.md` — Person entity docs (person_id FK dependency)
- `app_docs/feature-8d28116a-resource-entity-crud-backend.md` — Resource entity docs (closest pattern to follow)

### New Files
- `apps/Server/database/create_document_table.sql` — SQL migration for the document table
- `apps/Server/src/models/document.py` — SQLAlchemy Document model
- `apps/Server/src/interface/document_dto.py` — Pydantic DTOs (Create, Update, Response)
- `apps/Server/src/repository/document_repository.py` — Document repository with CRUD and expiring query
- `apps/Server/src/core/services/document_service.py` — Document service with expiration logic and file upload
- `apps/Server/src/adapter/rest/document_routes.py` — REST API routes for documents
- `apps/Server/tests/test_document_model.py` — DTO and model unit tests
- `apps/Server/tests/test_document_api.py` — API endpoint integration tests

## Implementation Plan
### Phase 1: Foundation
Create the database migration SQL and SQLAlchemy model. The document table needs UUID PK, restaurant_id FK (CASCADE), person_id FK (SET NULL), type, file_url, issue_date, expiration_date, description, and timestamps. Indexes on restaurant_id, type, expiration_date, and person_id.

### Phase 2: Core Implementation
Build the Pydantic DTOs with computed `expiration_status` field using `model_validator`, the repository with CRUD operations plus `get_expiring()` for expiration alerts, and the service layer with restaurant-scoped authorization, expiration status calculation, and file upload handling. The create endpoint accepts `multipart/form-data` using FastAPI's `UploadFile` and `Form` fields. File storage stores file to a local `uploads/documents/` directory and records the relative URL.

### Phase 3: Integration
Register the document router in `main.py`, add `Document` to the models `__init__.py`, and create comprehensive tests covering DTO validation, computed fields, and API endpoints.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create SQL Migration
- Create `apps/Server/database/create_document_table.sql`
- Define the `document` table with columns: `id` (UUID PK), `restaurant_id` (UUID NOT NULL FK to restaurant with ON DELETE CASCADE), `type` (VARCHAR(100) NOT NULL), `file_url` (TEXT nullable), `issue_date` (DATE nullable), `expiration_date` (DATE nullable), `person_id` (UUID nullable FK to person with ON DELETE SET NULL), `description` (TEXT nullable), `created_at` (TIMESTAMP WITH TIME ZONE DEFAULT NOW()), `updated_at` (TIMESTAMP WITH TIME ZONE DEFAULT NOW())
- Create indexes: `idx_document_restaurant` on `restaurant_id`, `idx_document_type` on `type`, `idx_document_expiration` on `expiration_date`, `idx_document_person` on `person_id`
- Create trigger `update_document_updated_at` using `update_updated_at_column()` function
- Add comment header: `-- Document Entity Table` and `-- RestaurantOS Wave 2: ROS-004`

### Step 2: Create SQLAlchemy Model
- Create `apps/Server/src/models/document.py`
- Define `Document(Base)` class with `__tablename__ = "document"`
- Map all columns following the Resource model pattern: UUID PK with `default=uuid.uuid4`, `restaurant_id` FK to `restaurant.id`, `person_id` FK to `person.id` (nullable), `type` as String(100), `file_url` as String (nullable), `issue_date` as Date (nullable), `expiration_date` as Date (nullable), `description` as String (nullable), timestamps with `DateTime(timezone=True)`
- Import `Date` from `sqlalchemy` for date columns
- Add `__repr__()` method returning `<Document(id=..., type=..., restaurant_id=...)>`
- Add `Document` to `apps/Server/src/models/__init__.py` imports and `__all__` list

### Step 3: Create Pydantic DTOs
- Create `apps/Server/src/interface/document_dto.py`
- Define `DocumentCreateDTO(BaseModel)`:
  - `restaurant_id: UUID` (required)
  - `type: str = Field(..., min_length=1, max_length=100)` (required)
  - `issue_date: Optional[date] = None`
  - `expiration_date: Optional[date] = None`
  - `person_id: Optional[UUID] = None`
  - `description: Optional[str] = None`
- Define `DocumentUpdateDTO(BaseModel)` with all fields optional:
  - `type: Optional[str] = Field(None, min_length=1, max_length=100)`
  - `issue_date: Optional[date] = None`
  - `expiration_date: Optional[date] = None`
  - `person_id: Optional[UUID] = None`
  - `description: Optional[str] = None`
- Define `DocumentResponseDTO(BaseModel)`:
  - All fields from model plus computed `expiration_status: str`
  - Use `@model_validator(mode="before")` to compute `expiration_status`:
    - If `expiration_date` is None → `"valid"` (no expiration set)
    - If `expiration_date` < today → `"expired"`
    - If `expiration_date` <= today + 30 days → `"expiring_soon"`
    - Otherwise → `"valid"`
  - Set `model_config = {"from_attributes": True}`
- Add a `@model_validator` on `DocumentCreateDTO` to validate that if both `issue_date` and `expiration_date` are provided, `expiration_date` must be after `issue_date`

### Step 4: Create Repository
- Create `apps/Server/src/repository/document_repository.py`
- Define `DocumentRepository` class with methods:
  - `create(db, restaurant_id, doc_type, file_url, issue_date, expiration_date, person_id, description)` → `Document`
  - `get_by_id(db, document_id)` → `Optional[Document]`
  - `get_by_restaurant(db, restaurant_id, type_filter=None)` → `list[Document]`
  - `update(db, document)` → `Document`
  - `delete(db, document_id)` → `bool`
  - `get_expiring(db, restaurant_id, days_ahead=30)` → `list[Document]` — query documents where `expiration_date` is between today and today + `days_ahead` days
- Follow the Resource repository pattern with print logging
- Create singleton: `document_repository = DocumentRepository()`

### Step 5: Create Service
- Create `apps/Server/src/core/services/document_service.py`
- Define `DocumentService` class with:
  - `_check_restaurant_access(db, user_id, restaurant_id)` — same pattern as ResourceService
  - `create_document(db, user_id, data: DocumentCreateDTO, file_url: Optional[str] = None)` → `Document`
    - Check restaurant access
    - Validate expiration_date > issue_date if both provided (done at DTO level, but double-check at service)
    - Call repository create with all fields
    - Log warning if document has an expiration_date within 30 days
  - `get_documents(db, user_id, restaurant_id, type_filter=None, expiration_status_filter=None)` → `list[Document]`
    - Check restaurant access
    - Get documents from repository
    - If `expiration_status_filter` is provided, post-filter by computed expiration status
  - `get_document(db, user_id, document_id)` → `Document`
  - `update_document(db, user_id, document_id, data: DocumentUpdateDTO)` → `Document`
  - `delete_document(db, user_id, document_id)` → `bool`
  - `get_expiring_documents(db, user_id, restaurant_id, days_ahead=30)` → `list[Document]`
  - `save_upload_file(file: UploadFile)` → `str` — save file to `uploads/documents/` directory, return relative path as file_url. Generate unique filename using UUID to prevent collisions.
- Create singleton: `document_service = DocumentService()`

### Step 6: Create REST Routes
- Create `apps/Server/src/adapter/rest/document_routes.py`
- Define `router = APIRouter(prefix="/api/documents", tags=["Documents"])`
- Define `_to_response(document)` helper for converting model to ResponseDTO (like Resource routes)
- Implement endpoints:
  - `POST /api/documents` (multipart/form-data) — accepts `UploadFile` for file and `Form(...)` fields for metadata. Use `File(None)` for optional file upload. Parse form fields to `DocumentCreateDTO`. Return 201.
  - `GET /api/documents/expiring` — get expiring documents for a restaurant (before parameterized routes). Query params: `restaurant_id`, `days_ahead` (default 30).
  - `GET /api/documents` — list documents with optional filters: `restaurant_id` (required), `type` (optional), `expiration_status` (optional: valid, expiring_soon, expired).
  - `GET /api/documents/{document_id}` — get document by ID
  - `PUT /api/documents/{document_id}` — update document metadata (JSON body, not multipart)
  - `DELETE /api/documents/{document_id}` — delete document, return 204
- All endpoints require `get_current_user` dependency
- Error handling: `PermissionError` → 403, `ValueError` → 404

### Step 7: Register Router
- Add `from src.adapter.rest.document_routes import router as document_router` to `apps/Server/main.py`
- Add `app.include_router(document_router)` after the resource_router
- Add `print("INFO [Main]: Document router registered")`

### Step 8: Create Unit Tests (DTO/Model)
- Create `apps/Server/tests/test_document_model.py`
- Test `DocumentCreateDTO`:
  - Valid creation with all fields
  - Valid creation with required fields only (restaurant_id, type)
  - Missing required fields rejected
  - Empty type rejected (min_length=1)
  - Type too long rejected (max_length=100)
  - expiration_date before issue_date rejected
  - Valid when only issue_date provided
  - Valid when only expiration_date provided
- Test `DocumentUpdateDTO`:
  - Single field update
  - Empty update (all None)
  - Type too long rejected
- Test `DocumentResponseDTO`:
  - From mock model attributes
  - `expiration_status` = "valid" when no expiration_date
  - `expiration_status` = "valid" when expiration_date > 30 days ahead
  - `expiration_status` = "expiring_soon" when expiration_date <= 30 days ahead
  - `expiration_status` = "expired" when expiration_date is in the past
- Test `Document` model:
  - `__repr__` method
  - `__tablename__` == "document"
- Follow test naming pattern: `test_document_[operation]_[scenario]()`
- Include `print("INFO [TestDocument]: test_name - PASSED")` at end of each test

### Step 9: Create API Integration Tests
- Create `apps/Server/tests/test_document_api.py`
- Mock helpers: `create_mock_user()`, `create_mock_document()`, `get_mock_db()`
- Override `get_current_user` and `get_db` dependencies
- Test sections:
  - Create: success, unauthenticated (no mock override), no restaurant access (PermissionError)
  - List: success with filters, unauthenticated, no access
  - Get by ID: success, not found (ValueError), unauthenticated, no access
  - Update: success, not found, unauthenticated, no access
  - Delete: success, not found, unauthenticated, no access
  - Expiring: success, unauthenticated, no access
- All tests use `@pytest.mark.asyncio` decorator
- Use `httpx.AsyncClient` with `ASGITransport` for async testing

### Step 10: Run Validation Commands
- Run `cd apps/Server && python -m pytest tests/ -v` to validate all tests pass with zero regressions
- Run `cd apps/Server && python -c "from src.models.document import Document; print('Document model imports OK')"` to validate model import
- Run `cd apps/Server && python -c "from src.adapter.rest.document_routes import router; print('Document routes import OK')"` to validate routes import

## Testing Strategy
### Unit Tests
- `DocumentCreateDTO` validation: required fields, optional fields, field constraints (min/max length), date validation (expiration_date > issue_date)
- `DocumentUpdateDTO` validation: partial updates, empty update, field constraints
- `DocumentResponseDTO` computed fields: `expiration_status` calculation for all states (valid, expiring_soon, expired, no expiration)
- `Document` model: tablename, repr

### Edge Cases
- Document with no expiration_date (expiration_status should be "valid")
- Document with expiration_date exactly 30 days in the future (should be "expiring_soon")
- Document with expiration_date exactly today (should be "expiring_soon")
- Document with expiration_date yesterday (should be "expired")
- Document with issue_date but no expiration_date
- Document with expiration_date but no issue_date
- Document with expiration_date before issue_date (should be rejected by DTO validator)
- Document with no person_id (standalone document)
- Document with person_id linking to an existing person
- File upload with no file (file_url should be None)
- Deleting a person linked to a document (person_id should become NULL, document should persist)

## Acceptance Criteria
- Document SQL migration creates the table with all specified columns, indexes, and trigger
- SQLAlchemy model correctly maps all columns including Date fields
- DTOs validate required fields, enforce constraints, and compute expiration_status
- Repository performs CRUD operations and supports get_expiring query
- Service enforces restaurant-scoped authorization via user_restaurants membership
- REST routes support all CRUD operations with JWT authentication
- POST endpoint supports multipart/form-data for file upload
- GET list endpoint supports type and expiration_status query filters
- GET /expiring endpoint returns documents expiring within N days
- Computed expiration_status correctly classifies: "valid" (>30 days or no date), "expiring_soon" (≤30 days), "expired" (past)
- All unit tests pass for DTO validation and computed fields
- All API integration tests pass for success and error cases
- All existing tests continue to pass (zero regressions)
- Document router is registered in main.py and logs registration on startup

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/test_document_model.py -v` — Run document DTO/model unit tests
- `cd apps/Server && python -m pytest tests/test_document_api.py -v` — Run document API endpoint tests
- `cd apps/Server && python -m pytest tests/ -v` — Run ALL Server tests to verify zero regressions
- `cd apps/Server && python -c "from src.models.document import Document; print('Document model imports OK')"` — Verify model import chain
- `cd apps/Server && python -c "from src.adapter.rest.document_routes import router; print('Document routes import OK')"` — Verify routes import chain

## Notes
- **File upload**: `python-multipart` is already in `requirements.txt`. No new dependencies needed.
- **File storage**: For this wave, files are stored locally in `uploads/documents/`. A future wave may migrate to cloud storage (S3, Supabase Storage). The service layer abstracts file handling to make this migration easy.
- **Expiration alerts**: This wave only adds the data model and `get_expiring` query. Wave 6 will wire in the actual alert automation. The `expiration_status` computed field and `GET /expiring` endpoint prepare for that integration.
- **ON DELETE SET NULL for person_id**: Unlike restaurant_id (CASCADE), person_id uses SET NULL because deleting a person should preserve their documents — the document remains as an independent artifact.
- **No enum for document type**: The issue specifies type as free-text VARCHAR(100) with suggested values (contrato, permiso, factura, licencia, factura_proveedor). This is intentional for flexibility — new document types can be added without code changes.
- **Backend only**: No frontend components, no E2E tests needed for this wave. Wave 4 will build the Document Management frontend page.
- **Parallel execution**: This issue runs in parallel with ROS-005 (Event entity) and ROS-006 (Inventory Movement entity). No shared files conflict except `main.py` router registration and `models/__init__.py`.
