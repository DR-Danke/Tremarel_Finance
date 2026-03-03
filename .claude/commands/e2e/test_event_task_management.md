# E2E Test: Event / Task Management

Test that the RestaurantOS event/task management page works correctly, including listing, creating, editing, filtering, quick-completing, and deleting events/tasks within a restaurant, with overdue highlighting and status badges.

## User Story

As a restaurant manager
I want to view, create, edit, and manage events and tasks for my restaurant in a date-grouped list with quick actions
So that I can track deadlines, assign tasks to employees, and ensure nothing becomes overdue

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials and is logged in
- At least one restaurant created in the system
- At least one person created (for responsible assignment)

## Test Steps

### Setup - Navigate to Events Page

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. If not logged in, log in with test credentials
3. Navigate to `/poc/restaurant-os/events`
4. Take a screenshot of the events page
5. **Verify** page loads with:
   - "Eventos / Tareas" heading (h4)
   - Current restaurant name displayed (h6)
   - "Agregar Evento" button is visible
   - Empty state message "No se encontraron eventos" or existing events table

### Test: Empty State

6. **Verify** if no events exist:
   - Empty state message "No se encontraron eventos" is displayed
7. Take a screenshot of empty state

### Test: Create Event - Form Validation

8. Click "Agregar Evento" button
9. Take a screenshot of the add event dialog
10. **Verify** dialog displays with title "Agregar Evento" and form fields:
    - Tipo (select, required: Tarea/Vencimiento/Pago/Turno/Checklist)
    - Descripción (textarea, optional, multiline)
    - Fecha (datetime-local, required)
    - Frecuencia (select: Sin repetición/Diario/Semanal/Mensual/Anual)
    - Responsable (person select, optional)
    - Canal de Notificación (select: Email/WhatsApp/Push)
    - "Cancelar" and "Agregar Evento" buttons

11. Submit the form without filling required fields
12. Take a screenshot
13. **Verify** validation errors displayed:
    - "El tipo es obligatorio" error on Tipo field
    - "La fecha es obligatoria" error on Fecha field

### Test: Conditional Validation (Tarea requires Responsable)

14. Select Tipo: "Tarea"
15. Leave Responsable empty
16. Fill Fecha with today's date/time
17. Submit the form
18. Take a screenshot
19. **Verify** validation error: "El responsable es obligatorio para tareas"

### Test: Create First Event (Tarea)

20. Fill in the event form:
    - Tipo: "Tarea"
    - Descripción: "Limpiar cocina"
    - Fecha: today's date and time
    - Frecuencia: "Diario"
    - Responsable: select first person from dropdown
    - Canal de Notificación: "Email"
21. Click "Agregar Evento" submit button
22. Take a screenshot
23. **Verify** dialog closes
24. **Verify** event appears in the data table with:
    - Tipo: "Tarea"
    - Descripción: "Limpiar cocina"
    - Responsable: person name displayed
    - Estado: "Pendiente" status badge (blue/info color)
    - Quick-complete (checkmark), Edit, and Delete action buttons visible

### Test: Create Second Event (Vencimiento with past date)

25. Click "Agregar Evento" button
26. Fill in:
    - Tipo: "Vencimiento"
    - Descripción: "Permiso sanitario"
    - Fecha: a past date (e.g., 2025-01-01)
    - Frecuencia: "Sin repetición"
27. Click "Agregar Evento" submit button
28. Take a screenshot
29. **Verify** second event appears in the table with:
    - Estado: "Vencido" status badge (red/error color)
    - Row has red background highlight (overdue highlighting)

### Test: Status Badge Colors

30. **Verify** status badges display correct colors:
    - "Pendiente" badge is blue (info color) for pending events
    - "Vencido" badge is red (error color) for overdue events
31. Take a screenshot showing different badge colors

### Test: Date Grouping

32. **Verify** events are grouped by date in the table
33. **Verify** date header rows appear separating events by date
34. Take a screenshot

### Test: Filter by Type

35. Locate the "Filtrar por tipo" select dropdown
36. Select "Tarea" from the type filter
37. Take a screenshot
38. **Verify** only task events appear in the table ("Limpiar cocina")
39. **Verify** "Permiso sanitario" is not visible

40. Select "Todos" to reset the filter
41. **Verify** all events visible again

### Test: Filter by Status

42. Locate the "Filtrar por estado" select dropdown
43. Select "Pendiente" from the status filter
44. Take a screenshot
45. **Verify** only pending events appear

46. Select "Vencido" from the status filter
47. Take a screenshot
48. **Verify** only overdue events appear

49. Select "Todos" to reset the filter
50. **Verify** all events visible again

### Test: Quick-Complete

51. Locate the quick-complete button (checkmark icon) on "Limpiar cocina"
52. Click the checkmark icon
53. Take a screenshot
54. **Verify** status changes to "Completado" (green/success badge)
55. **Verify** quick-complete button is no longer visible for this event (only shown for pending)

### Test: Edit Event

56. Click the Edit button (pencil icon) on "Permiso sanitario"
57. Take a screenshot of the edit dialog
58. **Verify** dialog title is "Editar Evento"
59. **Verify** form is pre-populated with event data:
    - Tipo: "Vencimiento"
    - Descripción: "Permiso sanitario"
    - Frecuencia: "Sin repetición"

60. Change Descripción to "Permiso sanitario 2025"
61. Click "Actualizar Evento" submit button
62. Take a screenshot
63. **Verify** dialog closes
64. **Verify** table shows updated description "Permiso sanitario 2025"

### Test: Delete Event

65. Click the Delete button (trash icon) on "Permiso sanitario 2025"
66. Take a screenshot of the delete confirmation dialog
67. **Verify** dialog title is "Eliminar Evento"
68. **Verify** confirmation text: "¿Está seguro que desea eliminar este evento?"
69. **Verify** "Cancelar" and "Eliminar" buttons visible

70. Click "Cancelar" to abort deletion
71. **Verify** event still in the table

72. Click Delete button on "Permiso sanitario 2025" again
73. Click "Eliminar" to confirm
74. Take a screenshot
75. **Verify** event removed from table

### Test: No Restaurant State

76. If possible, test with no restaurant selected
77. **Verify** `TRNoRestaurantPrompt` component is shown instead of the events page

## Success Criteria

- Event/Task management page loads at `/poc/restaurant-os/events` with "Eventos / Tareas" heading
- Page shows current restaurant name from RestaurantContext
- No-restaurant state shows TRNoRestaurantPrompt component
- Data table displays events grouped by date with columns: Fecha, Tipo, Descripción, Responsable, Estado, Acciones
- Overdue events are visually highlighted with red background tint
- TREventStatusBadge shows correct colors: blue (Pendiente), green (Completado), red (Vencido)
- "Agregar Evento" button opens dialog with TREventForm
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
- All UI labels are in Spanish (Colombian)
- Console shows INFO log messages for all operations

## Technical Verification

- Check browser console for:
  - INFO log messages for event operations
  - `INFO [EventService]: Fetching events for restaurant...`
  - `INFO [useEvents]: Fetched X events`
  - `INFO [TREventForm]: Submitting event form`
  - `INFO [RestaurantOSEventsPage]: Creating event`
  - `INFO [TREventStatusBadge]: Rendering status: ...`
  - No JavaScript errors
  - No React warnings
- Check network requests:
  - GET `/api/events?restaurant_id=...` on page load
  - POST `/api/events` on create
  - PUT `/api/events/{id}` on update
  - PATCH `/api/events/{id}/status` on quick-complete
  - DELETE `/api/events/{id}` on delete
  - Authorization header present in all requests

## Notes

- The backend Event API is fully implemented (all CRUD endpoints operational)
- Event type values are stored as lowercase (`tarea`, `vencimiento`, `pago`, `turno`, `checklist`) but displayed in Spanish with capital first letter
- The `alerta_stock` and `alerta_rentabilidad` event types are system-generated and should not appear in the form dropdown, but render correctly in the table
- The `responsible_id` field links to the Person entity — the page uses `usePersons` to fetch persons for dropdown and display
- The quick-complete action uses PATCH `/events/{id}/status` with `{ status: 'completed' }`
- Date grouping is client-side by extracting YYYY-MM-DD from event datetime
- All filters (type, status, responsible_id, date_from, date_to) are server-side query parameters
- Route `/poc/restaurant-os/events` is already registered in App.tsx
