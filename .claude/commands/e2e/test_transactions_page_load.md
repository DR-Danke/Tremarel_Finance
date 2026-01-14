# E2E Test: Transactions Page Load

Test that the Transactions page loads correctly without API errors, fetching categories from the correct endpoint.

## User Story

As a Finance Tracker user
I want the Transactions page to load without errors
So that I can view and manage my transactions without encountering API failures

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials
- The user is authenticated
- At least one entity exists for the user

## Test Steps

### Setup - Navigate and Authenticate

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. If not logged in, log in with test credentials:
   - Email: test@example.com (or a valid test user email)
   - Password: testpassword123 (or valid test password)
3. Take a screenshot of the logged-in state

### Test: Navigate to Transactions Page

4. Navigate to `/transactions` page by clicking "Transactions" in the sidebar
5. Take a screenshot of the Transactions page
6. **Verify** page loads with:
   - "Transactions" heading visible
   - "Add Transaction" button visible
   - Filter controls visible (date range, type dropdown)
   - Transaction table or empty state displayed
   - No error banners or alerts (unless expected from data state)

### Test: Verify No Console Errors

7. Open browser console/DevTools (or check network requests)
8. Take a screenshot showing the network tab or console
9. **Verify** NO 405 errors for category requests:
   - Should NOT see: `GET /api/categories/?entity_id=... 405`
   - Should see: `GET /api/categories/entity/{entityId} 200` (correct endpoint)
10. **Verify** NO CORS errors or 500 Internal Server Errors
11. **Verify** console shows success log:
    - "INFO [CategoryService]: Fetching categories for entity..."
    - "INFO [CategoryService]: Fetched X categories"
    - "INFO [TransactionsPage]: Loaded X categories from API"

### Test: Verify Categories Load from API

12. Click "Add Transaction" button
13. Take a screenshot of the Add Transaction dialog
14. **Verify** form displays:
    - Category dropdown is populated
    - Categories are from the API (not mock categories like "Salary", "Freelance", "Food & Dining")
    - OR if no categories exist, empty dropdown is shown
15. Close the dialog by clicking Cancel

### Test: Verify Transactions Load

16. Take a screenshot of the transactions table
17. **Verify** transactions table state:
    - If transactions exist: table shows transaction rows
    - If no transactions: empty state message "No Transactions Found" is displayed
18. **Verify** console shows transaction-related logs:
    - "INFO [useTransactions]: Fetching transactions for entity..."

### Test: Page Reload

19. Refresh the page (F5 or browser refresh)
20. Wait for page to fully load
21. Take a screenshot after reload
22. **Verify** page reloads successfully:
    - Same content displays as before
    - No new errors in console
    - Categories still load from API (not falling back to mock)

## Success Criteria

- Transactions page loads without any 405 Method Not Allowed errors
- Categories are fetched from `/api/categories/entity/{entityId}` (correct endpoint)
- No CORS errors or 500 Internal Server Errors in console
- CategoryService logs show successful category fetching
- TransactionsPage logs show "Loaded X categories from API" (not "Using mock categories")
- Add Transaction dialog shows categories from API
- Transactions table displays correctly (with data or empty state)
- Page can be reloaded without errors

## Technical Verification

- Check browser console for:
  - INFO log messages from CategoryService and TransactionsPage
  - No JavaScript errors or warnings
  - No React errors
  - No 405, 500, or CORS errors

- Check network requests:
  - GET `/api/categories/entity/{entityId}` returns 200
  - GET `/api/transactions/?entity_id=...` returns 200
  - No requests to `/api/categories/?entity_id=...` (old incorrect endpoint)
  - Authorization header present in all requests

## Notes

- This test specifically validates the fix for the 405 error when loading categories
- The fix changed TransactionsPage to use categoryService instead of a direct API call
- If categories fail to load, mock categories are used as fallback (but this should not happen normally)
- The test verifies both the absence of errors AND the presence of correct API calls
