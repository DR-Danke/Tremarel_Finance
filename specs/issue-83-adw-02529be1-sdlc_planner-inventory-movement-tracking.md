# Feature: Inventory Movement Tracking

## Metadata
issue_number: `83`
adw_id: `02529be1`
issue_json: ``

## Feature Description
Create the Inventory Movement tracking system for RestaurantOS. This feature adds the `inventory_movement` table and a complete API for recording all stock changes (entries and exits). Each movement records which resource was affected, the movement type (entry/exit), quantity, reason, date, and who performed it. Every movement automatically updates the resource's `current_stock` field. Exit movements that would cause negative stock are prevented. This is a backend-only feature (no UI — Wave 4 builds the frontend).

## User Story
As a restaurant operator
I want to track all inventory movements (entries and exits) with automatic stock updates
So that I always know my current stock levels, can audit stock changes, and prevent negative inventory

## Problem Statement
The RestaurantOS system has a Resource entity with `current_stock` and `minimum_stock` fields but no mechanism to track how stock changes over time. Without an inventory movement system, stock updates are manual and unauditable. There's no way to enforce business rules like preventing negative stock or automatically recording who changed what and why.

## Solution Statement
Build a complete backend CRUD system for inventory movements following the established RestaurantOS Clean Architecture pattern. The `InventoryMovement` entity records each stock change, and the `InventoryService` orchestrates the transactional logic: validate the resource exists, enforce non-negative stock for exit movements, create the movement record, and atomically update the resource's `current_stock`. A warning is logged when stock falls below `minimum_stock` (event creation deferred to issue #101).

## Relevant Files
Use these files to implement the feature:

- `apps/Server/main.py` — Register the new inventory movement router
- `apps/Server/src/config/database.py` — Base class for models, SessionLocal
- `apps/Server/src/adapter/rest/dependencies.py` — `get_db`, `get_current_user` dependencies
- `apps/Server/src/models/__init__.py` — Register the new InventoryMovement model
- `apps/Server/src/models/resource.py` — Resource model (referenced by inventory movements, stock updated here)
- `apps/Server/src/repository/resource_repository.py` — ResourceRepository with `get_by_id` and `update` used by the inventory service
- `apps/Server/src/core/services/resource_service.py` — ResourceService pattern reference (restaurant access check pattern)
- `apps/Server/src/adapter/rest/resource_routes.py` — Resource routes pattern reference (error handling, response mapping)
- `apps/Server/src/interface/resource_dto.py` — Resource DTO pattern reference (enums, BaseModel, Field usage)
- `apps/Server/src/repository/restaurant_repository.py` — `get_user_restaurant_role` used for authorization
- `apps/Server/database/create_resource_table.sql` — SQL migration pattern reference
- `apps/Server/tests/test_resource_api.py` — Test pattern reference (mock setup, auth token, assertions)
- `app_docs/feature-8d28116a-resource-entity-crud-backend.md` — Resource entity documentation (dependency context)
- `app_docs/feature-a692d2db-restaurant-multi-tenant-entity.md` — Restaurant multi-tenant scoping documentation

### New Files
- `apps/Server/database/create_inventory_movement_table.sql` — SQL migration for inventory_movement table
- `apps/Server/src/models/inventory_movement.py` — SQLAlchemy InventoryMovement model
- `apps/Server/src/interface/inventory_movement_dto.py` — Pydantic DTOs for inventory movements
- `apps/Server/src/repository/inventory_movement_repository.py` — Database operations for inventory movements
- `apps/Server/src/core/services/inventory_service.py` — Business logic for inventory movements with stock updates
- `apps/Server/src/adapter/rest/inventory_movement_routes.py` — REST API endpoints for inventory movements
- `apps/Server/tests/test_inventory_movement_model.py` — Unit tests for InventoryMovement model
- `apps/Server/tests/test_inventory_movement_api.py` — API integration tests for inventory movement endpoints

## Implementation Plan
### Phase 1: Foundation
Create the database migration SQL and SQLAlchemy model. Define Pydantic DTOs with enums for movement type and reason. These form the data layer that all other components depend on.

### Phase 2: Core Implementation
Build the repository for basic CRUD operations (create movement, query by resource, query by restaurant with filters). Then build the inventory service with the core business logic: resource validation, negative stock prevention, atomic movement creation + stock update, and low-stock warning logging.

### Phase 3: Integration
Create the REST routes with JWT authentication, register the router in `main.py`, register the model in `models/__init__.py`, and write comprehensive tests covering success paths, authorization, validation, and edge cases.

## Step by Step Tasks

### Step 1: Create SQL Migration
- Create `apps/Server/database/create_inventory_movement_table.sql` with the inventory_movement table definition
- Include columns: `id` (UUID PK), `resource_id` (FK to resource), `type` (VARCHAR(20)), `quantity` (DECIMAL(12,4)), `reason` (VARCHAR(100)), `date` (TIMESTAMP), `person_id` (FK to person, nullable), `restaurant_id` (UUID), `notes` (TEXT), `created_at` (TIMESTAMP)
- Add indexes on `resource_id`, `restaurant_id`, and `date`
- Follow the pattern in `create_resource_table.sql` (use `TIMESTAMP WITH TIME ZONE`, comment header with wave/issue info)

### Step 2: Create SQLAlchemy Model
- Create `apps/Server/src/models/inventory_movement.py` with class `InventoryMovement(Base)`
- Follow the pattern in `resource.py`: import from `src.config.database`, use `Column`, `UUID(as_uuid=True)`, `ForeignKey`, `DateTime(timezone=True)`, `Numeric(12, 4)`, `String`
- Map all columns from the SQL migration
- Add `__repr__` method
- Register in `apps/Server/src/models/__init__.py` by importing `InventoryMovement` and adding to `__all__`

### Step 3: Create Pydantic DTOs
- Create `apps/Server/src/interface/inventory_movement_dto.py`
- Define `MovementType(str, Enum)` with values `entry`, `exit`
- Define `MovementReason(str, Enum)` with values `compra`, `uso`, `produccion`, `merma`, `receta`, `ajuste`
- Define `InventoryMovementCreateDTO(BaseModel)` with fields: `resource_id` (UUID), `type` (MovementType), `quantity` (Decimal, gt=0), `reason` (MovementReason), `date` (Optional[datetime]), `person_id` (Optional[UUID]), `restaurant_id` (UUID), `notes` (Optional[str])
- Define `InventoryMovementResponseDTO(BaseModel)` with all fields plus `id`, `created_at`, and `model_config = {"from_attributes": True}`
- Follow the pattern in `resource_dto.py` for Field descriptions and model_config

### Step 4: Create Repository
- Create `apps/Server/src/repository/inventory_movement_repository.py` with class `InventoryMovementRepository`
- Implement `create(db, resource_id, type, quantity, reason, date, person_id, restaurant_id, notes)` — insert and return movement
- Implement `get_by_resource(db, resource_id, date_from=None, date_to=None)` — query movements for a resource with optional date range, ordered by date descending
- Implement `get_by_restaurant(db, restaurant_id, date_from=None, date_to=None, reason=None)` — query all movements for a restaurant with optional date range and reason filter, ordered by date descending
- Follow the `ResourceRepository` pattern: use `Session` param, `print` logging, singleton instance at module level
- Create singleton: `inventory_movement_repository = InventoryMovementRepository()`

### Step 5: Create Inventory Service
- Create `apps/Server/src/core/services/inventory_service.py` with class `InventoryService`
- Add `_check_restaurant_access(db, user_id, restaurant_id)` method using `restaurant_repository.get_user_restaurant_role` (same pattern as ResourceService)
- Implement `create_movement(db, user_id, data: InventoryMovementCreateDTO)`:
  1. Check restaurant access
  2. Validate resource exists via `resource_repository.get_by_id(db, data.resource_id)` — raise `ValueError("Resource not found")` if None
  3. Validate resource belongs to the same restaurant — raise `ValueError("Resource does not belong to this restaurant")` if mismatch
  4. For exit movements (`data.type == MovementType.EXIT`): check `resource.current_stock >= data.quantity` — raise `ValueError("Insufficient stock: current_stock is X but requested Y")` if not
  5. Create movement record via `inventory_movement_repository.create(...)`
  6. Update resource stock: `resource.current_stock += data.quantity` for entry, `resource.current_stock -= data.quantity` for exit
  7. Save resource via `resource_repository.update(db, resource)`
  8. If `resource.current_stock < resource.minimum_stock`: log `WARNING [InventoryService]: Resource 'X' is below minimum stock (current: Y, minimum: Z)`
  9. Return the created movement
- Implement `get_movements_by_resource(db, user_id, resource_id, date_from, date_to)`:
  1. Get resource, validate exists
  2. Check restaurant access using resource's restaurant_id
  3. Return `inventory_movement_repository.get_by_resource(db, resource_id, date_from, date_to)`
- Implement `get_movements_by_restaurant(db, user_id, restaurant_id, date_from, date_to, reason)`:
  1. Check restaurant access
  2. Return `inventory_movement_repository.get_by_restaurant(db, restaurant_id, date_from, date_to, reason)`
- All methods with INFO/ERROR `print` logging
- Create singleton: `inventory_service = InventoryService()`

### Step 6: Create REST Routes
- Create `apps/Server/src/adapter/rest/inventory_movement_routes.py`
- Define `router = APIRouter(prefix="/api/inventory-movements", tags=["Inventory Movements"])`
- Add `_to_response` helper that converts model to `InventoryMovementResponseDTO` using `model_validate(..., from_attributes=True)`
- Implement `POST ""` endpoint:
  - Accept `InventoryMovementCreateDTO` body
  - Depends on `get_db`, `get_current_user`
  - Call `inventory_service.create_movement(db, user_id, data)`
  - Return `InventoryMovementResponseDTO` with status 201
  - Handle `PermissionError` → 403, `ValueError` → 400 (for stock/validation errors) or 404 (for resource not found)
- Implement `GET ""` endpoint:
  - Accept query params: `resource_id` (Optional[UUID]), `restaurant_id` (Optional[UUID]), `date_from` (Optional[datetime]), `date_to` (Optional[datetime]), `reason` (Optional[MovementReason])
  - If `resource_id` provided: call `inventory_service.get_movements_by_resource`
  - Elif `restaurant_id` provided: call `inventory_service.get_movements_by_restaurant`
  - Else: return 400 "Either resource_id or restaurant_id is required"
  - Return `List[InventoryMovementResponseDTO]`
  - Handle `PermissionError` → 403, `ValueError` → 404
- Follow the error handling pattern from `resource_routes.py`

### Step 7: Register Router in main.py
- Import `from src.adapter.rest.inventory_movement_routes import router as inventory_movement_router`
- Add `app.include_router(inventory_movement_router)` after the event router
- Add `print("INFO [Main]: Inventory Movement router registered")`

### Step 8: Register Model in models/__init__.py
- Import `from src.models.inventory_movement import InventoryMovement`
- Add `"InventoryMovement"` to `__all__`

### Step 9: Create Model Unit Tests
- Create `apps/Server/tests/test_inventory_movement_model.py`
- Test InventoryMovement model instantiation with all fields
- Test default values (created_at)
- Test __repr__ method
- Follow the pattern in `test_resource_model.py`

### Step 10: Create API Integration Tests
- Create `apps/Server/tests/test_inventory_movement_api.py`
- Follow the pattern in `test_resource_api.py` (mock setup, auth token helpers, dependency overrides)
- Test sections:
  - **Create Movement Tests**:
    - `test_create_entry_movement_success` — verify 201, movement created, resource stock increased
    - `test_create_exit_movement_success` — verify 201, movement created, resource stock decreased
    - `test_create_exit_movement_insufficient_stock` — verify 400 when exit quantity > current_stock
    - `test_create_movement_resource_not_found` — verify 404 when resource_id is invalid
    - `test_create_movement_unauthenticated` — verify 401 without token
    - `test_create_movement_no_restaurant_access` — verify 403 when user lacks restaurant membership
    - `test_create_movement_invalid_quantity_zero` — verify 422 when quantity is 0
    - `test_create_movement_invalid_quantity_negative` — verify 422 when quantity is negative
  - **List Movements Tests**:
    - `test_list_movements_by_resource_success` — verify 200 with movement list
    - `test_list_movements_by_restaurant_success` — verify 200 with movement list
    - `test_list_movements_missing_filter` — verify 400 when neither resource_id nor restaurant_id provided
    - `test_list_movements_no_restaurant_access` — verify 403
  - Mock `inventory_movement_repository`, `resource_repository`, `restaurant_repository` in `src.core.services.inventory_service` namespace

### Step 11: Run Validation Commands
- Run `cd apps/Server && python -m pytest tests/ -v` to verify all tests pass
- Run `cd apps/Client && npx tsc --noEmit` to verify no TypeScript regressions
- Run `cd apps/Client && npm run build` to verify client build succeeds

## Testing Strategy
### Unit Tests
- **Model tests** (`test_inventory_movement_model.py`): Verify InventoryMovement model instantiation, field types, default values, and `__repr__`
- **API tests** (`test_inventory_movement_api.py`): Verify all endpoint behaviors through mocked dependencies:
  - POST create movement (entry and exit types)
  - GET list movements (by resource, by restaurant, with filters)
  - Authorization checks (unauthenticated, no restaurant access)
  - Validation checks (invalid quantity, missing resource, insufficient stock)

### Edge Cases
- Exit movement where quantity exactly equals current_stock (should succeed, stock becomes 0)
- Exit movement where quantity exceeds current_stock by a tiny amount (should fail)
- Entry movement that brings stock from below minimum_stock to above it (should not warn)
- Exit movement that drops stock from above minimum_stock to below it (should log warning)
- Movement with person_id that is None (nullable FK)
- Movement with custom date vs default date
- Multiple concurrent movements on the same resource (repository uses commit per operation)
- Resource restaurant_id mismatch with movement restaurant_id

## Acceptance Criteria
- `inventory_movement` table SQL migration file exists with correct schema and indexes
- SQLAlchemy `InventoryMovement` model maps all columns correctly
- Pydantic DTOs enforce `quantity > 0`, valid `MovementType` and `MovementReason` enums
- `POST /api/inventory-movements` creates a movement and atomically updates `resource.current_stock`
- Entry movements increment stock; exit movements decrement stock
- Exit movements are rejected with 400 if `quantity > resource.current_stock`
- A warning is logged when stock drops below `minimum_stock` after a movement
- `GET /api/inventory-movements?resource_id=X` returns movement history for a resource
- `GET /api/inventory-movements?restaurant_id=X` returns all movements with optional `date_from`, `date_to`, `reason` filters
- All endpoints require JWT authentication (401 without token)
- Restaurant-scoped authorization is enforced (403 for non-members)
- All tests pass with zero regressions
- Router is registered in `main.py`
- Model is registered in `models/__init__.py`

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/ -v` — Run all Server tests to validate inventory movement feature and zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate no TypeScript regressions
- `cd apps/Client && npm run build` — Run Client build to validate no build regressions

## Notes
- This is a **backend-only** feature. No frontend UI changes are needed (Wave 4 builds the frontend).
- The low-stock warning is currently a `print(WARNING ...)` log only. Issue #101 (Wave 8) will wire this up to automatically create an `alerta_stock` Event.
- The `restaurant_id` column on `inventory_movement` is intentionally not a FK to `restaurant` table in the migration (matching the issue spec). The resource's `restaurant_id` FK already provides referential integrity. The service layer validates that `resource.restaurant_id == data.restaurant_id`.
- No new pip dependencies are required.
- The `person_id` FK references the `person` table with `ON DELETE SET NULL` — if a person is deleted, the movement record is preserved with `person_id = NULL`.
