# E2E Test: ServiceDesk Ticket Creation

Test the ServiceDesk ticket creation flow to validate that tickets are created successfully with auto-generated ticket numbers in the format `TKT-YYYY-NNNNN`.

## User Story

As an IT support user
I want to create a support ticket and receive a confirmation with a ticket number
So that I can track my issue and reference it in future communications

## Test Steps

1. Navigate to the `Application URL` and login with test credentials
2. Navigate to the ServiceDesk dashboard at `/servicedesk`
3. Take a screenshot of the ServiceDesk dashboard
4. Click on the "Nuevo Ticket" (New Ticket) tab to open the ticket creation form
5. Take a screenshot of the ticket creation form
6. Fill in the form fields:
   - Subject/Title: "Test ticket for E2E validation"
   - Description: "This is an automated E2E test to validate ticket creation with auto-generated ticket numbers."
   - Category: Select "other"
   - Priority: Select "medium"
7. Take a screenshot of the filled form before submission
8. Submit the form by clicking the submit button
9. **Verify** that a success message appears indicating the ticket was created
10. **Verify** that the success message includes a ticket number in the format `TKT-YYYY-NNNNN` (e.g., TKT-2026-00001)
11. Take a screenshot of the success message with the ticket number
12. Navigate to the ticket list tab or refresh the page to see the ticket list
13. **Verify** that the newly created ticket appears in the ticket list
14. **Verify** that the ticket in the list shows the same ticket number from the success message
15. Take a screenshot of the ticket list showing the new ticket

## Success Criteria

- Ticket creation form loads correctly
- Form can be filled with valid data
- Form submission succeeds without errors (no null constraint violations)
- Success message displays a ticket number in format `TKT-YYYY-NNNNN`
- New ticket appears in the ticket list with the correct ticket number
- 5 screenshots are taken

## Test Data

- Test User: Any authenticated user in the system
- Subject: "Test ticket for E2E validation"
- Description: "This is an automated E2E test to validate ticket creation with auto-generated ticket numbers."
- Category: "other"
- Priority: "medium"

## Expected Ticket Number Format

The ticket number should match the regex pattern: `^TKT-\d{4}-\d{5}$`

Examples of valid ticket numbers:
- TKT-2026-00001
- TKT-2026-00015
- TKT-2025-99999
