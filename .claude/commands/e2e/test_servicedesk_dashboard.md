# E2E Test: ServiceDesk Dashboard

Test the ServiceDesk dashboard page with stats cards and tab navigation.

## User Story

As an IT support team member
I want to see a dashboard with ticket statistics and quick navigation
So that I can monitor workload, prioritize urgent issues, and access key ServiceDesk functions efficiently

## Test Steps

1. Navigate to `/servicedesk` (requires authentication)
2. Take a screenshot of the initial loading state
3. **Verify** the page loads with header "Service Desk"
4. **Verify** the subtitle "Panel de control y gestion de tickets de soporte IT" is visible

### Stats Cards Verification
5. **Verify** 4 stats cards are displayed:
   - "Tickets Abiertos" card with ticket icon
   - "Urgente/Alta Prioridad" card with priority icon
   - "Sin Asignar" card with person-off icon
   - "SLA En Riesgo" card with warning icon
6. Take a screenshot of the stats cards grid

### Refresh Functionality
7. **Verify** refresh button is present in the header
8. Click the refresh button
9. **Verify** loading state appears briefly during refresh
10. Take a screenshot after refresh completes

### Tab Navigation
11. **Verify** 3 tabs are visible:
    - "Cola Abierta" tab
    - "Crear Ticket" tab
    - "Base de Conocimiento" tab
12. **Verify** "Cola Abierta" tab is active by default
13. Click "Crear Ticket" tab
14. **Verify** ticket creation form appears
15. Take a screenshot of the Create Ticket tab
16. Click "Base de Conocimiento" tab
17. **Verify** Knowledge Base placeholder or content appears
18. Take a screenshot of the Knowledge Base tab
19. Click "Cola Abierta" tab
20. **Verify** Open Queue placeholder or list appears

### Admin Analytics Tab (Admin Only)
21. If user has admin role:
    - **Verify** "Analiticas" tab is visible
    - Click "Analiticas" tab
    - Take a screenshot of Analytics tab
22. If user does not have admin role:
    - **Verify** "Analiticas" tab is NOT visible

### Responsive Design
23. Set viewport to mobile size (375x667)
24. **Verify** stats cards stack vertically
25. **Verify** tabs are scrollable
26. Take a screenshot of mobile layout

### Error Handling
27. (Optional) Simulate API error by disconnecting network
28. **Verify** error message displays with user-friendly text
29. **Verify** retry functionality works

## Success Criteria
- Dashboard loads with correct header and subtitle
- All 4 stats cards display with correct titles and icons
- Refresh button triggers stats reload
- Tab navigation works correctly between all tabs
- Create Ticket tab shows the FKServicedeskTicketForm component
- Analytics tab only visible to admin users
- Responsive layout works on mobile
- Error handling shows appropriate messages
- At least 6 screenshots are taken
