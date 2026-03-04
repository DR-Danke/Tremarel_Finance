# E2E Test: Restaurant Operations Dashboard

Test that the RestaurantOS operations dashboard displays consolidated operational data including stat cards, today's tasks, alerts, and recent inventory movements.

## User Story

As a restaurant manager
I want to see a consolidated operational dashboard when I open RestaurantOS
So that I can quickly assess the day's tasks, expiring documents, stock levels, and recent inventory activity in one view

## Prerequisites

- Backend server running at configured port (default: http://localhost:8000)
- Frontend server running at configured port (default: http://localhost:5173)
- A test user account exists with valid credentials
- The user is authenticated
- At least one restaurant exists for the user

## Test Steps

### Setup - Navigate and Authenticate

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. If not logged in, log in with test credentials
3. Navigate to `/poc/restaurant-os/dashboard`
4. Take a screenshot of the dashboard page

### Test: Page Header

5. **Verify** page loads with:
   - "Dashboard Operativo" heading visible
   - Restaurant name displayed as subtitle
6. Take a screenshot

### Test: Stat Cards Display

7. **Verify** 4 stat cards are visible:
   - "Empleados" card with numeric value
   - "Recursos" card with numeric value
   - "Documentos Activos" card with numeric value
   - "Tareas Completadas Hoy" card with numeric value
8. **Verify** all stat cards show numeric values (may be 0 for empty restaurant)
9. Take a screenshot of the stat cards row

### Test: Today's Tasks Section

10. **Verify** "Tareas de Hoy" section heading is visible
11. If no tasks exist: **Verify** "No hay tareas para hoy" empty state message
12. If tasks exist: **Verify** tasks are displayed with status badges
13. Take a screenshot

### Test: Alerts Panel

14. **Verify** "Alertas" section heading is visible
15. **Verify** three subsections exist:
    - "Vencimientos de Documentos"
    - "Stock Bajo"
    - "Alertas Pendientes"
16. If no alerts exist: **Verify** appropriate empty state messages (e.g., "No hay documentos por vencer")
17. Take a screenshot

### Test: Recent Movements Section

18. **Verify** "Movimientos Recientes de Inventario" section heading is visible
19. If no movements exist: **Verify** "No hay movimientos recientes" empty state message
20. If movements exist: **Verify** table with columns: Fecha, Tipo, Cantidad, Razón, Notas
21. Take a screenshot

### Test: Responsive Layout

22. Resize viewport to mobile width (375px)
23. **Verify** stat cards stack vertically (1 per row)
24. **Verify** tasks and alerts sections stack vertically
25. Take a screenshot of mobile layout

## Success Criteria

- [ ] Dashboard page loads at `/poc/restaurant-os/dashboard`
- [ ] "Dashboard Operativo" heading and restaurant name are displayed
- [ ] 4 stat cards visible with numeric values
- [ ] Today's Tasks section renders with tasks or appropriate empty state
- [ ] Alerts panel renders with three subsections and appropriate empty states
- [ ] Recent Movements table renders with data or appropriate empty state
- [ ] All data is scoped to the current restaurant
- [ ] Responsive layout works on mobile viewports
- [ ] No console errors during navigation
