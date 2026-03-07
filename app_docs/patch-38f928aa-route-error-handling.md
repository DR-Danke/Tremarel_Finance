# Route Error Handling for Transactions and Reports

**ADW ID:** 38f928aa
**Date:** 2026-03-07
**Specification:** specs/patch/patch-adw-38f928aa-add-route-error-handling.md

## Overview

Added try/except error handling to all endpoints in `transaction_routes.py` and `reports_routes.py`. These were the only two route files in the codebase lacking structured error handling, causing raw 500 errors when services raised `ValueError` or `PermissionError`. The patch aligns them with the established pattern used in `category_routes.py`, `budget_routes.py`, and other route files.

## What Was Built

- Try/except blocks around all service calls in `transaction_routes.py` (5 endpoints)
- Try/except blocks around all service calls in `reports_routes.py` (2 endpoints)
- `PermissionError` mapped to HTTP 403 Forbidden
- `ValueError` mapped to HTTP 400 Bad Request
- ERROR log lines in every except block for agent debugging

## Technical Implementation

### Files Modified

- `apps/Server/src/adapter/rest/transaction_routes.py`: Wrapped service calls in `create_transaction`, `list_transactions`, `get_transaction`, `update_transaction`, and `delete_transaction` with try/except blocks. Existing `if not result` checks moved inside the try block.
- `apps/Server/src/adapter/rest/reports_routes.py`: Added `HTTPException` and `status` to FastAPI imports. Wrapped service calls in `get_report_data` and `export_csv` with try/except blocks.

### Key Changes

- `PermissionError` exceptions are caught and re-raised as `HTTPException(403)` with the original error message
- `ValueError` exceptions are caught and re-raised as `HTTPException(400)` with the original error message
- Each except block prints an `ERROR [RouteName]:` log line with context about which operation failed
- Existing 404 checks (e.g., `if not transaction`) remain inside the try block so they still function correctly
- `list_transactions` only catches `ValueError` since it doesn't perform permission-sensitive operations

## How to Use

1. Service layer code can now safely raise `ValueError` for invalid input (e.g., bad date ranges, invalid category IDs) and `PermissionError` for unauthorized access
2. The route layer catches these and returns structured JSON error responses with appropriate HTTP status codes
3. No frontend changes are needed -- the API contract (status codes + `detail` field) matches the existing pattern

## Configuration

No new configuration required.

## Testing

- Run backend syntax check: `cd apps/Server && python -m py_compile main.py`
- Run linter: `cd apps/Server && ruff check .`
- Run tests: `cd apps/Server && pytest tests/ -v --tb=short`
- No frontend changes, so no client-side testing needed

## Notes

- This patch closes CI issue #190
- The error handling pattern matches `category_routes.py` and `budget_routes.py` exactly
- Future route files should follow the same try/except pattern for consistency
