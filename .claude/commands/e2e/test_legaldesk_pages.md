# E2E Test: Legal Desk Pages

Test all 7 Legal Desk pages: Dashboard, Cases, New Case, Case Detail, Specialists, Clients, Analytics.

## User Story

As a legal operations manager
I want to access dashboard, cases, specialists, clients, and analytics pages
So that I can manage legal cases end-to-end

## Test Steps

### Dashboard Page
1. Navigate to `/poc/legal-desk/dashboard` (requires authentication)
2. Take a screenshot of the initial loading state
3. **Verify** the page loads with header "Legal Desk Dashboard"
4. **Verify** 4 stats cards are displayed: Active Cases, Total Cases, Specialists Active, Total Clients
5. **Verify** a pie chart for "Cases by Status" is rendered
6. **Verify** a bar chart for "Cases by Domain" is rendered
7. Take a screenshot of the dashboard

### Cases List Page
8. Navigate to `/poc/legal-desk/cases`
9. **Verify** the page loads with header "Legal Desk Cases"
10. **Verify** 4 filter selects are visible: Status, Domain, Priority, Type
11. **Verify** a "New Case" button is present
12. **Verify** the cases table has columns: Case #, Title, Client, Domain, Status, Priority
13. Take a screenshot of the cases list

### New Case Page
14. Click the "New Case" button or navigate to `/poc/legal-desk/cases/new`
15. **Verify** the page loads with header "New Case"
16. **Verify** the form has fields: Title, Client, Legal Domain, Description, Complexity, Priority, Budget, Estimated Cost, Deadline
17. **Verify** Title, Client, and Legal Domain are required fields
18. **Verify** a "Back to Cases" button is present
19. Take a screenshot of the new case form

### Case Detail Page
20. Navigate to `/poc/legal-desk/cases/1` (or first available case)
21. **Verify** the page loads with case number and title in header
22. **Verify** status, domain, and priority badges are displayed
23. **Verify** status transition buttons are visible
24. **Verify** 6 tabs are present: Overview, Specialists, Deliverables, Pricing, Messages, Documents
25. Click each tab and verify content switches:
    - Overview: case info grid with description, type, complexity, budget
    - Specialists: table of assigned specialists with "Suggest Specialists" button
    - Deliverables: checklist with add form
    - Pricing: timeline with action buttons
    - Messages: message list with add form
    - Documents: document table with add form
26. Take a screenshot of the case detail page with Overview tab
27. Take a screenshot after switching to Specialists tab

### Specialists Page
28. Navigate to `/poc/legal-desk/specialists`
29. **Verify** the page loads with header "Legal Desk Specialists"
30. **Verify** specialist cards show: name, email, experience, rate, score, workload
31. **Verify** an "Add Specialist" button is present
32. Click "Add Specialist" and verify dialog with form appears
33. Take a screenshot of the specialists page

### Clients Page
34. Navigate to `/poc/legal-desk/clients`
35. **Verify** the page loads with header "Legal Desk Clients"
36. **Verify** the clients table has columns: Name, Type, Email, Country, Industry
37. **Verify** an "Add Client" button is present
38. Click "Add Client" and verify dialog with form appears
39. Take a screenshot of the clients page

### Analytics Page
40. Navigate to `/poc/legal-desk/analytics`
41. **Verify** the page loads with header "Legal Desk Analytics"
42. **Verify** summary stat cards are displayed
43. **Verify** charts are rendered (Cases by Domain bar chart)
44. Take a screenshot of the analytics page

## Success Criteria
- All 7 pages load without errors
- Dashboard shows 4 stat cards and 2 charts
- Cases list has 4 filter controls and navigable table
- New Case form has required fields and validation
- Case Detail has 6 functional tabs
- Specialists shows card grid with score display
- Clients shows table with Add Client dialog
- Analytics shows charts
- All pages handle loading and error states
- At least 8 screenshots are taken
