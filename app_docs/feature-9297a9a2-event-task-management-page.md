# Event / Task Management Page

**ADW ID:** 9297a9a2
**Date:** 2026-03-03
**Specification:** specs/issue-89-adw-9297a9a2-sdlc_planner-event-task-management-page.md

## Overview

A full CRUD frontend page for managing events and tasks within a RestaurantOS restaurant. The page replaces a placeholder "Próximamente" message with a date-grouped data table featuring multi-filter capabilities, overdue visual highlighting, quick-complete actions, and dialog-based create/edit/delete operations. All UI text is in Spanish (Colombian). The backend Event API already existed; this feature is purely frontend.

## What Was Built

- **Event TypeScript types** — `Event`, `EventCreate`, `EventUpdate`, `EventStatusUpdate`, `EventFilters` interfaces and `EventType`/`EventFrequency`/`EventStatus` union types with Spanish-labeled option constants
- **Event API service** — `eventService` with `getAll`, `create`, `update`, `updateStatus`, and `delete` methods using the existing backend `/api/events` endpoints
- **useEvents custom hook** — State management for events list, loading, errors, filters, and all CRUD operations scoped to a restaurant
- **TREventForm component** — react-hook-form dialog form with create/edit modes, conditional validation (responsible required for tasks), and six fields: Tipo, Descripción, Fecha, Frecuencia, Responsable, Canal de Notificación
- **TREventStatusBadge component** — Color-coded MUI Chip displaying Pendiente (blue/info), Completado (green/success), or Vencido (red/error)
- **RestaurantOSEventsPage** — Complete CRUD page with date-grouped table, five filters (type, status, responsible, date range), overdue row highlighting, quick-complete action, and MUI dialog-based forms
- **E2E test specification** — Comprehensive test flow covering all CRUD operations, filters, quick-complete, validation, and overdue highlighting

## Technical Implementation

### Files Modified

- `apps/Client/src/pages/restaurantos/RestaurantOSEventsPage.tsx`: Replaced placeholder with full 530-line CRUD page including date-grouped table, filters, dialogs, and overdue highlighting

### Files Created

- `apps/Client/src/types/event.ts`: Event interfaces, union types, and option constant arrays (89 lines)
- `apps/Client/src/services/eventService.ts`: Event API service with 5 CRUD methods and logging (111 lines)
- `apps/Client/src/hooks/useEvents.ts`: Custom hook for event state management with filters (139 lines)
- `apps/Client/src/components/forms/TREventForm.tsx`: react-hook-form event form with conditional validation (283 lines)
- `apps/Client/src/components/ui/TREventStatusBadge.tsx`: Status badge chip with color mapping (28 lines)
- `.claude/commands/e2e/test_event_task_management.md`: E2E test specification (236 lines)

### Key Changes

- **Date grouping**: Events are grouped client-side by extracting YYYY-MM-DD from `event.date`, sorted chronologically, with localized Spanish date headers (e.g., "lunes 03 mar 2025")
- **Overdue highlighting**: Table rows for events with `is_overdue === true` or `status === 'overdue'` receive a subtle red background tint (`rgba(211, 47, 47, 0.08)`)
- **Quick-complete**: A green checkmark `IconButton` appears only on pending events, calling `PATCH /events/{id}/status` with `{ status: 'completed' }`
- **Conditional validation**: When event type is `tarea`, the `responsible_id` field becomes required with the message "El responsable es obligatorio para tareas"
- **Server-side filtering**: All five filters (type, status, responsible_id, date_from, date_to) are passed as query parameters to the backend API

## How to Use

1. Navigate to `/poc/restaurant-os/events` in the application
2. Select a restaurant from the restaurant selector if not already selected
3. Click **"Agregar Evento"** to open the creation form
4. Fill in the required fields: **Tipo** (event type) and **Fecha** (date/time). If type is "Tarea", a **Responsable** (person) must be selected
5. Optionally set **Descripción**, **Frecuencia** (recurrence), and **Canal de Notificación**
6. Use the filter row to narrow events by type, status, responsible person, or date range
7. Click the green checkmark icon on pending events to quickly mark them as completed
8. Click the edit icon to modify an event's details
9. Click the delete icon and confirm to remove an event

## Configuration

No additional configuration required. The feature uses the existing backend Event API endpoints (`/api/events`) and RestaurantContext for restaurant scoping. Persons must be created first (via Person Management page) to populate the responsible dropdown.

## Testing

- **TypeScript**: `cd apps/Client && npx tsc --noEmit` — validates zero type errors
- **Build**: `cd apps/Client && npm run build` — validates production build succeeds
- **Backend**: `cd apps/Server && python -m pytest tests/ -x` — validates no regressions
- **E2E**: Run the E2E test specification at `.claude/commands/e2e/test_event_task_management.md` covering full CRUD, filters, quick-complete, conditional validation, and overdue highlighting

## Notes

- System-generated event types (`alerta_stock`, `alerta_rentabilidad`) are excluded from the form dropdown but render correctly in the table if present
- The `usePersons` hook is used both for the form's responsible dropdown and for resolving person names in the table display
- The route `/poc/restaurant-os/events` was already registered in `App.tsx` — no routing changes were needed
- The page follows established patterns from `RestaurantOSPersonsPage` and `RestaurantOSDocumentsPage` for consistency
