# Feature: Resource & Inventory Management Page

## Metadata
issue_number: `90`
adw_id: `958fff68`
issue_json: ``

## Feature Description
Build a full-featured frontend page for managing resources (products, assets, services) and recording inventory movements within the RestaurantOS POC. The page displays current stock levels with low-stock indicators, supports CRUD operations on resources, allows registering inventory movements (entries/exits), and provides a detail drawer per resource showing movement history. All UI text is in Spanish (Colombian).

## User Story
As a restaurant manager
I want to manage my resources (products, assets, services) and track inventory movements
So that I can monitor stock levels, identify low-stock items, and maintain a complete movement history for each resource

## Problem Statement
Restaurant managers need visibility into their inventory — what resources they have, current stock levels, which items are running low, and a history of all movements (purchases, usage, waste, etc.). Without this page, the backend APIs for resources and inventory movements have no frontend interface.

## Solution Statement
Create a ResourcesPage at `/poc/restaurant-os/resources` that provides:
1. A data table listing all resources with stock status indicators
2. Type filtering (Producto/Activo/Servicio)
3. Dialog-based resource CRUD via TRResourceForm
4. Inventory movement registration via TRInventoryMovementForm
5. A detail drawer per resource showing resource info and movement history
6. Low-stock highlighting with red "Stock Bajo" chip

This follows the established RestaurantOS page patterns (PersonsPage, EventsPage) with services, hooks, types, and form components.

## Relevant Files
Use these files to implement the feature:

**Existing files to modify:**
- `apps/Client/src/pages/restaurantos/RestaurantOSResourcesPage.tsx` — Replace placeholder with full implementation
- `apps/Client/src/App.tsx` — Route already registered, no changes needed

**Reference files (read for patterns):**
- `apps/Client/src/services/personService.ts` — Service pattern (apiClient, logging, error handling)
- `apps/Client/src/types/person.ts` — Type definition pattern (interfaces, enums, Create/Update DTOs)
- `apps/Client/src/hooks/usePersons.ts` — Hook pattern (useState, useCallback, useEffect, filters)
- `apps/Client/src/components/forms/TRPersonForm.tsx` — Form pattern (react-hook-form, Controller, MUI, validation)
- `apps/Client/src/components/forms/TREventForm.tsx` — Form pattern with conditional fields
- `apps/Client/src/pages/restaurantos/RestaurantOSPersonsPage.tsx` — Page pattern (dialogs, table, search, filter)
- `apps/Client/src/pages/restaurantos/RestaurantOSEventsPage.tsx` — Page pattern with detail drawer
- `apps/Client/src/contexts/RestaurantContext.tsx` — Restaurant context for multi-tenant scoping
- `apps/Client/src/api/clients/` — API client with JWT interceptor

**Backend API reference (read-only, already implemented):**
- `apps/Server/src/adapter/rest/resource_routes.py` — Resource API endpoints
- `apps/Server/src/adapter/rest/inventory_movement_routes.py` — Movement API endpoints
- `apps/Server/src/interface/resource_dto.py` — Resource DTOs
- `apps/Server/src/interface/inventory_movement_dto.py` — Movement DTOs

**Documentation reference:**
- `app_docs/feature-8d28116a-resource-entity-crud-backend.md` — Backend resource implementation docs
- `app_docs/feature-342b3948-restaurant-selector-multitenant-navigation.md` — Restaurant context usage docs
- `app_docs/feature-75704e1f-section-based-sidebar-navigation.md` — Sidebar navigation docs

**E2E test reference:**
- `.claude/commands/test_e2e.md` — E2E test runner instructions
- `.claude/commands/e2e/test_person_management.md` — E2E test example (CRUD, search, filter pattern)
- `.claude/commands/e2e/test_event_task_management.md` — E2E test example (detail drawer, status badges)

### New Files
- `apps/Client/src/types/resource.ts` — Resource and InventoryMovement type definitions
- `apps/Client/src/services/resourceService.ts` — Resource API service
- `apps/Client/src/services/inventoryMovementService.ts` — Inventory movement API service
- `apps/Client/src/hooks/useResources.ts` — Resources state management hook
- `apps/Client/src/hooks/useInventoryMovements.ts` — Inventory movements state management hook
- `apps/Client/src/components/forms/TRResourceForm.tsx` — Resource create/edit form component
- `apps/Client/src/components/forms/TRInventoryMovementForm.tsx` — Inventory movement registration form
- `.claude/commands/e2e/test_resource_inventory.md` — E2E test specification

## Implementation Plan
### Phase 1: Foundation
Create the TypeScript types and API service layers that all other components depend on. This includes the Resource and InventoryMovement interfaces, Create/Update DTOs, and the service modules that wrap apiClient calls.

### Phase 2: Core Implementation
Build the custom hooks (useResources, useInventoryMovements) for state management, then the form components (TRResourceForm, TRInventoryMovementForm) using react-hook-form with MUI.

### Phase 3: Integration
Replace the ResourcesPage placeholder with the full page implementation that ties together hooks, forms, data table, filters, detail drawer, and stock status indicators. Create the E2E test specification. Validate with build and type checks.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create Resource & Movement Types
- Read `apps/Client/src/types/person.ts` for the type definition pattern
- Read `apps/Server/src/interface/resource_dto.py` and `apps/Server/src/interface/inventory_movement_dto.py` for backend DTO fields
- Create `apps/Client/src/types/resource.ts` with:
  - `ResourceType` union type: `'producto' | 'activo' | 'servicio'`
  - `Resource` interface: id, restaurant_id, type, name, unit, current_stock, minimum_stock, last_unit_cost, is_low_stock, created_at, updated_at
  - `ResourceCreate` interface: restaurant_id, type, name, unit, current_stock, minimum_stock, last_unit_cost
  - `ResourceUpdate` interface: all fields optional except id
  - `ResourceFilters` interface: type? filter
  - `MovementType` union type: `'entry' | 'exit'`
  - `MovementReason` union type: `'compra' | 'uso' | 'produccion' | 'merma' | 'receta' | 'ajuste'`
  - `InventoryMovement` interface: id, resource_id, type, quantity, reason, date, person_id?, restaurant_id, notes?, created_at
  - `InventoryMovementCreate` interface: resource_id, restaurant_id, type, quantity, reason, date?, person_id?, notes?
  - `MovementFilters` interface: date_from?, date_to?, reason?
  - Export label constants for Spanish display: `RESOURCE_TYPE_LABELS`, `MOVEMENT_TYPE_LABELS`, `MOVEMENT_REASON_LABELS`

### Step 2: Create Resource Service
- Read `apps/Client/src/services/personService.ts` for the service pattern
- Read `apps/Server/src/adapter/rest/resource_routes.py` for exact endpoint URLs and parameters
- Create `apps/Client/src/services/resourceService.ts` with:
  - `getAll(restaurantId: string, type?: ResourceType): Promise<Resource[]>` — GET `/resources?restaurant_id=...&type=...`
  - `getById(resourceId: string): Promise<Resource>` — GET `/resources/{resourceId}`
  - `getLowStock(restaurantId: string): Promise<Resource[]>` — GET `/resources/low-stock?restaurant_id=...`
  - `create(data: ResourceCreate): Promise<Resource>` — POST `/resources`
  - `update(resourceId: string, data: ResourceUpdate): Promise<Resource>` — PUT `/resources/{resourceId}`
  - `delete(resourceId: string): Promise<void>` — DELETE `/resources/{resourceId}`
- Follow logging pattern: `console.log('INFO [ResourceService]: ...')`

### Step 3: Create Inventory Movement Service
- Read `apps/Server/src/adapter/rest/inventory_movement_routes.py` for exact endpoint URLs and parameters
- Create `apps/Client/src/services/inventoryMovementService.ts` with:
  - `create(data: InventoryMovementCreate): Promise<InventoryMovement>` — POST `/inventory-movements`
  - `getByResource(resourceId: string, dateFrom?: string, dateTo?: string): Promise<InventoryMovement[]>` — GET `/inventory-movements?resource_id=...&date_from=...&date_to=...`
  - `getAll(restaurantId: string, filters?: MovementFilters): Promise<InventoryMovement[]>` — GET `/inventory-movements?restaurant_id=...`
- Follow logging pattern: `console.log('INFO [InventoryMovementService]: ...')`

### Step 4: Create useResources Hook
- Read `apps/Client/src/hooks/usePersons.ts` for the hook pattern
- Create `apps/Client/src/hooks/useResources.ts` with:
  - State: resources[], isLoading, error, filters (ResourceFilters)
  - Methods: fetchResources, createResource, updateResource, deleteResource, setFilters
  - useCallback for all operations, useEffect for initial fetch
  - Null check on restaurantId to skip fetch when no restaurant selected
  - Refresh list after create/update/delete
  - Comprehensive logging

### Step 5: Create useInventoryMovements Hook
- Create `apps/Client/src/hooks/useInventoryMovements.ts` with:
  - State: movements[], isLoading, error
  - Methods: fetchMovementsByResource(resourceId), createMovement, clearMovements
  - useCallback for all operations
  - After creating a movement, the parent should also refresh resources (stock changed) — expose a callback pattern or return a flag
  - Comprehensive logging

### Step 6: Create TRResourceForm Component
- Read `apps/Client/src/components/forms/TRPersonForm.tsx` for the form pattern
- Create `apps/Client/src/components/forms/TRResourceForm.tsx` with:
  - Props: onSubmit, initialData?, restaurantId, onCancel, isSubmitting?
  - Fields using react-hook-form:
    - `name` (TextField, required: "El nombre es obligatorio")
    - `type` (Controller + Select: Producto/Activo/Servicio, default "producto")
    - `unit` (TextField, required: "La unidad es obligatoria")
    - `current_stock` (TextField type="number", min 0: "El stock debe ser >= 0")
    - `minimum_stock` (TextField type="number", min 0: "El stock mínimo debe ser >= 0")
    - `last_unit_cost` (TextField type="number", min 0: "El costo debe ser >= 0")
  - Support create and edit modes via initialData
  - Spanish labels and validation messages
  - Submit button: "Agregar Recurso" (create) or "Actualizar Recurso" (edit)

### Step 7: Create TRInventoryMovementForm Component
- Create `apps/Client/src/components/forms/TRInventoryMovementForm.tsx` with:
  - Props: onSubmit, resources (Resource[]), persons (Person[])?, onCancel, isSubmitting?
  - Fields using react-hook-form:
    - `resource_id` (Controller + Select: list of resources by name)
    - `type` (Controller + Select: Entrada/Salida)
    - `quantity` (TextField type="number", required, min 1: "La cantidad debe ser mayor a 0")
    - `reason` (Controller + Select: Compra/Uso/Producción/Merma/Ajuste)
    - `person_id` (Controller + Select: optional person selector, label "Persona")
    - `notes` (TextField multiline, optional, label "Notas")
  - Warning Alert when type is "exit" and quantity would exceed selected resource's current_stock
  - Spanish labels and validation messages
  - Submit button: "Registrar Movimiento"

### Step 8: Implement ResourcesPage
- Read `apps/Client/src/pages/restaurantos/RestaurantOSPersonsPage.tsx` and `RestaurantOSEventsPage.tsx` for page patterns
- Replace placeholder in `apps/Client/src/pages/restaurantos/RestaurantOSResourcesPage.tsx` with full implementation:
  - Use `useRestaurant()` for restaurant context
  - Use `useResources(currentRestaurant?.id)` for resource data
  - Use `useInventoryMovements()` for movement operations
  - State for dialogs: isAddDialogOpen, isMovementDialogOpen, editingResource, selectedResource (for detail drawer)
  - State for delete confirmation: deleteTarget, isDeleteDialogOpen
  - **Header section**: Title "Recursos / Inventario", restaurant name subtitle
  - **Filter bar**: Type filter dropdown (Todos/Producto/Activo/Servicio), search by name TextField
  - **Action buttons**: "Agregar Recurso" and "Registrar Movimiento"
  - **Data table** with columns:
    - Nombre
    - Tipo (display Spanish label)
    - Unidad
    - Stock Actual
    - Stock Mínimo
    - Último Costo (formatted as currency)
    - Estado: Chip "Stock Bajo" (red/error) when is_low_stock is true, "OK" (green/success) otherwise
    - Acciones: Edit (pencil icon), Delete (trash icon), View movements (visibility icon)
  - **Clicking a row or view icon** opens a detail Drawer (right-side) showing:
    - Resource details (name, type, unit, stock, cost)
    - Movement history table: Fecha, Tipo (Entrada/Salida), Cantidad, Razón, Persona, Notas
    - Fetch movements via useInventoryMovements.fetchMovementsByResource when drawer opens
  - **Add Resource dialog**: TRResourceForm in Dialog
  - **Edit Resource dialog**: TRResourceForm with initialData in Dialog
  - **Register Movement dialog**: TRInventoryMovementForm in Dialog
  - **Delete confirmation dialog**: Spanish text "¿Está seguro que desea eliminar este recurso?"
  - Loading states, error alerts, empty state message "No se encontraron recursos"
  - No-restaurant state shows TRNoRestaurantPrompt
  - After creating a movement, refresh both movements (if drawer open) and resources (stock changed)
  - Client-side search filtering by resource name
  - Server-side type filtering via hook filters

### Step 9: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` for E2E runner instructions
- Read `.claude/commands/e2e/test_person_management.md` for test format and pattern
- Create `.claude/commands/e2e/test_resource_inventory.md` with test steps covering:
  - Page load with "Recursos / Inventario" heading
  - Empty state display
  - Create resource form validation (required fields, non-negative values)
  - Create a resource (type: Producto, with stock values)
  - Verify resource appears in table with correct columns
  - Create a second resource with stock below minimum to verify "Stock Bajo" chip
  - Filter by type (Producto vs Activo)
  - Search by name
  - Edit a resource and verify changes in table
  - Register inventory movement (Entrada) and verify stock update
  - Register inventory movement (Salida) and verify stock update
  - Open resource detail drawer and verify movement history
  - Delete a resource with confirmation
  - No-restaurant state verification
  - Success criteria and technical verification sections

### Step 10: Validate Implementation
- Run `cd apps/Client && npx tsc --noEmit` — TypeScript type check with zero errors
- Run `cd apps/Client && npm run build` — Production build with zero errors
- Run `cd apps/Server && python -m pytest tests/ -x` — Backend tests pass (no regressions)
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_resource_inventory.md` E2E test

## Testing Strategy
### Unit Tests
- No new unit tests are required for frontend-only feature (follows existing pattern where RestaurantOS POC pages don't have isolated unit tests)
- Backend tests already exist for resource and inventory movement APIs

### Edge Cases
- Resource with current_stock exactly equal to minimum_stock (should NOT show "Stock Bajo")
- Resource with current_stock = 0
- Exit movement that would bring stock below 0 (form should warn)
- Exit movement that would bring stock to exactly 0 (allowed)
- Resource with no movements yet (empty movement history in drawer)
- Long resource names in table columns
- Decimal stock values (e.g., 2.5 kg)
- Creating movement without optional person_id
- Type filter showing empty results
- Switching restaurants should reload resources

## Acceptance Criteria
- ResourcesPage loads at `/poc/restaurant-os/resources` with "Recursos / Inventario" heading
- Page shows current restaurant name from RestaurantContext
- No-restaurant state shows TRNoRestaurantPrompt component
- Data table displays resources with columns: Nombre, Tipo, Unidad, Stock Actual, Stock Mínimo, Último Costo, Estado, Acciones
- Low-stock resources display red "Stock Bajo" chip; normal stock shows green "OK" chip
- Type filter dropdown filters by Todos/Producto/Activo/Servicio
- Search by name filters the table client-side
- "Agregar Recurso" button opens dialog with TRResourceForm
- TRResourceForm validates: name and unit required, stock/cost values >= 0
- Creating a resource adds it to the table
- Edit button opens TRResourceForm pre-populated with resource data
- Updating a resource reflects changes in table
- Delete button shows Spanish confirmation dialog; confirming removes resource
- "Registrar Movimiento" button opens dialog with TRInventoryMovementForm
- TRInventoryMovementForm validates: quantity > 0, shows warning for stock-negative exits
- Creating a movement updates the resource's stock in the table
- Clicking a resource opens detail drawer with resource info and movement history
- Movement history table shows: Fecha, Tipo, Cantidad, Razón, Persona, Notas
- All UI labels are in Spanish (Colombian)
- Console shows INFO log messages for all operations
- TypeScript compiles with zero errors
- Production build succeeds with zero errors
- Backend tests pass with zero regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate zero type errors
- `cd apps/Client && npm run build` — Run Client production build to validate zero build errors
- `cd apps/Server && python -m pytest tests/ -x` — Run Server tests to validate zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_resource_inventory.md` E2E test to validate the feature works end-to-end

## Notes
- The backend APIs for resources (`/api/resources`) and inventory movements (`/api/inventory-movements`) are fully implemented and tested — this is a frontend-only feature
- The route `/poc/restaurant-os/resources` is already registered in App.tsx
- The sidebar navigation already includes "Recursos / Inventario" entry with InventoryIcon
- The RestaurantOSResourcesPage.tsx exists as a placeholder showing "Próximamente" — it needs to be replaced
- Movement creation auto-updates resource stock on the backend; frontend just needs to refresh data after creating a movement
- The `is_low_stock` field is computed server-side (current_stock < minimum_stock) so the frontend just reads it
- Person data may be needed in the movement form for the person_id selector — either pass persons from a usePersons hook or load them in the form
- No new npm packages are required; all dependencies (MUI, react-hook-form, axios) are already installed
