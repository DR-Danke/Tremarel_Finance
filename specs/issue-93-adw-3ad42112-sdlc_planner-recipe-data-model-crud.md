# Feature: Recipe Data Model & CRUD

## Metadata
issue_number: `93`
adw_id: `3ad42112`
issue_json: ``

## Feature Description
Create the Recipe entity for RestaurantOS with full CRUD operations and automatic cost/margin calculation. A Recipe represents a menu dish with a sale price. Each recipe contains RecipeItems that link to Resource ingredients with quantities. The recipe's cost is calculated as the sum of (ingredient quantity × resource last_unit_cost). Margin percentage and profitability status (threshold: 60%) are derived from cost vs sale price. This is a backend-only feature (Wave 5, ROS-016).

## User Story
As a restaurant manager
I want to create recipes that link to my ingredient resources with automatic cost and profitability calculations
So that I can track menu item profitability and make informed pricing decisions

## Problem Statement
Restaurant managers need to understand the true cost of each menu dish by linking recipes to their ingredient resources. Without automatic cost calculation from current ingredient prices, managers cannot determine which dishes are profitable and which need price adjustments.

## Solution Statement
Implement a Recipe entity with a child RecipeItem entity that references Resource (ingredients). When a recipe is created or updated, the system automatically calculates the total cost from ingredient quantities × resource unit costs, computes the margin percentage, and flags profitability status (≥60% margin threshold). Provide full CRUD endpoints plus a dedicated recalculate endpoint for on-demand cost refresh.

## Relevant Files
Use these files to implement the feature:

**Reference patterns (read these first):**
- `apps/Server/src/models/resource.py` — SQLAlchemy model pattern (FK to restaurant, UUID PK, timestamps)
- `apps/Server/src/models/inventory_movement.py` — Child entity model pattern (FK to resource with ondelete)
- `apps/Server/src/interface/resource_dto.py` — Pydantic DTO pattern with model_validator for computed fields
- `apps/Server/src/repository/resource_repository.py` — Repository pattern (CRUD, singleton, logging)
- `apps/Server/src/core/services/resource_service.py` — Service pattern (_check_restaurant_access, error handling)
- `apps/Server/src/adapter/rest/resource_routes.py` — Routes pattern (_to_response, auth, error handling)
- `apps/Server/database/create_resource_table.sql` — SQL migration pattern (indexes, triggers)
- `apps/Server/main.py` — Router registration pattern (import + include_router + print)
- `apps/Server/tests/test_resource_api.py` — API test pattern (mock db, mock user, AsyncClient)
- `apps/Server/tests/test_resource_model.py` — Model/DTO test pattern (validation tests)

**Conditional documentation to read:**
- `app_docs/feature-8d28116a-resource-entity-crud-backend.md` — Resource entity docs (Recipe depends on Resource for ingredients)
- `app_docs/feature-a692d2db-restaurant-multi-tenant-entity.md` — Restaurant multi-tenant scoping pattern
- `app_docs/feature-0f0d4c36-fastapi-backend-setup.md` — Server setup and router registration

### New Files
- `apps/Server/database/create_recipe_tables.sql` — SQL migration for recipe and recipe_item tables
- `apps/Server/src/models/recipe.py` — SQLAlchemy models for Recipe and RecipeItem
- `apps/Server/src/interface/recipe_dto.py` — Pydantic DTOs for recipe CRUD operations
- `apps/Server/src/repository/recipe_repository.py` — Repository for recipe database operations
- `apps/Server/src/core/services/recipe_service.py` — Service for recipe business logic and cost calculation
- `apps/Server/src/adapter/rest/recipe_routes.py` — FastAPI routes for recipe endpoints
- `apps/Server/tests/test_recipe_model.py` — Tests for Recipe model and DTOs
- `apps/Server/tests/test_recipe_api.py` — Tests for recipe API endpoints

## Implementation Plan
### Phase 1: Foundation
Create the database migration SQL and SQLAlchemy ORM models for both `recipe` and `recipe_item` tables. The recipe table holds the dish metadata and computed cost/margin fields. The recipe_item table is a junction linking recipes to resources (ingredients) with quantity and unit.

### Phase 2: Core Implementation
Build the data transfer objects (DTOs), repository, and service layers. The service layer implements the cost calculation logic: iterate recipe items, look up each resource's `last_unit_cost`, compute total cost, derive margin percentage, and determine profitability. The repository handles both recipe and recipe_item persistence as atomic operations (create/update recipe with items in a single transaction).

### Phase 3: Integration
Create REST API routes with JWT authentication and restaurant-scoped authorization. Register the recipe router in `main.py`. All endpoints follow the established pattern: auth via `get_current_user`, restaurant access check via service layer, proper HTTP status codes and error handling.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create Database Migration
- Create `apps/Server/database/create_recipe_tables.sql` with:
  - `recipe` table: id (UUID PK), restaurant_id (UUID NOT NULL), name (VARCHAR 255), sale_price (DECIMAL 12,2), current_cost (DECIMAL 12,2 DEFAULT 0), margin_percent (DECIMAL 5,2 DEFAULT 0), is_profitable (BOOLEAN DEFAULT true), is_active (BOOLEAN DEFAULT true), created_at, updated_at
  - `recipe_item` table: id (UUID PK), recipe_id (UUID FK → recipe ON DELETE CASCADE), resource_id (UUID FK → resource ON DELETE RESTRICT), quantity (DECIMAL 12,4), unit (VARCHAR 50), created_at
  - Indexes: idx_recipe_restaurant, idx_recipe_item_recipe, idx_recipe_item_resource
  - Auto-update trigger on recipe.updated_at using existing `update_updated_at_column()` function
  - Follow pattern from `create_resource_table.sql`

### Step 2: Create SQLAlchemy Models
- Create `apps/Server/src/models/recipe.py` with:
  - `Recipe` class: all columns from migration, follow Resource model pattern
  - `RecipeItem` class: all columns from migration, FK to recipe (CASCADE) and resource (RESTRICT)
  - Both classes include `__repr__` methods
  - Import from `src.config.database import Base`

### Step 3: Create Pydantic DTOs
- Create `apps/Server/src/interface/recipe_dto.py` with:
  - `RecipeItemCreateDTO`: resource_id (UUID), quantity (Decimal, gt=0), unit (str)
  - `RecipeItemResponseDTO`: id, resource_id, quantity, unit, created_at; model_config from_attributes
  - `RecipeCreateDTO`: restaurant_id, name (max_length=255), sale_price (gt=0), is_active (default True), items (list[RecipeItemCreateDTO], min_length=1)
  - `RecipeUpdateDTO`: optional name, sale_price, is_active, items (Optional list)
  - `RecipeResponseDTO`: all recipe fields + items list[RecipeItemResponseDTO], with model_config from_attributes
  - Follow validation patterns from `resource_dto.py`

### Step 4: Create Repository
- Create `apps/Server/src/repository/recipe_repository.py` with:
  - `RecipeRepository` class with methods:
    - `create(db, restaurant_id, name, sale_price, is_active, items)` — insert recipe + recipe_items atomically
    - `get_by_id(db, recipe_id)` — get recipe with items (eager load or separate query)
    - `get_by_restaurant(db, restaurant_id)` — list all recipes for a restaurant
    - `update(db, recipe, name, sale_price, is_active)` — update recipe fields
    - `replace_items(db, recipe_id, items)` — delete existing items and insert new ones
    - `update_cost(db, recipe_id, current_cost, margin_percent, is_profitable)` — update computed cost fields
    - `delete(db, recipe_id)` — delete recipe (cascade deletes items)
    - `get_by_resource(db, resource_id)` — find recipes that use a specific resource
  - Singleton instance `recipe_repository`
  - Comprehensive logging with `[RecipeRepository]` prefix
  - Follow pattern from `resource_repository.py`

### Step 5: Create Service
- Create `apps/Server/src/core/services/recipe_service.py` with:
  - `RecipeService` class with:
    - `_check_restaurant_access(db, user_id, restaurant_id)` — reuse pattern from ResourceService
    - `create_recipe(db, user_id, data: RecipeCreateDTO)` — check access, create recipe with items, auto-calculate cost, return recipe
    - `get_recipes(db, user_id, restaurant_id)` — check access, return list
    - `get_recipe(db, user_id, recipe_id)` — check access, return single with items
    - `update_recipe(db, user_id, recipe_id, data: RecipeUpdateDTO)` — check access, update fields, replace items if provided, recalculate cost
    - `delete_recipe(db, user_id, recipe_id)` — check access, delete
    - `calculate_cost(db, recipe_id)` — iterate items, lookup resource.last_unit_cost, compute total_cost, margin_percent = (sale_price - total_cost) / sale_price * 100, is_profitable = margin >= 60, update via repository
    - `recalculate_cost(db, user_id, recipe_id)` — check access, call calculate_cost, return updated cost info
  - Singleton instance `recipe_service`
  - Import `resource_repository` for ingredient cost lookups
  - Import `restaurant_repository` for access checks
  - Comprehensive logging with `[RecipeService]` prefix

### Step 6: Create REST Routes
- Create `apps/Server/src/adapter/rest/recipe_routes.py` with:
  - `router = APIRouter(prefix="/api/recipes", tags=["Recipes"])`
  - `_to_response(recipe, items)` helper for DTO conversion
  - `POST ""` — create recipe (201), body: RecipeCreateDTO
  - `GET ""` — list recipes, query param: restaurant_id (required)
  - `GET "/{recipe_id}"` — get recipe detail with items
  - `PUT "/{recipe_id}"` — update recipe, body: RecipeUpdateDTO
  - `DELETE "/{recipe_id}"` — delete recipe (204)
  - `POST "/{recipe_id}/recalculate"` — force cost recalculation
  - All endpoints: `Depends(get_current_user)`, `Depends(get_db)`
  - Error handling: PermissionError → 403, ValueError → 404
  - Follow pattern from `resource_routes.py`

### Step 7: Register Router in main.py
- Add import: `from src.adapter.rest.recipe_routes import router as recipe_router`
- Add `app.include_router(recipe_router)` after notification_router
- Add `print("INFO [Main]: Recipe router registered")`

### Step 8: Create Model/DTO Tests
- Create `apps/Server/tests/test_recipe_model.py` with tests for:
  - RecipeItemCreateDTO: valid creation, quantity validation (gt=0), missing fields
  - RecipeCreateDTO: all fields, required only, name validation, sale_price validation (gt=0), empty items list rejected (min_length=1)
  - RecipeUpdateDTO: partial update, all None fields
  - RecipeResponseDTO: from_attributes conversion, all fields present
  - RecipeItemResponseDTO: from_attributes conversion
  - Recipe model: repr, default values
  - RecipeItem model: repr
  - Follow pattern from `test_resource_model.py`

### Step 9: Create API Tests
- Create `apps/Server/tests/test_recipe_api.py` with tests for:
  - **Create**: success (201 with items), auth required (401), no restaurant access (403), validation errors (422: missing name, sale_price ≤ 0, empty items)
  - **List**: success, empty list, auth required
  - **Get**: success with items, not found (404), no access (403)
  - **Update**: success, update items, not found (404)
  - **Delete**: success (204), not found (404)
  - **Recalculate**: success with correct cost computation, not found (404)
  - Mock: database, auth, resource_repository (for cost lookup), restaurant_repository (for access), recipe_repository
  - Follow pattern from `test_resource_api.py`

### Step 10: Run Validation Commands
- Run all validation commands listed below to ensure zero regressions

## Testing Strategy
### Unit Tests
- **DTO validation tests**: Verify all field constraints (required fields, min_length, gt=0, max_length)
- **Model tests**: Verify SQLAlchemy model defaults and repr
- **API endpoint tests**: Mock all dependencies, test each endpoint for success, auth, permissions, validation, and not-found scenarios
- **Cost calculation tests**: Verify correct cost computation from ingredient costs, margin calculation, profitability threshold

### Edge Cases
- Recipe with a single item (minimum valid case)
- Recipe where all ingredients have last_unit_cost = 0 (cost = 0, margin = 100%)
- Recipe with sale_price resulting in exactly 60% margin (boundary: is_profitable = True)
- Recipe with sale_price resulting in 59.99% margin (boundary: is_profitable = False)
- Updating recipe items (replace all items, verify old items deleted)
- Deleting a recipe (verify cascade deletes recipe_items)
- Resource referenced by recipe_item cannot be deleted (ON DELETE RESTRICT)
- Recipe with sale_price = 0 (rejected by DTO validation gt=0)
- Recalculate cost when resource cost has changed

## Acceptance Criteria
- `recipe` and `recipe_item` tables created with correct schema, indexes, and triggers
- SQLAlchemy models correctly map to database tables
- Pydantic DTOs enforce all validation rules (name required, sale_price > 0, items non-empty, quantity > 0)
- Full CRUD operations work: create recipe with items, list by restaurant, get by ID with items, update recipe and items, delete with cascade
- Cost calculation correctly sums (quantity × resource.last_unit_cost) for all items
- Margin percentage calculated as (sale_price - cost) / sale_price × 100
- Profitability flag set to True when margin ≥ 60%, False otherwise
- Recalculate endpoint triggers fresh cost computation
- All endpoints require JWT authentication
- All endpoints enforce restaurant-scoped authorization
- All tests pass with zero regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/test_recipe_model.py -v` — Run recipe model/DTO tests
- `cd apps/Server && python -m pytest tests/test_recipe_api.py -v` — Run recipe API tests
- `cd apps/Server && python -m pytest tests/ -v` — Run all Server tests to validate zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check (no frontend changes expected, verify no breakage)
- `cd apps/Client && npm run build` — Run Client build to validate no breakage

## Notes
- This is a backend-only feature (no UI). The frontend recipe page will be added in Wave 6.
- The `is_profitable` threshold is hardcoded at 60% margin. Future work may make this configurable per restaurant.
- The `get_by_resource` repository method enables Wave 6's automatic cost recalculation when a resource's `last_unit_cost` changes.
- Recipe items use `ON DELETE RESTRICT` on resource_id to prevent deleting ingredients that are used in recipes.
- The recalculate endpoint enables on-demand cost refresh, which is needed before Wave 6 automates this via invoice OCR.
- Cost calculation uses `resource.last_unit_cost` (Decimal 12,4) for precision. All monetary calculations should use Decimal, never float.
