# Person Management Page (RestaurantOS)

**ADW ID:** de82eb81
**Date:** 2026-03-03
**Specification:** specs/issue-87-adw-de82eb81-sdlc_planner-person-management-page.md

## Overview

A full CRUD frontend page for managing persons (employees, suppliers, owners) within a RestaurantOS restaurant. The page replaces the previous "Pr&oacute;ximamente" placeholder at `/poc/restaurant-os/persons` with a data table, search/filter controls, and dialog-based forms for creating, editing, and deleting persons. All UI text is in Spanish (Colombian). The backend Person API (`/api/persons`) was already implemented; this feature is purely frontend.

## What Was Built

- **Person TypeScript types** (`Person`, `PersonCreate`, `PersonUpdate`, `PersonFilters`, `PersonType`) matching backend DTOs
- **Person API service** with `getAll`, `create`, `update`, `delete` methods using the shared `apiClient`
- **`usePersons` custom hook** for CRUD state management scoped to a restaurant ID, with auto-fetch on filter/restaurant changes
- **`TRPersonForm` component** using react-hook-form with create/edit modes, Spanish labels, email validation, and loading states
- **`RestaurantOSPersonsPage`** full CRUD page with data table, name search, type filter dropdown, and MUI dialogs for add/edit/delete
- **E2E test specification** for person management page validation

## Technical Implementation

### Files Modified

- `apps/Client/src/types/person.ts` (new): `PersonType` union type, `Person`, `PersonCreate`, `PersonUpdate`, `PersonFilters` interfaces
- `apps/Client/src/types/index.ts`: Added re-export for all person types
- `apps/Client/src/services/personService.ts` (new): CRUD service with `getAll` (supports `restaurant_id` + optional `type` filter), `create`, `update`, `delete`
- `apps/Client/src/hooks/usePersons.ts` (new): Custom hook managing `persons[]`, `isLoading`, `error`, `filters` state with `useCallback`/`useEffect` pattern
- `apps/Client/src/components/forms/TRPersonForm.tsx` (new): react-hook-form form with Controller for the type Select, supports create and edit modes
- `apps/Client/src/pages/restaurantos/RestaurantOSPersonsPage.tsx`: Replaced placeholder with full CRUD page (14 &rarr; 327 lines)
- `.claude/commands/e2e/test_person_management.md` (new): E2E test specification

### Key Changes

- **Service layer** follows the `restaurantService` pattern: each method wraps an `apiClient` call in try/catch with `INFO`/`ERROR` console logs
- **Hook** follows the `useProspects` pattern: accepts `restaurantId | null`, guards on null, refreshes list after every mutation, exposes `setFilters` for the type dropdown
- **Form** uses `Controller` for the MUI Select (Tipo) field and `register` for text fields; `useEffect` resets form when `initialData` changes for edit mode
- **Page** implements client-side name search via `useMemo` filter and server-side type filtering via `setFilters` which triggers a re-fetch
- **Person type mapping**: stored as lowercase English (`employee`, `supplier`, `owner`) but displayed in Spanish (`Empleado`, `Proveedor`, `Due&ntilde;o`) via a `PERSON_TYPE_LABELS` lookup

## How to Use

1. Navigate to **RestaurantOS > Personas** in the sidebar (route: `/poc/restaurant-os/persons`)
2. Select a restaurant if not already selected (the page shows `TRNoRestaurantPrompt` otherwise)
3. View the persons table with columns: Nombre, Rol, Tipo, Correo Electr&oacute;nico, WhatsApp, Acciones
4. Click **Agregar Persona** to open the create dialog; fill in name (required), role (required), type, email, and WhatsApp
5. Use the **Buscar por nombre** text field to search persons by name (client-side, case-insensitive)
6. Use the **Filtrar por tipo** dropdown to filter by Todos/Empleado/Proveedor/Due&ntilde;o (server-side)
7. Click the edit icon on a row to modify a person; click the delete icon to remove (with confirmation dialog)

## Configuration

No additional configuration required. The feature uses the existing `apiClient` with JWT interceptor and the `RestaurantContext` for multi-tenant scoping. Backend endpoints at `/api/persons` must be available.

## Testing

- **TypeScript validation**: `cd apps/Client && npx tsc --noEmit`
- **Production build**: `cd apps/Client && npm run build`
- **E2E test**: Run the person management E2E test spec at `.claude/commands/e2e/test_person_management.md`
- **Backend regression**: `cd apps/Server && python -m pytest tests/ -x`

## Notes

- The backend Person API (ROS-002) provides 6 endpoints: POST, GET (list), GET (search), GET (by-id), PUT, DELETE on `/api/persons`
- The route `/poc/restaurant-os/persons` was already registered in `App.tsx`; no routing changes were needed
- Person type values are lowercase English in the database but displayed in Spanish in the UI
- Search is client-side (filtering the fetched array); for large datasets, the backend search endpoint (`GET /persons/search?query=`) is available but not used here
