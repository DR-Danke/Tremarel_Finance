# E2E Test: ServiceDesk Technician Management

Test the admin-only technician management interface for ServiceDesk.

## User Story

As an admin user
I want to manage technician accounts from a dedicated interface
So that I can efficiently onboard new support staff, manage their expertise areas, and maintain account statuses

## Prerequisites

- User must be logged in with admin role
- Navigate to ServiceDesk module

## Test Steps

### Navigation and Access

1. Navigate to `/servicedesk/technicians`
2. Take a screenshot of the initial state
3. **Verify** the page title is "Gestión de Técnicos"
4. **Verify** core UI elements are present:
   - "Agregar Técnico" button (top right)
   - Search text field
   - Status filter dropdown
   - Data grid with technician list

### Data Grid Verification

5. **Verify** the data grid displays columns:
   - Nombre (full_name)
   - Email
   - Estado (Active/Inactive badge)
   - Rol
   - Tickets Activos (current_ticket_count)
   - Acciones (Edit, Toggle Status buttons)
6. Take a screenshot of the data grid

### Search Functionality

7. Enter "Juan" in the search field
8. **Verify** the grid filters to show only technicians with "Juan" in name or email
9. Clear the search field
10. **Verify** the full list is restored

### Status Filter

11. Select "Inactivo" in the status dropdown
12. **Verify** only inactive technicians are displayed
13. Select "Activo" in the status dropdown
14. **Verify** only active technicians are displayed
15. Click "Limpiar Filtros" button
16. **Verify** all technicians are displayed

### Create Technician Flow

17. Click "Agregar Técnico" button
18. **Verify** a dialog form opens with title "Nuevo Técnico"
19. Take a screenshot of the create form
20. **Verify** form fields are present:
    - Nombre completo (required)
    - Correo electrónico (required)
    - Teléfono (optional)
    - Rol (dropdown)
    - Activo (switch)
21. Leave all fields empty and click "Guardar"
22. **Verify** validation errors appear for required fields
23. Fill in the form:
    - Nombre completo: "Test Technician E2E"
    - Correo electrónico: "test.tech.e2e@example.com"
    - Rol: "technician"
24. Click "Guardar" button
25. **Verify** success message appears
26. **Verify** credentials dialog shows:
    - Username
    - Temporary password
    - Copy buttons
27. Take a screenshot of credentials dialog
28. Close the credentials dialog
29. **Verify** new technician appears in the grid

### Edit Technician Flow

30. Find the newly created technician in the grid
31. Click the Edit (pencil) icon in actions column
32. **Verify** dialog opens with title "Editar Técnico"
33. **Verify** form is pre-populated with technician data
34. Change the phone number to "+57 300 123 4567"
35. Click "Guardar" button
36. **Verify** success snackbar appears
37. **Verify** the grid updates with new data

### Toggle Status Flow

38. Find an active technician in the grid
39. Click the Toggle Status button in actions column
40. **Verify** confirmation dialog appears asking "¿Desactivar técnico?"
41. Click "Confirmar" button
42. **Verify** technician status changes to "Inactivo"
43. **Verify** success message appears
44. Click Toggle Status again
45. **Verify** confirmation dialog asks "¿Activar técnico?"
46. Click "Confirmar" button
47. **Verify** technician status changes to "Activo"

### Bulk Actions (if implemented)

48. Click checkbox on first technician row
49. Click checkbox on second technician row
50. **Verify** bulk action toolbar appears
51. Click "Desactivar Seleccionados" button
52. **Verify** confirmation dialog shows count of affected technicians
53. Click "Cancelar" to abort

### Error Handling

54. Disconnect network (or mock API error)
55. Attempt to load technicians
56. **Verify** error alert displays
57. Reconnect network
58. Click refresh button
59. **Verify** data loads successfully

## Success Criteria

- Page loads with data grid displaying technicians
- Search filters technicians by name/email
- Status dropdown filters by active status
- Create form validates required fields
- Create flow shows generated credentials
- Edit form pre-populates with existing data
- Toggle status shows confirmation and updates grid
- Error states display appropriately
- All UI text is in Spanish
- Only admin users can access this page
