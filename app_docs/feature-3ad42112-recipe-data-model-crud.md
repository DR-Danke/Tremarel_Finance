# Recipe Data Model & CRUD

**ADW ID:** 3ad42112
**Date:** 2026-03-03
**Specification:** specs/issue-93-adw-3ad42112-sdlc_planner-recipe-data-model-crud.md

## Overview

Backend-only feature (RestaurantOS Wave 5, ROS-016) that adds the Recipe entity with full CRUD operations and automatic cost/margin calculation. Recipes link to Resource ingredients via RecipeItems, computing total cost from ingredient quantities and unit costs, deriving margin percentage and profitability status (threshold: 60%).

## What Was Built

- `recipe` and `recipe_item` database tables with indexes and auto-update trigger
- SQLAlchemy models for Recipe and RecipeItem with proper FK relationships
- Pydantic DTOs for create, update, and response operations with field validation
- Repository layer with atomic recipe+items persistence and cost update methods
- Service layer with restaurant-scoped authorization, cost calculation, and margin computation
- REST API endpoints: create, list, get, update, delete, and on-demand recalculate
- Comprehensive test suites for model/DTO validation and API endpoints

## Technical Implementation

### Files Modified

- `apps/Server/database/create_recipe_tables.sql`: SQL migration creating `recipe` and `recipe_item` tables with UUID PKs, foreign keys (CASCADE to restaurant, CASCADE recipe→items, RESTRICT to resource), indexes, and updated_at trigger
- `apps/Server/src/models/recipe.py`: SQLAlchemy `Recipe` and `RecipeItem` models with all columns, `__repr__`, and Base import
- `apps/Server/src/interface/recipe_dto.py`: Pydantic DTOs — `RecipeItemCreateDTO`, `RecipeItemResponseDTO`, `RecipeCreateDTO` (items min_length=1, sale_price gt=0), `RecipeUpdateDTO` (all optional), `RecipeResponseDTO`
- `apps/Server/src/repository/recipe_repository.py`: `RecipeRepository` with `create`, `get_by_id`, `get_by_restaurant`, `update`, `replace_items`, `update_cost`, `delete`, `get_by_resource` methods; singleton instance
- `apps/Server/src/core/services/recipe_service.py`: `RecipeService` with restaurant access checks, CRUD operations, and `calculate_cost` logic (sum of quantity × resource.last_unit_cost, margin = (sale_price - cost) / sale_price × 100, profitable if margin ≥ 60%)
- `apps/Server/src/adapter/rest/recipe_routes.py`: FastAPI router at `/api/recipes` with 6 endpoints, `_to_response` helper, JWT auth, error handling (403 for PermissionError, 404 for ValueError)
- `apps/Server/main.py`: Recipe router import and registration
- `apps/Server/tests/test_recipe_model.py`: 414 lines of model/DTO validation tests
- `apps/Server/tests/test_recipe_api.py`: 841 lines of API endpoint tests with mocked dependencies

### Key Changes

- **Cost Calculation**: Service iterates recipe items, looks up each resource's `last_unit_cost` via `resource_repository`, computes total cost as sum of (quantity × unit_cost), then derives margin_percent and is_profitable
- **Atomic Item Management**: Repository creates/replaces recipe items within the same transaction as the recipe, ensuring data consistency
- **Recalculate Endpoint**: `POST /api/recipes/{id}/recalculate` triggers fresh cost computation, useful when ingredient prices change
- **Resource Protection**: `recipe_item.resource_id` uses `ON DELETE RESTRICT` to prevent deleting ingredients used in recipes
- **Restaurant Scoping**: All operations verify user has access to the target restaurant via `user_restaurants` junction table

## How to Use

1. **Create a recipe**: `POST /api/recipes` with body containing `restaurant_id`, `name`, `sale_price`, and `items` array (each with `resource_id`, `quantity`, `unit`). Returns the created recipe with auto-calculated cost and margin.
2. **List recipes**: `GET /api/recipes?restaurant_id={uuid}` to list all recipes for a restaurant.
3. **Get recipe detail**: `GET /api/recipes/{recipe_id}` to retrieve a recipe with its ingredient items.
4. **Update a recipe**: `PUT /api/recipes/{recipe_id}` with optional `name`, `sale_price`, `is_active`, and `items`. If items are provided, existing items are replaced and cost is recalculated.
5. **Delete a recipe**: `DELETE /api/recipes/{recipe_id}` (cascade deletes recipe items).
6. **Recalculate cost**: `POST /api/recipes/{recipe_id}/recalculate` to refresh cost based on current ingredient prices.

All endpoints require JWT authentication via `Authorization: Bearer <token>` header.

## Configuration

No new environment variables required. Uses existing database connection and JWT configuration.

## Testing

```bash
# Run recipe model/DTO tests
cd apps/Server && python -m pytest tests/test_recipe_model.py -v

# Run recipe API tests
cd apps/Server && python -m pytest tests/test_recipe_api.py -v

# Run all server tests (verify zero regressions)
cd apps/Server && python -m pytest tests/ -v
```

## Notes

- Backend-only feature — no frontend UI. The recipe management page will be added in Wave 6.
- Profitability threshold is hardcoded at 60% margin. Future work may make this configurable per restaurant.
- `get_by_resource` repository method enables future automatic cost recalculation when a resource's `last_unit_cost` changes.
- All monetary calculations use `Decimal` types for precision (never `float`).
- The recalculate endpoint supports on-demand cost refresh, needed before Wave 6 automates this via invoice OCR.
