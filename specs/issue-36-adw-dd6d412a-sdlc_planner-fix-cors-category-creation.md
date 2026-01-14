# Bug: CORS Error When Creating Categories

## Metadata
issue_number: `36`
adw_id: `dd6d412a`
issue_json: `{"number":36,"title":"Network Error when trying to create categories","body":"When the user attempts to create a new category, an error message comes up stating there is a network error. When going to the console, the error that comes up states this:\nAccess to XMLHttpRequest at 'http://localhost:8000/api/categories/' from origin 'http://localhost:5173/' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource."}`

## Bug Description
When a user attempts to create a new category via the Finance Tracker application, a network error is displayed. The browser console reveals a CORS policy violation:

```
Access to XMLHttpRequest at 'http://localhost:8000/api/categories/' from origin 'http://localhost:5173/' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**Expected behavior:** The POST request to `/api/categories/` should complete successfully, creating a new category and returning the created category data with appropriate CORS headers.

**Actual behavior:** The request fails with a CORS error, indicating no `Access-Control-Allow-Origin` header is present in the response.

## Problem Statement
The FastAPI backend's CORS middleware is not adding CORS headers to error responses. When the category creation endpoint encounters an unhandled exception (likely a database error or validation error during the POST request), the 500 Internal Server Error response is returned without CORS headers, causing the browser to block the response.

## Solution Statement
Add a global exception handler in the FastAPI application that catches all unhandled exceptions and ensures proper error responses are returned with CORS headers intact. This will wrap exceptions in properly formatted JSON responses that the CORS middleware can process normally.

## Steps to Reproduce
1. Start the backend server: `cd apps/Server && python -m uvicorn main:app --reload --port 8000`
2. Start the frontend server: `cd apps/Client && npm run dev`
3. Navigate to `http://localhost:5173` and log in with valid credentials
4. Navigate to the Categories page (`/categories`)
5. Click "Add Category" button
6. Fill in the form (name, type: income or expense)
7. Click Submit
8. Observe the network error in the UI and CORS error in browser console

## Root Cause Analysis
The issue occurs because FastAPI's CORS middleware adds headers to responses **after** the route handler returns. When an unhandled exception occurs:

1. The exception propagates up from the route handler
2. FastAPI's default exception handler generates a 500 response
3. In some cases, particularly with certain types of exceptions (database connection errors, validation errors during dependency injection), the CORS middleware doesn't get a chance to add headers to the error response
4. The browser receives a response without `Access-Control-Allow-Origin` header and blocks it

The CORS configuration itself is correct (`CORS_ORIGINS=["http://localhost:5173","http://localhost:9207"]`), but the error response bypasses the middleware.

## Relevant Files
Use these files to fix the bug:

- `apps/Server/main.py` - The main FastAPI application entry point where CORS middleware is configured and where we need to add a global exception handler
- `apps/Server/src/config/settings.py` - Settings configuration for CORS origins (for reference)
- `apps/Server/src/adapter/rest/category_routes.py` - Category endpoints (for context on the failing endpoint)
- `app_docs/feature-0f0d4c36-fastapi-backend-setup.md` - Documentation on FastAPI backend setup (for reference)
- `app_docs/feature-a2d71086-category-management-crud.md` - Documentation on category management (for reference)
- `.claude/commands/test_e2e.md` - E2E test runner documentation (for creating validation test)
- `.claude/commands/e2e/test_category_management.md` - Existing E2E test for category management (for reference)

### New Files
No new files need to be created for this fix. The existing E2E test at `.claude/commands/e2e/test_category_management.md` already covers category creation and will validate the fix.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add Global Exception Handler to FastAPI Application
- Open `apps/Server/main.py`
- Import the necessary exception handling utilities from FastAPI:
  ```python
  from fastapi import FastAPI, Request
  from fastapi.responses import JSONResponse
  ```
- Add a global exception handler after the app creation and before router registration that catches all unhandled exceptions:
  ```python
  @app.exception_handler(Exception)
  async def global_exception_handler(request: Request, exc: Exception):
      """
      Global exception handler to ensure CORS headers are always added.

      Catches all unhandled exceptions and returns a proper JSON response
      that the CORS middleware can process.
      """
      print(f"ERROR [Main]: Unhandled exception: {type(exc).__name__}: {str(exc)}")
      return JSONResponse(
          status_code=500,
          content={"detail": "Internal server error"}
      )
  ```
- This ensures all exceptions are converted to proper JSONResponse objects that flow through the CORS middleware

### Step 2: Verify CORS Middleware Order
- In `apps/Server/main.py`, confirm the CORS middleware is added immediately after app creation and before any routes are registered
- The current implementation is correct - CORS middleware is added at lines 53-59, before routers are included at lines 62-70
- No changes needed, but verify the order is maintained

### Step 3: Run Backend Tests to Ensure No Regressions
- Execute `cd apps/Server && uv run pytest tests/` to verify all existing tests pass
- Pay particular attention to tests in `tests/test_category.py` for category-related functionality

### Step 4: Manual Verification of Fix
- Start the backend server: `cd apps/Server && python -m uvicorn main:app --reload --port 8000`
- Verify the server starts without errors
- Check the console output shows CORS origins are loaded correctly
- Test the health endpoint: `curl http://localhost:8000/api/health` should return 200 with CORS headers

### Step 5: Test Category Creation API Directly
- Use curl or a tool like httpie to test the category endpoint directly:
  ```bash
  # Test OPTIONS preflight
  curl -X OPTIONS http://localhost:8000/api/categories/ \
    -H "Origin: http://localhost:5173" \
    -H "Access-Control-Request-Method: POST" \
    -v

  # Verify Access-Control-Allow-Origin header is present in response
  ```

### Step 6: Run E2E Test to Validate Full Flow
- Read `.claude/commands/test_e2e.md` for E2E test runner instructions
- Execute the existing E2E test for category management at `.claude/commands/e2e/test_category_management.md`
- Verify all test steps pass, especially:
  - Category creation (steps 15-17)
  - Success message displayed
  - Category appears in the tree view

### Step 7: Run Validation Commands
- Execute all validation commands listed in the Validation Commands section below

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `cd apps/Server && uv run pytest tests/` - Run Server tests to validate no regressions
- `cd apps/Server && uv run pytest tests/test_category.py -v` - Run category-specific tests to validate category functionality
- `cd apps/Client && npm run tsc --noEmit` - Run Client type check to validate no type errors
- `cd apps/Client && npm run build` - Run Client build to validate the frontend builds successfully

### Manual CORS Verification
After starting the server, run this command to verify CORS headers are present on error responses:
```bash
curl -X POST http://localhost:8000/api/categories/ \
  -H "Origin: http://localhost:5173" \
  -H "Content-Type: application/json" \
  -d '{}' \
  -v 2>&1 | grep -i "access-control"
```

This should show `Access-Control-Allow-Origin: http://localhost:5173` even on error responses.

### E2E Test Validation
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_category_management.md` to validate category creation works end-to-end

## Notes
- The fix is minimal and surgical - only adding a global exception handler to ensure CORS headers are always present on error responses
- The existing CORS configuration in settings.py is correct and doesn't need modification
- This fix will benefit all endpoints, not just categories, by ensuring consistent CORS header behavior on error responses
- The global exception handler logs the exception for debugging while returning a generic error message to clients for security
- If additional debugging is needed, check the backend console for "ERROR [Main]: Unhandled exception" messages
