# E2E Test: Prospect Kanban Board

Test that the Finance Tracker prospect Kanban board works correctly, including viewing pipeline stages as columns, creating prospects via the form dialog, and verifying prospect cards appear in the correct stage column.

## User Story

As a CRM user managing prospects
I want to view and manage prospects on a Kanban board
So that I can visually track the progression of deals through my sales pipeline

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials
- At least one entity exists for the test user

## Test Steps

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. Take a screenshot of the home page
3. **Verify** the home page loads with:
   - "Finance Tracker" heading
   - "Sign In" button is visible

4. Click the "Sign In" button to navigate to login page
5. Enter valid test credentials:
   - Email: test@example.com (or a valid test user email)
   - Password: testpassword123 (or valid test password)
6. Click "Sign In" button
7. Take a screenshot after login
8. **Verify** login successful (redirected to dashboard or home)

9. Navigate to `/prospects`
10. Take a screenshot of the prospects page
11. **Verify** prospects page loads with:
    - "Prospects" page title visible
    - "Add Prospect" button visible

12. **Verify** Kanban board renders with pipeline stage columns:
    - At least these columns visible: Lead, Contacted, Qualified, Proposal, Negotiation, Won, Lost
    - Each column shows a stage name header and prospect count badge

13. Click the "Add Prospect" button
14. Take a screenshot of the add prospect form dialog
15. **Verify** form dialog displays with fields:
    - Company Name (text input)
    - Contact Name (text input)
    - Contact Email (email input)
    - Contact Phone (text input)
    - Stage (select dropdown)
    - Estimated Value (number input)
    - Source (text input)
    - Notes (multiline text input)
    - Submit button ("Add Prospect")
    - Cancel button

16. Fill in the prospect form:
    - Company Name: "Test Corp"
    - Contact Name: "John Doe"
    - Contact Email: "john@test.com"
    - Stage: "lead" (should be default)
    - Estimated Value: "50000"
    - Source: "referral"
17. Click "Add Prospect" submit button
18. Take a screenshot after creation
19. **Verify** prospect created successfully:
    - Dialog closes
    - Prospect card "Test Corp" appears in the "Lead" column
    - Card shows "John Doe" contact name

20. Navigate away to `/dashboard`
21. Navigate back to `/prospects`
22. Take a screenshot after navigation
23. **Verify** "Test Corp" prospect still exists in the Kanban board

## Success Criteria

- Prospects page accessible at `/prospects` route
- Sidebar shows "Prospects" navigation item
- Kanban board loads with columns for all pipeline stages (auto-seeded if needed)
- Each column header shows stage display_name, color indicator, and prospect count
- "Add Prospect" button opens form dialog
- Prospect form contains all required fields
- Creating a prospect via the form adds the card to the correct column
- Prospect card displays company_name, contact_name, estimated_value (formatted), and source
- Data persists after navigation
- Console shows expected INFO log messages:
  - "INFO [ProspectsPage]: ..."
  - "INFO [ProspectService]: ..."
  - "INFO [PipelineStageService]: ..."

## Technical Verification

- Check browser console for:
  - INFO log messages for prospect and pipeline stage operations
  - No JavaScript errors
  - No React warnings
- Check network requests:
  - GET to `/api/pipeline-stages/?entity_id={id}` on page load
  - POST to `/api/pipeline-stages/seed` if no stages exist (auto-seed)
  - GET to `/api/prospects/?entity_id={id}` on page load
  - POST to `/api/prospects/` on create
  - Authorization header present in all requests

## Notes

- If backend is not running, API calls will fail with network error
- Test user must have access to at least one entity
- Pipeline stages are auto-seeded if none exist for the entity
- All data is scoped to the current entity via EntityContext
- No drag-and-drop functionality in this wave (CRM-009 will add it)
- Clicking a prospect card opens the edit dialog
