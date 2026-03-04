# Recipe-Based Inventory Deduction

**ADW ID:** 4801f61f
**Date:** 2026-03-03
**Specification:** specs/issue-96-adw-4801f61f-sdlc_planner-recipe-inventory-deduction.md

## Overview

When a dish is sold or produced, this feature automatically deducts the corresponding ingredient quantities from inventory. It creates exit movements (type=exit, reason=receta) for each recipe item in an atomic, all-or-nothing operation — if any ingredient has insufficient stock, no deductions occur.

## What Was Built

- `POST /api/recipes/{recipe_id}/produce` endpoint for recipe production
- `RecipeService.produce_recipe()` method with stock pre-check and atomic deduction logic
- `RecipeProduceRequestDTO` and `RecipeProduceResponseDTO` Pydantic models
- 6 unit tests covering success, quantity multiplier, not-found, no-access, insufficient stock, and unauthenticated scenarios

## Technical Implementation

### Files Modified

- `apps/Server/src/interface/recipe_dto.py`: Added `RecipeProduceRequestDTO` (quantity field, default=1, min=1) and `RecipeProduceResponseDTO` (recipe_id, recipe_name, quantity, movements_created)
- `apps/Server/src/core/services/recipe_service.py`: Added `produce_recipe()` method that pre-checks all ingredient stock levels, then creates exit movements via `inventory_service.create_movement()`
- `apps/Server/src/adapter/rest/recipe_routes.py`: Added `POST /{recipe_id}/produce` endpoint with error mapping (PermissionError→403, ValueError "not found"→404, ValueError other→400)
- `apps/Server/tests/test_recipe_api.py`: Added 6 production-specific test cases with mock inventory service patching

### Key Changes

- **Atomic pre-check**: All ingredient stocks are verified before any deductions begin, preventing partial inventory changes
- **Inventory integration**: Uses existing `inventory_service.create_movement()` with `MovementType.EXIT` and `MovementReason.RECETA` to create movements and update stock
- **Quantity multiplier**: Each ingredient quantity is multiplied by the production quantity (e.g., producing 3 units of a recipe uses 3x each ingredient)
- **Spanish error messages**: Insufficient stock returns `"Stock insuficiente para {name}: necesita {required} {unit}, disponible {stock}"`
- **Movement notes**: Each movement includes descriptive notes like `"Producción: Pasta Carbonara x3"`

## How to Use

1. Ensure a recipe exists with items linked to resources that have sufficient stock
2. Send `POST /api/recipes/{recipe_id}/produce` with body `{"quantity": 1}` (quantity defaults to 1)
3. The endpoint pre-checks all ingredients, creates exit movements, and returns a summary:
   ```json
   {
     "recipe_id": "uuid",
     "recipe_name": "Pasta Carbonara",
     "quantity": 3,
     "movements_created": 4
   }
   ```
4. If any ingredient lacks sufficient stock, a 400 error is returned with a Spanish message and no inventory changes occur

## Configuration

No additional configuration required. The endpoint uses existing authentication (JWT), restaurant-scoped authorization, and inventory movement infrastructure.

## Testing

```bash
cd apps/Server && python -m pytest tests/test_recipe_api.py -v -k "produce"
```

Test cases:
- `test_produce_recipe_success` — 2 ingredients, sufficient stock, returns 201
- `test_produce_recipe_with_quantity` — quantity=3 multiplies ingredient amounts
- `test_produce_recipe_not_found` — nonexistent recipe returns 404
- `test_produce_recipe_no_access` — no restaurant access returns 403
- `test_produce_recipe_insufficient_stock` — insufficient stock returns 400 with Spanish message
- `test_produce_recipe_unauthenticated` — no auth token returns 401

## Notes

- Backend-only feature (no UI changes)
- `MovementReason.RECETA` enum already existed in `inventory_movement_dto.py`
- `inventory_service.create_movement()` handles stock updates and low-stock warnings internally; the pre-check is an additional safeguard for atomic behavior
- Future enhancement: track production history for real vs. theoretical consumption analysis
