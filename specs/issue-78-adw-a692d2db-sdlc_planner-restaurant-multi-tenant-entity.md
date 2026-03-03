# Feature: Restaurant Multi-Tenant Entity

## Metadata
issue_number: `78`
adw_id: `a692d2db`
issue_json: ``

## Feature Description
Create the `restaurant` table that serves as the multi-tenant scope for the RestaurantOS module. A restaurant represents a single restaurant location/business. All future RestaurantOS entities (Person, Document, Event, Resource, Inventory Movement) will be scoped to a restaurant via `restaurant_id`. This is analogous to the existing "entity" concept in the Finance Tracker, but specialized for restaurant operations. Users can belong to multiple restaurants via a `user_restaurants` junction table with per-restaurant roles.

This is Wave 1, Issue ROS-001 of the Restaurant Operating System — the foundational multi-tenant entity that all downstream features depend on.

## User Story
As a restaurant owner or manager
I want to create and manage restaurant records with multi-user membership
So that all RestaurantOS data (people, documents, events, resources) can be scoped to a specific restaurant

## Problem Statement
The RestaurantOS module needs a multi-tenant foundation so that all downstream entities can be scoped to a specific restaurant. Without this, there is no way to separate data between different restaurant locations/businesses, and no way to control user access per restaurant.

## Solution Statement
Create a `restaurant` table with UUID primary key, name, address, and owner reference, along with a `user_restaurants` junction table for multi-restaurant user membership with per-restaurant roles. Implement full Clean Architecture backend: SQLAlchemy models, Pydantic DTOs, repository, service (with authorization), and REST routes. All endpoints require JWT authentication. The creator automatically becomes the restaurant's owner and admin.

## Relevant Files
Use these files to implement the feature:

**Existing files to reference for patterns:**
- `apps/Server/main.py` — Entry point, where the new restaurant router will be registered. Follow the existing router import and registration pattern.
- `apps/Server/src/models/entity.py` — Pattern for SQLAlchemy model with UUID, timestamps. Follow same Column types and Base import.
- `apps/Server/src/models/user_entity.py` — Pattern for junction table model with UniqueConstraint. Mirror for `UserRestaurant`.
- `apps/Server/src/models/__init__.py` — Must add new models to exports.
- `apps/Server/src/interface/entity_dto.py` — Pattern for Pydantic DTOs (Create, Update, Response) with Field validation and `from_attributes`.
- `apps/Server/src/repository/entity_repository.py` — Pattern for repository class with CRUD methods, logging, singleton instance.
- `apps/Server/src/core/services/entity_service.py` — Pattern for service class with authorization checks, PermissionError/ValueError handling.
- `apps/Server/src/adapter/rest/entity_routes.py` — Pattern for REST routes with Depends injection, error handling, status codes.
- `apps/Server/src/adapter/rest/dependencies.py` — `get_db` and `get_current_user` dependencies to inject.
- `apps/Server/src/config/database.py` — `Base` declarative base import for models.
- `apps/Server/database/schema.sql` — Existing schema for reference on table creation patterns (UUID, timestamps, FK conventions).
- `apps/Server/tests/test_entity.py` — Pattern for API endpoint tests with mock DB, AsyncClient, auth token helpers.

**Conditional documentation to read:**
- `app_docs/feature-0f0d4c36-fastapi-backend-setup.md` — Adding new routers/API endpoints to the Server.
- `app_docs/feature-db5f36c7-database-schema-tables.md` — Working with database tables and schema.
- `app_docs/feature-ed4cef49-backend-jwt-auth-rbac.md` — Working with backend authentication and protected routes.

### New Files
- `apps/Server/database/create_restaurant_tables.sql` — SQL migration for `restaurant` and `user_restaurants` tables.
- `apps/Server/src/models/restaurant.py` — SQLAlchemy `Restaurant` model.
- `apps/Server/src/models/user_restaurant.py` — SQLAlchemy `UserRestaurant` junction table model.
- `apps/Server/src/interface/restaurant_dto.py` — Pydantic DTOs for restaurant CRUD.
- `apps/Server/src/repository/restaurant_repository.py` — Restaurant data access layer.
- `apps/Server/src/core/services/restaurant_service.py` — Restaurant business logic with authorization.
- `apps/Server/src/adapter/rest/restaurant_routes.py` — REST API endpoints for restaurant CRUD.
- `apps/Server/tests/test_restaurant_model.py` — Unit tests for restaurant Pydantic DTOs.
- `apps/Server/tests/test_restaurant_api.py` — API endpoint tests for restaurant routes.

## Implementation Plan
### Phase 1: Foundation
Create the database migration SQL and SQLAlchemy models for the `restaurant` and `user_restaurants` tables. These form the data layer that all other components build on.

### Phase 2: Core Implementation
Build the DTO, repository, service, and routes layers following Clean Architecture. The repository handles raw data access, the service handles business logic and authorization (owner/admin checks), and the routes expose the REST API with JWT authentication.

### Phase 3: Integration
Register the restaurant router in `main.py`, export models from `__init__.py`, and add the SQL to `schema.sql`. Write comprehensive tests for both DTOs and API endpoints.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create Database Migration
- Create `apps/Server/database/create_restaurant_tables.sql` with the following SQL:
  ```sql
  -- Restaurant Multi-Tenant Entity Tables
  -- RestaurantOS Wave 1: ROS-001

  CREATE TABLE restaurant (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      name VARCHAR(255) NOT NULL,
      address TEXT,
      owner_id UUID REFERENCES users(id),
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
      updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
  );

  CREATE TABLE user_restaurants (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      user_id UUID NOT NULL REFERENCES users(id),
      restaurant_id UUID NOT NULL REFERENCES restaurant(id) ON DELETE CASCADE,
      role VARCHAR(50) NOT NULL DEFAULT 'user',
      created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
      UNIQUE(user_id, restaurant_id)
  );

  -- Indexes for common queries
  CREATE INDEX idx_user_restaurants_user_id ON user_restaurants(user_id);
  CREATE INDEX idx_user_restaurants_restaurant_id ON user_restaurants(restaurant_id);
  CREATE INDEX idx_restaurant_owner_id ON restaurant(owner_id);

  -- Trigger for auto-updating updated_at on restaurant
  CREATE TRIGGER update_restaurant_updated_at
      BEFORE UPDATE ON restaurant
      FOR EACH ROW
      EXECUTE FUNCTION update_updated_at_column();
  ```
- Also append the restaurant and user_restaurants table definitions to `apps/Server/database/schema.sql` at the end, following the existing pattern (with comments separating sections).

### Step 2: Create SQLAlchemy Models
- Create `apps/Server/src/models/restaurant.py`:
  - Class `Restaurant(Base)` with `__tablename__ = "restaurant"`
  - Columns: `id` (UUID PK, default uuid4), `name` (String(255), not null), `address` (Text, nullable), `owner_id` (UUID FK to users.id, nullable), `created_at` (DateTime with timezone, default utcnow), `updated_at` (DateTime with timezone, onupdate utcnow)
  - Follow exact pattern from `entity.py` for Column types and imports
  - Add `__repr__` method
- Create `apps/Server/src/models/user_restaurant.py`:
  - Class `UserRestaurant(Base)` with `__tablename__ = "user_restaurants"`
  - Columns: `id` (UUID PK), `user_id` (UUID FK to users.id, CASCADE, not null), `restaurant_id` (UUID FK to restaurant.id, CASCADE, not null), `role` (String(50), default "user", not null), `created_at` (DateTime with timezone)
  - Add `UniqueConstraint("user_id", "restaurant_id", name="user_restaurants_unique")` in `__table_args__`
  - Follow exact pattern from `user_entity.py`
  - Add `__repr__` method
- Update `apps/Server/src/models/__init__.py`:
  - Add imports for `Restaurant` and `UserRestaurant`
  - Add them to `__all__` list

### Step 3: Create Pydantic DTOs
- Create `apps/Server/src/interface/restaurant_dto.py`:
  - `RestaurantCreateDTO(BaseModel)`: `name` (str, required, min_length=1, max_length=255), `address` (Optional[str], default None)
  - `RestaurantUpdateDTO(BaseModel)`: `name` (Optional[str], min_length=1, max_length=255), `address` (Optional[str])
  - `RestaurantResponseDTO(BaseModel)`: `id` (UUID), `name` (str), `address` (Optional[str]), `owner_id` (Optional[UUID]), `created_at` (datetime), `updated_at` (Optional[datetime]). Set `model_config = {"from_attributes": True}`
  - `RestaurantListDTO(BaseModel)`: `restaurants` (list[RestaurantResponseDTO])
  - Follow exact pattern from `entity_dto.py` with Field(...) descriptions

### Step 4: Create Repository
- Create `apps/Server/src/repository/restaurant_repository.py`:
  - Class `RestaurantRepository` with methods:
    - `create_restaurant(db, name, address, owner_id)` → Creates `Restaurant` record, then creates `UserRestaurant` entry for owner with role "admin". Returns Restaurant.
    - `get_restaurant_by_id(db, restaurant_id)` → Returns Optional[Restaurant]
    - `get_restaurants_by_user(db, user_id)` → Joins `Restaurant` with `UserRestaurant`, filters by user_id. Returns list[Restaurant].
    - `update_restaurant(db, restaurant)` → Commits updated Restaurant object. Returns Restaurant.
    - `delete_restaurant(db, restaurant_id)` → Deletes restaurant by ID. Returns bool.
    - `get_user_restaurant_role(db, user_id, restaurant_id)` → Returns Optional[str] role.
    - `add_user_to_restaurant(db, user_id, restaurant_id, role)` → Creates UserRestaurant. Returns UserRestaurant.
  - All methods include logging with `print(f"INFO [RestaurantRepository]: ...")`
  - Singleton instance: `restaurant_repository = RestaurantRepository()`
  - Follow exact pattern from `entity_repository.py`

### Step 5: Create Service
- Create `apps/Server/src/core/services/restaurant_service.py`:
  - Class `RestaurantService` with methods:
    - `create_restaurant(db, user_id, data: RestaurantCreateDTO)` → Creates restaurant with user as owner/admin. Returns Restaurant.
    - `get_user_restaurants(db, user_id)` → Returns list[Restaurant] the user belongs to.
    - `get_restaurant(db, restaurant_id, user_id)` → Gets restaurant if user has access. Raises PermissionError if no access.
    - `update_restaurant(db, restaurant_id, user_id, data: RestaurantUpdateDTO)` → Updates if user is owner or admin. Raises PermissionError or ValueError.
    - `delete_restaurant(db, restaurant_id, user_id)` → Deletes if user is owner or admin. Raises PermissionError or ValueError.
  - Authorization pattern: check `get_user_restaurant_role()` — owner or admin can update/delete.
  - All methods include logging with `print(f"INFO [RestaurantService]: ...")`
  - Singleton instance: `restaurant_service = RestaurantService()`
  - Follow exact pattern from `entity_service.py`

### Step 6: Create REST Routes
- Create `apps/Server/src/adapter/rest/restaurant_routes.py`:
  - `router = APIRouter(prefix="/api/restaurants", tags=["Restaurants"])`
  - Endpoints:
    - `POST /api/restaurants` (201) → Creates restaurant, returns RestaurantResponseDTO
    - `GET /api/restaurants` (200) → Lists restaurants for authenticated user, returns list[RestaurantResponseDTO]
    - `GET /api/restaurants/{restaurant_id}` (200) → Gets restaurant detail, returns RestaurantResponseDTO
    - `PUT /api/restaurants/{restaurant_id}` (200) → Updates restaurant, returns RestaurantResponseDTO
    - `DELETE /api/restaurants/{restaurant_id}` (204) → Deletes restaurant
  - All endpoints use `Depends(get_db)` and `Depends(get_current_user)`
  - Error handling: PermissionError → 403, ValueError → 404
  - All endpoints include logging with `print(f"INFO [RestaurantRoutes]: ...")`
  - Follow exact pattern from `entity_routes.py`

### Step 7: Register Router in main.py
- Add import at top of `apps/Server/main.py`:
  ```python
  from src.adapter.rest.restaurant_routes import router as restaurant_router
  ```
- Add `app.include_router(restaurant_router)` after the prospect router registration
- Add `print("INFO [Main]: Restaurant router registered")` log line

### Step 8: Create DTO Unit Tests
- Create `apps/Server/tests/test_restaurant_model.py`:
  - Test `RestaurantCreateDTO` with valid data (name only, name + address)
  - Test `RestaurantCreateDTO` with invalid data (empty name, name too long, missing name)
  - Test `RestaurantUpdateDTO` with partial updates (name only, address only, both, neither)
  - Test `RestaurantResponseDTO` with `from_attributes` model config
  - Test `RestaurantListDTO` with list of restaurants
  - Follow pattern from existing `test_prospect_model.py`
  - Include `print("INFO [TestRestaurant]: test_name - PASSED")` for each test

### Step 9: Create API Endpoint Tests
- Create `apps/Server/tests/test_restaurant_api.py`:
  - Helper functions: `get_mock_db()`, `create_mock_user()`, `create_mock_restaurant()`, `create_mock_user_restaurant()`, `get_auth_token()`
  - Pre-computed `PASSWORD_HASH` constant
  - Test cases:
    - `test_create_restaurant_success` — POST creates restaurant and returns 201
    - `test_create_restaurant_unauthenticated` — POST without token returns 401
    - `test_create_restaurant_invalid_name` — POST with empty name returns 422
    - `test_list_restaurants_success` — GET returns user's restaurants
    - `test_list_restaurants_empty` — GET returns empty list
    - `test_get_restaurant_success` — GET by ID returns restaurant
    - `test_get_restaurant_no_access` — GET by ID without membership returns 403
    - `test_get_restaurant_not_found` — GET by ID for nonexistent returns 404
    - `test_update_restaurant_success` — PUT updates and returns 200
    - `test_update_restaurant_no_permission` — PUT without admin/owner returns 403
    - `test_delete_restaurant_success` — DELETE returns 204
    - `test_delete_restaurant_no_permission` — DELETE without admin/owner returns 403
  - Follow exact pattern from `test_entity.py` with AsyncClient, ASGITransport, patch decorators
  - Include `print("INFO [TestRestaurantAPI]: test_name - PASSED")` for each test

### Step 10: Run Validation Commands
- Run all validation commands listed in the Validation Commands section below to ensure zero regressions.

## Testing Strategy
### Unit Tests
- **DTO Validation Tests** (`test_restaurant_model.py`): Validate Pydantic DTOs accept valid data and reject invalid data (missing required fields, exceeding max length, wrong types).
- **API Endpoint Tests** (`test_restaurant_api.py`): Test all CRUD endpoints with mocked DB and services. Cover success paths, authentication failures, authorization failures, and not-found cases.

### Edge Cases
- Creating a restaurant with the maximum-length name (255 chars)
- Creating a restaurant with no address (address is optional)
- Attempting to update a restaurant as a non-owner/non-admin user
- Attempting to delete a restaurant as a non-owner/non-admin user
- Listing restaurants when user belongs to none (empty list)
- Getting a restaurant the user has no membership in
- Creating a restaurant when unauthenticated (no JWT token)

## Acceptance Criteria
- `restaurant` and `user_restaurants` tables are defined in SQL migration and schema.sql
- SQLAlchemy models `Restaurant` and `UserRestaurant` correctly map to the tables
- Pydantic DTOs validate input (name required, max 255 chars) and serialize output
- Repository implements CRUD operations with proper logging
- Service implements authorization (only owner/admin can update/delete)
- REST routes expose all 5 CRUD endpoints under `/api/restaurants`
- All endpoints require JWT authentication
- Creating a restaurant automatically adds the creator as owner and admin member
- All tests pass with zero failures
- Existing tests continue to pass (zero regressions)

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/test_restaurant_model.py -v` — Run restaurant DTO unit tests
- `cd apps/Server && python -m pytest tests/test_restaurant_api.py -v` — Run restaurant API endpoint tests
- `cd apps/Server && python -m pytest tests/ -v` — Run all Server tests to validate zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate no regressions
- `cd apps/Client && npm run build` — Run Client build to validate no regressions

## Notes
- This is a **backend-only** feature (no UI). The issue body explicitly states "UI Language: N/A (backend only)".
- This feature runs in **parallel** with ROS-002 and ROS-003 (Wave 1), so there are no dependencies on other in-progress issues.
- All downstream RestaurantOS entities (Person, Document, Event, Resource, Inventory Movement) will reference `restaurant_id` as a foreign key for multi-tenant scoping.
- The `restaurant` table uses `gen_random_uuid()` in the SQL migration (PostgreSQL native) but `uuid.uuid4` in the SQLAlchemy model (Python-side default), consistent with existing patterns.
- The issue specifies the `restaurant` table uses `owner_id` referencing `users(id)` which differs slightly from the `entity` model. This is intentional — restaurants have a dedicated owner concept.
- The `user_restaurants` junction table mirrors `user_entities` but scoped to restaurants, allowing users to belong to multiple restaurants with different roles.
- No new libraries are needed — all dependencies (FastAPI, SQLAlchemy, Pydantic, pytest, httpx) are already in requirements.txt.
