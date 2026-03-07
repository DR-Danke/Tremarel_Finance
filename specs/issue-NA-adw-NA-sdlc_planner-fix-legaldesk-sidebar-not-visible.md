# Bug: Legal Desk POC not visible in sidebar navigation

## Metadata
issue_number: `NA`
adw_id: `NA`
issue_json: `N/A - reported directly by user with screenshot`

## Bug Description
The user reports they cannot see the "Legal Desk" (Legal Hub) POC section in the sidebar navigation menu. The screenshot shows the sidebar with: Entity selector (KAI Partners), FINANCE section (7 items), POCS section expanded with only RESTAURANTOS subsection (6 items), and Settings at the bottom. The Legal Desk subsection (Dashboard, Cases, Specialists, Clients, Analytics) is completely missing between RESTAURANTOS and Settings.

**Expected behavior:** Under the POCS section, both RESTAURANTOS and LEGAL DESK subsections should be visible with their respective navigation items.

**Actual behavior:** Only RESTAURANTOS subsection appears under POCS. Legal Desk is absent.

## Problem Statement
The Legal Desk sidebar navigation items and routes were added as part of the Wave 6 merge (issues 151-153) into `main`. However, the user's running development server was still serving the pre-merge build, which did not include the Legal Desk sidebar entries. The fix requires verifying the code is correct (it is), restarting the development server to pick up the merged changes, and adding an E2E test to prevent regression.

Additionally, with the full Legal Desk navigation items added, the sidebar total content height (~1160px) may exceed typical viewport heights (720-900px). While MUI Drawer paper defaults to `overflow-y: auto`, we should explicitly ensure the sidebar `<List>` container scrolls to guarantee Legal Desk items are always accessible regardless of viewport height.

## Solution Statement
1. **Verify code correctness** — The `TRCollapsibleSidebar.tsx` already contains the Legal Desk subsection (lines 92-101) and `App.tsx` has all 7 Legal Desk routes registered (lines 255-329). No code changes needed for the core issue.
2. **Ensure sidebar scrollability** — Add explicit `overflowY: 'auto'` styling to the `<List>` component in `TRCollapsibleSidebar.tsx` so that all navigation items are scrollable when they exceed viewport height.
3. **Create E2E test** — Add an E2E test that validates the Legal Desk sidebar items are visible and navigable.
4. **Rebuild and verify** — Restart the development server and confirm Legal Desk appears.

## Steps to Reproduce
1. Start the development server (`npm run dev` in Client directory)
2. Log in with valid credentials
3. Observe the sidebar navigation
4. The POCS section shows only RESTAURANTOS — Legal Desk is missing

## Root Cause Analysis
The screenshot was captured from a running development server that loaded the pre-merge codebase. The Wave 6 merge (issues 151, 152, 153) added the Legal Desk subsection to `TRCollapsibleSidebar.tsx` and registered Legal Desk routes in `App.tsx`, but the user's dev server was still serving the old bundle.

Secondary concern: With both RestaurantOS (6 items) and Legal Desk (5 items) subsections plus Finance (7 items) and Settings, the sidebar content height exceeds most viewport heights. The sidebar must be scrollable to ensure all items are reachable.

## Relevant Files
Use these files to fix the bug:

- `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx` — Contains the sidebar navigation definition. Legal Desk subsection exists at lines 92-101. May need scrollability fix for the List container.
- `apps/Client/src/App.tsx` — Contains route registrations. Legal Desk routes exist at lines 255-329. No changes needed.
- `app_docs/feature-83119edc-legaldesk-routes-sidebar-navigation.md` — Documentation for the Legal Desk routes and sidebar navigation feature.
- `app_docs/feature-a201d4c8-main-layout-collapsible-sidebar.md` — Documentation for the main layout and sidebar component.
- `app_docs/feature-75704e1f-section-based-sidebar-navigation.md` — Documentation for the section-based sidebar navigation pattern.
- `.claude/commands/test_e2e.md` — E2E test runner instructions.
- `.claude/commands/e2e/test_basic_query.md` — E2E test file example for reference.

### New Files
- `.claude/commands/e2e/test_legaldesk_sidebar_visibility.md` — E2E test to validate Legal Desk sidebar items are visible and navigable.

## Step by Step Tasks

### Step 1: Verify sidebar code correctness
- Read `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`
- Confirm the `pocSection.subsections` array contains both `RestaurantOS` (index 0) and `Legal Desk` (index 1) entries
- Confirm Legal Desk has 5 items: Dashboard, Cases, Specialists, Clients, Analytics
- Confirm icons are imported: GavelIcon, BusinessCenterIcon, PersonSearchIcon, GroupsIcon, AnalyticsIcon
- Read `apps/Client/src/App.tsx` and confirm 7 Legal Desk routes are registered under `/poc/legal-desk/*`

### Step 2: Ensure sidebar scrollability
- In `TRCollapsibleSidebar.tsx`, add `sx={{ overflowY: 'auto', flex: 1 }}` to the `<List>` component that wraps the navigation sections (currently at line ~405)
- This ensures that when sidebar content exceeds viewport height, users can scroll to see all items including Legal Desk at the bottom of the POCS section

### Step 3: Create E2E test for Legal Desk sidebar visibility
- Read `.claude/commands/e2e/test_basic_query.md` and `.claude/commands/e2e/test_section_based_sidebar_navigation.md` as reference
- Create `.claude/commands/e2e/test_legaldesk_sidebar_visibility.md` that validates:
  1. Log in with valid credentials
  2. Navigate to any protected page (e.g., /dashboard)
  3. Expand the POCS section in the sidebar if collapsed
  4. Verify "LEGAL DESK" subsection header is visible
  5. Verify all 5 Legal Desk navigation items are visible: Dashboard, Cases, Specialists, Clients, Analytics
  6. Click "Dashboard" under Legal Desk and verify navigation to `/poc/legal-desk/dashboard`
  7. Verify the sidebar item shows active state (highlighted)
  8. Take screenshot as proof

### Step 4: Run validation commands
- Run TypeScript type check: `cd Client && npx tsc --noEmit`
- Run frontend build: `cd Client && npm run build`
- Run E2E test to validate sidebar visibility

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate no type errors
- `cd apps/Client && npm run build` — Run Client build to validate production build succeeds
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_legaldesk_sidebar_visibility.md` to validate the Legal Desk sidebar items are visible and navigable

## Notes
- The core issue (missing Legal Desk sidebar items) was resolved by the Wave 6 merge of branches: `feat-issue-151`, `feat-issue-152`, `feat-issue-153`. The sidebar code is correct.
- The user needs to restart their development server (`npm run dev`) to pick up the merged changes.
- The scrollability fix (Step 2) is a preventive measure — with 18+ navigation items across all sections, the sidebar content exceeds typical viewport heights and must be scrollable.
- No new libraries are needed.
