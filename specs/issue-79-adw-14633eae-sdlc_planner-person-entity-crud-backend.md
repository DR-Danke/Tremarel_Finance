# Feature: Person Entity Data Model & CRUD Backend

## Metadata
issue_number: `79`
adw_id: `14633eae`
issue_json: ``

## Feature Description
Create the `person` database table and full backend CRUD for the RestaurantOS module. A Person represents employees, suppliers, or owners within a restaurant. This is the second of four universal entities in Wave 1 (Foundation Core Entities) and is referenced by Documents (owner), Events (responsible), and Inventory Movements (performer) in later waves. The Person entity is scoped to a restaurant via `restaurant_id` for multi-tenant isolation. This is a backend-only feature — no UI components are included.

## User Story
As a restaurant manager or owner
I want to manage people (employees, suppliers, owners) associated with my restaurant
So that I can track who is involved in restaurant operations and reference them in documents, events, and inventory movements

## Problem Statement
The RestaurantOS module needs a Person entity to represent the people involved in restaurant operations. Without it, downstream features like Documents (which need an owner), Events (which need a responsible person), and Inventory Movements (which need a performer) cannot be built. Person is one of the four core entities required before any composed module (Contracts, Permits, Checklists, Inventory, Payments, Payroll) can be implemented.

## Solution Statement
Implement a full backend CRUD for the Person entity following the exact same Clean Architecture pattern established by the Restaurant entity (ROS-001). This includes: SQL migration, SQLAlchemy model, Pydantic DTOs with validation, repository layer, service layer with business logic and restaurant-scoped authorization, and REST API routes with JWT authentication. The Person entity will reference `restaurant_id` as a UUID column (the restaurant table already exists from ROS-001). All operations are scoped to a restaurant, and users must have membership in the restaurant (via `user_restaurants`) to manage persons.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/main.py` — Entry point where the person router must be registered. Follow the existing pattern of importing and including routers.
- `apps/Server/src/config/database.py` — Contains `Base` for SQLAlchemy models and database session configuration.
- `apps/Server/src/adapter/rest/dependencies.py` — Contains `get_db` and `get_current_user` dependency injection functions used in all routes.
- `apps/Server/src/models/__init__.py` — Must add `Person` to model exports.
- `apps/Server/src/models/restaurant.py` — Reference pattern for SQLAlchemy model (UUID primary key, timestamps, `__repr__`).
- `apps/Server/src/interface/restaurant_dto.py` — Reference pattern for Pydantic DTOs (Create, Update, Response, `model_config = {"from_attributes": True}`).
- `apps/Server/src/repository/restaurant_repository.py` — Reference pattern for repository (singleton instance, `db: Session` parameter, logging, CRUD methods).
- `apps/Server/src/core/services/restaurant_service.py` — Reference pattern for service layer (authorization via `get_user_restaurant_role`, `PermissionError`/`ValueError` exceptions, logging).
- `apps/Server/src/adapter/rest/restaurant_routes.py` — Reference pattern for REST routes (APIRouter, JWT auth, status codes, exception handling).
- `apps/Server/database/create_restaurant_tables.sql` — Reference pattern for SQL migration (UUID primary key, indexes, `updated_at` trigger).
- `apps/Server/tests/test_restaurant_api.py` — Reference pattern for API endpoint tests (mock DB, mock auth, AsyncClient, status code assertions).
- `apps/Server/tests/test_restaurant_model.py` — Reference pattern for DTO/model unit tests (validation, from_attributes, repr).
- `app_docs/feature-a692d2db-restaurant-multi-tenant-entity.md` — Documentation for the Restaurant entity that Person depends on. Read this to understand restaurant-scoped authorization.

### New Files
- `apps/Server/database/create_person_table.sql` — SQL migration for the person table
- `apps/Server/src/models/person.py` — SQLAlchemy Person model
- `apps/Server/src/interface/person_dto.py` — Pydantic DTOs for Person CRUD
- `apps/Server/src/repository/person_repository.py` — Person data access layer
- `apps/Server/src/core/services/person_service.py` — Person business logic
- `apps/Server/src/adapter/rest/person_routes.py` — Person REST API endpoints
- `apps/Server/tests/test_person_model.py` — Person DTO and model unit tests
- `apps/Server/tests/test_person_api.py` — Person API endpoint integration tests

## Implementation Plan
### Phase 1: Foundation
Create the database migration and SQLAlchemy model. The person table needs a UUID primary key, `restaurant_id` UUID NOT NULL (FK to restaurant table), required fields (`name`, `role`), optional fields (`email`, `whatsapp`), a `type` field with enum values (employee, supplier, owner), and timestamps. Add indexes on `restaurant_id` and `type` for query performance. Register the model in `__init__.py`.

### Phase 2: Core Implementation
Build the Clean Architecture layers bottom-up:
1. **DTOs** — `PersonType` enum, `PersonCreateDTO` (with email validation), `PersonUpdateDTO` (all optional for partial updates), `PersonResponseDTO` (with `from_attributes`).
2. **Repository** — CRUD operations: create, get_by_id, get_by_restaurant (with optional type filter), update, delete, search by name. All scoped to restaurant_id. Singleton instance.
3. **Service** — Wraps repository with restaurant-scoped authorization (check user has membership in the restaurant via `user_restaurants` before any operation). Raises `PermissionError` for access denied, `ValueError` for not found.
4. **Routes** — REST endpoints under `/api/persons` with JWT auth. List endpoint uses `restaurant_id` query parameter with optional `type` filter. Standard CRUD pattern matching restaurant_routes.

### Phase 3: Integration
Register the person router in `main.py`. Write comprehensive tests following the restaurant test patterns: DTO validation tests, model tests, and API endpoint tests covering success cases, authentication failures, authorization failures, not found, and validation errors.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create SQL Migration
- Create `apps/Server/database/create_person_table.sql`
- Define the `person` table with columns:
  - `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`
  - `restaurant_id UUID NOT NULL REFERENCES restaurant(id) ON DELETE CASCADE`
  - `name VARCHAR(255) NOT NULL`
  - `role VARCHAR(100) NOT NULL`
  - `email VARCHAR(255)`
  - `whatsapp VARCHAR(50)`
  - `type VARCHAR(50) NOT NULL DEFAULT 'employee'`
  - `created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()`
  - `updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()`
- Add indexes: `idx_person_restaurant` on `restaurant_id`, `idx_person_type` on `type`
- Add `updated_at` trigger using `update_updated_at_column()` function (already exists from restaurant migration)

### Step 2: Create SQLAlchemy Model
- Create `apps/Server/src/models/person.py`
- Define `Person` class inheriting from `Base`
- Set `__tablename__ = "person"`
- Map all columns from migration using SQLAlchemy Column types:
  - `UUID(as_uuid=True)` for id and restaurant_id
  - `String(255)` for name and email
  - `String(100)` for role
  - `String(50)` for whatsapp and type
  - `DateTime(timezone=True)` for timestamps
  - `ForeignKey("restaurant.id")` for restaurant_id
- Add `default=uuid.uuid4` for id, `default="employee"` for type
- Add `default=datetime.utcnow` for created_at, `onupdate=datetime.utcnow` for updated_at
- Add `__repr__` method
- Update `apps/Server/src/models/__init__.py` to import and export `Person`

### Step 3: Create Pydantic DTOs
- Create `apps/Server/src/interface/person_dto.py`
- Define `PersonType(str, Enum)` with values: EMPLOYEE, SUPPLIER, OWNER
- Define `PersonCreateDTO`:
  - `restaurant_id: UUID` (required)
  - `name: str = Field(..., min_length=1, max_length=255)` (required)
  - `role: str = Field(..., min_length=1, max_length=100)` (required)
  - `email: Optional[str] = Field(None, max_length=255)` with `EmailStr` validation or regex pattern
  - `whatsapp: Optional[str] = Field(None, max_length=50)` with pattern for international format
  - `type: PersonType = PersonType.EMPLOYEE`
- Define `PersonUpdateDTO` with all fields Optional
- Define `PersonResponseDTO` with all fields and `model_config = {"from_attributes": True}`

### Step 4: Create Repository
- Create `apps/Server/src/repository/person_repository.py`
- Define `PersonRepository` class with methods:
  - `create(db, restaurant_id, name, role, email, whatsapp, type)` — insert and return Person
  - `get_by_id(db, person_id)` — get single person by UUID
  - `get_by_restaurant(db, restaurant_id, type_filter=None)` — list persons, with optional type filter
  - `update(db, person)` — commit updated Person object
  - `delete(db, person_id)` — delete person by UUID, return True/False
  - `search(db, restaurant_id, query)` — search by name using ILIKE
- All methods take `db: Session` as first parameter
- Add INFO/ERROR logging with `print(f"INFO [PersonRepository]: ...")`
- Create singleton: `person_repository = PersonRepository()`

### Step 5: Create Service
- Create `apps/Server/src/core/services/person_service.py`
- Define `PersonService` class with methods:
  - `create_person(db, user_id, data: PersonCreateDTO)` — check user has restaurant membership, then create
  - `get_persons(db, user_id, restaurant_id, type_filter=None)` — check membership, list persons
  - `get_person(db, user_id, person_id)` — get person, check user has access to person's restaurant
  - `update_person(db, user_id, person_id, data: PersonUpdateDTO)` — check membership, update fields
  - `delete_person(db, user_id, person_id)` — check membership, delete person
  - `search_persons(db, user_id, restaurant_id, query)` — check membership, search by name
- Import and use `restaurant_repository.get_user_restaurant_role` for authorization checks
- Raise `PermissionError` when user doesn't have access to the restaurant
- Raise `ValueError` when person not found
- Add INFO/ERROR logging with `print(f"INFO [PersonService]: ...")`
- Create singleton: `person_service = PersonService()`

### Step 6: Create REST Routes
- Create `apps/Server/src/adapter/rest/person_routes.py`
- Define `router = APIRouter(prefix="/api/persons", tags=["Persons"])`
- Implement endpoints:
  - `POST ""` — create person, status 201, request body: `PersonCreateDTO`
  - `GET ""` — list persons, query params: `restaurant_id` (required UUID), `type` (optional PersonType)
  - `GET "/{person_id}"` — get person detail
  - `PUT "/{person_id}"` — update person, request body: `PersonUpdateDTO`
  - `DELETE "/{person_id}"` — delete person, status 204
  - `GET "/search"` — search persons, query params: `restaurant_id`, `query`
- All endpoints use `Depends(get_db)` and `Depends(get_current_user)`
- Catch `PermissionError` → 403, `ValueError` → 404
- Use `PersonResponseDTO.model_validate()` for response serialization
- Add INFO/ERROR logging with `print(f"INFO [PersonRoutes]: ...")`

### Step 7: Register Router in main.py
- Add import: `from src.adapter.rest.person_routes import router as person_router`
- Add `app.include_router(person_router)` after the restaurant router
- Add `print("INFO [Main]: Person router registered")`

### Step 8: Create DTO and Model Unit Tests
- Create `apps/Server/tests/test_person_model.py`
- Test `PersonCreateDTO`:
  - Valid creation with all fields
  - Valid creation with required fields only (name, role, restaurant_id)
  - Rejection of empty name (min_length=1)
  - Rejection of name > 255 chars
  - Rejection of empty role (min_length=1)
  - Rejection of missing required fields
  - Valid PersonType enum values
  - Default type is EMPLOYEE
- Test `PersonUpdateDTO`:
  - Partial update with single field
  - Empty DTO (all optional)
- Test `PersonResponseDTO`:
  - `model_validate` from mock model attributes
- Test `Person` model:
  - `__repr__` method
  - `__tablename__` is "person"
- Follow restaurant test patterns with print statements for each test

### Step 9: Create API Endpoint Integration Tests
- Create `apps/Server/tests/test_person_api.py`
- Test helper functions: `create_mock_user`, `create_mock_person`, `get_auth_token`
- Test `POST /api/persons`:
  - Success (201) — user has restaurant membership
  - Unauthenticated (401)
  - No restaurant access (403)
  - Invalid data (422)
- Test `GET /api/persons?restaurant_id={id}`:
  - Success (200) — returns person list
  - With type filter
  - Empty list
- Test `GET /api/persons/{id}`:
  - Success (200)
  - Not found (404)
  - No access (403)
- Test `PUT /api/persons/{id}`:
  - Success (200)
  - No access (403)
- Test `DELETE /api/persons/{id}`:
  - Success (204)
  - No access (403)
- Mock `person_repository` and `restaurant_repository` appropriately
- Follow restaurant API test patterns with patch decorators and AsyncClient

### Step 10: Run Validation Commands
- Run all server tests to validate zero regressions
- Run client type check and build to verify no side effects

## Testing Strategy
### Unit Tests
- **DTO Validation Tests** (`test_person_model.py`): Validate all Pydantic DTOs accept valid data, reject invalid data (empty required fields, too-long strings, invalid enum values), and correctly serialize from model attributes.
- **Model Tests** (`test_person_model.py`): Verify SQLAlchemy model has correct `__tablename__` and `__repr__` output.
- **API Endpoint Tests** (`test_person_api.py`): Test all REST endpoints with mocked database and authentication. Verify correct HTTP status codes (201, 200, 204, 401, 403, 404, 422) and response payloads.

### Edge Cases
- Person with maximum-length name (255 chars) and role (100 chars)
- Person with no optional fields (email, whatsapp both None)
- Empty person list for a restaurant
- Update with no fields changed (empty PersonUpdateDTO)
- Delete a non-existent person
- Access person from a restaurant the user doesn't belong to
- Search with empty query string
- Search with no matching results
- Invalid UUID format for restaurant_id or person_id
- PersonType enum: ensure only "employee", "supplier", "owner" are accepted

## Acceptance Criteria
- SQL migration creates the `person` table with all specified columns, indexes, and trigger
- SQLAlchemy `Person` model maps all columns correctly and is exported from `models/__init__.py`
- Pydantic DTOs validate all required fields, enforce max_length, and support `from_attributes`
- Repository provides create, read (by id, by restaurant, search), update, and delete operations
- Service enforces restaurant-scoped authorization using `user_restaurants` membership
- REST API exposes 6 endpoints under `/api/persons` with JWT authentication
- Person router is registered in `main.py`
- All DTO/model unit tests pass
- All API endpoint tests pass
- All existing server tests continue to pass (zero regressions)
- Client type check and build pass (no side effects)

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/test_person_model.py -v` — Run Person DTO and model unit tests
- `cd apps/Server && python -m pytest tests/test_person_api.py -v` — Run Person API endpoint integration tests
- `cd apps/Server && python -m pytest tests/ -v` — Run ALL Server tests to validate zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate no side effects
- `cd apps/Client && npm run build` — Run Client build to validate no side effects

## Notes
- This is a **backend-only** feature — no UI components, no E2E tests needed.
- This is part of RestaurantOS **Wave 1** (ROS-002) and runs in parallel with ROS-001 (Restaurant) and ROS-003 (Resource).
- The `restaurant_id` column uses a foreign key to `restaurant(id) ON DELETE CASCADE` since the restaurant table already exists from issue #78.
- The `type` column uses a string enum (`employee`, `supplier`, `owner`) stored as VARCHAR in the database, with a Pydantic `PersonType(str, Enum)` for validation.
- The `role` column is free-text (chef, mesero, dueño, proveedor, etc.) — not an enum — to allow flexibility.
- Email validation: use Pydantic `EmailStr` if `pydantic[email]` is available, otherwise use a regex pattern. Check `requirements.txt` first. If `email-validator` is not installed, use a simple regex pattern or skip email format validation to avoid adding a new dependency.
- WhatsApp field accepts international format strings (e.g., "+52 555 123 4567"). No strict format validation needed — just max_length=50.
- The search endpoint (`GET /api/persons/search`) must be defined BEFORE the `GET /api/persons/{person_id}` route to avoid FastAPI interpreting "search" as a UUID path parameter.
- Authorization follows the restaurant pattern: check `restaurant_repository.get_user_restaurant_role(db, user_id, restaurant_id)` returns a non-None value before allowing any operation.
- Wave 2 will create Document and Event entities that reference Person via foreign keys, so the Person model and API must be stable.
