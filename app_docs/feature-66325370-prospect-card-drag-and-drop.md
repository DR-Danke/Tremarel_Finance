# Prospect Card Drag-and-Drop

**ADW ID:** 66325370
**Date:** 2026-03-01
**Specification:** specs/issue-55-adw-66325370-sdlc_planner-prospect-card-drag-and-drop.md

## Overview

Adds drag-and-drop functionality to the CRM Kanban board, allowing users to move prospect cards between pipeline stage columns by dragging. The UI applies optimistic updates so the card moves immediately, with automatic rollback if the backend API call fails.

## What Was Built

- Drag-and-drop support on the Kanban board using `@hello-pangea/dnd`
- `DragDropContext` wrapping the board, `Droppable` columns, and `Draggable` cards
- Optimistic stage updates with automatic rollback on API failure
- Exposed `setProspects` setter from `useProspects` hook for local state manipulation

## Technical Implementation

### Files Modified

- `apps/Client/package.json`: Added `@hello-pangea/dnd` dependency (maintained fork of react-beautiful-dnd)
- `apps/Client/src/components/ui/TRKanbanBoard.tsx`: Wrapped board content in `DragDropContext`, added `onDragEnd` prop
- `apps/Client/src/components/ui/TRKanbanColumn.tsx`: Made each column a `Droppable` zone, wrapped each card in a `Draggable`
- `apps/Client/src/components/ui/TRProspectCard.tsx`: Accepts `draggableProps`, `dragHandleProps`, and `innerRef` for drag integration
- `apps/Client/src/hooks/useProspects.ts`: Exported `setProspects` state setter for optimistic updates
- `apps/Client/src/pages/ProspectsPage.tsx`: Implemented `handleDragEnd` with optimistic update and rollback logic

### Key Changes

- **DragDropContext** in `TRKanbanBoard` receives the `onDragEnd` callback from the parent page
- **Droppable** zones use `stage.name` as the `droppableId`, mapping directly to `ProspectStage` values
- **Draggable** cards use `prospect.id` as the `draggableId` for unique identification
- **Optimistic updates**: `handleDragEnd` saves the current prospects array, immediately updates local state via `setProspects`, then calls `updateProspectStage`. On failure, the saved array is restored
- **No-op guards**: Drops to the same column or outside valid zones are ignored without API calls

### Architecture

```
ProspectsPage (handleDragEnd)
  └─ TRKanbanBoard (DragDropContext, onDragEnd)
       └─ TRKanbanColumn (Droppable, droppableId=stage.name)
            └─ Draggable (draggableId=prospect.id)
                 └─ TRProspectCard (innerRef, draggableProps, dragHandleProps)
```

## How to Use

1. Navigate to the **Prospects** page (`/prospects`)
2. The Kanban board displays prospect cards grouped by pipeline stage columns
3. Click and hold any prospect card to begin dragging
4. Drag the card to a different stage column and release to drop
5. The card moves immediately to the new column (optimistic update)
6. If the backend update fails, the card automatically returns to its original column and an error message appears

## Configuration

No additional configuration required. The feature uses the existing `PATCH /api/prospects/{id}/stage` backend endpoint.

### Dependency

- `@hello-pangea/dnd` — Maintained community fork of `react-beautiful-dnd` (Atlassian, deprecated). Supports React 18+.

## Testing

- **TypeScript**: `cd apps/Client && npx tsc --noEmit`
- **Build**: `cd apps/Client && npm run build`
- **Backend regression**: `cd apps/Server && python -m pytest tests/`
- **E2E**: Run the `test_prospect_card_drag_and_drop` E2E test to validate drag-and-drop functionality

## Notes

- Within-column reordering is intentionally not persisted (no `order` field on prospects). Cards within a column maintain server-side order.
- The backend already tracks stage transitions via `StageTransition` records for audit trail purposes — no backend changes were needed.
- The `useProspects` hook's `updateProspectStage` handles server sync and refetch after the optimistic update settles.
