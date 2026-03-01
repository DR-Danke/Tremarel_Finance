# Feature: Prospect Card Drag-and-Drop

## Metadata
issue_number: `55`
adw_id: `66325370`
issue_json: ``

## Feature Description
Add drag-and-drop functionality to the TRKanbanBoard component so that prospect cards can be moved between pipeline stage columns by dragging. When a card is dropped into a new column, the prospect's stage is updated via `PATCH /api/prospects/{id}/stage`. The UI applies optimistic updates so the card moves immediately, with automatic rollback if the API call fails.

## User Story
As a CRM user managing a sales pipeline
I want to drag prospect cards between stage columns on the Kanban board
So that I can quickly update deal stages without opening edit dialogs

## Problem Statement
Currently, the Kanban board displays prospect cards in their respective stage columns but provides no way to move them between stages without opening the edit dialog. This creates friction in the sales workflow — users need a fast, visual way to update deal progression by simply dragging cards across columns.

## Solution Statement
Integrate `@hello-pangea/dnd` (a maintained fork of react-beautiful-dnd) into the existing TRKanbanBoard, TRKanbanColumn, and TRProspectCard components. The DragDropContext wraps the board, each column becomes a Droppable, and each card becomes a Draggable. On drop, the page handler calls `updateProspectStage` from the `useProspects` hook with optimistic local state updates and rollback on API failure.

## Relevant Files
Use these files to implement the feature:

- `apps/Client/package.json` — Add `@hello-pangea/dnd` dependency
- `apps/Client/src/components/ui/TRKanbanBoard.tsx` — Wrap board with `DragDropContext`, accept `onDragEnd` prop
- `apps/Client/src/components/ui/TRKanbanColumn.tsx` — Make column a `Droppable` zone, wrap each card in `Draggable`
- `apps/Client/src/components/ui/TRProspectCard.tsx` — Accept and spread drag handle props onto the Card element
- `apps/Client/src/pages/ProspectsPage.tsx` — Implement `handleDragEnd` with optimistic update logic, pass to TRKanbanBoard
- `apps/Client/src/hooks/useProspects.ts` — Already has `updateProspectStage(id, data)` — used as-is, but will add `setProspects` export for optimistic local updates
- `apps/Client/src/services/prospectService.ts` — Already has `updateStage()` — no changes needed
- `apps/Client/src/types/index.ts` — Already has `ProspectStage`, `ProspectStageUpdate`, `PipelineStage`, `Prospect` types — no changes needed
- `apps/Server/src/adapter/rest/prospect_routes.py` — Backend PATCH `/api/prospects/{id}/stage` endpoint — no changes needed
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` to understand how to create E2E test files
- `app_docs/feature-aa2af2a8-prospect-service-hook-types.md` — Relevant conditional docs for prospect hook/types when implementing drag-and-drop
- `app_docs/feature-6835fdde-prospect-kanban-board.md` — Relevant conditional docs for Kanban board enhancements
- `.claude/commands/e2e/test_prospect_kanban_board.md` — Existing Kanban board E2E test for reference

### New Files
- `.claude/commands/e2e/test_prospect_card_drag_and_drop.md` — New E2E test file validating drag-and-drop functionality

## Implementation Plan
### Phase 1: Foundation
Install the `@hello-pangea/dnd` library and expose the optimistic state setter from `useProspects` hook so that drag-and-drop can update the UI immediately without waiting for the API response.

### Phase 2: Core Implementation
Modify TRKanbanBoard to wrap its content in `DragDropContext`. Update TRKanbanColumn to use `Droppable` with `droppableId` set to the stage name. Update TRProspectCard to accept drag props from the `Draggable` wrapper in TRKanbanColumn. Wire up `handleDragEnd` in ProspectsPage with optimistic update and rollback.

### Phase 3: Integration
Connect the drag-end handler to the existing `updateProspectStage` from `useProspects`. Ensure the optimistic update applies instantly, with rollback restoring the original position on failure. Validate via E2E test.

## Step by Step Tasks

### Step 1: Install @hello-pangea/dnd
- Run `cd apps/Client && npm install @hello-pangea/dnd` to add the drag-and-drop library
- Verify it's added to `package.json` dependencies

### Step 2: Create E2E test specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` for format reference
- Read `.claude/commands/e2e/test_prospect_kanban_board.md` for the existing Kanban test pattern
- Create `.claude/commands/e2e/test_prospect_card_drag_and_drop.md` with test steps that:
  1. Log in and navigate to `/prospects`
  2. Create a test prospect in the "Lead" column (if none exists)
  3. Drag a prospect card from one column (e.g., "Lead") to another (e.g., "Contacted")
  4. Verify the card now appears in the destination column
  5. Verify the API call `PATCH /api/prospects/{id}/stage` fires with `{ new_stage: "contacted" }`
  6. Refresh the page and verify the card persists in the new column
  7. Verify console shows expected INFO log messages

### Step 3: Expose optimistic state setter from useProspects hook
- In `apps/Client/src/hooks/useProspects.ts`:
  - Export `setProspects` in the return object so `ProspectsPage` can perform optimistic local updates
  - Add `setProspects` to the `UseProspectsResult` interface

### Step 4: Update TRProspectCard to accept drag props
- In `apps/Client/src/components/ui/TRProspectCard.tsx`:
  - Add optional `dragHandleProps` and `draggableProps` to `TRProspectCardProps` interface (typed as `DraggableProvidedDragHandleProps | null` and `DraggableProvidedDraggableProps`)
  - Spread `draggableProps` and `dragHandleProps` onto the outer `Card` element
  - Accept and forward an optional `innerRef` prop (React ref callback) onto the `Card` element

### Step 5: Update TRKanbanColumn to use Droppable and Draggable
- In `apps/Client/src/components/ui/TRKanbanColumn.tsx`:
  - Import `Droppable` and `Draggable` from `@hello-pangea/dnd`
  - Wrap the inner scrollable `Box` (that contains the Stack of cards) with `<Droppable droppableId={stage.name}>`
  - Use the `provided` render prop: apply `provided.droppableProps` and `provided.innerRef` to the container Box
  - Place `{provided.placeholder}` at the end inside the Droppable
  - Wrap each `TRProspectCard` in `<Draggable draggableId={prospect.id} index={index}>`
  - Pass `provided.draggableProps`, `provided.dragHandleProps`, and `provided.innerRef` to TRProspectCard
  - Keep the "No prospects" empty state inside the Droppable so it remains a valid drop target

### Step 6: Update TRKanbanBoard to use DragDropContext
- In `apps/Client/src/components/ui/TRKanbanBoard.tsx`:
  - Import `DragDropContext` and `DropResult` from `@hello-pangea/dnd`
  - Add `onDragEnd?: (result: DropResult) => void` to `TRKanbanBoardProps`
  - Wrap the `Box` containing columns with `<DragDropContext onDragEnd={onDragEnd || (() => {})}>`

### Step 7: Implement handleDragEnd in ProspectsPage with optimistic updates
- In `apps/Client/src/pages/ProspectsPage.tsx`:
  - Import `DropResult` from `@hello-pangea/dnd`
  - Import `ProspectStage` from `@/types`
  - Destructure `updateProspectStage` and `setProspects` from `useProspects`
  - Implement `handleDragEnd(result: DropResult)`:
    1. Return early if no `result.destination` or if source equals destination
    2. Extract `prospectId` from `result.draggableId`
    3. Extract `newStage` from `result.destination.droppableId` (cast as `ProspectStage`)
    4. Save the current `prospects` array for rollback
    5. Optimistically update local state: `setProspects(prev => prev.map(p => p.id === prospectId ? { ...p, stage: newStage } : p))`
    6. Call `updateProspectStage(prospectId, { new_stage: newStage })` in a try/catch
    7. On catch: rollback with `setProspects(savedProspects)`, log the error, set an operation error message
  - Pass `handleDragEnd` to `<TRKanbanBoard onDragEnd={handleDragEnd} />`
  - Add console.log for drag operations: `INFO [ProspectsPage]: Dragging prospect {id} from {source} to {destination}`

### Step 8: Validate with tests and build
- Run `cd apps/Server && python -m pytest tests/` to ensure no backend regressions
- Run `cd apps/Client && npx tsc --noEmit` to validate TypeScript types
- Run `cd apps/Client && npm run build` to validate production build
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_prospect_card_drag_and_drop.md` to validate drag-and-drop E2E

## Testing Strategy
### Unit Tests
- No new unit test files required — the feature wires together existing tested components (useProspects hook, prospectService) with library code (@hello-pangea/dnd)
- The `handleDragEnd` logic in ProspectsPage is an event handler best validated via E2E tests
- Existing backend tests for `PATCH /api/prospects/{id}/stage` remain unchanged

### Edge Cases
- Dropping a card back to its original column (same source and destination) — should no-op
- Dropping outside a valid droppable zone (null destination) — should no-op
- API failure on stage update — should rollback the card to its original column and show error alert
- Dragging when board is loading — loading skeleton doesn't render Droppables, so DnD is implicitly disabled
- Dragging a card within the same column (reordering) — treated as no-op since ordering within a stage is not persisted

## Acceptance Criteria
- Prospect cards can be dragged from one pipeline stage column to another
- On drop, the card moves immediately to the destination column (optimistic update)
- A `PATCH /api/prospects/{id}/stage` API call fires with the new stage
- If the API call fails, the card rolls back to its original column and an error alert is displayed
- Dropping a card on the same column produces no API call
- Dropping outside a valid zone produces no effect
- Console shows `INFO [ProspectsPage]: Dragging prospect...` log messages
- TypeScript compiles with no errors
- Production build succeeds
- Existing backend tests pass without regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npm install @hello-pangea/dnd` — Install DnD dependency (idempotent)
- `cd apps/Server && python -m pytest tests/` — Run Server tests to validate no regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate no type errors
- `cd apps/Client && npm run build` — Run Client build to validate production build succeeds
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_prospect_card_drag_and_drop.md` to validate drag-and-drop functionality works E2E

## Notes
- `@hello-pangea/dnd` is the maintained community fork of `react-beautiful-dnd` (by Atlassian, now deprecated). It supports React 18+ and has active maintenance.
- The backend already fully supports stage transitions via `PATCH /api/prospects/{id}/stage` including audit trail via `StageTransition` records — no backend changes needed.
- The `useProspects` hook already has `updateProspectStage` that calls the API and refetches. The optimistic update in ProspectsPage provides instant UI feedback while the hook handles the server sync.
- Within-column reordering is intentionally not persisted (no `order` field on prospects). Cards within a column maintain their server-side order.
- New dependency: `@hello-pangea/dnd` — install via `cd apps/Client && npm install @hello-pangea/dnd`
