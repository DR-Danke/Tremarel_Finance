# Bug: Fix events endpoint CORS error caused by missing related_resource_id column

## Metadata
issue_number: ``
adw_id: ``
issue_json: ``

## Bug Description
When navigating to the Eventos/Tareas page in RestaurantOS, the browser console shows a CORS error:
```
Access to XMLHttpRequest at 'http://localhost:8000/api/events?restaurant_id=75925fef-8db1-4b96-8534-7058a92ae59c' from origin 'http://localhost:5173' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```
Followed by `ERR_NETWORK` / `net::ERR_FAILED` errors. The page fails to load any event data.

**Expected behavior**: The `/api/events` endpoint returns the list of events for the restaurant with proper CORS headers.

**Actual behavior**: The endpoint crashes with an unhandled `ProgrammingError` before the CORS middleware can attach response headers, causing the browser to report a CORS violation instead of showing the actual 500 Internal Server Error.

## Problem Statement
The SQLAlchemy `Event` model includes a `related_resource_id` column (added by the low-stock-alert-automation feature), but the corresponding database migration (`alter_event_add_related_resource_id.sql`) was never applied to the database. Every query to the `event` table generates SQL that references `event.related_resource_id`, which does not exist, causing a `ProgrammingError` that crashes the request handler.

## Solution Statement
Apply the missing database migration to add the `related_resource_id` column and its index to the `event` table. This is a non-destructive `ALTER TABLE ADD COLUMN` operation that brings the database schema in sync with the SQLAlchemy model.

## Steps to Reproduce
1. Start the backend server: `cd apps/Server && .venv/bin/python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`
2. Start the frontend: `cd apps/Client && npm run dev -- --host 0.0.0.0`
3. Log in to the application
4. Navigate to a restaurant's Eventos/Tareas page
5. Observe CORS errors in the browser console and no events loading

**Reproduce via CLI**:
```bash
cd apps/Server && .venv/bin/python -c "
from src.config.database import SessionLocal
from src.repository.event_repository import event_repository
from uuid import UUID
db = SessionLocal()
events = event_repository.get_by_restaurant(db, UUID('75925fef-8db1-4b96-8534-7058a92ae59c'))
"
```
This produces: `ProgrammingError: column event.related_resource_id does not exist`

## Root Cause Analysis
1. The `Event` model (`apps/Server/src/models/event.py`) defines 15 columns including `related_resource_id` (a UUID FK to `resource.id`).
2. The database `event` table only has 14 columns — it is missing `related_resource_id`.
3. The migration file `apps/Server/database/alter_event_add_related_resource_id.sql` exists but was never executed against the database.
4. When any `db.query(Event)` runs, SQLAlchemy generates `SELECT ... event.related_resource_id ...` which fails with `ProgrammingError: column event.related_resource_id does not exist`.
5. The `ProgrammingError` is not caught by the route's `PermissionError` handler, bubbles up to FastAPI's global exception handler, but the error response does not get CORS headers applied in time, causing the browser to report it as a CORS error.

This is the same root cause pattern as the previously fixed document table CORS bug (see `app_docs/bug-dd6d412a-cors-error-category-creation.md`).

## Relevant Files
Use these files to fix the bug:

- `apps/Server/database/alter_event_add_related_resource_id.sql` — The migration file that needs to be applied. Contains the `ALTER TABLE` and `CREATE INDEX` statements.
- `apps/Server/src/models/event.py` — The SQLAlchemy model that defines `related_resource_id`. Read to confirm the column definition matches the migration.
- `apps/Server/src/repository/event_repository.py` — The repository that queries the `event` table. Read to understand all query patterns that reference `related_resource_id`.
- `apps/Server/src/adapter/rest/event_routes.py` — The route handlers. Read to confirm error handling patterns.
- `apps/Server/src/core/services/event_service.py` — The service layer. Read to confirm the call chain.
- `apps/Client/src/services/eventService.ts` — Frontend service making the API call. Read to confirm the request format.
- `apps/Client/src/hooks/useEvents.ts` — Frontend hook consuming the service. Read to confirm the error handling.
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_event_task_management.md` to understand the existing E2E test and create a targeted regression test.

### New Files
- `.claude/commands/e2e/test_event_list_load.md` — E2E test to validate the events page loads without CORS errors.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Verify the missing column
- Run the following to confirm the column is missing:
  ```bash
  cd apps/Server && .venv/bin/python -c "
  from src.config.database import SessionLocal
  from sqlalchemy import text
  db = SessionLocal()
  result = db.execute(text(\"SELECT column_name FROM information_schema.columns WHERE table_name = 'event' AND column_name = 'related_resource_id'\"))
  rows = result.fetchall()
  if rows:
      print('Column exists - no fix needed')
  else:
      print('Column MISSING - fix required')
  db.close()
  "
  ```

### Step 2: Apply the database migration
- Read `apps/Server/database/alter_event_add_related_resource_id.sql` to confirm the migration contents.
- Execute the migration against the database:
  ```bash
  cd apps/Server && .venv/bin/python -c "
  from src.config.database import SessionLocal
  from sqlalchemy import text
  db = SessionLocal()
  db.execute(text('ALTER TABLE event ADD COLUMN IF NOT EXISTS related_resource_id UUID REFERENCES resource(id) ON DELETE SET NULL'))
  db.execute(text('CREATE INDEX IF NOT EXISTS idx_event_related_resource ON event(related_resource_id)'))
  db.commit()
  print('Migration applied successfully')
  db.close()
  "
  ```

### Step 3: Verify the fix
- Run the same repository query that was failing:
  ```bash
  cd apps/Server && .venv/bin/python -c "
  from src.config.database import SessionLocal
  from src.repository.event_repository import event_repository
  from uuid import UUID
  db = SessionLocal()
  events = event_repository.get_by_restaurant(db, UUID('75925fef-8db1-4b96-8534-7058a92ae59c'))
  print(f'Success: Found {len(events)} events')
  db.close()
  "
  ```
- Test the API endpoint directly:
  ```bash
  curl -s -H 'Origin: http://localhost:5173' 'http://localhost:8000/api/events?restaurant_id=75925fef-8db1-4b96-8534-7058a92ae59c' -w '\n%{http_code}' | tail -1
  ```
  Should return `401` (not authenticated) instead of crashing. Verify CORS headers are present:
  ```bash
  curl -sv -H 'Origin: http://localhost:5173' 'http://localhost:8000/api/events?restaurant_id=75925fef-8db1-4b96-8534-7058a92ae59c' 2>&1 | grep -i 'access-control-allow-origin'
  ```

### Step 4: Create E2E regression test
- Read `.claude/commands/e2e/test_event_task_management.md` and `.claude/commands/test_e2e.md` to understand the E2E test format.
- Create a new E2E test file `.claude/commands/e2e/test_event_list_load.md` that validates:
  1. Navigate to the Eventos/Tareas page for a restaurant
  2. Verify the page loads without CORS errors in the console
  3. Verify the events list component renders (even if empty)
  4. Take a screenshot to prove the page loaded successfully

### Step 5: Run validation commands
- Execute all validation commands listed below to confirm zero regressions.

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- Verify column exists after migration:
  ```bash
  cd apps/Server && .venv/bin/python -c "
  from src.config.database import SessionLocal
  from sqlalchemy import text
  db = SessionLocal()
  result = db.execute(text(\"SELECT column_name FROM information_schema.columns WHERE table_name = 'event' AND column_name = 'related_resource_id'\"))
  rows = result.fetchall()
  assert len(rows) == 1, 'Column still missing!'
  print('PASS: related_resource_id column exists')
  db.close()
  "
  ```

- Verify repository query succeeds:
  ```bash
  cd apps/Server && .venv/bin/python -c "
  from src.config.database import SessionLocal
  from src.repository.event_repository import event_repository
  from uuid import UUID
  db = SessionLocal()
  events = event_repository.get_by_restaurant(db, UUID('75925fef-8db1-4b96-8534-7058a92ae59c'))
  print(f'PASS: Query succeeded, found {len(events)} events')
  db.close()
  "
  ```

- Verify API endpoint returns proper response with CORS headers:
  ```bash
  curl -s -H 'Origin: http://localhost:5173' -o /dev/null -w '%{http_code}' 'http://localhost:8000/api/events?restaurant_id=75925fef-8db1-4b96-8534-7058a92ae59c'
  ```
  Expected: `401` (not `500` or connection error)

- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_event_list_load.md` E2E test to validate this functionality works.

- `cd apps/Server && .venv/bin/python -m pytest` — Run Server tests to validate the bug is fixed with zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate the bug is fixed with zero regressions
- `cd apps/Client && npm run build` — Run Client build to validate the bug is fixed with zero regressions

## Notes
- This is the exact same root cause pattern as the document table CORS bug fixed earlier in this session (missing `processing_status` and `processing_result` columns on the `document` table).
- The migration file `apps/Server/database/alter_event_add_related_resource_id.sql` already exists — it just was never applied to the database. No code changes are needed, only a database schema update.
- The `ALTER TABLE ADD COLUMN IF NOT EXISTS` syntax is used to make the migration idempotent (safe to run multiple times).
- Consider auditing all other model-to-database column mappings to catch any other unapplied migrations proactively.
