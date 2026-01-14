# Bug Fix: Recurring Templates CORS Error

**ADW ID:** 0cbd0859
**Date:** 2026-01-14
**Specification:** specs/issue-41-adw-0cbd0859-sdlc_planner-fix-recurring-templates-cors-error.md

## Overview

Fixed a CORS error that occurred when navigating to the Recurring Transactions page. The issue was caused by unhandled Pydantic validation errors that bypassed the CORS middleware, resulting in 500 Internal Server Error responses without proper CORS headers. Additionally, frontend hooks were updated to handle null entityId gracefully.

## What Was Built

- Added `RequestValidationError` exception handler to FastAPI main.py
- Added `ValidationError` (Pydantic) exception handler to FastAPI main.py
- Created helper function to serialize complex types (UUID, Decimal, datetime) in error responses
- Added try-except logging in recurring template routes for better debugging
- Added null entityId guards to frontend hooks (useRecurringTemplates, useBudgets, useTransactions)

## Technical Implementation

### Files Modified

- `apps/Server/main.py`: Added two new exception handlers and a serialization helper function to ensure all validation errors return proper JSON responses with CORS headers
- `apps/Server/src/adapter/rest/recurring_template_routes.py`: Added try-except block with detailed logging around the list_templates service call
- `apps/Client/src/hooks/useRecurringTemplates.ts`: Changed entityId parameter type to `string | null` and added null guards to mutation functions
- `apps/Client/src/hooks/useBudgets.ts`: Changed entityId parameter type to `string | null` and added null guards to updateBudget and deleteBudget
- `apps/Client/src/hooks/useTransactions.ts`: Changed entityId parameter type to `string | null` and added null guards to updateTransaction and deleteTransaction

### Key Changes

- **RequestValidationError Handler**: Catches FastAPI request validation errors (query params, body) and returns 422 status with serializable error details
- **ValidationError Handler**: Catches Pydantic model validation errors that occur during response serialization
- **`_make_serializable()` Helper**: Converts Decimal, UUID, datetime, and Exception objects to JSON-serializable strings to prevent serialization failures in error responses
- **Null EntityId Guards**: Frontend hooks now accept `null` entityId and early-return from mutation functions when entityId is null, preventing API calls with invalid entity IDs
- **Enhanced Logging**: Added detailed exception logging in recurring template routes to capture error type and message for debugging

## How to Use

1. Navigate to the Recurring Transactions page in the Finance Tracker application
2. The page should load successfully without CORS errors
3. All CRUD operations on recurring templates should work as expected
4. If validation errors occur, they will be returned as proper JSON responses with 422 status code

## Configuration

No additional configuration required. The exception handlers are automatically registered with the FastAPI application.

## Testing

1. Start the backend server: `cd apps/Server && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`
2. Start the frontend server: `cd apps/Client && npm run dev`
3. Navigate to http://localhost:5173 and log in
4. Click "Recurring" in the sidebar navigation
5. Verify the page loads without CORS errors in the browser console
6. Verify CORS headers are present on all responses:
   ```bash
   curl -X GET "http://localhost:8000/api/recurring-templates/?entity_id=<uuid>&include_inactive=false&skip=0&limit=10" \
     -H "Origin: http://localhost:5173" \
     -H "Authorization: Bearer <token>" \
     -v 2>&1 | grep -i "access-control"
   ```

## Notes

- This fix builds upon the previous CORS error fix (issue #36, ADW dd6d412a) which added the global exception handler
- FastAPI handles `RequestValidationError` separately from generic `Exception`, so it needed its own handler
- Pydantic's `ValidationError` can occur during response model validation (e.g., `model_validate()`) and also needed special handling
- The `_make_serializable()` function prevents secondary serialization errors when error objects contain non-JSON types like UUID or Decimal
- The null entityId guards in frontend hooks prevent unnecessary API calls when the entity context hasn't been initialized
