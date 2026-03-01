# Feature: Prospect Service, Hook & TypeScript Types

## Metadata
issue_number: `52`
adw_id: `aa2af2a8`
issue_json: `{"number":52,"title":"[CRM Pipeline] Wave 2: Prospect Service, Hook & TypeScript Types","body":"Create the frontend service layer, custom React hook, and TypeScript interfaces for managing prospect and meeting data."}`

## Feature Description
Create the complete frontend data layer for the CRM prospect and meeting record features. This includes TypeScript type definitions that mirror the backend DTOs, a service layer that wraps Axios API calls to the prospect and meeting record endpoints, and custom React hooks that manage component state (loading, error, data) while delegating HTTP operations to the services. This data layer is the foundation consumed by all downstream CRM UI components (Kanban board, detail view, drag-and-drop).

## User Story
As a CRM user
I want a typed, entity-scoped data layer for prospects and meeting records
So that downstream UI components (Kanban board, detail views, forms) can fetch, create, update, and delete prospect/meeting data with consistent loading states, error handling, and type safety.

## Problem Statement
The backend API endpoints for prospects (CRM-004) and meeting records (CRM-005) exist, but the frontend has no way to communicate with them. Without TypeScript types, services, and hooks, no CRM UI component can be built. This is the critical bridge between backend API and frontend UI.

## Solution Statement
Follow the established frontend patterns (transactionService/useTransactions) to create:
1. **TypeScript types** in `apps/Client/src/types/index.ts` — interfaces for Prospect, MeetingRecord, their Create/Update/Filter/ListResponse variants, and the ProspectStage union type, all matching the backend DTOs exactly.
2. **prospectService** in `apps/Client/src/services/prospectService.ts` — Axios-based service with CRUD + stage update + list with filters, following the singleton object pattern with INFO/ERROR logging.
3. **meetingRecordService** in `apps/Client/src/services/meetingRecordService.ts` — Axios-based service with CRUD + list with filters + HTML download, same pattern.
4. **useProspects** hook in `apps/Client/src/hooks/useProspects.ts` — React hook managing prospects state array, loading/error, filters, and CRUD callbacks with auto-fetch on entity/filter change.
5. **useMeetingRecords** hook in `apps/Client/src/hooks/useMeetingRecords.ts` — React hook managing meeting records state, scoped to both entity and prospect.

## Relevant Files
Use these files to implement the feature:

- `apps/Client/src/types/index.ts` — Add Prospect and MeetingRecord type definitions here. This is the centralized types file for the entire frontend.
- `apps/Client/src/api/clients/index.ts` — The Axios API client with JWT interceptor. Import `apiClient` from here in new services.
- `apps/Client/src/services/transactionService.ts` — Reference pattern for creating the prospect and meeting record services (singleton object, logging, error handling).
- `apps/Client/src/hooks/useTransactions.ts` — Reference pattern for creating the prospect and meeting record hooks (state management, useCallback, useEffect auto-fetch, entityId guard).
- `apps/Server/src/interface/prospect_dto.py` — Backend Prospect DTOs defining the exact field names, types, and validations the frontend types must match.
- `apps/Server/src/interface/meeting_record_dto.py` — Backend MeetingRecord DTOs defining the exact field names, types, and validations.
- `apps/Server/src/adapter/rest/prospect_routes.py` — Backend Prospect API routes defining URL patterns, query parameters, and HTTP methods the service must call.
- `apps/Server/src/adapter/rest/meeting_record_routes.py` — Backend MeetingRecord API routes defining URL patterns, query parameters, and HTTP methods.
- `.claude/commands/conditional_docs.md` — Check for task-specific documentation requirements.

### New Files
- `apps/Client/src/services/prospectService.ts` — New prospect service layer.
- `apps/Client/src/services/meetingRecordService.ts` — New meeting record service layer.
- `apps/Client/src/hooks/useProspects.ts` — New prospect React hook.
- `apps/Client/src/hooks/useMeetingRecords.ts` — New meeting record React hook.

## Implementation Plan
### Phase 1: Foundation
Add all TypeScript type definitions (Prospect, MeetingRecord, and their variants) to the centralized `types/index.ts` file. These types mirror the backend Pydantic DTOs field-for-field, using `string` for UUIDs and datetimes (as JSON serializes them), `number` for Decimal fields, and union string literals for stages.

### Phase 2: Core Implementation
Create the two service files (`prospectService.ts` and `meetingRecordService.ts`) following the established singleton object pattern. Each service method wraps an Axios call, includes INFO/ERROR logging, builds query parameters via URLSearchParams, and re-throws errors for the hook layer to catch.

### Phase 3: Integration
Create the two hook files (`useProspects.ts` and `useMeetingRecords.ts`) that wrap the services with React state management. Hooks provide loading/error states, auto-fetch on entityId/filter changes, and CRUD callbacks that refresh the list after mutations. The `useMeetingRecords` hook additionally accepts a `prospectId` parameter for scoping meeting records to a specific prospect.

## Step by Step Tasks

### Step 1: Add TypeScript Type Definitions
- Open `apps/Client/src/types/index.ts`
- Add at the end of the file, after the RecurringTemplate section:
  - `ProspectStage` union type: `'lead' | 'contacted' | 'qualified' | 'proposal' | 'negotiation' | 'won' | 'lost'`
  - `Prospect` interface with fields: `id`, `entity_id`, `company_name`, `contact_name?`, `contact_email?`, `contact_phone?`, `stage: ProspectStage`, `estimated_value?`, `source?`, `notes?`, `is_active`, `created_at`, `updated_at?`
  - `ProspectCreate` interface with fields: `entity_id`, `company_name`, `contact_name?`, `contact_email?`, `contact_phone?`, `stage?: ProspectStage`, `estimated_value?`, `source?`, `notes?`
  - `ProspectUpdate` interface with all fields optional: `company_name?`, `contact_name?`, `contact_email?`, `contact_phone?`, `stage?`, `estimated_value?`, `source?`, `notes?`, `is_active?`
  - `ProspectFilters` interface: `stage?: ProspectStage`, `is_active?: boolean`, `source?: string`
  - `ProspectListResponse` interface: `prospects: Prospect[]`, `total: number`
  - `MeetingRecord` interface with fields: `id`, `entity_id`, `prospect_id`, `title`, `transcript_ref?`, `summary?`, `action_items?` (string — JSON-serialized from backend), `participants?` (string — JSON-serialized from backend), `html_output?`, `meeting_date?`, `is_active`, `created_at`, `updated_at?`
  - `MeetingRecordCreate` interface: `entity_id`, `prospect_id`, `title`, `transcript_ref?`, `summary?`, `action_items?: string[]`, `participants?: string[]`, `html_output?`, `meeting_date?`
  - `MeetingRecordUpdate` interface: all optional — `title?`, `transcript_ref?`, `summary?`, `action_items?: string[]`, `participants?: string[]`, `html_output?`, `meeting_date?`, `is_active?`
  - `MeetingRecordFilters` interface: `prospect_id?: string`, `is_active?: boolean`, `meeting_date_from?: string`, `meeting_date_to?: string`
  - `MeetingRecordListResponse` interface: `meeting_records: MeetingRecord[]`, `total: number`

### Step 2: Create Prospect Service
- Create `apps/Client/src/services/prospectService.ts`
- Import `apiClient` from `@/api/clients` and types from `@/types`
- Implement the following methods on a `prospectService` singleton object:
  - `create(data: ProspectCreate): Promise<Prospect>` — POST `/prospects/`
  - `list(entityId: string, filters?: ProspectFilters, skip = 0, limit = 100): Promise<ProspectListResponse>` — GET `/prospects/` with URLSearchParams for entity_id, skip, limit, and optional stage/is_active/source filters
  - `get(prospectId: string, entityId: string): Promise<Prospect>` — GET `/prospects/{prospectId}?entity_id={entityId}`
  - `update(prospectId: string, entityId: string, data: ProspectUpdate): Promise<Prospect>` — PUT `/prospects/{prospectId}?entity_id={entityId}`
  - `updateStage(prospectId: string, entityId: string, newStage: ProspectStage, notes?: string): Promise<Prospect>` — PATCH `/prospects/{prospectId}/stage?entity_id={entityId}` with body `{ new_stage, notes }`
  - `delete(prospectId: string, entityId: string): Promise<void>` — DELETE `/prospects/{prospectId}?entity_id={entityId}`
- Every method must have INFO log on entry, INFO log on success, and ERROR log + re-throw in catch block
- Export as `export const prospectService = { ... }` and `export default prospectService`

### Step 3: Create Meeting Record Service
- Create `apps/Client/src/services/meetingRecordService.ts`
- Import `apiClient` from `@/api/clients` and types from `@/types`
- Implement the following methods on a `meetingRecordService` singleton object:
  - `create(data: MeetingRecordCreate): Promise<MeetingRecord>` — POST `/meeting-records/`
  - `list(entityId: string, filters?: MeetingRecordFilters, skip = 0, limit = 100): Promise<MeetingRecordListResponse>` — GET `/meeting-records/` with URLSearchParams for entity_id, skip, limit, and optional prospect_id/is_active/meeting_date_from/meeting_date_to filters
  - `get(recordId: string, entityId: string): Promise<MeetingRecord>` — GET `/meeting-records/{recordId}?entity_id={entityId}`
  - `getHtml(recordId: string, entityId: string): Promise<string>` — GET `/meeting-records/{recordId}/html?entity_id={entityId}`, return `response.data` as string (text/html response)
  - `update(recordId: string, entityId: string, data: MeetingRecordUpdate): Promise<MeetingRecord>` — PUT `/meeting-records/{recordId}?entity_id={entityId}`
  - `delete(recordId: string, entityId: string): Promise<void>` — DELETE `/meeting-records/{recordId}?entity_id={entityId}`
- Same logging and error handling pattern as prospectService
- Export as `export const meetingRecordService = { ... }` and `export default meetingRecordService`

### Step 4: Create useProspects Hook
- Create `apps/Client/src/hooks/useProspects.ts`
- Import `useState`, `useEffect`, `useCallback` from React
- Import `prospectService` from `@/services/prospectService`
- Import types `Prospect`, `ProspectCreate`, `ProspectUpdate`, `ProspectStage`, `ProspectFilters` from `@/types`
- Define `UseProspectsResult` interface with:
  - `prospects: Prospect[]`, `total: number`, `isLoading: boolean`, `error: string | null`, `filters: ProspectFilters`
  - `fetchProspects: () => Promise<void>`
  - `createProspect: (data: ProspectCreate) => Promise<void>`
  - `updateProspect: (id: string, data: ProspectUpdate) => Promise<void>`
  - `updateProspectStage: (id: string, newStage: ProspectStage, notes?: string) => Promise<void>`
  - `deleteProspect: (id: string) => Promise<void>`
  - `setFilters: (filters: ProspectFilters) => void`
- Implement `useProspects(entityId: string | null): UseProspectsResult`:
  - State: `prospects`, `total`, `isLoading`, `error`, `filters`
  - `fetchProspects` with entityId guard, try/catch, loading/error state
  - `createProspect` calls service.create then refreshes
  - `updateProspect` calls service.update then refreshes (guard entityId)
  - `updateProspectStage` calls service.updateStage then refreshes (guard entityId)
  - `deleteProspect` calls service.delete then refreshes (guard entityId)
  - `useEffect` to auto-fetch when `fetchProspects` callback identity changes
- Export as `export const useProspects` and `export default useProspects`

### Step 5: Create useMeetingRecords Hook
- Create `apps/Client/src/hooks/useMeetingRecords.ts`
- Import `useState`, `useEffect`, `useCallback` from React
- Import `meetingRecordService` from `@/services/meetingRecordService`
- Import types `MeetingRecord`, `MeetingRecordCreate`, `MeetingRecordUpdate`, `MeetingRecordFilters` from `@/types`
- Define `UseMeetingRecordsResult` interface with:
  - `meetingRecords: MeetingRecord[]`, `total: number`, `isLoading: boolean`, `error: string | null`, `filters: MeetingRecordFilters`
  - `fetchMeetingRecords: () => Promise<void>`
  - `createMeetingRecord: (data: MeetingRecordCreate) => Promise<void>`
  - `updateMeetingRecord: (id: string, data: MeetingRecordUpdate) => Promise<void>`
  - `deleteMeetingRecord: (id: string) => Promise<void>`
  - `getMeetingRecordHtml: (id: string) => Promise<string>`
  - `setFilters: (filters: MeetingRecordFilters) => void`
- Implement `useMeetingRecords(entityId: string | null, prospectId?: string): UseMeetingRecordsResult`:
  - Accept optional `prospectId` to scope records to a specific prospect — when provided, automatically set `filters.prospect_id`
  - State: `meetingRecords`, `total`, `isLoading`, `error`, `filters`
  - `fetchMeetingRecords` with entityId guard, merges prospectId into filters if provided
  - CRUD callbacks following same pattern as useProspects
  - `getMeetingRecordHtml` calls service.getHtml (guard entityId), returns HTML string
  - `useEffect` to auto-fetch when `fetchMeetingRecords` callback identity changes
- Export as `export const useMeetingRecords` and `export default useMeetingRecords`

### Step 6: Validate Implementation
- Run TypeScript type checking to ensure zero type errors
- Run Client build to ensure zero compilation errors
- Run Server tests to confirm no backend regressions

## Testing Strategy
### Unit Tests
This feature consists of pure data-layer code (types, services, hooks) with no UI. Unit testing would require mocking Axios and React test utilities which is beyond the scope of this issue. The types are validated by the TypeScript compiler. The services and hooks will be integration-tested when the Kanban board UI (CRM-008) and detail view (CRM-010) consume them.

### Edge Cases
- `entityId` is null — hooks must guard and skip all API calls, return empty arrays
- `prospectId` is undefined in `useMeetingRecords` — should not include `prospect_id` filter param
- `is_active` filter is explicitly `false` — must append `"false"` string, not skip (distinguish from undefined)
- `estimated_value` is `0` — valid value, must not be treated as falsy/skipped
- Backend returns `action_items` and `participants` as JSON strings (not arrays) in responses — types reflect this
- Stage update endpoint uses PATCH (not PUT) with a specific body shape `{ new_stage, notes }`

## Acceptance Criteria
- All Prospect and MeetingRecord types are defined in `apps/Client/src/types/index.ts` matching backend DTOs
- `prospectService` covers all 6 API operations: create, list, get, update, updateStage, delete
- `meetingRecordService` covers all 6 API operations: create, list, get, getHtml, update, delete
- `useProspects` hook provides state management with loading/error/filters and CRUD operations
- `useMeetingRecords` hook provides state management with optional prospect scoping
- All services use `INFO [ServiceName]:` and `ERROR [ServiceName]:` logging format
- All hooks guard against null `entityId` before making API calls
- `npm run tsc --noEmit` passes with zero errors
- `npm run build` succeeds with zero errors
- `uv run pytest` passes with zero server-side regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest` — Run Server tests to validate no backend regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate all new types, services, and hooks compile correctly with zero type errors
- `cd apps/Client && npm run build` — Run Client production build to validate the feature compiles and bundles with zero errors

## Notes
- The `action_items` and `participants` fields differ between Create/Update DTOs (arrays `string[]`) and Response DTO (JSON-serialized `string`). The backend stores these as text columns and JSON-serializes on response. The frontend Create/Update types use `string[]` to match what the API accepts, while the response `MeetingRecord` type uses `string` to match what the API returns.
- The `getHtml` method on `meetingRecordService` returns raw HTML text, not JSON. The Axios response type should be configured to accept text (`responseType: 'text'` or just reading `response.data` as string).
- This is a data-layer-only issue with no UI components. The Kanban board (CRM-008), drag-and-drop (CRM-009), and detail view (CRM-010) will consume these services and hooks.
- The `ProspectStage` type is intentionally a union type (not an enum) to match the project convention of using string literal unions for type safety.
