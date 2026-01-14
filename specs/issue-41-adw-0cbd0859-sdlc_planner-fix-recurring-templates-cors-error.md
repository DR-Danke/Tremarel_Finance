# Bug: Fix Recurring Templates CORS Error

## Metadata
issue_number: `41`
adw_id: `0cbd0859`
issue_json: `{"number":41,"title":"Recurring transactions error message","body":"When going to the Recurring transactions menu option, I get a Network Error..."}`

## Bug Description
When navigating to the Recurring Transactions page in the Finance Tracker application, users receive a Network Error. The browser console reveals two distinct issues:

1. **CORS Policy Violation**: The browser blocks the request to `/api/recurring-templates/` because no `Access-Control-Allow-Origin` header is present on the response.
2. **500 Internal Server Error**: The backend is returning a 500 status code, indicating an unhandled exception.

The error manifests as:
- `Access to XMLHttpRequest at 'http://localhost:8000/api/recurring-templates/?entity_id=...&include_inactive=false&skip=0&limit=100' from origin 'http://localhost:5173' has been blocked by CORS policy`
- `ERROR [ApiClient]: Unable to connect to server. Please ensure the backend is running at http://localhost:8000/api`
- `GET http://localhost:8000/api/recurring-templates/... net::ERR_FAILED 500 (Internal Server Error)`

**Expected Behavior**: The Recurring Transactions page should load successfully, displaying the list of recurring templates (or an empty state if none exist).

**Actual Behavior**: The page fails to load with a Network Error message, and the console shows CORS and 500 errors.

## Problem Statement
The recurring templates API endpoint is throwing an unhandled exception that:
1. Returns a 500 Internal Server Error
2. Bypasses the CORS middleware, resulting in responses without proper CORS headers

A previous bug fix (issue #36, ADW dd6d412a) added a global exception handler to ensure CORS headers are always present on error responses. However, the recurring templates endpoint is still experiencing this issue, suggesting either:
- The exception is occurring in a way that bypasses the global handler
- There's an import or initialization error with the recurring template module
- The exception occurs during Pydantic validation which may have special handling

## Solution Statement
Investigate and fix the root cause of the 500 Internal Server Error in the recurring templates endpoint. The fix should ensure that:
1. The endpoint functions correctly and returns template data
2. All error responses include proper CORS headers
3. Any exceptions are properly logged for debugging

The most likely causes to investigate:
1. Pydantic validation errors in the DTOs not being handled by the global exception handler
2. Database query issues in the repository layer
3. Import or initialization errors in the recurring template module

## Steps to Reproduce
1. Start the backend server: `cd apps/Server && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`
2. Start the frontend server: `cd apps/Client && npm run dev`
3. Navigate to http://localhost:5173
4. Log in with valid credentials
5. Click on "Recurring" in the sidebar navigation
6. Observe the Network Error message on the page
7. Open browser console to see the CORS and 500 errors

## Root Cause Analysis
Based on the error analysis, the 500 Internal Server Error is occurring when accessing the `/api/recurring-templates/` endpoint. The CORS error is a consequence of the 500 error, as unhandled exceptions may not flow through the CORS middleware properly.

Potential root causes (in order of likelihood):

1. **Pydantic ValidationError not caught**: FastAPI uses special exception handlers for `RequestValidationError` and `HTTPException`. If a Pydantic validation error occurs during response serialization (e.g., `RecurringTemplateResponseDTO.model_validate()`), it might not be caught by the generic `Exception` handler.

2. **Database connection issue**: The `get_db` dependency might be failing to establish a database connection, throwing an exception before the route handler executes.

3. **Entity ID validation**: The entity_id passed to the endpoint might not exist in the database, causing a foreign key lookup failure.

4. **Import/Module errors**: If there's an import error in the recurring template service or repository, it could cause a 500 error when the route is accessed.

The fix should add a `RequestValidationError` handler to main.py and investigate the specific exception being thrown.

## Relevant Files
Use these files to fix the bug:

**Backend Files**:
- `apps/Server/main.py` - Main FastAPI application entry point. Contains CORS configuration and the global exception handler. Need to add `RequestValidationError` handler.
- `apps/Server/src/adapter/rest/recurring_template_routes.py` - Recurring template API endpoints. Need to verify the route handlers are correct.
- `apps/Server/src/core/services/recurring_template_service.py` - Business logic for recurring templates. Need to verify service methods handle errors properly.
- `apps/Server/src/repository/recurring_template_repository.py` - Database operations for recurring templates. Need to verify repository methods work correctly.
- `apps/Server/src/interface/recurring_template_dto.py` - Pydantic DTOs for recurring templates. Need to verify schema matches model.
- `apps/Server/src/models/recurring_template.py` - SQLAlchemy model for recurring templates. Need to verify model matches database schema.
- `apps/Server/src/config/database.py` - Database connection configuration.
- `apps/Server/src/adapter/rest/dependencies.py` - FastAPI dependencies including `get_db` and `get_current_user`.

**Documentation Files**:
- `app_docs/feature-e44986c8-recurring-transactions.md` - Recurring transactions feature documentation.
- `app_docs/bug-dd6d412a-cors-error-category-creation.md` - Previous CORS error fix documentation.
- `app_docs/feature-0f0d4c36-fastapi-backend-setup.md` - FastAPI setup documentation.

**Test Files**:
- `apps/Server/tests/test_recurring_templates.py` - Existing unit tests for recurring templates.
- `.claude/commands/e2e/test_recurring_transactions.md` - E2E test for recurring transactions.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Start Backend and Reproduce the Error
- Start the backend server with verbose logging: `cd apps/Server && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- Monitor the backend console for error messages when the recurring templates endpoint is hit
- Document the exact error stack trace from the backend console

### Step 2: Add RequestValidationError Handler to main.py
- Read `apps/Server/main.py`
- Add import for `RequestValidationError` from `fastapi.exceptions`
- Add a new exception handler for `RequestValidationError` similar to the global `Exception` handler
- The handler should return a `JSONResponse` with status code 422 and the validation errors
- This ensures validation errors also get proper CORS headers

### Step 3: Add Detailed Logging to Recurring Template Routes
- Read `apps/Server/src/adapter/rest/recurring_template_routes.py`
- Add try-except blocks around the service calls in the `list_recurring_templates` function
- Add logging to print the full exception details if an error occurs
- This will help identify the exact location and type of error

### Step 4: Verify Database Model and DTO Compatibility
- Read `apps/Server/src/models/recurring_template.py`
- Read `apps/Server/src/interface/recurring_template_dto.py`
- Verify that all fields in the model are properly mapped in the DTO
- Ensure datetime/date serialization is handled correctly
- Check that UUID fields are properly typed

### Step 5: Test the Fix Locally
- Restart the backend server
- Navigate to the Recurring Transactions page in the frontend
- Verify the page loads without errors
- Check the browser console for any remaining errors
- Verify the backend console shows successful request handling

### Step 6: Run Existing Tests
- Run the recurring templates tests: `cd apps/Server && uv run pytest tests/test_recurring_templates.py -v`
- Verify all tests pass without errors
- If any tests fail, fix the issues before proceeding

### Step 7: Execute E2E Test
- Read `.claude/commands/test_e2e.md`
- Read `.claude/commands/e2e/test_recurring_transactions.md`
- Execute the E2E test to validate the recurring transactions functionality works end-to-end

### Step 8: Run Validation Commands
- Execute all validation commands to ensure zero regressions

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

### Backend Tests
```bash
cd apps/Server && uv run pytest tests/ -v
```
Run all backend tests to ensure no regressions.

### Backend Lint
```bash
cd apps/Server && uv run ruff check src/
```
Run linting on the backend code.

### Frontend Type Check
```bash
cd apps/Client && npm run typecheck
```
Run TypeScript type checking on the frontend.

### Frontend Build
```bash
cd apps/Client && npm run build
```
Build the frontend to ensure no compilation errors.

### Verify CORS Headers
After starting the server, run this command to verify CORS headers are present on recurring templates endpoint:
```bash
curl -X GET "http://localhost:8000/api/recurring-templates/?entity_id=00000000-0000-0000-0000-000000000001&include_inactive=false&skip=0&limit=10" \
  -H "Origin: http://localhost:5173" \
  -H "Authorization: Bearer test-token" \
  -v 2>&1 | grep -i "access-control"
```
Even on error responses, this should show `Access-Control-Allow-Origin: http://localhost:5173`.

### E2E Test
Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_recurring_transactions.md` to validate the recurring transactions functionality works end-to-end.

## Notes
- The previous CORS fix (issue #36, ADW dd6d412a) added a global exception handler but may have missed `RequestValidationError` which FastAPI handles separately
- The error sequence (CORS error followed by 500 error) suggests the first request fails with CORS, then a retry may show the actual 500 error
- WSL2 environments require `--host 0.0.0.0` for the backend to be accessible from the Windows host
- The recurring templates feature was implemented in ADW e44986c8 and may have edge cases not covered by the global exception handler
- Consider adding integration tests that specifically test error handling and CORS headers on error responses
