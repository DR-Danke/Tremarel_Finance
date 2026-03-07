# E2E Test: Legal Desk Demo User

Test that the Legal Desk demo user can sign in and sees only Legal Desk navigation items, with non-allowed routes redirecting to the Legal Desk dashboard.

## Prerequisites

- Database migration `add_allowed_modules_column.sql` has been run
- Demo user `demo.legaldesk@tremarel.com` exists with password `LegalDesk2026!`
- Application is running (frontend + backend)

## User Story

As a product owner presenting the Legal Desk POC
I want to sign in with a demo account that only shows Legal Desk
So that the presentation is focused without unrelated navigation

## Test Steps

1. Navigate to `/login`
2. Take a screenshot of the login page
3. Enter email: `demo.legaldesk@tremarel.com`
4. Enter password: `LegalDesk2026!`
5. Click the login/submit button
6. Wait for redirect (up to 5 seconds)
7. **Verify** the URL is `/poc/legal-desk/dashboard` (NOT `/dashboard`)
8. Take a screenshot of the Legal Desk dashboard
9. **Verify** the sidebar shows "Legal Desk" section header
10. **Verify** the sidebar shows these items: Dashboard, Cases, Specialists, Clients, Analytics
11. **Verify** the sidebar does NOT show "Finance" section header
12. **Verify** the sidebar does NOT show "RestaurantOS" text
13. **Verify** the sidebar does NOT show "Entity" selector dropdown
14. **Verify** the sidebar shows "Settings" item
15. Click "Cases" in the sidebar
16. **Verify** the URL is `/poc/legal-desk/cases`
17. Take a screenshot of the cases page
18. Navigate directly to `/dashboard` (type in URL bar or use router)
19. Wait for redirect (up to 3 seconds)
20. **Verify** the URL is `/poc/legal-desk/dashboard` (redirected back)
21. Take a screenshot showing the redirect landed on Legal Desk dashboard

## Success Criteria
- Demo user login succeeds and redirects to Legal Desk dashboard
- Sidebar only shows Legal Desk navigation items + Settings
- Finance section and RestaurantOS section are hidden
- Entity selector is hidden
- Navigation between Legal Desk pages works
- Attempting to visit non-allowed routes redirects to Legal Desk dashboard
- 4 screenshots are taken
