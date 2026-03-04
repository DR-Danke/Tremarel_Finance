# Feature: RestaurantOS Operations Dashboard Page

## Metadata
issue_number: `104`
adw_id: `28ba0bbb`
issue_json: `N/A`

## Feature Description
Build the RestaurantOS Operations Dashboard page — the daily operational overview for restaurant managers. This page aggregates data from all 4 core RestaurantOS entities (Person, Document, Event, Resource) into a single operational view. It shows summary stat cards (employees, resources, active documents, tasks completed today), today's tasks grouped by employee, upcoming document expirations, low-stock alerts, recent inventory movements, and pending profitability/alert warnings. This is the "daily operating system" — the first thing a manager sees when they open RestaurantOS.

## User Story
As a restaurant manager
I want to see a consolidated operational dashboard when I open RestaurantOS
So that I can quickly assess the day's tasks, expiring documents, stock levels, and recent inventory activity in one view

## Problem Statement
Currently the RestaurantOS Dashboard page (`/poc/restaurant-os/dashboard`) is a placeholder showing "Próximamente". Restaurant managers have no centralized view of their daily operations and must navigate to each entity page individually to check tasks, documents, stock levels, and inventory movements.

## Solution Statement
Replace the placeholder dashboard with a fully functional operations dashboard that:
1. Creates a backend aggregation endpoint (`/api/restaurant-dashboard/{restaurant_id}/overview`) that queries multiple services and returns consolidated data
2. Adds helper query methods to existing services (expiring documents, low-stock items, recent movements, pending alerts, count methods)
3. Builds a responsive frontend dashboard page with stat cards, task summary, alerts panel, and recent movements table
4. Creates reusable UI components (`TRStatCard`, `TRAlertsList`) for the dashboard and potential future use

## Relevant Files
Use these files to implement the feature:

**Backend — Routes (adapter/rest layer):**
- `apps/Server/main.py` — Router registration; add new `restaurant_dashboard_routes` router
- `apps/Server/src/adapter/rest/restaurant_event_routes.py` — Reference for route patterns (auth, restaurant_id param, error handling)
- `apps/Server/src/adapter/rest/restaurant_document_routes.py` — Reference for route patterns
- `apps/Server/src/adapter/rest/restaurant_resource_routes.py` — Reference for route patterns
- `apps/Server/src/adapter/rest/dependencies.py` — `get_current_user` dependency for auth

**Backend — Services (core/services layer):**
- `apps/Server/src/core/services/restaurant_event_service.py` — Add `get_tasks_summary()`, `get_pending_alerts()`, `count_completed_tasks()` methods
- `apps/Server/src/core/services/restaurant_document_service.py` — Add `get_expiring_soon()`, `count_active()` methods
- `apps/Server/src/core/services/restaurant_resource_service.py` — Add `get_low_stock()`, `count()` methods
- `apps/Server/src/core/services/inventory_service.py` — Add `get_recent()` method
- `apps/Server/src/core/services/restaurant_person_service.py` — Add `count_by_type()` method

**Backend — Repositories (data access layer):**
- `apps/Server/src/repository/restaurant_event_repository.py` — Add query methods for tasks summary, pending alerts, completed count
- `apps/Server/src/repository/restaurant_document_repository.py` — Add query methods for expiring documents, active count
- `apps/Server/src/repository/restaurant_resource_repository.py` — Add query methods for low stock, total count
- `apps/Server/src/repository/inventory_movement_repository.py` — Add query method for recent movements with limit
- `apps/Server/src/repository/restaurant_person_repository.py` — Add query method for count by type

**Backend — Models:**
- `apps/Server/src/models/event.py` — Event model (type, status, responsible_id, date fields)
- `apps/Server/src/models/document.py` — Document model (expiration_date, type fields)
- `apps/Server/src/models/resource.py` — Resource model (current_stock, minimum_stock fields)
- `apps/Server/src/models/inventory_movement.py` — InventoryMovement model
- `apps/Server/src/models/person.py` — Person model (type field)

**Backend — Tests:**
- `apps/Server/tests/` — Existing test directory; add dashboard route and service tests

**Frontend — Pages:**
- `apps/Client/src/pages/restaurantos/RestaurantOSDashboardPage.tsx` — Replace placeholder with full dashboard implementation

**Frontend — Components:**
- `apps/Client/src/components/ui/TRStatCard.tsx` — Existing stat card component (check if needs enhancement or if new one needed)
- `apps/Client/src/components/ui/TRExpirationBadge.tsx` — Reuse for document expiration display
- `apps/Client/src/components/ui/TREventStatusBadge.tsx` — Reuse for task status display
- `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx` — Verify Dashboard is first item in RestaurantOS section (already present)

**Frontend — Services:**
- `apps/Client/src/services/eventService.ts` — Reference for service patterns
- `apps/Client/src/services/documentService.ts` — Reference for service patterns
- `apps/Client/src/services/resourceService.ts` — Reference for service patterns

**Frontend — Hooks:**
- `apps/Client/src/hooks/useRestaurant.ts` — RestaurantContext consumer hook
- `apps/Client/src/hooks/useEvents.ts` — Reference for hook patterns
- `apps/Client/src/hooks/useDocuments.ts` — Reference for hook patterns

**Frontend — Types:**
- `apps/Client/src/types/event.ts` — Event, EventType, EventStatus types
- `apps/Client/src/types/document.ts` — Document, ExpirationStatus types
- `apps/Client/src/types/resource.ts` — Resource, InventoryMovement types

**Frontend — Contexts:**
- `apps/Client/src/contexts/RestaurantContext.tsx` — RestaurantProvider (currentRestaurant)
- `apps/Client/src/contexts/restaurantContextDef.ts` — RestaurantContext type definitions

**Frontend — App routing:**
- `apps/Client/src/App.tsx` — Route registration (route already exists, verify)

**Conditional Documentation:**
- `app_docs/feature-342b3948-restaurant-selector-multitenant-navigation.md` — Restaurant selector & multi-tenant navigation patterns
- `app_docs/feature-a692d2db-restaurant-multi-tenant-entity.md` — Restaurant multi-tenant entity architecture
- `app_docs/feature-9297a9a2-event-task-management-page.md` — Event/Task management page patterns
- `app_docs/feature-26972c6e-document-management-page.md` — Document management page patterns
- `app_docs/feature-958fff68-resource-inventory-page.md` — Resource & inventory page patterns

**E2E Test References:**
- `.claude/commands/test_e2e.md` — E2E test runner instructions
- `.claude/commands/e2e/test_basic_query.md` — E2E test file format example

### New Files
- `apps/Server/src/adapter/rest/restaurant_dashboard_routes.py` — Dashboard aggregation API endpoint
- `apps/Server/src/core/services/restaurant_dashboard_service.py` — Dashboard service that orchestrates data aggregation from multiple services
- `apps/Server/tests/adapter/rest/test_restaurant_dashboard_routes.py` — Backend tests for dashboard endpoint
- `apps/Client/src/services/restaurantDashboardService.ts` — Frontend service for dashboard API calls
- `apps/Client/src/hooks/useDashboardOverview.ts` — Custom hook for fetching dashboard overview data
- `apps/Client/src/types/dashboard.ts` — TypeScript interfaces for dashboard overview response
- `apps/Client/src/components/ui/TRAlertsList.tsx` — Alerts panel component for dashboard
- `.claude/commands/e2e/test_restaurant_ops_dashboard.md` — E2E test specification for dashboard

## Implementation Plan

### Phase 1: Foundation
Establish backend data access layer by adding query methods to existing repositories for dashboard-specific queries (expiring documents, low-stock resources, recent movements, pending alerts, count methods). Then add corresponding service methods that call these repositories. This phase does not create new files — it extends existing ones.

### Phase 2: Core Implementation
1. Create the `RestaurantDashboardService` that orchestrates calls to all entity services and returns an aggregated overview DTO.
2. Create the `restaurant_dashboard_routes.py` endpoint that exposes the aggregation via `GET /api/restaurant-dashboard/{restaurant_id}/overview`.
3. Register the new router in `main.py`.
4. Create frontend types (`dashboard.ts`), service (`restaurantDashboardService.ts`), and hook (`useDashboardOverview.ts`).
5. Create the `TRAlertsList` component for the alerts panel.
6. Replace the placeholder `RestaurantOSDashboardPage.tsx` with full dashboard grid layout.

### Phase 3: Integration
1. Verify sidebar navigation already has Dashboard as the first RestaurantOS item.
2. Verify route `/poc/restaurant-os/dashboard` is already registered in `App.tsx`.
3. Add backend tests for the dashboard endpoint.
4. Create E2E test specification.
5. Run full validation suite (pytest, typecheck, build).

## Step by Step Tasks

### Step 1: Add Dashboard Query Methods to Existing Repositories
- Open `apps/Server/src/repository/restaurant_document_repository.py` and add:
  - `get_expiring_soon(db, restaurant_id, days=30)` — query documents where `expiration_date` is between today and today + N days, ordered by expiration_date ASC
  - `count_active(db, restaurant_id)` — count documents where expiration_date is NULL or expiration_date >= today
- Open `apps/Server/src/repository/restaurant_resource_repository.py` and add:
  - `get_low_stock(db, restaurant_id)` — query resources where `current_stock < minimum_stock` and `minimum_stock > 0`
  - `count(db, restaurant_id)` — count all resources for a restaurant
- Open `apps/Server/src/repository/inventory_movement_repository.py` and add:
  - `get_recent(db, restaurant_id, limit=10)` — query last N movements ordered by `created_at DESC`, with limit
- Open `apps/Server/src/repository/restaurant_event_repository.py` and add:
  - `get_tasks_by_date(db, restaurant_id, target_date)` — query events where type='tarea' and date matches target_date
  - `get_pending_alerts(db, restaurant_id)` — query events where type IN ('alerta_stock', 'alerta_rentabilidad', 'vencimiento') and status='pending'
  - `count_completed_tasks(db, restaurant_id, target_date)` — count events where type='tarea', status='completed', and completed_at date matches target_date
- Open `apps/Server/src/repository/restaurant_person_repository.py` and add:
  - `count_by_type(db, restaurant_id, person_type)` — count persons filtered by type (e.g. 'employee')

### Step 2: Add Dashboard Service Methods to Existing Services
- Open `apps/Server/src/core/services/restaurant_document_service.py` and add:
  - `get_expiring_soon(db, user_id, restaurant_id, days=30)` — with restaurant access check, calls repository
  - `count_active(db, user_id, restaurant_id)` — with restaurant access check, calls repository
- Open `apps/Server/src/core/services/restaurant_resource_service.py` and add:
  - `get_low_stock(db, user_id, restaurant_id)` — with restaurant access check, calls repository
  - `count(db, user_id, restaurant_id)` — with restaurant access check, calls repository
- Open `apps/Server/src/core/services/inventory_service.py` and add:
  - `get_recent(db, user_id, restaurant_id, limit=10)` — with restaurant access check, calls repository
- Open `apps/Server/src/core/services/restaurant_event_service.py` and add:
  - `get_tasks_summary(db, user_id, restaurant_id, target_date)` — with restaurant access check, returns tasks grouped by responsible_id
  - `get_pending_alerts(db, user_id, restaurant_id)` — with restaurant access check, calls repository
  - `count_completed_tasks(db, user_id, restaurant_id, target_date)` — with restaurant access check, calls repository
- Open `apps/Server/src/core/services/restaurant_person_service.py` and add:
  - `count_by_type(db, user_id, restaurant_id, person_type)` — with restaurant access check, calls repository

### Step 3: Create Dashboard Service (Backend)
- Create `apps/Server/src/core/services/restaurant_dashboard_service.py`
- Import all 5 entity services (event, document, resource, inventory, person)
- Create `RestaurantDashboardService` class with:
  - `get_overview(db, user_id, restaurant_id)` method that calls all service methods and assembles the response dict:
    ```python
    {
        "today_tasks": [...],          # from event_service.get_tasks_summary()
        "upcoming_expirations": [...], # from document_service.get_expiring_soon()
        "low_stock_items": [...],      # from resource_service.get_low_stock()
        "recent_movements": [...],     # from inventory_service.get_recent()
        "pending_alerts": [...],       # from event_service.get_pending_alerts()
        "stats": {
            "total_employees": int,    # from person_service.count_by_type()
            "total_resources": int,    # from resource_service.count()
            "active_documents": int,   # from document_service.count_active()
            "tasks_completed_today": int  # from event_service.count_completed_tasks()
        }
    }
    ```
- Use `_check_restaurant_access` pattern from existing services
- Add print logging for all operations following `INFO [RestaurantDashboardService]:` pattern

### Step 4: Create Dashboard API Endpoint (Backend)
- Create `apps/Server/src/adapter/rest/restaurant_dashboard_routes.py`
- Define `router = APIRouter(prefix="/api/restaurant-dashboard", tags=["RestaurantDashboard"])`
- Add `GET /{restaurant_id}/overview` endpoint:
  - Depends on `get_current_user` for auth
  - Depends on `get_db` for database session
  - Calls `restaurant_dashboard_service.get_overview(db, current_user["id"], restaurant_id)`
  - Returns the overview dict
  - Error handling: 403 for PermissionError, 500 for unexpected errors
  - Logging: `print(f"INFO [RestaurantDashboard]: Fetching overview for restaurant {restaurant_id}")`
- Register router in `apps/Server/main.py` with `app.include_router(restaurant_dashboard_router)`

### Step 5: Create Backend Tests
- Create `apps/Server/tests/adapter/rest/test_restaurant_dashboard_routes.py`
- Test `GET /api/restaurant-dashboard/{restaurant_id}/overview`:
  - Test successful overview fetch returns expected structure (today_tasks, upcoming_expirations, low_stock_items, recent_movements, pending_alerts, stats)
  - Test unauthenticated request returns 401
  - Test restaurant access denied returns 403
  - Test with non-existent restaurant_id returns appropriate error
- Use existing test patterns from other route test files

### Step 6: Create Frontend Types
- Create `apps/Client/src/types/dashboard.ts`
- Define interfaces:
  ```typescript
  interface DashboardStats {
    total_employees: number
    total_resources: number
    active_documents: number
    tasks_completed_today: number
  }

  interface DashboardAlert {
    id: string
    type: 'vencimiento' | 'alerta_stock' | 'alerta_rentabilidad'
    description: string | null
    date: string
    status: string
    severity: 'warning' | 'critical'
  }

  interface DashboardOverview {
    today_tasks: Event[]
    upcoming_expirations: Document[]
    low_stock_items: Resource[]
    recent_movements: InventoryMovement[]
    pending_alerts: DashboardAlert[]
    stats: DashboardStats
  }
  ```

### Step 7: Create Frontend Dashboard Service
- Create `apps/Client/src/services/restaurantDashboardService.ts`
- Follow existing service pattern (apiClient, console logging)
- Single method:
  ```typescript
  async getOverview(restaurantId: string): Promise<DashboardOverview>
  ```
- Calls `GET /restaurant-dashboard/${restaurantId}/overview`

### Step 8: Create Frontend Dashboard Hook
- Create `apps/Client/src/hooks/useDashboardOverview.ts`
- Follow existing hook pattern (useState, useEffect, useCallback)
- Returns: `{ overview: DashboardOverview | null, isLoading: boolean, error: string | null, refresh: () => Promise<void> }`
- Auto-fetches when restaurantId changes
- Sets loading/error states appropriately

### Step 9: Check and Enhance TRStatCard Component
- Read `apps/Client/src/components/ui/TRStatCard.tsx` to check its current implementation
- If it exists and meets the dashboard needs (title, value, icon, color props), reuse as-is
- If it only supports financial stat cards (income/expense/balance), create a more generic version or enhance it to support:
  ```typescript
  interface TRStatCardProps {
    title: string
    value: number | string
    icon: React.ReactNode
    color?: string
  }
  ```
- The card should render a Paper/Card with: icon (colored), title (Typography variant subtitle2), value (Typography variant h4, bold)

### Step 10: Create TRAlertsList Component
- Create `apps/Client/src/components/ui/TRAlertsList.tsx`
- Props interface:
  ```typescript
  interface TRAlertsListProps {
    expirations: Document[]
    lowStockItems: Resource[]
    pendingAlerts: DashboardAlert[]
  }
  ```
- Render three sections with List components:
  1. **Document Expirations** — sorted by expiration_date ASC (closest first), show document type, description, days until expiration, use `TRExpirationBadge` for status. Color: orange tint.
  2. **Low Stock Items** — show resource name, current_stock vs minimum_stock, unit. Color: red tint.
  3. **Profitability/Other Alerts** — show alert description, date, type. Color: yellow tint.
- Each item should be clickable (navigate to relevant entity page)
- Empty state per section: "No hay alertas" or similar message
- Use MUI `List`, `ListItem`, `ListItemIcon`, `ListItemText`, `Chip`, `Divider`

### Step 11: Build RestaurantOSDashboardPage
- Replace the placeholder content in `apps/Client/src/pages/restaurantos/RestaurantOSDashboardPage.tsx`
- Use `useRestaurant()` for currentRestaurant
- Use new `useDashboardOverview(currentRestaurant?.id)` hook
- Layout structure with MUI Grid:
  - **Page header**: "Dashboard Operativo" title + restaurant name subtitle
  - **Top row (Grid container, 4 columns on desktop, 2 on tablet, 1 on mobile):**
    - TRStatCard: "Empleados" — stats.total_employees — PeopleIcon — blue
    - TRStatCard: "Recursos" — stats.total_resources — InventoryIcon — green
    - TRStatCard: "Documentos Activos" — stats.active_documents — DescriptionIcon — purple
    - TRStatCard: "Tareas Completadas Hoy" — stats.tasks_completed_today — CheckCircleIcon — teal
  - **Middle row (Grid container, 2 columns on desktop, 1 on mobile):**
    - Left column: **Today's Tasks** section
      - Group `today_tasks` by `responsible_id`
      - For each employee group: Card with employee name header, list of tasks with status badges
      - Show quick-complete checkmark action for pending tasks
      - Empty state: "No hay tareas para hoy"
    - Right column: **TRAlertsList** component with expirations, low stock, and pending alerts
  - **Bottom row (full width):**
    - **Recent Inventory Movements** table (MUI Table)
    - Columns: Date, Resource Name, Type (entry/exit), Quantity, Reason, Person
    - Show last 10 movements
    - Empty state: "No hay movimientos recientes"
- Loading state: Show `CircularProgress` centered while `isLoading` is true
- No-restaurant state: Show `TRNoRestaurantPrompt` if `restaurants.length === 0`
- Error state: Show `Alert` component with error message and retry button

### Step 12: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` to understand the E2E test format
- Create `.claude/commands/e2e/test_restaurant_ops_dashboard.md` with:
  - **Prerequisites**: Backend running at configured port, Frontend running at configured port, user logged in, at least one restaurant created
  - **Test Steps**:
    1. Navigate to `/poc/restaurant-os/dashboard`
    2. Verify page loads with "Dashboard Operativo" heading and restaurant name
    3. Verify 4 stat cards are visible (Empleados, Recursos, Documentos Activos, Tareas Completadas Hoy)
    4. Verify stat cards show numeric values (may be 0 for empty restaurant)
    5. Verify "Today's Tasks" section is visible with appropriate empty state
    6. Verify "Alerts" panel is visible with appropriate empty state
    7. Verify "Recent Movements" section is visible with appropriate empty state
    8. Navigate to Events page, create a task for today, return to dashboard, verify task appears
    9. Navigate to Documents page, create an expiring document, return to dashboard, verify it appears in alerts
    10. Verify responsive layout: resize viewport to mobile, cards stack vertically
  - **Success Criteria**: All sections load, data is scoped to current restaurant, empty states display properly, navigation works

### Step 13: Verify Route and Sidebar Registration
- Read `apps/Client/src/App.tsx` and confirm `/poc/restaurant-os/dashboard` route exists (it should already be registered from the placeholder)
- Read `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx` and confirm Dashboard is the first item in the RestaurantOS section
- No changes expected — just verification

### Step 14: Run Validation Commands
- Run `cd apps/Server && python -m pytest tests/` to validate backend tests pass
- Run `cd apps/Client && npx tsc --noEmit` to validate frontend TypeScript compiles without errors
- Run `cd apps/Client && npm run build` to validate frontend production build succeeds
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_restaurant_ops_dashboard.md` to validate E2E

## Testing Strategy

### Unit Tests
- **Backend**: Test `RestaurantDashboardService.get_overview()` returns correct structure with mocked repository data
- **Backend**: Test each new repository method (get_expiring_soon, get_low_stock, get_recent, get_tasks_by_date, get_pending_alerts, count methods)
- **Backend**: Test dashboard route returns 200 with valid restaurant_id, 401 without auth, 403 without access
- **Frontend**: TypeScript type-checks ensure all interfaces are correctly defined

### Edge Cases
- Dashboard with completely empty restaurant (no persons, documents, events, resources) — should show all empty states
- Dashboard with no tasks for today but tasks on other days — "Today's Tasks" shows empty state
- Documents with NULL expiration_date — should not appear in "upcoming expirations"
- Resources with minimum_stock = 0 — should never trigger low-stock alert
- Restaurant with many items — verify performance with reasonable data volume
- User without restaurant access — should return 403

## Acceptance Criteria
- [ ] Dashboard page accessible at `/poc/restaurant-os/dashboard`
- [ ] Backend endpoint `GET /api/restaurant-dashboard/{restaurant_id}/overview` returns aggregated data
- [ ] Shows 4 summary stat cards (employees, resources, documents, tasks today)
- [ ] Shows today's tasks grouped by employee with status badges
- [ ] Shows upcoming document expirations (next 30 days) sorted by closest first
- [ ] Shows low stock alerts with current vs minimum stock values
- [ ] Shows recent inventory movements (last 10) in a table
- [ ] Shows pending alerts (vencimiento, alerta_stock, alerta_rentabilidad events)
- [ ] All data scoped to current restaurant (from RestaurantContext)
- [ ] Loading states shown while data is being fetched
- [ ] Empty states shown when no data available per section
- [ ] All components use TR prefix (TRStatCard, TRAlertsList)
- [ ] Responsive layout: cards stack on mobile breakpoints
- [ ] Backend tests pass
- [ ] Frontend TypeScript compiles without errors
- [ ] Frontend production build succeeds

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/` — Run Server tests to validate the feature works with zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate the feature works with zero regressions
- `cd apps/Client && npm run build` — Run Client build to validate the feature works with zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_restaurant_ops_dashboard.md` E2E test file to validate this functionality works

## Notes
- The dashboard page placeholder already exists at `apps/Client/src/pages/restaurantos/RestaurantOSDashboardPage.tsx` — this implementation replaces the placeholder content
- The route `/poc/restaurant-os/dashboard` and sidebar entry are already registered — no routing changes needed
- The `TRStatCard` component already exists at `apps/Client/src/components/ui/TRStatCard.tsx` — check its current interface before deciding whether to enhance or create a dashboard-specific variant
- Existing badge components (`TRExpirationBadge`, `TREventStatusBadge`) should be reused in the dashboard for consistency
- All UI text should be in Spanish to match existing RestaurantOS pages (e.g., "Empleados", "Recursos", "Documentos Activos", "No hay tareas para hoy")
- The `RestaurantDashboardService` follows the "entity composition" architecture pattern — it doesn't duplicate data access logic but delegates to existing entity services
- Event types used for alerts: `vencimiento`, `alerta_stock`, `alerta_rentabilidad` — these are system-generated events, distinct from user-created tasks
- The `is_low_stock` computed field already exists on the Resource model/type — leverage it for dashboard filtering
- For the tasks-by-employee grouping, use `responsible_id` to group and join with person names client-side (persons data available from the overview response or a separate fetch)
