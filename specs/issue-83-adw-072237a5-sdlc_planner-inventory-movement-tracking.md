# Feature: Inventory Movement Tracking

## Metadata
issue_number: `83`
adw_id: `072237a5`
issue_json: ``

## Feature Description
Create the `inventory_movement` table and full CRUD API for tracking all stock changes in RestaurantOS. Each movement records a resource, type (entry/exit), quantity, reason, and the person who performed it. Every movement automatically updates the resource's `current_stock` — incrementing for entries, decrementing for exits. Negative stock is prevented at the service layer by rejecting exit movements that would reduce `current_stock` below zero. When stock drops below `minimum_stock`, a warning is logged (future Wave 8 will create alerta_stock Events).

## User Story
As a restaurant manager
I want to record every inventory entry and exit with a reason and responsible person
So that I can maintain accurate stock levels and trace all inventory changes

## Problem Statement
RestaurantOS has a Resource entity with `current_stock` but no mechanism to track _how_ or _why_ stock changes. Without an inventory movement ledger, stock updates are opaque — there's no audit trail for purchases (compra), daily usage (uso), spoilage (merma), production batches (produccion), recipe deductions (receta), or manual adjustments (ajuste). This makes it impossible to investigate discrepancies or generate usage reports.

## Solution Statement
Implement a full inventory movement tracking system consisting of: (1) a `inventory_movement` database table with foreign keys to `resource` and `person`, (2) a SQLAlchemy model, (3) Pydantic DTOs with strict enum validation for movement type and reason, (4) a repository for persistence, (5) a service layer that validates resource existence, prevents negative stock, atomically updates `current_stock`, and logs low-stock warnings, and (6) JWT-protected REST endpoints for creating movements and querying movement history with date/reason filters. The entire stack follows the existing Clean Architecture pattern established by Resource, Person, and Event entities.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/main.py` — Register the new inventory movement router alongside existing routers
- `apps/Server/src/models/resource.py` — Reference for model pattern (UUID PK, restaurant_id FK, Decimal columns, DateTime fields); also the Resource model whose `current_stock` will be updated by the service
- `apps/Server/src/interface/resource_dto.py` — Reference for DTO pattern (Enum definitions, Create/Response DTOs, `model_config`, `model_validator`)
- `apps/Server/src/repository/resource_repository.py` — Reference for repository pattern (singleton, Session-based CRUD, print logging); also used by inventory service to fetch and update resources
- `apps/Server/src/core/services/resource_service.py` — Reference for service pattern (`_check_restaurant_access`, PermissionError/ValueError raises, print logging)
- `apps/Server/src/adapter/rest/resource_routes.py` — Reference for routes pattern (APIRouter, Depends, try/except, `_to_response` helper, HTTP status codes)
- `apps/Server/src/adapter/rest/dependencies.py` — Provides `get_db` and `get_current_user` dependencies
- `apps/Server/src/repository/restaurant_repository.py` — Provides `get_user_restaurant_role` for authorization checks
- `apps/Server/src/config/database.py` — Provides `Base` for SQLAlchemy model declaration
- `apps/Server/tests/test_resource_api.py` — Reference for API test pattern (mock fixtures, AsyncClient, get_auth_token, patch mocking)
- `apps/Server/tests/test_resource_model.py` — Reference for model/DTO test pattern (validation tests, enum tests, response DTO tests)
- `apps/Server/database/create_resource_table.sql` — Reference for SQL migration pattern (UUID PK, indexes, trigger)
- `app_docs/feature-a692d2db-restaurant-multi-tenant-entity.md` — Restaurant multi-tenant scoping pattern
- `app_docs/feature-8d28116a-resource-entity-crud-backend.md` — Resource entity documentation (the entity whose stock is updated)
- `app_docs/feature-14633eae-person-entity-crud-backend.md` — Person entity documentation (optional FK reference)
- `app_docs/feature-0f0d4c36-fastapi-backend-setup.md` — FastAPI setup and router registration pattern

### New Files
- `apps/Server/database/create_inventory_movement_table.sql` — SQL migration for the inventory_movement table
- `apps/Server/src/models/inventory_movement.py` — SQLAlchemy InventoryMovement model
- `apps/Server/src/interface/inventory_movement_dto.py` — Pydantic DTOs (MovementType, MovementReason enums, CreateDTO, ResponseDTO)
- `apps/Server/src/repository/inventory_movement_repository.py` — Repository for inventory movement persistence
- `apps/Server/src/core/services/inventory_service.py` — Service with stock validation and atomic update logic
- `apps/Server/src/adapter/rest/inventory_movement_routes.py` — REST API endpoints
- `apps/Server/tests/test_inventory_movement_model.py` — Unit tests for model, DTOs, and enums
- `apps/Server/tests/test_inventory_movement_api.py` — API integration tests

## Implementation Plan
### Phase 1: Foundation
Create the database migration SQL, SQLAlchemy model, and Pydantic DTOs. These are standalone artifacts that don't depend on other new code and establish the data contract.

### Phase 2: Core Implementation
Build the repository for CRUD operations, then the service layer that orchestrates movement creation with resource stock validation and atomic updates. The service is the heart of the feature — it enforces the negative-stock constraint and updates `current_stock`.

### Phase 3: Integration
Wire up the REST routes with JWT auth, register the router in `main.py`, and create comprehensive tests for both the model/DTO layer and the API layer.

## Step by Step Tasks

### Step 1: Create Database Migration
- Create `apps/Server/database/create_inventory_movement_table.sql`
- Define the `inventory_movement` table with:
  - `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
  - `resource_id` UUID NOT NULL REFERENCES resource(id) ON DELETE CASCADE
  - `type` VARCHAR(20) NOT NULL (values: entry, exit)
  - `quantity` DECIMAL(12,4) NOT NULL
  - `reason` VARCHAR(100) NOT NULL (values: compra, uso, produccion, merma, receta, ajuste)
  - `date` TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
  - `person_id` UUID REFERENCES person(id) ON DELETE SET NULL
  - `restaurant_id` UUID NOT NULL
  - `notes` TEXT
  - `created_at` TIMESTAMP WITH TIME ZONE DEFAULT NOW()
- Add indexes: `idx_inv_movement_resource` on resource_id, `idx_inv_movement_restaurant` on restaurant_id, `idx_inv_movement_date` on date

### Step 2: Create SQLAlchemy Model
- Create `apps/Server/src/models/inventory_movement.py`
- Define `InventoryMovement(Base)` with `__tablename__ = "inventory_movement"`
- Follow the Resource model pattern: UUID columns with `UUID(as_uuid=True)`, `Numeric(12, 4)` for quantity, `DateTime(timezone=True)` for timestamps
- Include `__repr__` method for debugging

### Step 3: Create Pydantic DTOs
- Create `apps/Server/src/interface/inventory_movement_dto.py`
- Define `MovementType(str, Enum)` with values: `ENTRY = "entry"`, `EXIT = "exit"`
- Define `MovementReason(str, Enum)` with values: `COMPRA = "compra"`, `USO = "uso"`, `PRODUCCION = "produccion"`, `MERMA = "merma"`, `RECETA = "receta"`, `AJUSTE = "ajuste"`
- Define `InventoryMovementCreateDTO(BaseModel)`:
  - `resource_id: UUID` (required)
  - `type: MovementType` (required)
  - `quantity: Decimal = Field(..., gt=0)` (must be positive)
  - `reason: MovementReason` (required)
  - `date: Optional[datetime] = None` (defaults to server time)
  - `person_id: Optional[UUID] = None`
  - `restaurant_id: UUID` (required)
  - `notes: Optional[str] = Field(None, max_length=1000)`
- Define `InventoryMovementResponseDTO(BaseModel)`:
  - All fields from the model plus `model_config = {"from_attributes": True}`
  - Include `id`, `resource_id`, `type`, `quantity`, `reason`, `date`, `person_id`, `restaurant_id`, `notes`, `created_at`

### Step 4: Create Repository
- Create `apps/Server/src/repository/inventory_movement_repository.py`
- Define `InventoryMovementRepository` class with methods:
  - `create(self, db: Session, resource_id, type, quantity, reason, date, person_id, restaurant_id, notes) -> InventoryMovement` — Insert a new movement record
  - `get_by_resource(self, db: Session, resource_id: UUID, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> list[InventoryMovement]` — Get movement history for a resource with optional date range filter, ordered by date descending
  - `get_by_restaurant(self, db: Session, restaurant_id: UUID, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None, reason: Optional[str] = None) -> list[InventoryMovement]` — Get all movements for a restaurant with optional date range and reason filters, ordered by date descending
- Create singleton instance: `inventory_movement_repository = InventoryMovementRepository()`
- Include print logging in every method following the `INFO [InventoryMovementRepository]:` pattern

### Step 5: Create Service
- Create `apps/Server/src/core/services/inventory_service.py`
- Define `InventoryService` class with:
  - `_check_restaurant_access(self, db, user_id, restaurant_id)` — Same authorization pattern as ResourceService
  - `create_movement(self, db: Session, user_id: UUID, data: InventoryMovementCreateDTO) -> InventoryMovement`:
    1. Check restaurant access for user
    2. Fetch resource via `resource_repository.get_by_id(db, data.resource_id)` — raise `ValueError("Resource not found")` if None
    3. Verify `resource.restaurant_id == data.restaurant_id` — raise `ValueError("Resource does not belong to this restaurant")` if mismatch
    4. For `EXIT` movements: check `resource.current_stock >= data.quantity` — raise `ValueError("Insufficient stock. Current: {current}, requested: {quantity}")` if not enough
    5. Create movement record via `inventory_movement_repository.create(...)`
    6. Update `resource.current_stock`: add for ENTRY, subtract for EXIT
    7. Save resource via `resource_repository.update(db, resource)`
    8. Check if `resource.current_stock < resource.minimum_stock` → print `WARNING [InventoryService]: Resource '{name}' is below minimum stock ({current} < {minimum})`
    9. Return the created movement
  - `get_movements_by_resource(self, db, user_id, resource_id, date_from, date_to) -> list[InventoryMovement]`:
    1. Fetch resource to get its restaurant_id
    2. Check restaurant access
    3. Return `inventory_movement_repository.get_by_resource(...)`
  - `get_movements_by_restaurant(self, db, user_id, restaurant_id, date_from, date_to, reason) -> list[InventoryMovement]`:
    1. Check restaurant access
    2. Return `inventory_movement_repository.get_by_restaurant(...)`
- Create singleton instance: `inventory_service = InventoryService()`
- Include print logging for all operations following the `INFO/ERROR/WARNING [InventoryService]:` pattern

### Step 6: Create REST Routes
- Create `apps/Server/src/adapter/rest/inventory_movement_routes.py`
- Define `router = APIRouter(prefix="/api/inventory-movements", tags=["Inventory Movements"])`
- Define `_to_response(movement) -> InventoryMovementResponseDTO` helper
- Endpoints:
  - `POST ""` (201) — Create movement and update stock
    - Body: `InventoryMovementCreateDTO`
    - Deps: `get_db`, `get_current_user`
    - Catch `PermissionError` → 403, `ValueError` → 400 (for stock validation) or 404 (for resource not found)
  - `GET ""` (200) — List movements
    - Query params: `resource_id: Optional[UUID]`, `restaurant_id: Optional[UUID]`, `date_from: Optional[datetime]`, `date_to: Optional[datetime]`, `reason: Optional[MovementReason]`
    - If `resource_id` provided: use `get_movements_by_resource`
    - If `restaurant_id` provided: use `get_movements_by_restaurant`
    - If neither provided: return 422 (must provide one filter)
    - Catch `PermissionError` → 403, `ValueError` → 404
- Include print logging in every endpoint following the `INFO/ERROR [InventoryMovementRoutes]:` pattern

### Step 7: Register Router in main.py
- Import: `from src.adapter.rest.inventory_movement_routes import router as inventory_movement_router`
- Add: `app.include_router(inventory_movement_router)` after the event_router
- Add: `print("INFO [Main]: Inventory Movement router registered")`

### Step 8: Create Model and DTO Unit Tests
- Create `apps/Server/tests/test_inventory_movement_model.py`
- Tests for `MovementType` enum (exactly 2 values: entry, exit)
- Tests for `MovementReason` enum (exactly 6 values: compra, uso, produccion, merma, receta, ajuste)
- Tests for `InventoryMovementCreateDTO`:
  - Valid creation with all fields
  - Valid creation with required fields only
  - Reject zero quantity (gt=0)
  - Reject negative quantity
  - Reject invalid movement type
  - Reject invalid reason
  - Reject missing required fields (resource_id, type, quantity, reason, restaurant_id)
  - Accept optional person_id and notes
  - Accept optional date (None defaults)
- Tests for `InventoryMovementResponseDTO`:
  - From mock model object (model_validate with from_attributes=True)
  - All fields correctly mapped
- Tests for `InventoryMovement` model:
  - `__tablename__` is "inventory_movement"
  - `__repr__` output
- Follow existing `test_resource_model.py` print logging pattern

### Step 9: Create API Integration Tests
- Create `apps/Server/tests/test_inventory_movement_api.py`
- Follow `test_resource_api.py` pattern exactly: mock fixtures, `get_mock_db`, `get_auth_token`, AsyncClient with ASGITransport
- Define `create_mock_inventory_movement(...)` helper
- Test suites:
  - **Create Movement:**
    - `test_create_entry_movement_success` — 201, resource stock increased
    - `test_create_exit_movement_success` — 201, resource stock decreased
    - `test_create_exit_movement_insufficient_stock` — 400, stock not enough
    - `test_create_movement_resource_not_found` — 404
    - `test_create_movement_unauthenticated` — 401
    - `test_create_movement_no_restaurant_access` — 403
    - `test_create_movement_invalid_type` — 422
    - `test_create_movement_zero_quantity` — 422
    - `test_create_movement_negative_quantity` — 422
  - **List Movements:**
    - `test_list_movements_by_resource_success` — 200
    - `test_list_movements_by_restaurant_success` — 200
    - `test_list_movements_by_restaurant_with_reason_filter` — 200
    - `test_list_movements_empty` — 200, empty array
    - `test_list_movements_unauthenticated` — 401
    - `test_list_movements_no_restaurant_access` — 403
- Follow existing print logging pattern: `print("INFO [TestInventoryMovementAPI]: test_name - PASSED")`

### Step 10: Run Validation Commands
- Run all validation commands listed below to ensure zero regressions

## Testing Strategy
### Unit Tests
- **Enum validation**: Verify MovementType has exactly 2 values and MovementReason has exactly 6 values
- **DTO validation**: Test all Pydantic constraints (gt=0 for quantity, required fields, enum validation, optional defaults)
- **Response DTO**: Test model_validate with from_attributes=True correctly maps all fields
- **Model**: Test __tablename__ and __repr__
- **Service logic** (via API tests): Test stock increment/decrement, negative stock prevention, resource not found, restaurant access check, low-stock warning logging

### Edge Cases
- Exit movement with quantity exactly equal to current_stock (should succeed, leaving stock at 0)
- Exit movement with quantity exceeding current_stock by 0.0001 (should fail)
- Entry movement on a resource with 0 current_stock (should succeed)
- Movement with person_id that references a valid person (nullable FK)
- Movement with notes at maximum length
- Date filtering with date_from only, date_to only, and both
- Resource belonging to a different restaurant than the movement's restaurant_id
- Concurrent movements (not tested at unit level, but service should handle via DB transactions)

## Acceptance Criteria
- `inventory_movement` table SQL migration exists with correct schema and indexes
- SQLAlchemy model maps all columns correctly
- MovementType enum accepts only "entry" and "exit"
- MovementReason enum accepts only "compra", "uso", "produccion", "merma", "receta", "ajuste"
- POST /api/inventory-movements creates a movement and atomically updates resource.current_stock
- Entry movements increment current_stock by quantity
- Exit movements decrement current_stock by quantity
- Exit movements are rejected with 400 when quantity > current_stock
- GET /api/inventory-movements?resource_id={id} returns movement history for a resource
- GET /api/inventory-movements?restaurant_id={id} returns all movements with optional date_from, date_to, reason filters
- All endpoints require JWT authentication (401 without token)
- Restaurant access is enforced (403 for unauthorized users)
- Low-stock warning is logged when stock drops below minimum_stock after a movement
- All tests pass with zero regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest tests/test_inventory_movement_model.py -v` — Run inventory movement model and DTO tests
- `cd apps/Server && uv run pytest tests/test_inventory_movement_api.py -v` — Run inventory movement API tests
- `cd apps/Server && uv run pytest` — Run all Server tests to validate zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check (no frontend changes expected, but verify no breakage)
- `cd apps/Client && npm run build` — Run Client build to validate no breakage

## Notes
- This is a backend-only feature (no UI). Wave 4 will build the frontend Resource & Inventory page.
- The low-stock warning is a log-only output for now. Wave 8 (issue #101) will create alerta_stock Events when stock drops below minimum_stock.
- The `restaurant_id` on inventory_movement is denormalized (could be derived from resource.restaurant_id) but is kept for efficient queries and consistency with the pattern used by other RestaurantOS entities.
- No new libraries are needed — all dependencies (FastAPI, SQLAlchemy, Pydantic, psycopg2) are already in requirements.txt.
- The service catches the ValueError for "insufficient stock" and the routes should map it to HTTP 400 (bad request) rather than 404, since the resource exists but the operation is invalid. Other ValueErrors (resource not found) should map to 404. The route layer should differentiate based on the error message content.
