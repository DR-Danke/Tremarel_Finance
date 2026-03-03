# Bug: Prospects disappearing from CRM pipeline after login

## Metadata
issue_number: `I`
adw_id: `had`
issue_json: `two`

## Bug Description
The user previously had two prospects (ASV Corp and Faroo Legal) visible on the CRM Kanban pipeline board. After logging out and back in, the Prospects page shows zero prospects — both cards have vanished from the board. No error message is displayed; the board simply appears empty. The expected behavior is that all previously created prospects persist and are visible on the Kanban board across login sessions.

## Problem Statement
Prospects that were previously visible on the CRM Kanban board are silently disappearing between sessions. The user sees an empty pipeline with no error feedback, making it impossible to determine whether the data was lost, filtered out, or simply not displayed due to wrong entity selection.

## Solution Statement
1. **Fix the entity context** so the ProspectsPage makes it obvious which entity is selected and makes switching easy when no prospects are found.
2. **Fix the Kanban board** to never silently drop prospects — if a prospect's stage doesn't match any pipeline stage column, it must still be visible.
3. **Improve empty state feedback** so the user can distinguish "no prospects exist" from "wrong entity selected."
4. **Harden the pipeline stages hook** to surface auto-seed failures instead of swallowing them silently.

## Steps to Reproduce
1. Have two entities: "Tremarel" (family, no prospects) and "KAI Partners" (startup, has prospects)
2. Log out or clear browser localStorage
3. Log in to the Finance Tracker application
4. Navigate to the Prospects page (/prospects)
5. Observe that EntityContext defaults to "Tremarel" (first entity alphabetically)
6. The Kanban board shows zero prospect cards because "Tremarel" has none
7. The prospects (ASV Corp, Faroo Legal) exist in "KAI Partners" but the user is looking at the wrong entity

## Root Cause Analysis

### Verified Facts (from live API diagnosis)
- **Database**: All 3 prospect records exist with `is_active=true` in entity `f1ae369a-38ae-4ec1-8d9e-4edadf46518c` (KAI Partners)
- **API**: `GET /api/prospects/?entity_id=f1ae369a...` returns all 3 prospects correctly (ASV Corp, 2x Faroo Legal)
- **Pipeline stages**: All 7 stages exist and are active for KAI Partners
- **Two entities exist**: `Tremarel` (`649eb405...`, type: family) and `KAI Partners` (`f1ae369a...`, type: startup)
- **Entity order**: API returns `Tremarel` first, `KAI Partners` second

### Root Cause 1: EntityContext defaults to wrong entity (PRIMARY)
In `apps/Client/src/contexts/EntityContext.tsx` (lines 38-54), when `currentEntityId` is not found in localStorage (new session, cleared cache, different device), the EntityContext falls back to `userEntities[0]` — which is `Tremarel`. Since `Tremarel` has zero prospects, the Kanban board appears empty. The user sees "Managing prospects for: **Tremarel**" but may not realize they need to switch entities. The entity selector is in the collapsed sidebar, making it easy to miss.

### Root Cause 2: TRKanbanBoard silently drops unmatched prospects (DEFENSIVE)
In `apps/Client/src/components/ui/TRKanbanBoard.tsx` (lines 24-36), the `prospectsByStage` memo builds a map keyed by `stage.name`, then matches prospects by `prospect.stage`. If a prospect's stage doesn't match ANY pipeline stage name, the prospect is **silently discarded** — no warning, no fallback. While this is not the primary cause here (stages and prospect stages do match for KAI Partners), it's a latent bug that could cause the same symptom in the future.

### Root Cause 3: No actionable empty state
The ProspectsPage shows empty Kanban columns with no indication of whether the user should switch entities, add prospects, or investigate an error. For a multi-entity user, this is confusing.

## Relevant Files
Use these files to fix the bug:

**Frontend (primary fix targets)**
- `apps/Client/src/pages/ProspectsPage.tsx` — Main page component; needs improved empty state with entity-aware messaging and entity switch prompt
- `apps/Client/src/components/ui/TRKanbanBoard.tsx` — Kanban board; fix silent drop of unmatched-stage prospects
- `apps/Client/src/hooks/usePipelineStages.ts` — Auto-seed failure is swallowed silently; needs error surfacing
- `apps/Client/src/contexts/EntityContext.tsx` — Entity context with localStorage fallback logic (reference only, do not modify core logic)
- `apps/Client/src/hooks/useProspects.ts` — Prospect fetching hook (reference, currently correct)
- `apps/Client/src/services/pipelineStageService.ts` — Frontend service for pipeline stage API calls (reference)
- `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx` — Contains the entity selector dropdown (reference)

**Backend (reference only — no changes needed)**
- `apps/Server/src/adapter/rest/prospect_routes.py` — Verified: correctly returns all prospects for entity
- `apps/Server/src/adapter/rest/pipeline_stage_routes.py` — Verified: correctly returns all 7 stages; `/seed` requires admin/manager
- `apps/Server/src/repository/prospect_repository.py` — Verified: no `is_active` filter by default

**E2E and docs**
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_prospect_kanban_board.md` to understand how to create E2E test files

**Conditional Documentation**
- `app_docs/feature-6835fdde-prospect-kanban-board.md` — Prospect Kanban board feature documentation
- `app_docs/feature-eb19b5cd-pipeline-stage-configuration.md` — Pipeline stage configuration documentation

### New Files
- `.claude/commands/e2e/test_prospect_persistence_across_sessions.md` — E2E test to validate prospects persist and remain visible after entity switch and navigation

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add entity-aware empty state to ProspectsPage
- In `apps/Client/src/pages/ProspectsPage.tsx`, after the Kanban board renders, add an empty state check:
  - When `prospects.length === 0` AND `!prospectsLoading` AND `!error`, show a helpful empty state panel
  - The panel should display: "No prospects found for **{currentEntity.name}**."
  - If the user has multiple entities (`entities.length > 1`), show a prominent message: "You have other entities. Try switching entities using the sidebar selector." along with a list of other entity names that the user can click to switch directly
  - If the user has only one entity, show: "Use the 'Add Prospect' button to create your first prospect."
- This directly addresses the primary root cause by guiding the user to switch entities

### Step 2: Fix TRKanbanBoard to never silently drop prospects
- In `apps/Client/src/components/ui/TRKanbanBoard.tsx`, modify the `prospectsByStage` memo:
  - After iterating all prospects, collect any that didn't match a stage into an `uncategorized` array
  - If there are uncategorized prospects AND stages exist, log a console warning: `WARN [TRKanbanBoard]: ${count} prospect(s) have stages not matching any pipeline stage column`
  - Append an extra "Uncategorized" column to the board displaying these orphaned prospects so they are never invisible
  - If there are NO stages at all but there ARE prospects, log: `WARN [TRKanbanBoard]: No pipeline stages loaded but ${prospects.length} prospects exist — prospects cannot be displayed`
- This is a defensive fix that prevents future occurrences of silently hidden prospects

### Step 3: Fix usePipelineStages to surface auto-seed failures
- In `apps/Client/src/hooks/usePipelineStages.ts`, update the catch block for the auto-seed call:
  - When seeding fails AND no stages were loaded, set the error state: `setError('Pipeline stages could not be loaded. An administrator may need to configure them.')`
  - Keep the console.error for debugging
- This ensures the user gets feedback when stages are missing rather than seeing an empty board

### Step 4: Create E2E test for prospect visibility across entity switch
- Read `.claude/commands/e2e/test_basic_query.md` and `.claude/commands/e2e/test_prospect_kanban_board.md` as reference for E2E test format
- Create a new E2E test file at `.claude/commands/e2e/test_prospect_persistence_across_sessions.md` that validates:
  1. Login and navigate to /prospects
  2. Note the current entity name displayed on the page
  3. If entity has prospects, verify prospect cards are visible on the Kanban board
  4. If entity has no prospects, verify the empty state message is shown with entity-switch guidance
  5. Switch to a different entity using the sidebar entity selector
  6. Verify the Kanban board updates to show prospects for the newly selected entity
  7. Navigate away from /prospects to /dashboard
  8. Navigate back to /prospects
  9. Verify the same entity is still selected and prospects are still visible
  10. Take screenshots at each key step
- The test should specifically verify that switching from an entity with no prospects to one with prospects shows the correct data

### Step 5: Run validation commands
- Execute all validation commands listed below to confirm the fix works and introduces zero regressions

## Validation Commands
Execute every command to validate the bug is fixed with zero regressions.

- `curl -s http://localhost:8000/api/health` — Verify backend is healthy
- `curl -s -H "Authorization: Bearer <TOKEN>" "http://localhost:8000/api/prospects/?entity_id=f1ae369a-38ae-4ec1-8d9e-4edadf46518c&limit=100"` — Verify API returns 3 prospects (ASV Corp and 2x Faroo Legal) for KAI Partners
- `curl -s -H "Authorization: Bearer <TOKEN>" "http://localhost:8000/api/pipeline-stages/?entity_id=f1ae369a-38ae-4ec1-8d9e-4edadf46518c&active_only=true"` — Verify all 7 pipeline stages exist for KAI Partners
- Read `.claude/commands/test_e2e.md`, then read and execute your new E2E `.claude/commands/e2e/test_prospect_persistence_across_sessions.md` test file to validate this functionality works
- `cd apps/Server && .venv/bin/python -m pytest tests/ -v` — Run Server tests to validate the bug is fixed with zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate the bug is fixed with zero regressions
- `cd apps/Client && npm run build` — Run Client build to validate the bug is fixed with zero regressions

## Notes
- **Duplicate prospect**: There are 2 Faroo Legal records (IDs `83b82340...` and `c9ad79d5...`). This is a separate issue caused by `crm_api_client.search_prospect()` not deduplicating. Not in scope for this bug fix.
- **No backend changes needed**: The API correctly returns data. All fixes are frontend-only.
- The entity selector lives in `TRCollapsibleSidebar.tsx` line 111. When the sidebar is collapsed, only the first letter of the entity name is shown as an avatar (line 134). This makes entity awareness harder for users.
- The `ProspectUpdateDTO` exposes `is_active` via PUT API, but the `TRProspectForm` does not include it, so the UI cannot accidentally deactivate prospects.
- No new libraries are required for this fix.
