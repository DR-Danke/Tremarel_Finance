# Legal Desk Routes & Sidebar Navigation

**ADW ID:** 83119edc
**Date:** 2026-03-04
**Specification:** specs/issue-153-adw-83119edc-sdlc_planner-ld-routes-sidebar-navigation.md

## Overview

Registers all 7 Legal Desk routes in `App.tsx` under `/poc/legal-desk/*` and adds 5 navigation items to the collapsible sidebar under a new "Legal Desk" subsection within the existing "POCs" section. This is the final wiring step (Wave 6, Issue LD-016) that makes the Legal Desk POC accessible through the application's navigation system.

## What Was Built

- 7 Legal Desk page components in `apps/Client/src/pages/legaldesk/`
- 8 route registrations in `App.tsx` (7 pages + 1 redirect)
- "Legal Desk" sidebar subsection with 5 navigation items in `TRCollapsibleSidebar.tsx`
- E2E test specification for route and navigation validation
- Minor backend lint fixes in `legaldesk_routes.py`

## Technical Implementation

### Files Modified

- `apps/Client/src/App.tsx`: Added 7 Legal Desk page imports and 8 `<Route>` elements (dashboard, cases, cases/new, cases/:id, specialists, clients, analytics, plus redirect from `/poc/legal-desk` to `/poc/legal-desk/dashboard`)
- `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`: Added 5 MUI icon imports (Gavel, BusinessCenter, PersonSearch, Groups, Analytics) and a "Legal Desk" subsection to `pocSection.subsections`
- `apps/Client/src/pages/legaldesk/LegalDeskDashboardPage.tsx`: Dashboard page with 4 stat cards (total cases, active cases, specialists, clients) using `useLegaldeskDashboard` hook
- `apps/Client/src/pages/legaldesk/LegalDeskCasesPage.tsx`: Cases list with table display (case number, title, status chip, priority) using `useLegaldeskCases` hook
- `apps/Client/src/pages/legaldesk/LegalDeskCaseDetailPage.tsx`: Case detail view with status chip and description using `useLegaldeskCaseDetail` hook and URL param `:id`
- `apps/Client/src/pages/legaldesk/LegalDeskSpecialistsPage.tsx`: Specialists table (name, email, experience, score) using `useLegaldeskSpecialists` hook
- `apps/Client/src/pages/legaldesk/LegalDeskClientsPage.tsx`: Clients table (name, type chip, email, country) using `useLegaldeskClients` hook
- `apps/Client/src/pages/legaldesk/LegalDeskNewCasePage.tsx`: Placeholder page for new case creation
- `apps/Client/src/pages/legaldesk/LegalDeskAnalyticsPage.tsx`: Placeholder page for analytics
- `apps/Server/src/adapter/rest/legaldesk_routes.py`: Removed unused `DeliverableStatus` import, fixed f-string lint warnings
- `.claude/commands/e2e/test_legaldesk_routes_sidebar_navigation.md`: E2E test specification

### Key Changes

- All routes are wrapped in `ProtectedRoute` + `TRMainLayout` following the established pattern
- Route ordering places `/poc/legal-desk/cases/new` before `/poc/legal-desk/cases/:id` so the static path matches first
- Pages with available hooks (Dashboard, Cases, CaseDetail, Specialists, Clients) wire up loading/error/data states with `CircularProgress` and `Alert` components
- Pages without hooks (NewCase, Analytics) render placeholder content
- The sidebar "Legal Desk" subsection is the second entry in `pocSection.subsections` (after RestaurantOS), using the existing section rendering logic without any changes to `renderNavItem` or `renderSection`

## How to Use

1. Log in to the application
2. In the collapsible sidebar, expand the "POCs" section
3. The "Legal Desk" subsection appears below "RestaurantOS" with 5 items: Dashboard, Cases, Specialists, Clients, Analytics
4. Click any item to navigate to the corresponding Legal Desk page
5. Navigate directly to `/poc/legal-desk` to be redirected to the dashboard
6. Navigate to `/poc/legal-desk/cases/:id` to view a specific case detail

### Routes

| Path | Page | Description |
|------|------|-------------|
| `/poc/legal-desk` | Redirect | Redirects to dashboard |
| `/poc/legal-desk/dashboard` | LegalDeskDashboardPage | Overview with stat cards |
| `/poc/legal-desk/cases` | LegalDeskCasesPage | Case list with table |
| `/poc/legal-desk/cases/new` | LegalDeskNewCasePage | New case form (placeholder) |
| `/poc/legal-desk/cases/:id` | LegalDeskCaseDetailPage | Case detail view |
| `/poc/legal-desk/specialists` | LegalDeskSpecialistsPage | Specialist list |
| `/poc/legal-desk/clients` | LegalDeskClientsPage | Client list |
| `/poc/legal-desk/analytics` | LegalDeskAnalyticsPage | Analytics (placeholder) |

### Sidebar Navigation Items

| Label | Path | Icon |
|-------|------|------|
| Dashboard | `/poc/legal-desk/dashboard` | GavelIcon |
| Cases | `/poc/legal-desk/cases` | BusinessCenterIcon |
| Specialists | `/poc/legal-desk/specialists` | PersonSearchIcon |
| Clients | `/poc/legal-desk/clients` | GroupsIcon |
| Analytics | `/poc/legal-desk/analytics` | AnalyticsIcon |

## Configuration

No additional configuration required. All MUI icons used are part of the existing `@mui/icons-material` package. Pages consume hooks and services from the Legal Desk data layer (implemented in prior waves).

## Testing

- **TypeScript**: `cd apps/Client && npx tsc --noEmit`
- **Lint**: `cd apps/Client && npm run lint`
- **Build**: `cd apps/Client && npm run build`
- **E2E**: Run `/test_e2e` then `/e2e:test_legaldesk_routes_sidebar_navigation`

## Notes

- Pages are functional but minimal — they wire up available hooks for loading/error/data display. When full page components are delivered (LD-015), they can replace these files.
- No lazy loading is used, following the existing codebase pattern of static imports.
- The `buildNavigationSections` no-entities branch only shows `subsections[0]` (RestaurantOS). Users without entities won't see Legal Desk in the sidebar. This is acceptable since Legal Desk is entity-independent and entity-less users are an edge case.
