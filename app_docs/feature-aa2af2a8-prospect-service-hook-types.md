# Prospect Service, Hook & TypeScript Types

**ADW ID:** aa2af2a8
**Date:** 2026-03-01
**Specification:** specs/issue-52-adw-aa2af2a8-sdlc_planner-prospect-service-hook-types.md

## Overview

Implements the complete frontend data layer for the CRM prospect and meeting record features. This includes TypeScript type definitions mirroring backend DTOs, Axios-based service layers for API communication, and React hooks managing component state (loading, error, data) with auto-fetch on entity/filter changes. This data layer is the foundation consumed by all downstream CRM UI components (Kanban board, detail view, drag-and-drop).

## What Was Built

- **TypeScript types** for Prospect and MeetingRecord domains (12 interfaces + 1 union type) in the centralized types file
- **prospectService** — Axios-based service with 6 API operations: create, list, get, update, updateStage, delete
- **meetingRecordService** — Axios-based service with 6 API operations: create, list, get, getHtml, update, delete
- **useProspects** hook — React state management with loading/error/filters and CRUD callbacks with auto-fetch
- **useMeetingRecords** hook — React state management with optional prospect scoping and HTML download support

## Technical Implementation

### Files Modified

- `apps/Client/src/types/index.ts`: Added 12 interfaces and 1 union type — `ProspectStage`, `Prospect`, `ProspectCreate`, `ProspectUpdate`, `ProspectFilters`, `ProspectListResponse`, `MeetingRecord`, `MeetingRecordCreate`, `MeetingRecordUpdate`, `MeetingRecordFilters`, `MeetingRecordListResponse`
- `apps/Client/src/services/prospectService.ts`: New prospect service with CRUD + stage update + filtered listing via URLSearchParams
- `apps/Client/src/services/meetingRecordService.ts`: New meeting record service with CRUD + filtered listing + HTML download
- `apps/Client/src/hooks/useProspects.ts`: New React hook managing prospects state array with entity-scoped auto-fetch
- `apps/Client/src/hooks/useMeetingRecords.ts`: New React hook managing meeting records with optional prospect scoping

### Key Changes

- **ProspectStage union type** (`'lead' | 'contacted' | 'qualified' | 'proposal' | 'negotiation' | 'won' | 'lost'`) follows the project convention of string literal unions over enums
- **MeetingRecord response types** use `string` for `action_items` and `participants` (JSON-serialized by the backend), while Create/Update types use `string[]` matching what the API accepts
- **Stage update** uses PATCH `/prospects/{id}/stage` with `{ new_stage, notes }` body, distinct from the general PUT update endpoint
- **HTML download** via `getHtml()` returns raw HTML text using `responseType: 'text'`
- **All hooks guard against null `entityId`** — skipping API calls and returning empty arrays when no entity is selected
- **Auto-fetch pattern** — hooks use `useEffect` triggered by `useCallback` identity changes when `entityId` or `filters` change

## How to Use

1. **Import types** for type-safe prospect/meeting record data:
   ```typescript
   import type { Prospect, ProspectCreate, ProspectStage, MeetingRecord } from '@/types'
   ```

2. **Use the prospect hook** in components:
   ```typescript
   const { prospects, isLoading, error, createProspect, updateProspectStage, setFilters } = useProspects(entityId)
   ```

3. **Use the meeting records hook** scoped to a prospect:
   ```typescript
   const { meetingRecords, createMeetingRecord, getMeetingRecordHtml } = useMeetingRecords(entityId, prospectId)
   ```

4. **Filter prospects by stage**:
   ```typescript
   setFilters({ stage: 'qualified', is_active: true })
   ```

5. **Update prospect pipeline stage**:
   ```typescript
   await updateProspectStage(prospectId, 'proposal', 'Moved to proposal after demo')
   ```

6. **Download meeting HTML**:
   ```typescript
   const html = await getMeetingRecordHtml(recordId)
   ```

## Configuration

No additional configuration required. Services use the existing `apiClient` from `@/api/clients` with JWT interceptor. All endpoints are relative to the configured `VITE_API_URL`.

## Testing

- Run `cd apps/Client && npx tsc --noEmit` to validate all types compile correctly
- Run `cd apps/Client && npm run build` to verify production build succeeds
- Run `cd apps/Server && uv run pytest` to confirm no backend regressions
- Full integration testing occurs when downstream UI components (Kanban board CRM-008, detail view CRM-010) consume these hooks

## Notes

- This is a data-layer-only feature with no UI components. The Kanban board (CRM-008), drag-and-drop (CRM-009), and detail view (CRM-010) will consume these services and hooks.
- The `is_active` filter correctly handles explicit `false` values by checking `!== undefined` rather than truthiness.
- The `estimated_value` field uses `number` type (matching backend `Decimal` serialized as JSON number).
