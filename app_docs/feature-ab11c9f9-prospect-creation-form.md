# CRM Prospect Creation Form (TRProspectForm)

**ADW ID:** ab11c9f9
**Date:** 2026-03-01
**Specification:** specs/issue-53-adw-ab11c9f9-sdlc_planner-prospect-creation-form.md

## Overview

Implements the `TRProspectForm` component — a react-hook-form + MUI form for creating and editing CRM prospects. Includes the full frontend infrastructure: TypeScript types for the prospect domain, an Axios-based API service layer, and a custom React hook for state management. This is part of CRM Wave 2, designed as a standalone component that the Kanban Board (CRM-008) will integrate in a dialog.

## What Was Built

- **TRProspectForm** — React form component for prospect creation/editing with 8 fields, validation, create/edit mode, loading states, and cancel support
- **CRM TypeScript types** — `Prospect`, `ProspectCreate`, `ProspectUpdate`, `ProspectStage`, `ProspectStageUpdate`, `ProspectFilters`, `ProspectListResponse` interfaces
- **prospectService** — Axios-based API service with full CRUD operations (create, list, get, update, updateStage, delete)
- **useProspects hook** — React hook wrapping the service with state management, filtering, and auto-fetch on entity/filter changes
- **E2E test specification** — Test spec for validating form rendering, field validation, and submission

## Technical Implementation

### Files Modified

- `apps/Client/src/types/index.ts`: Added 7 CRM prospect-related TypeScript interfaces and types (59 lines)
- `apps/Client/src/components/forms/TRProspectForm.tsx`: New form component with 8 fields, validation, create/edit modes (269 lines)
- `apps/Client/src/services/prospectService.ts`: New API service with 6 CRUD methods and structured logging (169 lines)
- `apps/Client/src/hooks/useProspects.ts`: New custom hook with state management, filtering, and CRUD wrappers (150 lines)
- `.claude/commands/e2e/test_prospect_creation_form.md`: New E2E test specification (141 lines)

### Key Changes

- **ProspectStage union type** defines the 7 pipeline stages: `lead`, `contacted`, `qualified`, `proposal`, `negotiation`, `won`, `lost`
- **TRProspectForm** follows the `TRBudgetForm` pattern — uses `Controller` for the stage `Select`, `InputAdornment` for currency on estimated value, and `register` for all text fields
- **Create/Edit mode** is determined by the presence of `initialData` prop; form resets after successful creation but not after edit
- **Empty optional fields** are converted to `undefined` (not empty strings) before submission to match the backend API contract
- **useProspects hook** auto-fetches prospects when `entityId` or `filters` change via `useEffect`, with null `entityId` guard to prevent invalid API calls

## How to Use

1. Import the form component:
   ```typescript
   import { TRProspectForm } from '@/components/forms/TRProspectForm'
   ```

2. Use in a page or dialog with required props:
   ```typescript
   <TRProspectForm
     onSubmit={async (data) => { await createProspect(data) }}
     entityId={currentEntity.id}
     isLoading={isLoading}
     onCancel={() => setDialogOpen(false)}
   />
   ```

3. For edit mode, pass existing prospect data:
   ```typescript
   <TRProspectForm
     onSubmit={async (data) => { await updateProspect(prospect.id, data) }}
     initialData={prospect}
     entityId={currentEntity.id}
   />
   ```

4. Use the `useProspects` hook for state management:
   ```typescript
   const {
     prospects, total, isLoading, error,
     createProspect, updateProspect, deleteProspect,
     filters, setFilters
   } = useProspects(currentEntity?.id ?? null)
   ```

## Form Fields

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| Company Name | TextField | Yes | max 255 chars |
| Contact Name | TextField | No | max 255 chars |
| Contact Email | TextField (email) | No | email pattern, max 255 chars |
| Contact Phone | TextField | No | max 100 chars |
| Pipeline Stage | Select (Controller) | Yes | defaults to "lead" |
| Estimated Value | TextField (number) | No | min 0, step 0.01, $ adornment |
| Source | TextField | No | max 100 chars |
| Notes | TextField (multiline) | No | 3 rows |

## Configuration

No additional configuration needed. The component uses the existing `apiClient` from `@/api/clients` which handles JWT authentication and base URL configuration.

## API Endpoints Used

- `POST /api/prospects/` — Create prospect
- `GET /api/prospects/?entity_id=&stage=&is_active=&source=&skip=&limit=` — List/filter prospects
- `GET /api/prospects/{id}?entity_id=` — Get single prospect
- `PUT /api/prospects/{id}?entity_id=` — Update prospect
- `PATCH /api/prospects/{id}/stage?entity_id=` — Update pipeline stage
- `DELETE /api/prospects/{id}?entity_id=` — Delete prospect

## Testing

- TypeScript compilation: `cd apps/Client && npx tsc --noEmit`
- Production build: `cd apps/Client && npm run build`
- E2E test: Run the test spec at `.claude/commands/e2e/test_prospect_creation_form.md`

## Notes

- The form is a **standalone component** — no page, route, or sidebar entry is created. CRM-008 (Kanban Board) will integrate it in a dialog.
- The `is_active` field is excluded from the form — it's managed programmatically for soft delete, not set during creation.
- Pipeline stage colors are NOT used in the form; they belong to the Kanban Board visualization (CRM-008).
- All logging follows `INFO/ERROR [ComponentName]` format for agent debugging.
