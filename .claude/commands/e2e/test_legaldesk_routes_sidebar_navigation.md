# E2E Test: Legal Desk Routes & Sidebar Navigation

Test that all 7 Legal Desk routes are registered, load correctly, and that 5 sidebar navigation items appear under a "Legal Desk" subsection within the POCs collapsible section.

## User Story

As an authenticated Finance Tracker user
I want to navigate to Legal Desk pages via the sidebar
So that I can access the case management, specialist assignment, client management, and analytics features of the Legal Desk POC

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials

## Test Steps

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. Click "Sign In" and log in with valid test credentials
3. Wait for the dashboard to load with the sidebar visible

4. Expand the POCs section in the sidebar by clicking the "POCs" header
5. **Verify** "Legal Desk" subsection label appears under POCs (alongside "RestaurantOS")
6. **Verify** 5 navigation items appear under the Legal Desk subsection:
   - Dashboard (GavelIcon)
   - Cases (BusinessCenterIcon)
   - Specialists (PersonSearchIcon)
   - Clients (GroupsIcon)
   - Analytics (AnalyticsIcon)

7. Take a screenshot showing the POCs section with both RestaurantOS and Legal Desk subsections

8. Click the "Dashboard" item under Legal Desk
9. **Verify** the route changes to `/poc/legal-desk/dashboard`
10. **Verify** the page renders with "Legal Desk Dashboard" heading and no errors
11. **Verify** the Dashboard nav item is highlighted as active

12. Take a screenshot of the Legal Desk Dashboard page

13. Click the "Cases" item under Legal Desk
14. **Verify** the route changes to `/poc/legal-desk/cases`
15. **Verify** the page renders with "Cases" heading and no errors

16. Click the "Specialists" item under Legal Desk
17. **Verify** the route changes to `/poc/legal-desk/specialists`
18. **Verify** the page renders with "Specialists" heading and no errors

19. Click the "Clients" item under Legal Desk
20. **Verify** the route changes to `/poc/legal-desk/clients`
21. **Verify** the page renders with "Clients" heading and no errors

22. Click the "Analytics" item under Legal Desk
23. **Verify** the route changes to `/poc/legal-desk/analytics`
24. **Verify** the page renders with "Analytics" heading and no errors

25. Take a screenshot of the Legal Desk Analytics page

26. Navigate directly to `/poc/legal-desk`
27. **Verify** the browser redirects to `/poc/legal-desk/dashboard`
28. **Verify** the Dashboard page renders

29. Navigate directly to `/poc/legal-desk/cases/new`
30. **Verify** the page renders with "New Case" heading

31. Navigate directly to `/poc/legal-desk/cases/1`
32. **Verify** the page renders (may show loading or error state for non-existent case, but no crash)

33. Take a screenshot of the case detail page

34. Navigate back to `/poc/legal-desk/dashboard`
35. **Verify** the Dashboard nav item is highlighted as active
36. Click each Legal Desk nav item in turn and verify active state highlighting works on each

37. Click the menu toggle button (hamburger icon) to collapse the sidebar to icon-only mode
38. **Verify** Legal Desk icons (Gavel, BusinessCenter, PersonSearch, Groups, Analytics) are still visible
39. **Verify** clicking a Legal Desk icon navigates to the correct route

40. Take a screenshot showing collapsed sidebar with Legal Desk icons visible

41. Click the menu toggle button to expand the sidebar again
42. **Verify** Legal Desk subsection label and nav items reappear

## Success Criteria

- All 7 Legal Desk routes load their respective pages without errors
- `/poc/legal-desk` redirects to `/poc/legal-desk/dashboard`
- `/poc/legal-desk/cases/new` renders the New Case page
- `/poc/legal-desk/cases/:id` renders the Case Detail page
- 5 sidebar navigation items appear under a "Legal Desk" subsection within POCs
- Each sidebar item has the correct icon: Dashboard (Gavel), Cases (BusinessCenter), Specialists (PersonSearch), Clients (Groups), Analytics (Analytics)
- Active state highlighting works on Legal Desk nav items
- Collapsed sidebar (icon-only mode) shows Legal Desk icons and they are clickable
- No JavaScript errors in the console
- No React warnings in the console

## Technical Verification

- Check browser console for:
  - `INFO [App]: Route changed to /poc/legal-desk/dashboard` when navigating
  - No JavaScript errors
  - No React warnings
- Check localStorage:
  - `sidebarSectionState` key persists POCs section state
- Verify all routes are wrapped in ProtectedRoute (unauthenticated users should be redirected to login)

## Notes

- The Legal Desk pages are placeholder/minimal implementations wired to data hooks
- Pages with hooks (Dashboard, Cases, CaseDetail, Specialists, Clients) will show loading/error/data states
- Pages without hooks (NewCase, Analytics) show static placeholder content
- The redirect from `/poc/legal-desk` to `/poc/legal-desk/dashboard` uses `<Navigate replace />`
- Route ordering places `/poc/legal-desk/cases/new` before `/poc/legal-desk/cases/:id` so the static path matches first
