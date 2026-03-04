# Legal Desk All Pages (Dashboard, Cases, Specialists, Clients, Analytics)

**ADW ID:** 7febcc45
**Date:** 2026-03-04
**Specification:** specs/issue-152-adw-7febcc45-sdlc_planner-legaldesk-all-pages.md

## Overview

Implements the complete Legal Desk frontend UI — 7 page components, 6 shared UI components, and 3 form components — that wire together the existing service layer (`legaldeskService`), React hooks, and TypeScript types into user-facing pages for end-to-end legal case management. This is the final UI layer of the Legal Desk module, enabling users to manage cases from intake through specialist assignment, pricing negotiation, deliverable tracking, and analytics review.

## What Was Built

### Pages (7)
- **LegalDeskDashboardPage** — Stats cards (active/total cases, specialists, clients) + Recharts pie chart (cases by status) and bar chart (cases by domain)
- **LegalDeskCasesPage** — Filterable case table with 4 filter controls (status, domain, priority, type) and row-click navigation
- **LegalDeskNewCasePage** — Case creation form with client dropdown, redirects to case detail on success
- **LegalDeskCaseDetailPage** — 6-tab interface (Overview, Specialists, Deliverables, Pricing, Messages, Documents) with status transition controls
- **LegalDeskSpecialistsPage** — Card grid with score display, workload indicators, and "Add Specialist" dialog
- **LegalDeskClientsPage** — Table with "Add Client" dialog
- **LegalDeskAnalyticsPage** — Summary stats + domain distribution bar chart with specialist utilization placeholder

### Shared UI Components (6)
- **TRCaseStatusBadge** — MUI Chip displaying case status with color from CASE_STATUS_COLORS
- **TRLegalDomainBadge** — MUI Chip displaying legal domain with color
- **TRCasePriorityBadge** — MUI Chip displaying case priority with color
- **TRSpecialistScoreDisplay** — Score number + LinearProgress bar (score/maxScore)
- **TRDeliverableChecklist** — Deliverable list with checkbox status toggles
- **TRPricingTimeline** — Chronological pricing negotiation history display

### Form Components (3)
- **TRLegalCaseForm** — react-hook-form case creation form (title, client, domain, complexity, priority, budget, deadline)
- **TRLegalSpecialistForm** — react-hook-form specialist creation form (name, email, experience, hourly rate)
- **TRLegalClientForm** — react-hook-form client creation form (name, type, email, country, industry)

## Technical Implementation

### Files Modified

- `apps/Client/src/components/ui/TRCaseStatusBadge.tsx`: New — status badge using CASE_STATUS_LABELS/COLORS (25 LOC)
- `apps/Client/src/components/ui/TRCaseStatusBadge.tsx`: New — case status chip (25 LOC)
- `apps/Client/src/components/ui/TRLegalDomainBadge.tsx`: New — domain chip (25 LOC)
- `apps/Client/src/components/ui/TRCasePriorityBadge.tsx`: New — priority chip (25 LOC)
- `apps/Client/src/components/ui/TRSpecialistScoreDisplay.tsx`: New — score with progress bar (29 LOC)
- `apps/Client/src/components/ui/TRDeliverableChecklist.tsx`: New — deliverable checklist with status toggles (87 LOC)
- `apps/Client/src/components/ui/TRPricingTimeline.tsx`: New — pricing action timeline (83 LOC)
- `apps/Client/src/components/forms/TRLegalCaseForm.tsx`: New — case creation form (227 LOC)
- `apps/Client/src/components/forms/TRLegalSpecialistForm.tsx`: New — specialist creation form (158 LOC)
- `apps/Client/src/components/forms/TRLegalClientForm.tsx`: New — client creation form (141 LOC)
- `apps/Client/src/pages/legaldesk/LegalDeskDashboardPage.tsx`: New — dashboard with stats + charts (180 LOC)
- `apps/Client/src/pages/legaldesk/LegalDeskCasesPage.tsx`: New — filterable case table (215 LOC)
- `apps/Client/src/pages/legaldesk/LegalDeskNewCasePage.tsx`: New — case creation page (85 LOC)
- `apps/Client/src/pages/legaldesk/LegalDeskCaseDetailPage.tsx`: New — 6-tab case detail (747 LOC)
- `apps/Client/src/pages/legaldesk/LegalDeskSpecialistsPage.tsx`: New — specialist card grid (158 LOC)
- `apps/Client/src/pages/legaldesk/LegalDeskClientsPage.tsx`: New — client table with dialog (138 LOC)
- `apps/Client/src/pages/legaldesk/LegalDeskAnalyticsPage.tsx`: New — analytics charts (136 LOC)
- `apps/Client/src/pages/legaldesk/index.ts`: New — barrel exports (7 LOC)
- `apps/Server/src/adapter/rest/legaldesk_routes.py`: Minor lint fix
- `apps/Server/tests/test_ld_classification_service.py`: Minor lint fix
- `.claude/commands/e2e/test_legaldesk_pages.md`: New — E2E test spec

### Key Changes

- **Case Detail 6-Tab Architecture**: The most complex page (747 LOC) implements Overview, Specialists, Deliverables, Pricing, Messages, and Documents tabs with `useState(0)` tab switching. Uses both `useLegaldeskCaseDetail` and `useLegaldeskPricing` hooks simultaneously.
- **Status Transition Engine**: Case Detail includes a `CASE_STATUS_TRANSITIONS` map defining valid next-state transitions per status (e.g., `new → classifying → open → assigning → active → in_progress → review → completed → closed → archived`), rendering only valid transition buttons.
- **Recharts Integration**: Dashboard and Analytics pages use PieChart and BarChart from Recharts, transforming `stats.cases_by_status` and `stats.cases_by_domain` records into chart data arrays using label/color constant maps.
- **All hooks consumed**: Pages consume all 6 existing Legal Desk hooks — `useLegaldeskDashboard`, `useLegaldeskCases`, `useLegaldeskCaseDetail`, `useLegaldeskPricing`, `useLegaldeskSpecialists`, `useLegaldeskClients`.
- **Consistent UX patterns**: All pages implement loading (CircularProgress), error (Alert + retry), and empty states. CRUD operations use MUI Dialogs with Snackbar feedback.

## How to Use

1. Navigate to `/poc/legal-desk/dashboard` to see the overview with stats and charts
2. Click "Cases" or navigate to `/poc/legal-desk/cases` to see the filterable case list
3. Use the 4 filter dropdowns (Status, Domain, Priority, Type) to narrow results
4. Click "New Case" or navigate to `/poc/legal-desk/cases/new` to create a case
5. Click any case row to open the detail view at `/poc/legal-desk/cases/:id`
6. Use the 6 tabs to manage different aspects of a case:
   - **Overview**: View case metadata, client info, AI classification
   - **Specialists**: View assigned specialists, suggest and assign new ones
   - **Deliverables**: Track deliverables with checklist, add new ones
   - **Pricing**: View negotiation timeline, propose/counter/accept/reject pricing
   - **Messages**: Send internal or external messages, filter by internal flag
   - **Documents**: View and upload case documents
7. Use status transition buttons to advance the case through the workflow
8. Navigate to `/poc/legal-desk/specialists` to manage specialists
9. Navigate to `/poc/legal-desk/clients` to manage clients
10. Navigate to `/poc/legal-desk/analytics` for domain distribution and summary stats

## Configuration

No additional configuration required. Pages consume existing hooks and services that connect to the Legal Desk API endpoints already registered in the backend.

**Note:** Routes are not yet wired into `App.tsx` or sidebar navigation — that is handled by a separate issue (LD-016).

## Testing

- **TypeScript check**: `cd apps/Client && npx tsc --noEmit`
- **Production build**: `cd apps/Client && npm run build`
- **E2E test**: See `.claude/commands/e2e/test_legaldesk_pages.md` for page-level E2E test steps
- All pages handle loading, error, and empty data states gracefully

## Notes

- The Case Detail page is the most complex at 747 LOC — it manages 11 `useState` hooks for form inputs, tab index, snackbar, and internal message filtering
- Pages were designed for parallel execution with LD-014 (UI components issue) — shared components are created inline here and can be reused
- Dashboard stats are limited to fields available in `LdDashboardStats` (total_cases, active_cases, total_specialists, total_clients, cases_by_status, cases_by_domain)
- Recharts was already installed in the project; no new dependencies were added
- Total: ~2,843 lines added across 23 files
