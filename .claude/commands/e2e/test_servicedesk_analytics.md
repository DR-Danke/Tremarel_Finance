# E2E Test: ServiceDesk Analytics Dashboard

Test the ServiceDesk analytics dashboard with charts, metrics, and export functionality.

## User Story

As an IT support administrator
I want to view comprehensive analytics and visualizations of ServiceDesk metrics
So that I can make data-driven decisions, monitor team performance, track SLA compliance, and identify areas for improvement

## Test Steps

1. Navigate to `/servicedesk` (requires admin authentication)
2. Take a screenshot of the initial dashboard loading state
3. **Verify** the page loads with header "Service Desk"

### Admin Access Verification
4. **Verify** the "Analiticas" tab is visible (admin only)
5. Click the "Analiticas" tab
6. Take a screenshot of the Analytics tab loading state

### Analytics Dashboard Structure
7. **Verify** the analytics dashboard loads with controls section:
   - Date range picker (From/To date fields)
   - "Exportar CSV" button
   - Auto-refresh toggle
8. Take a screenshot of the analytics controls

### KPI Cards Section
9. **Verify** 4 KPI summary cards are displayed:
   - "Total Tickets" card with count
   - "Tiempo Promedio de Resolucion" card with hours
   - "Cumplimiento SLA" card with percentage
   - "Satisfaccion Promedio" card with rating
10. Take a screenshot of the KPI cards grid

### Ticket Trends Chart
11. **Verify** "Tendencia de Tickets" chart section is visible
12. **Verify** the line chart displays:
    - X-axis with date labels
    - Y-axis with ticket count
    - Two lines: "Tickets Creados" and "Tickets Resueltos"
    - Legend showing both series
13. Hover over a data point to verify tooltip appears
14. Take a screenshot of the trends chart with tooltip

### Category Distribution Chart
15. **Verify** "Distribucion por Categoria" chart section is visible
16. **Verify** the pie/donut chart displays:
    - Category segments with colors
    - Legend showing category names
    - Percentage labels
17. Take a screenshot of the category distribution chart

### SLA Compliance Chart
18. **Verify** "Cumplimiento SLA por Prioridad" chart section is visible
19. **Verify** the bar chart displays:
    - X-axis with priority levels (Baja, Media, Alta, Critica)
    - Y-axis with ticket count
    - Stacked bars showing "Dentro de SLA" and "Fuera de SLA"
    - Green and red color coding
20. Take a screenshot of the SLA compliance chart

### Technician Performance Table
21. **Verify** "Desempeno de Tecnicos" section is visible
22. **Verify** the data table displays columns:
    - Nombre del Tecnico
    - Tickets Resueltos
    - Tiempo Promedio
    - Satisfaccion
    - Cumplimiento SLA
23. Click a column header to verify sorting works
24. Take a screenshot of the technician performance table

### Satisfaction Breakdown Chart
25. **Verify** "Desglose de Satisfaccion" chart section is visible
26. **Verify** horizontal bars display:
    - "Satisfaccion General"
    - "Tiempo de Respuesta"
    - "Expertise Tecnico"
    - "Resolucion"
27. **Verify** color coding based on score (green/yellow/red)
28. Take a screenshot of the satisfaction breakdown chart

### Date Range Filtering
29. Change the "Desde" (From) date to 30 days ago
30. Change the "Hasta" (To) date to today
31. **Verify** all charts update with filtered data
32. **Verify** loading state appears during data refresh
33. Take a screenshot of filtered dashboard

### Export Functionality
34. Click the "Exportar CSV" button
35. **Verify** CSV file downloads (or download dialog appears)
36. Take a screenshot showing export action completed

### Auto-Refresh Toggle
37. **Verify** auto-refresh toggle is present
38. Click the auto-refresh toggle to enable
39. **Verify** toggle shows enabled state
40. Wait 5 seconds and **verify** no immediate refresh (interval is 30s)
41. Click toggle again to disable
42. Take a screenshot of auto-refresh toggle states

### Responsive Layout
43. Set viewport to tablet size (768x1024)
44. **Verify** charts reorganize to 2-column layout where appropriate
45. Take a screenshot of tablet layout
46. Set viewport to mobile size (375x667)
47. **Verify** all sections stack vertically
48. **Verify** charts remain visible and readable
49. Take a screenshot of mobile layout

### Error Handling
50. (Optional) Simulate API error by disconnecting network
51. **Verify** error message displays with retry option
52. Take a screenshot of error state

### Empty State Handling
53. (Optional) Filter to date range with no data
54. **Verify** appropriate empty state messages appear in charts
55. Take a screenshot of empty states

## Success Criteria
- Analytics tab only visible to admin users
- All 4 KPI cards display with correct metrics
- Trends chart shows two lines with interactive tooltips
- Category distribution shows pie chart with legend
- SLA compliance shows stacked bar chart by priority
- Technician table is sortable with all columns
- Satisfaction breakdown shows horizontal bars with color coding
- Date range picker filters all charts simultaneously
- Export button triggers CSV download
- Auto-refresh toggle works correctly
- Responsive layout works on tablet and mobile
- Error handling shows appropriate messages
- At least 12 screenshots are taken
