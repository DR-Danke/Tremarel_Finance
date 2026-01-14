# E2E Test: Category API Integration

Test that all pages using categories (Budgets, Recurring Templates, Transactions) call the correct category API endpoint and do not use mock/fallback data.

## User Story

As a Finance Tracker developer
I want to ensure all pages use the correct category API endpoint
So that users see real category data and HTTP 405 errors are eliminated

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials
- At least one entity exists for the test user
- Browser DevTools Network tab open to monitor API calls

## Test Steps

### Setup - Navigate and Authenticate

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. Open browser DevTools (F12) and switch to Network tab
3. Clear the Network log
4. If not logged in, log in with test credentials:
   - Email: test@example.com (or a valid test user email)
   - Password: testpassword123 (or valid test password)
5. Take a screenshot after login
6. **Verify** login successful (redirected to dashboard)

### Test: Budgets Page Category API Call

7. Clear the Network log in DevTools
8. Navigate to `/budgets` page
9. Take a screenshot of the budgets page
10. **Verify** in Network tab:
    - Request to `/api/categories/entity/{entity_id}` is made
    - Request uses GET method
    - Response status is 200 OK
    - NO request to `/api/categories?entity_id=...` (wrong endpoint)
    - NO 405 Method Not Allowed errors

11. Open browser Console tab
12. **Verify** console logs:
    - "INFO [CategoryService]: Fetching categories for entity ..." is logged
    - "INFO [CategoryService]: Fetched X categories" is logged
    - NO "mock" or "fallback" messages appear

### Test: Recurring Templates Page Category API Call

13. Clear the Network log in DevTools
14. Navigate to `/recurring` page
15. Take a screenshot of the recurring templates page
16. **Verify** in Network tab:
    - Request to `/api/categories/entity/{entity_id}` is made
    - Request uses GET method
    - Response status is 200 OK
    - NO request to `/api/categories?entity_id=...` (wrong endpoint)
    - NO 405 Method Not Allowed errors

17. Open browser Console tab
18. **Verify** console logs:
    - "INFO [RecurringTemplatesPage]: Loaded X categories from API" is logged
    - NO "Using mock categories" message
    - NO "mock" or "fallback" messages appear

### Test: Transactions Page Category API Call

19. Clear the Network log in DevTools
20. Navigate to `/transactions` page
21. Take a screenshot of the transactions page
22. **Verify** in Network tab:
    - Request to `/api/categories/entity/{entity_id}` is made
    - Request uses GET method
    - Response status is 200 OK
    - NO request to `/api/categories?entity_id=...` (wrong endpoint)
    - NO 405 Method Not Allowed errors

23. Open browser Console tab
24. **Verify** console logs:
    - "INFO [TransactionsPage]: Loaded X categories from API" is logged
    - NO "using mock categories" message
    - NO "mock" or "fallback" messages appear

### Test: No Entity Selected State

25. If possible, deselect the current entity or use a user with no entities
26. Navigate to `/budgets` page
27. Take a screenshot
28. **Verify** in Network tab:
    - NO category API call is made when entityId is null
    - Console shows "INFO [BudgetsPage]: No entityId, skipping category load"

29. Navigate to `/recurring` page
30. Take a screenshot
31. **Verify** in Network tab:
    - NO category API call is made when entityId is null
    - Console shows "INFO [RecurringTemplatesPage]: No entityId, skipping category load"

32. Navigate to `/transactions` page
33. Take a screenshot
34. **Verify** in Network tab:
    - NO category API call is made when entityId is null
    - Console shows "INFO [TransactionsPage]: No entityId, skipping category load"

### Test: Category Dropdown Population

35. Select an entity with categories
36. Navigate to `/budgets` page
37. Click "Add Budget" button
38. Take a screenshot of the budget form
39. **Verify** Category dropdown:
    - Dropdown is populated with real categories from database
    - Categories match what is stored in database
    - NO mock categories like "Salary", "Freelance", "Food & Dining" unless they exist in DB

40. Navigate to `/recurring` page
41. Click "Add Recurring Template" button
42. Take a screenshot of the recurring template form
43. **Verify** Category dropdown:
    - Dropdown is populated with real categories from database
    - Categories match what is stored in database

44. Navigate to `/transactions` page
45. Click "Add Transaction" button
46. Take a screenshot of the transaction form
47. **Verify** Category dropdown:
    - Dropdown is populated with real categories from database
    - Categories match what is stored in database

## Success Criteria

- All three pages (Budgets, Recurring, Transactions) use the correct endpoint:
  - `GET /api/categories/entity/{entity_id}` (correct)
  - NOT `GET /api/categories?entity_id=...` (wrong)
- No HTTP 405 Method Not Allowed errors occur
- No HTTP 4xx or 5xx errors on category API calls
- Console shows proper INFO logs from CategoryService
- Console does NOT show any "mock" or "fallback" category messages
- Category dropdowns show real database categories, not hardcoded mock data
- When entityId is null, no category API call is made (null guard works)
- When entityId is null, appropriate console message is logged

## Technical Verification

- Check browser console for:
  - "INFO [CategoryService]: Fetching categories for entity ..." messages
  - "INFO [CategoryService]: Fetched X categories" messages
  - NO "mock" or "fallback" related messages
  - NO JavaScript errors
  - NO React warnings

- Check network requests:
  - GET to `/api/categories/entity/{entityId}` returns 200
  - NO requests to `/api/categories?entity_id=...`
  - NO 405 status codes
  - Authorization header present in all requests

## Notes

- The correct API endpoint is `/api/categories/entity/{entity_id}` with path parameter
- The wrong endpoint `/api/categories?entity_id=...` with query parameter returns 405
- MOCK_CATEGORIES constants have been removed from all pages
- Categories are initialized as empty arrays - dropdowns will be empty until API responds
- The categoryService.getCategories() method handles the correct API call pattern
- This test validates the fix for the category API endpoint mismatch bug
