# E2E Test: Prospect Creation Form

Test that the CRM prospect creation form (TRProspectForm) renders correctly, validates input, and successfully submits prospect data to the backend API.

## User Story

As a sales/account manager
I want to create prospects through a form
So that I can track potential deals and manage my CRM pipeline

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials
- At least one entity exists for the test user
- Backend prospect CRUD API endpoints are available at `/api/prospects/`

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

9. Mount the TRProspectForm component in an accessible location (e.g., navigate to a page that renders it, or mount it via a test page/dialog)
10. Take a screenshot of the prospect form
11. **Verify** all form fields are present:
    - "Company Name" text field
    - "Contact Name" text field
    - "Contact Email" email field
    - "Contact Phone" text field
    - "Pipeline Stage" select dropdown
    - "Estimated Value" number field with $ adornment
    - "Source" text field
    - "Notes" multiline text field
    - "Add Prospect" submit button

12. Test required field validation:
    - Click "Add Prospect" without filling any fields
13. Take a screenshot of validation errors
14. **Verify** validation error appears:
    - "Company name is required" error message on Company Name field

15. Test email validation:
    - Enter "invalid-email" in the Contact Email field
    - Enter "Test Company" in Company Name field
    - Click "Add Prospect"
16. Take a screenshot of email validation error
17. **Verify** email validation error appears:
    - "Invalid email format" error message on Contact Email field

18. Clear the form and fill all fields with valid data:
    - Company Name: "Acme Corp"
    - Contact Name: "John Doe"
    - Contact Email: "john@acme.com"
    - Contact Phone: "555-0100"
    - Pipeline Stage: select "Qualified" from dropdown
    - Estimated Value: "50000"
    - Source: "Website"
    - Notes: "Hot lead from website"
19. Take a screenshot of completed form
20. **Verify** all fields are filled correctly

21. Click "Add Prospect" to submit the form
22. Take a screenshot after submission
23. **Verify** form submission:
    - POST request sent to `/api/prospects/` with correct payload:
      - `entity_id` matches current entity
      - `company_name`: "Acme Corp"
      - `contact_name`: "John Doe"
      - `contact_email`: "john@acme.com"
      - `contact_phone`: "555-0100"
      - `stage`: "qualified"
      - `estimated_value`: 50000
      - `source`: "Website"
      - `notes`: "Hot lead from website"
    - Form resets after successful creation (all fields cleared, stage back to "Lead")

24. Test Pipeline Stage dropdown:
    - Click on the Pipeline Stage select
25. Take a screenshot of stage options
26. **Verify** all 7 stages are present:
    - Lead, Contacted, Qualified, Proposal, Negotiation, Won, Lost

27. Test minimal submission (only required fields):
    - Enter Company Name: "Minimal Corp"
    - Leave all other fields empty/default
    - Click "Add Prospect"
28. Take a screenshot
29. **Verify** submission succeeds with only company_name and default stage "lead"

30. Test Cancel button:
    - If Cancel button is visible (depends on onCancel prop being provided):
      - Click Cancel
      - **Verify** cancel action is triggered

## Success Criteria

- Prospect form renders all 8 fields (Company Name, Contact Name, Contact Email, Contact Phone, Pipeline Stage, Estimated Value, Source, Notes)
- Company Name field validation: required, max 255 chars
- Contact Email field validation: email format when provided
- Pipeline Stage shows all 7 stages in dropdown, defaults to "Lead"
- Estimated Value field has $ adornment and accepts numeric input
- Notes field is multiline (3 rows)
- Form submits valid data via POST to `/api/prospects/`
- Form resets after successful creation
- Submit button shows "Add Prospect" in create mode
- Loading state disables fields and shows CircularProgress on submit button
- Console shows expected log messages

## Technical Verification

- Check browser console for:
  - `INFO [TRProspectForm]: Form submitted` on form submission
  - `INFO [TRProspectForm]: Prospect submitted successfully` on success
  - `INFO [ProspectService]: Creating prospect for entity:` on API call
  - `INFO [ProspectService]: Prospect created:` on API response
  - No JavaScript errors
  - No React warnings
- Check network requests:
  - POST to `/api/prospects/` with correct JSON payload
  - Authorization header present in request
  - Response status 201 Created

## Notes

- The TRProspectForm is a standalone component — it may not have a dedicated route. It is designed to be mounted inside a Dialog by CRM-008 (Kanban Board Page). For E2E testing, mount it in any accessible context.
- The form handles both create and edit modes. Edit mode is tested by passing `initialData` prop with an existing Prospect object.
- The `is_active` field is not part of the form — it is managed programmatically.
- Empty optional string fields should be sent as `undefined` (not empty strings) to the API.
- The `estimated_value` field converts from string (form input) to number (API payload).
