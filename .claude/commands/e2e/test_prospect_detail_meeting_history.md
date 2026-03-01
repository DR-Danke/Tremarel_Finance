# E2E Test: Prospect Detail Drawer with Meeting History

Test that clicking a prospect card on the CRM Kanban board opens a right-anchored detail drawer showing prospect information, stage transition history, and meeting history sections.

## User Story

As a CRM user managing prospects
I want to click a prospect card and see its full details, stage history, and meeting records in a slide-out drawer
So that I can quickly review a prospect's progression and meeting history without leaving the Kanban board

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
    - Kanban board columns visible

12. If no prospect cards are visible on the board, create one:
    - Click "Add Prospect" button
    - Fill in Company Name: "Detail Test Corp"
    - Fill in Contact Name: "Jane Smith"
    - Fill in Contact Email: "jane@detailtest.com"
    - Fill in Contact Phone: "+1234567890"
    - Fill in Estimated Value: "75000"
    - Fill in Source: "website"
    - Click submit button
    - Take a screenshot after creation
    - **Verify** prospect card appears on the board

13. Click on a prospect card on the Kanban board
14. Take a screenshot of the detail drawer
15. **Verify** the detail drawer opens on the right side:
    - Drawer slides in from the right
    - Drawer contains a close button (X icon)
    - Drawer contains an edit button (Edit icon)

16. **Verify** prospect info section displays:
    - Company name as a heading
    - Current stage displayed as a colored Chip
    - Contact name (if available)
    - Contact email as a mailto link (if available)
    - Contact phone (if available)
    - Estimated value formatted as currency (if available)
    - Source (if available)

17. Take a screenshot of the stage history section
18. **Verify** stage history section is visible:
    - "Stage History" subheader is present
    - Section shows either stage transitions or "No stage transitions yet" empty state

19. Take a screenshot of the meeting history section
20. **Verify** meeting history section is visible:
    - "Meeting History" subheader is present
    - Section shows either meeting records or "No meetings recorded yet" empty state

21. Click the close button (X icon) on the drawer
22. Take a screenshot after closing
23. **Verify** the drawer closes and the Kanban board is fully visible again

24. Click the same prospect card again to reopen the drawer
25. Click the edit button (Edit icon) in the drawer header
26. Take a screenshot of the edit dialog
27. **Verify** the edit dialog opens with the prospect's data pre-filled:
    - Edit Prospect dialog title visible
    - Company name field pre-filled
    - Cancel and submit buttons visible

28. Close the edit dialog (click Cancel or close)
29. Take a final screenshot of the prospects page

## Success Criteria

- Clicking a prospect card opens a right-anchored detail drawer (~520px wide)
- Drawer header shows prospect company name, close button, and edit button
- Prospect info section displays company name, stage chip, contact details, estimated value, source
- Stage history section is visible with "Stage History" heading
- Stage history shows transitions or empty state message
- Meeting history section is visible with "Meeting History" heading
- Meeting history shows meetings or empty state message
- Close button dismisses the drawer
- Edit button opens the existing edit prospect dialog
- Drawer does not interfere with the Kanban board behind it
- Console shows expected INFO log messages:
  - "INFO [TRProspectDetailDrawer]: ..."
  - "INFO [ProspectsPage]: ..."
  - "INFO [PipelineStageService]: ..."

## Technical Verification

- Check browser console for:
  - INFO log messages for drawer operations
  - No JavaScript errors
  - No React warnings
- Check network requests:
  - GET to `/api/pipeline-stages/transitions/{prospect_id}?entity_id={id}` when drawer opens
  - GET to `/api/meeting-records/?entity_id={id}&prospect_id={id}` when drawer opens
  - Authorization header present in all requests

## Notes

- Stage transitions may be empty if prospect has not been moved between stages
- Meeting records may be empty if no meetings have been recorded for the prospect
- The detail drawer and edit dialog are separate UI flows: drawer for viewing, dialog for editing
- HTML download button is only visible for meetings that have html_output
