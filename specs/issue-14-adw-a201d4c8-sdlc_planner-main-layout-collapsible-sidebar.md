# Feature: Main Layout with Collapsible Sidebar

## Metadata
issue_number: `14`
adw_id: `a201d4c8`
issue_json: `{"number":14,"title":"[FinanceTracker] Wave 3: Main Layout with Collapsible Sidebar","body":"..."}`

## Feature Description
Build the main application shell with a collapsible sidebar navigation and top navbar for the Finance Tracker application. The sidebar provides navigation to all major application sections (Dashboard, Transactions, Categories, Budgets, Reports, Settings) and includes an entity switcher to toggle between Family and Startup contexts. The layout should be responsive, with the sidebar collapsing to icons on smaller screens.

## User Story
As an authenticated Finance Tracker user
I want to have a consistent navigation layout with a collapsible sidebar
So that I can easily navigate between different sections of the application and switch between my Family and Startup financial entities

## Problem Statement
The current application lacks a consistent navigation structure. Each page is standalone without proper navigation between sections. Users need a way to navigate to different features (Dashboard, Transactions, Categories, Budgets, Reports, Settings) and switch between their financial entities (Family/Startup) from any page in the application.

## Solution Statement
Implement a main layout component (`TRMainLayout`) that wraps all authenticated pages, containing:
1. A collapsible sidebar (`TRCollapsibleSidebar`) with navigation links and entity switcher
2. A top navbar (`TRTopNavbar`) with application branding and user actions
3. A main content area that renders the current page
4. EntityContext for managing the current entity selection across the application

The layout uses Material-UI's Drawer component for the sidebar with responsive breakpoints to automatically collapse on smaller screens.

## Relevant Files
Use these files to implement the feature:

- `apps/Client/src/main.tsx` - Entry point where EntityProvider will be added alongside AuthProvider
- `apps/Client/src/App.tsx` - Route definitions need to wrap protected routes with TRMainLayout
- `apps/Client/src/types/index.ts` - Contains Entity interface already defined
- `apps/Client/src/contexts/AuthContext.tsx` - Reference for context pattern implementation
- `apps/Client/src/contexts/authContextDef.ts` - Reference for context definition pattern
- `apps/Client/src/hooks/useAuth.ts` - Reference for custom hook pattern
- `apps/Client/src/pages/DashboardPage.tsx` - First page to integrate with new layout
- `apps/Client/src/theme/index.ts` - Theme values to use for consistent styling
- `app_docs/feature-f6f89b86-frontend-jwt-auth-context.md` - Auth context documentation for pattern reference
- `.claude/commands/test_e2e.md` - E2E test runner documentation
- `.claude/commands/e2e/test_auth_login.md` - Reference E2E test format

### New Files
- `apps/Client/src/contexts/EntityContext.tsx` - EntityProvider component with state management
- `apps/Client/src/contexts/entityContextDef.ts` - EntityContext and EntityContextType definitions
- `apps/Client/src/hooks/useEntity.ts` - Custom hook for accessing EntityContext
- `apps/Client/src/components/layout/TRMainLayout.tsx` - Main layout wrapper component
- `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx` - Collapsible sidebar with navigation
- `apps/Client/src/components/layout/TRTopNavbar.tsx` - Top navigation bar component
- `apps/Client/src/components/layout/index.ts` - Barrel export for layout components
- `.claude/commands/e2e/test_main_layout_sidebar.md` - E2E test for layout functionality

## Implementation Plan
### Phase 1: Foundation
Set up the EntityContext for managing entity selection state across the application. This context will track which entity (Family or Startup) the user is currently viewing and provide a method to switch between entities.

### Phase 2: Core Implementation
Build the layout components following Material-UI patterns:
1. `TRCollapsibleSidebar` - A responsive drawer that shows full navigation when expanded and icons only when collapsed
2. `TRTopNavbar` - A fixed app bar with menu toggle, title, and user actions
3. `TRMainLayout` - The container that composes the sidebar, navbar, and content area

### Phase 3: Integration
Integrate the layout with the routing system so all authenticated pages render within the layout. Update App.tsx to wrap protected routes with TRMainLayout and add placeholder routes for future pages.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Task 1: Create E2E Test File
- Create `.claude/commands/e2e/test_main_layout_sidebar.md` following the pattern from `test_auth_login.md`
- Define test steps to verify:
  - Layout renders with sidebar and navbar after login
  - Navigation links are visible and clickable
  - Sidebar toggle button collapses/expands sidebar
  - Entity switcher displays and allows switching entities
  - Navigation links change route correctly

### Task 2: Create EntityContext Definition
- Create `apps/Client/src/contexts/entityContextDef.ts`
- Define `EntityContextType` interface with:
  - `currentEntity: Entity | null`
  - `entities: Entity[]`
  - `switchEntity: (entityId: string) => void`
  - `isLoading: boolean`
- Create and export the `EntityContext` using `createContext<EntityContextType | null>(null)`

### Task 3: Create EntityContext Provider
- Create `apps/Client/src/contexts/EntityContext.tsx`
- Implement `EntityProvider` component:
  - State for `currentEntity`, `entities`, and `isLoading`
  - For now, use mock entities (Family and Startup) since backend entity endpoints don't exist yet
  - Persist selected entity ID in localStorage
  - Add console logging per CLAUDE.md standards
- Export `EntityProvider` component

### Task 4: Create useEntity Hook
- Create `apps/Client/src/hooks/useEntity.ts`
- Implement hook that:
  - Gets context value using `useContext(EntityContext)`
  - Throws error if used outside `EntityProvider`
  - Returns the context value

### Task 5: Create TRTopNavbar Component
- Create `apps/Client/src/components/layout/TRTopNavbar.tsx`
- Implement top navigation bar with:
  - Menu toggle button (hamburger icon) for sidebar
  - Application title "Finance Tracker"
  - User info display (name/email from useAuth)
  - Logout button
- Use Material-UI AppBar, Toolbar, IconButton, Typography components
- Accept `onMenuToggle: () => void` and `isSidebarOpen: boolean` props

### Task 6: Create TRCollapsibleSidebar Component
- Create `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`
- Implement collapsible sidebar with:
  - Navigation links with icons: Dashboard, Transactions, Categories, Budgets, Reports, Settings
  - Entity switcher section with Select dropdown
  - Drawer component with responsive width (240px expanded, 56px collapsed)
  - Icons: DashboardIcon, AccountBalanceWalletIcon, CategoryIcon, SavingsIcon, AssessmentIcon, SettingsIcon
- Accept props: `open: boolean`, `onToggle: () => void`
- Use React Router's `NavLink` for active state styling

### Task 7: Create TRMainLayout Component
- Create `apps/Client/src/components/layout/TRMainLayout.tsx`
- Implement layout container with:
  - State for sidebar open/collapsed
  - TRTopNavbar at the top
  - TRCollapsibleSidebar on the left
  - Main content area that renders children
  - Responsive behavior: auto-collapse sidebar below 'md' breakpoint
- Use Box component for layout structure
- Add smooth transition animations for sidebar

### Task 8: Create Layout Barrel Export
- Create `apps/Client/src/components/layout/index.ts`
- Export all layout components:
  - TRMainLayout
  - TRCollapsibleSidebar
  - TRTopNavbar

### Task 9: Add EntityProvider to App Entry Point
- Update `apps/Client/src/main.tsx`
- Wrap App with `EntityProvider` inside `AuthProvider`
- Add logging for EntityProvider initialization

### Task 10: Update App.tsx with Layout Integration
- Update `apps/Client/src/App.tsx`
- Import TRMainLayout from `@/components/layout`
- Wrap protected routes with TRMainLayout
- Add placeholder routes for: /transactions, /categories, /budgets, /reports, /settings
- Create simple placeholder page components for each route (can be inline)

### Task 11: Update DashboardPage
- Update `apps/Client/src/pages/DashboardPage.tsx`
- Remove Container wrapper (layout handles this)
- Remove logout button (moved to TRTopNavbar)
- Show current entity name in the dashboard header

### Task 12: Run Validation Commands
- Execute all validation commands to ensure feature works correctly with zero regressions

## Testing Strategy
### Unit Tests
- EntityContext: Test entity state management, switching, and persistence
- useEntity hook: Test it throws when used outside provider
- Layout components: Test rendering, prop handling, and state changes

### Edge Cases
- Sidebar state persists across page refreshes
- Entity selection persists in localStorage
- Layout renders correctly with no entities
- Navigation highlights correct active route
- Responsive breakpoint transitions work smoothly
- User without entities sees appropriate message

## Acceptance Criteria
- Main layout with collapsible sidebar renders on all authenticated pages
- Sidebar shows navigation links: Dashboard, Transactions, Categories, Budgets, Reports, Settings
- Sidebar toggle button expands/collapses the sidebar
- Collapsed sidebar shows only icons
- Entity switcher allows selecting between Family and Startup
- Selected entity persists across page refreshes
- Navigation links route to correct pages
- Active navigation link is visually highlighted
- Top navbar shows application title and user info
- Logout button in navbar works correctly
- Layout is responsive and sidebar auto-collapses on small screens
- All existing authentication functionality continues to work

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_main_layout_sidebar.md` to validate the layout functionality.

- `cd apps/Client && npm run tsc` - Run Client type check to validate no TypeScript errors
- `cd apps/Client && npm run build` - Run Client build to validate the feature compiles correctly
- `cd apps/Client && npm run lint` - Run linting to ensure code quality

## Notes
- This feature uses mock entities since Wave 3 runs in parallel with Entity Management (FT-007). Once entity endpoints exist, EntityContext should fetch real entities from the API.
- The sidebar drawer width constants (240px expanded, 56px collapsed) align with Material-UI design guidelines.
- Navigation routes for Transactions, Categories, Budgets, Reports, and Settings create placeholder pages. These will be implemented in subsequent issues.
- Consider adding keyboard shortcuts for sidebar toggle (e.g., Ctrl+B) in a future enhancement.
- The entity switcher uses a simple Select component. Consider upgrading to a more elaborate entity card/selector in the future.
