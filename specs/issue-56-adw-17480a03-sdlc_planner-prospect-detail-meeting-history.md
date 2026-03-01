# Feature: Prospect Detail Drawer with Meeting History

## Metadata
issue_number: `56`
adw_id: `17480a03`
issue_json: ``

## Feature Description
When a user clicks a prospect card on the CRM Kanban board, a right-anchored detail drawer slides open showing three sections: (1) prospect information header with company name, contact details, stage badge, estimated value, source, and notes; (2) a stage transition history timeline showing how the prospect has moved through pipeline stages chronologically; and (3) a chronological list of meetings with structured summaries, where each meeting entry includes a download button for the formatted HTML output. This is Wave 2, Issue CRM-010 of the CRM Pipeline feature set.

## User Story
As a CRM user managing prospects
I want to click a prospect card and see its full details, stage history, and meeting records in a slide-out drawer
So that I can quickly review a prospect's progression and meeting history without leaving the Kanban board

## Problem Statement
Currently, clicking a prospect card on the Kanban board opens an edit dialog. There is no way for users to view a prospect's stage transition history or meeting records. Users need a read-focused detail view that aggregates prospect info, stage history, and meetings in one place to make informed decisions about next steps.

## Solution Statement
Create a `TRProspectDetailDrawer` component that renders as a right-anchored MUI Drawer (~520px wide). The drawer fetches stage transitions via a new `pipelineStageService.getTransitions()` method and meeting records via the existing `useMeetingRecords` hook. Stage transitions are displayed as a timeline, meetings as a chronological list with download buttons. The `ProspectsPage` is updated so `onProspectClick` opens the drawer, while `onProspectEdit` retains the existing edit dialog behavior.

## Relevant Files
Use these files to implement the feature:

**Types & Interfaces:**
- `apps/Client/src/types/index.ts` — Add `StageTransition` and `StageTransitionListResponse` TypeScript interfaces to match the backend `StageTransitionResponseDTO` and `StageTransitionListResponseDTO`. Existing `Prospect`, `MeetingRecord`, `PipelineStage` types are already defined here.

**Services:**
- `apps/Client/src/services/pipelineStageService.ts` — Add `getTransitions(prospectId, entityId)` method that calls `GET /api/pipeline-stages/transitions/{prospectId}?entity_id={entityId}`. Currently only has `list` and `seedDefaults`.
- `apps/Client/src/services/meetingRecordService.ts` — Already has `list(entityId, filters)` and `getHtml(recordId, entityId)` methods. No changes needed.

**Hooks:**
- `apps/Client/src/hooks/useMeetingRecords.ts` — Existing hook that accepts `prospectId` param to filter meetings. Will be used inside the drawer.
- `apps/Client/src/hooks/usePipelineStages.ts` — Existing hook for loading pipeline stages. Already used in ProspectsPage.

**Components:**
- `apps/Client/src/components/ui/TRKanbanBoard.tsx` — Has `onProspectClick` prop already wired through columns/cards. No changes needed.
- `apps/Client/src/components/ui/TRProspectCard.tsx` — Handles click → calls `onClick(prospect)`. No changes needed.

**Pages:**
- `apps/Client/src/pages/ProspectsPage.tsx` — Must add drawer state (`isDetailDrawerOpen`, `detailProspect`), change `onProspectClick` to open the drawer, import and render `TRProspectDetailDrawer`.

**Backend (reference only, no changes needed):**
- `apps/Server/src/adapter/rest/pipeline_stage_routes.py` — `GET /api/pipeline-stages/transitions/{prospect_id}` endpoint already exists.
- `apps/Server/src/adapter/rest/meeting_record_routes.py` — `GET /api/meeting-records/` with `prospect_id` filter and `GET /api/meeting-records/{id}/html` endpoints already exist.
- `apps/Server/src/interface/stage_transition_dto.py` — Backend DTO structure to mirror in TypeScript types.

**Documentation (read for context):**
- `app_docs/feature-aa2af2a8-prospect-service-hook-types.md` — CRM frontend data layer docs
- `app_docs/feature-6835fdde-prospect-kanban-board.md` — Kanban board implementation docs
- `app_docs/feature-d1b26544-meeting-record-api-endpoints.md` — Meeting record API docs
- `app_docs/feature-eb19b5cd-pipeline-stage-configuration.md` — Pipeline stages & transitions docs

**E2E Test References:**
- `.claude/commands/test_e2e.md` — Read to understand how to create and run E2E tests
- `.claude/commands/e2e/test_basic_query.md` — Read as an E2E test template example
- `.claude/commands/e2e/test_prospect_kanban_board.md` — Read as the closest existing E2E test for the Prospects feature

### New Files
- `apps/Client/src/components/ui/TRProspectDetailDrawer.tsx` — The main detail drawer component
- `.claude/commands/e2e/test_prospect_detail_meeting_history.md` — E2E test spec for validating the drawer feature

## Implementation Plan
### Phase 1: Foundation
Add the `StageTransition` and `StageTransitionListResponse` TypeScript interfaces to `types/index.ts`, matching the backend `StageTransitionResponseDTO` fields. Add the `getTransitions()` method to `pipelineStageService.ts` to fetch stage transition history from the existing backend endpoint.

### Phase 2: Core Implementation
Create the `TRProspectDetailDrawer` component with three sections:
1. **Prospect Info Header** — Company name, contact details (name, email, phone), current stage as a colored `Chip`, estimated value formatted as currency, source, and notes.
2. **Stage History Timeline** — Fetch transitions via `pipelineStageService.getTransitions()`, resolve `from_stage_id`/`to_stage_id` UUIDs to display names using the `stages` prop, render as a vertical timeline using MUI `Timeline` (from `@mui/lab`) or a simple styled list with date, from→to stage names, and optional notes.
3. **Meeting History List** — Use `useMeetingRecords(entityId, prospect.id)` hook to fetch meetings. Display each meeting as a card/list item with title, meeting date, summary text, and a download button that calls `meetingRecordService.getHtml()` and triggers a browser file download.

### Phase 3: Integration
Update `ProspectsPage` to:
- Add `isDetailDrawerOpen` and `detailProspect` state
- Wire `onProspectClick` on `TRKanbanBoard` to open the drawer (instead of edit dialog)
- Keep `onProspectEdit` on `TRKanbanBoard` wired to the existing edit dialog
- Render `TRProspectDetailDrawer` with the selected prospect, passing `stages` from `usePipelineStages`
- Add an "Edit" button inside the drawer header that opens the existing edit dialog for the currently viewed prospect

## Step by Step Tasks

### Step 1: Create E2E Test Spec
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` to understand the E2E test format
- Read `.claude/commands/e2e/test_prospect_kanban_board.md` as the closest existing E2E reference
- Create `.claude/commands/e2e/test_prospect_detail_meeting_history.md` with steps to:
  1. Log in and navigate to `/prospects`
  2. Ensure a prospect exists (create one if needed)
  3. Click a prospect card on the Kanban board
  4. Verify the detail drawer opens on the right side
  5. Verify prospect info section shows company name, contact details, stage chip
  6. Verify stage history section is visible (may be empty if no transitions)
  7. Verify meeting history section is visible (may show empty state)
  8. Verify the drawer can be closed
  9. Take screenshots at each verification step

### Step 2: Add TypeScript Types for Stage Transitions
- Edit `apps/Client/src/types/index.ts`
- Add after the `PipelineStageListResponse` interface:
  ```typescript
  export interface StageTransition {
    id: string
    prospect_id: string
    entity_id: string
    from_stage_id: string | null
    to_stage_id: string
    transitioned_by: string | null
    notes: string | null
    created_at: string
  }

  export interface StageTransitionListResponse {
    transitions: StageTransition[]
    total: number
  }
  ```

### Step 3: Add getTransitions to pipelineStageService
- Edit `apps/Client/src/services/pipelineStageService.ts`
- Import `StageTransitionListResponse` from `@/types`
- Add a `getTransitions(prospectId: string, entityId: string)` method that:
  - Calls `GET /api/pipeline-stages/transitions/{prospectId}?entity_id={entityId}`
  - Returns `StageTransitionListResponse`
  - Follows existing logging patterns (`INFO [PipelineStageService]: ...`)

### Step 4: Create TRProspectDetailDrawer Component
- Create `apps/Client/src/components/ui/TRProspectDetailDrawer.tsx`
- Define `TRProspectDetailDrawerProps` interface:
  ```typescript
  interface TRProspectDetailDrawerProps {
    prospect: Prospect | null
    open: boolean
    onClose: () => void
    onEdit: (prospect: Prospect) => void
    entityId: string
    stages: PipelineStage[]
  }
  ```
- Use MUI `Drawer` with `anchor="right"` and paper width ~520px
- **Drawer Header**: Prospect company name as title, close button (X icon), edit button (Edit icon)
- **Prospect Info Section** (Box):
  - Company name (Typography variant h6)
  - Current stage as colored `Chip` (resolve color from `stages` prop)
  - Contact details: name, email (mailto link), phone
  - Estimated value formatted as currency (if present)
  - Source and notes (if present)
  - Use `Divider` to separate sections
- **Stage History Section** (Box with "Stage History" subheader):
  - Fetch transitions via `pipelineStageService.getTransitions(prospect.id, entityId)` in a `useEffect` (when `prospect` changes and `open` is true)
  - Create a helper function to resolve stage UUID → display_name using the `stages` prop, with fallback to "Unknown"
  - For initial assignment (`from_stage_id === null`), show "→ {to_stage_name}" with "Initial" label
  - For transitions, show "{from_stage_name} → {to_stage_name}" with formatted date
  - Show notes if present
  - Handle loading state with `CircularProgress`
  - Handle empty state with "No stage transitions yet" message
- **Meeting History Section** (Box with "Meeting History" subheader):
  - Use `useMeetingRecords(entityId, prospect.id)` hook
  - Display each meeting as a `Paper`/`Card` item with:
    - Title (Typography variant subtitle1)
    - Meeting date formatted (or "Date not set")
    - Summary text truncated to ~3 lines with "show more" if needed
    - Download HTML button (Download icon) that:
      - Calls `meetingRecordService.getHtml(meeting.id, entityId)`
      - Creates a Blob and triggers browser download as `{title}.html`
    - Show participants if available (parse JSON string)
  - Handle loading state with `CircularProgress`
  - Handle empty state with "No meetings recorded yet" message
  - Sort by `meeting_date` descending (newest first), fallback to `created_at`
- Add console logging following project standards

### Step 5: Update ProspectsPage to Integrate the Drawer
- Edit `apps/Client/src/pages/ProspectsPage.tsx`
- Add state: `const [isDetailDrawerOpen, setIsDetailDrawerOpen] = useState(false)` and `const [detailProspect, setDetailProspect] = useState<Prospect | null>(null)`
- Create `handleProspectCardClick` that sets `detailProspect` and opens the drawer
- Create `handleCloseDetailDrawer` that closes the drawer and clears the prospect
- Create `handleEditFromDrawer` that closes the drawer and opens the edit dialog for the prospect
- Change `onProspectClick={handleProspectClick}` to `onProspectClick={handleProspectCardClick}` on `TRKanbanBoard`
- Keep `onProspectEdit={handleProspectClick}` (existing edit behavior via the three-dot menu or card edit icon)
- Import and render `TRProspectDetailDrawer` below the existing dialogs:
  ```tsx
  <TRProspectDetailDrawer
    prospect={detailProspect}
    open={isDetailDrawerOpen}
    onClose={handleCloseDetailDrawer}
    onEdit={handleEditFromDrawer}
    entityId={currentEntity.id}
    stages={stages}
  />
  ```

### Step 6: Run Validation Commands
- Run backend tests: `cd apps/Server && python -m pytest tests/ -v`
- Run frontend type check: `cd apps/Client && npx tsc --noEmit`
- Run frontend build: `cd apps/Client && npm run build`
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_prospect_detail_meeting_history.md` E2E test to validate this functionality works

## Testing Strategy
### Unit Tests
- No new unit test files required for this feature since the backend APIs are already tested and the frontend implementation is primarily UI composition using existing hooks and services
- The E2E test validates the full integration

### Edge Cases
- Prospect with no stage transitions (empty timeline) — show "No stage transitions yet"
- Prospect with no meetings (empty meeting list) — show "No meetings recorded yet"
- Meeting record with no `html_output` — disable or hide the download button
- Meeting record with no `meeting_date` — display "Date not set"
- Meeting record with `action_items` / `participants` as JSON strings — parse safely with try/catch
- Stage transition with `from_stage_id` or `to_stage_id` not found in current stages — show "Unknown" fallback
- Rapid clicking different prospect cards — ensure drawer updates to latest clicked prospect
- Drawer opened while stages are still loading — show loading indicator

## Acceptance Criteria
- Clicking a prospect card on the Kanban board opens a right-side detail drawer
- The drawer displays the prospect's company name, contact info, current stage (as colored chip), estimated value, source, and notes
- The drawer shows a stage transition history section with chronological transitions showing from→to stage names and dates
- The drawer shows a meeting history section with a list of meetings showing title, date, and summary
- Each meeting entry has a download button that downloads the HTML output as a file
- The drawer has a close button and an edit button that opens the existing edit dialog
- The drawer handles empty states gracefully (no transitions, no meetings)
- The existing edit dialog still works via the `onProspectEdit` prop (three-dot menu / edit icon on card)
- No TypeScript errors, build succeeds, backend tests pass

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/ -v` — Run Server tests to validate the feature works with zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate the feature works with zero regressions
- `cd apps/Client && npm run build` — Run Client build to validate the feature works with zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_prospect_detail_meeting_history.md` E2E test to validate this functionality works

## Notes
- **No backend changes required** — All needed API endpoints already exist: `GET /api/pipeline-stages/transitions/{prospect_id}`, `GET /api/meeting-records/` with `prospect_id` filter, `GET /api/meeting-records/{id}/html`
- **MUI Lab Timeline** — Consider using `@mui/lab` Timeline components for the stage history if already installed; otherwise, a simple styled list with left-border timeline effect is sufficient and avoids adding a dependency
- **HTML Download** — The download button creates a Blob from the HTML string returned by `getHtml()` and uses `URL.createObjectURL` + anchor click pattern for browser download
- **Wave 3 Integration** — Wave 3 (transcript pipeline) will create meeting records that automatically appear in this detail view since it uses the same `meeting_records` API
- **Future Enhancement** — Action items could be rendered as a checklist; participants could show avatars. These are out of scope for this issue.
