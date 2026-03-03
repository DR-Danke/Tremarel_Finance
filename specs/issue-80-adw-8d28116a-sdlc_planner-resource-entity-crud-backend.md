# Feature: Resource Entity Data Model & CRUD Backend

## Metadata
issue_number: `80`
adw_id: `8d28116a`
issue_json: ``

## Feature Description
Create the `resource` database table and full backend CRUD for the RestaurantOS module. A Resource represents any physical item within a restaurant: products (ingredients), assets (equipment), or services. Resources track current stock levels and minimum thresholds. When stock falls below the minimum after an update, the service logs a low-stock warning (actual Event creation is deferred to issue #101 — Wave 8: Low Stock Alert Automation). The Resource entity is scoped to a restaurant via `restaurant_id` for multi-tenant isolation. This is a backend-only feature — no UI components are included.

## User Story
As a restaurant manager or owner
I want to manage resources (products, assets, services) associated with my restaurant with stock tracking
So that I can track inventory levels, know when stock is low, and reference resources in inventory movements and recipes

## Problem Statement
The RestaurantOS module needs a Resource entity to represent physical items tracked in restaurant operations. Without it, downstream features like Inventory Movements (Wave 2, ROS-006) which track stock changes, and Recipe Management (Wave 4) which references resources as ingredients, cannot be built. Resource is one of the four core entities in Wave 1 required before composed modules can be implemented.

## Solution Statement
Implement a full backend CRUD for the Resource entity following the exact same Clean Architecture pattern established by the Restaurant entity (ROS-001) and Person entity (ROS-002). This includes: SQL migration, SQLAlchemy model, Pydantic DTOs with validation (including computed `is_low_stock` field), repository layer with a `get_low_stock` query, service layer with business logic for low-stock detection and restaurant-scoped authorization, and REST API routes with JWT authentication. All operations are scoped to a restaurant, and users must have membership in the restaurant (via `user_restaurants`) to manage resources.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/main.py` — Entry point where the resource router must be registered. Follow the existing pattern of importing and including routers.
- `apps/Server/src/config/database.py` — Contains `Base` for SQLAlchemy models and database session configuration.
- `apps/Server/src/adapter/rest/dependencies.py` — Contains `get_db` and `get_current_user` dependency injection functions used in all routes.
- `apps/Server/src/models/__init__.py` — Must add `Resource` to model exports.
- `apps/Server/src/models/person.py` — Reference pattern for SQLAlchemy model (UUID primary key, ForeignKey to restaurant, timestamps, `__repr__`).
- `apps/Server/src/interface/person_dto.py` — Reference pattern for Pydantic DTOs (Create, Update, Response with `model_config = {"from_attributes": True}`, str Enum).
- `apps/Server/src/repository/person_repository.py` — Reference pattern for repository (singleton instance, `db: Session` parameter, logging, CRUD + filter methods).
- `apps/Server/src/repository/restaurant_repository.py` — Contains `get_user_restaurant_role` needed for authorization checks.
- `apps/Server/src/core/services/person_service.py` — Reference pattern for service layer (authorization via `get_user_restaurant_role`, `PermissionError`/`ValueError` exceptions, logging).
- `apps/Server/src/adapter/rest/person_routes.py` — Reference pattern for REST routes (APIRouter, JWT auth, status codes, exception handling, query param filters).
- `apps/Server/database/create_person_table.sql` — Reference pattern for SQL migration (UUID primary key, FK to restaurant with CASCADE, indexes, `updated_at` trigger).
- `apps/Server/tests/test_person_model.py` — Reference pattern for DTO/model unit tests (validation, from_attributes, repr).
- `apps/Server/tests/test_person_api.py` — Reference pattern for API endpoint tests (mock DB, mock auth, AsyncClient, status code assertions).
- `app_docs/feature-db5f36c7-database-schema-tables.md` — Documentation for database schema and table patterns.
- `app_docs/feature-0f0d4c36-fastapi-backend-setup.md` — Documentation for adding new routers to main.py.
- `app_docs/feature-ed4cef49-backend-jwt-auth-rbac.md` — Documentation for protected routes with RBAC.

### New Files
- `apps/Server/database/create_resource_table.sql` — SQL migration for the resource table
- `apps/Server/src/models/resource.py` — SQLAlchemy Resource model
- `apps/Server/src/interface/resource_dto.py` — Pydantic DTOs for Resource CRUD
- `apps/Server/src/repository/resource_repository.py` — Resource data access layer
- `apps/Server/src/core/services/resource_service.py` — Resource business logic with low-stock detection
- `apps/Server/src/adapter/rest/resource_routes.py` — Resource REST API endpoints
- `apps/Server/tests/test_resource_model.py` — Resource DTO and model unit tests
- `apps/Server/tests/test_resource_api.py` — Resource API endpoint integration tests

## Implementation Plan
### Phase 1: Foundation
Create the database migration and SQLAlchemy model. The resource table needs a UUID primary key, `restaurant_id` UUID NOT NULL (FK to restaurant table with CASCADE), required fields (`name`, `unit`), a `type` field with enum values (producto, activo, servicio), decimal fields for stock tracking (`current_stock`, `minimum_stock`, `last_unit_cost`), and timestamps. Add indexes on `restaurant_id` and `type` for query performance. Register the model in `__init__.py`.

### Phase 2: Core Implementation
Build the Clean Architecture layers bottom-up:
1. **DTOs** — `ResourceType` enum (producto, activo, servicio), `ResourceCreateDTO` (with Decimal fields and non-negative validation), `ResourceUpdateDTO` (all optional for partial updates), `ResourceResponseDTO` (with computed `is_low_stock` property and `from_attributes`).
2. **Repository** — CRUD operations: create, get_by_id, get_by_restaurant (with optional type filter), update, delete, get_low_stock (resources where current_stock < minimum_stock). All scoped to restaurant_id. Singleton instance.
3. **Service** — Wraps repository with restaurant-scoped authorization (check user has membership in the restaurant via `user_restaurants` before any operation). Includes low-stock detection: after any update that changes stock levels, log a warning if current_stock < minimum_stock. Raises `PermissionError` for access denied, `ValueError` for not found.
4. **Routes** — REST endpoints under `/api/resources` with JWT auth. List endpoint uses `restaurant_id` query parameter with optional `type` filter. Includes a dedicated low-stock endpoint. Standard CRUD pattern matching person_routes.

### Phase 3: Integration
Register the resource router in `main.py`. Write comprehensive tests following the person test patterns: DTO validation tests (including Decimal fields and non-negative constraints), model tests, and API endpoint tests covering success cases, authentication failures, authorization failures, not found, and validation errors.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create SQL Migration
- Create `apps/Server/database/create_resource_table.sql`
- Define the `resource` table with columns:
  - `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`
  - `restaurant_id UUID NOT NULL REFERENCES restaurant(id) ON DELETE CASCADE`
  - `type VARCHAR(50) NOT NULL DEFAULT 'producto'`
  - `name VARCHAR(255) NOT NULL`
  - `unit VARCHAR(50) NOT NULL`
  - `current_stock DECIMAL(12,4) NOT NULL DEFAULT 0`
  - `minimum_stock DECIMAL(12,4) NOT NULL DEFAULT 0`
  - `last_unit_cost DECIMAL(12,4) DEFAULT 0`
  - `created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()`
  - `updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()`
- Add indexes: `idx_resource_restaurant` on `restaurant_id`, `idx_resource_type` on `type`
- Add `updated_at` trigger using `update_updated_at_column()` function (already exists from restaurant migration)

### Step 2: Create SQLAlchemy Model
- Create `apps/Server/src/models/resource.py`
- Define `Resource` class inheriting from `Base`
- Set `__tablename__ = "resource"`
- Map all columns from migration using SQLAlchemy Column types:
  - `UUID(as_uuid=True)` for id and restaurant_id
  - `String(255)` for name
  - `String(50)` for type and unit
  - `Numeric(12, 4)` for current_stock, minimum_stock, last_unit_cost
  - `DateTime(timezone=True)` for timestamps
  - `ForeignKey("restaurant.id")` for restaurant_id
- Add `default=uuid.uuid4` for id, `default="producto"` for type
- Add `default=0` for current_stock, minimum_stock, last_unit_cost
- Add `default=datetime.utcnow` for created_at, `onupdate=datetime.utcnow` for updated_at
- Add `__repr__` method: `<Resource(id={self.id}, name={self.name}, type={self.type}, restaurant_id={self.restaurant_id})>`
- Update `apps/Server/src/models/__init__.py` to import and export `Resource`

### Step 3: Create Pydantic DTOs
- Create `apps/Server/src/interface/resource_dto.py`
- Define `ResourceType(str, Enum)` with values: PRODUCTO = "producto", ACTIVO = "activo", SERVICIO = "servicio"
- Define `ResourceCreateDTO`:
  - `restaurant_id: UUID` (required)
  - `type: ResourceType = ResourceType.PRODUCTO` (default producto)
  - `name: str = Field(..., min_length=1, max_length=255)` (required)
  - `unit: str = Field(..., min_length=1, max_length=50)` (required)
  - `current_stock: Decimal = Field(default=Decimal("0"), ge=0)` (non-negative)
  - `minimum_stock: Decimal = Field(default=Decimal("0"), ge=0)` (non-negative)
  - `last_unit_cost: Decimal = Field(default=Decimal("0"), ge=0)` (non-negative)
- Define `ResourceUpdateDTO` with all fields Optional:
  - `type: Optional[ResourceType]`
  - `name: Optional[str] = Field(None, min_length=1, max_length=255)`
  - `unit: Optional[str] = Field(None, min_length=1, max_length=50)`
  - `current_stock: Optional[Decimal] = Field(None, ge=0)`
  - `minimum_stock: Optional[Decimal] = Field(None, ge=0)`
  - `last_unit_cost: Optional[Decimal] = Field(None, ge=0)`
- Define `ResourceResponseDTO` with all fields and computed `is_low_stock`:
  - All standard fields (id, restaurant_id, type, name, unit, current_stock, minimum_stock, last_unit_cost, created_at, updated_at)
  - `is_low_stock: bool` — computed field: `current_stock < minimum_stock`
  - Use `@model_validator(mode='before')` or a `@computed_field` or custom `model_validate` classmethod to compute `is_low_stock` from the model. The simplest approach: use a custom classmethod `from_model` or override using `@model_validator(mode='before')` that checks if the source object has `current_stock` and `minimum_stock` attributes and sets `is_low_stock` accordingly. Alternatively, compute it in the routes layer before constructing the DTO.
  - `model_config = {"from_attributes": True}`

### Step 4: Create Repository
- Create `apps/Server/src/repository/resource_repository.py`
- Define `ResourceRepository` class with methods:
  - `create(db, restaurant_id, type, name, unit, current_stock, minimum_stock, last_unit_cost)` — insert and return Resource
  - `get_by_id(db, resource_id)` — get single resource by UUID
  - `get_by_restaurant(db, restaurant_id, type_filter=None)` — list resources, with optional type filter
  - `update(db, resource)` — commit updated Resource object
  - `delete(db, resource_id)` — delete resource by UUID, return True/False
  - `get_low_stock(db, restaurant_id)` — get resources where `current_stock < minimum_stock` for a restaurant
- All methods take `db: Session` as first parameter
- Add INFO/ERROR logging with `print(f"INFO [ResourceRepository]: ...")`
- Create singleton: `resource_repository = ResourceRepository()`

### Step 5: Create Service
- Create `apps/Server/src/core/services/resource_service.py`
- Define `ResourceService` class with methods:
  - `_check_restaurant_access(db, user_id, restaurant_id)` — private method to check user has restaurant membership via `restaurant_repository.get_user_restaurant_role`
  - `create_resource(db, user_id, data: ResourceCreateDTO)` — check membership, create resource. After creation, if `current_stock < minimum_stock`, log warning: `"WARNING [ResourceService]: Resource '{name}' is below minimum stock ({current_stock} < {minimum_stock})"`
  - `get_resources(db, user_id, restaurant_id, type_filter=None)` — check membership, list resources
  - `get_resource(db, user_id, resource_id)` — get resource, check user has access to resource's restaurant
  - `update_resource(db, user_id, resource_id, data: ResourceUpdateDTO)` — check membership, update fields. After update, if `current_stock < minimum_stock`, log warning: `"WARNING [ResourceService]: Resource '{name}' stock dropped below minimum ({current_stock} < {minimum_stock})"`
  - `delete_resource(db, user_id, resource_id)` — check membership, delete resource
  - `get_low_stock_resources(db, user_id, restaurant_id)` — check membership, return resources where current_stock < minimum_stock
- Import and use `restaurant_repository.get_user_restaurant_role` for authorization checks
- Raise `PermissionError` when user doesn't have access to the restaurant
- Raise `ValueError` when resource not found
- Add INFO/ERROR/WARNING logging with `print(f"INFO [ResourceService]: ...")`
- Create singleton: `resource_service = ResourceService()`

### Step 6: Create REST Routes
- Create `apps/Server/src/adapter/rest/resource_routes.py`
- Define `router = APIRouter(prefix="/api/resources", tags=["Resources"])`
- Implement endpoints:
  - `POST ""` — create resource, status 201, request body: `ResourceCreateDTO`
  - `GET "/low-stock"` — get low-stock resources, query param: `restaurant_id` (required UUID). **IMPORTANT**: This must be defined BEFORE `GET "/{resource_id}"` to avoid FastAPI interpreting "low-stock" as a UUID path parameter.
  - `GET ""` — list resources, query params: `restaurant_id` (required UUID), `type` (optional ResourceType)
  - `GET "/{resource_id}"` — get resource detail
  - `PUT "/{resource_id}"` — update resource, request body: `ResourceUpdateDTO`
  - `DELETE "/{resource_id}"` — delete resource, status 204
- All endpoints use `Depends(get_db)` and `Depends(get_current_user)`
- Catch `PermissionError` → 403, `ValueError` → 404
- For response serialization, compute `is_low_stock` and construct `ResourceResponseDTO`:
  - Helper function `_to_response(resource: Resource) -> ResourceResponseDTO` that creates the DTO and sets `is_low_stock = resource.current_stock < resource.minimum_stock`
- Add INFO/ERROR logging with `print(f"INFO [ResourceRoutes]: ...")`

### Step 7: Register Router in main.py
- Add import: `from src.adapter.rest.resource_routes import router as resource_router`
- Add `app.include_router(resource_router)` after the person router
- Add `print("INFO [Main]: Resource router registered")`

### Step 8: Create DTO and Model Unit Tests
- Create `apps/Server/tests/test_resource_model.py`
- Test `ResourceCreateDTO`:
  - Valid creation with all fields
  - Valid creation with required fields only (name, unit, restaurant_id) — defaults for type, current_stock, minimum_stock, last_unit_cost
  - Rejection of empty name (min_length=1)
  - Rejection of name > 255 chars
  - Rejection of empty unit (min_length=1)
  - Rejection of unit > 50 chars
  - Rejection of missing required fields
  - Rejection of negative current_stock (ge=0)
  - Rejection of negative minimum_stock (ge=0)
  - Rejection of negative last_unit_cost (ge=0)
  - Valid ResourceType enum values (producto, activo, servicio)
  - Rejection of invalid ResourceType value
  - Default type is PRODUCTO
  - Default stock values are 0
- Test `ResourceUpdateDTO`:
  - Partial update with single field
  - Empty DTO (all optional)
  - Rejection of negative stock values
- Test `ResourceResponseDTO`:
  - `model_validate` from mock model attributes
  - `is_low_stock` is True when current_stock < minimum_stock
  - `is_low_stock` is False when current_stock >= minimum_stock
  - `is_low_stock` is False when both are 0
- Test `Resource` model:
  - `__repr__` method
  - `__tablename__` is "resource"
- Follow person test patterns with print statements for each test

### Step 9: Create API Endpoint Integration Tests
- Create `apps/Server/tests/test_resource_api.py`
- Test helper functions: `create_mock_user`, `create_mock_resource`, `get_auth_token`
- Test `POST /api/resources`:
  - Success (201) — user has restaurant membership, returns resource with `is_low_stock` computed
  - Unauthenticated (401)
  - No restaurant access (403)
  - Invalid data — negative stock (422)
  - Invalid data — missing required fields (422)
- Test `GET /api/resources?restaurant_id={id}`:
  - Success (200) — returns resource list
  - With type filter (e.g., `type=producto`)
  - Empty list
- Test `GET /api/resources/{id}`:
  - Success (200) — returns resource with `is_low_stock`
  - Not found (404)
  - No access (403)
- Test `PUT /api/resources/{id}`:
  - Success (200) — update stock values
  - No access (403)
- Test `DELETE /api/resources/{id}`:
  - Success (204)
  - No access (403)
- Test `GET /api/resources/low-stock?restaurant_id={id}`:
  - Success (200) — returns only low-stock resources
  - Empty when no low-stock resources
- Mock `resource_repository` and `restaurant_repository` appropriately
- Follow person API test patterns with patch decorators and AsyncClient

### Step 10: Run Validation Commands
- Run all server tests to validate zero regressions
- Run client type check and build to verify no side effects

## Testing Strategy
### Unit Tests
- **DTO Validation Tests** (`test_resource_model.py`): Validate all Pydantic DTOs accept valid data, reject invalid data (empty required fields, too-long strings, invalid enum values, negative Decimal values), and correctly serialize from model attributes including computed `is_low_stock`.
- **Model Tests** (`test_resource_model.py`): Verify SQLAlchemy model has correct `__tablename__` and `__repr__` output.
- **API Endpoint Tests** (`test_resource_api.py`): Test all REST endpoints with mocked database and authentication. Verify correct HTTP status codes (201, 200, 204, 401, 403, 404, 422), response payloads, and `is_low_stock` computation.

### Edge Cases
- Resource with maximum-length name (255 chars) and unit (50 chars)
- Resource with current_stock = 0 and minimum_stock = 0 (is_low_stock should be False)
- Resource with current_stock = 0 and minimum_stock > 0 (is_low_stock should be True)
- Resource with current_stock = minimum_stock exactly (is_low_stock should be False — not strictly less than)
- Resource with very large Decimal values (DECIMAL(12,4) max)
- Resource with Decimal precision (e.g., 0.0001)
- Empty resource list for a restaurant
- Update with no fields changed (empty ResourceUpdateDTO)
- Update that causes stock to drop below minimum (low-stock warning logged)
- Delete a non-existent resource
- Access resource from a restaurant the user doesn't belong to
- Invalid UUID format for restaurant_id or resource_id
- ResourceType enum: ensure only "producto", "activo", "servicio" are accepted
- Low-stock endpoint returns empty list when all resources are above minimum

## Acceptance Criteria
- SQL migration creates the `resource` table with all specified columns (including DECIMAL(12,4) for stock fields), indexes, and trigger
- SQLAlchemy `Resource` model maps all columns correctly (including `Numeric(12, 4)` for stock fields) and is exported from `models/__init__.py`
- Pydantic DTOs validate all required fields, enforce max_length, enforce non-negative constraints (ge=0) on stock and cost fields, and support `from_attributes`
- `ResourceResponseDTO` includes computed `is_low_stock` field (True when current_stock < minimum_stock)
- Repository provides create, read (by id, by restaurant with type filter), update, delete, and get_low_stock operations
- Service enforces restaurant-scoped authorization using `user_restaurants` membership
- Service logs WARNING when stock drops below minimum after create or update
- REST API exposes 6 endpoints under `/api/resources` with JWT authentication (CRUD + low-stock)
- Resource router is registered in `main.py`
- All DTO/model unit tests pass
- All API endpoint tests pass
- All existing server tests continue to pass (zero regressions)
- Client type check and build pass (no side effects)

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/test_resource_model.py -v` — Run Resource DTO and model unit tests
- `cd apps/Server && python -m pytest tests/test_resource_api.py -v` — Run Resource API endpoint integration tests
- `cd apps/Server && python -m pytest tests/ -v` — Run ALL Server tests to validate zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate no side effects
- `cd apps/Client && npm run build` — Run Client build to validate no side effects

## Notes
- This is a **backend-only** feature — no UI components, no E2E tests needed.
- This is part of RestaurantOS **Wave 1** (ROS-003) and runs in parallel with ROS-001 (Restaurant) and ROS-002 (Person).
- The `restaurant_id` column uses a foreign key to `restaurant(id) ON DELETE CASCADE` since the restaurant table already exists from issue #78.
- The `type` column uses a string enum (`producto`, `activo`, `servicio`) stored as VARCHAR in the database, with a Pydantic `ResourceType(str, Enum)` for validation.
- Decimal fields use `DECIMAL(12,4)` in SQL and `Numeric(12, 4)` in SQLAlchemy. In Pydantic, use `Decimal` from the `decimal` module with `Field(ge=0)` for non-negative validation.
- The `is_low_stock` field in `ResourceResponseDTO` is computed, not stored in the database. It is calculated as `current_stock < minimum_stock`. The simplest approach is to compute it in the routes layer using a helper function before constructing the response DTO. An alternative is to use a `@model_validator(mode='before')` in the DTO.
- The `GET /api/resources/low-stock` endpoint must be defined BEFORE `GET /api/resources/{resource_id}` to avoid FastAPI interpreting "low-stock" as a UUID path parameter.
- Low-stock detection in the service layer is **logging only** for now. Actual Event creation for low-stock alerts is deferred to issue #101 (Wave 8: Low Stock Alert Automation).
- Authorization follows the restaurant pattern: check `restaurant_repository.get_user_restaurant_role(db, user_id, restaurant_id)` returns a non-None value before allowing any operation.
- Wave 2 will create Inventory Movement (ROS-006) that tracks stock changes for resources, so the Resource model and API must be stable.
- Wave 4 builds recipe management referencing resources as ingredients.
