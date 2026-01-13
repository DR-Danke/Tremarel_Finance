# E2E Test: Transaction CRUD Flow

Test that the Finance Tracker transaction management works correctly, including creating, viewing, editing, and deleting transactions.

## User Story

As a Finance Tracker user
I want to manage my income and expense transactions
So that I can accurately track my financial activity for my family or startup

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials
- The user is authenticated

## Test Steps

### Setup - Navigate and Authenticate

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. If not logged in, log in with test credentials:
   - Email: test@example.com (or a valid test user email)
   - Password: testpassword123 (or valid test password)
3. Navigate to `/transactions` page
4. Take a screenshot of the transactions page
5. **Verify** page loads with:
   - "Transactions" heading
   - "Add Transaction" button is visible
   - Filter controls visible (date range, type)
   - Transaction table or empty state message

### Test: Empty State

6. **Verify** if no transactions exist:
   - Empty state message "No Transactions Found" is displayed
   - Message suggests adding first transaction
7. Take a screenshot of empty state

### Test: Create Transaction

8. Click "Add Transaction" button
9. Take a screenshot of the transaction form dialog
10. **Verify** form displays:
    - Type dropdown (Income/Expense)
    - Amount input field with $ prefix
    - Category dropdown
    - Date input (defaulted to today)
    - Description text field
    - Notes textarea
    - Cancel and Add Transaction buttons

11. Test form validation - submit with empty required fields
12. Take a screenshot
13. **Verify** validation errors displayed:
    - "Amount is required" error
    - "Category is required" error

14. Fill in transaction form:
    - Type: Expense
    - Amount: 50.00
    - Category: First available expense category
    - Date: Today's date
    - Description: "Test grocery expense"
    - Notes: "E2E test transaction"

15. Click "Add Transaction" button
16. Take a screenshot
17. **Verify** dialog closes
18. **Verify** new transaction appears in table with:
    - Correct date
    - "Expense" chip (red)
    - Category name
    - Amount: -$50.00 (red)
    - Description: "Test grocery expense"
    - Edit and Delete buttons visible

19. Take a screenshot of the transaction in the table

### Test: Filter Transactions

20. Click type filter dropdown
21. Select "Income"
22. Click "Apply" button
23. Take a screenshot
24. **Verify** transaction table filters correctly:
    - If no income transactions, empty state shows
    - If income transactions exist, only income shown

25. Click "Clear" button to reset filters
26. **Verify** all transactions visible again

### Test: Edit Transaction

27. Click Edit button (pencil icon) on the test transaction
28. Take a screenshot of edit dialog
29. **Verify** form is prefilled with transaction data

30. Change amount from 50.00 to 75.00
31. Change description to "Updated grocery expense"
32. Click "Update Transaction" button
33. Take a screenshot
34. **Verify** dialog closes
35. **Verify** table shows updated values:
    - Amount: -$75.00
    - Description: "Updated grocery expense"

### Test: Delete Transaction (Admin/Manager only)

36. **Note:** Delete requires admin or manager role
37. If user has admin/manager role:
    - Click Delete button (trash icon) on the test transaction
    - Take a screenshot of delete confirmation dialog
    - **Verify** confirmation shows transaction details
    - Click "Delete" button
    - Take a screenshot
    - **Verify** transaction removed from table
    - **Verify** empty state or updated transaction count

38. If user has regular user/viewer role:
    - **Verify** Delete button is not visible or disabled
    - Take a screenshot showing delete not available

### Test: Create Income Transaction

39. Click "Add Transaction" button
40. Fill in transaction form:
    - Type: Income
    - Amount: 1000.00
    - Category: First available income category
    - Date: Today's date
    - Description: "Test salary income"

41. Click "Add Transaction" button
42. Take a screenshot
43. **Verify** new transaction appears:
    - "Income" chip (green)
    - Amount: +$1,000.00 (green)

## Success Criteria

- Transactions page loads without errors
- Add Transaction form displays all required fields
- Form validation works correctly for:
  - Empty required fields
  - Invalid amount format
- Transaction creation adds new row to table
- Table displays transactions with:
  - Formatted date
  - Type chip with correct color (green for income, red for expense)
  - Category name
  - Formatted currency amount with sign
  - Description text
- Filters work correctly for type and date range
- Edit form prefills with current values
- Update saves changes and reflects in table
- Delete removes transaction (admin/manager only)
- Console shows expected INFO log messages:
  - "INFO [TransactionsPage]: Opening add transaction dialog"
  - "INFO [TransactionService]: Creating transaction..."
  - "INFO [useTransactions]: Transaction created, refreshing list"

## Technical Verification

- Check browser console for:
  - INFO log messages for transaction operations
  - No JavaScript errors
  - No React warnings
- Check network requests:
  - POST to `/api/transactions/` on create
  - GET to `/api/transactions/?entity_id=...` on list
  - PUT to `/api/transactions/{id}` on update
  - DELETE to `/api/transactions/{id}` on delete
  - Authorization header present in all requests

## Notes

- If the backend is not running, operations will fail with network errors
- Category selection depends on categories existing in the database
- Delete operation requires admin or manager role
- Transaction amounts are always positive; type determines income/expense
- The entity_id may be a placeholder until EntityContext is implemented
