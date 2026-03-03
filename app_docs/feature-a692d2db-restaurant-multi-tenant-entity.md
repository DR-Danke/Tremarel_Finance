# Restaurant Multi-Tenant Entity

**ADW ID:** a692d2db
**Date:** 2026-03-03
**Specification:** specs/issue-78-adw-a692d2db-sdlc_planner-restaurant-multi-tenant-entity.md

## Overview

Implements the foundational multi-tenant `restaurant` entity for the RestaurantOS module (Wave 1, ROS-001). This backend-only feature adds a `restaurant` table with UUID primary key and a `user_restaurants` junction table for multi-restaurant user membership with per-restaurant roles. All future RestaurantOS entities (Person, Document, Event, Resource, Inventory Movement) will be scoped to a restaurant via `restaurant_id`.

## What Was Built

- **Database tables**: `restaurant` and `user_restaurants` with SQL migration and schema definitions
- **SQLAlchemy models**: `Restaurant` and `UserRestaurant` with UUID primary keys, timestamps, and foreign keys
- **Pydantic DTOs**: `RestaurantCreateDTO`, `RestaurantUpdateDTO`, `RestaurantResponseDTO`, `RestaurantListDTO` with Field validation
- **Repository layer**: `RestaurantRepository` with CRUD operations and user-restaurant membership management
- **Service layer**: `RestaurantService` with authorization (owner/admin checks for update/delete)
- **REST API**: Five CRUD endpoints under `/api/restaurants` with JWT authentication
- **Tests**: DTO unit tests and API endpoint tests with mocked DB and auth

## Technical Implementation

### Files Modified

- `apps/Server/database/create_restaurant_tables.sql`: Standalone SQL migration for `restaurant` and `user_restaurants` tables with indexes and `updated_at` trigger
- `apps/Server/database/schema.sql`: Appended `restaurant` and `user_restaurants` table definitions to the main schema file
- `apps/Server/src/models/restaurant.py`: `Restaurant` SQLAlchemy model (id, name, address, owner_id, created_at, updated_at)
- `apps/Server/src/models/user_restaurant.py`: `UserRestaurant` junction table model with UniqueConstraint on (user_id, restaurant_id)
- `apps/Server/src/models/__init__.py`: Added `Restaurant` and `UserRestaurant` to model exports
- `apps/Server/src/interface/restaurant_dto.py`: Pydantic DTOs for create, update, response, and list operations
- `apps/Server/src/repository/restaurant_repository.py`: Data access with create, get, list, update, delete, role lookup, and add-user methods
- `apps/Server/src/core/services/restaurant_service.py`: Business logic with authorization enforcement
- `apps/Server/src/adapter/rest/restaurant_routes.py`: REST API endpoints with JWT dependency injection
- `apps/Server/main.py`: Registered `restaurant_router` in the FastAPI app
- `apps/Server/tests/test_restaurant_model.py`: DTO validation unit tests
- `apps/Server/tests/test_restaurant_api.py`: API endpoint integration tests

### Key Changes

- **Multi-tenant scoping**: The `restaurant` table uses `owner_id` referencing `users(id)`, giving each restaurant a dedicated owner. This differs from the existing `entity` model and is intentional for RestaurantOS.
- **Automatic owner membership**: Creating a restaurant automatically adds the creator as both owner (`owner_id` column) and admin member (`user_restaurants` entry with role "admin").
- **Authorization model**: Update and delete operations require "admin" role in `user_restaurants`. Read access requires any membership. The service layer enforces these checks before repository calls.
- **Cascade delete**: The `user_restaurants` junction table uses `ON DELETE CASCADE` on `restaurant_id`, so deleting a restaurant automatically removes all membership records.
- **Pattern consistency**: Follows the exact same Clean Architecture layers as the existing Entity CRUD — models, DTOs, repository, service, routes — making it easy to navigate for both developers and AI agents.

## How to Use

1. **Create a restaurant**: `POST /api/restaurants` with JSON body `{"name": "My Restaurant", "address": "123 Main St"}`. Requires JWT auth. The authenticated user becomes the owner and admin automatically.
2. **List restaurants**: `GET /api/restaurants` returns all restaurants the authenticated user belongs to.
3. **Get restaurant details**: `GET /api/restaurants/{restaurant_id}` returns a single restaurant. User must be a member.
4. **Update a restaurant**: `PUT /api/restaurants/{restaurant_id}` with JSON body `{"name": "New Name"}`. Only owner or admin can update.
5. **Delete a restaurant**: `DELETE /api/restaurants/{restaurant_id}`. Only owner or admin can delete. Returns 204 No Content.

## Configuration

No additional configuration is required. The feature uses the existing database connection, JWT auth, and CORS settings. The SQL migration (`create_restaurant_tables.sql`) must be run against the database to create the tables.

## Testing

```bash
# Run restaurant DTO unit tests
cd apps/Server && python -m pytest tests/test_restaurant_model.py -v

# Run restaurant API endpoint tests
cd apps/Server && python -m pytest tests/test_restaurant_api.py -v

# Run all Server tests (verify zero regressions)
cd apps/Server && python -m pytest tests/ -v
```

## Notes

- This is a **backend-only** feature — no UI components were added.
- This is part of RestaurantOS Wave 1 and runs in parallel with ROS-002 and ROS-003.
- All downstream RestaurantOS entities will reference `restaurant_id` as a foreign key for multi-tenant scoping.
- The `restaurant` table uses `gen_random_uuid()` in SQL (PostgreSQL native) and `uuid.uuid4` in the SQLAlchemy model (Python-side default), consistent with existing patterns.
