# Inventory Movement Tracking

**ADW ID:** 02529be1
**Date:** 2026-03-03
**Specification:** specs/issue-83-adw-02529be1-sdlc_planner-inventory-movement-tracking.md

## Overview

Backend-only feature that adds a complete inventory movement tracking system to RestaurantOS. It introduces the `inventory_movement` table and a full CRUD API for recording stock entries and exits, with automatic `current_stock` updates on the associated resource and negative-stock prevention.

## What Was Built

- SQL migration for the `inventory_movement` table with indexes on resource, restaurant, and date
- SQLAlchemy `InventoryMovement` model registered in the models package
- Pydantic DTOs with `MovementType` (entry/exit) and `MovementReason` (compra, uso, produccion, merma, receta, ajuste) enums
- `InventoryMovementRepository` with create, get-by-resource, and get-by-restaurant queries (with date range and reason filters)
- `InventoryService` with transactional business logic: resource validation, restaurant-scoped authorization, negative-stock prevention, atomic stock updates, and low-stock warning logging
- REST API endpoints: `POST /api/inventory-movements` and `GET /api/inventory-movements` with JWT authentication
- Comprehensive test suite: 602-line API integration tests and 261-line model unit tests

## Technical Implementation

### Files Modified

- `apps/Server/main.py`: Registered `inventory_movement_router` and added startup log
- `apps/Server/src/models/__init__.py`: Registered `InventoryMovement` in model exports

### New Files

- `apps/Server/database/create_inventory_movement_table.sql`: Table schema with UUID PK, FKs to resource and person, and three indexes
- `apps/Server/src/models/inventory_movement.py`: SQLAlchemy model (43 lines) mapping all columns
- `apps/Server/src/interface/inventory_movement_dto.py`: `InventoryMovementCreateDTO` (with `quantity > 0` validation) and `InventoryMovementResponseDTO`
- `apps/Server/src/repository/inventory_movement_repository.py`: CRUD operations with date range and reason filtering, ordered by date descending
- `apps/Server/src/core/services/inventory_service.py`: Business logic orchestrator (170 lines) handling authorization, validation, stock math, and low-stock warnings
- `apps/Server/src/adapter/rest/inventory_movement_routes.py`: Two endpoints with proper error mapping (PermissionError -> 403, ValueError -> 400/404)
- `apps/Server/tests/test_inventory_movement_api.py`: API integration tests (602 lines)
- `apps/Server/tests/test_inventory_movement_model.py`: Model unit tests (261 lines)

### Key Changes

- **Atomic stock updates**: Creating a movement automatically increments (entry) or decrements (exit) the resource's `current_stock` in the same transaction
- **Negative stock prevention**: Exit movements are rejected with HTTP 400 if the requested quantity exceeds the resource's current stock
- **Restaurant-scoped authorization**: All operations verify user membership in the target restaurant via `restaurant_repository.get_user_restaurant_role`
- **Resource-restaurant validation**: The service verifies that the target resource belongs to the specified restaurant before creating a movement
- **Low-stock warnings**: A `WARNING` log is emitted when a movement causes stock to drop below `minimum_stock` (event creation deferred to issue #101)

## How to Use

1. **Create an inventory entry** (stock in):
   ```
   POST /api/inventory-movements
   Authorization: Bearer <token>
   {
     "resource_id": "<uuid>",
     "type": "entry",
     "quantity": 50.0,
     "reason": "compra",
     "restaurant_id": "<uuid>",
     "notes": "Weekly supply order"
   }
   ```

2. **Create an inventory exit** (stock out):
   ```
   POST /api/inventory-movements
   {
     "resource_id": "<uuid>",
     "type": "exit",
     "quantity": 10.0,
     "reason": "uso",
     "restaurant_id": "<uuid>"
   }
   ```

3. **List movements by resource**:
   ```
   GET /api/inventory-movements?resource_id=<uuid>&date_from=2026-01-01&date_to=2026-03-01
   ```

4. **List movements by restaurant** (with optional reason filter):
   ```
   GET /api/inventory-movements?restaurant_id=<uuid>&reason=compra
   ```

## Configuration

No new environment variables or dependencies required. The feature uses existing database connections and JWT authentication.

## Testing

Run the full server test suite:
```bash
cd apps/Server && python -m pytest tests/ -v
```

Key test files:
- `tests/test_inventory_movement_model.py` — Model instantiation, defaults, repr
- `tests/test_inventory_movement_api.py` — Endpoint behavior: success paths, auth (401/403), validation (400/422), not-found (404), insufficient stock

## Notes

- **Backend only** — No frontend UI changes. Wave 4 will build the inventory management frontend.
- The `restaurant_id` column on `inventory_movement` is intentionally not a FK to the restaurant table; referential integrity is enforced through the resource's `restaurant_id` FK and service-layer validation.
- `person_id` uses `ON DELETE SET NULL` — deleting a person preserves the movement record with null person.
- Low-stock warnings are currently log-only. Issue #101 (Wave 8) will wire them to automatically create `alerta_stock` events.
