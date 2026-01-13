# E2E Test: Main Layout with Collapsible Sidebar

Test that the Finance Tracker main layout with collapsible sidebar works correctly, including navigation, entity switching, and responsive behavior.

## User Story

As an authenticated Finance Tracker user
I want to have a consistent navigation layout with a collapsible sidebar
So that I can easily navigate between different sections of the application and switch between my Family and Startup financial entities

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials

## Test Steps

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. Click "Sign In" and log in with valid test credentials
3. Take a screenshot of the dashboard with layout
4. **Verify** the main layout renders with:
   - Top navbar with "Finance Tracker" title
   - Menu toggle button (hamburger icon) in the navbar
   - User info or logout button in the navbar
   - Collapsible sidebar on the left
   - Main content area showing the dashboard

5. **Verify** the sidebar displays navigation links:
   - Dashboard (with icon)
   - Transactions (with icon)
   - Categories (with icon)
   - Budgets (with icon)
   - Reports (with icon)
   - Settings (with icon)

6. **Verify** the Dashboard link is highlighted as active

7. Take a screenshot showing the expanded sidebar

8. **Verify** the Entity Switcher section:
   - Entity switcher dropdown is visible
   - Shows current entity name (e.g., "Family" or "Startup")
   - Click dropdown to see available entities

9. Switch entity from Family to Startup (or vice versa)
10. Take a screenshot
11. **Verify** entity selection changed
12. **Verify** entity selection persists (refresh page and verify selection)

13. Click the menu toggle button (hamburger icon) to collapse sidebar
14. Take a screenshot
15. **Verify** sidebar collapses to show only icons
16. **Verify** navigation icons are still visible and clickable

17. Click the menu toggle button again to expand sidebar
18. Take a screenshot
19. **Verify** sidebar expands to show full navigation with labels

20. Click on "Transactions" navigation link
21. Take a screenshot
22. **Verify** route changes to `/transactions`
23. **Verify** Transactions link is now highlighted as active
24. **Verify** layout persists (sidebar, navbar, content area)

25. Navigate to each placeholder route and verify:
    - `/categories` - Categories page loads
    - `/budgets` - Budgets page loads
    - `/reports` - Reports page loads
    - `/settings` - Settings page loads
26. Take screenshots of each page

27. Click the Logout button in the navbar
28. Take a screenshot
29. **Verify** redirect to login page
30. **Verify** user is logged out

31. Navigate directly to `/dashboard` (without logging in)
32. Take a screenshot
33. **Verify** redirect to login page (protected route working)

## Success Criteria

- Main layout renders on all authenticated pages
- Sidebar shows all 6 navigation links with icons
- Sidebar toggle button collapses/expands the sidebar
- Collapsed sidebar shows only icons
- Entity switcher displays and allows switching entities
- Selected entity persists in localStorage across refreshes
- Navigation links route to correct pages
- Active navigation link is visually highlighted
- Top navbar shows application title
- Logout button works correctly
- Protected routes redirect unauthenticated users to login
- Console shows expected INFO log messages:
  - "INFO [EntityContext]: Entity selected: ..."
  - "INFO [EntityContext]: Switching to entity: ..."
  - "INFO [TRMainLayout]: Sidebar toggled"

## Technical Verification

- Check browser console for:
  - INFO log messages for entity and layout state changes
  - No JavaScript errors
  - No React warnings
- Check localStorage:
  - `selectedEntityId` stored after entity selection
  - Entity selection persists across page refreshes
- Check responsive behavior:
  - Resize browser window to verify sidebar auto-collapses on small screens

## Notes

- The entity switcher uses mock data (Family and Startup) since backend entity endpoints don't exist yet
- Navigation routes for Transactions, Categories, Budgets, Reports, and Settings show placeholder pages
- The sidebar drawer width is 240px when expanded and 56px when collapsed
