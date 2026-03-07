# Patch: Add Error Handling to Create Endpoints

**ADW ID:** 7fc048f5
**Date:** 2026-03-07
**Specification:** specs/patch/patch-adw-7fc048f5-add-create-endpoint-error-handling.md

## Overview

Added try/except error handling to the `create_restaurant` and `create_recurring_template` endpoints. These endpoints previously lacked `PermissionError` and `ValueError` handling that was already present in their sibling get/update/delete endpoints, resulting in unstructured 500 errors when the service layer raised these exceptions.

## What Was Built

- Consistent error handling for `create_restaurant` in `restaurant_routes.py`
- Consistent error handling for `create_recurring_template` in `recurring_template_routes.py`
- Proper HTTP status codes: 403 for `PermissionError`, 400 for `ValueError`
- Structured error logging following existing `ERROR [*Routes]` conventions

## Technical Implementation

### Files Modified

- `apps/Server/src/adapter/rest/restaurant_routes.py`: Wrapped `create_restaurant` service call in try/except block catching `PermissionError` (403) and `ValueError` (400)
- `apps/Server/src/adapter/rest/recurring_template_routes.py`: Wrapped `create_recurring_template` service call in try/except block catching `PermissionError` (403) and `ValueError` (400)

### Key Changes

- Each create endpoint's service call, success log, and return statement are now wrapped in a `try` block
- `PermissionError` is caught and re-raised as `HTTPException` with `status.HTTP_403_FORBIDDEN`, logged as `ERROR [*Routes]: Access denied: {str(e)}`
- `ValueError` is caught and re-raised as `HTTPException` with `status.HTTP_400_BAD_REQUEST`, logged as `ERROR [*Routes]: {str(e)}`
- Pattern matches the existing error handling in update/delete endpoints of the same files

## How to Use

No user-facing changes. The endpoints now return proper HTTP error responses:

1. **403 Forbidden** - When the service layer raises `PermissionError` (e.g., insufficient role)
2. **400 Bad Request** - When the service layer raises `ValueError` (e.g., invalid input data)

Previously, these exceptions would propagate as unstructured 500 Internal Server Errors.

## Configuration

No configuration changes required.

## Testing

- Python syntax check: `cd apps/Server && python -m py_compile main.py`
- Linting: `cd apps/Server && ruff check .`
- Backend tests: `cd apps/Server && pytest tests/ -v --tb=short`

## Notes

- This is a low-risk consistency patch (~20 lines changed)
- Addresses Issue #191: [CI] restaurant_routes.py create endpoint missing error handling
- The same error handling pattern was already established in the update/delete endpoints of both files
