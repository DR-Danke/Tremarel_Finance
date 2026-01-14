# Start the application

## Variables

FRONTEND_PORT: If `.ports.env` exists, read FRONTEND_PORT from it, otherwise default to 5173
BACKEND_PORT: If `.ports.env` exists, read BACKEND_PORT from it, otherwise default to 8000

## Workflow

1. Check if `.ports.env` exists:
   - If it exists, source it and use `FRONTEND_PORT` and `BACKEND_PORT` variables
   - If not, use defaults: FRONTEND_PORT=5173, BACKEND_PORT=8000

2. Check and start the **Backend** (port BACKEND_PORT):
   - Check if a process is running on port BACKEND_PORT with `lsof -i :BACKEND_PORT`
   - If running, log "Backend already running on port BACKEND_PORT"
   - If NOT running:
     - Start backend with: `cd apps/Server && .venv/bin/python -m uvicorn main:app --reload --host 0.0.0.0 --port BACKEND_PORT &`
     - **IMPORTANT**: `--host 0.0.0.0` is required for WSL2 environments so Windows can reach the backend
     - Wait 3 seconds for startup
     - Verify with health check: `curl -s http://localhost:BACKEND_PORT/api/health`

3. Check and start the **Frontend** (port FRONTEND_PORT):
   - Check if a process is running on port FRONTEND_PORT with `lsof -i :FRONTEND_PORT`
   - If running, log "Frontend already running on port FRONTEND_PORT"
   - If NOT running:
     - Start frontend with: `cd apps/Client && npm run dev -- --host 0.0.0.0 &`
     - **IMPORTANT**: `--host 0.0.0.0` is required for WSL2 environments
     - Wait 3 seconds for startup

4. Open browser:
   - Run `powershell.exe -Command "Start-Process 'http://localhost:FRONTEND_PORT'"` (for WSL2)
   - Or `open http://localhost:FRONTEND_PORT` (for Mac/Linux)

5. Report status to user:
   - Frontend: http://localhost:FRONTEND_PORT
   - Backend API: http://localhost:BACKEND_PORT/api
   - API Docs: http://localhost:BACKEND_PORT/docs

## Notes

- In WSL2 environments, both servers must bind to `0.0.0.0` to be accessible from Windows browsers
- The backend uses `.venv` virtual environment in the Server directory
- Frontend uses Vite dev server with hot module replacement