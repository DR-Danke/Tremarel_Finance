# E2E Test: Dashboard Summary Stats and Charts

Test that the Finance Tracker dashboard displays summary statistics and charts correctly, providing a visual overview of the user's financial health.

## User Story

As a Finance Tracker user
I want to see a visual summary of my financial data on the dashboard
So that I can quickly understand my financial health and take action

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials
- The user is authenticated
- An entity is selected in the EntityContext
- Some transactions exist for the entity (optional - test empty state if none)

## Test Steps

### Setup - Navigate and Authenticate

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. If not logged in, log in with test credentials:
   - Email: test@example.com (or a valid test user email)
   - Password: testpassword123 (or valid test password)
3. Navigate to `/dashboard` page (or `/` which is the dashboard)
4. Take a screenshot of the dashboard page
5. **Verify** page loads with:
   - Welcome message with user name
   - Entity selector visible
   - Current entity info displayed

### Test: Stat Cards Display

6. **Verify** three stat cards are visible:
   - "Total Income" card (green themed)
   - "Total Expenses" card (red themed)
   - "Net Balance" card (blue themed)
7. Take a screenshot of the stat cards section
8. **Verify** stat cards show:
   - Properly formatted currency values (e.g., $1,234.56)
   - Appropriate icons for each card
   - Labels for each metric

### Test: Monthly Trend Chart

9. Scroll to the line chart section if needed
10. Take a screenshot of the monthly trend chart
11. **Verify** line chart displays:
   - Title "Income vs Expenses (Last 6 Months)" or similar
   - Two data lines (income in green, expenses in red)
   - X-axis with month labels (Jan, Feb, Mar, etc.)
   - Y-axis with currency values
   - Legend showing Income and Expenses
12. Hover over a data point on the chart
13. **Verify** tooltip shows:
   - Month name
   - Income value for that month
   - Expense value for that month

### Test: Expense Breakdown Pie Chart

14. Locate the pie chart section
15. Take a screenshot of the expense breakdown chart
16. **Verify** pie chart displays:
   - Title "Expenses by Category" or similar
   - Colored segments for each expense category
   - Legend with category names
17. Hover over a pie segment
18. **Verify** tooltip shows:
   - Category name
   - Amount spent
   - Percentage of total expenses

### Test: Quick Action Button

19. Locate the "Add Transaction" quick action button
20. Take a screenshot showing the button
21. Click the "Add Transaction" button
22. **Verify** user is navigated to the transactions page
23. Take a screenshot of the transactions page
24. Navigate back to dashboard

### Test: Entity Switching

25. Select a different entity from the EntitySelector
26. Take a screenshot after entity switch
27. **Verify** all dashboard data updates:
   - Stat cards show new entity's totals
   - Charts update with new entity's data
   - Loading indicator shown during data fetch

### Test: Empty State (No Transactions)

28. If possible, select or create an entity with no transactions
29. Take a screenshot of empty state dashboard
30. **Verify** empty state displays:
   - Stat cards show $0.00 for all metrics
   - Charts show appropriate empty state message (e.g., "No data to display")
   - Suggestion to add first transaction

### Test: Loading State

31. Refresh the dashboard page
32. **Verify** loading indicators appear while data is being fetched:
   - Skeleton loaders or CircularProgress for stat cards
   - Loading indicator for charts
33. **Verify** data appears after loading completes

### Test: Error State

34. (Optional) If backend can be temporarily stopped:
   - Stop the backend server
   - Refresh the dashboard
   - Take a screenshot of error state
   - **Verify** error message is displayed
   - Restart the backend server

## Success Criteria

- Dashboard page loads without errors
- Three stat cards display correctly with:
  - Total Income (green, with income icon)
  - Total Expenses (red, with expense icon)
  - Net Balance (blue, calculated as income - expenses)
- Currency values are properly formatted with $ symbol and commas
- Line chart shows 6 months of income vs expense data
- Pie chart shows expense breakdown by category
- Charts have proper tooltips on hover
- Quick action button navigates to transaction creation
- Dashboard updates when entity is changed
- Empty state is handled gracefully
- Loading state shows appropriate indicators
- Console shows expected INFO log messages:
  - "INFO [DashboardPage]: Fetching dashboard stats for entity..."
  - "INFO [DashboardService]: Dashboard stats fetched successfully"
  - "INFO [useDashboard]: Stats loaded for entity..."

## Technical Verification

- Check browser console for:
  - INFO log messages for dashboard operations
  - No JavaScript errors
  - No React warnings
- Check network requests:
  - GET to `/api/dashboard/stats?entity_id=...` on load
  - Authorization header present in request
  - Correct entity_id parameter sent
- Verify API response contains:
  - current_month_summary object
  - monthly_trends array (6 months)
  - expense_breakdown array

## Notes

- If the backend is not running, dashboard will show error state
- Charts require Recharts library to render
- Stat card values depend on transactions existing in the database
- Pie chart only shows expense categories (not income)
- Monthly trends show last 6 months including current month
- Net balance can be negative (shown in red if so)
- Currency formatting should handle large numbers with commas
