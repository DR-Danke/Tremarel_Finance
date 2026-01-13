# E2E Test: Budget Management CRUD

Test that the Finance Tracker budget management works correctly, including creating, viewing, editing, and deleting budgets with visual progress indicators showing spending vs. budget amounts.

## User Story

As a Finance Tracker user
I want to set spending limits per category and track my progress against them
So that I can manage my finances and stay within my spending goals

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials
- At least one entity exists for the test user
- At least one expense category exists for the entity
- Some expense transactions exist to show spending progress

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

9. Navigate to `/budgets` page
10. Take a screenshot of the budgets page
11. **Verify** budgets page loads with:
    - Page title "Budgets" visible
    - "Add Budget" button visible
    - Budget list section visible (may be empty)

12. Click the "Add Budget" button
13. Take a screenshot of the budget form
14. **Verify** budget form displays with:
    - Category select dropdown (expense categories only)
    - Amount input field
    - Period type select (Monthly, Quarterly, Yearly)
    - Start date input
    - Submit button
    - Cancel button

15. Create a monthly budget:
    - Select category: (first available expense category)
    - Enter amount: "500"
    - Select period type: "Monthly"
    - Select start date: first day of current month
    - Click Submit
16. Take a screenshot
17. **Verify** budget created:
    - Success message displayed OR dialog closes
    - New budget card appears in the list
    - Budget shows category name
    - Budget shows "$500.00" amount
    - Budget shows "Monthly" period
    - Progress bar is visible

18. **Verify** progress bar color:
    - If spending < 75% of budget: green color
    - If spending >= 75% and <= 100%: yellow/amber color
    - If spending > 100%: red color

19. Create a yearly budget:
    - Click "Add Budget" button
    - Select a different expense category
    - Enter amount: "2000"
    - Select period type: "Yearly"
    - Select start date: January 1st of current year
    - Click Submit
20. Take a screenshot
21. **Verify** second budget created:
    - New budget card appears in list
    - Shows "$2,000.00" amount
    - Shows "Yearly" period

22. View budget details:
    - Locate the first budget card
    - **Verify** card displays:
      - Category name
      - Budget amount
      - Period type
      - Spent amount (e.g., "$150.00 / $500.00")
      - Percentage spent (e.g., "30%")
      - Progress bar with appropriate fill level

23. Edit a budget:
    - Click the edit button (pencil icon) on the first budget
24. Take a screenshot of edit form
25. **Verify** edit form displays with:
    - Current amount "500" pre-filled
    - Current period type "Monthly" selected
    - Current start date pre-filled

26. Update the budget amount:
    - Change amount from "500" to "600"
    - Click Submit
27. Take a screenshot
28. **Verify** budget updated:
    - Success message displayed OR dialog closes
    - Budget card shows "$600.00" amount
    - Progress bar percentage recalculated

29. Delete a budget (admin/manager only):
    - Click the delete button (trash icon) on the yearly budget
    - Confirm deletion in dialog
30. Take a screenshot
31. **Verify** budget deleted:
    - Success message displayed
    - Yearly budget no longer appears in list
    - Monthly budget still exists

32. Test over-budget warning:
    - If any budget shows spending > 100%:
      - **Verify** progress bar is red
      - **Verify** warning indicator or text is shown

33. Navigate away and back to verify persistence:
    - Navigate to `/dashboard`
    - Navigate back to `/budgets`
34. Take a screenshot
35. **Verify** budgets persisted:
    - Previously created budget still visible
    - Spending amounts still accurate

## Success Criteria

- Budgets page loads without errors
- Budget form displays all required fields
- Can create budget with Monthly period
- Can create budget with Yearly period
- Budget cards display correct information:
  - Category name
  - Budget amount (formatted as currency)
  - Period type
  - Spent amount vs budget amount
  - Percentage spent
  - Progress bar
- Progress bar colors correctly indicate status:
  - Green: < 75% spent
  - Yellow/Amber: 75-100% spent
  - Red: > 100% spent (over budget)
- Can edit budget amount
- Can delete budget (admin/manager roles)
- Budgets persist after navigation
- All CRUD operations show appropriate success/error messages
- Console shows expected INFO log messages:
  - "INFO [BudgetService]: Creating budget..."
  - "INFO [BudgetService]: Updating budget..."
  - "INFO [BudgetService]: Deleting budget..."

## Technical Verification

- Check browser console for:
  - INFO log messages for budget operations
  - No JavaScript errors
  - No React warnings
- Check network requests:
  - POST to `/api/budgets/` on create
  - GET to `/api/budgets/?entity_id={id}` on load
  - PUT to `/api/budgets/{id}?entity_id={id}` on update
  - DELETE to `/api/budgets/{id}?entity_id={id}` on delete
  - Authorization header present in all requests

## Notes

- If backend is not running, API calls will fail with network error
- Test user must have access to at least one entity with expense categories
- Budgets are entity-specific - only budgets for current entity should display
- Category dropdown should only show expense categories (not income)
- Delete button should only be visible/enabled for admin and manager roles
- Progress bar calculation: (spent_amount / budget_amount) * 100
- Spending is calculated from transactions within the budget period date range
