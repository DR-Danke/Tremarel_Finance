# Feature: Legal Desk Demo User with Module-Scoped Access

## Metadata
issue_number: `NA`
adw_id: `NA`
issue_json: `"I am going to present the Legal Desk POC. For this, it would be ideal to create a user who only has access and who can only view the menu items related to this POC. That way I can sign in with that user and do the presentation"`

## Feature Description
Add an `allowed_modules` column to the users table that controls which application sections a user can access. When set (e.g., `["legaldesk"]`), the sidebar only shows that module's navigation items and routes for other modules redirect to the user's default landing page. When `null`, the user has access to all modules (backwards compatible). A seed script creates a "Legal Desk Demo" user with `allowed_modules = ["legaldesk"]` and password `LegalDesk2026!` for presentation purposes.

## User Story
As a product owner presenting the Legal Desk POC
I want to sign in with a dedicated demo account that only shows Legal Desk menu items
So that the presentation is focused and clean without unrelated navigation clutter

## Problem Statement
Currently, all authenticated users see the full sidebar navigation (Finance, POCs with RestaurantOS and Legal Desk, Settings). During a Legal Desk POC presentation, the extra menu items (Finance, RestaurantOS) are distracting and confusing for stakeholders. There is no way to scope a user's view to a specific module.

## Solution Statement
Add a nullable `allowed_modules` JSON column to the `users` table. The backend includes this field in the auth response. The frontend reads it from the `User` object and uses it to:
1. Filter sidebar sections — only showing navigation for allowed modules
2. Redirect unauthorized route access — sending module-restricted users to their default landing page
3. Set the correct post-login landing page — redirecting to `/poc/legal-desk/dashboard` instead of `/dashboard`

This is backwards compatible: existing users with `allowed_modules = NULL` retain full access.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/database/schema.sql` — Users table definition; add `allowed_modules` column
- `apps/Server/src/models/user.py` — SQLAlchemy User model; add `allowed_modules` field
- `apps/Server/src/interface/auth_dto.py` — `UserResponseDTO`; add `allowed_modules` field
- `apps/Server/src/adapter/rest/dependencies.py` — `get_current_user()`; include `allowed_modules` in returned dict
- `apps/Server/src/core/services/auth_service.py` — Auth service; no changes needed (passes User object through)
- `apps/Client/src/types/index.ts` — `User` interface; add `allowed_modules` field
- `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx` — Sidebar; filter sections based on `allowed_modules`
- `apps/Client/src/components/auth/ProtectedRoute.tsx` — Route guard; add module access check
- `apps/Client/src/App.tsx` — Route definitions; wrap Legal Desk and other module routes with module check
- `apps/Client/src/contexts/AuthContext.tsx` — Auth context; ensure `allowed_modules` flows through
- `apps/Server/tests/test_auth.py` — Auth tests; add tests for `allowed_modules` in responses
- Read `app_docs/feature-ed4cef49-backend-jwt-auth-rbac.md` for backend auth patterns
- Read `app_docs/feature-f6f89b86-frontend-jwt-auth-context.md` for frontend auth patterns
- Read `app_docs/feature-75704e1f-section-based-sidebar-navigation.md` for sidebar section patterns
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_auth_login.md` to understand how to create an E2E test file

### New Files
- `apps/Server/database/add_allowed_modules_column.sql` — Migration script to add column and create demo user
- `.claude/commands/e2e/test_legaldesk_demo_user.md` — E2E test for demo user login and restricted navigation

## Implementation Plan
### Phase 1: Foundation (Backend Schema + Model)
Add the `allowed_modules` column to the database and SQLAlchemy model. This is a nullable JSONB column — `NULL` means "all access" (backwards compatible). Create a migration script that adds the column and inserts the demo user.

### Phase 2: Core Implementation (Backend API + Frontend Types)
Update `UserResponseDTO` and `get_current_user` dependency to include `allowed_modules`. Update the frontend `User` type to receive and store this field. No JWT payload changes needed — the field is fetched from the database on every `get_current_user` call.

### Phase 3: Integration (Sidebar Filtering + Route Guards)
Update `TRCollapsibleSidebar` to filter navigation sections based on `user.allowed_modules`. Update `ProtectedRoute` or `App.tsx` to redirect module-restricted users away from non-allowed routes. Set the correct post-login redirect for module-restricted users.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create migration script with demo user
- Create `apps/Server/database/add_allowed_modules_column.sql`:
  ```sql
  -- Add allowed_modules column (nullable JSONB, NULL = all access)
  ALTER TABLE users ADD COLUMN IF NOT EXISTS allowed_modules JSONB DEFAULT NULL;

  -- Insert Legal Desk demo user
  -- Password: LegalDesk2026! (bcrypt hash)
  INSERT INTO users (email, password_hash, first_name, last_name, role, allowed_modules)
  VALUES (
    'demo.legaldesk@tremarel.com',
    '$2b$12$HASH_PLACEHOLDER',  -- Generate real hash in step
    'Legal Desk',
    'Demo',
    'manager',
    '["legaldesk"]'
  )
  ON CONFLICT (email) DO UPDATE SET allowed_modules = '["legaldesk"]';
  ```
- Generate the bcrypt hash for `LegalDesk2026!` using the backend's auth_service
- Run the migration against the database

### Step 2: Update SQLAlchemy User model
- Open `apps/Server/src/models/user.py`
- Add import: `from sqlalchemy.dialects.postgresql import JSONB`
- Add column: `allowed_modules = Column(JSONB, nullable=True, default=None)` after the `is_active` column
- This maps to the new `allowed_modules` JSONB column

### Step 3: Update UserResponseDTO
- Open `apps/Server/src/interface/auth_dto.py`
- Add to `UserResponseDTO`: `allowed_modules: Optional[list[str]] = Field(None, description="List of allowed module keys, null means all access")`
- Add `Optional` and `list` to imports if needed

### Step 4: Update get_current_user dependency
- Open `apps/Server/src/adapter/rest/dependencies.py`
- In the returned dict (lines 103-110), add: `"allowed_modules": user.allowed_modules`

### Step 5: Update frontend User type
- Open `apps/Client/src/types/index.ts`
- Add `allowed_modules?: string[] | null` to the `User` interface

### Step 6: Update sidebar to filter by allowed_modules
- Open `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`
- Import `useAuth` from AuthContext
- Get `user` from `useAuth()`
- Define a module-to-section mapping:
  - `"legaldesk"` → Legal Desk subsection paths start with `/poc/legal-desk`
  - `"restaurant_os"` → RestaurantOS subsection paths start with `/poc/restaurant-os`
  - `"finance"` → Finance section paths (no prefix or `/dashboard`, `/transactions`, etc.)
- Update `buildNavigationSections` to accept `allowedModules: string[] | null` parameter
- When `allowedModules` is not null:
  - If `allowedModules` includes `"legaldesk"` only: return only the Legal Desk subsection items as a flat section (like the entity-less RestaurantOS pattern) + settings
  - Filter POC subsections to only those matching allowed modules
  - Only include finance section if `"finance"` is in `allowedModules`
- When `allowedModules` is null: current behavior (all sections)

### Step 7: Update post-login redirect for module-restricted users
- Open `apps/Client/src/components/auth/ProtectedRoute.tsx`
- After authentication check, if user has `allowed_modules` set (not null/undefined):
  - Define a mapping: `{ legaldesk: '/poc/legal-desk/dashboard', restaurant_os: '/poc/restaurant-os/dashboard', finance: '/dashboard' }`
  - If current location path does not start with any allowed module prefix, redirect to the first allowed module's default page
- This ensures navigating to `/dashboard` (the default post-login) redirects to `/poc/legal-desk/dashboard` for the demo user

### Step 8: Add backend tests
- Open `apps/Server/tests/test_auth.py`
- Add test verifying `allowed_modules` is included in `UserResponseDTO` serialization
- Add test verifying `get_current_user` returns `allowed_modules` in the user dict
- Add test for `allowed_modules = None` (full access user) and `allowed_modules = ["legaldesk"]` (restricted user)

### Step 9: Create E2E test file
- Read `.claude/commands/e2e/test_auth_login.md` and `.claude/commands/e2e/test_legaldesk_pages.md` to understand the E2E test pattern
- Create `.claude/commands/e2e/test_legaldesk_demo_user.md` with steps:
  1. Navigate to `/login`
  2. Sign in with `demo.legaldesk@tremarel.com` / `LegalDesk2026!`
  3. **Verify** redirect to `/poc/legal-desk/dashboard` (not `/dashboard`)
  4. **Verify** sidebar only shows Legal Desk items (Dashboard, Cases, Specialists, Clients, Analytics) and Settings
  5. **Verify** Finance section is NOT visible
  6. **Verify** RestaurantOS section is NOT visible
  7. Click "Cases" in sidebar, verify navigation works
  8. Navigate manually to `/dashboard` (Finance), verify redirect back to Legal Desk
  9. Take screenshots at key steps

### Step 10: Run validation commands
- Execute all validation commands below

## Testing Strategy
### Unit Tests
- `test_auth.py`: Verify `allowed_modules` is included in `UserResponseDTO` serialization for both null and non-null values
- `test_auth.py`: Verify `get_current_user` dependency returns `allowed_modules` field
- Frontend type check: Verify `User` interface includes `allowed_modules`

### Edge Cases
- User with `allowed_modules = null` sees all sections (backwards compatibility)
- User with `allowed_modules = []` (empty array) sees only Settings
- User with `allowed_modules = ["legaldesk"]` sees only Legal Desk + Settings
- User with `allowed_modules = ["legaldesk", "finance"]` sees both
- Direct URL navigation to non-allowed module redirects correctly
- Post-login redirect goes to the first allowed module's default page

## Acceptance Criteria
- A demo user `demo.legaldesk@tremarel.com` exists with password `LegalDesk2026!`
- Signing in with this user redirects to `/poc/legal-desk/dashboard`
- The sidebar only shows Legal Desk navigation items (Dashboard, Cases, Specialists, Clients, Analytics) and Settings
- Finance section, RestaurantOS section, and entity selector are NOT visible
- Navigating to `/dashboard` or `/transactions` redirects back to `/poc/legal-desk/dashboard`
- Existing users with `allowed_modules = NULL` are not affected — they see all sections as before
- All backend tests pass
- Frontend type check and build succeed

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && .venv/bin/python -c "from src.core.services.auth_service import auth_service; print(auth_service.hash_password('LegalDesk2026!'))"` — Generate bcrypt hash for migration script
- `cd apps/Server && .venv/bin/python -m pytest tests/test_auth.py -x -v` — Run auth tests
- `cd apps/Server && .venv/bin/python -m pytest tests/ -x` — Run all backend tests for zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check
- `cd apps/Client && npm run build` — Run Client build
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_legaldesk_demo_user.md` E2E test to validate this functionality works

## Notes
- The `allowed_modules` field uses module keys: `"legaldesk"`, `"restaurant_os"`, `"finance"`. These are internal identifiers, not display labels.
- The demo user uses role `manager` to have full access to Legal Desk CRUD operations (create cases, assign specialists, etc.) without being an `admin`.
- The demo user does NOT need entity assignments — Legal Desk doesn't use the entity system. The sidebar logic should handle this: when `allowed_modules` is set, bypass the `hasEntities` check entirely.
- Password `LegalDesk2026!` is for demo/presentation only. In production, use strong unique passwords.
- Future enhancement: A UI in Settings to manage `allowed_modules` per user (admin only). Not needed for this task.
- The `allowed_modules` column is added via a separate migration script, not by modifying `schema.sql`, to avoid conflicts with existing deployments. However, `schema.sql` should also be updated for documentation purposes.
