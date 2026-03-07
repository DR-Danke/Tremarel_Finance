# E2E Test: Legal Desk Suggest Specialist

Test that the "Suggest Specialists" button on the Case Detail page returns and displays specialist candidates, and that a candidate can be assigned.

## Prerequisites

- Seed data loaded (`seed_legaldesk_data.sql`) with specialists having "corporate" domain expertise
- At least one client exists in the system
- User is authenticated

## User Story

As a legal operations manager
I want to suggest and assign specialists to a case
So that the best-matched specialists are working on the right cases

## Test Steps

1. Navigate to `/poc/legal-desk/cases/new` (requires authentication)
2. Take a screenshot of the new case form
3. Fill in the case form:
   - Title: "E2E Test Suggest Specialist Case"
   - Select a client from the dropdown
   - Legal Domain: select "corporate"
   - Complexity: select "medium"
   - Priority: select "medium"
4. Click the submit/create button
5. **Verify** redirect to the case detail page (URL matches `/poc/legal-desk/cases/:id`)
6. Take a screenshot of the case detail page
7. Click the "Specialists" tab (second tab)
8. **Verify** the "Assigned Specialists" heading is visible
9. **Verify** the "Suggest Specialists" button is visible
10. Click the "Suggest Specialists" button
11. Wait for the API response (up to 5 seconds)
12. **Verify** the "Suggested Candidates" section appears
13. **Verify** at least one candidate row is displayed in the table
14. **Verify** the candidate table has columns: Name, Match Score, Workload, Expertise, Action
15. **Verify** the first candidate row shows a percentage in the Match Score column (e.g., "85%")
16. **Verify** the first candidate row shows workload in "N/M" format (e.g., "2/5")
17. **Verify** the first candidate row has an "Assign" button
18. Take a screenshot of the suggested candidates table
19. Click the "Assign" button on the first candidate row
20. Wait for the assignment API response (up to 5 seconds)
21. **Verify** the "Assigned Specialists" table now has at least one row
22. Take a screenshot of the final state with the assigned specialist

## Success Criteria
- New case form submits successfully and redirects to detail page
- "Suggest Specialists" button triggers the suggestion API and displays results
- Candidate table renders with correct columns and data format
- "Assign" button successfully creates the assignment
- Assigned specialists table updates after assignment
- 4 screenshots are taken
