# Feature: CRM Prospect Creation Form (TRProspectForm)

## Metadata
issue_number: `53`
adw_id: `ab11c9f9`
issue_json: `{"number":53,"title":"[CRM Pipeline] Wave 2: Prospect Creation Form","body":"## Context\n**Project:** Meeting Processing CRM Pipeline — CRM prospect tracking and automated meeting transcript processing for Finance Tracker\n**Overview:** Create the TRProspectForm component for manually adding new prospects. Uses react-hook-form with MUI components following existing form patterns. Allows setting company name, contact name, contact email, initial stage, and notes.\n\n**Current Wave:** Wave 2 of 3 — CRM Kanban Board Frontend\n**Current Issue:** CRM-007 (Issue 7 of 14)\n**Parallel Execution:** YES — This issue runs in parallel with CRM-006, CRM-008.\n\n**Dependencies:** CRM-006 (TypeScript types for Prospect and PipelineStage)\n**What comes next:** CRM-008 (Kanban Board Page) integrates this form in a dialog for creating new prospects.\n\n## Request\nCreate the TRProspectForm component with react-hook-form and MUI."}`

## Feature Description
Create the `TRProspectForm` component — a react-hook-form + MUI form for manually creating and editing CRM prospects. The form captures company name, contact details (name, email, phone), initial pipeline stage, estimated deal value, source, and notes. It follows the exact same patterns as `TRBudgetForm`, `TRTransactionForm`, and other existing TR-prefixed forms in the codebase. This also requires adding the TypeScript types for Prospect and PipelineStage (CRM-006 dependency), creating the prospect API service layer, and a custom hook — all prerequisite infrastructure the form relies on.

## User Story
As a sales/account manager
I want to manually add new prospects through a form
So that I can track potential deals and manage my CRM pipeline

## Problem Statement
There is no frontend mechanism to create prospect records. The backend CRUD API exists (`/api/prospects/`) but there is no form component to allow users to input prospect data from the UI. The CRM Kanban Board (CRM-008) needs this form to be available in a dialog for prospect creation.

## Solution Statement
Create `TRProspectForm.tsx` following the established form component pattern (react-hook-form + MUI + Controller for selects). Add the prerequisite TypeScript types, prospect API service, and useProspects hook. The form handles both create and edit modes via the `initialData` prop, validates all fields against the backend DTO constraints, and includes proper loading states, error display, and logging.

## Relevant Files
Use these files to implement the feature:

**Reference patterns (read these to match conventions):**
- `apps/Client/src/components/forms/TRBudgetForm.tsx` — Primary reference: uses Controller for Select, InputAdornment for currency, handles create/edit mode. Follow this exact pattern.
- `apps/Client/src/components/forms/TRTransactionForm.tsx` — Additional reference for form patterns with multiple field types.
- `apps/Client/src/components/forms/TRRecurringTemplateForm.tsx` — Reference for forms with optional fields and multiline notes.
- `apps/Client/src/types/index.ts` — Where all TypeScript interfaces live. Append new CRM types here.
- `apps/Client/src/services/transactionService.ts` — Reference for service layer pattern (axios + logging).
- `apps/Client/src/services/budgetService.ts` — Additional service reference.
- `apps/Client/src/hooks/useBudgets.ts` — Reference for custom hook pattern (useState + useCallback + useEffect).
- `apps/Client/src/hooks/useTransactions.ts` — Additional hook reference.
- `apps/Client/src/api/clients/index.ts` — Axios apiClient (import from here for the service).

**Backend reference (understand the API contract):**
- `apps/Server/src/interface/prospect_dto.py` — Backend DTOs: `ProspectCreateDTO` fields, validation rules, stage literal values.
- `apps/Server/src/adapter/rest/prospect_routes.py` — API endpoints: POST `/api/prospects/`, GET with query params, etc.

**Conditional documentation (read these for additional context):**
- `app_docs/feature-57f962c3-prospect-data-model.md` — Prospect DB schema, model structure
- `app_docs/feature-eb19b5cd-pipeline-stage-configuration.md` — Pipeline stage names, colors, and configuration
- `app_docs/feature-70362135-prospect-crud-api-endpoints.md` — REST endpoint details, query params, auth/RBAC
- `app_docs/feature-2a0579e1-frontend-react-vite-setup.md` — Frontend structure, path aliases, axios config

**E2E test references (read these for E2E test creation):**
- `.claude/commands/test_e2e.md` — How to run E2E tests
- `.claude/commands/e2e/test_basic_query.md` — Example E2E test format and structure
- `.claude/commands/e2e/test_budget_management.md` — E2E reference for CRUD form testing

### New Files
- `apps/Client/src/components/forms/TRProspectForm.tsx` — The prospect creation/edit form component (core deliverable)
- `apps/Client/src/services/prospectService.ts` — Prospect API service layer
- `apps/Client/src/hooks/useProspects.ts` — Custom hook for prospect state management
- `.claude/commands/e2e/test_prospect_creation_form.md` — E2E test specification for the prospect form

## Implementation Plan
### Phase 1: Foundation
Add TypeScript types for Prospect, ProspectStage, and related interfaces to `apps/Client/src/types/index.ts`. These types mirror the backend DTOs (`ProspectCreateDTO`, `ProspectUpdateDTO`, `ProspectResponseDTO`, `ProspectListResponseDTO`, `ProspectFilterDTO`) and must match the API contract exactly.

### Phase 2: Core Implementation
1. Create `prospectService.ts` — Axios-based service with methods for `create`, `list`, `get`, `update`, `updateStage`, `delete`. Follows the same pattern as `transactionService.ts` and `budgetService.ts` with proper logging.
2. Create `useProspects.ts` — Custom React hook that wraps the service, manages state (prospects array, loading, error, filters), and exposes CRUD operations. Follows the `useBudgets.ts` pattern.
3. Create `TRProspectForm.tsx` — The form component with all fields, validation rules, create/edit mode handling, and proper MUI integration.

### Phase 3: Integration
The form is designed as a standalone component that receives `onSubmit`, `entityId`, and optional `initialData` props. CRM-008 (Kanban Board Page) will integrate this form in a dialog. No routing, page, or sidebar changes are needed for this issue — those belong to CRM-008.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add CRM TypeScript Types
- Open `apps/Client/src/types/index.ts`
- Append the following types at the end of the file:
  - `ProspectStage` — Union type: `'lead' | 'contacted' | 'qualified' | 'proposal' | 'negotiation' | 'won' | 'lost'`
  - `Prospect` — Interface matching `ProspectResponseDTO`: `id`, `entity_id`, `company_name`, `contact_name?`, `contact_email?`, `contact_phone?`, `stage`, `estimated_value?`, `source?`, `notes?`, `is_active`, `created_at`, `updated_at?`
  - `ProspectCreate` — Interface matching `ProspectCreateDTO`: `entity_id`, `company_name`, `contact_name?`, `contact_email?`, `contact_phone?`, `stage?`, `estimated_value?`, `source?`, `notes?`
  - `ProspectUpdate` — Interface matching `ProspectUpdateDTO`: all fields optional including `is_active?`
  - `ProspectStageUpdate` — Interface: `new_stage: ProspectStage`, `notes?: string`
  - `ProspectFilters` — Interface: `stage?`, `is_active?`, `source?`
  - `ProspectListResponse` — Interface: `prospects: Prospect[]`, `total: number`
- All string IDs (not UUIDs) per frontend convention — backend returns UUID as string in JSON

### Step 2: Create Prospect API Service
- Create `apps/Client/src/services/prospectService.ts`
- Import `apiClient` from `@/api/clients`
- Import types from `@/types`
- Export `prospectService` object with methods:
  - `create(data: ProspectCreate): Promise<Prospect>` — POST `/prospects/`
  - `list(entityId: string, filters?: ProspectFilters, skip?: number, limit?: number): Promise<ProspectListResponse>` — GET `/prospects/` with query params (`entity_id`, `stage`, `is_active`, `source`, `skip`, `limit`)
  - `get(prospectId: string, entityId: string): Promise<Prospect>` — GET `/prospects/{id}?entity_id=`
  - `update(prospectId: string, entityId: string, data: ProspectUpdate): Promise<Prospect>` — PUT `/prospects/{id}?entity_id=`
  - `updateStage(prospectId: string, entityId: string, data: ProspectStageUpdate): Promise<Prospect>` — PATCH `/prospects/{id}/stage?entity_id=`
  - `delete(prospectId: string, entityId: string): Promise<void>` — DELETE `/prospects/{id}?entity_id=`
- Add `console.log` / `console.error` logging with `INFO [ProspectService]` / `ERROR [ProspectService]` format
- Follow the exact pattern of `transactionService.ts`

### Step 3: Create useProspects Hook
- Create `apps/Client/src/hooks/useProspects.ts`
- Import `useState`, `useEffect`, `useCallback` from React
- Import `prospectService` from `@/services/prospectService`
- Import types from `@/types`
- Hook signature: `useProspects(entityId: string | null)`
- State: `prospects: Prospect[]`, `total: number`, `isLoading: boolean`, `error: string | null`, `filters: ProspectFilters`
- Methods (all wrapped in `useCallback`):
  - `fetchProspects()` — calls `prospectService.list(entityId, filters)`, sets state
  - `createProspect(data: ProspectCreate)` — calls `prospectService.create(data)`, then refetches
  - `updateProspect(id: string, data: ProspectUpdate)` — calls `prospectService.update(id, entityId, data)`, then refetches
  - `updateProspectStage(id: string, data: ProspectStageUpdate)` — calls `prospectService.updateStage(id, entityId, data)`, then refetches
  - `deleteProspect(id: string)` — calls `prospectService.delete(id, entityId)`, then refetches
  - `setFilters(filters: ProspectFilters)` — updates filter state (triggers refetch via useEffect)
- `useEffect` to auto-fetch when `entityId` or `filters` change (guard: skip if `entityId` is null)
- Add logging: `INFO [useProspects]` / `ERROR [useProspects]`
- Return: `{ prospects, total, isLoading, error, fetchProspects, createProspect, updateProspect, updateProspectStage, deleteProspect, filters, setFilters }`

### Step 4: Create TRProspectForm Component
- Create `apps/Client/src/components/forms/TRProspectForm.tsx`
- Follow the `TRBudgetForm.tsx` pattern exactly

**Internal form data interface:**
```typescript
interface ProspectFormData {
  company_name: string
  contact_name: string
  contact_email: string
  contact_phone: string
  stage: ProspectStage
  estimated_value: string  // string for number input
  source: string
  notes: string
}
```

**Props interface:**
```typescript
interface TRProspectFormProps {
  onSubmit: (data: ProspectCreate) => Promise<void>
  initialData?: Prospect
  entityId: string
  isLoading?: boolean
  onCancel?: () => void
}
```

**Stage options constant (inside the file):**
```typescript
const STAGE_OPTIONS: { value: ProspectStage; label: string }[] = [
  { value: 'lead', label: 'Lead' },
  { value: 'contacted', label: 'Contacted' },
  { value: 'qualified', label: 'Qualified' },
  { value: 'proposal', label: 'Proposal' },
  { value: 'negotiation', label: 'Negotiation' },
  { value: 'won', label: 'Won' },
  { value: 'lost', label: 'Lost' },
]
```

**Form fields (in order):**
1. `company_name` — `TextField` with `register`, required, `maxLength: 255`, label "Company Name"
2. `contact_name` — `TextField` with `register`, optional, `maxLength: 255`, label "Contact Name"
3. `contact_email` — `TextField` with `register`, optional, `maxLength: 255`, email pattern validation (`/^[^\s@]+@[^\s@]+\.[^\s@]+$/`), label "Contact Email", type="email"
4. `contact_phone` — `TextField` with `register`, optional, `maxLength: 100`, label "Contact Phone"
5. `stage` — `Controller` + MUI `Select` with `STAGE_OPTIONS`, required, default "lead", label "Pipeline Stage"
6. `estimated_value` — `TextField` type="number" with `register`, optional, `min: 0`, `$` InputAdornment, label "Estimated Value", step="0.01"
7. `source` — `TextField` with `register`, optional, `maxLength: 100`, label "Source"
8. `notes` — `TextField` with `register`, optional, `multiline`, `rows={3}`, label "Notes"

**Submit handler (`handleFormSubmit`):**
- Build `ProspectCreate` payload from form data
- Parse `estimated_value` with `parseFloat()`, send `undefined` if empty
- Include `entity_id` from props (not a form field)
- Set `stage` from form data
- Only include optional string fields if non-empty (send `undefined` for empty strings)
- Call `onSubmit(payload)`
- If not edit mode, `reset()` the form on success

**Buttons:**
- Cancel button (shown only if `onCancel` prop provided)
- Submit button: "Add Prospect" (create) / "Update Prospect" (edit)
- Both disabled during `isFormLoading = isLoading || isSubmitting`
- Submit button shows `CircularProgress` when loading

**Logging:**
- `console.log('INFO [TRProspectForm]: Form submitted', data)`
- `console.log('INFO [TRProspectForm]: Prospect submitted successfully')`
- `console.error('ERROR [TRProspectForm]: Failed to submit prospect:', error)`

### Step 5: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` to understand E2E test format
- Create `.claude/commands/e2e/test_prospect_creation_form.md` with:
  - **User Story:** As a sales manager, I want to create prospects through a form so I can manage my CRM pipeline
  - **Prerequisites:** Backend running, frontend running, test user logged in, at least one entity exists
  - **Test Steps:**
    1. Navigate to application and log in
    2. Verify the prospect form can be rendered (mount TRProspectForm in a test page or dialog)
    3. Verify all form fields are present: Company Name, Contact Name, Contact Email, Contact Phone, Pipeline Stage (select), Estimated Value, Source, Notes
    4. Test validation: submit empty form → "Company name is required" error appears
    5. Test email validation: enter invalid email → validation error appears
    6. Fill out all fields with valid data (company: "Acme Corp", contact: "John Doe", email: "john@acme.com", phone: "555-0100", stage: "qualified", value: "50000", source: "Website", notes: "Hot lead from website")
    7. Submit the form
    8. Verify POST request to `/api/prospects/` with correct payload
    9. Verify form resets after successful creation
    10. Take screenshots at key steps
  - **Success Criteria:** Form renders all fields, validation works, successful submission creates prospect via API
  - **Technical Verification:** Console logs for `INFO [TRProspectForm]`, `INFO [ProspectService]`; network request to `POST /api/prospects/`

### Step 6: Run Validation Commands
- Run `cd apps/Server && python -m pytest tests/` to verify backend tests pass (zero regressions)
- Run `cd apps/Client && npx tsc --noEmit` to verify TypeScript compilation with no errors
- Run `cd apps/Client && npm run build` to verify production build succeeds
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_prospect_creation_form.md` to validate the prospect form E2E

## Testing Strategy
### Unit Tests
- TypeScript compilation validates type correctness of all new interfaces
- The form component follows established patterns that are already validated by existing tests
- Service layer and hook follow the same patterns as tested counterparts (transactionService, useBudgets)

### Edge Cases
- Empty optional fields should send `undefined` (not empty string) to the API
- `estimated_value` empty string should become `undefined` (not `NaN` or `0`)
- Email validation should reject clearly invalid formats but allow standard emails
- Form should properly reset all fields (including the Select for stage) after successful creation
- Edit mode should populate all fields from `initialData`, including setting the stage Select
- Submitting with only the required field (company_name) should succeed — all other fields are optional
- Stage should default to "lead" when no initialData is provided

## Acceptance Criteria
- `TRProspectForm` component exists at `apps/Client/src/components/forms/TRProspectForm.tsx`
- Form uses react-hook-form with MUI components (TextField, Select via Controller)
- Company Name field is required with max 255 chars validation
- Contact Email validates email format when provided
- Pipeline Stage uses a Select dropdown with all 7 stages, defaults to "lead"
- Estimated Value field uses number input with `$` adornment
- Notes field is multiline (3 rows)
- Form handles both create mode and edit mode (via `initialData` prop)
- Form resets after successful creation (not after edit)
- Loading state disables all fields and shows CircularProgress on submit button
- Cancel button appears when `onCancel` prop is provided
- All logging follows `INFO/ERROR [TRProspectForm]` format
- TypeScript types for Prospect, ProspectCreate, ProspectStage etc. are defined in `types/index.ts`
- `prospectService` provides full CRUD + stage update via axios
- `useProspects` hook manages state with fetch/create/update/delete operations
- `npx tsc --noEmit` passes with zero errors
- `npm run build` succeeds
- Backend `pytest` passes with zero regressions
- E2E test specification created at `.claude/commands/e2e/test_prospect_creation_form.md`

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/` — Run Server tests to validate zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate all new types and components compile correctly
- `cd apps/Client && npm run build` — Run Client production build to validate the feature builds without errors
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_prospect_creation_form.md` to validate the prospect creation form E2E

## Notes
- This issue runs **in parallel** with CRM-006 (TypeScript types) and CRM-008 (Kanban Board Page). Since CRM-006's deliverable (types) is a dependency, Step 1 of this plan adds the types directly — if CRM-006 has already added them, Step 1 should verify they exist and skip or reconcile.
- The form is designed as a **standalone component** — it doesn't require a dedicated page or route. CRM-008 will mount it inside a Dialog for the Kanban Board's "Add Prospect" flow.
- The `useProspects` hook and `prospectService` are included because the form needs them for the E2E test and they'll be immediately used by CRM-008. Building them now prevents duplication.
- Pipeline stage colors (`#90CAF9`, `#80DEEA`, etc.) are NOT used in the form itself — they'll be used in the Kanban Board (CRM-008). The form only needs stage values and labels.
- The `is_active` field is intentionally excluded from the form — it's an update-only field managed programmatically (soft delete), not set during creation.
- No new npm packages are required — all dependencies (react-hook-form, @mui/material) are already installed.
