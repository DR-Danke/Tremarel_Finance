# Prospect Detail Drawer with Meeting History

**ADW ID:** 17480a03
**Date:** 2026-03-01
**Specification:** specs/issue-56-adw-17480a03-sdlc_planner-prospect-detail-meeting-history.md

## Overview

Adds a right-anchored detail drawer to the CRM Kanban board that slides open when a user clicks a prospect card. The drawer displays three sections: prospect information header, stage transition history timeline, and chronological meeting history with HTML download support.

## What Was Built

- `TRProspectDetailDrawer` component with prospect info, stage history timeline, and meeting history
- `StageTransition` and `StageTransitionListResponse` TypeScript types
- `getTransitions()` method in `pipelineStageService` to fetch stage transition history
- Integration into `ProspectsPage` so card click opens the detail drawer while edit remains via the menu
- E2E test specification for the drawer feature

## Technical Implementation

### Files Modified

- `apps/Client/src/types/index.ts`: Added `StageTransition` and `StageTransitionListResponse` interfaces
- `apps/Client/src/services/pipelineStageService.ts`: Added `getTransitions(prospectId, entityId)` method calling `GET /api/pipeline-stages/transitions/{prospectId}`
- `apps/Client/src/components/ui/TRProspectDetailDrawer.tsx`: New 381-line component with three-section detail drawer
- `apps/Client/src/pages/ProspectsPage.tsx`: Added drawer state, rewired `onProspectClick` to open drawer, kept `onProspectEdit` for edit dialog
- `.claude/commands/e2e/test_prospect_detail_meeting_history.md`: E2E test specification

### Key Changes

- **Card click behavior changed**: Clicking a prospect card now opens the detail drawer instead of the edit dialog. The edit dialog is still accessible via the card's edit action or the drawer's edit button.
- **Stage transition resolution**: Stage UUIDs (`from_stage_id`, `to_stage_id`) are resolved to display names using the `stages` prop, with "Unknown" fallback for deleted or missing stages.
- **Meeting HTML download**: Uses Blob + `URL.createObjectURL` pattern to trigger browser file download of meeting HTML output.
- **Conditional data fetching**: Transitions fetch only when the drawer is open and a prospect is selected. Meeting records use the existing `useMeetingRecords` hook with `entityId` gated by `open` state.
- **Edit from drawer**: An edit button in the drawer header closes the drawer and opens the existing edit dialog for the selected prospect.

## How to Use

1. Navigate to the Prospects page (`/prospects`)
2. Click any prospect card on the Kanban board to open the detail drawer on the right side
3. View prospect information (company name, contact details, stage, estimated value, source, notes)
4. Scroll down to see the stage history timeline showing how the prospect moved through pipeline stages
5. Continue scrolling to see meeting history with title, date, and summary for each meeting
6. Click the download icon on a meeting entry to download the formatted HTML output
7. Click the edit (pencil) icon in the drawer header to open the edit dialog
8. Click the X button or click outside the drawer to close it
9. Use the three-dot menu or edit icon on the prospect card to directly open the edit dialog (bypassing the drawer)

## Configuration

No additional configuration required. The feature uses existing backend endpoints:
- `GET /api/pipeline-stages/transitions/{prospect_id}?entity_id={entity_id}` for stage transitions
- `GET /api/meeting-records/?prospect_id={prospect_id}&entity_id={entity_id}` for meetings
- `GET /api/meeting-records/{id}/html?entity_id={entity_id}` for HTML download

## Testing

Run the E2E test for this feature:
```bash
# Read and execute the E2E test spec
# .claude/commands/e2e/test_prospect_detail_meeting_history.md
```

Validation commands:
```bash
cd apps/Server && python -m pytest tests/ -v
cd apps/Client && npx tsc --noEmit
cd apps/Client && npm run build
```

## Notes

- No backend changes were required; all API endpoints existed prior to this feature
- The drawer width is 520px with `maxWidth: 100vw` for mobile responsiveness
- Meeting summaries are truncated to 3 lines with CSS `-webkit-line-clamp`
- Participants are parsed from JSON strings with safe fallback to empty array
- Meetings are sorted by `meeting_date` descending, with `created_at` as fallback
- Future Wave 3 transcript pipeline will automatically populate meetings visible in this drawer
