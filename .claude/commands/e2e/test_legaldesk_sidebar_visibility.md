# E2E Test: Legal Desk Sidebar Visibility

Test that the Legal Desk POC subsection appears in the sidebar under the POCs section with all 5 navigation items, and that clicking them navigates to the correct Legal Desk pages.

## User Story

As an authenticated Finance Tracker user
I want to see the Legal Desk subsection in the sidebar under POCs
So that I can navigate to all Legal Desk pages (Dashboard, Cases, Specialists, Clients, Analytics)

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials and at least one entity

## Test Steps

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. Click "Sign In" and log in with valid test credentials
3. Wait for the dashboard to load with the sidebar visible

4. **Verify** the "POCs" section header is visible in the sidebar
5. If the POCs section is collapsed, click the POCs header to expand it

6. Take a screenshot showing the POCs section expanded

7. **Verify** "RESTAURANTOS" subsection label is visible under POCs
8. **Verify** "LEGAL DESK" subsection label is visible below the RestaurantOS items

9. Take a screenshot showing both RESTAURANTOS and LEGAL DESK subsection headers

10. **Verify** the following 5 Legal Desk navigation items are visible under the LEGAL DESK subsection:
    - Dashboard (with Gavel icon)
    - Cases (with BusinessCenter icon)
    - Specialists (with PersonSearch icon)
    - Clients (with Groups icon)
    - Analytics (with Analytics icon)

11. Take a screenshot showing all 5 Legal Desk navigation items

12. Scroll down in the sidebar if needed to see all Legal Desk items
13. **Verify** all 5 items are accessible (visible and clickable) even on smaller viewports

14. Click "Dashboard" under the Legal Desk subsection
15. **Verify** the URL changes to `/poc/legal-desk/dashboard`
16. **Verify** the Legal Desk Dashboard page content loads (title or heading visible)
17. **Verify** the "Dashboard" item under Legal Desk shows active/highlighted state

18. Take a screenshot showing the Legal Desk Dashboard page with active sidebar item

19. Click "Cases" under the Legal Desk subsection
20. **Verify** the URL changes to `/poc/legal-desk/cases`
21. **Verify** the Cases page content loads

22. Click "Specialists" under the Legal Desk subsection
23. **Verify** the URL changes to `/poc/legal-desk/specialists`

24. Click "Clients" under the Legal Desk subsection
25. **Verify** the URL changes to `/poc/legal-desk/clients`

26. Click "Analytics" under the Legal Desk subsection
27. **Verify** the URL changes to `/poc/legal-desk/analytics`

28. Take a screenshot showing the Legal Desk Analytics page with active sidebar item

29. Collapse the POCs section by clicking the POCs header
30. **Verify** both RESTAURANTOS and LEGAL DESK subsection labels are hidden
31. Expand the POCs section again
32. **Verify** both RESTAURANTOS and LEGAL DESK subsection labels reappear with their items

33. Take a screenshot showing the final state with POCs expanded

## Success Criteria

- "LEGAL DESK" subsection label appears under the POCs section, below RestaurantOS items
- All 5 Legal Desk navigation items render with correct labels and icons
- Clicking each Legal Desk nav item navigates to the correct route
- Active item highlighting works for Legal Desk items
- Legal Desk items are accessible via scrolling on smaller viewports
- Collapsing/expanding POCs section toggles visibility of both RestaurantOS AND Legal Desk subsections
- No JavaScript errors in the console
- No React warnings in the console

## Technical Verification

- Check browser console for:
  - No JavaScript errors
  - No React warnings
- Verify route paths match expected patterns:
  - `/poc/legal-desk/dashboard`
  - `/poc/legal-desk/cases`
  - `/poc/legal-desk/specialists`
  - `/poc/legal-desk/clients`
  - `/poc/legal-desk/analytics`

## Notes

- The Legal Desk sidebar items were added as part of the Wave 6 merge (issues 151-153)
- The sidebar List component has `overflowY: auto` to ensure all items are scrollable on smaller viewports
- Legal Desk items appear as the second subsection under POCs, after RestaurantOS
