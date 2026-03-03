# E2E Test: Person Management

Test that the RestaurantOS person management page works correctly, including listing, creating, editing, and deleting persons (employees, suppliers, owners) within a restaurant.

## User Story

As a restaurant manager
I want to list, create, edit, and delete persons associated with my restaurant
So that I can maintain an up-to-date registry of employees, suppliers, and owners

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials and is logged in
- At least one restaurant created in the system

## Test Steps

### Setup - Navigate to Persons Page

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. If not logged in, log in with test credentials
3. Navigate to `/poc/restaurant-os/persons`
4. Take a screenshot of the persons page
5. **Verify** page loads with:
   - "Personas" heading (h4)
   - Current restaurant name displayed (h6)
   - "Agregar Persona" button is visible
   - Empty state message "No se encontraron personas" or existing persons table

### Test: Empty State

6. **Verify** if no persons exist:
   - Empty state message "No se encontraron personas" is displayed
7. Take a screenshot of empty state

### Test: Create Person - Form Validation

8. Click "Agregar Persona" button
9. Take a screenshot of the add person dialog
10. **Verify** dialog displays with title "Agregar Persona" and form fields:
    - Nombre (text, required)
    - Rol (text, required)
    - Tipo (select: Empleado/Proveedor/Dueño)
    - Correo Electrónico (email, optional)
    - WhatsApp (text, optional)
    - "Cancelar" and "Agregar Persona" buttons

11. Submit the form without filling required fields
12. Take a screenshot
13. **Verify** validation errors displayed:
    - "El nombre es obligatorio" error on Nombre field
    - "El rol es obligatorio" error on Rol field

### Test: Create First Person

14. Fill in the person form:
    - Nombre: "Carlos García"
    - Rol: "Chef"
    - Tipo: Select "Empleado" (employee)
    - Correo Electrónico: "carlos@test.com"
    - WhatsApp: "+573001234567"

15. Click "Agregar Persona" submit button
16. Take a screenshot
17. **Verify** dialog closes
18. **Verify** person appears in the data table with:
    - Nombre: "Carlos García"
    - Rol: "Chef"
    - Tipo: "Empleado"
    - Correo Electrónico: "carlos@test.com"
    - WhatsApp: "+573001234567"
    - Edit and Delete action buttons visible

### Test: Create Second Person

19. Click "Agregar Persona" button
20. Fill in:
    - Nombre: "María López"
    - Rol: "Mesera"
    - Tipo: Select "Empleado"
21. Click "Agregar Persona" submit button
22. Take a screenshot
23. **Verify** both persons visible in the table

### Test: Search by Name

24. Locate the "Buscar por nombre" search field
25. Type "Carlos" in the search field
26. Take a screenshot
27. **Verify** only "Carlos García" appears in the table
28. **Verify** "María López" is not visible

29. Clear the search field
30. **Verify** both persons are visible again

### Test: Filter by Type

31. Locate the "Filtrar por tipo" select dropdown
32. Select "Empleado" from the type filter
33. Take a screenshot
34. **Verify** both persons show (both are Empleado type)

35. Select "Proveedor" from the type filter
36. Take a screenshot
37. **Verify** no persons shown (empty state) or only supplier-type persons

38. Select "Todos" to reset the filter
39. **Verify** all persons visible again

### Test: Edit Person

40. Click the Edit button (pencil icon) on "Carlos García"
41. Take a screenshot of the edit dialog
42. **Verify** dialog title is "Editar Persona"
43. **Verify** form is pre-populated with Carlos's data:
    - Nombre: "Carlos García"
    - Rol: "Chef"
    - Tipo: "Empleado"
    - Correo Electrónico: "carlos@test.com"
    - WhatsApp: "+573001234567"

44. Change Rol from "Chef" to "Chef Principal"
45. Click "Actualizar Persona" submit button
46. Take a screenshot
47. **Verify** dialog closes
48. **Verify** table shows updated role "Chef Principal" for Carlos García

### Test: Delete Person

49. Click the Delete button (trash icon) on "María López"
50. Take a screenshot of the delete confirmation dialog
51. **Verify** dialog title is "Eliminar Persona"
52. **Verify** confirmation text: "¿Está seguro que desea eliminar esta persona?"
53. **Verify** "Cancelar" and "Eliminar" buttons visible

54. Click "Cancelar" to abort deletion
55. **Verify** María López still in the table

56. Click Delete button on "María López" again
57. Click "Eliminar" to confirm
58. Take a screenshot
59. **Verify** María López removed from table
60. **Verify** only Carlos García remains

### Test: No Restaurant State

61. If possible, test with no restaurant selected
62. **Verify** `TRNoRestaurantPrompt` component is shown instead of the persons page

## Success Criteria

- Persons page loads at `/poc/restaurant-os/persons` with "Personas" heading
- Page shows current restaurant name from RestaurantContext
- No-restaurant state shows TRNoRestaurantPrompt component
- Data table displays persons with columns: Nombre, Rol, Tipo, Correo Electrónico, WhatsApp, Acciones
- "Agregar Persona" button opens dialog with TRPersonForm
- Form fields: Nombre (required), Rol (required), Tipo (select), Correo Electrónico (optional), WhatsApp (optional)
- Form validation prevents submission with missing required fields
- Creating a person adds it to the table
- Edit button opens form pre-populated with person data
- Updating a person reflects changes in the table
- Delete button shows confirmation dialog with Spanish text
- Confirming delete removes person from table
- Search by name filters the table (case-insensitive)
- Type filter dropdown filters by Todos/Empleado/Proveedor/Dueño
- All UI labels are in Spanish (Colombian)
- Console shows INFO log messages for all operations

## Technical Verification

- Check browser console for:
  - INFO log messages for person operations
  - `INFO [PersonService]: Fetching persons for restaurant...`
  - `INFO [usePersons]: Fetched X persons`
  - `INFO [TRPersonForm]: Submitting person form`
  - `INFO [RestaurantOSPersonsPage]: Creating person`
  - No JavaScript errors
  - No React warnings
- Check network requests:
  - GET `/api/persons?restaurant_id=...` on page load
  - POST `/api/persons` on create
  - PUT `/api/persons/{id}` on update
  - DELETE `/api/persons/{id}` on delete
  - Authorization header present in all requests

## Notes

- The backend Person API is fully implemented (all CRUD endpoints operational)
- Person type values are stored as lowercase English (`employee`, `supplier`, `owner`) but displayed in Spanish (`Empleado`, `Proveedor`, `Dueño`)
- Search is client-side (filters the loaded persons array by name)
- The type filter is server-side (passed as query parameter to the API)
- Route `/poc/restaurant-os/persons` is already registered in App.tsx
