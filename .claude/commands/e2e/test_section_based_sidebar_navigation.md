# E2E Test: Section-Based Sidebar Navigation

Test that the sidebar renders navigation items organized into collapsible sections (Finance, POCs, Settings) with proper collapse/expand behavior, localStorage persistence, and correct routing.

## User Story

As an authenticated Finance Tracker user
I want to see navigation items organized into collapsible sections in the sidebar
So that I can easily navigate between Finance features and future POC modules (like RestaurantOS) without clutter

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials

## Test Steps

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. Click "Sign In" and log in with valid test credentials
3. Wait for the dashboard to load with the sidebar visible

4. **Verify** the sidebar renders a "Finance" section header above the existing navigation items:
   - Dashboard (with icon)
   - Transactions (with icon)
   - Recurring (with icon)
   - Categories (with icon)
   - Budgets (with icon)
   - Prospects (with icon)
   - Reports (with icon)

5. Take a screenshot showing the Finance section with all nav items

6. **Verify** a "POCs" section header appears below the Finance section items
7. **Verify** the POCs section header has a collapse/expand chevron icon
8. **Verify** "RestaurantOS" appears as a subsection label under POCs

9. Take a screenshot showing the POCs section with RestaurantOS subsection

10. **Verify** Settings appears at the bottom of the sidebar, separated by a divider
11. **Verify** Settings has its gear icon visible

12. Take a screenshot showing Settings at the bottom with divider

13. Click the POCs section header to collapse the section
14. **Verify** the RestaurantOS subsection label is hidden after collapse
15. Take a screenshot showing the collapsed POCs section

16. Click the POCs section header again to expand the section
17. **Verify** the RestaurantOS subsection label reappears
18. Take a screenshot showing the re-expanded POCs section

19. Collapse the POCs section again
20. Refresh the page (reload)
21. **Verify** the POCs section remains collapsed after page refresh (localStorage persistence)
22. Take a screenshot showing POCs still collapsed after refresh

23. Expand the POCs section
24. Refresh the page
25. **Verify** the POCs section remains expanded after page refresh
26. Take a screenshot confirming persistence of expanded state

27. Click the menu toggle button (hamburger icon) to collapse the sidebar to icon-only mode
28. **Verify** section headers ("Finance", "POCs") are hidden in collapsed mode
29. **Verify** navigation icons are still visible
30. **Verify** dividers appear between sections in collapsed mode
31. Take a screenshot showing the collapsed sidebar with icons and dividers

32. Click the menu toggle button to expand the sidebar
33. **Verify** section headers reappear with their items

34. Click on "Dashboard" navigation link
35. **Verify** Dashboard link is highlighted as active
36. **Verify** route is `/dashboard`

37. Click on "Transactions" navigation link
38. **Verify** Transactions link is highlighted as active
39. **Verify** route changes to `/transactions`
40. Take a screenshot showing active Transactions link

41. Click on "Settings" navigation link
42. **Verify** Settings link is highlighted as active
43. **Verify** route changes to `/settings`
44. Take a screenshot showing active Settings in bottom section

45. Navigate to each Finance nav route and verify:
    - `/dashboard` - Dashboard page loads
    - `/categories` - Categories page loads
    - `/budgets` - Budgets page loads
    - `/reports` - Reports page loads
46. Take a screenshot of the final page visited

## Success Criteria

- "Finance" section header appears above all existing Finance navigation items
- All 7 Finance navigation items render with correct icons and labels
- "POCs" section appears below Finance with a collapsible header and chevron icon
- "RestaurantOS" appears as a subsection label under POCs (no nav items beneath it)
- Settings appears at the bottom, separated from other sections by a divider
- Clicking the POCs section header toggles collapse/expand of its content
- Section collapse state persists in localStorage across page refreshes
- Collapsed sidebar (icon-only mode) hides section headers and shows dividers between sections
- Active item highlighting works correctly across all sections
- Existing Finance navigation links route correctly
- No JavaScript errors in the console
- No React warnings in the console

## Technical Verification

- Check browser console for:
  - No JavaScript errors
  - No React warnings
- Check localStorage:
  - `sidebarSectionState` key exists after toggling a section
  - Value persists after page refresh
- Verify the Finance section header is non-collapsible (no chevron icon)
- Verify the POCs section header has a chevron icon and is collapsible

## Notes

- The POCs > RestaurantOS subsection has zero nav items — only the subsection label renders
- The Finance section is non-collapsible by design
- Settings is in an unlabeled bottom section (no section header text)
- The sidebar drawer width remains 240px expanded and 56px collapsed
