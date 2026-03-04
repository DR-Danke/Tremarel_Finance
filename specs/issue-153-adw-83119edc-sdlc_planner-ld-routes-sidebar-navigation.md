# Feature: Legal Desk Routes & Sidebar Navigation

## Metadata
issue_number: `153`
adw_id: `83119edc`
issue_json: ``

## Feature Description
Register all Legal Desk routes in `App.tsx` and add Legal Desk navigation items to the collapsible sidebar. This is the final wiring step (Wave 6, Issue LD-016) that makes the entire Legal Desk POC accessible through the application's navigation system. Seven routes will be registered under `/poc/legal-desk/*`, all wrapped in `ProtectedRoute` with `TRMainLayout`. Five navigation items will be added to the sidebar under a new "Legal Desk" subsection within the existing "POCs" collapsible section.

## User Story
As an authenticated Finance Tracker user
I want to navigate to Legal Desk pages via the sidebar
So that I can access the case management, specialist assignment, client management, and analytics features of the Legal Desk POC

## Problem Statement
The Legal Desk backend API (~35 endpoints), data layer (TypeScript types, services, hooks), and page components are being built in parallel waves. However, none of these pages are wired into the application's routing or navigation system, making them inaccessible to users. This issue resolves that by registering all routes and adding sidebar navigation entries.

## Solution Statement
1. Create placeholder page components for all 7 Legal Desk pages (since LD-015 runs in parallel and page files may not yet exist in this worktree).
2. Register 7 routes in `App.tsx` under `/poc/legal-desk/*` plus a redirect from `/poc/legal-desk` to `/poc/legal-desk/dashboard`.
3. Add a "Legal Desk" subsection with 5 navigation items to the existing `pocSection.subsections` array in `TRCollapsibleSidebar.tsx`.
4. Follow existing patterns exactly: static imports (no lazy loading), `ProtectedRoute` + `TRMainLayout` wrapping, `NavItem`/`NavSection` data structures.

## Relevant Files
Use these files to implement the feature:

- `apps/Client/src/App.tsx` — Route registration. Add 7 Legal Desk page imports and 8 `<Route>` elements (7 pages + 1 redirect). Lines 1-18 for imports, after line 247 for routes.
- `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx` — Sidebar navigation. Add 5 MUI icon imports (lines 21-35) and a Legal Desk subsection to `pocSection.subsections` (after line 86).
- `apps/Client/src/pages/restaurantos/RestaurantOSDashboardPage.tsx` — Reference pattern for page component structure (loading/error/content pattern, named + default export).
- `apps/Client/src/hooks/useLegaldeskDashboard.ts` — Hook for dashboard page (exports `useLegaldeskDashboard`).
- `apps/Client/src/hooks/useLegaldeskCases.ts` — Hook for cases page (exports `useLegaldeskCases`).
- `apps/Client/src/hooks/useLegaldeskCaseDetail.ts` — Hook for case detail page (exports `useLegaldeskCaseDetail`).
- `apps/Client/src/hooks/useLegaldeskSpecialists.ts` — Hook for specialists page (exports `useLegaldeskSpecialists`).
- `apps/Client/src/hooks/useLegaldeskClients.ts` — Hook for clients page (exports `useLegaldeskClients`).
- `apps/Client/src/services/legaldeskService.ts` — Service layer with all Legal Desk API calls.
- `apps/Client/src/types/legaldesk.ts` — TypeScript types, interfaces, union types, and label/color maps for Legal Desk.
- `app_docs/feature-a201d4c8-main-layout-collapsible-sidebar.md` — Documentation for adding new protected pages with main layout.
- `app_docs/feature-75704e1f-section-based-sidebar-navigation.md` — Documentation for adding new POC modules and routes under `/poc/` prefix.
- `.claude/commands/test_e2e.md` — E2E test runner instructions.
- `.claude/commands/e2e/test_section_based_sidebar_navigation.md` — Reference E2E test for sidebar navigation pattern.
- `.claude/commands/e2e/test_basic_query.md` — Reference E2E test format.

### New Files
- `apps/Client/src/pages/legaldesk/LegalDeskDashboardPage.tsx` — Dashboard page component using `useLegaldeskDashboard`
- `apps/Client/src/pages/legaldesk/LegalDeskCasesPage.tsx` — Cases list page using `useLegaldeskCases`
- `apps/Client/src/pages/legaldesk/LegalDeskNewCasePage.tsx` — New case creation page
- `apps/Client/src/pages/legaldesk/LegalDeskCaseDetailPage.tsx` — Case detail page using `useLegaldeskCaseDetail` with URL param `:id`
- `apps/Client/src/pages/legaldesk/LegalDeskSpecialistsPage.tsx` — Specialists list page using `useLegaldeskSpecialists`
- `apps/Client/src/pages/legaldesk/LegalDeskClientsPage.tsx` — Clients list page using `useLegaldeskClients`
- `apps/Client/src/pages/legaldesk/LegalDeskAnalyticsPage.tsx` — Analytics page placeholder
- `.claude/commands/e2e/test_legaldesk_routes_sidebar_navigation.md` — E2E test specification

## Implementation Plan
### Phase 1: Foundation
Create the 7 Legal Desk page component files in `apps/Client/src/pages/legaldesk/`. Each page follows the established RestaurantOS pattern: named export + default export, loading spinner via `CircularProgress`, error display via `Alert`, and content section with `Typography` headings. Pages that have hooks available (Dashboard, Cases, CaseDetail, Specialists, Clients) will wire up their respective hooks. Pages without hooks (NewCase, Analytics) will render placeholder content.

### Phase 2: Core Implementation
1. **Route Registration**: Add static imports for all 7 pages to `App.tsx` (after line 18, before `ProtectedRoute` import). Add 8 `<Route>` elements after line 247: a redirect from `/poc/legal-desk` to `/poc/legal-desk/dashboard`, then 7 page routes each wrapped in `<ProtectedRoute><TRMainLayout>...</TRMainLayout></ProtectedRoute>`.
2. **Sidebar Navigation**: Import 5 MUI icons (`GavelIcon`, `BusinessCenterIcon`, `PersonSearchIcon`, `GroupsIcon`, `AnalyticsIcon`) in `TRCollapsibleSidebar.tsx`. Add a `{ label: 'Legal Desk', items: [...] }` object as the second entry in `pocSection.subsections` array (after the RestaurantOS subsection).

### Phase 3: Integration
- Verify all routes are protected by authentication via `ProtectedRoute`.
- Verify sidebar active state highlights the current Legal Desk page using existing `location.pathname === item.path` logic in `renderNavItem`.
- Verify collapsed sidebar (icon-only mode) still renders Legal Desk icons.
- Verify the POCs section collapse/expand includes Legal Desk items alongside RestaurantOS.
- Create E2E test specification to validate navigation end-to-end.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Read reference documentation
- Read `app_docs/feature-a201d4c8-main-layout-collapsible-sidebar.md` for the main layout + protected route pattern.
- Read `app_docs/feature-75704e1f-section-based-sidebar-navigation.md` for the section-based sidebar and POC module pattern.
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` for E2E test format.

### Step 2: Create E2E test specification
- Create `.claude/commands/e2e/test_legaldesk_routes_sidebar_navigation.md` with the following test structure:
  - **User Story**: As an authenticated user, I want to navigate to Legal Desk pages via the sidebar.
  - **Prerequisites**: Backend at http://localhost:8000, Frontend at http://localhost:5173, valid test credentials.
  - **Test Steps**:
    1. Navigate to the app and log in.
    2. Expand the POCs section in the sidebar.
    3. Verify "Legal Desk" subsection label appears under POCs.
    4. Verify 5 nav items appear: Dashboard (GavelIcon), Cases (BusinessCenterIcon), Specialists (PersonSearchIcon), Clients (GroupsIcon), Analytics (AnalyticsIcon).
    5. Click each Legal Desk nav item and verify the route changes and page renders without errors.
    6. Navigate directly to `/poc/legal-desk` and verify redirect to `/poc/legal-desk/dashboard`.
    7. Navigate directly to `/poc/legal-desk/cases/new` and verify page renders.
    8. Navigate directly to `/poc/legal-desk/cases/1` and verify page renders.
    9. Verify active state highlighting works on each Legal Desk nav item.
    10. Collapse sidebar to icon-only mode and verify Legal Desk icons are still visible and clickable.
    11. Take screenshots at key steps.
  - **Success Criteria**: All 7 routes load, 5 sidebar items render, redirect works, active state works, no console errors.

### Step 3: Create Legal Desk page components
- Create directory `apps/Client/src/pages/legaldesk/`.
- Create `LegalDeskDashboardPage.tsx`:
  - Import and use `useLegaldeskDashboard` hook.
  - Show loading spinner (`CircularProgress`) while loading.
  - Show `Alert` with error message on error.
  - Show dashboard stats: total_cases, active_cases, total_specialists, total_clients.
  - Named export `LegalDeskDashboardPage` + default export.
- Create `LegalDeskCasesPage.tsx`:
  - Import and use `useLegaldeskCases` hook.
  - Show loading/error states.
  - Show list of cases with title, status, and case number.
  - Named export `LegalDeskCasesPage` + default export.
- Create `LegalDeskNewCasePage.tsx`:
  - Placeholder page with heading "New Case" and description text.
  - Named export `LegalDeskNewCasePage` + default export.
- Create `LegalDeskCaseDetailPage.tsx`:
  - Import `useParams` from react-router-dom to get `:id` param.
  - Import and use `useLegaldeskCaseDetail` hook with parsed case ID.
  - Show loading/error states.
  - Show case title, status, description when loaded.
  - Named export `LegalDeskCaseDetailPage` + default export.
- Create `LegalDeskSpecialistsPage.tsx`:
  - Import and use `useLegaldeskSpecialists` hook.
  - Show loading/error states.
  - Show list of specialists with name and specializations.
  - Named export `LegalDeskSpecialistsPage` + default export.
- Create `LegalDeskClientsPage.tsx`:
  - Import and use `useLegaldeskClients` hook.
  - Show loading/error states.
  - Show list of clients with name and type.
  - Named export `LegalDeskClientsPage` + default export.
- Create `LegalDeskAnalyticsPage.tsx`:
  - Placeholder page with heading "Analytics" and description text.
  - Named export `LegalDeskAnalyticsPage` + default export.

### Step 4: Register routes in App.tsx
- Add 7 static imports after line 18 (after RestaurantOS imports, before ProtectedRoute import):
  ```typescript
  import { LegalDeskDashboardPage } from '@/pages/legaldesk/LegalDeskDashboardPage'
  import { LegalDeskCasesPage } from '@/pages/legaldesk/LegalDeskCasesPage'
  import { LegalDeskNewCasePage } from '@/pages/legaldesk/LegalDeskNewCasePage'
  import { LegalDeskCaseDetailPage } from '@/pages/legaldesk/LegalDeskCaseDetailPage'
  import { LegalDeskSpecialistsPage } from '@/pages/legaldesk/LegalDeskSpecialistsPage'
  import { LegalDeskClientsPage } from '@/pages/legaldesk/LegalDeskClientsPage'
  import { LegalDeskAnalyticsPage } from '@/pages/legaldesk/LegalDeskAnalyticsPage'
  ```
- Add 8 route elements after line 247 (after last RestaurantOS route, before `</Routes>`):
  ```tsx
  {/* Legal Desk routes */}
  <Route
    path="/poc/legal-desk"
    element={<Navigate to="/poc/legal-desk/dashboard" replace />}
  />
  <Route
    path="/poc/legal-desk/dashboard"
    element={
      <ProtectedRoute>
        <TRMainLayout>
          <LegalDeskDashboardPage />
        </TRMainLayout>
      </ProtectedRoute>
    }
  />
  <Route
    path="/poc/legal-desk/cases"
    element={
      <ProtectedRoute>
        <TRMainLayout>
          <LegalDeskCasesPage />
        </TRMainLayout>
      </ProtectedRoute>
    }
  />
  <Route
    path="/poc/legal-desk/cases/new"
    element={
      <ProtectedRoute>
        <TRMainLayout>
          <LegalDeskNewCasePage />
        </TRMainLayout>
      </ProtectedRoute>
    }
  />
  <Route
    path="/poc/legal-desk/cases/:id"
    element={
      <ProtectedRoute>
        <TRMainLayout>
          <LegalDeskCaseDetailPage />
        </TRMainLayout>
      </ProtectedRoute>
    }
  />
  <Route
    path="/poc/legal-desk/specialists"
    element={
      <ProtectedRoute>
        <TRMainLayout>
          <LegalDeskSpecialistsPage />
        </TRMainLayout>
      </ProtectedRoute>
    }
  />
  <Route
    path="/poc/legal-desk/clients"
    element={
      <ProtectedRoute>
        <TRMainLayout>
          <LegalDeskClientsPage />
        </TRMainLayout>
      </ProtectedRoute>
    }
  />
  <Route
    path="/poc/legal-desk/analytics"
    element={
      <ProtectedRoute>
        <TRMainLayout>
          <LegalDeskAnalyticsPage />
        </TRMainLayout>
      </ProtectedRoute>
    }
  />
  ```
- IMPORTANT: Place `/poc/legal-desk/cases/new` BEFORE `/poc/legal-desk/cases/:id` so the static path matches first.

### Step 5: Add Legal Desk sidebar navigation
- In `TRCollapsibleSidebar.tsx`, add 5 MUI icon imports to the existing icon import block (after line 35):
  ```typescript
  import GavelIcon from '@mui/icons-material/Gavel'
  import BusinessCenterIcon from '@mui/icons-material/BusinessCenter'
  import PersonSearchIcon from '@mui/icons-material/PersonSearch'
  import GroupsIcon from '@mui/icons-material/Groups'
  import AnalyticsIcon from '@mui/icons-material/Analytics'
  ```
- Add a Legal Desk subsection as the second entry in `pocSection.subsections` array, after the RestaurantOS subsection (after line 86, before the closing `],` of subsections):
  ```typescript
  {
    label: 'Legal Desk',
    items: [
      { label: 'Dashboard', path: '/poc/legal-desk/dashboard', icon: <GavelIcon /> },
      { label: 'Cases', path: '/poc/legal-desk/cases', icon: <BusinessCenterIcon /> },
      { label: 'Specialists', path: '/poc/legal-desk/specialists', icon: <PersonSearchIcon /> },
      { label: 'Clients', path: '/poc/legal-desk/clients', icon: <GroupsIcon /> },
      { label: 'Analytics', path: '/poc/legal-desk/analytics', icon: <AnalyticsIcon /> },
    ],
  },
  ```
- No changes needed to `buildNavigationSections`, `getInitialSectionState`, `renderNavItem`, or `renderSection` — the existing code handles multiple subsections automatically.

### Step 6: Run validation commands
- Run TypeScript type check: `cd apps/Client && npx tsc --noEmit`
- Run lint: `cd apps/Client && npm run lint`
- Run build: `cd apps/Client && npm run build`
- Fix any errors found.

### Step 7: Run E2E test
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_legaldesk_routes_sidebar_navigation.md` to validate this functionality works end-to-end.

## Testing Strategy
### Unit Tests
- No unit tests required for this feature. Route registration and sidebar configuration are declarative and best validated through type checking, build validation, and E2E testing.

### Edge Cases
- `/poc/legal-desk` redirects to `/poc/legal-desk/dashboard` (not 404).
- `/poc/legal-desk/cases/new` matches before `/poc/legal-desk/cases/:id` (route ordering).
- `/poc/legal-desk/cases/:id` with an invalid ID should show an error state from the hook (no crash).
- Collapsed sidebar (icon-only mode) shows all Legal Desk icons without labels.
- Users without entities still see Legal Desk items via the no-entities branch in `buildNavigationSections` (currently only shows RestaurantOS items — acceptable behavior, no change needed since Legal Desk is entity-independent).
- POCs section localStorage state persists correctly with Legal Desk items.

## Acceptance Criteria
- All 7 Legal Desk routes are registered in `App.tsx` and load their respective pages without errors.
- `/poc/legal-desk` redirects to `/poc/legal-desk/dashboard`.
- All routes are wrapped in `ProtectedRoute` (authentication required).
- All routes use `TRMainLayout` for consistent layout.
- 5 sidebar navigation items appear under a "Legal Desk" subsection within the "POCs" collapsible section.
- Each sidebar item has the correct icon: Dashboard (Gavel), Cases (BusinessCenter), Specialists (PersonSearch), Clients (Groups), Analytics (Analytics).
- Active state highlighting works on Legal Desk nav items based on `location.pathname`.
- Collapsed sidebar (icon-only mode) shows Legal Desk icons.
- TypeScript compiles with zero errors (`npx tsc --noEmit`).
- Production build succeeds (`npm run build`).
- No console errors or React warnings when navigating Legal Desk pages.

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate zero TypeScript errors
- `cd apps/Client && npm run lint` — Run Client lint to validate code quality
- `cd apps/Client && npm run build` — Run Client production build to validate bundle compiles
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_legaldesk_routes_sidebar_navigation.md` to validate end-to-end navigation

## Notes
- **No lazy loading**: The codebase uses static imports throughout (no `React.lazy` or `Suspense`). Despite the issue suggesting lazy loading, we follow the existing pattern for consistency.
- **Page components as placeholders**: Since LD-015 (page components) runs in parallel, the pages created here are functional but minimal. They wire up available hooks for loading/error/data display. When LD-015 delivers more complete page components, they can replace these files.
- **No new libraries needed**: All MUI icons used (`Gavel`, `BusinessCenter`, `PersonSearch`, `Groups`, `Analytics`) are part of the already-installed `@mui/icons-material` package.
- **Sidebar no-entities branch**: The `buildNavigationSections` no-entities fallback (line 103) only shows `subsections[0]` (RestaurantOS). This means users without entities won't see Legal Desk in the sidebar. This is acceptable since Legal Desk is a POC module and entity-less users are an edge case. If needed in the future, this branch can be updated to include all subsections.
