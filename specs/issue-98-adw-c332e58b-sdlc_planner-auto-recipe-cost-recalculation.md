# Feature: Automatic Recipe Cost Recalculation

## Metadata
issue_number: `98`
adw_id: `c332e58b`
issue_json: ``

## Feature Description
Whenever a resource's `last_unit_cost` changes (e.g., after invoice OCR processing or manual update), automatically recalculate the cost of all recipes that use that resource. Update each affected recipe's `current_cost`, `margin_percent`, and `is_profitable` fields. If any recipe transitions from profitable to unprofitable (margin below configurable threshold), trigger a profitability alert Event (`alerta_rentabilidad`) that notifies the restaurant owner.

This completes the cost intelligence loop: Invoice → OCR → Cost Update → Recipe Recalculation → Profitability Alert.

## User Story
As a restaurant owner
I want recipe costs to automatically recalculate when ingredient prices change
So that I always have accurate profitability data and get alerted when a recipe becomes unprofitable

## Problem Statement
Currently, when a resource's `last_unit_cost` is updated via `PUT /api/resources/{id}`, the cost change does NOT propagate to recipes using that resource. Recipe costs become stale until manually recalculated. The owner has no visibility into recipes that have become unprofitable due to ingredient price changes.

## Solution Statement
Hook into `ResourceService.update_resource()` to detect `last_unit_cost` changes. When a cost change is detected, automatically find all affected recipes via `RecipeRepository.get_by_resource()`, recalculate each recipe's cost using the existing `RecipeService.calculate_cost()`, and create profitability alert events when a recipe transitions from profitable to unprofitable. Add a `find_owner()` method to PersonRepository for assigning alerts. Make the profitability threshold configurable via environment variable (default: 60%).

## Relevant Files
Use these files to implement the feature:

**Core Services (modify):**
- `apps/Server/src/core/services/resource_service.py` — Add cost-change detection in `update_resource()` and trigger recipe recalculation. Import recipe_service.
- `apps/Server/src/core/services/recipe_service.py` — Add `recalculate_by_resource()` and `_create_profitability_alert()` methods. Import event_repository, person_repository.

**Repositories (modify):**
- `apps/Server/src/repository/person_repository.py` — Add `find_owner(restaurant_id)` method to find the person with type="owner" for a restaurant.

**DTOs (read-only reference):**
- `apps/Server/src/interface/event_dto.py` — Reference `EventType.ALERTA_RENTABILIDAD`, `EventFrequency.NONE`, and `EventCreateDTO` structure for creating alerts via event_repository.
- `apps/Server/src/interface/recipe_dto.py` — Reference for recipe response structure.
- `apps/Server/src/interface/resource_dto.py` — Reference `ResourceUpdateDTO` for understanding update payload.

**Models (read-only reference):**
- `apps/Server/src/models/recipe.py` — Recipe and RecipeItem models with `current_cost`, `margin_percent`, `is_profitable` fields.
- `apps/Server/src/models/resource.py` — Resource model with `last_unit_cost` field.
- `apps/Server/src/models/event.py` — Event model for alert creation.
- `apps/Server/src/models/person.py` — Person model with `type` field (owner, employee, supplier).

**Repositories (read-only reference):**
- `apps/Server/src/repository/recipe_repository.py` — Has `get_by_resource()` (finds recipes using a resource) and `update_cost()` methods already.
- `apps/Server/src/repository/event_repository.py` — Has `create()` method for direct event creation without auth check.
- `apps/Server/src/repository/restaurant_repository.py` — Restaurant access checks.

**Routes (read-only reference):**
- `apps/Server/src/adapter/rest/resource_routes.py` — Update endpoint triggers the flow via `resource_service.update_resource()`.
- `apps/Server/src/adapter/rest/recipe_routes.py` — Existing recalculate endpoint for reference.

**Tests (modify):**
- `apps/Server/tests/test_resource_api.py` — Add tests for cost-change triggering recipe recalculation.
- `apps/Server/tests/test_recipe_api.py` — Add tests for `recalculate_by_resource` and profitability alerts.

**Conditional docs:**
- Read `docs/features/feature-3ad42112-recipe-data-model-crud.md` — Recipe cost calculation, margin computation, profitability tracking patterns.

### New Files
No new files are needed. All changes are modifications to existing files.

## Implementation Plan
### Phase 1: Foundation
- Add `find_owner()` to PersonRepository for locating restaurant owners
- Make profitability threshold configurable via `PROFITABILITY_THRESHOLD` environment variable (default: 60%)

### Phase 2: Core Implementation
- Add `recalculate_by_resource(db, resource_id)` to RecipeService — finds all affected recipes, recalculates each, detects profitability transitions
- Add `_create_profitability_alert(db, recipe, cost_result)` to RecipeService — creates `alerta_rentabilidad` event via event_repository
- Modify `calculate_cost()` to use configurable threshold instead of hardcoded `Decimal("60")`

### Phase 3: Integration
- Modify `ResourceService.update_resource()` to detect `last_unit_cost` changes and trigger `recipe_service.recalculate_by_resource()`
- Handle the dependency injection: ResourceService imports recipe_service singleton
- Add comprehensive tests for the full flow

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Read conditional documentation
- Read `docs/features/feature-3ad42112-recipe-data-model-crud.md` for recipe cost calculation patterns and conventions
- Read `apps/Server/src/core/services/recipe_service.py` to understand existing `calculate_cost()` flow
- Read `apps/Server/src/core/services/resource_service.py` to understand existing `update_resource()` flow

### Step 2: Add `find_owner()` to PersonRepository
- Open `apps/Server/src/repository/person_repository.py`
- Add method `find_owner(self, db: Session, restaurant_id: UUID) -> Optional[Person]`
- Query Person where `restaurant_id` matches AND `type == "owner"`, return first result
- Follow existing logging pattern: `print(f"INFO [PersonRepository]: Finding owner for restaurant {restaurant_id}")`
- Return `None` if no owner found (not an error condition)

### Step 3: Add configurable profitability threshold
- Open `apps/Server/src/core/services/recipe_service.py`
- Add at module level (after imports): `import os` and `PROFITABILITY_THRESHOLD = Decimal(os.getenv("PROFITABILITY_THRESHOLD", "60"))`
- Update `calculate_cost()` line 358: change `Decimal("60")` to `PROFITABILITY_THRESHOLD`

### Step 4: Add `recalculate_by_resource()` and `_create_profitability_alert()` to RecipeService
- Open `apps/Server/src/core/services/recipe_service.py`
- Add imports at top: `import os`, `from datetime import datetime`, `from src.repository.event_repository import event_repository`, `from src.repository.person_repository import person_repository`
- Add `recalculate_by_resource(self, db: Session, resource_id: UUID) -> list[dict]`:
  - Call `recipe_repository.get_by_resource(db, resource_id)` to find affected recipes
  - Log: `print(f"INFO [RecipeService]: Recalculating {len(recipes)} recipes affected by resource {resource_id}")`
  - For each recipe:
    - Save old `is_profitable` state: `was_profitable = recipe.is_profitable`
    - Call `self.calculate_cost(db, recipe.id)` to get new cost result
    - Check profitability transition: if `was_profitable and not result["is_profitable"]` then call `self._create_profitability_alert(db, recipe, result)`
    - This ensures alerts only fire on transition from profitable → unprofitable, NOT on every recalculation
  - Return list of cost results
- Add `_create_profitability_alert(self, db: Session, recipe: Recipe, cost_result: dict) -> None`:
  - Find owner: `owner = person_repository.find_owner(db, recipe.restaurant_id)`
  - Create event directly via `event_repository.create()` (no auth check needed for system alerts):
    ```python
    event_repository.create(
        db=db,
        restaurant_id=recipe.restaurant_id,
        event_type="alerta_rentabilidad",
        description=(
            f"Alerta de rentabilidad: {recipe.name} - "
            f"Costo: ${cost_result['current_cost']}, "
            f"Precio venta: ${recipe.sale_price}, "
            f"Margen: {cost_result['margin_percent']:.1f}%"
        ),
        event_date=datetime.utcnow(),
        frequency="none",
        responsible_id=owner.id if owner else None,
        notification_channel="whatsapp",
    )
    ```
  - Log: `print(f"INFO [RecipeService]: Profitability alert created for recipe '{recipe.name}'")`

### Step 5: Modify ResourceService to trigger recipe recalculation
- Open `apps/Server/src/core/services/resource_service.py`
- Add import at top: `from src.core.services.recipe_service import recipe_service`
- In `update_resource()`, before updating `last_unit_cost` (around line 178), capture old cost:
  ```python
  old_last_unit_cost = resource.last_unit_cost
  ```
- After `updated_resource = resource_repository.update(db, resource)` (line 181), add cost-change detection:
  ```python
  if data.last_unit_cost is not None and data.last_unit_cost != old_last_unit_cost:
      print(f"INFO [ResourceService]: Cost changed for resource {resource_id}: {old_last_unit_cost} → {data.last_unit_cost}, triggering recipe recalculation")
      recipe_service.recalculate_by_resource(db, resource_id)
  ```
- Place this BEFORE the low-stock warning check (before line 183)

### Step 6: Add unit tests for PersonRepository.find_owner
- Open `apps/Server/tests/test_resource_api.py` (or create section in existing test file)
- Add test: `test_update_resource_triggers_recipe_recalculation` — mock resource with changed last_unit_cost, verify recipe_service.recalculate_by_resource is called
- Add test: `test_update_resource_no_recalculation_when_cost_unchanged` — verify no recalculation when cost stays the same

### Step 7: Add unit tests for RecipeService recalculation
- Open `apps/Server/tests/test_recipe_api.py`
- Add test: `test_recalculate_by_resource_finds_and_updates_recipes` — mock recipes using a resource, verify calculate_cost called for each
- Add test: `test_recalculate_by_resource_creates_alert_on_profitability_transition` — mock recipe transitioning from profitable to unprofitable, verify event created
- Add test: `test_recalculate_by_resource_no_alert_when_already_unprofitable` — mock recipe that was already unprofitable, verify NO new alert created
- Add test: `test_recalculate_by_resource_no_recipes_affected` — verify graceful handling when no recipes use the resource

### Step 8: Run validation commands
- Run all validation commands listed below to ensure zero regressions

## Testing Strategy
### Unit Tests
- **PersonRepository.find_owner**: Test finding owner, test when no owner exists
- **RecipeService.recalculate_by_resource**: Test batch recalculation, test with 0 affected recipes, test with multiple affected recipes
- **RecipeService._create_profitability_alert**: Test event creation with owner, test event creation without owner (responsible_id=None)
- **ResourceService.update_resource cost hook**: Test recalculation triggered on cost change, test no recalculation when cost unchanged, test no recalculation when last_unit_cost not in update

### Edge Cases
- Resource has no recipes using it → `recalculate_by_resource` returns empty list gracefully
- Recipe has no `sale_price` (zero) → margin calculation handles division, `is_profitable` = False
- No owner person exists for restaurant → alert created with `responsible_id=None`
- Cost change from None to a value → should trigger recalculation
- Multiple recipes affected by same resource change → all recalculated, alerts created per recipe
- Recipe was already unprofitable → no duplicate alert (only on profitable→unprofitable transition)
- Concurrent cost updates → each triggers independent recalculation (SQLAlchemy session handles)

## Acceptance Criteria
- When a resource's `last_unit_cost` is updated via `PUT /api/resources/{id}`, all recipes using that resource are automatically recalculated
- Recipe `current_cost`, `margin_percent`, and `is_profitable` fields are updated after recalculation
- When a recipe transitions from profitable to unprofitable, an `alerta_rentabilidad` event is created
- Alert description is in Spanish (Colombian): "Alerta de rentabilidad: {nombre} - Costo: ${costo}, Precio venta: ${precio}, Margen: {margen}%"
- Alerts only fire on profitability status transition (profitable → unprofitable), not on every recalculation
- Alert notification channel is "whatsapp"
- Alert responsible_id is the restaurant owner (or None if no owner)
- Profitability threshold is configurable via `PROFITABILITY_THRESHOLD` env var (default: 60%)
- No recalculation triggered if `last_unit_cost` is not in the update payload or value hasn't changed
- All existing tests continue to pass with zero regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/ -v` - Run all Server tests to validate the feature works with zero regressions
- `cd apps/Client && npx tsc --noEmit` - Run Client type check to confirm no frontend regressions (this is backend-only but confirms no breakage)
- `cd apps/Client && npm run build` - Run Client build to confirm no frontend regressions

## Notes
- **No UI changes**: This feature is entirely backend. Profitability alerts appear in the existing Events system UI.
- **No new API endpoints**: The recalculation is triggered automatically as a side effect of the existing `PUT /api/resources/{id}` endpoint.
- **No circular imports**: ResourceService imports recipe_service (singleton). RecipeService does NOT import ResourceService — it uses resource_repository directly for cost lookups.
- **System alerts bypass auth**: Profitability alerts are created via `event_repository.create()` directly (not `event_service.create_event()`) since the authorization was already verified when the user updated the resource. The cascading alert creation is a system operation.
- **Alert description language**: Spanish (Colombian) as specified in the issue.
- **Future consideration**: The `PROFITABILITY_THRESHOLD` could be made per-restaurant via a restaurant settings table instead of a global env var. This is out of scope for this issue.
- **RecipeRepository.get_by_resource()** already exists and handles finding recipes by resource ingredient — no new repository methods needed except `find_owner()`.
