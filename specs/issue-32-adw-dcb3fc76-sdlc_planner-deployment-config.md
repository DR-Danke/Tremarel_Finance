# Chore: Deployment Configuration

## Metadata
issue_number: `32`
adw_id: `dcb3fc76`
issue_json: `{"number":32,"title":"[FinanceTracker] Wave 6: Deployment Configuration","body":"```markdown\n## Context\n**Project:** Finance Tracker - Income & Expense Management\n**Overview:** We are building a full-stack income/expense tracking application for family and startup company management. The system includes multi-entity support (family/startup separation), custom JWT authentication, transaction management, budgeting, reporting with charts, and CSV export. Frontend deploys to Vercel, backend to Render, database on Supabase PostgreSQL.\n\n**Current Wave:** Wave 6 of 6 - Polish & Deploy\n**Current Issue:** FT-014 (Issue 14 of 14)\n**Parallel Execution:** NO - This is the final issue that prepares the application for production deployment.\n\n**Dependencies:** Requires all previous waves to be complete.\n**What comes next:** After this issue, the application is ready for production deployment!\n\n## Request\nFinalize deployment configuration. Ensure vercel.json is correct for the Client folder. Add any needed Render configuration for the Server folder. Create .env.sample files documenting all required environment variables. Update README with deployment instructions. Verify CORS is configured for production URLs.\n```"}`

## Chore Description

This chore finalizes the deployment configuration for the Finance Tracker application, ensuring both frontend (Vercel) and backend (Render) are properly configured for production deployment. The tasks include:

1. **Vercel Configuration (Client)**: Verify and enhance `vercel.json` for SPA routing and proper build configuration
2. **Render Configuration (Server)**: Create `render.yaml` with proper Python version, build/start commands, and health check configuration
3. **Environment Variable Documentation**: Update `.env.sample` files for both Client and Server with comprehensive documentation including production placeholders
4. **README Updates**: Create deployment instructions in the apps folder README with step-by-step guides for Vercel, Render, and Supabase setup
5. **CORS Verification**: Ensure CORS configuration supports production URLs in JSON array format

## Relevant Files

Use these files to resolve the chore:

- `apps/Client/vercel.json` - Existing Vercel configuration for SPA deployment. Already has basic rewrites for SPA routing; may need verification for production readiness.
- `apps/Client/.env.sample` - Existing client environment variables template. Currently minimal; needs production URL placeholders and documentation.
- `apps/Client/vite.config.ts` - Vite build configuration. Reference for understanding build output configuration.
- `apps/Client/package.json` - NPM configuration with build scripts. Reference for build command verification.
- `apps/Server/.env.sample` - Existing server environment variables template. Has good documentation; needs production placeholders for CORS.
- `apps/Server/main.py` - FastAPI entry point. Contains CORS middleware configuration that needs to support production URLs.
- `apps/Server/src/config/settings.py` - Pydantic Settings class. Contains CORS parsing logic; need to verify production URL support.
- `apps/Server/requirements.txt` - Python dependencies. Reference for Render configuration.
- `app_docs/feature-0f0d4c36-fastapi-backend-setup.md` - Backend setup documentation. Contains environment variable documentation.
- `app_docs/feature-2a0579e1-frontend-react-vite-setup.md` - Frontend setup documentation. Contains Vercel deployment notes.

### New Files

- `apps/Server/render.yaml` - New file. Render deployment configuration with service definition, build commands, health check, and environment variable placeholders.
- `apps/README.md` - New file. Deployment documentation with step-by-step instructions for Vercel, Render, and Supabase setup.

## Step by Step Tasks

### Step 1: Verify and Update Client vercel.json

- Read `apps/Client/vercel.json` to verify current configuration
- Ensure the following configuration is present:
  - `buildCommand`: "npm run build"
  - `outputDirectory`: "dist"
  - `framework`: "vite"
  - `rewrites`: SPA fallback to index.html for client-side routing
- The current configuration appears correct; verify no changes needed

### Step 2: Update Client .env.sample with Production Documentation

- Update `apps/Client/.env.sample` with comprehensive documentation:
  - Add header comment explaining the purpose
  - Include `VITE_API_URL` with both localhost and production placeholder examples
  - Include `VITE_APP_NAME` with descriptive comment
  - Add comments about environment-specific values

### Step 3: Create Render Configuration for Server

- Create `apps/Server/render.yaml` with the following configuration:
  - Service type: web
  - Service name: finance-tracker-api
  - Environment: python
  - Build command: `pip install -r requirements.txt`
  - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
  - Health check path: `/api/health`
  - Python version: 3.11.9 (critical for compatibility)
  - Environment variables placeholders (DATABASE_URL, JWT_SECRET_KEY, etc.)
  - Plan: starter (free tier)

### Step 4: Update Server .env.sample with Production Documentation

- Update `apps/Server/.env.sample` with enhanced documentation:
  - Keep existing environment variables
  - Add production URL examples for CORS_ORIGINS (include Vercel URL placeholder)
  - Add clear section headers for different configuration categories
  - Add comments explaining the JSON array format for CORS

### Step 5: Verify CORS Configuration in Settings

- Read `apps/Server/src/config/settings.py` to verify CORS parsing logic
- Verify the `get_cors_origins()` method properly parses JSON array format
- The current implementation should support multiple origins in JSON format: `["http://localhost:5173","https://your-app.vercel.app"]`
- No code changes expected; verification only

### Step 6: Create Deployment README

- Create `apps/README.md` with comprehensive deployment documentation:
  - Overview section explaining the deployment architecture
  - Prerequisites section (accounts needed: Vercel, Render, Supabase)
  - Database Setup section (Supabase PostgreSQL configuration)
  - Backend Deployment section (Render step-by-step)
  - Frontend Deployment section (Vercel step-by-step)
  - Environment Variables reference table
  - Post-deployment verification checklist
  - Troubleshooting common issues

### Step 7: Run Validation Commands

- Run Server tests to ensure no regressions: `cd apps/Server && python -m pytest tests/ -v`
- Run Client type check: `cd apps/Client && npm run typecheck`
- Run Client build: `cd apps/Client && npm run build`
- Run Client lint: `cd apps/Client && npm run lint`

## Validation Commands

Execute every command to validate the chore is complete with zero regressions.

- `cd /mnt/c/Users/guill/danke_apps/tac/tac-8/tac8_app1__agent_layer_primitives/trees/dcb3fc76/apps/Server && python -m pytest tests/ -v` - Run Server tests to validate no regressions
- `cd /mnt/c/Users/guill/danke_apps/tac/tac-8/tac8_app1__agent_layer_primitives/trees/dcb3fc76/apps/Client && npm run typecheck` - Validate TypeScript types
- `cd /mnt/c/Users/guill/danke_apps/tac/tac-8/tac8_app1__agent_layer_primitives/trees/dcb3fc76/apps/Client && npm run build` - Validate production build succeeds
- `cd /mnt/c/Users/guill/danke_apps/tac/tac-8/tac8_app1__agent_layer_primitives/trees/dcb3fc76/apps/Client && npm run lint` - Validate linting passes

## Notes

- **Python Version**: The Render configuration MUST specify `PYTHON_VERSION=3.11.9` as this is critical for compatibility with the project dependencies.
- **CORS Format**: CORS_ORIGINS must be in JSON array format: `["origin1","origin2"]`. The settings.py already handles this parsing correctly.
- **vercel.json Location**: The vercel.json file should remain in the Client folder (not root) since Vercel is configured with root directory as "Client".
- **render.yaml Location**: The render.yaml file should be in the Server folder (not root) since Render is configured with root directory as "Server".
- **No Code Changes Expected**: This chore primarily involves configuration files and documentation. The CORS handling in settings.py is already correctly implemented.
- **Health Check**: The backend already has a health endpoint at `/api/health` which Render will use for health checks.
