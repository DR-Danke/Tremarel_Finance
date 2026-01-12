# E2E Test: ServiceDesk Ticket Form

Test the ServiceDesk ticket creation form functionality including validation, knowledge suggestions, and submission.

## User Story

As an IT support user
I want to create a support ticket with my issue details
So that I can get help from the IT team while also seeing self-service articles that might solve my problem immediately

## Test Steps

1. Navigate to the `Application URL` and login with test credentials
2. Navigate to the ServiceDesk ticket creation page
3. Take a screenshot of the initial form state
4. **Verify** the form loads with pre-filled contact information from authenticated user:
   - Contact Name field should have user's name
   - Contact Email field should have user's email
5. **Verify** form validation works for required fields:
   - Clear the Subject field and try to submit
   - **Verify** error message appears for Subject field
   - Clear the Description field and try to submit
   - **Verify** error message appears for Description field
6. Take a screenshot of validation errors
7. Fill in the form fields:
   - Subject: "Cannot connect to VPN"
   - Description: "I am unable to connect to the company VPN since this morning. I have tried restarting my computer and the VPN client but the issue persists. The error message says 'Connection timeout'."
   - Category: Select "network"
   - Priority: Select "high"
8. **Verify** knowledge suggestions appear after typing in description (debounced)
9. Take a screenshot of knowledge suggestions panel
10. **Verify** "Esto resolvió mi problema" button is visible in suggestions panel
11. Click "Esto resolvió mi problema" button
12. **Verify** form is reset or cancelled with success message
13. Take a screenshot of the success dismissal state
14. Navigate back to ticket creation form
15. Fill in form again with valid data:
    - Subject: "Printer not working"
    - Description: "The office printer on floor 3 is not printing. When I send a print job, it stays in queue and never completes."
    - Category: Select "hardware"
    - Priority: Select "medium"
16. Test file upload:
    - Click or drag a test file to the upload area
    - **Verify** file appears in the selected files list
    - **Verify** file can be removed
17. Take a screenshot of file upload state
18. Submit the form
19. **Verify** loading state appears during submission
20. **Verify** success message appears with ticket number
21. Take a screenshot of success state

## Success Criteria

- Form loads with pre-filled contact info from authenticated user
- Form validation shows error messages for required fields
- Knowledge suggestions appear when user types (after debounce)
- "This solved my problem" button dismisses form creation
- File upload works (select/drag, display, remove)
- Form submission creates ticket and shows ticket number
- Loading states display during API calls
- 7 screenshots are taken

## Test Data

- Test User: Any authenticated user in the system
- Test Files: Small image or PDF file for upload testing
