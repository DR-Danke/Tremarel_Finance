# Feature: Legal Desk UI Components & Forms

## Metadata
issue_number: `151`
adw_id: `e846c4b4`
issue_json: `{"number":151,"title":"[Legal Desk] Wave 6: UI Components & Forms"}`

## Feature Description
Build 6 reusable UI components and 3 react-hook-form based forms for the Legal Desk module. These are the building blocks used by all Legal Desk pages (LD-015, LD-016). The UI components include status/priority/domain badges, a specialist score display, a pricing negotiation timeline, and a deliverable checklist. The forms cover case creation/editing, specialist management, and client management. All components follow the TR-prefix naming convention and use existing TypeScript types from `@/types/legaldesk`.

## User Story
As a legal desk user
I want reusable UI components and forms for managing cases, specialists, and clients
So that I can efficiently interact with the Legal Desk system through consistent, well-typed interface elements

## Problem Statement
The Legal Desk module has its data layer complete (types, services, hooks) but lacks all UI components. Pages (LD-015, LD-016) cannot be built without these foundational badge components, display widgets, and CRUD forms.

## Solution Statement
Create 6 presentational UI components and 3 form components following existing codebase patterns:
- Badge components use MUI Chip with color/label maps from `@/types/legaldesk`
- Score display uses MUI Rating component
- Timeline uses MUI Stepper (vertical) as a lightweight alternative to `@mui/lab` Timeline (which is not installed)
- Deliverable checklist uses MUI List with Chip status badges
- Forms use react-hook-form with MUI components, supporting create and edit modes
- All components are fully typed with TypeScript, no `any` types

## Relevant Files
Use these files to implement the feature:

- **`apps/Client/src/types/legaldesk.ts`** — All Legal Desk types, interfaces, label maps, and color maps. Source of truth for `CaseStatus`, `CasePriority`, `LegalDomain`, `DeliverableStatus`, `PricingAction`, `LdPricingHistory`, `LdCaseDeliverable`, `LdCaseCreate`, `LdCaseUpdate`, `LdClientCreate`, `LdClientUpdate`, `LdSpecialistCreate`, `LdSpecialistUpdate`, `LdSpecialistExpertiseCreate`, `LdSpecialistJurisdictionCreate`, and all label/color constant maps.
- **`apps/Client/src/types/index.ts`** — Re-exports all legaldesk types; verify imports work via `@/types`.
- **`apps/Client/src/components/ui/TREventStatusBadge.tsx`** — Reference pattern for badge components (MUI Chip with config lookup).
- **`apps/Client/src/components/ui/TRBudgetCard.tsx`** — Reference pattern for TR-prefixed UI components with helper functions.
- **`apps/Client/src/components/forms/TRPersonForm.tsx`** — Reference pattern for react-hook-form with MUI (register, Controller, error display, edit mode).
- **`apps/Client/src/components/forms/TRTransactionForm.tsx`** — Reference pattern for complex forms with Select fields, watch, and Controller.
- **`apps/Client/src/hooks/useLegaldeskCases.ts`** — Hook providing `createCase` for form integration.
- **`apps/Client/src/hooks/useLegaldeskClients.ts`** — Hook providing `clients` list for case form Autocomplete, and `createClient`/`updateClient` for client form.
- **`apps/Client/src/hooks/useLegaldeskSpecialists.ts`** — Hook providing `createSpecialist`/`updateSpecialist` for specialist form.
- **`apps/Client/src/hooks/useLegaldeskPricing.ts`** — Hook providing `history` for pricing timeline.
- **`apps/Client/src/hooks/useLegaldeskCaseDetail.ts`** — Hook providing `caseDetail.deliverables` and `updateDeliverableStatus`.
- **`apps/Client/src/services/legaldeskService.ts`** — Service layer for all API calls.
- **`apps/Client/package.json`** — Check installed dependencies; `@mui/lab` is NOT installed.
- **`.claude/commands/test_e2e.md`** — Read to understand E2E test execution pattern.
- **`.claude/commands/e2e/test_transaction_crud.md`** — Read as reference for E2E test file format.
- **`app_docs/feature-e9ee37e2-legaldesk-frontend-typescript-types.md`** — Frontend TypeScript types documentation.

### New Files
- `apps/Client/src/components/ui/TRCaseStatusBadge.tsx`
- `apps/Client/src/components/ui/TRCasePriorityBadge.tsx`
- `apps/Client/src/components/ui/TRLegalDomainBadge.tsx`
- `apps/Client/src/components/ui/TRSpecialistScoreDisplay.tsx`
- `apps/Client/src/components/ui/TRPricingTimeline.tsx`
- `apps/Client/src/components/ui/TRDeliverableChecklist.tsx`
- `apps/Client/src/components/forms/TRLegalCaseForm.tsx`
- `apps/Client/src/components/forms/TRLegalSpecialistForm.tsx`
- `apps/Client/src/components/forms/TRLegalClientForm.tsx`
- `.claude/commands/e2e/test_legaldesk_ui_components.md`

## Implementation Plan
### Phase 1: Foundation
- Verify all required types and label/color maps exist in `@/types/legaldesk` (they do — confirmed via research)
- No new dependencies needed: MUI Rating is in `@mui/material`, and for the timeline we use MUI Stepper (vertical) instead of `@mui/lab` Timeline to avoid adding a new dependency
- Create the E2E test specification file

### Phase 2: Core Implementation
- Build the 6 UI components in order of complexity (badges first, then score, then timeline and checklist)
- Build the 3 forms in order (client form — simplest, case form — medium, specialist form — most complex with dynamic sub-sections)

### Phase 3: Integration
- All components import types from `@/types/legaldesk` and follow existing TR-prefix patterns
- Forms accept `onSubmit` and `onCancel` callbacks, making them composable by pages (LD-015)
- Badge components are pure/presentational, ready for use in tables, cards, and detail views
- Run validation commands to ensure zero regressions

## Step by Step Tasks

### Step 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` to understand the E2E test format
- Create `.claude/commands/e2e/test_legaldesk_ui_components.md` with test scenarios covering:
  - Badge components rendering with correct colors and labels
  - Score display showing stars and numeric value
  - Pricing timeline displaying history entries chronologically
  - Deliverable checklist showing items with status badges
  - Case form validation (required fields, create/edit modes)
  - Specialist form with dynamic expertise/jurisdiction sub-sections
  - Client form with email validation

### Step 2: Create TRCaseStatusBadge Component
- Create `apps/Client/src/components/ui/TRCaseStatusBadge.tsx`
- Import `CaseStatus`, `CASE_STATUS_LABELS`, `CASE_STATUS_COLORS` from `@/types/legaldesk`
- Define `TRCaseStatusBadgeProps` interface: `{ status: CaseStatus; size?: 'small' | 'medium' }`
- Render MUI `Chip` with `label` from `CASE_STATUS_LABELS[status]` and `sx={{ backgroundColor }}` from `CASE_STATUS_COLORS[status]`
- Support `size` prop (default `'small'`)
- Add `console.log('INFO [TRCaseStatusBadge]: Rendering status:', status)` logging
- Named export + default export

### Step 3: Create TRCasePriorityBadge Component
- Create `apps/Client/src/components/ui/TRCasePriorityBadge.tsx`
- Import `CasePriority`, `CASE_PRIORITY_LABELS`, `CASE_PRIORITY_COLORS` from `@/types/legaldesk`
- Define `TRCasePriorityBadgeProps` interface: `{ priority: CasePriority }`
- Render MUI `Chip` with label from `CASE_PRIORITY_LABELS[priority]` and background color from `CASE_PRIORITY_COLORS[priority]`
- Colors: low=green (#4CAF50), medium=yellow (#FFC107), high=orange (#FF9800), urgent=red (#F44336) — already in `CASE_PRIORITY_COLORS`
- Add logging, named export + default export

### Step 4: Create TRLegalDomainBadge Component
- Create `apps/Client/src/components/ui/TRLegalDomainBadge.tsx`
- Import `LegalDomain`, `LEGAL_DOMAIN_LABELS`, `LEGAL_DOMAIN_COLORS` from `@/types/legaldesk`
- Define `TRLegalDomainBadgeProps` interface: `{ domain: LegalDomain }`
- Render MUI `Chip` with label from `LEGAL_DOMAIN_LABELS[domain]` and background color from `LEGAL_DOMAIN_COLORS[domain]`, white text for contrast
- Add logging, named export + default export

### Step 5: Create TRSpecialistScoreDisplay Component
- Create `apps/Client/src/components/ui/TRSpecialistScoreDisplay.tsx`
- Import MUI `Rating`, `Box`, `Typography` from `@mui/material`
- Define `TRSpecialistScoreDisplayProps` interface: `{ score: number; showNumeric?: boolean }`
- Render MUI `Rating` component with `value={score}`, `precision={0.5}`, `readOnly`, `max={5}`
- When `showNumeric` is true (default true), show numeric score next to stars as `Typography` variant `body2`
- Add logging, named export + default export

### Step 6: Create TRPricingTimeline Component
- Create `apps/Client/src/components/ui/TRPricingTimeline.tsx`
- Import `LdPricingHistory`, `PRICING_ACTION_LABELS` from `@/types/legaldesk`
- Import MUI `Stepper`, `Step`, `StepLabel`, `StepContent`, `Typography`, `Box`, `Chip` from `@mui/material`
- Define `TRPricingTimelineProps` interface: `{ history: LdPricingHistory[] }`
- Sort history by `created_at` chronologically
- Render a vertical `Stepper` (with `orientation="vertical"` and `activeStep={history.length - 1}`) where each `Step` shows:
  - `StepLabel`: Action type label from `PRICING_ACTION_LABELS[entry.action]` + formatted date
  - `StepContent`: Previous amount → New amount (formatted as currency), margin info if available, notes if present
- Handle empty history with a "No pricing history" message
- Add logging, named export + default export

### Step 7: Create TRDeliverableChecklist Component
- Create `apps/Client/src/components/ui/TRDeliverableChecklist.tsx`
- Import `LdCaseDeliverable`, `DeliverableStatus`, `DELIVERABLE_STATUS_LABELS`, `DELIVERABLE_STATUS_COLORS` from `@/types/legaldesk`
- Import MUI `List`, `ListItem`, `ListItemText`, `Chip`, `Box`, `Typography`, `Select`, `MenuItem`, `FormControl` from `@mui/material`
- Define `TRDeliverableChecklistProps` interface: `{ deliverables: LdCaseDeliverable[]; onStatusChange?: (id: number, status: DeliverableStatus) => void }`
- Render a `List` where each `ListItem` shows:
  - Title as primary text
  - Specialist ID (or "Unassigned") and due date as secondary text
  - Status `Chip` with color from `DELIVERABLE_STATUS_COLORS` and label from `DELIVERABLE_STATUS_LABELS`
  - If `onStatusChange` is provided, render a small `Select` dropdown to change status
- Handle empty deliverables with "No deliverables" message
- Add logging, named export + default export

### Step 8: Create TRLegalClientForm Component
- Create `apps/Client/src/components/forms/TRLegalClientForm.tsx`
- Import `useForm`, `Controller` from `react-hook-form`
- Import MUI components: `TextField`, `Button`, `Box`, `FormControl`, `InputLabel`, `Select`, `MenuItem`, `FormHelperText`, `CircularProgress`
- Import types: `LdClient`, `LdClientCreate`, `LdClientUpdate`, `ClientType`, `CLIENT_TYPE_LABELS` from `@/types/legaldesk`
- Define `ClientFormData` interface for form fields: `name`, `client_type`, `contact_email`, `contact_phone`, `country`, `industry`
- Define `TRLegalClientFormProps`: `{ onSubmit: (data: LdClientCreate | LdClientUpdate) => Promise<void>; initialData?: LdClient; onCancel: () => void; isSubmitting?: boolean }`
- Form fields:
  - `name`: TextField, required validation
  - `client_type`: Controller + Select with options from `CLIENT_TYPE_LABELS` (company, individual)
  - `contact_email`: TextField with email pattern validation (`/^$|^[^\s@]+@[^\s@]+\.[^\s@]+$/`)
  - `contact_phone`: TextField
  - `country`: TextField
  - `industry`: TextField
- Support create and edit modes via `initialData` prop, use `reset()` in `useEffect`
- `isFormLoading = isSubmitting || formSubmitting` disables all inputs
- Logging: `console.log('INFO [TRLegalClientForm]: ...')`
- Named export + default export

### Step 9: Create TRLegalCaseForm Component
- Create `apps/Client/src/components/forms/TRLegalCaseForm.tsx`
- Import `useForm`, `Controller` from `react-hook-form`
- Import MUI components: `TextField`, `Button`, `Box`, `FormControl`, `InputLabel`, `Select`, `MenuItem`, `FormHelperText`, `CircularProgress`, `Autocomplete`
- Import types: `LdCase`, `LdCaseCreate`, `LdCaseUpdate`, `LdClient`, `LegalDomain`, `CaseType`, `CaseComplexity`, `CasePriority`, `OriginationChannel`, `LEGAL_DOMAIN_LABELS`, `CASE_TYPE_LABELS`, `CASE_COMPLEXITY_LABELS`, `CASE_PRIORITY_LABELS` from `@/types/legaldesk`
- Define `CaseFormData` interface: `title`, `description`, `client_id`, `legal_domain`, `case_type`, `complexity`, `origination_channel`, `client_budget`, `deadline`, `jurisdiction`, `priority`
- Define `TRLegalCaseFormProps`: `{ onSubmit: (data: LdCaseCreate | LdCaseUpdate) => Promise<void>; initialData?: LdCase; clients: LdClient[]; onCancel: () => void; isSubmitting?: boolean }`
- Form fields:
  - `title`: TextField, required
  - `description`: TextField, multiline
  - `client_id`: Controller + MUI `Autocomplete` with `clients` prop as options, `getOptionLabel` showing client name, required
  - `legal_domain`: Controller + Select with options from `LEGAL_DOMAIN_LABELS`, required
  - `case_type`: Controller + Select with options from `CASE_TYPE_LABELS`
  - `complexity`: Controller + Select with options from `CASE_COMPLEXITY_LABELS`
  - `priority`: Controller + Select with options from `CASE_PRIORITY_LABELS`
  - `origination_channel`: Controller + Select with options `[{value: 'direct', label: 'Direct'}, {value: 'referral', label: 'Referral'}]`
  - `client_budget`: TextField type="number"
  - `deadline`: TextField type="date" with `InputLabelProps={{ shrink: true }}`
  - `jurisdiction`: TextField
- Support create and edit modes
- Logging, named export + default export

### Step 10: Create TRLegalSpecialistForm Component
- Create `apps/Client/src/components/forms/TRLegalSpecialistForm.tsx`
- Import `useForm`, `Controller`, `useFieldArray` from `react-hook-form`
- Import MUI components: `TextField`, `Button`, `Box`, `FormControl`, `InputLabel`, `Select`, `MenuItem`, `FormHelperText`, `CircularProgress`, `Typography`, `IconButton`, `Divider`
- Import `Add` and `Delete` icons from `@mui/icons-material`
- Import types: `LdSpecialist`, `LdSpecialistCreate`, `LdSpecialistUpdate`, `SpecialistType`, `LegalDomain`, `ProficiencyLevel`, `LEGAL_DOMAIN_LABELS`, `PROFICIENCY_LEVEL_LABELS` from `@/types/legaldesk`
- Define `ExpertiseEntry`: `{ legal_domain: LegalDomain; proficiency_level: ProficiencyLevel }`
- Define `JurisdictionEntry`: `{ country: string; region: string; is_primary: boolean }`
- Define `SpecialistFormData`: `name`, `specialist_type`, `email`, `phone`, `country`, `city`, `years_experience`, `hourly_rate`, `expertise: ExpertiseEntry[]`, `jurisdictions: JurisdictionEntry[]`
- Define `TRLegalSpecialistFormProps`: `{ onSubmit: (data: LdSpecialistCreate | LdSpecialistUpdate, expertise?: ExpertiseEntry[], jurisdictions?: JurisdictionEntry[]) => Promise<void>; initialData?: LdSpecialist; onCancel: () => void; isSubmitting?: boolean }`
- Use `useFieldArray` for dynamic expertise and jurisdiction sub-sections
- Main fields:
  - `name`: TextField, required (maps to `full_name`)
  - `specialist_type`: Controller + Select with options: individual, boutique_firm
  - `email`: TextField
  - `phone`: TextField
  - `country`: TextField
  - `city`: TextField (note: city is not in the backend model, include as optional UI field)
  - `years_experience`: TextField type="number"
  - `hourly_rate`: TextField type="number"
- Expertise sub-section:
  - "Add Expertise" button appends a new row with `legal_domain` Select and `proficiency_level` Select
  - Delete icon button to remove rows
- Jurisdictions sub-section:
  - "Add Jurisdiction" button appends a new row with `country` TextField, `region` TextField, `is_primary` checkbox
  - Delete icon button to remove rows
- Support create and edit modes
- Logging, named export + default export

### Step 11: Run Validation Commands
- Run `cd apps/Client && npx tsc --noEmit` to verify TypeScript compilation with zero errors
- Run `cd apps/Client && npm run build` to verify production build succeeds
- Run `cd apps/Server && python -m pytest tests/ -x` to verify backend tests still pass (no regressions)
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_legaldesk_ui_components.md` to validate components work end-to-end

## Testing Strategy
### Unit Tests
- Components are presentational and tested via E2E tests rather than unit tests
- Forms are validated through E2E test scenarios covering create/edit modes, required field validation, and submission

### Edge Cases
- Badge components receiving undefined/invalid status values — use fallback config
- Empty arrays for `TRPricingTimeline` (history=[]) and `TRDeliverableChecklist` (deliverables=[]) — show empty state messages
- Score values outside 0-5 range in `TRSpecialistScoreDisplay` — MUI Rating handles clamping
- Client form email field with invalid format — validation pattern rejects
- Specialist form with no expertise/jurisdiction entries — valid submission, arrays sent as empty
- Case form with no clients available — Autocomplete shows empty, required validation prevents submit
- Edit mode forms with null optional fields — default to empty strings

## Acceptance Criteria
- All 6 UI components render correctly with proper types from `@/types/legaldesk`
- `TRCaseStatusBadge` shows correct color and label for all 11 case statuses
- `TRCasePriorityBadge` shows correct color for low (green), medium (blue/yellow), high (orange), urgent (red)
- `TRLegalDomainBadge` shows correct label for all 10 legal domains
- `TRSpecialistScoreDisplay` renders 5-star rating with optional numeric display
- `TRPricingTimeline` renders chronological history entries with amounts and action types
- `TRDeliverableChecklist` renders deliverables with status chips and optional status change
- All 3 forms use react-hook-form with proper validation and error display
- `TRLegalCaseForm` supports create and edit modes with Autocomplete client selection
- `TRLegalSpecialistForm` supports dynamic expertise and jurisdiction sub-sections
- `TRLegalClientForm` validates email format
- All components use TR prefix naming convention
- All components have full TypeScript typing with no `any` types
- `npx tsc --noEmit` passes with zero errors
- `npm run build` succeeds
- Backend tests pass with zero regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run TypeScript type check to validate all new components compile without errors
- `cd apps/Client && npm run build` — Run production build to validate no build errors
- `cd apps/Server && python -m pytest tests/ -x` — Run backend tests to confirm zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_legaldesk_ui_components.md` E2E test file to validate components work end-to-end

## Notes
- **No `@mui/lab` needed**: The `TRPricingTimeline` uses MUI's `Stepper` component with `orientation="vertical"` instead of `@mui/lab` Timeline, avoiding a new dependency install.
- **No `@mui/x-date-pickers` needed**: Date fields use native `<TextField type="date">` with `InputLabelProps={{ shrink: true }}`, consistent with other forms in the codebase.
- **Specialist form `city` field**: The `LdSpecialistCreate` interface does not have a `city` field. The form includes it as UI-only or it should be omitted. Implementer should check if the backend supports it and either include or exclude accordingly.
- **Parallel execution**: This issue runs in parallel with LD-015 (pages) and LD-016. Components built here will be consumed by LD-015 pages.
- **Interface naming**: The issue references `PricingHistoryEntry` and `CaseDeliverable` but the actual type names are `LdPricingHistory` and `LdCaseDeliverable` — use the actual names from `@/types/legaldesk`.
