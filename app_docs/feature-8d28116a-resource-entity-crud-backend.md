# Resource Entity CRUD Backend

**ADW ID:** 8d28116a
**Date:** 2026-03-03
**Specification:** specs/issue-80-adw-8d28116a-sdlc_planner-resource-entity-crud-backend.md

## Overview

Full backend CRUD implementation for the Resource entity in RestaurantOS (Wave 1, ROS-003). A Resource represents physical items within a restaurant — products (ingredients), assets (equipment), or services — with stock level tracking and low-stock detection. All operations are scoped to a restaurant via `restaurant_id` for multi-tenant isolation.

## What Was Built

- SQL migration for the `resource` table with DECIMAL(12,4) stock fields and indexes
- SQLAlchemy `Resource` model with UUID primary key and restaurant foreign key
- Pydantic DTOs with `ResourceType` enum (producto, activo, servicio), non-negative validation, and computed `is_low_stock` field
- Repository layer with CRUD operations plus `get_low_stock` query
- Service layer with restaurant-scoped authorization and low-stock warning logging
- REST API with 6 endpoints under `/api/resources` (CRUD + low-stock)
- Comprehensive unit tests (DTO validation, model) and API integration tests

## Technical Implementation

### Files Modified

- `apps/Server/main.py`: Registered `resource_router` import and `app.include_router(resource_router)`
- `apps/Server/src/models/__init__.py`: Added `Resource` to model imports and `__all__` exports

### Files Created

- `apps/Server/database/create_resource_table.sql`: SQL migration with UUID PK, `restaurant_id` FK (CASCADE), `type` VARCHAR(50), `name` VARCHAR(255), `unit` VARCHAR(50), stock DECIMAL(12,4) fields, indexes on `restaurant_id` and `type`, `updated_at` trigger
- `apps/Server/src/models/resource.py`: SQLAlchemy model mapping all columns with `Numeric(12, 4)` for stock/cost fields
- `apps/Server/src/interface/resource_dto.py`: `ResourceType` enum, `ResourceCreateDTO` (with `ge=0` validation on stock/cost), `ResourceUpdateDTO` (all optional for partial updates), `ResourceResponseDTO` (with `@model_validator` computing `is_low_stock`)
- `apps/Server/src/repository/resource_repository.py`: `ResourceRepository` with `create`, `get_by_id`, `get_by_restaurant` (optional type filter), `update`, `delete`, `get_low_stock` methods; singleton instance
- `apps/Server/src/core/services/resource_service.py`: `ResourceService` with `_check_restaurant_access` authorization, CRUD methods, low-stock WARNING logging after create/update; singleton instance
- `apps/Server/src/adapter/rest/resource_routes.py`: 6 endpoints with JWT auth, `_to_response` helper for DTO conversion
- `apps/Server/tests/test_resource_model.py`: 434 lines — DTO validation tests (required fields, max_length, non-negative constraints, enum values, defaults), `is_low_stock` computation, model `__repr__` and `__tablename__`
- `apps/Server/tests/test_resource_api.py`: 718 lines — API endpoint tests with mocked DB/auth covering success, 401, 403, 404, 422 scenarios

### Key Changes

- **ResourceType enum**: `producto`, `activo`, `servicio` — stored as VARCHAR in DB, validated via Pydantic `str, Enum`
- **Computed `is_low_stock`**: Calculated in `ResourceResponseDTO` via `@model_validator(mode='before')` — `True` when `current_stock < minimum_stock`, `False` when equal or above
- **Low-stock endpoint ordering**: `GET /api/resources/low-stock` is defined before `GET /api/resources/{resource_id}` to prevent FastAPI from interpreting "low-stock" as a UUID path parameter
- **Authorization**: Uses `restaurant_repository.get_user_restaurant_role()` to verify user membership in the restaurant before any operation; raises `PermissionError` → HTTP 403
- **Low-stock logging**: Service logs `WARNING` when stock drops below minimum after create or update (actual Event creation deferred to issue #101)

## How to Use

1. **Run the SQL migration** against your PostgreSQL database:
   ```bash
   psql $DATABASE_URL -f apps/Server/database/create_resource_table.sql
   ```

2. **Create a resource** — `POST /api/resources` with JWT token:
   ```json
   {
     "restaurant_id": "uuid",
     "type": "producto",
     "name": "Flour",
     "unit": "kg",
     "current_stock": 50.0,
     "minimum_stock": 10.0,
     "last_unit_cost": 2.50
   }
   ```

3. **List resources** — `GET /api/resources?restaurant_id={uuid}&type=producto`

4. **Get a resource** — `GET /api/resources/{resource_id}`

5. **Update a resource** (partial) — `PUT /api/resources/{resource_id}`:
   ```json
   { "current_stock": 5.0 }
   ```

6. **Delete a resource** — `DELETE /api/resources/{resource_id}` (returns 204)

7. **Check low-stock resources** — `GET /api/resources/low-stock?restaurant_id={uuid}`

## Configuration

No new environment variables required. The resource feature uses the existing database connection (`DATABASE_URL`) and JWT authentication (`JWT_SECRET_KEY`).

## Testing

```bash
# Resource DTO and model unit tests
cd apps/Server && python -m pytest tests/test_resource_model.py -v

# Resource API endpoint integration tests
cd apps/Server && python -m pytest tests/test_resource_api.py -v

# All server tests (zero regression check)
cd apps/Server && python -m pytest tests/ -v
```

## Notes

- **Backend-only feature** — no UI components or E2E tests
- Part of RestaurantOS **Wave 1** (ROS-003), runs in parallel with Restaurant (ROS-001) and Person (ROS-002)
- Wave 2 (Inventory Movements, ROS-006) will track stock changes for resources
- Wave 4 (Recipe Management) will reference resources as ingredients
- Low-stock detection is **logging only** for now; Event creation deferred to issue #101 (Wave 8)
