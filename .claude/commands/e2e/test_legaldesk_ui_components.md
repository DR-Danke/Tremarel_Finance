# E2E Test: Legal Desk UI Components & Forms

Test that the Legal Desk UI components and forms render correctly and function properly.

## User Story

As a legal desk user
I want reusable UI components and forms for managing cases, specialists, and clients
So that I can efficiently interact with the Legal Desk system through consistent, well-typed interface elements

## Prerequisites

- Backend server running
- Frontend server running
- A test user account exists with valid credentials
- The user is authenticated

## Test Steps

### Setup - Navigate and Authenticate

1. Navigate to the `Application URL`
2. If not logged in, log in with test credentials
3. Navigate to the Legal Desk section of the application
4. Take a screenshot of the Legal Desk landing page

### Test: Badge Components Rendering

5. Navigate to a page or component that renders `TRCaseStatusBadge`
6. **Verify** the badge renders with correct color and label for each status value
7. **Verify** `TRCasePriorityBadge` renders with:
   - Low priority: green (#4CAF50) background
   - Medium priority: yellow (#FFC107) background
   - High priority: orange (#FF9800) background
   - Urgent priority: red (#F44336) background
8. **Verify** `TRLegalDomainBadge` renders with correct labels for all 10 legal domains
9. Take a screenshot of the badge components

### Test: Specialist Score Display

10. Navigate to a specialist detail view or component
11. **Verify** `TRSpecialistScoreDisplay` renders:
    - 5-star rating component
    - Numeric score value next to stars (e.g., "4.5")
    - Stars reflect the score accurately
12. Take a screenshot of the score display

### Test: Pricing Timeline

13. Navigate to a case detail view with pricing history
14. **Verify** `TRPricingTimeline` renders:
    - Chronological order of pricing entries
    - Action type labels (Proposal, Counter, Accept, etc.)
    - Previous and new amounts formatted as currency
    - Date for each entry
15. **Verify** empty state shows "No pricing history" when no entries
16. Take a screenshot of the pricing timeline

### Test: Deliverable Checklist

17. Navigate to a case detail view with deliverables
18. **Verify** `TRDeliverableChecklist` renders:
    - List of deliverables with titles
    - Status chips with correct colors
    - Specialist assignment info or "Unassigned"
    - Due date for each item
19. **Verify** status dropdown appears when onStatusChange is provided
20. **Verify** empty state shows "No deliverables" when list is empty
21. Take a screenshot of the deliverable checklist

### Test: Legal Case Form - Create Mode

22. Navigate to or trigger case creation form
23. **Verify** `TRLegalCaseForm` displays in create mode:
    - Title field (required)
    - Description field (multiline)
    - Client Autocomplete selector (required)
    - Legal Domain dropdown (required)
    - Case Type dropdown
    - Complexity dropdown
    - Priority dropdown
    - Budget field (number)
    - Deadline field (date)
    - Jurisdiction field
    - Cancel and Create Case buttons
24. Test validation - submit with empty required fields
25. **Verify** validation errors for title, client, and legal domain
26. Fill in required fields and submit
27. **Verify** form submits successfully
28. Take a screenshot

### Test: Legal Case Form - Edit Mode

29. Open case form in edit mode with existing data
30. **Verify** form fields are pre-populated with case data
31. Modify a field and submit
32. **Verify** update submits successfully
33. Take a screenshot

### Test: Legal Specialist Form

34. Navigate to or trigger specialist creation form
35. **Verify** `TRLegalSpecialistForm` displays:
    - Name field (required)
    - Specialist Type dropdown
    - Email field
    - Phone field
    - Country field
    - Years of Experience field (number)
    - Hourly Rate field (number)
    - Expertise section with Add/Delete functionality
    - Jurisdictions section with Add/Delete functionality
    - Cancel and Create Specialist buttons
36. Click "Add Expertise" button
37. **Verify** new expertise row appears with domain and proficiency dropdowns
38. Click delete icon on expertise row
39. **Verify** expertise row is removed
40. Click "Add Jurisdiction" button
41. **Verify** new jurisdiction row appears with country, region, and primary checkbox
42. Take a screenshot

### Test: Legal Client Form

43. Navigate to or trigger client creation form
44. **Verify** `TRLegalClientForm` displays:
    - Name field (required)
    - Client Type dropdown (Company/Individual)
    - Email field with validation
    - Phone field
    - Country field
    - Industry field
    - Cancel and Create Client buttons
45. Enter invalid email format
46. Submit form
47. **Verify** email validation error is displayed
48. Enter valid data and submit
49. **Verify** form submits successfully
50. Take a screenshot

## Success Criteria

- All 6 UI components render without errors
- Badge components show correct colors and labels for all status/priority/domain values
- Score display shows stars and numeric value
- Pricing timeline shows chronological entries with formatted amounts
- Deliverable checklist shows items with status badges
- All 3 forms validate required fields
- Forms support both create and edit modes
- Specialist form handles dynamic expertise and jurisdiction rows
- Client form validates email format
- Console shows expected INFO log messages
- No TypeScript or React errors in console

## Technical Verification

- Check browser console for:
  - INFO log messages for component rendering
  - No JavaScript errors
  - No React warnings
- Verify components use correct types from `@/types/legaldesk`

## Notes

- Badge components are presentational and don't make API calls
- Forms use react-hook-form for validation and state management
- The specialist form uses useFieldArray for dynamic sub-sections
- All components follow the TR-prefix naming convention
