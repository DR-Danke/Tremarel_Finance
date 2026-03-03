# Feature: Event / Task Management Page

## Metadata
issue_number: `89`
adw_id: `9297a9a2`
issue_json: `{"number":89,"title":"[RestaurantOS] Wave 4: Event / Task Management Page"}`

## Feature Description
Build a full CRUD frontend page for managing events and tasks within a RestaurantOS restaurant. The page provides a list view grouped by date with columns for Fecha, Tipo, Descripción, Responsable, Estado, and Acciones. Events can be filtered by type, responsible person, status, and date range. Overdue events are visually highlighted with red background/border. A quick-complete button (checkmark icon) allows marking pending tasks as completed directly from the table. The backend API already exists (`/api/events` and `/api/events/tasks`), so this feature is purely frontend: types, service, hook, form component, status badge component, and page component. All UI text is in Spanish (Colombian).

## User Story
As a restaurant manager
I want to view, create, edit, and manage events and tasks for my restaurant in a date-grouped list with quick actions
So that I can track deadlines, assign tasks to employees, and ensure nothing becomes overdue

## Problem Statement
The RestaurantOS Events page (`/poc/restaurant-os/events`) currently shows a placeholder "Próximamente" message. Restaurant managers need a fully functional interface to manage events (deadlines, payments, shifts, checklists) and tasks with filtering, overdue highlighting, and quick-complete capabilities.

## Solution Statement
Replace the placeholder `RestaurantOSEventsPage` with a complete CRUD page that uses the existing backend Event API. Create an event service, custom hook, form component, and status badge component following established codebase patterns (personService, usePersons, TRPersonForm, TRExpirationBadge). The page will include a data table grouped by date, multi-filter row (type, status, responsible, date range), overdue visual highlighting, quick-complete action, and MUI dialogs for create/edit/delete operations.

## Relevant Files
Use these files to implement the feature:

**Existing files to modify:**
- `apps/Client/src/pages/restaurantos/RestaurantOSEventsPage.tsx` — Replace placeholder with full CRUD page

**Reference files (read for patterns, do not modify):**
- `apps/Client/src/services/personService.ts` — Service pattern with try/catch and console logging
- `apps/Client/src/hooks/usePersons.ts` — Custom CRUD hook pattern with useState/useCallback/useEffect
- `apps/Client/src/components/forms/TRPersonForm.tsx` — Form pattern with react-hook-form, Controller for selects, create/edit modes
- `apps/Client/src/components/ui/TRExpirationBadge.tsx` — Status badge chip pattern with color-coded Chip component
- `apps/Client/src/pages/restaurantos/RestaurantOSPersonsPage.tsx` — Table-based CRUD page pattern with dialogs, filters, loading/empty states
- `apps/Client/src/contexts/RestaurantContext.tsx` — RestaurantContext providing currentRestaurant
- `apps/Client/src/hooks/useRestaurant.ts` — useRestaurant hook
- `apps/Client/src/pages/restaurantos/TRNoRestaurantPrompt.tsx` — No-restaurant guard component
- `apps/Client/src/api/clients/index.ts` — apiClient with JWT interceptor
- `apps/Client/src/types/person.ts` — Person type for responsible person dropdown
- `apps/Client/src/App.tsx` — Route already registered at line 218-226, no changes needed
- `apps/Server/src/interface/event_dto.py` — Backend DTOs defining field constraints and enums (EventType, EventFrequency, EventStatus)
- `apps/Server/src/adapter/rest/event_routes.py` — Backend API endpoints for reference

**Conditional documentation files (read before implementation):**
- `app_docs/feature-dc999a0b-event-entity-crud-backend.md` — Event backend API documentation
- `app_docs/feature-07ac42cd-task-assignment-recurrence.md` — Task assignment and recurrence documentation
- `app_docs/feature-342b3948-restaurant-selector-multitenant-navigation.md` — RestaurantContext and navigation documentation
- `app_docs/feature-de82eb81-person-management-page.md` — Person management page pattern documentation

**E2E test reference files (read for E2E test creation):**
- `.claude/commands/test_e2e.md` — E2E test runner instructions
- `.claude/commands/e2e/test_person_management.md` — E2E test format for CRUD page (best reference)
- `.claude/commands/e2e/test_document_management.md` — E2E test format for CRUD page with badges

### New Files
- `apps/Client/src/types/event.ts` — Event, EventCreate, EventUpdate, EventFilters interfaces and EventType/EventFrequency/EventStatus types
- `apps/Client/src/services/eventService.ts` — Event API service with getAll, create, update, updateStatus, delete methods
- `apps/Client/src/hooks/useEvents.ts` — Custom hook for event CRUD state management with filters
- `apps/Client/src/components/forms/TREventForm.tsx` — react-hook-form event form with create/edit modes and conditional validation
- `apps/Client/src/components/ui/TREventStatusBadge.tsx` — Color-coded status chip (Pendiente/Completado/Vencido)
- `.claude/commands/e2e/test_event_task_management.md` — E2E test specification for event/task management page

## Implementation Plan
### Phase 1: Foundation
Create the TypeScript types and API service layer. Define the Event interface matching the backend EventResponseDTO, plus EventCreate, EventUpdate, EventStatusUpdate, and EventFilters interfaces. Define union types for EventType, EventFrequency, and EventStatus. Create the eventService with methods mapping to each backend endpoint. Create the TREventStatusBadge component.

### Phase 2: Core Implementation
Build the useEvents custom hook following the usePersons pattern — managing events state, loading, errors, filters (type, status, responsibleId, dateFrom, dateTo), and CRUD operations scoped to a restaurantId. Then build the TREventForm component with react-hook-form, supporting both create and edit modes with Spanish labels, conditional validation (responsible_id required when type=tarea), and select fields for type, frequency, and notification channel. Also fetch persons list for the responsible person dropdown.

### Phase 3: Integration
Replace the RestaurantOSEventsPage placeholder with a full CRUD page featuring a data table grouped by date, overdue row highlighting (red background), multi-filter row, quick-complete action button (checkmark icon that calls updateStatus), and dialog-based forms for create/edit/delete. The route `/poc/restaurant-os/events` is already registered in App.tsx. Create the E2E test specification. Run all validation commands.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` to understand the E2E test runner
- Read `.claude/commands/e2e/test_person_management.md` and `.claude/commands/e2e/test_document_management.md` for CRUD test patterns
- Create `.claude/commands/e2e/test_event_task_management.md` with the following test flow:
  - Prerequisites: backend at http://localhost:8000, frontend at http://localhost:5173, logged-in user, at least one restaurant created, at least one person created (for responsible assignment)
  - Navigate to `/poc/restaurant-os/events`
  - Verify page loads with "Eventos / Tareas" heading, current restaurant name, "Agregar Evento" button, and empty state
  - Click "Agregar Evento", verify form dialog with fields: Tipo (select), Descripción, Fecha (datetime), Frecuencia (select), Responsable (person select), Canal de Notificación (select)
  - Test form validation: submit empty form, verify "El tipo es obligatorio" and "La fecha es obligatoria" errors
  - Test conditional validation: select type "Tarea", verify "El responsable es obligatorio" error appears on submit without responsible
  - Fill form: type "Tarea", description "Limpiar cocina", date (today), frequency "Diario", responsible (first person), notification "email"
  - Submit and verify event appears in table with correct data and "Pendiente" status badge (blue)
  - Create a second event: type "Vencimiento", description "Permiso sanitario", date (past date), frequency "Sin repetición"
  - Verify second event shows "Vencido" status badge (red) and row has red highlight
  - Test filter by type: select "Tarea" from type filter, verify only task shows
  - Test filter by status: select "Pendiente" from status filter, verify only pending events show
  - Test quick-complete: click checkmark icon on "Limpiar cocina", verify status changes to "Completado" (green badge)
  - Test edit: click edit on "Permiso sanitario", verify form pre-populated, change description to "Permiso sanitario 2025", submit, verify updated in table
  - Test delete: click delete, verify confirmation dialog "¿Está seguro que desea eliminar este evento?", confirm, verify removed from table
  - Success criteria: all CRUD operations work, quick-complete works, Spanish labels displayed, filters functional, overdue highlighting works, console shows INFO logs

### Step 2: Read Conditional Documentation
- Read `app_docs/feature-dc999a0b-event-entity-crud-backend.md` for backend Event API details
- Read `app_docs/feature-07ac42cd-task-assignment-recurrence.md` for task assignment and recurrence rules
- Read `app_docs/feature-342b3948-restaurant-selector-multitenant-navigation.md` for RestaurantContext patterns
- Read `app_docs/feature-de82eb81-person-management-page.md` for person page patterns to follow

### Step 3: Create Event Types
- Create `apps/Client/src/types/event.ts` with:
  - `EventType` union type: `'tarea' | 'vencimiento' | 'pago' | 'turno' | 'checklist' | 'alerta_stock' | 'alerta_rentabilidad'`
  - `EventFrequency` union type: `'none' | 'daily' | 'weekly' | 'monthly' | 'yearly'`
  - `EventStatus` union type: `'pending' | 'completed' | 'overdue'`
  - `Event` interface matching backend EventResponseDTO: `id` (string), `restaurant_id` (string), `type` (EventType), `description` (string | null), `date` (string), `frequency` (EventFrequency), `responsible_id` (string | null), `notification_channel` (string), `status` (EventStatus), `related_document_id` (string | null), `parent_event_id` (string | null), `completed_at` (string | null), `is_overdue` (boolean), `created_at` (string), `updated_at` (string | null)
  - `EventCreate` interface: `restaurant_id` (string), `type` (EventType), `date` (string), `description` (string, optional), `frequency` (EventFrequency, optional, default none), `responsible_id` (string, optional), `notification_channel` (string, optional, default email), `related_document_id` (string, optional)
  - `EventUpdate` interface: all fields optional — `type`, `description`, `date`, `frequency`, `responsible_id`, `notification_channel`, `related_document_id`
  - `EventStatusUpdate` interface: `status` (EventStatus)
  - `EventFilters` interface: `type` (EventType, optional), `status` (EventStatus, optional), `responsible_id` (string, optional), `date_from` (string, optional), `date_to` (string, optional)
  - `EVENT_TYPE_OPTIONS` constant array: `[{ value: 'tarea', label: 'Tarea' }, { value: 'vencimiento', label: 'Vencimiento' }, { value: 'pago', label: 'Pago' }, { value: 'turno', label: 'Turno' }, { value: 'checklist', label: 'Checklist' }]` (exclude alerta_stock and alerta_rentabilidad as they are system-generated)
  - `EVENT_FREQUENCY_OPTIONS` constant array: `[{ value: 'none', label: 'Sin repetición' }, { value: 'daily', label: 'Diario' }, { value: 'weekly', label: 'Semanal' }, { value: 'monthly', label: 'Mensual' }, { value: 'yearly', label: 'Anual' }]`
  - `EVENT_STATUS_OPTIONS` constant array: `[{ value: 'pending', label: 'Pendiente' }, { value: 'completed', label: 'Completado' }, { value: 'overdue', label: 'Vencido' }]`
  - `NOTIFICATION_CHANNEL_OPTIONS` constant array: `[{ value: 'email', label: 'Email' }, { value: 'whatsapp', label: 'WhatsApp' }, { value: 'push', label: 'Push' }]`

### Step 4: Create Event Service
- Read `apps/Client/src/services/personService.ts` for the service pattern
- Create `apps/Client/src/services/eventService.ts` following the personService pattern:
  - Import `apiClient` from `@/api/clients`
  - Import event types from `@/types/event`
  - `getAll(restaurantId: string, filters?: EventFilters): Promise<Event[]>` — GET `/events?restaurant_id={restaurantId}` with optional query params: `type`, `status`, `date_from`, `date_to`, `responsible_id`. Build params object conditionally from filters.
  - `create(data: EventCreate): Promise<Event>` — POST `/events`
  - `update(id: string, data: EventUpdate): Promise<Event>` — PUT `/events/{id}`
  - `updateStatus(id: string, data: EventStatusUpdate): Promise<Event>` — PATCH `/events/{id}/status`
  - `delete(id: string): Promise<void>` — DELETE `/events/{id}`
  - All methods wrapped in try/catch with `console.log('INFO [EventService]: ...')` and `console.error('ERROR [EventService]: ...')`
  - Export as `eventService` object and `default`

### Step 5: Create TREventStatusBadge Component
- Read `apps/Client/src/components/ui/TRExpirationBadge.tsx` for the badge pattern
- Create `apps/Client/src/components/ui/TREventStatusBadge.tsx`:
  - Props interface `TREventStatusBadgeProps`: `status` (EventStatus)
  - `STATUS_CONFIG` record mapping: `pending` → `{ label: 'Pendiente', color: 'info' }`, `completed` → `{ label: 'Completado', color: 'success' }`, `overdue` → `{ label: 'Vencido', color: 'error' }`
  - Render MUI `<Chip>` with label, color, and size="small"
  - Console.log on render: `INFO [TREventStatusBadge]: Rendering status: {status}`
  - Export as named `TREventStatusBadge` and `default`

### Step 6: Create useEvents Hook
- Read `apps/Client/src/hooks/usePersons.ts` for the hook pattern
- Create `apps/Client/src/hooks/useEvents.ts`:
  - Accept `restaurantId: string | null` parameter
  - State: `events` (Event[]), `isLoading` (boolean), `error` (string | null), `filters` (EventFilters)
  - `fetchEvents` — useCallback, guards on `!restaurantId`, calls `eventService.getAll(restaurantId, filters)`, with INFO/ERROR logging
  - `createEvent(data: EventCreate)` — useCallback, calls `eventService.create(data)`, then `fetchEvents()` to refresh
  - `updateEvent(id: string, data: EventUpdate)` — useCallback, calls `eventService.update(id, data)`, then `fetchEvents()` to refresh
  - `updateEventStatus(id: string, status: EventStatus)` — useCallback, calls `eventService.updateStatus(id, { status })`, then `fetchEvents()` to refresh. This is used by the quick-complete button.
  - `deleteEvent(id: string)` — useCallback, calls `eventService.delete(id)`, then `fetchEvents()` to refresh
  - `setFilters` — to update filters (type, status, responsibleId, dateFrom, dateTo)
  - useEffect to auto-fetch when `restaurantId` or `filters` change
  - Return `UseEventsResult` interface with all state and methods
  - Export as named `useEvents` and default

### Step 7: Create TREventForm Component
- Read `apps/Client/src/components/forms/TRPersonForm.tsx` for the form pattern
- Create `apps/Client/src/components/forms/TREventForm.tsx`:
  - Props interface `TREventFormProps`: `onSubmit` (async function receiving EventCreate | EventUpdate), `initialData` (Event, optional for edit mode), `restaurantId` (string), `persons` (Person[] for responsible dropdown), `onCancel` (function), `isSubmitting` (boolean, optional)
  - Internal form data interface `EventFormData`: `type` (string), `description` (string), `date` (string), `frequency` (string), `responsible_id` (string), `notification_channel` (string)
  - Use `useForm<EventFormData>` with `defaultValues` from `initialData` or sensible defaults (type empty, frequency 'none', notification_channel 'email')
  - Use `useEffect` to `reset` form when `initialData` changes
  - Use `watch('type')` to conditionally require `responsible_id` when type is 'tarea'
  - Fields (all Spanish labels):
    - `type`: Controller + Select, required, label "Tipo", options from EVENT_TYPE_OPTIONS, register with `{ required: 'El tipo es obligatorio' }`
    - `description`: TextField, optional, multiline (2 rows), label "Descripción"
    - `date`: TextField type="datetime-local", required, label "Fecha", register with `{ required: 'La fecha es obligatoria' }`, use InputLabelProps shrink for datetime-local
    - `frequency`: Controller + Select, label "Frecuencia", options from EVENT_FREQUENCY_OPTIONS, default 'none'
    - `responsible_id`: Controller + Select, label "Responsable", options from persons prop (map person.id → person.name), conditionally required when type='tarea' with message 'El responsable es obligatorio para tareas'
    - `notification_channel`: Controller + Select, label "Canal de Notificación", options from NOTIFICATION_CHANNEL_OPTIONS, default 'email'
  - Submit handler: builds EventCreate (with `restaurant_id`) or EventUpdate based on `isEditMode`. Convert empty strings to undefined for optional fields.
  - Buttons: "Cancelar" (outlined, type button) and "Agregar Evento" / "Actualizar Evento" (contained, type submit)
  - Loading state: disable fields and show CircularProgress in submit button when `isSubmitting`
  - Console.log on submit: `INFO [TREventForm]: Submitting event form`

### Step 8: Build RestaurantOSEventsPage
- Read `apps/Client/src/pages/restaurantos/RestaurantOSPersonsPage.tsx` for the table-based CRUD page pattern
- Read `apps/Client/src/pages/restaurantos/RestaurantOSEventsPage.tsx` (current placeholder)
- Replace the placeholder with a full CRUD page:
  - Use `useRestaurant()` for `currentRestaurant`, `restaurants`, `isLoading`
  - Use `useEvents(currentRestaurant?.id ?? null)` for event data and operations
  - Use `usePersons(currentRestaurant?.id ?? null)` for persons list (responsible dropdown in form and display)
  - State: `isAddDialogOpen`, `isEditDialogOpen`, `isDeleteDialogOpen`, `selectedEvent` (Event | null), `isSubmitting`, `typeFilter` (string), `statusFilter` (string), `responsibleFilter` (string), `dateFromFilter` (string), `dateToFilter` (string)
  - Guards:
    - Loading: show `CircularProgress` with "Cargando..."
    - No restaurants: show `<TRNoRestaurantPrompt />`
  - Header: "Eventos / Tareas" (h4), current restaurant name (h6), "Agregar Evento" button (contained, Add icon)
  - Error display: `<Alert severity="error">` when `error` is set
  - Filters row (responsive flex with gap):
    - Type filter: Select with label "Filtrar por tipo", options: "Todos" (empty value) plus EVENT_TYPE_OPTIONS, onChange calls `setFilters` with type
    - Status filter: Select with label "Filtrar por estado", options: "Todos" (empty value) plus EVENT_STATUS_OPTIONS, onChange calls `setFilters` with status
    - Responsible filter: Select with label "Filtrar por responsable", options: "Todos" (empty value) plus persons mapped to id/name, onChange calls `setFilters` with responsible_id
    - Date from: TextField type="date", label "Desde", InputLabelProps shrink, onChange calls `setFilters` with date_from
    - Date to: TextField type="date", label "Hasta", InputLabelProps shrink, onChange calls `setFilters` with date_to
  - Group events by date: use `useMemo` to group events array by date (extract YYYY-MM-DD from event.date). Sort groups chronologically. Each group has a date header row.
  - Data table (`<Table>` / `<TableContainer>`):
    - For each date group, render a date header row (spanning all columns, e.g., "Lunes 03 Mar 2025" or formatted date string)
    - Headers: Fecha, Tipo, Descripción, Responsable, Estado, Acciones
    - Rows: display event data
    - Fecha column: format time portion (HH:MM) from event.date
    - Tipo column: map type value to Spanish label using EVENT_TYPE_OPTIONS lookup
    - Descripción column: show event.description or '—'
    - Responsable column: look up person name from persons array by responsible_id, or '—'
    - Estado column: render `<TREventStatusBadge status={event.status} />`
    - Acciones column:
      - Quick-complete button: IconButton with CheckCircle icon, only shown when `event.status === 'pending'`, onClick calls `handleQuickComplete(event.id)` which calls `updateEventStatus(event.id, 'completed')`
      - Edit button: IconButton with Edit icon, onClick opens edit dialog
      - Delete button: IconButton with Delete icon, color="error", onClick opens delete dialog
    - Overdue row highlighting: apply `sx={{ backgroundColor: 'error.light', opacity: 0.15 }}` or similar to TableRow when `event.is_overdue || event.status === 'overdue'`. Use a subtle red tint that doesn't obscure text: `sx={{ bgcolor: event.is_overdue ? 'rgba(211, 47, 47, 0.08)' : 'inherit' }}`
  - Empty state: "No se encontraron eventos" when events list is empty
  - Add Dialog: MUI Dialog with title "Agregar Evento", `<TREventForm>` with `restaurantId`, `persons`, `onSubmit` calls `createEvent` then closes dialog
  - Edit Dialog: MUI Dialog with title "Editar Evento", `<TREventForm>` with `initialData={selectedEvent}`, `persons`, `onSubmit` calls `updateEvent` then closes dialog
  - Delete Dialog: MUI Dialog with title "Eliminar Evento", body text "¿Está seguro que desea eliminar este evento?", "Cancelar" and "Eliminar" buttons, confirm calls `deleteEvent(selectedEvent.id)` then closes
  - Console.log on all operations: `INFO [RestaurantOSEventsPage]: ...`

### Step 9: Run Validation Commands
- Run `cd apps/Client && npx tsc --noEmit` to validate TypeScript compilation with zero errors
- Run `cd apps/Client && npm run build` to validate production build succeeds
- Run `cd apps/Server && python -m pytest tests/ -x` to verify no backend regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_event_task_management.md` E2E test to validate the feature end-to-end

## Testing Strategy
### Unit Tests
No dedicated unit test files are required for this feature — the existing codebase convention for frontend CRUD pages relies on E2E tests for validation rather than unit tests. The TypeScript compiler (`tsc --noEmit`) validates type correctness across all new files.

### Edge Cases
- No restaurant selected: page shows `TRNoRestaurantPrompt`
- Empty events list: page shows "No se encontraron eventos" message
- Filters with no results: filtered table shows empty state
- Type=tarea without responsible_id: form shows "El responsable es obligatorio para tareas" validation error
- Overdue event highlighting: events with is_overdue=true or status='overdue' get red background tint
- Quick-complete on non-pending event: button only shown for pending events
- Empty persons list: responsible dropdown shows no options (user must create persons first)
- Date range filters: date_from and date_to correctly scope events
- API error on CRUD operations: error state shown via Alert component
- Delete confirmation: cancel should not delete, confirm should remove and refresh
- Event with no description: shows '—' in description column
- Event with no responsible: shows '—' in responsible column

## Acceptance Criteria
- Event/Task Management page loads at `/poc/restaurant-os/events` with "Eventos / Tareas" heading
- Page shows current restaurant name from RestaurantContext
- No-restaurant state shows `TRNoRestaurantPrompt` component
- Data table displays events grouped by date with columns: Fecha, Tipo, Descripción, Responsable, Estado, Acciones
- Overdue events are visually highlighted with red background tint
- "Agregar Evento" button opens a dialog with TREventForm
- Form fields: Tipo (required select), Descripción (optional textarea), Fecha (required datetime), Frecuencia (select), Responsable (person select, required for tarea), Canal de Notificación (select)
- Form validation prevents submission with missing required fields
- Conditional validation: responsible_id required when type='tarea'
- Creating an event adds it to the table
- Quick-complete button (checkmark icon) on pending events changes status to completed
- Edit button opens form pre-populated with event data
- Updating an event reflects changes in the table
- Delete button shows confirmation dialog with "¿Está seguro que desea eliminar este evento?"
- Confirming delete removes event from table
- Filter by type dropdown works (Todos/Tarea/Vencimiento/Pago/Turno/Checklist)
- Filter by status dropdown works (Todos/Pendiente/Completado/Vencido)
- Filter by responsible person dropdown works
- Filter by date range works
- TREventStatusBadge shows correct colors: blue (Pendiente), green (Completado), red (Vencido)
- All UI labels are in Spanish (Colombian)
- Console shows INFO log messages for all operations
- TypeScript compiles with zero errors
- Production build succeeds

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate zero TypeScript errors
- `cd apps/Client && npm run build` — Run Client production build to validate the feature compiles correctly
- `cd apps/Server && python -m pytest tests/ -x` — Run Server tests to validate no backend regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_event_task_management.md` E2E test to validate this functionality works end-to-end

## Notes
- The backend Event API is fully implemented (ROS-005 + ROS-007). All endpoints are operational: POST/GET/GET(due)/GET(by-id)/PUT/PATCH(status)/DELETE on `/api/events`, plus POST/GET on `/api/events/tasks` and POST on `/api/events/tasks/flag-overdue`.
- The route `/poc/restaurant-os/events` is already registered in `App.tsx` (lines 218-226) with the import for `RestaurantOSEventsPage`. No routing changes are needed.
- The `TRNoRestaurantPrompt` component already exists and is imported in the current placeholder page.
- Event type values are stored as lowercase (`tarea`, `vencimiento`, `pago`, `turno`, `checklist`) but displayed in Spanish with capital first letter (`Tarea`, `Vencimiento`, `Pago`, `Turno`, `Checklist`).
- The `alerta_stock` and `alerta_rentabilidad` event types are system-generated by automation flows and should not appear in the form dropdown, but should render correctly in the table if they exist.
- The `responsible_id` field links to the Person entity. The page uses `usePersons` to fetch the persons list for both the form dropdown and the table display of responsible person names.
- The quick-complete action uses the PATCH `/events/{id}/status` endpoint with `{ status: 'completed' }`.
- Date grouping is implemented client-side by extracting the date portion (YYYY-MM-DD) from each event's datetime string and grouping events under date headers.
- This feature runs in parallel with ROS-009, ROS-010, ROS-011, ROS-013. No conflicts expected since each page is in its own file.
- The `useEvents` hook passes all filters to the backend API as query parameters, enabling server-side filtering for type, status, responsible_id, date_from, and date_to.
