# RestaurantOS Operations Dashboard Page

**ADW ID:** 28ba0bbb
**Date:** 2026-03-04
**Specification:** specs/issue-104-adw-28ba0bbb-sdlc_planner-restaurant-ops-dashboard-page.md

## Overview

Replaces the placeholder "Próximamente" RestaurantOS Dashboard page with a fully functional operations dashboard. The page aggregates data from all four core RestaurantOS entities (Person, Document, Event, Resource) into a single daily operational view, giving restaurant managers an at-a-glance overview of employees, stock levels, expiring documents, tasks, and recent inventory movements.

## What Was Built

- **Backend aggregation endpoint** (`GET /api/restaurant-dashboard/{restaurant_id}/overview`) that queries multiple services and returns consolidated dashboard data
- **RestaurantDashboardService** that orchestrates data aggregation from five entity services (event, document, resource, inventory, person)
- **New repository and service query methods** across five existing entities for dashboard-specific queries (expiring documents, low-stock items, recent movements, pending alerts, count methods)
- **Frontend dashboard page** with stat cards, today's tasks grouped by employee, alerts panel, and recent inventory movements table
- **TRAlertsList component** — reusable alerts panel showing document expirations, low-stock items, and pending alerts
- **Enhanced TRStatCard component** — now supports both financial variants (income/expense/balance) and generic mode (custom icon + color)
- **Dashboard service, hook, and types** on the frontend for API integration
- **Backend tests** for the dashboard API endpoint
- **E2E test specification** for dashboard validation

## Technical Implementation

### Files Modified

- `apps/Server/main.py`: Registered `restaurant_dashboard_router`
- `apps/Server/src/adapter/rest/restaurant_dashboard_routes.py`: New — dashboard overview endpoint with DTO serialization
- `apps/Server/src/core/services/restaurant_dashboard_service.py`: New — orchestrates calls to event, document, resource, inventory, and person services
- `apps/Server/src/core/services/document_service.py`: Added `get_expiring_documents()` and `count_active()` methods
- `apps/Server/src/core/services/event_service.py`: Added `get_tasks_by_date()`, `get_pending_alerts()`, and `count_completed_tasks()` methods
- `apps/Server/src/core/services/inventory_service.py`: Added `get_recent_movements()` method
- `apps/Server/src/core/services/person_service.py`: Added `count_by_type()` method
- `apps/Server/src/core/services/resource_service.py`: Added `get_low_stock_resources()` and `count_resources()` methods
- `apps/Server/src/repository/document_repository.py`: Added `get_expiring_soon()` and `count_active()` query methods
- `apps/Server/src/repository/event_repository.py`: Added `get_tasks_by_date()`, `get_pending_alerts()`, and `count_completed_tasks()` query methods
- `apps/Server/src/repository/inventory_movement_repository.py`: Added `get_recent()` query method
- `apps/Server/src/repository/person_repository.py`: Added `count_by_type()` query method
- `apps/Server/src/repository/resource_repository.py`: Added `get_low_stock()` and `count()` query methods
- `apps/Server/tests/test_restaurant_dashboard_api.py`: New — comprehensive test suite for dashboard endpoint
- `apps/Client/src/pages/restaurantos/RestaurantOSDashboardPage.tsx`: Replaced placeholder with full dashboard implementation
- `apps/Client/src/components/ui/TRStatCard.tsx`: Enhanced with generic mode (discriminated union props)
- `apps/Client/src/components/ui/TRAlertsList.tsx`: New — three-section alerts panel component
- `apps/Client/src/hooks/useDashboardOverview.ts`: New — custom hook for fetching dashboard data
- `apps/Client/src/services/restaurantDashboardService.ts`: New — API service for dashboard endpoint
- `apps/Client/src/types/dashboard.ts`: New — TypeScript interfaces for DashboardOverview and DashboardStats
- `.claude/commands/e2e/test_restaurant_ops_dashboard.md`: New — E2E test specification

### Key Changes

- **Entity composition pattern**: RestaurantDashboardService delegates to five existing entity services rather than duplicating data access logic, following Clean Architecture principles
- **TRStatCard discriminated union**: The component now uses a TypeScript discriminated union (`TRStatCardFinancialProps | TRStatCardGenericProps`) to support both financial stat cards and generic stat cards with custom icons/colors
- **Dashboard overview DTO serialization**: The route layer serializes raw SQLAlchemy model instances through existing Pydantic DTOs (EventResponseDTO, DocumentResponseDTO, etc.) before returning JSON
- **Restaurant access control**: Dashboard endpoint checks user-restaurant membership via `_check_restaurant_access` before aggregating any data
- **Responsive grid layout**: Uses MUI Grid with breakpoints — 4 stat cards across on desktop (md=3), 2 on tablet (sm=6), 1 on mobile (xs=12)

## How to Use

1. Navigate to `/poc/restaurant-os/dashboard` in the application
2. Select a restaurant using the restaurant selector (if not already selected)
3. The dashboard displays:
   - **Stat cards** (top row): Empleados, Recursos, Documentos Activos, Tareas Completadas Hoy
   - **Tareas de Hoy** (middle left): Today's tasks grouped by responsible employee with status badges
   - **Alertas** (middle right): Document expirations (next 30 days), low-stock items, and pending system alerts
   - **Movimientos Recientes de Inventario** (bottom): Last 10 inventory movements in a table
4. If no data exists, each section shows an appropriate empty state message in Spanish
5. On error, a retry button is displayed to re-fetch the dashboard data

## Configuration

No additional configuration required. The dashboard uses the existing restaurant context and authentication.

- Backend endpoint: `GET /api/restaurant-dashboard/{restaurant_id}/overview`
- Authentication: JWT Bearer token (same as all other endpoints)
- Authorization: User must have membership in the target restaurant

## Testing

- **Backend tests**: `cd apps/Server && python -m pytest tests/test_restaurant_dashboard_api.py`
- **TypeScript check**: `cd apps/Client && npx tsc --noEmit`
- **Production build**: `cd apps/Client && npm run build`
- **E2E test**: See `.claude/commands/e2e/test_restaurant_ops_dashboard.md`

## Notes

- The dashboard aggregates data across five services in a single API call — for restaurants with large datasets, consider adding caching or pagination in the future
- Tasks are grouped by `responsible_id` on the client side; employee names display as truncated UUIDs unless a person lookup is added
- The `TRAlertsList` component is reusable and can be placed on other pages that need alert displays
- All UI text is in Spanish to match existing RestaurantOS pages
