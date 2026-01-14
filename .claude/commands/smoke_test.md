# Application Smoke Test

## Purpose

Validate that frontend and backend can communicate before running full test suite.
This is a **non-blocking validation** - failures are logged as warnings but do not stop the workflow.

## Variables

- BACKEND_PORT: Read from `.ports.env` if exists, otherwise default to 8000
- FRONTEND_PORT: Read from `.ports.env` if exists, otherwise default to 5173

## Workflow

### 1. Read Port Configuration

Check if `.ports.env` exists:
- If it exists, source it and use `BACKEND_PORT` and `FRONTEND_PORT` variables
- If not, use defaults: BACKEND_PORT=8000, FRONTEND_PORT=5173

### 2. Start Backend (if not running)

- Check if backend is running: `lsof -i :$BACKEND_PORT`
- If NOT running:
  - Start with: `cd apps/Server && .venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT &`
  - **CRITICAL**: Must use `--host 0.0.0.0` for WSL2 compatibility
  - Wait up to 10 seconds for startup
  - Verify with health check: `curl -s http://localhost:$BACKEND_PORT/api/health`

### 3. Start Frontend (if not running)

- Check if frontend is running: `lsof -i :$FRONTEND_PORT`
- If NOT running:
  - Start with: `cd apps/Client && npm run dev -- --host 0.0.0.0 &`
  - **CRITICAL**: Must use `--host 0.0.0.0` for WSL2 compatibility
  - Wait up to 10 seconds for startup

### 4. Run Smoke Tests

Execute the following tests and collect results:

**Test 1: Backend Health**
```bash
curl -s http://localhost:$BACKEND_PORT/api/health
```
- Pass: Returns JSON with `"status": "healthy"`
- Fail: Connection refused, timeout, or unhealthy status

**Test 2: Frontend Serves**
```bash
curl -s http://localhost:$FRONTEND_PORT | head -5
```
- Pass: Returns HTML content (contains `<!DOCTYPE html>`)
- Fail: Connection refused or no HTML returned

**Test 3: CORS Preflight**
```bash
curl -s -X OPTIONS -H "Origin: http://localhost:$FRONTEND_PORT" http://localhost:$BACKEND_PORT/api/health -i
```
- Pass: Returns 200 status with CORS headers
- Fail: Returns error or missing CORS headers

**Test 4: Backend Bound to All Interfaces**
```bash
lsof -i :$BACKEND_PORT | grep -q "\*:$BACKEND_PORT\|0.0.0.0"
```
- Pass: Backend bound to `*` or `0.0.0.0`
- Fail: Backend only bound to `localhost` or `127.0.0.1`

### 5. Report Results

Return a JSON array with test results:

```json
[
  {
    "test": "backend_health",
    "passed": true,
    "details": "Backend returned healthy status"
  },
  {
    "test": "frontend_serves",
    "passed": true,
    "details": "Frontend returned HTML content"
  },
  {
    "test": "cors_preflight",
    "passed": true,
    "details": "CORS headers present"
  },
  {
    "test": "backend_binding",
    "passed": true,
    "details": "Backend bound to 0.0.0.0"
  }
]
```

### 6. Summary

After running all tests:
- Count passed/failed tests
- Log summary: `INFO [SmokeTest]: X/4 tests passed`
- If any test failed, log: `WARN [SmokeTest]: Smoke test has warnings - see details above`
- **Do not fail the workflow** - this is informational only

## Success Criteria

All tests should pass for optimal operation:
- Backend returns healthy status
- Frontend returns HTML
- CORS preflight succeeds
- Backend is bound to all interfaces (0.0.0.0)

## Notes

- This smoke test is **non-blocking** - failures generate warnings but don't stop the ADW workflow
- Always use `--host 0.0.0.0` when starting services for WSL2 compatibility
- The test validates connectivity that unit tests cannot catch
- Run this before E2E tests to catch configuration issues early
