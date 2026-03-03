# Feature: Restaurant Selector & Multi-Tenant Navigation

## Metadata
issue_number: `85`
adw_id: `342b3948`
issue_json: `{"number":85,"title":"[RestaurantOS] Wave 3: Restaurant Selector & Multi-Tenant Navigation"}`

## Feature Description
Add restaurant selection to the RestaurantOS application shell. Users who belong to multiple restaurants can switch between them via a selector in the sidebar. All RestaurantOS data views will filter by the currently selected restaurant. The sidebar navigation is updated to include RestaurantOS-specific page links under the POCs > RestaurantOS subsection. This mirrors the existing EntityContext pattern used for Finance Tracker multi-entity support.

## User Story
As a restaurant owner or manager who operates multiple restaurants
I want to select which restaurant I am currently managing and navigate to restaurant-specific pages
So that I can view and manage data scoped to a specific restaurant without mixing up data across locations

## Problem Statement
The RestaurantOS module has backend APIs for CRUD operations on restaurants, but the frontend has no mechanism to select/switch between restaurants or navigate to RestaurantOS feature pages. The sidebar POCs > RestaurantOS subsection is currently empty with no navigation items. Without a RestaurantContext, Wave 4 entity management pages cannot scope data to the active restaurant.

## Solution Statement
Create a RestaurantContext (mirroring EntityContext), a restaurant service, a restaurant selector component in the sidebar, and populate the RestaurantOS sidebar subsection with navigation links to placeholder pages. The context will persist the selected restaurant in localStorage and load user's restaurants on authentication. Placeholder pages for Personas, Documentos, Eventos/Tareas, and Recursos/Inventario will be created with "Coming Soon" messages until Wave 4 implements them.

## Relevant Files
Use these files to implement the feature:

**Read first for patterns and conventions:**
- `apps/Client/src/contexts/entityContextDef.ts` — Pattern for context type definition (mirror for RestaurantContext)
- `apps/Client/src/contexts/EntityContext.tsx` — Pattern for context provider implementation (mirror for RestaurantContext)
- `apps/Client/src/services/entityService.ts` — Pattern for API service (mirror for restaurantService)
- `apps/Client/src/hooks/useEntity.ts` — Pattern for context hook (mirror for useRestaurant)
- `apps/Client/src/types/index.ts` — Where all TypeScript types live; add Restaurant types here
- `apps/Client/src/api/clients/index.ts` — API client with JWT interceptor (used by services)

**Files to modify:**
- `apps/Client/src/types/index.ts` — Add Restaurant, CreateRestaurantData, UpdateRestaurantData interfaces
- `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx` — Add RestaurantOS nav items and restaurant selector
- `apps/Client/src/App.tsx` — Add nested routes for RestaurantOS pages with RestaurantContext wrapping
- `apps/Client/src/main.tsx` — Add RestaurantProvider to the provider tree

**Conditional documentation to read:**
- `app_docs/feature-a692d2db-restaurant-multi-tenant-entity.md` — Restaurant table and RestaurantOS scoping
- `app_docs/feature-a201d4c8-main-layout-collapsible-sidebar.md` — Sidebar patterns and EntityContext
- `app_docs/feature-75704e1f-section-based-sidebar-navigation.md` — Section-based sidebar structure
- `app_docs/feature-d6d0f56d-entity-management-crud.md` — Multi-entity patterns (the template to mirror)

**E2E test reference files:**
- `.claude/commands/test_e2e.md` — How to create and run E2E tests
- `.claude/commands/e2e/test_section_based_sidebar_navigation.md` — Existing sidebar E2E test (reference for new test)
- `.claude/commands/e2e/test_entity_management.md` — Entity management E2E test (reference for context switching test)

**Backend API (already implemented — read for understanding response shapes):**
- `apps/Server/src/adapter/rest/restaurant_routes.py` — REST endpoints (GET/POST/PUT/DELETE /api/restaurants)
- `apps/Server/src/interface/restaurant_dto.py` — Response DTO shapes (RestaurantResponseDTO)

### New Files
- `apps/Client/src/types/restaurant.ts` — Restaurant TypeScript types
- `apps/Client/src/services/restaurantService.ts` — Restaurant API service
- `apps/Client/src/contexts/restaurantContextDef.ts` — RestaurantContext type definition
- `apps/Client/src/contexts/RestaurantContext.tsx` — RestaurantContext provider implementation
- `apps/Client/src/hooks/useRestaurant.ts` — useRestaurant custom hook
- `apps/Client/src/components/layout/TRRestaurantSelector.tsx` — Restaurant selector dropdown component
- `apps/Client/src/pages/restaurantos/RestaurantOSPersonsPage.tsx` — Placeholder page for Personas
- `apps/Client/src/pages/restaurantos/RestaurantOSDocumentsPage.tsx` — Placeholder page for Documentos
- `apps/Client/src/pages/restaurantos/RestaurantOSEventsPage.tsx` — Placeholder page for Eventos/Tareas
- `apps/Client/src/pages/restaurantos/RestaurantOSResourcesPage.tsx` — Placeholder page for Recursos/Inventario
- `apps/Client/src/pages/restaurantos/RestaurantOSDashboardPage.tsx` — Placeholder page for RestaurantOS Dashboard
- `apps/Client/src/pages/restaurantos/TRNoRestaurantPrompt.tsx` — Prompt shown when user has no restaurants
- `.claude/commands/e2e/test_restaurant_selector_navigation.md` — E2E test for restaurant selector and navigation

## Implementation Plan
### Phase 1: Foundation
Create the TypeScript types, API service, and context definition files that other components will depend on. These are the foundational building blocks that mirror the existing Entity pattern.

### Phase 2: Core Implementation
Build the RestaurantContext provider, useRestaurant hook, restaurant selector component, and placeholder pages. Wire up localStorage persistence and authentication-driven loading.

### Phase 3: Integration
Integrate the RestaurantContext provider into the app's provider tree, add RestaurantOS navigation items to the sidebar with the restaurant selector, register routes for placeholder pages, and create the E2E test file.

## Step by Step Tasks

### Step 1: Create E2E Test File
- Create `.claude/commands/e2e/test_restaurant_selector_navigation.md` following the pattern in `.claude/commands/e2e/test_section_based_sidebar_navigation.md` and `.claude/commands/e2e/test_entity_management.md`
- The E2E test should validate:
  1. Login and navigate to dashboard
  2. Expand the POCs section in sidebar
  3. Verify RestaurantOS subsection shows navigation items: Dashboard, Personas, Documentos, Eventos / Tareas, Recursos / Inventario
  4. Click on each RestaurantOS nav item and verify the route changes correctly to `/poc/restaurant-os/<page>`
  5. Verify each placeholder page shows a "Coming Soon" style message
  6. Verify the restaurant selector appears in the sidebar when RestaurantOS routes are active
  7. If user has restaurants, verify the selector shows restaurant names and switching works (persists in localStorage)
  8. If user has no restaurants, verify a prompt to create one is shown
  9. Take screenshots at each verification point

### Step 2: Create Restaurant TypeScript Types
- Create `apps/Client/src/types/restaurant.ts` with:
  - `Restaurant` interface matching backend `RestaurantResponseDTO` (id, name, address?, owner_id, created_at, updated_at)
  - `CreateRestaurantData` interface (name, address?)
  - `UpdateRestaurantData` interface (name?, address?)
- Add re-exports to `apps/Client/src/types/index.ts` by appending `export type { Restaurant, CreateRestaurantData, UpdateRestaurantData } from './restaurant'` or add the types directly to `index.ts` following the existing pattern

### Step 3: Create Restaurant Service
- Create `apps/Client/src/services/restaurantService.ts` following `entityService.ts` pattern
- Methods:
  - `getRestaurants(): Promise<Restaurant[]>` — GET `/restaurants`
  - `getRestaurant(id: string): Promise<Restaurant>` — GET `/restaurants/{id}`
  - `createRestaurant(data: CreateRestaurantData): Promise<Restaurant>` — POST `/restaurants`
  - `updateRestaurant(id: string, data: UpdateRestaurantData): Promise<Restaurant>` — PUT `/restaurants/{id}`
  - `deleteRestaurant(id: string): Promise<void>` — DELETE `/restaurants/{id}`
- Include proper logging with `INFO [RestaurantService]` and `ERROR [RestaurantService]` prefixes
- Use `apiClient` from `@/api/clients`

### Step 4: Create RestaurantContext Definition
- Create `apps/Client/src/contexts/restaurantContextDef.ts` following `entityContextDef.ts` pattern
- Define `RestaurantContextType` interface with:
  - `restaurants: Restaurant[]`
  - `currentRestaurant: Restaurant | null`
  - `isLoading: boolean`
  - `switchRestaurant: (restaurantId: string) => void`
  - `createRestaurant: (data: CreateRestaurantData) => Promise<Restaurant>`
  - `updateRestaurant: (id: string, data: UpdateRestaurantData) => Promise<Restaurant>`
  - `deleteRestaurant: (id: string) => Promise<void>`
  - `refreshRestaurants: () => Promise<void>`
- Create the context with `createContext<RestaurantContextType | undefined>(undefined)`

### Step 5: Create RestaurantContext Provider
- Create `apps/Client/src/contexts/RestaurantContext.tsx` following `EntityContext.tsx` pattern exactly
- Use `useAuth()` hook for `isAuthenticated` check
- localStorage key: `'currentRestaurantId'`
- On mount (when authenticated): fetch restaurants via `restaurantService.getRestaurants()`
- Restore selected restaurant from localStorage or select first
- Implement `switchRestaurant`, `createRestaurant`, `updateRestaurant`, `deleteRestaurant`, `refreshRestaurants` callbacks
- Memoize all callbacks with `useCallback` and the context value with `useMemo`
- Include proper logging with `INFO [RestaurantContext]` and `ERROR [RestaurantContext]` prefixes

### Step 6: Create useRestaurant Hook
- Create `apps/Client/src/hooks/useRestaurant.ts` following `useEntity.ts` pattern
- Import `RestaurantContext` and `RestaurantContextType` from `restaurantContextDef`
- Throw descriptive error if used outside `RestaurantProvider`

### Step 7: Create TRRestaurantSelector Component
- Create `apps/Client/src/components/layout/TRRestaurantSelector.tsx`
- Use MUI `FormControl`, `InputLabel`, `Select`, `MenuItem` (same pattern as entity selector in `TRCollapsibleSidebar.tsx` lines 318-338)
- Props interface: `{ open: boolean }` — controls whether to show full selector or collapsed initial
- Use `useRestaurant()` hook to get `currentRestaurant`, `restaurants`, `switchRestaurant`
- When `open`: render full Select dropdown with label "Restaurante"
- When collapsed (`!open`): show first letter of current restaurant name
- Handle empty state: if no restaurants, show nothing (the no-restaurant prompt handles this at page level)

### Step 8: Create TRNoRestaurantPrompt Component
- Create `apps/Client/src/pages/restaurantos/TRNoRestaurantPrompt.tsx`
- Simple MUI Box with:
  - Restaurant icon
  - Typography: "No tienes restaurantes" (or similar Spanish message)
  - Typography: "Crea tu primer restaurante para comenzar"
  - Button: "Crear Restaurante" that opens a simple create form
- Use `useRestaurant()` to call `createRestaurant` with a simple form (name, optional address) using `react-hook-form`
- Use MUI Dialog for the creation form

### Step 9: Create Placeholder Pages
- Create `apps/Client/src/pages/restaurantos/RestaurantOSDashboardPage.tsx`:
  - Import and use `useRestaurant()` to get `currentRestaurant`
  - If no restaurants: render `TRNoRestaurantPrompt`
  - If restaurant selected: show "RestaurantOS Dashboard — {currentRestaurant.name}" with "Próximamente" message
- Create `apps/Client/src/pages/restaurantos/RestaurantOSPersonsPage.tsx`:
  - Same pattern: check for restaurant, show "Personas — Próximamente"
- Create `apps/Client/src/pages/restaurantos/RestaurantOSDocumentsPage.tsx`:
  - Same pattern: check for restaurant, show "Documentos — Próximamente"
- Create `apps/Client/src/pages/restaurantos/RestaurantOSEventsPage.tsx`:
  - Same pattern: check for restaurant, show "Eventos / Tareas — Próximamente"
- Create `apps/Client/src/pages/restaurantos/RestaurantOSResourcesPage.tsx`:
  - Same pattern: check for restaurant, show "Recursos / Inventario — Próximamente"
- All pages use MUI Box, Typography with consistent styling

### Step 10: Update Sidebar Navigation
- Modify `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`:
  - Add new MUI icon imports: `RestaurantIcon`, `DescriptionIcon`, `EventIcon`, `InventoryIcon` (from `@mui/icons-material`)
  - Update the `navigationSections` array's POCs > RestaurantOS subsection to include nav items:
    - `{ label: 'Dashboard', path: '/poc/restaurant-os/dashboard', icon: <RestaurantIcon /> }`
    - `{ label: 'Personas', path: '/poc/restaurant-os/persons', icon: <PeopleIcon /> }`
    - `{ label: 'Documentos', path: '/poc/restaurant-os/documents', icon: <DescriptionIcon /> }`
    - `{ label: 'Eventos / Tareas', path: '/poc/restaurant-os/events', icon: <EventIcon /> }`
    - `{ label: 'Recursos / Inventario', path: '/poc/restaurant-os/resources', icon: <InventoryIcon /> }`
  - Add the `TRRestaurantSelector` component below the entity selector section (after the entity divider)
  - Only show the restaurant selector when the current route starts with `/poc/restaurant-os` (use `useLocation()` which is already imported)

### Step 11: Update Route Registration
- Modify `apps/Client/src/App.tsx`:
  - Import all placeholder pages from `@/pages/restaurantos/`
  - Import `RestaurantProvider` from `@/contexts/RestaurantContext`
  - Replace the existing catch-all `/poc/restaurant-os/*` route with individual nested routes:
    ```
    /poc/restaurant-os/dashboard → RestaurantOSDashboardPage
    /poc/restaurant-os/persons → RestaurantOSPersonsPage
    /poc/restaurant-os/documents → RestaurantOSDocumentsPage
    /poc/restaurant-os/events → RestaurantOSEventsPage
    /poc/restaurant-os/resources → RestaurantOSResourcesPage
    ```
  - Each route should be wrapped in `ProtectedRoute > TRMainLayout` (same pattern as existing routes)
  - Add a default redirect: `/poc/restaurant-os` → `/poc/restaurant-os/dashboard`

### Step 12: Add RestaurantProvider to Provider Tree
- Modify `apps/Client/src/main.tsx`:
  - Import `RestaurantProvider` from `@/contexts/RestaurantContext`
  - Add `<RestaurantProvider>` wrapping inside `<EntityProvider>` (after EntityProvider, before ThemeProvider):
    ```
    <AuthProvider>
      <EntityProvider>
        <RestaurantProvider>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <App />
          </ThemeProvider>
        </RestaurantProvider>
      </EntityProvider>
    </AuthProvider>
    ```

### Step 13: Run Validation Commands
- Execute all validation commands to ensure zero regressions
- Run the E2E test if application is running

## Testing Strategy
### Unit Tests
- No new backend unit tests needed (backend is already implemented and tested)
- Frontend testing is done via E2E tests using Playwright (per project convention)

### Edge Cases
- User has zero restaurants → TRNoRestaurantPrompt displayed with creation form
- User has one restaurant → auto-selected, selector still visible but with single option
- User has multiple restaurants → selector shows all, switching persists to localStorage
- User logs out → restaurants and currentRestaurant cleared, localStorage key removed on next load
- Stored restaurant ID in localStorage references a deleted restaurant → falls back to first available
- API call to fetch restaurants fails → error logged, empty state shown

## Acceptance Criteria
- RestaurantContext provides currentRestaurant, restaurants, switchRestaurant, and loading state
- Selected restaurant persists in localStorage across page refreshes
- Restaurant selector dropdown appears in the sidebar when navigating RestaurantOS routes
- Sidebar POCs > RestaurantOS subsection shows 5 navigation items (Dashboard, Personas, Documentos, Eventos/Tareas, Recursos/Inventario)
- Clicking each nav item navigates to the correct `/poc/restaurant-os/<page>` route
- Each placeholder page displays a "Próximamente" (Coming Soon) message with the restaurant name
- If user has no restaurants, a prompt to create one is displayed instead of page content
- UI text is in Spanish (Colombian): "Restaurante", "Personas", "Documentos", "Eventos / Tareas", "Recursos / Inventario"
- TypeScript compilation passes with zero errors
- Production build succeeds with zero errors
- No console errors or React warnings

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest` - Run Server tests to validate the feature works with zero regressions
- `cd apps/Client && npx tsc --noEmit` - Run Client type check to validate the feature works with zero regressions
- `cd apps/Client && npm run build` - Run Client build to validate the feature works with zero regressions

Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_restaurant_selector_navigation.md` E2E test file to validate this functionality works.

## Notes
- The backend restaurant API is fully implemented (ROS-001 dependency satisfied): GET/POST/PUT/DELETE `/api/restaurants`
- This feature runs in parallel with ROS-007 (Task Engine) which is backend-only, so no conflicts expected
- Wave 4 will replace the placeholder pages with full CRUD management pages that use `useRestaurant()` to scope data
- The RestaurantContext is placed at the app root level (in main.tsx) rather than only around restaurant routes, because the sidebar needs access to it for the restaurant selector regardless of current route
- The restaurant selector only renders visually when the user navigates to `/poc/restaurant-os/*` routes, to avoid cluttering the sidebar for Finance-only users
- Backend `RestaurantResponseDTO` returns `owner_id` as an optional `UUID` and timestamps as `datetime` — the frontend types use `string` for these fields since JSON serialization converts them
