# Patch: Add error handling to create endpoints in restaurant and recurring template routes

## Metadata
adw_id: `7fc048f5`
review_change_request: `Issue #191 — [CI] restaurant_routes.py create endpoint missing error handling`

## Issue Summary
**Original Spec:** N/A
**Issue:** The `create_restaurant` endpoint in `restaurant_routes.py` (lines 41-45) and the `create_recurring_template` endpoint in `recurring_template_routes.py` (lines 41-46) lack try/except blocks for `PermissionError` and `ValueError`. This is inconsistent with the same files' get/update/delete endpoints which all handle these exceptions properly, resulting in unstructured 500 errors when the service layer raises these exceptions.
**Solution:** Wrap the create endpoint service calls in try/except blocks following the exact same pattern already used in the update/delete endpoints of each respective file.

## Files to Modify

- `apps/Server/src/adapter/rest/restaurant_routes.py` — lines 41-45 (create_restaurant endpoint)
- `apps/Server/src/adapter/rest/recurring_template_routes.py` — lines 43-46 (create_recurring_template endpoint)

## Implementation Steps
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add try/except to `create_restaurant` in `restaurant_routes.py`
- Wrap lines 41-45 (the `user_id` assignment, service call, log, and return) in a try/except block
- Catch `PermissionError` → log with `ERROR [RestaurantRoutes]: Access denied: {str(e)}` and raise `HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))`
- Catch `ValueError` → log with `ERROR [RestaurantRoutes]: {str(e)}` and raise `HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))`
- Follow the exact same pattern as the `update_restaurant` endpoint (lines 140-155) in the same file

### Step 2: Add try/except to `create_recurring_template` in `recurring_template_routes.py`
- Wrap lines 43-46 (the service call, log, and return) in a try/except block
- Catch `PermissionError` → log with `ERROR [RecurringTemplateRoutes]: Access denied: {str(e)}` and raise `HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))`
- Catch `ValueError` → log with `ERROR [RecurringTemplateRoutes]: {str(e)}` and raise `HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))`

## Validation
Execute every command to validate the patch is complete with zero regressions.

1. **Python Syntax Check**
   - Command: `cd apps/Server && .venv/bin/python -m py_compile main.py src/**/*.py`
2. **Server Code Quality Check**
   - Command: `cd apps/Server && .venv/bin/ruff check .`
3. **All Server Tests**
   - Command: `cd apps/Server && .venv/bin/pytest tests/ -v --tb=short`

## Patch Scope
**Lines of code to change:** ~20 (10 per file — wrapping existing lines in try/except + adding 2 except clauses)
**Risk level:** low
**Testing required:** Python syntax check, ruff linting, and existing backend test suite
