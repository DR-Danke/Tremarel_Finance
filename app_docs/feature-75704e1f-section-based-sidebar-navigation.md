# Section-Based Sidebar Navigation with POCs Group

**ADW ID:** 75704e1f
**Date:** 2026-03-03
**Specification:** specs/issue-100-adw-75704e1f-sdlc_planner-section-based-sidebar-navigation.md

## Overview

Refactored the sidebar navigation from a flat list of menu items to a section-based, collapsible navigation structure. This groups navigation items under labeled sections ("Finance", "POCs") with support for nested subsections (e.g., "POCs > RestaurantOS"), providing the infrastructure needed for future POC modules. Settings remains at the bottom separated by a divider.

## What Was Built

- **NavSection interface** for defining collapsible, labeled navigation groups with optional subsections
- **Section-based sidebar rendering** replacing the flat `navigationItems` array with `navigationSections`
- **Collapsible POCs section** with expand/collapse chevron and `<Collapse>` animation
- **RestaurantOS subsection** placeholder under POCs (empty, ready for issue #85)
- **localStorage persistence** of section collapse states across page refreshes
- **Collapsed sidebar support** (icon-only mode) with hidden headers and divider separators between sections
- **Catch-all route** for `/poc/restaurant-os/*` with a placeholder page wrapped in ProtectedRoute + TRMainLayout
- **E2E test specification** for validating section-based sidebar navigation

## Technical Implementation

### Files Modified

- `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`: Primary refactor — replaced flat `navigationItems` array with `navigationSections: NavSection[]` data structure. Added `NavSection` interface, section collapse state management with localStorage persistence, `renderNavItem` and `renderSection` helper functions, and MUI `Collapse`/`ListSubheader` rendering logic.
- `apps/Client/src/App.tsx`: Added `/poc/restaurant-os/*` catch-all route with a placeholder page inside ProtectedRoute + TRMainLayout.

### New Files

- `.claude/commands/e2e/test_section_based_sidebar_navigation.md`: E2E test specification covering section rendering, collapse/expand, localStorage persistence, icon-only mode, and active item highlighting.

### Key Changes

- **NavSection interface**: Supports `label`, `collapsible` (default true), `defaultOpen` (default true), `items: NavItem[]`, and optional `subsections: NavSection[]` for nesting.
- **Section state persistence**: Uses `sidebarSectionState` localStorage key. Initial state is derived from each section's `defaultOpen` value. State updates are persisted on every toggle. Graceful fallback if localStorage is unavailable or corrupted.
- **Collapsed sidebar mode**: When the drawer is collapsed (icon-only), section headers are hidden entirely. Dividers separate sections. All nav items render as icons regardless of section collapse state.
- **Subsection rendering**: Subsection labels render as small uppercase captions with left indentation (`pl: 4`). Subsection items receive additional left padding via `indentLevel` parameter.
- **Finance section is non-collapsible** by design (`collapsible: false`). POCs section defaults to collapsed (`defaultOpen: false`).

## How to Use

1. All existing Finance navigation items (Dashboard, Transactions, Recurring, Categories, Budgets, Prospects, Reports) appear under a "Finance" section header.
2. Below Finance, a "POCs" section with a collapsible header groups future proof-of-concept modules.
3. Click the POCs section header (or its chevron icon) to expand/collapse the section.
4. "RestaurantOS" appears as a subsection label under POCs (currently empty — routes will be added by issue #85).
5. Settings remains at the bottom of the sidebar, separated by a divider.
6. In collapsed sidebar mode (icon-only), section headers are hidden and dividers separate the groups.

### Adding a New POC Module

To add a new POC module, update `navigationSections` in `TRCollapsibleSidebar.tsx`:

```typescript
{
  label: 'POCs',
  collapsible: true,
  defaultOpen: false,
  items: [],
  subsections: [
    { label: 'RestaurantOS', items: [/* ... */] },
    { label: 'NewModule', items: [
      { label: 'Page Name', path: '/poc/new-module/page', icon: <SomeIcon /> },
    ]},
  ],
}
```

## Configuration

- **localStorage key**: `sidebarSectionState` — stores a JSON object mapping section labels to boolean open/closed state.
- **Section collapse defaults**: Set via `defaultOpen` property on each `NavSection`. Finance is non-collapsible; POCs defaults to collapsed.

## Testing

- Run `cd apps/Client && npx tsc --noEmit` for TypeScript validation
- Run `cd apps/Client && npm run build` for production build
- Run `cd apps/Client && npm run lint` for lint checks
- Execute the E2E test: `.claude/commands/e2e/test_section_based_sidebar_navigation.md`

## Notes

- This is a **frontend-only** change. No backend modifications.
- The `NavSection` interface supports arbitrary nesting via `subsections`, but currently only one level is used (POCs > RestaurantOS).
- No new npm dependencies — all components (`Collapse`, `ListSubheader`, `ExpandLess`, `ExpandMore`) come from MUI.
- The existing E2E test `test_main_layout_sidebar.md` should still pass since Finance navigation items remain unchanged.
- Future POC modules should follow the same pattern: add a subsection under POCs and a catch-all route in App.tsx.
