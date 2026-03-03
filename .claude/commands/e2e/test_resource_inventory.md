# E2E Test: Resource & Inventory Management

Test that the RestaurantOS resource and inventory management page works correctly, including listing resources, creating/editing/deleting resources, registering inventory movements, filtering, and viewing resource detail with movement history.

## User Story

As a restaurant manager
I want to manage my resources (products, assets, services) and track inventory movements
So that I can monitor stock levels, identify low-stock items, and maintain a complete movement history for each resource

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials and is logged in
- At least one restaurant created in the system

## Test Steps

### Setup - Navigate to Resources Page

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. If not logged in, log in with test credentials
3. Navigate to `/poc/restaurant-os/resources`
4. Take a screenshot of the resources page
5. **Verify** page loads with:
   - "Recursos / Inventario" heading (h4)
   - Current restaurant name displayed (h6)
   - "Agregar Recurso" button is visible
   - "Registrar Movimiento" button is visible
   - Empty state message "No se encontraron recursos" or existing resources table

### Test: Empty State

6. **Verify** if no resources exist:
   - Empty state message "No se encontraron recursos" is displayed
7. Take a screenshot of empty state

### Test: Create Resource - Form Validation

8. Click "Agregar Recurso" button
9. Take a screenshot of the add resource dialog
10. **Verify** dialog displays with title "Agregar Recurso" and form fields:
    - Nombre (text, required)
    - Tipo (select: Producto/Activo/Servicio)
    - Unidad (text, required)
    - Stock Actual (number, >= 0)
    - Stock Mínimo (number, >= 0)
    - Último Costo Unitario (number, >= 0)
    - "Cancelar" and "Agregar Recurso" buttons

11. Clear the Nombre field and submit the form
12. Take a screenshot
13. **Verify** validation errors displayed:
    - "El nombre es obligatorio" error on Nombre field

### Test: Create First Resource (Normal Stock)

14. Fill in the resource form:
    - Nombre: "Arroz"
    - Tipo: Select "Producto"
    - Unidad: "kg"
    - Stock Actual: 50
    - Stock Mínimo: 10
    - Último Costo Unitario: 3500

15. Click "Agregar Recurso" submit button
16. Take a screenshot
17. **Verify** dialog closes
18. **Verify** resource appears in the data table with:
    - Nombre: "Arroz"
    - Tipo: "Producto"
    - Unidad: "kg"
    - Stock Actual: 50
    - Stock Mínimo: 10
    - Último Costo: formatted as COP currency
    - Estado: green "OK" chip (stock 50 > minimum 10)
    - Edit, Delete, and View action buttons visible

### Test: Create Second Resource (Low Stock)

19. Click "Agregar Recurso" button
20. Fill in:
    - Nombre: "Aceite de Oliva"
    - Tipo: Select "Producto"
    - Unidad: "litros"
    - Stock Actual: 2
    - Stock Mínimo: 5
    - Último Costo Unitario: 25000

21. Click "Agregar Recurso" submit button
22. Take a screenshot
23. **Verify** both resources visible in the table
24. **Verify** "Aceite de Oliva" shows red "Stock Bajo" chip (stock 2 < minimum 5)

### Test: Create Third Resource (Different Type)

25. Click "Agregar Recurso" button
26. Fill in:
    - Nombre: "Horno Industrial"
    - Tipo: Select "Activo"
    - Unidad: "unidad"
    - Stock Actual: 1
    - Stock Mínimo: 1
    - Último Costo Unitario: 5000000

27. Click "Agregar Recurso" submit button
28. Take a screenshot
29. **Verify** three resources visible in the table
30. **Verify** "Horno Industrial" shows "OK" chip (stock 1 = minimum 1, NOT low stock)

### Test: Filter by Type

31. Locate the "Filtrar por tipo" select dropdown
32. Select "Producto" from the type filter
33. Take a screenshot
34. **Verify** only "Arroz" and "Aceite de Oliva" appear (both are Producto)
35. **Verify** "Horno Industrial" is not visible

36. Select "Activo" from the type filter
37. Take a screenshot
38. **Verify** only "Horno Industrial" appears

39. Select "Servicio" from the type filter
40. Take a screenshot
41. **Verify** no resources shown (empty state) since no services exist

42. Select "Todos" to reset the filter
43. **Verify** all three resources visible again

### Test: Search by Name

44. Locate the "Buscar por nombre" search field
45. Type "Arroz" in the search field
46. Take a screenshot
47. **Verify** only "Arroz" appears in the table
48. **Verify** "Aceite de Oliva" and "Horno Industrial" are not visible

49. Clear the search field
50. **Verify** all resources are visible again

### Test: Edit Resource

51. Click the Edit button (pencil icon) on "Arroz"
52. Take a screenshot of the edit dialog
53. **Verify** dialog title is "Editar Recurso"
54. **Verify** form is pre-populated with Arroz data:
    - Nombre: "Arroz"
    - Tipo: "Producto"
    - Unidad: "kg"
    - Stock Actual: 50
    - Stock Mínimo: 10

55. Change Stock Mínimo from 10 to 20
56. Click "Actualizar Recurso" submit button
57. Take a screenshot
58. **Verify** dialog closes
59. **Verify** table shows updated Stock Mínimo: 20 for "Arroz"
60. **Verify** "Arroz" still shows "OK" chip (stock 50 > minimum 20)

### Test: Register Inventory Movement (Entry)

61. Click "Registrar Movimiento" button
62. Take a screenshot of the movement dialog
63. **Verify** dialog title is "Registrar Movimiento"
64. **Verify** form fields:
    - Recurso (select: list of resources with stock info)
    - Tipo (select: Entrada/Salida)
    - Cantidad (number, required, > 0)
    - Razón (select: Compra/Uso/Producción/Merma/Receta/Ajuste)
    - Persona (optional select)
    - Notas (text, optional)

65. Fill in:
    - Recurso: Select "Arroz"
    - Tipo: Select "Entrada"
    - Cantidad: 25
    - Razón: Select "Compra"
    - Notas: "Compra semanal"

66. Click "Registrar Movimiento" submit button
67. Take a screenshot
68. **Verify** dialog closes
69. **Verify** "Arroz" Stock Actual updated from 50 to 75 in the table

### Test: Register Inventory Movement (Exit)

70. Click "Registrar Movimiento" button
71. Fill in:
    - Recurso: Select "Arroz"
    - Tipo: Select "Salida"
    - Cantidad: 10
    - Razón: Select "Uso"

72. Click "Registrar Movimiento" submit button
73. Take a screenshot
74. **Verify** dialog closes
75. **Verify** "Arroz" Stock Actual updated from 75 to 65 in the table

### Test: Exit Movement Stock Warning

76. Click "Registrar Movimiento" button
77. Select Recurso: "Aceite de Oliva" (stock: 2)
78. Select Tipo: "Salida"
79. Enter Cantidad: 5
80. Take a screenshot
81. **Verify** warning Alert is displayed about quantity exceeding current stock
82. Click "Cancelar" to close the dialog

### Test: Open Resource Detail Drawer

83. Click on the "Arroz" row in the table (or click the eye icon)
84. Take a screenshot of the detail drawer
85. **Verify** drawer opens from the right side with:
    - Resource name "Arroz" as heading
    - Type, Unit, Stock Actual, Stock Mínimo, Último Costo details
    - "OK" status chip
    - "Historial de Movimientos" heading
    - Movement history table with columns: Fecha, Tipo, Cantidad, Razón, Persona, Notas
    - At least 2 movements listed (the entry and exit created earlier)

86. **Verify** movement entries show:
    - One "Entrada" movement with quantity 25 and reason "Compra"
    - One "Salida" movement with quantity 10 and reason "Uso"

87. Close the drawer
88. Take a screenshot

### Test: Resource with No Movements

89. Click on "Horno Industrial" row to open detail drawer
90. Take a screenshot
91. **Verify** drawer shows resource details
92. **Verify** movement history shows "No hay movimientos registrados" message
93. Close the drawer

### Test: Delete Resource

94. Click the Delete button (trash icon) on "Aceite de Oliva"
95. Take a screenshot of the delete confirmation dialog
96. **Verify** dialog title is "Eliminar Recurso"
97. **Verify** confirmation text: "¿Está seguro que desea eliminar este recurso?"
98. **Verify** "Cancelar" and "Eliminar" buttons visible

99. Click "Cancelar" to abort deletion
100. **Verify** "Aceite de Oliva" still in the table

101. Click Delete button on "Aceite de Oliva" again
102. Click "Eliminar" to confirm
103. Take a screenshot
104. **Verify** "Aceite de Oliva" removed from table
105. **Verify** only "Arroz" and "Horno Industrial" remain

### Test: No Restaurant State

106. If possible, test with no restaurant selected
107. **Verify** `TRNoRestaurantPrompt` component is shown instead of the resources page

## Success Criteria

- ResourcesPage loads at `/poc/restaurant-os/resources` with "Recursos / Inventario" heading
- Page shows current restaurant name from RestaurantContext
- No-restaurant state shows TRNoRestaurantPrompt component
- Data table displays resources with columns: Nombre, Tipo, Unidad, Stock Actual, Stock Mínimo, Último Costo, Estado, Acciones
- Low-stock resources display red "Stock Bajo" chip; normal stock shows green "OK" chip
- Resource with current_stock == minimum_stock shows "OK" chip (not low stock)
- Type filter dropdown filters by Todos/Producto/Activo/Servicio
- Search by name filters the table client-side (case-insensitive)
- "Agregar Recurso" button opens dialog with TRResourceForm
- TRResourceForm validates: name and unit required, stock/cost values >= 0
- Creating a resource adds it to the table
- Edit button opens TRResourceForm pre-populated with resource data
- Updating a resource reflects changes in table
- Delete button shows Spanish confirmation dialog; confirming removes resource
- "Registrar Movimiento" button opens dialog with TRInventoryMovementForm
- TRInventoryMovementForm validates: quantity > 0, shows warning for stock-negative exits
- Creating a movement updates the resource's stock in the table
- Clicking a resource row opens detail drawer with resource info and movement history
- Movement history table shows: Fecha, Tipo, Cantidad, Razón, Persona, Notas
- All UI labels are in Spanish (Colombian)
- Console shows INFO log messages for all operations
- TypeScript compiles with zero errors
- Production build succeeds with zero errors
- Backend tests pass with zero regressions

## Technical Verification

- Check browser console for:
  - INFO log messages for resource and movement operations
  - `INFO [ResourceService]: Fetching resources for restaurant...`
  - `INFO [useResources]: Fetched X resources`
  - `INFO [TRResourceForm]: Submitting resource form`
  - `INFO [RestaurantOSResourcesPage]: Creating resource`
  - `INFO [InventoryMovementService]: Creating movement for resource...`
  - `INFO [useInventoryMovements]: Movement created successfully`
  - No JavaScript errors
  - No React warnings
- Check network requests:
  - GET `/api/resources?restaurant_id=...` on page load
  - GET `/api/resources?restaurant_id=...&type=...` when type filter applied
  - POST `/api/resources` on create
  - PUT `/api/resources/{id}` on update
  - DELETE `/api/resources/{id}` on delete
  - POST `/api/inventory-movements` on movement creation
  - GET `/api/inventory-movements?resource_id=...` when detail drawer opens
  - Authorization header present in all requests

## Notes

- The backend Resource API (`/api/resources`) and Inventory Movement API (`/api/inventory-movements`) are fully implemented
- Resource type values are stored as lowercase Spanish (`producto`, `activo`, `servicio`) and displayed capitalized
- Movement type values are stored as English (`entry`, `exit`) but displayed in Spanish (`Entrada`, `Salida`)
- Movement reason values are stored as lowercase Spanish (`compra`, `uso`, `produccion`, `merma`, `receta`, `ajuste`)
- `is_low_stock` is computed server-side: `current_stock < minimum_stock` (strictly less than)
- Search is client-side (filters the loaded resources array by name)
- The type filter is server-side (passed as query parameter to the API)
- Movement creation auto-updates resource stock on the backend
- Route `/poc/restaurant-os/resources` is already registered in App.tsx
