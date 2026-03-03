# Feature: Section-Based Sidebar Navigation with POCs Group

## Metadata
issue_number: `100`
adw_id: `75704e1f`
issue_json: ``

## Feature Description
Refactor the sidebar navigation from a flat list of menu items to a section-based, collapsible navigation structure. This enables grouping of navigation items under labeled sections (e.g., "Finance", "POCs") with support for nested subsections (e.g., "POCs > RestaurantOS"). This is a prerequisite infrastructure change (Wave 0) for the RestaurantOS module and all future POC modules. The Finance Tracker's existing navigation items will be grouped under a "Finance" section header, a new collapsible "POCs" section will house the RestaurantOS subsection (initially empty), and Settings will remain at the bottom separated by a divider.

## User Story
As an authenticated Finance Tracker user
I want to see navigation items organized into collapsible sections in the sidebar
So that I can easily navigate between Finance features and future POC modules (like RestaurantOS) without clutter

## Problem Statement
The current sidebar renders all navigation items in a flat list. As the application grows to include POC modules (RestaurantOS, and future modules), the flat list becomes unmanageable. There is no way to visually group related navigation items or collapse sections the user doesn't need, making the sidebar harder to navigate as more features are added.

## Solution Statement
Refactor TRCollapsibleSidebar to support a `NavSection[]` data structure with collapsible headers, nested subsections, and dividers. Existing Finance items are grouped under a non-collapsible "Finance" header, a new collapsible "POCs" section contains a "RestaurantOS" subsection (empty for now), and Settings stays at the bottom. Section collapse state is persisted in localStorage. The collapsed sidebar (icon-only mode) continues to work by hiding section headers and showing only item icons with dividers between sections.

## Relevant Files
Use these files to implement the feature:

- `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx` — **Primary file to modify.** Contains the current flat `NavItem` interface and `navigationItems` array. Must be refactored to support `NavSection` interface with collapsible sections, subsections, and section rendering logic.
- `apps/Client/src/components/layout/TRMainLayout.tsx` — Parent layout component that renders TRCollapsibleSidebar. No changes expected unless props change.
- `apps/Client/src/components/layout/TRTopNavbar.tsx` — Top navbar component. No changes expected.
- `apps/Client/src/components/layout/index.ts` — Barrel exports for layout components. No changes expected.
- `apps/Client/src/App.tsx` — Route definitions. Must add a catch-all route for `/poc/restaurant-os/*` wrapped in ProtectedRoute + TRMainLayout.
- `app_docs/feature-a201d4c8-main-layout-collapsible-sidebar.md` — Documentation for the existing sidebar implementation. Read for context.
- `.claude/commands/test_e2e.md` — E2E test runner instructions. Read to understand how to create E2E test files.
- `.claude/commands/e2e/test_main_layout_sidebar.md` — Existing sidebar E2E test. Read for reference on E2E test structure and sidebar testing patterns.

### New Files
- `.claude/commands/e2e/test_section_based_sidebar_navigation.md` — New E2E test file for section-based sidebar navigation validation.

## Implementation Plan
### Phase 1: Foundation
Update the `NavItem` and add `NavSection` interfaces in TRCollapsibleSidebar. Define the `navigationSections` data structure grouping existing items under "Finance", adding the "POCs" section with "RestaurantOS" subsection, and placing Settings in an unlabeled bottom section.

### Phase 2: Core Implementation
Refactor the sidebar rendering to iterate over `NavSection[]` instead of `NavItem[]`. Implement collapsible section headers using MUI `<Collapse>`, `<ListSubheader>`, and expand/collapse chevron icons. Add localStorage persistence for section collapse states. Handle the collapsed sidebar mode (icon-only) by hiding section headers and showing dividers between sections. Support nested subsections with extra indentation.

### Phase 3: Integration
Add the `/poc/restaurant-os/*` catch-all route in App.tsx. Create the E2E test specification. Validate no visual regression on existing Finance navigation, ensure type safety, and confirm the build passes.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_main_layout_sidebar.md` for reference
- Create `.claude/commands/e2e/test_section_based_sidebar_navigation.md` with test steps that validate:
  - Sidebar renders with "Finance" section header containing all existing nav items
  - "POCs" section appears below Finance with a collapsible header
  - "RestaurantOS" appears as a subsection label under POCs
  - Settings appears at the bottom separated by a divider
  - Clicking the POCs section header collapses/expands the section
  - Section collapse state persists after page refresh (via localStorage)
  - Collapsed sidebar (icon-only mode) still works correctly
  - Existing navigation links still route correctly
  - Active item highlighting works across sections

### Step 2: Update NavItem and Add NavSection Interfaces
- In `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`:
- Keep the existing `NavItem` interface unchanged:
  ```typescript
  interface NavItem {
    label: string
    path: string
    icon: React.ReactNode
  }
  ```
- Add the new `NavSection` interface:
  ```typescript
  interface NavSection {
    label: string
    collapsible?: boolean     // default true
    defaultOpen?: boolean     // default true for top-level, false for POCs
    items: NavItem[]
    subsections?: NavSection[]  // for nesting like POCs > RestaurantOS
  }
  ```

### Step 3: Define navigationSections Data Structure
- Replace the existing `navigationItems: NavItem[]` array with `navigationSections: NavSection[]`:
  ```typescript
  const navigationSections: NavSection[] = [
    {
      label: 'Finance',
      collapsible: false,
      items: [
        { label: 'Dashboard', path: '/dashboard', icon: <DashboardIcon /> },
        { label: 'Transactions', path: '/transactions', icon: <AccountBalanceWalletIcon /> },
        { label: 'Recurring', path: '/recurring', icon: <RepeatIcon /> },
        { label: 'Categories', path: '/categories', icon: <CategoryIcon /> },
        { label: 'Budgets', path: '/budgets', icon: <SavingsIcon /> },
        { label: 'Prospects', path: '/prospects', icon: <PeopleIcon /> },
        { label: 'Reports', path: '/reports', icon: <AssessmentIcon /> },
      ],
    },
    {
      label: 'POCs',
      collapsible: true,
      defaultOpen: false,
      subsections: [
        {
          label: 'RestaurantOS',
          items: [],  // populated by issue #85
        },
      ],
      items: [],
    },
    {
      label: '',  // no header — bottom section
      items: [
        { label: 'Settings', path: '/settings', icon: <SettingsIcon /> },
      ],
    },
  ]
  ```

### Step 4: Implement Section Collapse State with localStorage Persistence
- Add MUI imports: `Collapse`, `ListSubheader` from `@mui/material` and `ExpandLess`, `ExpandMore` from `@mui/icons-material`
- Create a state object to track which sections are open/closed, initialized from localStorage:
  ```typescript
  const SIDEBAR_SECTIONS_KEY = 'sidebarSectionState'

  const getInitialSectionState = (): Record<string, boolean> => {
    const stored = localStorage.getItem(SIDEBAR_SECTIONS_KEY)
    if (stored) {
      return JSON.parse(stored) as Record<string, boolean>
    }
    const initial: Record<string, boolean> = {}
    navigationSections.forEach((section) => {
      if (section.label && section.collapsible !== false) {
        initial[section.label] = section.defaultOpen ?? true
      }
    })
    return initial
  }

  const [sectionState, setSectionState] = useState<Record<string, boolean>>(getInitialSectionState)
  ```
- Create a toggle handler that updates state and persists to localStorage:
  ```typescript
  const handleSectionToggle = (sectionLabel: string) => {
    setSectionState((prev) => {
      const next = { ...prev, [sectionLabel]: !prev[sectionLabel] }
      localStorage.setItem(SIDEBAR_SECTIONS_KEY, JSON.stringify(next))
      return next
    })
  }
  ```

### Step 5: Refactor Sidebar Rendering to Use Sections
- Replace the current `<List>` that maps over `navigationItems` with a new rendering that iterates over `navigationSections`
- For each section:
  - If `section.label` is non-empty and sidebar is expanded (`open` prop is true):
    - Render a `<ListSubheader>` with the section label
    - If `section.collapsible !== false`, add a click handler and expand/collapse chevron icon (`<ExpandLess>` / `<ExpandMore>`)
    - Wrap the section's items in `<Collapse in={sectionState[section.label]} ...>`
  - If `section.label` is empty (bottom section like Settings), render a `<Divider>` before the items
  - If sidebar is collapsed (icon-only mode):
    - Hide section headers entirely
    - Render a `<Divider>` between sections (except for the first section)
    - Show all nav items as icon-only regardless of collapse state
- For subsections within a section:
  - Render subsection label as a smaller, indented subheader (when sidebar is expanded)
  - Subsection items get extra left padding (`pl: 4` or similar)
  - Subsections follow the same collapsible pattern as their parent section
- Render each `NavItem` using the existing `ListItemButton` + `NavLink` pattern (active highlighting, icon, label display)

### Step 6: Add Route Support for POC RestaurantOS
- In `apps/Client/src/App.tsx`:
- Add a catch-all route for `/poc/restaurant-os/*` that renders a placeholder page:
  ```typescript
  <Route
    path="/poc/restaurant-os/*"
    element={
      <ProtectedRoute>
        <TRMainLayout>
          <Box>
            <Typography variant="h4">RestaurantOS</Typography>
            <Typography color="text.secondary">
              RestaurantOS pages coming soon.
            </Typography>
          </Box>
        </TRMainLayout>
      </ProtectedRoute>
    }
  />
  ```
- This placeholder will be replaced by actual routes in issue #85

### Step 7: Validate and Fix TypeScript Errors
- Run `cd apps/Client && npx tsc --noEmit` to check for TypeScript errors
- Ensure no `any` types are used
- Ensure all interfaces are properly typed
- Fix any compilation issues

### Step 8: Run Validation Commands
- Run `cd apps/Client && npx tsc --noEmit` — TypeScript type check
- Run `cd apps/Client && npm run build` — Production build validation
- Run `cd apps/Client && npm run lint` — Lint check
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_section_based_sidebar_navigation.md` to validate the feature E2E

## Testing Strategy
### Unit Tests
- No separate unit test files needed for this refactor since the sidebar is a presentational component best validated via E2E tests
- TypeScript compilation serves as a type-level unit test for interface correctness

### Edge Cases
- Sidebar collapsed mode: section headers must be hidden, all items show as icons with dividers between sections
- Empty subsection (RestaurantOS has no items): should render the subsection label but no nav items beneath it
- localStorage corruption: `getInitialSectionState` should handle invalid JSON gracefully by falling back to defaults
- Multiple sections collapsed simultaneously: each section's state is independent
- Browser with localStorage disabled: component should work with in-memory state only (no crash)
- Navigation to a route within a collapsed section: the section should remain as-is (user controls collapse state)

## Acceptance Criteria
- [ ] Sidebar renders existing Finance items unchanged (no visual regression)
- [ ] "Finance" section header appears above existing navigation items
- [ ] "POCs" section appears below Finance items with a collapsible header and chevron icon
- [ ] "RestaurantOS" appears as a subsection label under POCs (empty for now)
- [ ] Settings remains at the bottom, separated by a divider
- [ ] Clicking the POCs section header toggles collapse/expand
- [ ] Collapsed sidebar still works correctly (icons only, dividers between sections)
- [ ] Section collapse state persists in localStorage across page refreshes
- [ ] Active item highlighting works across all sections
- [ ] `/poc/restaurant-os/*` catch-all route is defined and wrapped in ProtectedRoute + TRMainLayout
- [ ] No TypeScript errors, no `any` types
- [ ] Production build succeeds with zero errors
- [ ] E2E test validates sidebar section navigation end-to-end

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate no TypeScript errors
- `cd apps/Client && npm run build` — Run Client production build to validate no build errors
- `cd apps/Client && npm run lint` — Run Client lint check
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_section_based_sidebar_navigation.md` to validate this functionality works E2E

## Notes
- This is a **frontend-only** change. No backend modifications are needed.
- The POCs > RestaurantOS subsection will have zero nav items until issue #85 populates it with actual routes.
- Future POC modules will follow the same pattern: add a new subsection under the "POCs" section with their nav items.
- The `NavSection` interface supports arbitrary nesting via `subsections`, but for now only one level of nesting is used (POCs > RestaurantOS).
- No new npm dependencies are required — MUI already provides `Collapse`, `ListSubheader`, `ExpandLess`, `ExpandMore`.
- The existing E2E test `test_main_layout_sidebar.md` should still pass since Finance navigation items remain unchanged.
