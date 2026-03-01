# Feature: Prospect Kanban Board Page

## Metadata
issue_number: `54`
adw_id: `6835fdde`
issue_json: ``

## Feature Description
Create the ProspectsPage with a Kanban board layout where each column represents a CRM pipeline stage (lead, contacted, qualified, proposal, negotiation, won, lost). Prospect cards appear in their respective stage columns showing key info (company name, contact, estimated value, source). The page uses TRMainLayout and useEntity() for entity scoping, is accessible from the sidebar navigation via a "Prospects" link, and includes a button to open the TRProspectForm in a dialog for creating new prospects. Pipeline stages are loaded from the backend API (with auto-seeding if none exist) and ordered by `order_index`. This is Wave 2 of the CRM Pipeline — the Kanban Board frontend. It depends on Wave 1's backend API (already completed) and runs in parallel with CRM-006 (useProspects hook, prospectService, types) and CRM-007 (TRProspectForm).

## User Story
As a CRM user managing prospects
I want to see all my prospects organized in a Kanban board by pipeline stage
So that I can visually track the progression of deals through my sales pipeline

## Problem Statement
Users need a visual way to see where each prospect stands in the sales pipeline. Without a Kanban board, prospect data is just a flat list with no spatial relationship to pipeline stages, making it hard to assess pipeline health at a glance.

## Solution Statement
Build a Kanban board page at `/prospects` that:
1. Fetches pipeline stages for the current entity (auto-seeds defaults if none exist)
2. Fetches all prospects for the current entity
3. Groups prospects into columns by their `stage` field
4. Renders each column with a header (stage display_name, color, prospect count)
5. Renders prospect cards with key details (company_name, contact_name, estimated_value, source)
6. Provides an "Add Prospect" button that opens TRProspectForm in a dialog
7. Integrates with sidebar navigation and routing

## Relevant Files
Use these files to implement the feature:

**Existing files to modify:**
- `apps/Client/src/types/index.ts` — Add Prospect, PipelineStage, and related TypeScript interfaces
- `apps/Client/src/App.tsx` — Add `/prospects` route with ProtectedRoute + TRMainLayout
- `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx` — Add "Prospects" navigation item with icon

**Existing files to reference (patterns):**
- `apps/Client/src/services/transactionService.ts` — Service pattern to follow for prospectService and pipelineStageService
- `apps/Client/src/hooks/useTransactions.ts` — Hook pattern to follow for useProspects and usePipelineStages
- `apps/Client/src/pages/TransactionsPage.tsx` — Page pattern to follow (entity scoping, dialog CRUD, loading states)
- `apps/Client/src/components/forms/TRTransactionForm.tsx` — Form component pattern to follow for TRProspectForm
- `apps/Client/src/components/ui/TRStatCard.tsx` — UI card component pattern
- `apps/Client/src/api/clients/index.ts` — API client with JWT interceptor
- `apps/Client/src/contexts/EntityContext.tsx` — Entity scoping pattern
- `apps/Client/src/hooks/useEntity.ts` — Entity hook usage

**Backend API reference (already implemented):**
- `apps/Server/src/adapter/rest/prospect_routes.py` — Prospect CRUD endpoints
- `apps/Server/src/adapter/rest/pipeline_stage_routes.py` — Pipeline stage endpoints + seed
- `apps/Server/src/interface/prospect_dto.py` — Prospect DTOs (field names, types)
- `apps/Server/src/interface/pipeline_stage_dto.py` — PipelineStage DTOs (field names, types)

**Conditional documentation to read:**
- `app_docs/feature-a201d4c8-main-layout-collapsible-sidebar.md` — Sidebar navigation patterns
- `app_docs/feature-d6d0f56d-entity-management-crud.md` — Entity-scoped feature patterns
- `app_docs/feature-70362135-prospect-crud-api-endpoints.md` — Prospect API endpoint details
- `app_docs/feature-eb19b5cd-pipeline-stage-configuration.md` — Pipeline stage configuration details
- `app_docs/feature-57f962c3-prospect-data-model.md` — Prospect data model reference

**E2E test reference:**
- `.claude/commands/test_e2e.md` — E2E test runner instructions
- `.claude/commands/e2e/test_budget_management.md` — Example E2E test with CRUD operations (pattern to follow)

### New Files
- `apps/Client/src/types/prospect.ts` — Prospect and PipelineStage type definitions (re-exported from types/index.ts)
- `apps/Client/src/services/prospectService.ts` — Prospect API service (CRUD + stage update)
- `apps/Client/src/services/pipelineStageService.ts` — Pipeline stage API service (list + seed)
- `apps/Client/src/hooks/useProspects.ts` — Hook for prospect state management and CRUD
- `apps/Client/src/hooks/usePipelineStages.ts` — Hook for pipeline stage loading and auto-seeding
- `apps/Client/src/components/ui/TRKanbanBoard.tsx` — Kanban board layout component (columns + scroll)
- `apps/Client/src/components/ui/TRKanbanColumn.tsx` — Single Kanban column (stage header + card list)
- `apps/Client/src/components/ui/TRProspectCard.tsx` — Prospect card for Kanban board display
- `apps/Client/src/components/forms/TRProspectForm.tsx` — Prospect create/edit form dialog
- `apps/Client/src/pages/ProspectsPage.tsx` — Main prospects page with Kanban board
- `.claude/commands/e2e/test_prospect_kanban_board.md` — E2E test spec for prospect Kanban board

## Implementation Plan
### Phase 1: Foundation
Add TypeScript type definitions for Prospect and PipelineStage that match the backend DTOs exactly. Create the prospectService and pipelineStageService API service layers. Create the useProspects and usePipelineStages hooks for state management.

### Phase 2: Core Implementation
Build the Kanban board UI components: TRKanbanBoard (horizontal scrolling container), TRKanbanColumn (stage column with header and card list), TRProspectCard (compact card showing prospect details). Build the TRProspectForm for creating and editing prospects. Build the ProspectsPage that composes everything together with entity scoping, loading states, and CRUD dialogs.

### Phase 3: Integration
Add the `/prospects` route to App.tsx. Add the "Prospects" navigation item to TRCollapsibleSidebar. Create the E2E test spec. Validate the full feature with type checks, build, and tests.

## Step by Step Tasks

### Step 1: Add Prospect and PipelineStage TypeScript Types
- Add the following interfaces to `apps/Client/src/types/index.ts`:
  - `ProspectStage` — String literal union type: `'lead' | 'contacted' | 'qualified' | 'proposal' | 'negotiation' | 'won' | 'lost'`
  - `Prospect` — Fields: id, entity_id, company_name, contact_name?, contact_email?, contact_phone?, stage (ProspectStage), estimated_value? (number | null), source? (string | null), notes? (string | null), is_active, created_at, updated_at? (string | null)
  - `ProspectCreate` — Fields: entity_id, company_name, contact_name?, contact_email?, contact_phone?, stage? (defaults to 'lead'), estimated_value?, source?, notes?
  - `ProspectUpdate` — All fields optional: company_name?, contact_name?, contact_email?, contact_phone?, stage?, estimated_value?, source?, notes?, is_active?
  - `ProspectListResponse` — Fields: prospects (Prospect[]), total (number)
  - `ProspectFilters` — Fields: stage? (ProspectStage), is_active? (boolean), source? (string)
  - `PipelineStage` — Fields: id, entity_id, name, display_name, order_index (number), color? (string | null), is_default, is_active, created_at, updated_at? (string | null)
  - `PipelineStageListResponse` — Fields: stages (PipelineStage[]), total (number)

### Step 2: Create prospectService
- Create `apps/Client/src/services/prospectService.ts` following the transactionService pattern
- Methods:
  - `list(entityId: string, filters?: ProspectFilters, skip?: number, limit?: number): Promise<ProspectListResponse>` — GET /prospects/?entity_id=...&stage=...&is_active=...&source=...
  - `get(prospectId: string, entityId: string): Promise<Prospect>` — GET /prospects/{id}?entity_id=...
  - `create(data: ProspectCreate): Promise<Prospect>` — POST /prospects/
  - `update(prospectId: string, entityId: string, data: ProspectUpdate): Promise<Prospect>` — PUT /prospects/{id}?entity_id=...
  - `updateStage(prospectId: string, entityId: string, newStage: string, notes?: string): Promise<Prospect>` — PATCH /prospects/{id}/stage?entity_id=... with body { new_stage, notes }
  - `delete(prospectId: string, entityId: string): Promise<void>` — DELETE /prospects/{id}?entity_id=...
- All methods include INFO/ERROR logging with `[ProspectService]` prefix
- Import apiClient from `@/api/clients`

### Step 3: Create pipelineStageService
- Create `apps/Client/src/services/pipelineStageService.ts` following the same service pattern
- Methods:
  - `list(entityId: string, activeOnly?: boolean): Promise<PipelineStageListResponse>` — GET /pipeline-stages/?entity_id=...&active_only=...
  - `seedDefaults(entityId: string): Promise<PipelineStage[]>` — POST /pipeline-stages/seed with body { entity_id }
- Include INFO/ERROR logging with `[PipelineStageService]` prefix

### Step 4: Create usePipelineStages Hook
- Create `apps/Client/src/hooks/usePipelineStages.ts`
- State: `stages: PipelineStage[]`, `isLoading: boolean`, `error: string | null`
- On mount (when entityId changes): fetch stages via pipelineStageService.list()
- If stages come back empty, auto-call pipelineStageService.seedDefaults() then re-fetch
- Sort stages by `order_index` before returning
- Return: `{ stages, isLoading, error, refetchStages }`

### Step 5: Create useProspects Hook
- Create `apps/Client/src/hooks/useProspects.ts` following useTransactions pattern
- State: `prospects: Prospect[]`, `total: number`, `isLoading: boolean`, `error: string | null`, `filters: ProspectFilters`
- Methods: `fetchProspects`, `createProspect`, `updateProspect`, `updateProspectStage`, `deleteProspect`, `setFilters`
- useEffect to auto-fetch when entityId or filters change
- Return: `{ prospects, total, isLoading, error, filters, fetchProspects, createProspect, updateProspect, updateProspectStage, deleteProspect, setFilters }`

### Step 6: Create TRProspectCard Component
- Create `apps/Client/src/components/ui/TRProspectCard.tsx`
- Props: `prospect: Prospect`, `onEdit?: (prospect: Prospect) => void`, `onClick?: (prospect: Prospect) => void`
- Render MUI `Card` with:
  - Company name as primary text (Typography variant="subtitle2", fontWeight 600)
  - Contact name as secondary text (if exists)
  - Estimated value chip (formatted as currency, if exists)
  - Source chip (if exists)
  - Small timestamp showing created_at
- Card has cursor pointer, subtle hover elevation change
- Compact layout suitable for Kanban column

### Step 7: Create TRKanbanColumn Component
- Create `apps/Client/src/components/ui/TRKanbanColumn.tsx`
- Props: `stage: PipelineStage`, `prospects: Prospect[]`, `onProspectClick?: (prospect: Prospect) => void`, `onProspectEdit?: (prospect: Prospect) => void`
- Render:
  - Column header: Paper with stage display_name, colored left border (stage.color or default), prospect count badge
  - Scrollable card list: Stack of TRProspectCard components
  - Min width: 280px, max height: calc(100vh - 220px) with overflow-y auto
- Column background: light gray (theme.palette.grey[100])

### Step 8: Create TRKanbanBoard Component
- Create `apps/Client/src/components/ui/TRKanbanBoard.tsx`
- Props: `stages: PipelineStage[]`, `prospects: Prospect[]`, `isLoading: boolean`, `onProspectClick?: (prospect: Prospect) => void`, `onProspectEdit?: (prospect: Prospect) => void`
- Group prospects by stage name into a Map
- Render horizontal scrolling container (Box with display: flex, overflowX: auto, gap: 2)
- For each stage (sorted by order_index), render a TRKanbanColumn with that stage's prospects
- Loading state: show Skeleton placeholders for columns
- Empty state per column: show "No prospects" Typography if column is empty

### Step 9: Create TRProspectForm Component
- Create `apps/Client/src/components/forms/TRProspectForm.tsx`
- Props: `onSubmit: (data: ProspectCreate | ProspectUpdate) => Promise<void>`, `initialData?: Prospect`, `entityId: string`, `stages: PipelineStage[]`, `onCancel: () => void`, `isSubmitting?: boolean`
- Use react-hook-form with MUI components:
  - `company_name` — TextField, required, max 255 chars
  - `contact_name` — TextField, optional, max 255 chars
  - `contact_email` — TextField, optional, type email, max 255 chars
  - `contact_phone` — TextField, optional, max 100 chars
  - `stage` — Select dropdown populated from stages prop (display_name), default "lead"
  - `estimated_value` — TextField, type number, optional, min 0
  - `source` — TextField, optional, max 100 chars
  - `notes` — TextField, multiline, 3 rows, optional
- Submit and Cancel buttons at bottom
- If initialData provided, pre-fill form (edit mode)
- If no initialData, default stage to "lead"

### Step 10: Create ProspectsPage
- Create `apps/Client/src/pages/ProspectsPage.tsx`
- Use useEntity() to get currentEntity
- Use usePipelineStages(entityId) to get stages
- Use useProspects(entityId) to get prospects and CRUD methods
- Page structure:
  - Header: Typography "Prospects" + Button "Add Prospect" (with Add icon)
  - Entity info paper (like TransactionsPage pattern): show currentEntity.name
  - TRKanbanBoard with stages and prospects
  - Dialog for Add Prospect: opens TRProspectForm, calls createProspect on submit
  - Dialog for Edit Prospect: opens TRProspectForm with initialData, calls updateProspect on submit
- Loading states: CircularProgress while entity, stages, or prospects load
- No entity selected: show "Please select an entity" message
- Error states: show Alert with error message
- After successful create/edit: close dialog, refetch prospects
- Console logging: `console.log('INFO [ProspectsPage]: ...')`

### Step 11: Add Route to App.tsx
- Import `ProspectsPage` from `@/pages/ProspectsPage`
- Add route block after `/reports` route:
  ```tsx
  <Route
    path="/prospects"
    element={
      <ProtectedRoute>
        <TRMainLayout>
          <ProspectsPage />
        </TRMainLayout>
      </ProtectedRoute>
    }
  />
  ```

### Step 12: Add Sidebar Navigation Item
- In `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`:
  - Import `BusinessIcon` from `@mui/icons-material/Business`
  - Add new nav item to `navigationItems` array before Settings:
    ```ts
    { label: 'Prospects', path: '/prospects', icon: <BusinessIcon /> }
    ```

### Step 13: Create E2E Test Spec
- Create `.claude/commands/e2e/test_prospect_kanban_board.md`
- Follow the pattern from `test_budget_management.md`
- User Story: "As a CRM user, I want to view and manage prospects on a Kanban board"
- Test Steps:
  1. Navigate to Application URL
  2. Screenshot initial state
  3. Verify home page with "Finance Tracker" heading and "Sign In" button
  4. Click "Sign In", enter test credentials, submit
  5. Screenshot after login
  6. Navigate to `/prospects`
  7. Screenshot prospects page
  8. Verify "Prospects" page title visible
  9. Verify "Add Prospect" button visible
  10. Verify Kanban board renders with pipeline stage columns (at least: Lead, Contacted, Qualified, Proposal, Negotiation, Won, Lost)
  11. Click "Add Prospect" button
  12. Screenshot add prospect form dialog
  13. Verify form fields: Company Name, Contact Name, Contact Email, Contact Phone, Stage, Estimated Value, Source, Notes
  14. Fill in: Company Name = "Test Corp", Contact Name = "John Doe", Contact Email = "john@test.com", Stage = "lead", Estimated Value = "50000", Source = "referral"
  15. Click Submit
  16. Screenshot after creation
  17. Verify prospect card "Test Corp" appears in the "Lead" column
  18. Verify card shows "John Doe" contact name
  19. Navigate away to /dashboard and back to /prospects
  20. Screenshot after navigation
  21. Verify "Test Corp" prospect still exists in Kanban board
- Success Criteria: Kanban board loads with columns, add prospect form works, prospect card appears in correct column, data persists

### Step 14: Run Validation Commands
- Run all validation commands to ensure zero regressions
- Fix any TypeScript errors, build errors, or test failures

## Testing Strategy
### Unit Tests
- No new unit test files needed for this wave (Wave 2 is frontend-only; backend tests already exist from Wave 1)
- TypeScript type checking serves as compile-time validation for all interfaces
- E2E test validates the full feature end-to-end

### Edge Cases
- Entity has no pipeline stages yet → usePipelineStages auto-seeds defaults
- Entity has no prospects → Kanban columns render empty with "No prospects" message
- Prospect has null estimated_value → TRProspectCard omits the value chip
- Prospect has null source → TRProspectCard omits the source chip
- User has no entity selected → ProspectsPage shows "Please select an entity" message
- API error during fetch → ProspectsPage shows Alert with error message
- Long company names → Text truncation with ellipsis in TRProspectCard
- Many prospects in one stage → Column scrolls vertically

## Acceptance Criteria
- Prospects page accessible at `/prospects` route
- Sidebar shows "Prospects" navigation item with Business icon
- Kanban board displays columns for all active pipeline stages (ordered by order_index)
- Each column header shows stage display_name, color indicator, and prospect count
- Prospect cards display company_name, contact_name, estimated_value (formatted), and source
- "Add Prospect" button opens a dialog with TRProspectForm
- Creating a prospect via the form adds the card to the correct column
- Editing a prospect via clicking the card opens TRProspectForm with pre-filled data
- All data is scoped to the current entity via useEntity()
- Pipeline stages are auto-seeded if entity has none
- Loading states display CircularProgress / Skeleton components
- Error states display Alert with error message
- Console logging follows `INFO [ComponentName]:` pattern
- All existing tests continue to pass (zero regressions)
- TypeScript compiles without errors
- Production build succeeds

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_prospect_kanban_board.md` E2E test to validate this functionality works
- `cd apps/Server && python -m pytest tests/ -v` — Run Server tests to validate zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate no type errors
- `cd apps/Client && npm run build` — Run Client production build to validate zero regressions

## Notes
- **Parallel execution**: This issue (CRM-008) runs in parallel with CRM-006 (useProspects hook, prospectService, types) and CRM-007 (TRProspectForm). Since those may not be merged yet, this plan includes creating all required files (types, services, hooks, form) as part of this implementation. If they already exist when implementation starts, skip the duplicate steps.
- **No drag-and-drop yet**: CRM-009 will add drag-and-drop to the Kanban board in a subsequent issue. This implementation focuses on the visual Kanban layout and CRUD via dialogs.
- **No prospect detail drawer yet**: CRM-010 will add a detail drawer. For now, clicking a prospect card opens the edit dialog.
- **Pipeline stage colors**: The backend seeds default stages with colors. If color is null, use a neutral default (theme.palette.grey[500]).
- **Currency formatting**: Use `Intl.NumberFormat` or similar for estimated_value display. Follow existing patterns from transaction amount formatting.
- **No new npm packages needed**: The Kanban board is built with standard MUI components (Box, Paper, Card, Chip, Stack) — no dedicated Kanban library required for this wave.
