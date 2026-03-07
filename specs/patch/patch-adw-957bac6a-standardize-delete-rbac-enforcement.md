# Patch: Standardize RBAC enforcement on delete endpoints

## Metadata
adw_id: `957bac6a`
review_change_request: `Issue #192 — Inconsistent RBAC enforcement on delete endpoints across routes`

## Issue Summary
**Original Spec:** N/A
**Issue:** Delete endpoints in person_routes.py, resource_routes.py, recipe_routes.py, and restaurant_routes.py use only `get_current_user` + service-layer PermissionError for authorization, while the majority of delete endpoints (transaction, budget, recurring_template, meeting_record, prospect, pipeline_stage) enforce `require_roles(["admin", "manager"])` at the route level.
**Solution:** Add `require_roles(["admin", "manager"])` as the dependency on the delete endpoints in the four affected files, replacing `get_current_user` with `require_roles(["admin", "manager"])` (which itself calls `get_current_user` internally, so service-layer checks remain as defense-in-depth).

## Files to Modify

1. `apps/Server/src/adapter/rest/person_routes.py` — line 204: change `get_current_user` to `require_roles(["admin", "manager"])` on delete endpoint
2. `apps/Server/src/adapter/rest/resource_routes.py` — line 207: change `get_current_user` to `require_roles(["admin", "manager"])` on delete endpoint
3. `apps/Server/src/adapter/rest/recipe_routes.py` — line 191: change `get_current_user` to `require_roles(["admin", "manager"])` on delete endpoint
4. `apps/Server/src/adapter/rest/restaurant_routes.py` — line 162: change `get_current_user` to `require_roles(["admin", "manager"])` on delete endpoint

## Implementation Steps
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add `require_roles` import to each affected file
- In each of the 4 files, add `from src.adapter.rest.rbac_dependencies import require_roles` to the imports section
- The existing `get_current_user` import remains (used by other endpoints in the same file)

### Step 2: Replace `get_current_user` with `require_roles(["admin", "manager"])` on delete endpoints
- In `person_routes.py` line 204: change `current_user: Dict[str, Any] = Depends(get_current_user)` to `current_user: Dict[str, Any] = Depends(require_roles(["admin", "manager"]))`
- In `resource_routes.py` line 207: same change
- In `recipe_routes.py` line 191: same change
- In `restaurant_routes.py` line 162: same change
- Keep all other endpoint signatures unchanged (create, list, get, update remain with `get_current_user`)

### Step 3: Update docstrings on delete endpoints
- Add "Only admin or manager roles can delete." to each delete endpoint docstring to match the pattern used in transaction_routes.py

## Validation
Execute every command to validate the patch is complete with zero regressions.

1. `cd apps/Server && .venv/bin/python -m py_compile main.py src/**/*.py` — Python syntax check
2. `cd apps/Server && .venv/bin/ruff check .` — Code quality / linting check
3. `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short` — All backend tests pass
4. `cd apps/Client && npm run typecheck` — Frontend type check (no frontend changes expected, sanity check)
5. `cd apps/Client && npm run build` — Frontend build succeeds

## Patch Scope
**Lines of code to change:** ~20 (4 import additions + 4 dependency swaps + ~8 docstring lines)
**Risk level:** low
**Testing required:** Backend syntax check, linting, and all backend tests must pass. The change is purely additive RBAC gating — it restricts access further, never loosens it.
