# Feature: Recipe-Based Inventory Deduction

## Metadata
issue_number: `96`
adw_id: `4801f61f`
issue_json: ``

## Feature Description
When a dish is sold or produced, automatically deduct the corresponding ingredient quantities from inventory. The system creates inventory exit movements (type=exit, reason=receta) for each recipe item. If any ingredient has insufficient stock, the entire operation is prevented — no partial deductions occur. This is an atomic, all-or-nothing operation.

## User Story
As a restaurant manager
I want to produce a recipe and have all ingredient quantities automatically deducted from inventory
So that my inventory levels stay accurate and I can track real consumption versus theoretical usage

## Problem Statement
Currently, recipe production does not affect inventory. When a dish is made, staff must manually create individual exit movements for each ingredient. This is error-prone, time-consuming, and makes it impossible to track real consumption accurately.

## Solution Statement
Add a `POST /api/recipes/{recipe_id}/produce` endpoint that takes a quantity parameter, pre-checks all ingredient stock levels, and atomically creates exit movements (type=exit, reason=receta) for each recipe item. The pre-check ensures that if any single ingredient lacks sufficient stock, no deductions occur and a clear Spanish-language error message is returned.

## Relevant Files
Use these files to implement the feature:

**Backend - Routes (modify):**
- `apps/Server/src/adapter/rest/recipe_routes.py` — Add the `POST /{recipe_id}/produce` endpoint following existing patterns (error mapping, auth, logging)

**Backend - Service (modify):**
- `apps/Server/src/core/services/recipe_service.py` — Add `produce_recipe()` method with stock pre-check and movement creation logic

**Backend - Dependencies (read-only, import):**
- `apps/Server/src/core/services/inventory_service.py` — Use `inventory_service.create_movement()` to create exit movements and update stock
- `apps/Server/src/interface/inventory_movement_dto.py` — Import `InventoryMovementCreateDTO`, `MovementType`, `MovementReason` for creating movements
- `apps/Server/src/interface/recipe_dto.py` — Existing DTOs; add `RecipeProduceRequestDTO` and `RecipeProduceResponseDTO`
- `apps/Server/src/repository/recipe_repository.py` — Use `get_by_id()` and `get_items()` to fetch recipe and ingredients
- `apps/Server/src/repository/resource_repository.py` — Use `get_by_id()` to check `current_stock` for each ingredient
- `apps/Server/src/models/recipe.py` — Recipe and RecipeItem models
- `apps/Server/src/models/resource.py` — Resource model with `current_stock` field
- `apps/Server/src/models/inventory_movement.py` — InventoryMovement model

**Backend - Tests (modify):**
- `apps/Server/tests/test_recipe_api.py` — Add produce endpoint tests following existing patterns

**Documentation (read for context):**
- `app_docs/feature-3ad42112-recipe-data-model-crud.md` — Recipe entity architecture
- `app_docs/feature-02529be1-inventory-movement-tracking.md` — Inventory movement patterns and enums
- `app_docs/feature-8d28116a-resource-entity-crud-backend.md` — Resource entity with stock tracking

### New Files
- `apps/Server/src/interface/recipe_produce_dto.py` — DTOs for the produce request/response (alternatively can be added to existing `recipe_dto.py`)

## Implementation Plan
### Phase 1: Foundation
Add the request/response DTOs for the produce endpoint. The `RecipeProduceRequestDTO` accepts an optional `quantity` (default 1, min 1). The `RecipeProduceResponseDTO` returns the recipe_id, quantity produced, and count of movements created.

### Phase 2: Core Implementation
Add the `produce_recipe()` method to `RecipeService`. This method:
1. Fetches the recipe and verifies it exists
2. Checks restaurant access for the user
3. Fetches all recipe items
4. Pre-checks ALL ingredients for sufficient stock before any deductions
5. Creates exit movements for each ingredient via `inventory_service.create_movement()`
6. Returns a summary of the production

### Phase 3: Integration
Add the `POST /{recipe_id}/produce` route to `recipe_routes.py` following existing patterns for error mapping (PermissionError→403, ValueError with "not found"→404, ValueError with "Insufficient"/"insuficiente"→400). Wire the route to the service method.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add Produce DTOs to recipe_dto.py
- Add `RecipeProduceRequestDTO` to `apps/Server/src/interface/recipe_dto.py`:
  - `quantity: int = Field(default=1, ge=1, description="Number of recipe units to produce")`
- Add `RecipeProduceResponseDTO` to `apps/Server/src/interface/recipe_dto.py`:
  - `recipe_id: UUID`
  - `recipe_name: str`
  - `quantity: int`
  - `movements_created: int`

### Step 2: Add produce_recipe method to RecipeService
- Open `apps/Server/src/core/services/recipe_service.py`
- Add import for `inventory_service` from `src.core.services.inventory_service`
- Add import for `InventoryMovementCreateDTO`, `MovementType`, `MovementReason` from `src.interface.inventory_movement_dto`
- Add `produce_recipe(self, db, user_id, recipe_id, quantity=1)` method:
  1. Fetch recipe via `recipe_repository.get_by_id(db, recipe_id)` — raise `ValueError("Recipe not found")` if None
  2. Call `self._check_restaurant_access(db, user_id, recipe.restaurant_id)` — raises `PermissionError` if no access
  3. Fetch items via `recipe_repository.get_items(db, recipe_id)`
  4. **Pre-check loop**: For each item, fetch resource via `resource_repository.get_by_id(db, item.resource_id)`, compute `required = item.quantity * quantity`. If `resource.current_stock < required`, raise `ValueError(f"Stock insuficiente para {resource.name}: necesita {required} {item.unit}, disponible {resource.current_stock}")`
  5. **Deduction loop**: For each item, call `inventory_service.create_movement(db, user_id, InventoryMovementCreateDTO(resource_id=item.resource_id, type=MovementType.EXIT, quantity=item.quantity * quantity, reason=MovementReason.RECETA, restaurant_id=recipe.restaurant_id, notes=f"Producción: {recipe.name} x{quantity}"))` and collect the movements
  6. Log and return `{"recipe_id": recipe.id, "recipe_name": recipe.name, "quantity": quantity, "movements_created": len(movements)}`

### Step 3: Add produce endpoint to recipe_routes.py
- Open `apps/Server/src/adapter/rest/recipe_routes.py`
- Add import for `RecipeProduceRequestDTO`, `RecipeProduceResponseDTO` from `src.interface.recipe_dto`
- Add `POST /{recipe_id}/produce` endpoint:
  - Accept `recipe_id: UUID` path param and `data: RecipeProduceRequestDTO` body
  - Call `recipe_service.produce_recipe(db, user_id, recipe_id, data.quantity)`
  - Return `RecipeProduceResponseDTO` with status 201
  - Error handling: `PermissionError` → 403, `ValueError` with "not found" → 404, `ValueError` (other, e.g. insufficient stock) → 400
  - Follow existing logging patterns

### Step 4: Add unit tests for produce endpoint
- Open `apps/Server/tests/test_recipe_api.py`
- Add a section `# Recipe Production Tests`
- Import `InventoryMovement` model from `src.models.inventory_movement`
- Add helper `create_mock_movement()` to create mock `InventoryMovement` objects
- Add test cases:

  1. **`test_produce_recipe_success`**: Mock recipe with 2 items, both resources have sufficient stock. Patch `inventory_service.create_movement` to return mock movements. Assert 201, verify response has `recipe_id`, `quantity`, `movements_created=2`.

  2. **`test_produce_recipe_with_quantity`**: Same as above but with `quantity=3`. Verify the movement creation is called with `item.quantity * 3` for each item.

  3. **`test_produce_recipe_not_found`**: Recipe doesn't exist. Assert 404.

  4. **`test_produce_recipe_no_access`**: User has no restaurant access. Assert 403.

  5. **`test_produce_recipe_insufficient_stock`**: One ingredient has insufficient stock. Assert 400 with Spanish error message containing "Stock insuficiente".

  6. **`test_produce_recipe_unauthenticated`**: No auth token. Assert 401.

- Patching pattern: patch `src.core.services.recipe_service.inventory_service` in addition to existing recipe service patches (recipe_repository, resource_repository, restaurant_repository)

### Step 5: Run validation commands
- Run `cd apps/Server && python -m pytest tests/test_recipe_api.py -v` to validate the new tests pass
- Run `cd apps/Server && python -m pytest tests/ -v` to validate no regressions across all tests

## Testing Strategy
### Unit Tests
- Test successful recipe production with single and multiple quantities
- Test that all ingredients create corresponding exit movements
- Test pre-check prevents partial deductions when one ingredient has insufficient stock
- Test proper error codes: 401 (unauth), 403 (no access), 404 (recipe not found), 400 (insufficient stock)
- Test Spanish error message format for insufficient stock

### Edge Cases
- Recipe with zero items (edge case — should not happen due to min_length=1 on creation, but service should handle gracefully)
- Quantity of exactly available stock (should succeed, leaving stock at 0)
- Multiple ingredients where the last one fails the pre-check (verify no movements were created)
- Resource not found for a recipe item (stale recipe data)

## Acceptance Criteria
- `POST /api/recipes/{recipe_id}/produce` endpoint exists and returns 201 on success
- Request body accepts `quantity` parameter (default 1, minimum 1)
- All ingredient stocks are pre-checked before any deductions begin
- If any ingredient has insufficient stock, return 400 with Spanish message: "Stock insuficiente para {nombre}: necesita {cantidad} {unidad}, disponible {stock}"
- Each ingredient creates an exit movement with type=exit, reason=receta
- Movement notes contain recipe name and quantity (e.g., "Producción: Pasta Carbonara x3")
- Resource current_stock is updated after each movement
- Proper auth (401), access (403), and not-found (404) error handling
- All existing recipe API tests continue to pass

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/test_recipe_api.py -v` — Run recipe-specific tests to validate produce endpoint
- `cd apps/Server && python -m pytest tests/ -v` — Run all Server tests to validate zero regressions

## Notes
- This feature is backend-only (no UI changes). No E2E test file is needed.
- The `MovementReason.RECETA` enum value already exists in `inventory_movement_dto.py`, so no enum changes are needed.
- The `inventory_service.create_movement()` already handles stock updates and low-stock warnings internally. The pre-check in `produce_recipe` is an additional safeguard to ensure atomic all-or-nothing behavior.
- Error messages are in Spanish (Colombian) as specified in the issue.
- This feature runs in parallel with ROS-017, ROS-018, ROS-020. No merge conflicts expected since changes are scoped to recipe files only.
- Future enhancement: track production history for real vs. theoretical consumption analysis.
