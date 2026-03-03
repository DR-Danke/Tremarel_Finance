# E2E Test: Restaurant Selector & Multi-Tenant Navigation

Test that the RestaurantOS restaurant selector and navigation items work correctly, including restaurant switching, localStorage persistence, sidebar navigation, and placeholder page rendering.

## User Story

As a restaurant owner or manager who operates multiple restaurants
I want to select which restaurant I am currently managing and navigate to restaurant-specific pages
So that I can view and manage data scoped to a specific restaurant without mixing up data across locations

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials

## Test Steps

### Login and Initial Navigation

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. Click "Sign In" and log in with valid test credentials
3. Wait for the dashboard to load with the sidebar visible
4. Take a screenshot of the dashboard

### RestaurantOS Sidebar Navigation Items

5. Locate the "POCs" section in the sidebar
6. Click the POCs section header to expand it (if collapsed)
7. **Verify** the "RestaurantOS" subsection label is visible under POCs
8. **Verify** the following navigation items appear under RestaurantOS:
   - Dashboard (with icon)
   - Personas (with icon)
   - Documentos (with icon)
   - Eventos / Tareas (with icon)
   - Recursos / Inventario (with icon)
9. Take a screenshot showing the expanded POCs section with all RestaurantOS nav items

### Navigation Routing

10. Click on the "Dashboard" nav item under RestaurantOS
11. **Verify** the route changes to `/poc/restaurant-os/dashboard`
12. **Verify** the page shows RestaurantOS Dashboard content (either a dashboard view or a "Próximamente" message or a no-restaurant prompt)
13. Take a screenshot of the RestaurantOS Dashboard page

14. Click on the "Personas" nav item
15. **Verify** the route changes to `/poc/restaurant-os/persons`
16. **Verify** the page shows Personas content
17. Take a screenshot of the Personas page

18. Click on the "Documentos" nav item
19. **Verify** the route changes to `/poc/restaurant-os/documents`
20. **Verify** the page shows Documentos content
21. Take a screenshot of the Documentos page

22. Click on the "Eventos / Tareas" nav item
23. **Verify** the route changes to `/poc/restaurant-os/events`
24. **Verify** the page shows Eventos / Tareas content
25. Take a screenshot of the Eventos/Tareas page

26. Click on the "Recursos / Inventario" nav item
27. **Verify** the route changes to `/poc/restaurant-os/resources`
28. **Verify** the page shows Recursos / Inventario content
29. Take a screenshot of the Recursos/Inventario page

### Restaurant Selector Visibility

30. While on a RestaurantOS route (e.g., `/poc/restaurant-os/dashboard`), check the sidebar
31. **Verify** the restaurant selector dropdown appears in the sidebar
32. Take a screenshot showing the restaurant selector in the sidebar

33. Navigate to `/dashboard` (Finance Dashboard)
34. **Verify** the restaurant selector is NOT visible in the sidebar (only shows on RestaurantOS routes)
35. Take a screenshot showing the sidebar without the restaurant selector

### Restaurant Switching (if user has restaurants)

36. Navigate back to `/poc/restaurant-os/dashboard`
37. If the user has restaurants:
    - **Verify** the restaurant selector shows the current restaurant name
    - Open the restaurant selector dropdown
    - Take a screenshot of the dropdown with restaurant options
    - If multiple restaurants exist, select a different restaurant
    - **Verify** the page updates to show the newly selected restaurant's name
    - Refresh the page
    - **Verify** the selected restaurant persists after page refresh (localStorage persistence)
    - Take a screenshot confirming persistence

### No Restaurants State

38. If the user has no restaurants:
    - **Verify** a prompt is displayed encouraging the user to create a restaurant
    - **Verify** a "Crear Restaurante" button is visible
    - Take a screenshot of the no-restaurant prompt

### Restaurant Creation (if no restaurants exist)

39. If the no-restaurant prompt is shown:
    - Click the "Crear Restaurante" button
    - **Verify** a creation dialog/form appears with name and optional address fields
    - Fill in restaurant name: "Mi Restaurante Test"
    - Click the submit/create button
    - **Verify** the restaurant is created and selected as the current restaurant
    - **Verify** the placeholder page now shows the restaurant name
    - Take a screenshot after restaurant creation

## Success Criteria

- POCs > RestaurantOS subsection shows 5 navigation items: Dashboard, Personas, Documentos, Eventos / Tareas, Recursos / Inventario
- Clicking each nav item navigates to the correct `/poc/restaurant-os/<page>` route
- Each placeholder page displays a "Próximamente" (Coming Soon) message with the restaurant name (when a restaurant is selected)
- Restaurant selector dropdown appears in the sidebar only when navigating RestaurantOS routes
- Restaurant selector shows current restaurant name and allows switching between restaurants
- Selected restaurant persists in localStorage across page refreshes
- If user has no restaurants, a prompt to create one is displayed
- If user creates a restaurant from the prompt, it becomes the current restaurant
- UI text is in Spanish: "Restaurante", "Personas", "Documentos", "Eventos / Tareas", "Recursos / Inventario"
- No JavaScript errors in the console
- No React warnings in the console

## Technical Verification

- Check browser console for:
  - INFO [RestaurantContext] log messages for restaurant operations
  - No JavaScript errors
  - No React warnings
- Check localStorage:
  - `currentRestaurantId` key exists after restaurant selection
  - Value persists across page refreshes
- Check network requests:
  - GET `/api/restaurants` on authentication
  - POST `/api/restaurants` on restaurant creation (if tested)
  - Authorization header present in all requests

## Notes

- The backend restaurant API is fully implemented: GET/POST/PUT/DELETE `/api/restaurants`
- Placeholder pages show "Próximamente" messages until Wave 4 implements full CRUD
- The restaurant selector only renders when the current route starts with `/poc/restaurant-os`
- RestaurantContext is at the app root level, so it loads restaurants on authentication regardless of route
- Screenshots should be taken at key steps to document the flow
