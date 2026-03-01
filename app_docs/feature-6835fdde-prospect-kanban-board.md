# Prospect Kanban Board Page

**ADW ID:** 6835fdde
**Date:** 2026-03-01
**Specification:** specs/issue-54-adw-6835fdde-sdlc_planner-prospect-kanban-board-page.md

## Overview

The Prospect Kanban Board is a visual CRM pipeline management page that displays prospects organized into columns by pipeline stage (Lead, Contacted, Qualified, Proposal, Negotiation, Won, Lost). Users can create and edit prospects through dialog forms, with all data scoped to the current entity. This is Wave 2 of the CRM Pipeline frontend, building on the Wave 1 backend API.

## What Was Built

- **ProspectsPage** — Main page at `/prospects` with Kanban board layout, CRUD dialogs, entity scoping, and loading/error states
- **TRKanbanBoard** — Horizontal scrolling container that groups prospects by stage and renders columns with skeleton loading
- **TRKanbanColumn** — Single pipeline stage column with colored header, prospect count badge, and scrollable card list
- **TRProspectCard** — Compact prospect card showing company name, contact name, estimated value (USD formatted), source, and creation date
- **TRProspectForm** — react-hook-form based create/edit form with fields for company name, contact info, stage selector, estimated value, source, and notes
- **prospectService** — API service for prospect CRUD operations (list, get, create, update, updateStage, delete)
- **pipelineStageService** — API service for pipeline stage listing and default seeding
- **useProspects hook** — State management for prospect data with CRUD operations and filter support
- **usePipelineStages hook** — Stage loading with auto-seed when no stages exist for an entity
- **TypeScript types** — Prospect, ProspectCreate, ProspectUpdate, ProspectFilters, PipelineStage, and related interfaces
- **Sidebar navigation** — "Prospects" item with Business icon added to TRCollapsibleSidebar
- **Route** — `/prospects` protected route with TRMainLayout wrapper in App.tsx
- **E2E test spec** — test_prospect_kanban_board.md for end-to-end validation

## Technical Implementation

### Files Modified

- `apps/Client/src/types/index.ts`: Added ProspectStage, Prospect, ProspectCreate, ProspectUpdate, ProspectListResponse, ProspectFilters, PipelineStage, and PipelineStageListResponse interfaces (+73 lines)
- `apps/Client/src/App.tsx`: Added `/prospects` route with ProtectedRoute and TRMainLayout (+11 lines)
- `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`: Added BusinessIcon import and "Prospects" navigation item (+2 lines)

### New Files Created

- `apps/Client/src/services/prospectService.ts` (128 lines): Full CRUD service with list (filters, pagination), get, create, update, updateStage (PATCH), and delete methods
- `apps/Client/src/services/pipelineStageService.ts` (48 lines): Pipeline stage list and seed defaults service
- `apps/Client/src/hooks/useProspects.ts` (148 lines): Prospect state management hook with auto-fetch on entity/filter change, CRUD callbacks, and error handling
- `apps/Client/src/hooks/usePipelineStages.ts` (65 lines): Pipeline stage hook with auto-seed logic when no stages exist
- `apps/Client/src/components/ui/TRKanbanBoard.tsx` (65 lines): Board layout with useMemo grouping, skeleton loading, and sorted columns
- `apps/Client/src/components/ui/TRKanbanColumn.tsx` (94 lines): Column with colored left border header, count chip, "No prospects" empty state, and scrollable card stack
- `apps/Client/src/components/ui/TRProspectCard.tsx` (102 lines): Card with currency formatting (Intl.NumberFormat), date formatting, hover elevation, text truncation
- `apps/Client/src/components/forms/TRProspectForm.tsx` (274 lines): Form with react-hook-form, Controller for stage Select, email pattern validation, currency input with $ adornment, edit mode with reset
- `apps/Client/src/pages/ProspectsPage.tsx` (225 lines): Page with entity guard, add/edit dialogs, error alerts, CircularProgress loading
- `.claude/commands/e2e/test_prospect_kanban_board.md` (113 lines): E2E test specification

### Key Changes

- **Kanban grouping**: TRKanbanBoard uses `useMemo` to create a `Map<string, Prospect[]>` grouping prospects by stage name, ensuring efficient re-rendering
- **Auto-seeding**: usePipelineStages automatically seeds default pipeline stages when an entity has none, then re-fetches to display them
- **Entity scoping**: All API calls pass `entity_id` as query parameter; ProspectsPage guards against no entity selected with a redirect to entities page
- **Form dual-mode**: TRProspectForm supports both create (with entity_id) and edit (pre-filled via reset) modes through the `initialData` prop
- **Currency display**: TRProspectCard formats estimated_value with `Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })` with no decimal places

## How to Use

1. Log in to the application and select an entity
2. Click "Prospects" in the sidebar navigation to navigate to `/prospects`
3. The Kanban board loads with pipeline stage columns (auto-seeded on first visit)
4. Click "Add Prospect" to open the creation dialog
5. Fill in company name (required), contact details, stage, estimated value, source, and notes
6. Submit the form to create the prospect — it appears in the corresponding stage column
7. Click any prospect card to open the edit dialog with pre-filled data
8. Modify fields and submit to update the prospect

## Configuration

No additional configuration is required. The feature uses existing:
- `VITE_API_URL` environment variable for API base URL
- JWT authentication via the existing API client interceptor
- Entity context for multi-entity scoping

### Backend API Endpoints Used

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/prospects/` | List prospects with filters |
| GET | `/api/prospects/{id}` | Get single prospect |
| POST | `/api/prospects/` | Create prospect |
| PUT | `/api/prospects/{id}` | Update prospect |
| PATCH | `/api/prospects/{id}/stage` | Update prospect stage |
| DELETE | `/api/prospects/{id}` | Delete prospect |
| GET | `/api/pipeline-stages/` | List pipeline stages |
| POST | `/api/pipeline-stages/seed` | Seed default stages |

## Testing

- **E2E test**: Run the prospect Kanban board E2E test via `.claude/commands/e2e/test_prospect_kanban_board.md`
- **Type check**: `cd apps/Client && npx tsc --noEmit`
- **Build**: `cd apps/Client && npm run build`
- **Backend tests**: `cd apps/Server && python -m pytest tests/ -v`

## Notes

- **No drag-and-drop**: This wave focuses on visual layout and CRUD via dialogs. Drag-and-drop stage changes are planned for CRM-009.
- **No prospect detail drawer**: Clicking a card opens the edit dialog. A detail drawer is planned for CRM-010.
- **Pipeline stage colors**: Default stages come with pre-assigned colors from the backend seed. If color is null, the column uses grey (#9e9e9e).
- **Column dimensions**: Each column is fixed at 280px width with max height `calc(100vh - 220px)` and vertical scrolling for overflow.
- **Built with standard MUI**: No additional npm packages required — uses Box, Paper, Card, Chip, Stack, Dialog, and Select components.
