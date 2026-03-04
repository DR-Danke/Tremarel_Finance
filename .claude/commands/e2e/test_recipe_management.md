# E2E Test: Recipe Management

Test that the RestaurantOS recipe management page works correctly, including listing recipes, creating/editing/deleting recipes with dynamic ingredients, profitability badges, production actions, and viewing recipe detail with ingredient breakdown.

## User Story

As a restaurant manager
I want to manage recipes and track profitability
So that I can optimize my menu, identify unprofitable dishes, and trigger ingredient deduction when producing dishes

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials and is logged in
- At least one restaurant created in the system
- At least two resources (ingredients) exist in the restaurant for recipe creation

## Test Steps

### Setup - Navigate to Recipes Page

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. If not logged in, log in with test credentials
3. Navigate to `/poc/restaurant-os/recipes`
4. Take a screenshot of the recipes page
5. **Verify** page loads with:
   - "Recetas" heading (h4)
   - Current restaurant name displayed (h6)
   - "Agregar Receta" button is visible
   - Empty state message "No se encontraron recetas" or existing recipes table

### Test: Empty State

6. **Verify** if no recipes exist:
   - Empty state message "No se encontraron recetas" is displayed
7. Take a screenshot of empty state

### Test: Create Recipe - Form Validation

8. Click "Agregar Receta" button
9. Take a screenshot of the add recipe dialog
10. **Verify** dialog displays with title "Agregar Receta" and form fields:
    - Nombre (text, required)
    - Precio de Venta (number, required, > 0)
    - Activo toggle (default checked)
    - Ingredients section with "Agregar Ingrediente" button
    - "Cancelar" and "Agregar Receta" buttons

11. Clear the Nombre field and submit the form
12. Take a screenshot
13. **Verify** validation errors displayed:
    - "El nombre es obligatorio" error on Nombre field

### Test: Create First Recipe

14. Fill in the recipe form:
    - Nombre: "Pasta Carbonara"
    - Precio de Venta: 35000

15. Click "Agregar Ingrediente" button
16. Select a resource from the ingredient selector (e.g., first available resource)
17. Enter quantity: 2
18. **Verify** unit is auto-filled from selected resource (read-only)

19. Click "Agregar Ingrediente" again to add a second ingredient
20. Select a different resource
21. Enter quantity: 1

22. **Verify** real-time cost and margin calculation displayed:
    - "Costo Estimado: $X" shows calculated cost
    - "Margen Estimado: X%" shows calculated margin

23. Click "Agregar Receta" submit button
24. Take a screenshot
25. **Verify** dialog closes
26. **Verify** recipe appears in the data table with columns:
    - Nombre: "Pasta Carbonara"
    - Precio Venta: formatted as COP currency
    - Costo Actual: formatted as COP currency
    - Margen %: percentage value
    - Rentabilidad: TRProfitabilityBadge (green "Rentable" or red "No Rentable")
    - Estado: green "Activa" chip
    - Acciones: Edit, Delete, "Producir" buttons

### Test: Profitability Badge

27. **Verify** TRProfitabilityBadge shows correct color:
    - Green chip with "Rentable (XX%)" if margin >= 60%
    - Red chip with "No Rentable (XX%)" if margin < 60%
28. Take a screenshot of the profitability badge

### Test: Recipe Detail Drawer

29. Click on the "Pasta Carbonara" row in the table
30. Take a screenshot of the detail drawer
31. **Verify** drawer opens from the right side with:
    - Recipe name "Pasta Carbonara" as heading
    - Sale price, current cost, margin percent details
    - TRProfitabilityBadge
    - "Ingredientes" heading
    - Ingredient breakdown table with columns: Ingrediente, Cantidad, Unidad, Costo Unitario
    - At least 2 ingredients listed

32. Close the drawer
33. Take a screenshot

### Test: Edit Recipe

34. Click the Edit button (pencil icon) on "Pasta Carbonara"
35. Take a screenshot of the edit dialog
36. **Verify** dialog title is "Editar Receta"
37. **Verify** form is pre-populated with recipe data:
    - Nombre: "Pasta Carbonara"
    - Precio de Venta: 35000
    - Existing ingredients listed

38. Change Precio de Venta from 35000 to 40000
39. Click "Actualizar Receta" submit button
40. Take a screenshot
41. **Verify** dialog closes
42. **Verify** table shows updated Precio Venta for "Pasta Carbonara"

### Test: Produce Recipe

43. Click the "Producir" button on "Pasta Carbonara"
44. Take a screenshot of the production dialog
45. **Verify** dialog shows:
    - Title: "Producir"
    - Text: "¿Cuántas porciones producir?"
    - Quantity input (number, min 1, default 1)
    - "Cancelar" and "Producir" buttons

46. Enter quantity: 2
47. Click "Producir" button
48. Take a screenshot
49. **Verify** production success or error handling:
    - If success: recipe list refreshes
    - If insufficient stock: error message displayed

### Test: Search by Name

50. Locate the "Buscar por nombre" search field
51. Type "Pasta" in the search field
52. Take a screenshot
53. **Verify** only recipes matching "Pasta" appear in the table

54. Clear the search field
55. **Verify** all recipes are visible again

### Test: Delete Recipe

56. Click the Delete button (trash icon) on "Pasta Carbonara"
57. Take a screenshot of the delete confirmation dialog
58. **Verify** dialog title is "Eliminar Receta"
59. **Verify** confirmation text: "¿Está seguro que desea eliminar esta receta?"
60. **Verify** "Cancelar" and "Eliminar" buttons visible

61. Click "Cancelar" to abort deletion
62. **Verify** "Pasta Carbonara" still in the table

63. Click Delete button on "Pasta Carbonara" again
64. Click "Eliminar" to confirm
65. Take a screenshot
66. **Verify** "Pasta Carbonara" removed from table

### Test: No Restaurant State

67. If possible, test with no restaurant selected
68. **Verify** `TRNoRestaurantPrompt` component is shown instead of the recipes page

## Success Criteria

- RecipesPage loads at `/poc/restaurant-os/recipes` with "Recetas" heading
- Page shows current restaurant name from RestaurantContext
- No-restaurant state shows TRNoRestaurantPrompt component
- "Recetas" navigation item appears in sidebar under POCs > RestaurantOS
- Data table displays recipes with columns: Nombre, Precio Venta, Costo Actual, Margen %, Rentabilidad, Estado, Acciones
- TRProfitabilityBadge shows green "Rentable (XX%)" for margin >= 60%, red "No Rentable (XX%)" for margin < 60%
- Unprofitable recipes are visually highlighted in the table
- "Agregar Receta" button opens TRRecipeForm in a dialog
- TRRecipeForm has: name, sale_price, is_active toggle, dynamic ingredient rows (resource selector, quantity, unit)
- "Agregar Ingrediente" adds a new ingredient row; remove button deletes a row
- Real-time cost and margin calculation displayed as ingredients are added
- Form validates: name required, sale_price > 0, at least one ingredient, quantity > 0
- Creating a recipe adds it to the table and refreshes the list
- Edit button opens TRRecipeForm pre-populated with recipe data
- Updating a recipe reflects changes in table
- Delete button shows Spanish confirmation dialog; confirming removes recipe
- "Producir" button opens quantity dialog; submitting triggers `/recipes/{id}/produce` API
- Production success refreshes the recipe list; failure shows error message
- Clicking a recipe row opens detail drawer with recipe info and ingredient breakdown
- Search by name filters the table client-side
- All UI labels are in Spanish (Colombian)
- Console shows INFO log messages for all operations
- TypeScript compiles with zero errors
- Production build succeeds with zero errors
- Backend tests pass with zero regressions

## Technical Verification

- Check browser console for:
  - INFO log messages for recipe operations
  - `INFO [RecipeService]: Fetching recipes for restaurant...`
  - `INFO [useRecipes]: Fetched X recipes`
  - `INFO [TRRecipeForm]: Submitting recipe form`
  - `INFO [RestaurantOSRecipesPage]: Creating recipe`
  - No JavaScript errors
  - No React warnings
- Check network requests:
  - GET `/api/recipes?restaurant_id=...` on page load
  - POST `/api/recipes` on create
  - PUT `/api/recipes/{id}` on update
  - DELETE `/api/recipes/{id}` on delete
  - POST `/api/recipes/{id}/produce` on production
  - Authorization header present in all requests

## Notes

- The backend Recipe CRUD API (`/api/recipes`) and production API (`/api/recipes/{id}/produce`) are fully implemented
- Profitability threshold is 60% margin, computed server-side; frontend uses `is_profitable` field
- Currency formatting uses `Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' })`
- Cost/margin in the form is an estimate based on `resource.last_unit_cost`; authoritative cost is server-side
- The `useResources` hook provides the resources list for ingredient selection in the form
- Search is client-side (filters the loaded recipes array by name)
- Route `/poc/restaurant-os/recipes` is registered in App.tsx
