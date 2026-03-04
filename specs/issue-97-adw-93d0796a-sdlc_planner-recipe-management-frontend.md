# Feature: Recipe Management Frontend

## Metadata
issue_number: `97`
adw_id: `93d0796a`
issue_json: ``

## Feature Description
Build a complete frontend page for managing restaurant recipes. The page enables restaurant managers to view all dishes with their current cost, margin, and profitability status; add/edit recipes with ingredient selection from existing resources; see visual indicators for unprofitable dishes (margin < 60%); and trigger production actions that deduct ingredients from inventory. This connects the existing backend Recipe CRUD API (ROS-016) and Recipe Inventory Deduction API (ROS-016/produce) to a user-facing UI within the RestaurantOS section.

## User Story
As a restaurant manager
I want to manage my recipes with cost tracking and profitability analysis
So that I can identify unprofitable dishes, adjust pricing, and trigger ingredient deduction when producing dishes

## Problem Statement
The backend Recipe CRUD and production APIs exist but have no frontend UI. Restaurant managers cannot view, create, edit, or produce recipes without direct API calls. There is no visibility into dish profitability or cost breakdown.

## Solution Statement
Create a Recipe Management frontend page following existing RestaurantOS patterns (services, hooks, forms, page structure). The page will include a data table with profitability badges, a form with dynamic ingredient rows, a production dialog, and a detail drawer showing ingredient breakdown. All UI in Spanish (Colombian).

## Relevant Files
Use these files to implement the feature:

**Read first — understand patterns:**
- `apps/Client/src/services/resourceService.ts` — Service pattern (apiClient, logging, error handling)
- `apps/Client/src/hooks/useResources.ts` — Hook pattern (useState, useCallback, useEffect, fetchOnMount)
- `apps/Client/src/types/resource.ts` — Type/interface pattern with label maps
- `apps/Client/src/components/forms/TRResourceForm.tsx` — Form pattern (react-hook-form, MUI, validation)
- `apps/Client/src/components/ui/TRExpirationBadge.tsx` — Badge/Chip component pattern
- `apps/Client/src/pages/restaurantos/RestaurantOSResourcesPage.tsx` — Full page pattern (dialogs, CRUD, drawer, filters, table)
- `apps/Client/src/pages/restaurantos/TRNoRestaurantPrompt.tsx` — No-restaurant state component

**Modify — add route and navigation:**
- `apps/Client/src/App.tsx` — Route registration (add `/poc/restaurant-os/recipes`)
- `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx` — Sidebar navigation (add "Recetas" item)

**Reference — backend API structure:**
- `app_docs/feature-3ad42112-recipe-data-model-crud.md` — Recipe CRUD API docs
- `app_docs/feature-4801f61f-recipe-inventory-deduction.md` — Recipe production/deduction API docs
- `apps/Server/src/adapter/rest/recipe_routes.py` — Backend recipe endpoints
- `apps/Server/src/interface/recipe_dto.py` — Backend DTOs (RecipeCreateDTO, RecipeResponseDTO, RecipeProduceRequestDTO, RecipeProduceResponseDTO)

**Reference — E2E test patterns:**
- `.claude/commands/test_e2e.md` — E2E test runner instructions
- `.claude/commands/e2e/test_resource_inventory.md` — E2E test example for similar RestaurantOS page

### New Files
- `apps/Client/src/types/recipe.ts` — Recipe and RecipeItem TypeScript interfaces
- `apps/Client/src/services/recipeService.ts` — Recipe API service
- `apps/Client/src/hooks/useRecipes.ts` — Recipe state management hook
- `apps/Client/src/components/ui/TRProfitabilityBadge.tsx` — Profitability badge component
- `apps/Client/src/components/forms/TRRecipeForm.tsx` — Recipe form with dynamic ingredient rows
- `apps/Client/src/pages/restaurantos/RestaurantOSRecipesPage.tsx` — Recipes page
- `.claude/commands/e2e/test_recipe_management.md` — E2E test specification

## Implementation Plan
### Phase 1: Foundation
Create the TypeScript types, API service, and state management hook that form the data layer for the feature. These follow the exact same patterns as `resource.ts`, `resourceService.ts`, and `useResources.ts`.

### Phase 2: Core Implementation
Build the UI components: TRProfitabilityBadge (simple chip), TRRecipeForm (complex form with dynamic ingredient rows and real-time cost/margin calculation), and RestaurantOSRecipesPage (full CRUD page with data table, dialogs, production action, and detail drawer).

### Phase 3: Integration
Register the route in App.tsx, add "Recetas" to the sidebar navigation in TRCollapsibleSidebar.tsx, create the E2E test specification, and validate everything compiles and builds cleanly.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create Recipe Types
- Create `apps/Client/src/types/recipe.ts`
- Define interfaces matching the backend DTOs:
  - `RecipeItem`: id (optional), resource_id, resource_name (optional), quantity, unit, item_cost (optional)
  - `Recipe`: id, restaurant_id, name, sale_price, current_cost, margin_percent, is_profitable, is_active, items (RecipeItem[]), created_at, updated_at
  - `RecipeCreate`: restaurant_id, name, sale_price, is_active (optional), items (array of { resource_id, quantity, unit })
  - `RecipeUpdate`: name (optional), sale_price (optional), is_active (optional), items (optional array)
- Follow pattern from `apps/Client/src/types/resource.ts`

### Step 2: Create Recipe Service
- Create `apps/Client/src/services/recipeService.ts`
- Implement methods following `resourceService.ts` pattern:
  - `getAll(restaurantId: string): Promise<Recipe[]>` — GET `/recipes?restaurant_id={id}`
  - `getById(recipeId: string): Promise<Recipe>` — GET `/recipes/{id}`
  - `create(data: RecipeCreate): Promise<Recipe>` — POST `/recipes`
  - `update(id: string, data: RecipeUpdate): Promise<Recipe>` — PUT `/recipes/{id}`
  - `delete(id: string): Promise<void>` — DELETE `/recipes/{id}`
  - `produce(recipeId: string, quantity: number): Promise<RecipeProduceResponse>` — POST `/recipes/{id}/produce`
  - `recalculate(recipeId: string): Promise<Recipe>` — POST `/recipes/{id}/recalculate`
- Add `RecipeProduceResponse` interface: recipe_id, recipe_name, quantity, movements_created
- Include INFO/ERROR logging with `[RecipeService]` prefix

### Step 3: Create useRecipes Hook
- Create `apps/Client/src/hooks/useRecipes.ts`
- Follow `useResources.ts` pattern:
  - `useState` for: recipes, isLoading, error
  - `useCallback` for: fetchRecipes, createRecipe, updateRecipe, deleteRecipe, produceRecipe
  - `useEffect` triggers fetch when restaurantId changes
  - `produceRecipe(recipeId: string, quantity: number)` calls service, refreshes list after
- Return `{ recipes, isLoading, error, fetchRecipes, createRecipe, updateRecipe, deleteRecipe, produceRecipe }`
- Spanish error messages (e.g., "Error al cargar recetas. Intente de nuevo.")

### Step 4: Create TRProfitabilityBadge Component
- Create `apps/Client/src/components/ui/TRProfitabilityBadge.tsx`
- Follow `TRExpirationBadge.tsx` pattern exactly:
  - Props: `marginPercent: number`, `isProfitable: boolean`
  - Green Chip: "Rentable (XX%)" when margin >= 60%
  - Red Chip: "No Rentable (XX%)" when margin < 60%
  - Use MUI `Chip` with `color="success"` or `color="error"` and `size="small"`
- Include INFO logging

### Step 5: Create E2E Test Specification
- Create `.claude/commands/e2e/test_recipe_management.md`
- Follow the structure of `.claude/commands/e2e/test_resource_inventory.md`
- User Story: "As a restaurant manager, I want to manage recipes and track profitability so that I can optimize my menu"
- Test Steps should cover:
  1. Navigate to `/poc/restaurant-os/recipes` and verify page loads with heading "Recetas", restaurant name, and "Agregar Receta" button
  2. Verify empty state message "No se encontraron recetas"
  3. Click "Agregar Receta" — verify dialog opens with TRRecipeForm fields: Nombre, Precio de Venta, Activo toggle, ingredient rows section with "Agregar Ingrediente" button
  4. Create a recipe: fill name "Pasta Carbonara", sale_price 35000, add 2 ingredients from resource selector with quantities, submit
  5. Verify recipe appears in table with columns: Nombre, Precio Venta, Costo Actual, Margen %, Rentabilidad (TRProfitabilityBadge), Estado, Acciones
  6. Verify profitability badge color (green "Rentable" or red "No Rentable" based on margin)
  7. Click recipe row — verify detail drawer opens showing ingredient breakdown table
  8. Edit recipe — click edit button, verify form pre-populated, change sale_price, submit, verify update
  9. Test "Producir" button — click, verify quantity dialog opens with "¿Cuántas porciones producir?", enter quantity, submit
  10. Verify production success or error handling for insufficient stock
  11. Delete recipe — confirm dialog, verify removed from table
  12. Search by name filter works
- Success Criteria: page loads, CRUD works, profitability badges display correctly, production triggers deduction, all Spanish labels correct, no JS errors

### Step 6: Create TRRecipeForm Component
- Create `apps/Client/src/components/forms/TRRecipeForm.tsx`
- Follow `TRResourceForm.tsx` patterns but with dynamic ingredient rows:
- Props interface:
  - `onSubmit: (data: RecipeCreate | RecipeUpdate) => void`
  - `initialData?: Recipe` (for edit mode)
  - `restaurantId: string`
  - `resources: Resource[]` (available resources for ingredient selection)
  - `onCancel: () => void`
  - `isSubmitting?: boolean`
- Fields:
  - `name` — TextField, required, validation: "El nombre es obligatorio"
  - `sale_price` — TextField type="number", required, min > 0, validation: "El precio de venta es obligatorio"
  - `is_active` — Switch/toggle, default true
- Dynamic ingredient rows section:
  - Use local state array for ingredient items `[{ resource_id, quantity, unit }]`
  - Each row: resource selector (Select from `resources` prop), quantity (TextField number > 0), unit (auto-filled from selected resource, read-only)
  - "Agregar Ingrediente" button adds a new empty row
  - Remove button (IconButton with Delete icon) per row
  - Validation: at least one ingredient required, quantity > 0 for each
- Real-time cost/margin display (read-only):
  - Calculate estimated cost: sum of (item.quantity × resource.last_unit_cost) for each ingredient
  - Calculate margin: (sale_price - cost) / sale_price × 100 (if sale_price > 0)
  - Display: "Costo Estimado: $X" and "Margen Estimado: X%"
- Submit button: "Agregar Receta" (create) or "Actualizar Receta" (edit)
- Cancel button: "Cancelar"

### Step 7: Create RestaurantOSRecipesPage
- Create `apps/Client/src/pages/restaurantos/RestaurantOSRecipesPage.tsx`
- Follow `RestaurantOSResourcesPage.tsx` pattern exactly:
- Hooks: `useRestaurant()`, `useRecipes(currentRestaurant?.id)`, `useResources(currentRestaurant?.id)` (for ingredient selection)
- State: isAddDialogOpen, isEditDialogOpen, isDeleteDialogOpen, isProduceDialogOpen, selectedRecipe, drawerRecipe, isSubmitting, searchQuery, produceQuantity
- Loading state: CircularProgress with "Cargando..."
- No restaurants: TRNoRestaurantPrompt
- Error display: Alert severity="error"
- Header: "Recetas" h4, currentRestaurant.name h6, "Agregar Receta" button (contained, Add icon)
- Search: TextField "Buscar por nombre" with client-side filtering
- Data table columns:
  - Nombre
  - Precio Venta — formatted with COP currency (use formatCurrency)
  - Costo Actual — formatted with COP currency
  - Margen % — show percentage
  - Rentabilidad — TRProfitabilityBadge component
  - Estado — Chip: green "Activa" or grey "Inactiva" based on is_active
  - Acciones — Edit, Delete, "Producir" buttons
- Row click: open detail drawer showing recipe info + ingredient breakdown table
- Unprofitable recipes: highlight row with `sx={{ backgroundColor: 'error.50' }}` or subtle red tint
- Dialogs:
  - Add Recipe: TRRecipeForm in Dialog
  - Edit Recipe: TRRecipeForm with initialData in Dialog
  - Delete Confirmation: same pattern as resources page, Spanish text "¿Está seguro que desea eliminar esta receta?"
  - Produce Dialog: small Dialog with title "Producir", text "¿Cuántas porciones producir?", TextField for quantity (number, min 1, default 1), "Cancelar" and "Producir" buttons
- CRUD handlers: handleCreate, handleUpdate, handleDelete, handleProduce (calls produceRecipe from hook)
- Detail Drawer:
  - Recipe name, sale_price, current_cost, margin_percent
  - TRProfitabilityBadge
  - "Ingredientes" heading with table: Ingrediente (resource_name), Cantidad, Unidad, Costo Unitario
- All console.log INFO/ERROR with `[RestaurantOSRecipesPage]` prefix

### Step 8: Register Route in App.tsx
- Add import for `RestaurantOSRecipesPage` from `@/pages/restaurantos/RestaurantOSRecipesPage`
- Add route block after the resources route:
  ```tsx
  <Route
    path="/poc/restaurant-os/recipes"
    element={
      <ProtectedRoute>
        <TRMainLayout>
          <RestaurantOSRecipesPage />
        </TRMainLayout>
      </ProtectedRoute>
    }
  />
  ```

### Step 9: Add Sidebar Navigation
- Edit `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`
- Import `MenuBookIcon` from `@mui/icons-material/MenuBook`
- Add to the RestaurantOS subsection items array, after "Recursos / Inventario":
  ```typescript
  { label: 'Recetas', path: '/poc/restaurant-os/recipes', icon: <MenuBookIcon /> },
  ```

### Step 10: Run Validation Commands
- Run `cd apps/Server && python -m pytest tests/` to verify backend tests pass with zero regressions
- Run `cd apps/Client && npx tsc --noEmit` to verify TypeScript compiles with zero errors
- Run `cd apps/Client && npm run build` to verify production build succeeds with zero errors
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_recipe_management.md` E2E test to validate this functionality works

## Testing Strategy
### Unit Tests
- TypeScript type compilation validates Recipe/RecipeItem interfaces match backend DTOs
- TRProfitabilityBadge renders correct color/label for profitable (margin >= 60%) and unprofitable (margin < 60%) cases
- TRRecipeForm validates required fields (name, sale_price > 0, at least 1 ingredient)
- TRRecipeForm calculates estimated cost and margin correctly in real-time
- recipeService methods call correct API endpoints with proper parameters
- useRecipes hook fetches on mount, refreshes after CRUD operations

### Edge Cases
- Recipe with zero ingredients — form validation should prevent submission
- Recipe with sale_price = 0 — form validation should prevent submission
- Margin calculation when cost = 0 — should show 100% margin
- Margin calculation when sale_price = cost — should show 0% margin
- Production with insufficient stock — should display backend error message in Spanish
- Production with quantity > 1 — should multiply ingredient deduction
- Recipe with no resource_name (ingredient resource deleted) — handle gracefully
- No restaurant selected — show TRNoRestaurantPrompt
- Empty recipes list — show "No se encontraron recetas" message
- Network errors on any API call — display error Alert

## Acceptance Criteria
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

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/` — Run Server tests to validate zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate zero type errors
- `cd apps/Client && npm run build` — Run Client build to validate zero build errors
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_recipe_management.md` E2E test to validate this functionality works

## Notes
- The backend Recipe CRUD API (`/api/recipes`) and production API (`/api/recipes/{id}/produce`) are fully implemented (see `app_docs/feature-3ad42112-recipe-data-model-crud.md` and `app_docs/feature-4801f61f-recipe-inventory-deduction.md`)
- Profitability threshold is hardcoded at 60% margin on the backend; frontend should use the `is_profitable` field from the API response
- The `useResources` hook is needed in the page to provide the resources list for ingredient selection in the form
- Currency formatting should use `Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' })` following existing pattern
- Cost/margin in the form is an estimate based on `resource.last_unit_cost`; the authoritative cost is computed server-side
- The `recalculate` service method is available but not exposed as a UI action in this initial implementation (can be added later)
- No new npm packages required — all dependencies (MUI, react-hook-form, axios) already exist
