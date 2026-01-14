# Bug Fix: CORS Error When Creating Categories

**ADW ID:** dd6d412a
**Date:** 2026-01-14
**Specification:** specs/issue-36-adw-dd6d412a-sdlc_planner-fix-cors-category-creation.md

## Overview

Fixed a CORS policy violation that occurred when creating categories in the Finance Tracker application. The issue was caused by unhandled exceptions bypassing the CORS middleware, resulting in error responses without the required `Access-Control-Allow-Origin` header. The fix adds a global exception handler to ensure all responses (including errors) include proper CORS headers.

## What Was Built

- Global exception handler in FastAPI application to catch all unhandled exceptions
- Proper JSON error responses that flow through CORS middleware
- Logging for unhandled exceptions to aid debugging

## Technical Implementation

### Files Modified

- `apps/Server/main.py`: Added global exception handler and required imports (`Request`, `JSONResponse`)
- `apps/Server/tests/test_*.py`: Updated all test files to use bcrypt directly for password hashing

### Key Changes

- Added `Request` and `JSONResponse` imports from FastAPI
- Implemented `@app.exception_handler(Exception)` decorator to catch all unhandled exceptions
- Exception handler returns a proper `JSONResponse` with status code 500 and generic error message
- Handler logs the exception type and message for debugging: `ERROR [Main]: Unhandled exception: {type}: {message}`
- Error responses now flow through the CORS middleware, ensuring headers are always present

## How to Use

1. The fix is automatic - no user action required
2. All API error responses now include proper CORS headers
3. If debugging is needed, check backend console for `ERROR [Main]: Unhandled exception` messages

## Configuration

No additional configuration required. The fix works with the existing CORS configuration in `apps/Server/src/config/settings.py`:

```bash
CORS_ORIGINS=["http://localhost:5173","https://your-app.vercel.app"]
```

## Testing

### Verify CORS Headers on Error Responses

After starting the server, run this command to verify CORS headers are present on error responses:

```bash
curl -X POST http://localhost:8000/api/categories/ \
  -H "Origin: http://localhost:5173" \
  -H "Content-Type: application/json" \
  -d '{}' \
  -v 2>&1 | grep -i "access-control"
```

This should show `Access-Control-Allow-Origin: http://localhost:5173` even on error responses.

### Run Backend Tests

```bash
cd apps/Server && uv run pytest tests/
```

### Run E2E Category Management Test

Execute the E2E test at `.claude/commands/e2e/test_category_management.md` to validate the full category creation flow.

## Notes

- The fix benefits all endpoints, not just categories, by ensuring consistent CORS header behavior on error responses
- The global exception handler logs exceptions for debugging while returning a generic error message to clients for security
- The existing CORS configuration was correct; the issue was error responses bypassing the middleware
