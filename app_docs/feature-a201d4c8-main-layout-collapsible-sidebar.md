# Main Layout with Collapsible Sidebar

**ADW ID:** a201d4c8
**Date:** 2026-01-13
**Specification:** specs/issue-14-adw-a201d4c8-sdlc_planner-main-layout-collapsible-sidebar.md

## Overview

This feature implements the main application shell with a collapsible sidebar navigation and top navbar for the Finance Tracker application. The layout provides consistent navigation across all authenticated pages, including an entity switcher to toggle between Family and Startup contexts with responsive behavior on different screen sizes.

## What Was Built

- **TRMainLayout** - Main layout wrapper component composing navbar, sidebar, and content area
- **TRCollapsibleSidebar** - Responsive drawer with navigation links and entity switcher
- **TRTopNavbar** - Fixed app bar with menu toggle, title, and user actions
- **EntityContext** - React context for managing entity selection across the application
- **useEntity hook** - Custom hook for accessing entity context
- Placeholder routes for Transactions, Categories, Budgets, Reports, and Settings pages

## Technical Implementation

### Files Modified

- `apps/Client/src/main.tsx`: Added EntityProvider wrapping the App component
- `apps/Client/src/App.tsx`: Integrated TRMainLayout with protected routes, added placeholder pages
- `apps/Client/src/pages/DashboardPage.tsx`: Removed Container wrapper and logout button, added entity name display

### Files Created

- `apps/Client/src/components/layout/TRMainLayout.tsx`: Main layout container (68 lines)
- `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`: Collapsible sidebar (187 lines)
- `apps/Client/src/components/layout/TRTopNavbar.tsx`: Top navigation bar (93 lines)
- `apps/Client/src/components/layout/index.ts`: Barrel export for layout components
- `apps/Client/src/contexts/EntityContext.tsx`: EntityProvider with state management (97 lines)
- `apps/Client/src/contexts/entityContextDef.ts`: EntityContext type definitions
- `apps/Client/src/hooks/useEntity.ts`: Custom hook for EntityContext access
- `.claude/commands/e2e/test_main_layout_sidebar.md`: E2E test specification

### Key Changes

- **Sidebar with responsive width**: Expanded 240px, collapsed 56px, auto-collapse on mobile
- **Navigation links**: Dashboard, Transactions, Categories, Budgets, Reports, Settings with MUI icons
- **Entity switcher**: Dropdown in sidebar to switch between Family and Startup contexts
- **Active route highlighting**: Visual feedback for current navigation item
- **Entity persistence**: Selected entity ID stored in localStorage for session persistence
- **Mock entities**: Using hardcoded Family/Startup entities until backend entity endpoints exist

## How to Use

1. Log in to the application with valid credentials
2. The main layout appears with sidebar and top navbar
3. Use the hamburger menu icon to toggle sidebar expand/collapse
4. Navigate between sections using sidebar links (Dashboard, Transactions, etc.)
5. Switch between entities (Family/Startup) using the dropdown in the sidebar
6. Click Logout in the top navbar to sign out

## Configuration

### Sidebar Width Constants

```typescript
export const DRAWER_WIDTH_EXPANDED = 240  // Full sidebar width
export const DRAWER_WIDTH_COLLAPSED = 56  // Icon-only width
```

### Entity Storage Key

```typescript
const SELECTED_ENTITY_KEY = 'selectedEntityId'  // localStorage key
```

### Mock Entities

Currently using mock entities with IDs `entity-family-001` and `entity-startup-001`. These will be replaced with API-fetched entities once backend entity endpoints are implemented.

## Testing

Run the E2E test to validate layout functionality:

```bash
# Read and execute the E2E test
# See .claude/commands/e2e/test_main_layout_sidebar.md
```

Validation commands:
```bash
cd apps/Client && npm run tsc    # Type check
cd apps/Client && npm run build  # Build validation
cd apps/Client && npm run lint   # Lint check
```

## Notes

- Mock entities are used since this feature runs in parallel with Entity Management backend
- Navigation routes for Transactions, Categories, Budgets, Reports, and Settings are placeholders
- The sidebar automatically collapses below 'md' breakpoint (900px) for mobile responsiveness
- Entity selection persists across page refreshes via localStorage
- All layout components follow the TR prefix naming convention per project standards
