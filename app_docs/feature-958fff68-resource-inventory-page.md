# Resource & Inventory Management Page

**ADW ID:** 958fff68
**Date:** 2026-03-03
**Specification:** specs/issue-90-adw-958fff68-sdlc_planner-resource-inventory-page.md

## Overview

A full-featured frontend page for managing resources (products, assets, services) and recording inventory movements within the RestaurantOS POC. The page displays current stock levels with low-stock indicators, supports CRUD operations on resources, allows registering inventory movements (entries/exits), and provides a detail drawer per resource showing movement history. All UI text is in Spanish (Colombian).

## What Was Built

- **TypeScript types** for Resource, InventoryMovement, and related DTOs with Spanish label constants
- **Resource service** (`resourceService`) for CRUD operations against `/api/resources`
- **Inventory movement service** (`inventoryMovementService`) for creating and querying movements against `/api/inventory-movements`
- **`useResources` hook** for resource state management with type filtering
- **`useInventoryMovements` hook** for movement state management
- **`TRResourceForm`** component for creating/editing resources with react-hook-form validation
- **`TRInventoryMovementForm`** component for registering stock entries/exits with stock-exceed warning
- **`RestaurantOSResourcesPage`** — full page replacing the placeholder, with data table, filters, dialogs, detail drawer, and stock status indicators
- **E2E test specification** for comprehensive feature validation

## Technical Implementation

### Files Modified

- `apps/Client/src/types/resource.ts` *(new)*: TypeScript interfaces (`Resource`, `ResourceCreate`, `ResourceUpdate`, `InventoryMovement`, `InventoryMovementCreate`, `MovementFilters`), union types (`ResourceType`, `MovementType`, `MovementReason`), and Spanish label constants (`RESOURCE_TYPE_LABELS`, `MOVEMENT_TYPE_LABELS`, `MOVEMENT_REASON_LABELS`)
- `apps/Client/src/services/resourceService.ts` *(new)*: API service with `getAll`, `getById`, `getLowStock`, `create`, `update`, `delete` methods using `apiClient`
- `apps/Client/src/services/inventoryMovementService.ts` *(new)*: API service with `create`, `getByResource`, `getAll` methods using `apiClient`
- `apps/Client/src/hooks/useResources.ts` *(new)*: State management hook with `resources`, `isLoading`, `error`, `filters`, `fetchResources`, `createResource`, `updateResource`, `deleteResource`, `setFilters`
- `apps/Client/src/hooks/useInventoryMovements.ts` *(new)*: State management hook with `movements`, `isLoading`, `error`, `fetchMovementsByResource`, `createMovement`, `clearMovements`
- `apps/Client/src/components/forms/TRResourceForm.tsx` *(new)*: react-hook-form form with fields for name, type (Producto/Activo/Servicio), unit, current_stock, minimum_stock, last_unit_cost; supports create and edit modes
- `apps/Client/src/components/forms/TRInventoryMovementForm.tsx` *(new)*: react-hook-form form with resource selector, movement type (Entrada/Salida), quantity, reason, optional person and notes; shows stock-exceed warning for exit movements
- `apps/Client/src/pages/restaurantos/RestaurantOSResourcesPage.tsx` *(replaced)*: Full page implementation replacing the "Próximamente" placeholder
- `.claude/commands/e2e/test_resource_inventory.md` *(new)*: E2E test specification covering CRUD, filtering, movements, detail drawer, and stock indicators

### Key Changes

- **Data table** displays resources with columns: Nombre, Tipo, Unidad, Stock Actual, Stock Mínimo, Último Costo, Estado (low-stock chip), Acciones
- **Low-stock indicator**: Red "Stock Bajo" chip when `is_low_stock` is true (computed server-side as `current_stock < minimum_stock`), green "OK" chip otherwise
- **Type filtering** (server-side via `resourceService.getAll`) and **name search** (client-side via `useMemo`)
- **Detail drawer** (right-side `Drawer`) shows resource info and movement history table with columns: Fecha, Tipo, Cantidad, Razón, Persona, Notas
- **Movement creation** refreshes both the resource list (stock changed) and the detail drawer movements if open for the same resource
- **Currency formatting** uses `Intl.NumberFormat` with `es-CO` locale and `COP` currency
- **No-restaurant state** renders `TRNoRestaurantPrompt` component
- **Person resolution** in movement history uses a `personsMap` built from `usePersons` hook data

## How to Use

1. Navigate to **RestaurantOS > Recursos / Inventario** in the sidebar (route: `/poc/restaurant-os/resources`)
2. Select a restaurant from the restaurant selector if not already selected
3. Click **"Agregar Recurso"** to open the resource creation form — fill in name, type, unit, stock values, and cost
4. Use the **type filter dropdown** (Todos/Producto/Activo/Servicio) and **search field** to find resources
5. Click the **edit icon** (pencil) on a resource row to modify its details
6. Click the **delete icon** (trash) on a resource row to remove it (with confirmation dialog)
7. Click **"Registrar Movimiento"** to record a stock entry or exit — select resource, type, quantity, reason, and optionally a person and notes
8. Click a **resource row** or the **view icon** (eye) to open the detail drawer showing resource info and movement history

## Configuration

No additional configuration required. The feature uses existing:
- `apiClient` with JWT interceptor for authenticated API calls
- `RestaurantContext` for multi-tenant restaurant scoping
- Backend `/api/resources` and `/api/inventory-movements` endpoints (already deployed)

## Testing

- **E2E test**: Run the E2E test spec at `.claude/commands/e2e/test_resource_inventory.md` using the E2E test runner
- **Type check**: `cd apps/Client && npx tsc --noEmit`
- **Build**: `cd apps/Client && npm run build`
- **Backend tests**: `cd apps/Server && python -m pytest tests/ -x` (no regressions)

## Notes

- The backend APIs for resources and inventory movements are fully implemented — this is a frontend-only feature
- The `is_low_stock` field is computed server-side (`current_stock < minimum_stock`); the frontend only reads it
- Movement creation auto-updates `current_stock` on the backend; the frontend refreshes data after creating a movement
- All UI labels are in Spanish (Colombian) as per the RestaurantOS POC convention
- The route `/poc/restaurant-os/resources` and sidebar entry were already registered prior to this implementation
