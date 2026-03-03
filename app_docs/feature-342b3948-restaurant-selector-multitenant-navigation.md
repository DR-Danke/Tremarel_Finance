# Restaurant Selector & Multi-Tenant Navigation

**ADW ID:** 342b3948
**Date:** 2026-03-03
**Specification:** specs/issue-85-adw-342b3948-sdlc_planner-restaurant-selector-multitenant-navigation.md

## Overview

Adds restaurant selection and multi-tenant navigation to the RestaurantOS module. Users who belong to multiple restaurants can switch between them via a dropdown selector in the sidebar. The sidebar POCs > RestaurantOS subsection is populated with navigation links to five placeholder pages, and a RestaurantContext (mirroring the existing EntityContext) provides restaurant state management with localStorage persistence.

## What Was Built

- **RestaurantContext** — Global context provider with restaurant CRUD operations, localStorage persistence, and authentication-driven loading
- **TRRestaurantSelector** — Sidebar dropdown component for switching between restaurants (visible only on `/poc/restaurant-os/*` routes)
- **TRNoRestaurantPrompt** — Empty-state component with a creation dialog for users with no restaurants
- **Five placeholder pages** — Dashboard, Personas, Documentos, Eventos/Tareas, Recursos/Inventario (all show "Próximamente")
- **Restaurant service** — API service with full CRUD operations against `/api/restaurants`
- **Restaurant types** — TypeScript interfaces matching the backend RestaurantResponseDTO
- **Sidebar navigation items** — Five nav items under POCs > RestaurantOS subsection
- **E2E test specification** — Playwright test for restaurant selector and navigation validation

## Technical Implementation

### Files Modified

- `apps/Client/src/main.tsx`: Added `RestaurantProvider` to the provider tree (inside EntityProvider, wrapping ThemeProvider)
- `apps/Client/src/App.tsx`: Replaced catch-all `/poc/restaurant-os/*` route with five individual routes plus a redirect from `/poc/restaurant-os` to `/poc/restaurant-os/dashboard`
- `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`: Added RestaurantOS nav items (Dashboard, Personas, Documentos, Eventos/Tareas, Recursos/Inventario) and conditionally renders `TRRestaurantSelector` on RestaurantOS routes
- `apps/Client/src/types/index.ts`: Added re-exports for Restaurant, CreateRestaurantData, UpdateRestaurantData

### New Files

- `apps/Client/src/types/restaurant.ts`: Restaurant, CreateRestaurantData, UpdateRestaurantData interfaces
- `apps/Client/src/services/restaurantService.ts`: API service (getRestaurants, getRestaurant, createRestaurant, updateRestaurant, deleteRestaurant)
- `apps/Client/src/contexts/restaurantContextDef.ts`: RestaurantContextType interface and context creation
- `apps/Client/src/contexts/RestaurantContext.tsx`: RestaurantProvider with auth-driven fetch, localStorage persistence, memoized CRUD callbacks
- `apps/Client/src/hooks/useRestaurant.ts`: Custom hook with provider boundary check
- `apps/Client/src/components/layout/TRRestaurantSelector.tsx`: Dropdown selector (expanded/collapsed modes)
- `apps/Client/src/pages/restaurantos/TRNoRestaurantPrompt.tsx`: Empty-state prompt with react-hook-form creation dialog
- `apps/Client/src/pages/restaurantos/RestaurantOSDashboardPage.tsx`: Dashboard placeholder
- `apps/Client/src/pages/restaurantos/RestaurantOSPersonsPage.tsx`: Personas placeholder
- `apps/Client/src/pages/restaurantos/RestaurantOSDocumentsPage.tsx`: Documentos placeholder
- `apps/Client/src/pages/restaurantos/RestaurantOSEventsPage.tsx`: Eventos/Tareas placeholder
- `apps/Client/src/pages/restaurantos/RestaurantOSResourcesPage.tsx`: Recursos/Inventario placeholder
- `.claude/commands/e2e/test_restaurant_selector_navigation.md`: E2E test specification

### Key Changes

- **RestaurantContext mirrors EntityContext**: Same provider pattern — fetches on auth, persists selection in localStorage (`currentRestaurantId`), falls back to first restaurant if stored ID is invalid
- **Conditional sidebar selector**: `TRRestaurantSelector` only renders when `location.pathname.startsWith('/poc/restaurant-os')`, avoiding sidebar clutter for Finance-only users
- **Provider placement at root level**: RestaurantProvider is in `main.tsx` (not route-scoped) because the sidebar needs access to restaurant state regardless of route nesting
- **Placeholder pages with empty-state handling**: All five pages check `restaurants.length === 0` and render `TRNoRestaurantPrompt` instead of page content
- **Spanish UI text**: Labels use Colombian Spanish — "Restaurante", "Personas", "Documentos", "Eventos / Tareas", "Recursos / Inventario", "Próximamente", "No tienes restaurantes"

## How to Use

1. Log in to the application
2. Expand the **POCs** section in the sidebar
3. Expand the **RestaurantOS** subsection — five navigation items appear
4. Click any RestaurantOS nav item (e.g., Dashboard) to navigate to `/poc/restaurant-os/dashboard`
5. The **restaurant selector dropdown** appears in the sidebar above the navigation links
6. If you have no restaurants, a prompt appears with a **"Crear Restaurante"** button to create your first one
7. If you have multiple restaurants, use the dropdown labeled **"Restaurante"** to switch between them
8. The selected restaurant persists across page refreshes via localStorage

## Configuration

No additional environment variables required. The feature uses the existing backend REST API at `/api/restaurants` which is already deployed.

## Testing

Run the E2E test specification:
```bash
# Read and execute the E2E test
.claude/commands/e2e/test_restaurant_selector_navigation.md
```

Validation commands:
```bash
cd apps/Client && npx tsc --noEmit       # TypeScript check
cd apps/Client && npm run build           # Production build
cd apps/Server && uv run pytest           # Backend tests (no regressions)
```

## Notes

- The backend restaurant API (GET/POST/PUT/DELETE `/api/restaurants`) was already implemented in a prior wave
- Wave 4 will replace placeholder pages with full CRUD management pages that use `useRestaurant()` to scope data
- The `Restaurant` type uses `string` for `owner_id`, `created_at`, and `updated_at` since JSON serialization converts UUID/datetime to strings
- When collapsed, the sidebar shows the first letter of the current restaurant name instead of the full dropdown
