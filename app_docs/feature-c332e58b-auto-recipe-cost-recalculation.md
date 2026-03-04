# Automatic Recipe Cost Recalculation

**ADW ID:** c332e58b
**Date:** 2026-03-04
**Specification:** specs/issue-98-adw-c332e58b-sdlc_planner-auto-recipe-cost-recalculation.md

## Overview

When a resource's `last_unit_cost` changes (via `PUT /api/resources/{id}`), all recipes using that resource are automatically recalculated. If any recipe transitions from profitable to unprofitable (margin below configurable threshold), an `alerta_rentabilidad` event is created to notify the restaurant owner via WhatsApp. This completes the cost intelligence loop: Invoice -> OCR -> Cost Update -> Recipe Recalculation -> Profitability Alert.

## What Was Built

- **Cost-change detection** in `ResourceService.update_resource()` that triggers automatic recipe recalculation
- **Batch recipe recalculation** via `RecipeService.recalculate_by_resource()` for all recipes using a changed resource
- **Profitability transition alerts** via `RecipeService._create_profitability_alert()` creating `alerta_rentabilidad` events
- **Owner lookup** via `PersonRepository.find_owner()` to assign alert responsibility
- **Configurable profitability threshold** via `PROFITABILITY_THRESHOLD` environment variable (default: 60%)

## Technical Implementation

### Files Modified

- `apps/Server/src/core/services/resource_service.py`: Added cost-change detection in `update_resource()` — captures `old_last_unit_cost` before update, compares after update, triggers `recipe_service.recalculate_by_resource()` on change
- `apps/Server/src/core/services/recipe_service.py`: Added `recalculate_by_resource()` and `_create_profitability_alert()` methods; made profitability threshold configurable via `PROFITABILITY_THRESHOLD` env var replacing hardcoded `Decimal("60")`
- `apps/Server/src/repository/person_repository.py`: Added `find_owner(db, restaurant_id)` method to locate the person with `type="owner"` for a restaurant
- `apps/Server/tests/test_recipe_api.py`: Added 4 tests for `recalculate_by_resource` covering: batch recalculation, profitability transition alerts, no-alert when already unprofitable, empty recipe list
- `apps/Server/tests/test_resource_api.py`: Added 2 tests for cost-change detection: triggers recalculation on cost change, no recalculation when cost unchanged

### Key Changes

- **ResourceService hook**: Before updating a resource, the old `last_unit_cost` is captured. After the repository update, if `last_unit_cost` changed, `recipe_service.recalculate_by_resource(db, resource_id)` is called
- **Batch recalculation**: `recalculate_by_resource()` uses `recipe_repository.get_by_resource()` to find all affected recipes, calls `calculate_cost()` on each, and checks for profitability transitions (profitable -> unprofitable only)
- **Alert creation**: Alerts are created directly via `event_repository.create()` (bypassing auth since the original resource update was already authorized). Alert includes recipe name, cost, sale price, and margin in Spanish
- **No circular imports**: ResourceService imports recipe_service singleton; RecipeService does NOT import ResourceService

## How to Use

1. Update a resource's cost via `PUT /api/resources/{resource_id}` with a new `last_unit_cost` value
2. All recipes containing that resource as an ingredient are automatically recalculated
3. Recipe `current_cost`, `margin_percent`, and `is_profitable` fields are updated
4. If any recipe transitions from profitable to unprofitable, an `alerta_rentabilidad` event is automatically created
5. The alert appears in the Events system and is set for WhatsApp notification to the restaurant owner

## Configuration

| Variable | Default | Description |
|---|---|---|
| `PROFITABILITY_THRESHOLD` | `60` | Minimum margin percentage for a recipe to be considered profitable |

## Testing

Run the full test suite to validate:

```bash
cd apps/Server && python -m pytest tests/ -v
```

Key test cases:
- `test_recalculate_by_resource_finds_and_updates_recipes` — verifies batch recalculation
- `test_recalculate_by_resource_creates_alert_on_profitability_transition` — verifies alert on profitable->unprofitable
- `test_recalculate_by_resource_no_alert_when_already_unprofitable` — verifies no duplicate alerts
- `test_recalculate_by_resource_no_recipes_affected` — verifies graceful empty handling
- `test_update_resource_triggers_recipe_recalculation` — verifies ResourceService integration
- `test_update_resource_no_recalculation_when_cost_unchanged` — verifies no false triggers

## Notes

- This is a backend-only feature; no UI changes required. Alerts appear in the existing Events system UI.
- No new API endpoints are created. Recalculation is a side effect of `PUT /api/resources/{id}`.
- Alerts only fire on profitability status transitions (profitable -> unprofitable), not on every recalculation.
- Alert descriptions are in Spanish (Colombian) as specified.
- The `PROFITABILITY_THRESHOLD` could be made per-restaurant via a settings table in the future (out of scope).
