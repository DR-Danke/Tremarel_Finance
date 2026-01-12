# E2E Test: ServiceDesk Ticket List

Test the ServiceDesk ticket list component with filtering, sorting, and pagination functionality.

## User Story

As an IT support technician
I want to view, filter, and sort support tickets in a data grid
So that I can efficiently manage my workload and prioritize tickets based on status, priority, and SLA deadlines

## Test Steps

1. Navigate to the `Application URL` ServiceDesk page (e.g., /servicedesk/tickets)
2. Take a screenshot of the initial state
3. **Verify** the page loads with the ticket list component visible:
   - Filter panel is present with "Filtros" header
   - DataGrid is visible with columns: Ticket #, Asunto, Estado, Prioridad, Categoría, Asignado a, SLA, Creado

4. **Verify** filter panel elements are present:
   - Search input with placeholder "Buscar por número, título o descripción..."
   - Estado dropdown
   - Prioridad dropdown
   - Categoría dropdown
   - Asignado a dropdown
   - Desde date picker
   - Hasta date picker
   - "Limpiar Filtros" button

5. Test filtering by status:
   - Click on Estado dropdown
   - Select "Abierto" option
   - **Verify** the filter is applied (chip count updates to 1)
   - Take a screenshot of the filtered results

6. Test filtering by priority:
   - Click on Prioridad dropdown
   - Select "Alta" option
   - **Verify** the filter chip count updates to 2
   - Take a screenshot

7. Test date range filter:
   - Set "Desde" date to first day of current month
   - **Verify** the filter is applied

8. Test search input:
   - Type "error" in the search input
   - Wait for debounce (300ms)
   - **Verify** search filter is applied

9. Test clear filters:
   - Click "Limpiar Filtros" button
   - **Verify** all filters are cleared
   - **Verify** filter chip count returns to 0
   - Take a screenshot of cleared filters

10. Test pagination:
    - If total rows > page size, verify pagination controls are visible
    - Verify "Filas por página" dropdown shows options [10, 25, 50, 100]
    - Take a screenshot of pagination

11. **Verify** ticket status badges display with correct colors:
    - "Nuevo" badge should be gray
    - "Abierto" badge should be blue
    - "Resuelto" badge should be green

12. **Verify** priority badges display with icons:
    - "Crítica" should show alarm icon in red
    - "Alta" should show warning icon in orange
    - "Media" should show info icon in yellow
    - "Baja" should show check icon in green

13. **Verify** SLA countdown displays:
    - SLA column shows time remaining with clock icon
    - Breached tickets show "Vencido" in red
    - Take a screenshot of SLA column

14. Test ticket click navigation:
    - Click on any ticket number link
    - **Verify** the ticket click handler is triggered or navigation occurs
    - Take a screenshot

15. Test filter panel collapse/expand:
    - Click on the filter panel header
    - **Verify** the filter controls collapse/hide
    - Click again to expand
    - **Verify** the filter controls reappear

## Success Criteria

- Page loads with ticket list and filter panel
- All filter dropdowns are functional
- Search input triggers filtered results after debounce
- Clear filters button resets all filters
- Pagination controls work correctly
- Status badges display correct colors per status
- Priority badges display correct icons and colors
- SLA countdown shows remaining time with color coding
- Clicking ticket number triggers navigation/handler
- Filter panel collapse/expand works
- 8+ screenshots are captured

## Screenshots to Capture

1. Initial page state with empty or populated ticket list
2. Filtered results by status
3. Multiple filters applied
4. Cleared filters state
5. Pagination controls
6. SLA countdown column
7. Ticket click navigation
8. Filter panel collapsed state
