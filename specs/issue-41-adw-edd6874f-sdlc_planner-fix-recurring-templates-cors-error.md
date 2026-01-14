# Bug: Recurring Templates CORS Error

## Metadata
issue_number: `41`
adw_id: `edd6874f`
issue_json: `{"number":41,"title":"Recurring transactions error message","body":"When going to the Recurring transactions menu option, I get a Network Error..."}`

## Bug Description
When navigating to the Recurring Transactions page in the Finance Tracker application, users encounter a Network Error. The browser console displays a CORS policy violation error followed by a 500 Internal Server Error when attempting to fetch recurring templates from `GET /api/recurring-templates/?entity_id=...`.

**Symptoms:**
- CORS error: "Access to XMLHttpRequest at 'http://localhost:8000/api/recurring-templates/...' from origin 'http://localhost:5173' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource"
- Network Error: "Unable to connect to server. Please ensure the backend is running at http://localhost:8000/api"
- 500 Internal Server Error on the recurring-templates endpoint

**Expected Behavior:**
- The recurring templates page should load successfully and display the list of recurring templates (or an empty state if none exist)
- API responses should include proper CORS headers

**Actual Behavior:**
- The page shows a Network Error
- The browser console shows CORS policy violation
- The backend returns a 500 Internal Server Error that doesn't include CORS headers

## Problem Statement
The recurring-templates API endpoint is throwing an unhandled exception that bypasses the CORS middleware, causing the error response to be sent without the required `Access-Control-Allow-Origin` header. This makes the frontend unable to read the error response due to browser CORS policy enforcement.

## Solution Statement
Investigate and fix the root cause of the 500 Internal Server Error on the recurring-templates endpoint. The error is likely caused by:
1. Missing database table (recurring_templates schema not applied to database)
2. Database connection issues
3. Pydantic serialization errors during response generation

The fix should ensure:
1. The recurring_templates table exists in the database
2. All exceptions are properly caught and return responses with CORS headers
3. The endpoint returns proper error responses that the frontend can handle

## Steps to Reproduce
1. Start the backend server: `cd Server && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`
2. Start the frontend dev server: `cd Client && npm run dev`
3. Navigate to `http://localhost:5173` and log in with valid credentials
4. Click on "Recurring" in the sidebar navigation
5. Observe the Network Error message on the page
6. Check browser developer console to see CORS and 500 errors

## Root Cause Analysis
Based on the error logs and code review:

1. **Primary Issue - Database Schema**: The `recurring_templates` table may not have been created in the Supabase database. The schema was defined in `database/schema.sql` but may not have been applied to the production/development database.

2. **Secondary Issue - Error Handling**: When a database-level exception occurs (e.g., "relation does not exist"), it may bypass the global exception handler in certain scenarios, particularly during:
   - Pydantic model validation (`model_validate()`)
   - SQLAlchemy query execution
   - Response serialization

3. **CORS Header Absence**: The global exception handler in `main.py` is designed to catch unhandled exceptions and return a JSONResponse that flows through the CORS middleware. However, certain exceptions (like those occurring during response serialization in FastAPI) may not be caught by this handler.

4. **Error Flow**:
   - Request arrives at `/api/recurring-templates/`
   - Authentication succeeds
   - Database query fails (likely due to missing table or connection issue)
   - Exception occurs but response may not include CORS headers
   - Browser blocks the response due to missing CORS headers
   - Frontend shows generic "Network Error"

## Relevant Files
Use these files to fix the bug:

### Backend Files
- `apps/Server/main.py` - Entry point with CORS configuration and global exception handler; verify exception handler is catching all errors
- `apps/Server/src/adapter/rest/recurring_template_routes.py` - API routes for recurring templates; may need additional error handling
- `apps/Server/src/core/services/recurring_template_service.py` - Business logic for recurring templates; check for unhandled exceptions
- `apps/Server/src/repository/recurring_template_repository.py` - Data access layer; database operations that may throw exceptions
- `apps/Server/src/models/recurring_template.py` - SQLAlchemy model definition
- `apps/Server/src/interface/recurring_template_dto.py` - Pydantic DTOs for request/response validation
- `apps/Server/database/schema.sql` - Database schema definition; verify recurring_templates table is defined
- `apps/Server/src/config/database.py` - Database connection configuration

### Documentation Files
- `app_docs/bug-dd6d412a-cors-error-category-creation.md` - Previous CORS error fix for reference
- `app_docs/feature-e44986c8-recurring-transactions.md` - Recurring transactions feature documentation

### Frontend Files (for validation)
- `apps/Client/src/services/recurringTemplateService.ts` - Frontend service making API calls
- `apps/Client/src/hooks/useRecurringTemplates.ts` - Hook managing recurring templates state
- `apps/Client/src/pages/RecurringTemplatesPage.tsx` - Page component showing the error

### E2E Test Files
- `.claude/commands/test_e2e.md` - E2E test runner instructions
- `.claude/commands/e2e/test_recurring_transactions.md` - Existing E2E test for recurring transactions feature

## Step by Step Tasks

### 1. Verify Database Schema
- Check if the `recurring_templates` table exists in the database
- Connect to the Supabase database and run: `\dt recurring_templates` or `SELECT * FROM recurring_templates LIMIT 1;`
- If the table doesn't exist, apply the schema from `apps/Server/database/schema.sql`
- Specifically ensure lines 233-278 (recurring_templates table) and lines 280-292 (transactions alter table for recurring_template_id) have been executed

### 2. Add Enhanced Error Handling to Routes
- Read `apps/Server/src/adapter/rest/recurring_template_routes.py`
- Add try-except blocks around database operations in the `list_recurring_templates` endpoint
- Ensure all database and serialization errors are caught and logged
- Return proper HTTPException with appropriate status codes

### 3. Verify Global Exception Handler
- Read `apps/Server/main.py`
- Verify the global exception handler catches all exceptions including SQLAlchemy and Pydantic errors
- Add explicit exception types to the handler if needed (e.g., `@app.exception_handler(SQLAlchemyError)`)
- Ensure error responses flow through CORS middleware

### 4. Add Endpoint-Level Error Handling
- Wrap the list_recurring_templates endpoint logic in try-except
- Catch specific exceptions: `SQLAlchemyError`, `ValidationError`, `Exception`
- Log detailed error information for debugging
- Return appropriate HTTP status codes (500 for server errors, 400 for validation errors)

### 5. Test the Fix Locally
- Start the backend server
- Use curl to test the endpoint directly with CORS headers:
  ```bash
  curl -X GET "http://localhost:8000/api/recurring-templates/?entity_id=649eb405-3b51-433b-921e-7978bb378243&include_inactive=false&skip=0&limit=100" \
    -H "Origin: http://localhost:5173" \
    -H "Authorization: Bearer <token>" \
    -v 2>&1 | grep -i "access-control"
  ```
- Verify CORS headers are present in both success and error responses

### 6. Run Validation Commands
- Execute all validation commands listed in the Validation Commands section
- Ensure all tests pass and the build succeeds
- If the E2E test was updated, run it to validate the fix

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

### Pre-fix Verification (reproduce the bug)
```bash
# Start the backend and verify the error occurs
cd apps/Server && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
sleep 5
curl -X GET "http://localhost:8000/api/recurring-templates/?entity_id=649eb405-3b51-433b-921e-7978bb378243&include_inactive=false&skip=0&limit=100" \
  -H "Origin: http://localhost:5173" \
  -H "Content-Type: application/json" \
  -v 2>&1 | head -50
```

### Post-fix Verification
```bash
# Verify CORS headers are present on error responses
curl -X GET "http://localhost:8000/api/recurring-templates/?entity_id=649eb405-3b51-433b-921e-7978bb378243&include_inactive=false&skip=0&limit=100" \
  -H "Origin: http://localhost:5173" \
  -H "Content-Type: application/json" \
  -v 2>&1 | grep -i "access-control"
```

### Backend Tests
```bash
cd apps/Server && uv run pytest tests/ -v
```

### Frontend Type Check
```bash
cd apps/Client && npm run typecheck
```

### Frontend Build
```bash
cd apps/Client && npm run build
```

### E2E Test
Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_recurring_transactions.md` to validate the recurring transactions functionality works end-to-end.

## Notes

1. **Database Migration Priority**: The most likely root cause is that the `recurring_templates` table was never created in the Supabase database. The first step should be verifying and applying the database schema.

2. **CORS Error Pattern**: This bug follows the same pattern as issue #36 (CORS error during category creation). The existing global exception handler should catch most errors, but specific database-level errors may require additional handling.

3. **WSL2 Considerations**: Since this is a WSL2 development environment, ensure the backend is started with `--host 0.0.0.0` flag to allow connections from the Windows host.

4. **Supabase Connection**: If the database table exists but queries still fail, verify the `DATABASE_URL` in the `.env` file is correct and the connection to Supabase is working.

5. **Error Response Format**: All error responses should be in JSON format to ensure they flow through the CORS middleware:
   ```python
   return JSONResponse(
       status_code=500,
       content={"detail": "Database error occurred"}
   )
   ```

6. **Logging**: The existing code has good logging patterns. Use `print(f"ERROR [ModuleName]: message")` format for new error logs to maintain consistency.
