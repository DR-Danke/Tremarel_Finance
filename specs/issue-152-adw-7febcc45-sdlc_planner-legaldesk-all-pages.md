# Feature: Legal Desk All Pages (Dashboard, Cases, Specialists, Clients, Analytics)

## Metadata
issue_number: `152`
adw_id: `7febcc45`
issue_json: ``

## Feature Description
Build all 7 Legal Desk frontend pages that compose UI components with data hooks to create the complete Legal Desk case management interface. The pages include: Dashboard (stats + charts), Cases List (filterable table), New Case (form), Case Detail (6-tab interface — the most complex page), Specialists (card grid), Clients (table), and Analytics (charts + rankings). These pages are the final UI layer that wires together the existing service layer (`legaldeskService`), React hooks (`useLegaldeskDashboard`, `useLegaldeskCases`, `useLegaldeskCaseDetail`, `useLegaldeskPricing`, `useLegaldeskSpecialists`, `useLegaldeskClients`), and TypeScript types (`legaldesk.ts`) into user-facing pages.

## User Story
As a legal operations manager
I want to access dashboard, cases, specialists, clients, and analytics pages for the Legal Desk module
So that I can manage legal cases end-to-end — from intake through specialist assignment, pricing negotiation, deliverable tracking, and analytics review

## Problem Statement
The Legal Desk backend API (33 endpoints), frontend service layer, React hooks, and TypeScript types are fully implemented, but there are no user-facing pages to interact with this data. Users cannot view, create, or manage cases, specialists, or clients without the page components.

## Solution Statement
Create 7 page components under `apps/Client/src/pages/legaldesk/` that consume existing hooks and render the Legal Desk data. Since the UI components from LD-014 (TRCaseStatusBadge, TRLegalDomainBadge, TRLegalCaseForm, etc.) may not yet exist (parallel execution), this plan includes creating the necessary UI components and forms inline or as shared component files. Each page handles loading, error, and empty states following existing project patterns.

## Relevant Files
Use these files to implement the feature:

**Types & Constants (read-only, already exist):**
- `apps/Client/src/types/legaldesk.ts` — All 14 string literal types, entity interfaces, create/update DTOs, filter interfaces, label/color constant maps (CASE_STATUS_LABELS, CASE_STATUS_COLORS, LEGAL_DOMAIN_LABELS, etc.)

**Service Layer (read-only, already exists):**
- `apps/Client/src/services/legaldeskService.ts` — 40+ methods covering cases, assignments, deliverables, messages, documents, pricing, specialists, clients, analytics

**React Hooks (read-only, already exist):**
- `apps/Client/src/hooks/useLegaldeskDashboard.ts` — Returns `stats: LdDashboardStats | null`, `loading`, `error`, `refreshStats`
- `apps/Client/src/hooks/useLegaldeskCases.ts` — Returns `cases`, `loading`, `error`, `filters`, `setFilters`, `createCase`, `refreshCases`
- `apps/Client/src/hooks/useLegaldeskCaseDetail.ts` — Returns `caseDetail`, `loading`, `error`, `candidates`, `updateCase`, `updateStatus`, `classifyCase`, `assignSpecialist`, `suggestSpecialists`, `updateAssignmentStatus`, `addDeliverable`, `updateDeliverableStatus`, `addMessage`, `addDocument`, `refreshCase`
- `apps/Client/src/hooks/useLegaldeskPricing.ts` — Returns `history`, `loading`, `error`, `propose`, `counter`, `accept`, `reject`, `refreshPricing`
- `apps/Client/src/hooks/useLegaldeskSpecialists.ts` — Returns `specialists`, `loading`, `error`, `createSpecialist`, `updateSpecialist`, `addExpertise`, `addJurisdiction`, `submitScore`, `refreshSpecialists`
- `apps/Client/src/hooks/useLegaldeskClients.ts` — Returns `clients`, `loading`, `error`, `createClient`, `updateClient`, `refreshClients`

**Existing Page Patterns (reference):**
- `apps/Client/src/pages/DashboardPage.tsx` — Stats cards + charts pattern with Grid layout
- `apps/Client/src/pages/restaurantos/RestaurantOSDashboardPage.tsx` — Loading/error/empty state patterns
- `apps/Client/src/pages/CategoriesPage.tsx` — Dialog-based CRUD with Snackbar notifications

**E2E Test References:**
- `.claude/commands/test_e2e.md` — How to create and run E2E tests
- `.claude/commands/e2e/test_basic_query.md` — E2E test file format reference
- `.claude/commands/e2e/test_servicedesk_dashboard.md` — Dashboard E2E test pattern

**Conditional Documentation (read if needed):**
- `app_docs/feature-e9ee37e2-legaldesk-frontend-typescript-types.md` — Frontend TS types reference
- `app_docs/feature-cbc09752-legaldesk-pydantic-dtos-enums.md` — Backend DTOs for understanding API shapes

### New Files

**Pages (7 files):**
- `apps/Client/src/pages/legaldesk/LegalDeskDashboardPage.tsx`
- `apps/Client/src/pages/legaldesk/LegalDeskCasesPage.tsx`
- `apps/Client/src/pages/legaldesk/LegalDeskNewCasePage.tsx`
- `apps/Client/src/pages/legaldesk/LegalDeskCaseDetailPage.tsx`
- `apps/Client/src/pages/legaldesk/LegalDeskSpecialistsPage.tsx`
- `apps/Client/src/pages/legaldesk/LegalDeskClientsPage.tsx`
- `apps/Client/src/pages/legaldesk/LegalDeskAnalyticsPage.tsx`

**Shared UI Components (9 files — needed by pages, may be created by LD-014 in parallel):**
- `apps/Client/src/components/ui/TRCaseStatusBadge.tsx` — Chip displaying case status with label/color from constants
- `apps/Client/src/components/ui/TRLegalDomainBadge.tsx` — Chip displaying legal domain with label/color
- `apps/Client/src/components/ui/TRCasePriorityBadge.tsx` — Chip displaying case priority with label/color
- `apps/Client/src/components/ui/TRSpecialistScoreDisplay.tsx` — Score display with visual indicator (rating or progress bar)
- `apps/Client/src/components/ui/TRDeliverableChecklist.tsx` — Checklist of deliverables with status toggles
- `apps/Client/src/components/ui/TRPricingTimeline.tsx` — Timeline of pricing negotiation history

**Form Components (3 files):**
- `apps/Client/src/components/forms/TRLegalCaseForm.tsx` — Case creation/edit form with react-hook-form
- `apps/Client/src/components/forms/TRLegalSpecialistForm.tsx` — Specialist creation form with react-hook-form
- `apps/Client/src/components/forms/TRLegalClientForm.tsx` — Client creation form with react-hook-form

**Page Index:**
- `apps/Client/src/pages/legaldesk/index.ts` — Re-exports all page components

**E2E Test:**
- `.claude/commands/e2e/test_legaldesk_pages.md` — E2E test for Legal Desk pages

## Implementation Plan
### Phase 1: Foundation — Shared UI Components & Forms
Create the reusable badge components (TRCaseStatusBadge, TRLegalDomainBadge, TRCasePriorityBadge, TRSpecialistScoreDisplay), the composite components (TRDeliverableChecklist, TRPricingTimeline), and the 3 form components (TRLegalCaseForm, TRLegalSpecialistForm, TRLegalClientForm). These are the building blocks the pages will compose.

### Phase 2: Core Implementation — Page Components
Build all 7 pages in dependency order:
1. **Dashboard** — simplest, just stats + charts
2. **Clients** — simple table with dialog form
3. **Specialists** — card grid with dialog form
4. **Cases List** — filterable table with navigation
5. **New Case** — form page with redirect
6. **Case Detail** — most complex, 6-tab interface with status transitions
7. **Analytics** — charts + rankings

### Phase 3: Integration — Index & Validation
Create the page index file for clean imports. Run TypeScript type checks and build to ensure zero regressions.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` to understand E2E test format
- Create `.claude/commands/e2e/test_legaldesk_pages.md` with test steps covering:
  - Navigate to `/poc/legal-desk/dashboard` and verify stats cards, charts
  - Navigate to `/poc/legal-desk/cases` and verify filterable table
  - Click "New Case" and verify form renders
  - Navigate to `/poc/legal-desk/cases/:id` and verify 6-tab interface, tab switching
  - Navigate to `/poc/legal-desk/specialists` and verify card grid
  - Navigate to `/poc/legal-desk/clients` and verify table
  - Navigate to `/poc/legal-desk/analytics` and verify charts

### Step 2: Create Badge Components
- Create `apps/Client/src/components/ui/TRCaseStatusBadge.tsx`:
  - Props: `{ status: CaseStatus; size?: 'small' | 'medium' }`
  - Renders MUI Chip with `CASE_STATUS_LABELS[status]` as label and `CASE_STATUS_COLORS[status]` as background color
- Create `apps/Client/src/components/ui/TRLegalDomainBadge.tsx`:
  - Props: `{ domain: LegalDomain; size?: 'small' | 'medium' }`
  - Renders MUI Chip with `LEGAL_DOMAIN_LABELS[domain]` as label and `LEGAL_DOMAIN_COLORS[domain]` as background color
- Create `apps/Client/src/components/ui/TRCasePriorityBadge.tsx`:
  - Props: `{ priority: CasePriority; size?: 'small' | 'medium' }`
  - Renders MUI Chip with `CASE_PRIORITY_LABELS[priority]` as label and `CASE_PRIORITY_COLORS[priority]` as background color
- Create `apps/Client/src/components/ui/TRSpecialistScoreDisplay.tsx`:
  - Props: `{ score: number; maxScore?: number }`
  - Renders score as a number with a LinearProgress bar (value = score / maxScore * 100, default maxScore=10)

### Step 3: Create Composite UI Components
- Create `apps/Client/src/components/ui/TRDeliverableChecklist.tsx`:
  - Props: `{ deliverables: LdCaseDeliverable[]; onStatusChange: (deliverableId: number, status: DeliverableStatus) => void }`
  - Renders a list of deliverables with Checkbox for completion toggle
  - Each item shows: title, due_date, current status (DELIVERABLE_STATUS_LABELS), assigned specialist_id
  - Checking marks as `completed`, unchecking marks as `pending`
- Create `apps/Client/src/components/ui/TRPricingTimeline.tsx`:
  - Props: `{ history: LdPricingHistory[] }`
  - Renders MUI Timeline (or simple list) showing pricing actions chronologically
  - Each entry shows: action label (PRICING_ACTION_LABELS), new_amount, currency, changed_by, notes, created_at

### Step 4: Create Form Components
- Create `apps/Client/src/components/forms/TRLegalCaseForm.tsx`:
  - Uses react-hook-form with MUI TextField/Select
  - Fields: title (required), client_id (Select from client list, required), legal_domain (Select, required), description, complexity (Select), priority (Select), budget (number), estimated_cost (number), deadline (date)
  - Props: `{ onSubmit: (data: LdCaseCreate) => Promise<void>; clients: LdClient[]; loading?: boolean }`
  - Validation on required fields
- Create `apps/Client/src/components/forms/TRLegalSpecialistForm.tsx`:
  - Fields: full_name (required), email (required, email pattern), phone, years_experience (number), hourly_rate (number), currency (default USD), max_concurrent_cases (number)
  - Props: `{ onSubmit: (data: LdSpecialistCreate) => Promise<void>; loading?: boolean }`
- Create `apps/Client/src/components/forms/TRLegalClientForm.tsx`:
  - Fields: name (required), client_type (Select: company/individual), contact_email (email pattern), contact_phone, country, industry, notes
  - Props: `{ onSubmit: (data: LdClientCreate) => Promise<void>; loading?: boolean }`

### Step 5: Create Dashboard Page
- Create `apps/Client/src/pages/legaldesk/LegalDeskDashboardPage.tsx`:
  - Use `useLegaldeskDashboard` hook
  - Handle loading state with CircularProgress, error state with Alert + retry button
  - 4 stat cards in Grid (xs=12 sm=6 md=3): Active Cases (`stats.active_cases`), Total Cases (`stats.total_cases`), Specialists Active (`stats.total_specialists`), Total Clients (`stats.total_clients`)
  - Pie chart: Cases by Status — transform `stats.cases_by_status` Record into Recharts data array `[{ name, value, fill }]` using CASE_STATUS_LABELS and CASE_STATUS_COLORS
  - Bar chart: Cases by Domain — transform `stats.cases_by_domain` Record into Recharts data array using LEGAL_DOMAIN_LABELS and LEGAL_DOMAIN_COLORS
  - Add console logging for component lifecycle

### Step 6: Create Clients Page
- Create `apps/Client/src/pages/legaldesk/LegalDeskClientsPage.tsx`:
  - Use `useLegaldeskClients` hook
  - MUI Table with columns: name, client_type (CLIENT_TYPE_LABELS), contact_email, country, industry
  - "Add Client" Button opens MUI Dialog containing TRLegalClientForm
  - On form submit: call `createClient`, close dialog, show Snackbar success
  - Handle loading/error states

### Step 7: Create Specialists Page
- Create `apps/Client/src/pages/legaldesk/LegalDeskSpecialistsPage.tsx`:
  - Use `useLegaldeskSpecialists` hook
  - Grid of MUI Cards showing: full_name, email, years_experience, hourly_rate + currency, overall_score (TRSpecialistScoreDisplay), workload indicator (current_workload / max_concurrent_cases)
  - "Add Specialist" Button opens MUI Dialog containing TRLegalSpecialistForm
  - On form submit: call `createSpecialist`, close dialog, show Snackbar success
  - Handle loading/error states

### Step 8: Create Cases List Page
- Create `apps/Client/src/pages/legaldesk/LegalDeskCasesPage.tsx`:
  - Use `useLegaldeskCases` hook
  - Filter row with 4 MUI Selects: status (CaseStatus options from CASE_STATUS_LABELS), legal_domain (LEGAL_DOMAIN_LABELS), priority (CASE_PRIORITY_LABELS), case_type (CASE_TYPE_LABELS). Include empty "All" option. Changes call `setFilters`
  - MUI Table columns: case_number, title, client_id, domain (TRLegalDomainBadge), status (TRCaseStatusBadge), priority (TRCasePriorityBadge)
  - "New Case" button: `useNavigate` to `/poc/legal-desk/cases/new`
  - Row click: navigate to `/poc/legal-desk/cases/${case.id}`
  - Handle loading/error states

### Step 9: Create New Case Page
- Create `apps/Client/src/pages/legaldesk/LegalDeskNewCasePage.tsx`:
  - Use `useLegaldeskCases` hook (for `createCase`) and `useLegaldeskClients` hook (for client list in dropdown)
  - Render TRLegalCaseForm with `clients` prop
  - On submit: call `createCase(data)`, on success navigate to `/poc/legal-desk/cases/${newCase.id}`
  - Show loading during submission, Alert on error
  - "Back to Cases" link/button

### Step 10: Create Case Detail Page (Most Complex)
- Create `apps/Client/src/pages/legaldesk/LegalDeskCaseDetailPage.tsx`:
  - Use `useParams` to get `:id`, parse to number
  - Use `useLegaldeskCaseDetail(caseId)` and `useLegaldeskPricing(caseId)` hooks
  - Handle loading/error states
  - **Header**: case_number + title, status badge, domain badge, priority badge
  - **Status Action Bar**: Define `CASE_STATUS_TRANSITIONS: Record<CaseStatus, CaseStatus[]>` mapping current status to valid next statuses. Render a Button for each valid transition. On click call `updateStatus(nextStatus)`
  - **6 MUI Tabs** with `useState(0)` for tab index:
    - **Tab 0 — Overview**: Case info grid (description, case_type, complexity, budget, estimated_cost, final_quote, margin_percentage, deadline), client details (`caseDetail.client`), AI classification results (`caseDetail.ai_classification` rendered as JSON or key-value)
    - **Tab 1 — Specialists**: Table of `caseDetail.specialists` (specialist_id, role with ASSIGNMENT_ROLE_LABELS, status with ASSIGNMENT_STATUS_LABELS, proposed_fee, agreed_fee). "Suggest Specialists" button calls `suggestSpecialists()`, displays `candidates` list with availability_score, overall_score, expertise_match. "Assign" button on each candidate calls `assignSpecialist({ case_id, specialist_id, role })`
    - **Tab 2 — Deliverables**: Render TRDeliverableChecklist with `caseDetail.deliverables`. Add deliverable form (title, description, due_date) at bottom, on submit calls `addDeliverable(data)`
    - **Tab 3 — Pricing**: Render TRPricingTimeline with `history` from pricing hook. Action buttons: "Propose" (opens amount input, calls `propose`), "Counter" (amount input, calls `counter`), "Accept" (calls `accept`), "Reject" (calls `reject`). Show buttons conditionally based on latest pricing action state
    - **Tab 4 — Messages**: List of `caseDetail.messages` sorted by created_at. Each shows sender_name, message, is_internal badge, timestamp. Checkbox toggle for "Show Internal" to filter. Add message form (sender_type, sender_name, message, is_internal checkbox), on submit calls `addMessage(data)`
    - **Tab 5 — Documents**: Table of `caseDetail.documents` (file_name, file_type, file_size_bytes, uploaded_by, created_at). Add document form (file_name, file_url, file_type, uploaded_by), on submit calls `addDocument(data)`

### Step 11: Create Analytics Page
- Create `apps/Client/src/pages/legaldesk/LegalDeskAnalyticsPage.tsx`:
  - Use `useLegaldeskDashboard` hook
  - Revenue summary cards: Total Cases, Active Cases, Total Specialists (derived from stats)
  - Recharts Line chart: Cases by Status over time (placeholder with status distribution)
  - Recharts Bar chart: Cases by Domain using `stats.cases_by_domain` with LEGAL_DOMAIN_LABELS/COLORS
  - Specialist utilization placeholder section

### Step 12: Create Page Index
- Create `apps/Client/src/pages/legaldesk/index.ts`:
  - Re-export all 7 page components for clean imports

### Step 13: Run Validation Commands
- Run TypeScript type check: `cd apps/Client && npx tsc --noEmit`
- Run production build: `cd apps/Client && npm run build`
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_legaldesk_pages.md` E2E test

## Testing Strategy
### Unit Tests
- No dedicated unit tests required for page components (pages are integration-level by nature)
- TypeScript compilation validates type safety across all components
- E2E tests cover user-facing functionality

### Edge Cases
- Empty data states: No cases, no specialists, no clients — pages should show empty messages
- Loading states: All pages display CircularProgress while hooks fetch data
- Error states: All pages display Alert with error message and retry button
- Case Detail with no specialists, deliverables, messages, or documents — tabs show empty state
- Invalid case ID in URL — handle gracefully with error message
- Status transitions — only valid transitions shown as buttons
- Pricing tab with no history — show "No pricing history" message

## Acceptance Criteria
- All 7 Legal Desk pages render without errors
- Dashboard shows 4 stat cards, pie chart (cases by status), bar chart (cases by domain)
- Cases List page has 4 filter controls and navigable table rows
- New Case page renders form with client dropdown, creates case, and redirects
- Case Detail page has 6 functional tabs that switch correctly
- Case Detail status bar only shows valid next-status transitions
- Specialists page shows card grid with score display and workload indicator
- Clients page shows table with "Add Client" dialog
- Analytics page shows charts derived from dashboard stats
- All pages handle loading, error, and empty states
- TypeScript compiles with zero errors (`npx tsc --noEmit`)
- Production build succeeds (`npm run build`)
- No `any` types used anywhere

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate zero type errors
- `cd apps/Client && npm run build` — Run Client build to validate production build succeeds
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_legaldesk_pages.md` to validate Legal Desk pages work end-to-end

## Notes
- **Parallel Execution with LD-014**: This issue runs in parallel with LD-014 (UI components and forms). The plan creates the badge/form components that LD-014 would also create. If LD-014 merges first, the component files will already exist — in that case, skip creating them and use the existing ones. If this issue merges first, LD-014 should use the components created here.
- **CASE_STATUS_TRANSITIONS Map**: The Case Detail page needs a status transition map. Define it inline in the Case Detail page:
  ```typescript
  const CASE_STATUS_TRANSITIONS: Record<CaseStatus, CaseStatus[]> = {
    new: ['classifying'],
    classifying: ['open'],
    open: ['assigning'],
    assigning: ['active'],
    active: ['in_progress'],
    in_progress: ['review'],
    review: ['negotiating', 'completed'],
    negotiating: ['completed'],
    completed: ['closed'],
    closed: ['archived'],
    archived: [],
  }
  ```
- **Recharts**: Already installed in the project (used by DashboardPage). No new dependencies needed.
- **No routing changes**: This issue does NOT modify `App.tsx` or sidebar navigation — that is LD-016's responsibility. Pages are created but not wired into routes yet.
- **Dashboard stats limitations**: `LdDashboardStats` does not include pipeline_value or avg_duration. The Dashboard uses available fields (total_cases, active_cases, total_specialists, total_clients). Analytics similarly works with available data.
