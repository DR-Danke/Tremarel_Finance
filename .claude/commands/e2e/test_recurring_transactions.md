# E2E Test: Recurring Transactions

Test that the Finance Tracker recurring transactions management works correctly, including creating, viewing, editing, and deactivating recurring templates, and verifying recurring indicators on transactions.

## User Story

As a Finance Tracker user
I want to create recurring transaction templates with patterns (daily, weekly, monthly, yearly)
So that I can easily track regular income like salary or regular expenses like subscriptions

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials
- The user is authenticated
- At least one category exists for both income and expense types

## Test Steps

### Setup - Navigate and Authenticate

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. If not logged in, log in with test credentials:
   - Email: test@example.com (or a valid test user email)
   - Password: testpassword123 (or valid test password)
3. Navigate to `/recurring` page using sidebar navigation
4. Take a screenshot of the recurring templates page
5. **Verify** page loads with:
   - "Recurring Transactions" heading
   - "Add Recurring Template" button is visible
   - Recurring templates table or empty state message

### Test: Empty State

6. **Verify** if no recurring templates exist:
   - Empty state message "No Recurring Templates Found" is displayed
   - Message suggests creating first recurring template
7. Take a screenshot of empty state

### Test: Create Recurring Template

8. Click "Add Recurring Template" button
9. Take a screenshot of the recurring template form dialog
10. **Verify** form displays:
    - Name input field
    - Type dropdown (Income/Expense)
    - Amount input field with $ prefix
    - Category dropdown
    - Frequency dropdown (Daily/Weekly/Monthly/Yearly)
    - Start Date input
    - End Date input (optional)
    - Description text field
    - Notes textarea
    - Cancel and Add Template buttons

11. Test form validation - submit with empty required fields
12. Take a screenshot
13. **Verify** validation errors displayed:
    - "Name is required" error
    - "Amount is required" error
    - "Category is required" error
    - "Frequency is required" error
    - "Start date is required" error

14. Fill in recurring template form:
    - Name: "Netflix Subscription"
    - Type: Expense
    - Amount: 15.99
    - Category: First available expense category
    - Frequency: Monthly
    - Start Date: First of current month
    - Description: "Monthly streaming subscription"
    - Notes: "E2E test recurring template"

15. Click "Add Template" button
16. Take a screenshot
17. **Verify** dialog closes
18. **Verify** new template appears in table with:
    - Name: "Netflix Subscription"
    - Type: "Expense" chip (red)
    - Amount: $15.99
    - Frequency: "Monthly"
    - Start Date displayed
    - Status: "Active" chip (green)
    - Edit and Deactivate/Delete buttons visible

19. Take a screenshot of the template in the table

### Test: Create Second Template (Income)

20. Click "Add Recurring Template" button
21. Fill in recurring template form:
    - Name: "Monthly Salary"
    - Type: Income
    - Amount: 5000.00
    - Category: First available income category
    - Frequency: Monthly
    - Start Date: First of current month
    - Description: "Regular monthly salary"

22. Click "Add Template" button
23. Take a screenshot
24. **Verify** new template appears:
    - "Income" chip (green)
    - Amount: $5,000.00

### Test: Edit Recurring Template

25. Click Edit button (pencil icon) on "Netflix Subscription" template
26. Take a screenshot of edit dialog
27. **Verify** form is prefilled with template data

28. Change amount from 15.99 to 19.99
29. Change name to "Netflix Premium"
30. Click "Update Template" button
31. Take a screenshot
32. **Verify** dialog closes
33. **Verify** table shows updated values:
    - Name: "Netflix Premium"
    - Amount: $19.99

### Test: Deactivate Recurring Template

34. Click Deactivate button on "Netflix Premium" template
35. Take a screenshot of deactivation confirmation dialog
36. **Verify** confirmation shows template name and details
37. Click "Deactivate" button
38. Take a screenshot
39. **Verify** template status changes to "Inactive" chip (gray)
40. **Verify** template remains in list but marked as inactive

### Test: Delete Recurring Template (Admin/Manager only)

41. **Note:** Hard delete requires admin or manager role
42. If user has admin/manager role:
    - Click Delete button (trash icon) on the inactive "Netflix Premium" template
    - Take a screenshot of delete confirmation dialog
    - **Verify** confirmation warns this is permanent
    - Click "Delete" button
    - Take a screenshot
    - **Verify** template removed from table

43. If user has regular user/viewer role:
    - **Verify** Delete button is not visible (only Deactivate available)
    - Take a screenshot showing only deactivate option

### Test: Verify Recurring Indicator on Transactions Page

44. Navigate to `/transactions` page
45. **Note:** If transactions were created and linked to recurring templates, verify the indicator
46. **Verify** any transaction with `recurring_template_id` shows:
    - Recurring indicator icon (e.g., repeat icon)
    - Tooltip showing template name on hover (if applicable)
47. Take a screenshot of transaction with recurring indicator

### Test: Create Template with End Date

48. Navigate back to `/recurring` page
49. Click "Add Recurring Template" button
50. Fill in template with end date:
    - Name: "Gym Membership"
    - Type: Expense
    - Amount: 50.00
    - Category: First available expense category
    - Frequency: Monthly
    - Start Date: First of current month
    - End Date: 6 months from now
    - Description: "6-month gym membership"

51. Click "Add Template" button
52. Take a screenshot
53. **Verify** template shows end date in table

## Success Criteria

- Recurring Templates page loads without errors
- Sidebar shows "Recurring" navigation link
- Add Recurring Template form displays all required fields
- Form validation works correctly for:
  - Empty required fields
  - Invalid amount format
  - End date before start date (if validated)
- Template creation adds new row to table
- Table displays templates with:
  - Template name
  - Type chip with correct color (green for income, red for expense)
  - Formatted currency amount
  - Frequency label
  - Start/End dates
  - Status indicator (Active/Inactive)
- Edit form prefills with current values
- Update saves changes and reflects in table
- Deactivate changes status without removing template
- Delete removes template (admin/manager only)
- Transactions page shows recurring indicator for linked transactions
- Console shows expected INFO log messages:
  - "INFO [RecurringTemplatesPage]: Opening add template dialog"
  - "INFO [RecurringTemplateService]: Creating recurring template..."
  - "INFO [useRecurringTemplates]: Template created, refreshing list"

## Technical Verification

- Check browser console for:
  - INFO log messages for recurring template operations
  - No JavaScript errors
  - No React warnings
- Check network requests:
  - POST to `/api/recurring-templates/` on create
  - GET to `/api/recurring-templates/?entity_id=...` on list
  - PUT to `/api/recurring-templates/{id}` on update
  - DELETE to `/api/recurring-templates/{id}` on delete
  - Authorization header present in all requests

## Notes

- If the backend is not running, operations will fail with network errors
- Category selection depends on categories existing in the database
- Hard delete operation requires admin or manager role
- Template amounts are always positive; type determines income/expense
- The entity_id may be a placeholder until EntityContext is implemented
- Deactivation is preferred over deletion to maintain transaction history integrity
- This feature does NOT implement automatic transaction generation - templates are for manual reference and future automation
