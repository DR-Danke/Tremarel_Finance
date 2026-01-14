# Bug: WSL2 Backend Not Accessible from Windows Frontend

## Metadata
issue_number: `NA`
adw_id: `NA`
issue_json: `"when I try to create a category, I get an error stating that <Cannot connect to server. Please ensure the backend is running.>"`

## Bug Description
When users try to create a category in the Finance Tracker application, they receive the error message "Cannot connect to server. Please ensure the backend is running." even though the backend server is running. This occurs specifically in WSL2 development environments where the frontend (Vite/React) runs on Windows through WSL interop, but the backend (FastAPI/uvicorn) runs inside WSL2 and binds only to `127.0.0.1`.

**Expected behavior:** Category creation should succeed when both frontend and backend are running.

**Actual behavior:** Frontend cannot reach the backend because uvicorn binds to `localhost:8000` (127.0.0.1), which is not accessible from Windows host.

## Problem Statement
The backend uvicorn server binds to `127.0.0.1:8000` by default, which is only accessible from within WSL2. The frontend running on Windows (via WSL interop with Windows Node.js) cannot reach this address because `localhost` in Windows resolves to a different network namespace than WSL2's `localhost`.

## Solution Statement
Start the backend with `--host 0.0.0.0` flag so uvicorn binds to all network interfaces, making it accessible from both WSL2 and Windows host. This is a development environment configuration issue, not a code bug.

## Steps to Reproduce
1. Start the backend with: `cd apps/Server && .venv/bin/python -m uvicorn main:app --reload --port 8000`
2. Start the frontend with: `cd apps/Client && npm run dev -- --host 0.0.0.0`
3. Open browser to http://localhost:5173
4. Log in and navigate to Categories page
5. Try to create a new category
6. Observe error: "Cannot connect to server. Please ensure the backend is running."

## Root Cause Analysis
The root cause is WSL2 networking architecture:
- WSL2 runs in a lightweight VM with its own network namespace
- `localhost` inside WSL2 resolves to `127.0.0.1` within WSL2's namespace
- `localhost` on Windows host resolves to Windows' loopback interface
- When the frontend runs via Windows Node.js (through WSL interop), API calls to `localhost:8000` go to Windows' localhost, not WSL2's localhost
- The backend bound to `127.0.0.1` inside WSL2 is not accessible from Windows

The solution is to bind uvicorn to `0.0.0.0` which makes it listen on all interfaces, including the virtual ethernet interface that WSL2 uses to communicate with Windows.

## Relevant Files
Use these files to fix the bug:

- `apps/Server/main.py` - Contains the uvicorn.run() configuration at the bottom that defaults to `host="0.0.0.0"` but this is only used when running directly with `python main.py`, not with the `uvicorn` CLI command
- `CLAUDE.md` - Documents the development commands including how to start the backend server

### New Files
None required - this is a configuration/startup procedure issue.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Verify the Issue
- Check that the backend is running with `lsof -i :8000`
- Confirm it's bound to `localhost` (127.0.0.1) not `0.0.0.0`
- Test connectivity from WSL: `curl http://localhost:8000/api/health` (should work)
- Test connectivity from Windows context: Browser at `http://localhost:8000/api/health` (should fail if bound to 127.0.0.1)

### 2. Restart Backend with Correct Host Binding
- Stop the current backend process
- Start the backend with host binding: `cd apps/Server && .venv/bin/python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- Verify it's now bound to `0.0.0.0:8000` with `lsof -i :8000`

### 3. Update CLAUDE.md Documentation
- Update the backend development server command in CLAUDE.md to include `--host 0.0.0.0` for WSL2 compatibility
- Current command: `python -m uvicorn main:app --reload --port 8000`
- Updated command: `python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`

### 4. Test Category Creation
- Open browser to http://localhost:5173
- Log in with valid credentials
- Navigate to Categories page
- Create a new category
- Verify success message appears and category is created

### 5. Run Validation Commands
- Execute all validation commands to ensure no regressions

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `lsof -i :8000 | grep -q "0.0.0.0" && echo "Backend bound to all interfaces" || echo "Backend NOT bound correctly"` - Verify backend is bound to 0.0.0.0
- `curl -s http://localhost:8000/api/health` - Verify backend health check from WSL
- `cd apps/Server && uv run pytest` - Run Server tests to validate the bug is fixed with zero regressions
- `cd apps/Client && npm run tsc --noEmit` - Run Client type check to validate the bug is fixed with zero regressions
- `cd apps/Client && npm run build` - Run Client build to validate the bug is fixed with zero regressions

## Notes
- This is a WSL2-specific development environment issue, not a code bug
- The `main.py` file already has `host="0.0.0.0"` in the `if __name__ == "__main__"` block, but this only applies when running `python main.py` directly, not when using the `uvicorn` CLI command
- Production deployments (Render) are not affected as they use environment variables and proper host binding
- Consider creating a `scripts/start-backend.sh` script that includes the correct flags for development
- The frontend Vite server already uses `--host 0.0.0.0` which is why it's accessible from Windows
