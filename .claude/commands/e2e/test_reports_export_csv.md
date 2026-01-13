# E2E Test: Reports and CSV Export

Test that the Finance Tracker Reports page displays financial reports with date range filtering, income vs expense comparison charts, category breakdown tables, and CSV export functionality.

## User Story

As a Finance Tracker user
I want to view comprehensive financial reports and export my transaction data
So that I can analyze my financial health over time, identify spending patterns, and use my data in external tools like spreadsheets

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
3. Navigate to `/reports` page
4. Take a screenshot of the initial Reports page
5. **Verify** page loads with:
   - "Reports" title visible
   - Date range picker visible
   - Current entity info displayed

### Test: Date Range Picker

6. Locate the date range picker component
7. Take a screenshot of the date range picker
8. **Verify** date range picker contains:
   - Start date input field
   - End date input field
   - Quick select buttons (This Month, Last 3 Months, Last 6 Months, This Year)
9. Click "This Month" quick select button
10. **Verify** date inputs update to current month range
11. Click "Last 3 Months" quick select button
12. **Verify** date inputs update to last 3 months range
13. Take a screenshot after selecting date range

### Test: Report Summary Cards

14. Scroll to the summary section if needed
15. Take a screenshot of the report summary cards
16. **Verify** four summary cards are visible:
   - "Total Income" card (green themed)
   - "Total Expenses" card (red themed)
   - "Net Balance" card (blue themed)
   - "Transaction Count" card
17. **Verify** summary cards show:
   - Properly formatted currency values (e.g., $1,234.56)
   - Appropriate icons for each card
   - Labels for each metric

### Test: Income vs Expense Chart

18. Scroll to the chart section if needed
19. Take a screenshot of the income vs expense chart
20. **Verify** line chart displays:
   - Title "Income vs Expenses" or similar
   - Two data lines (income in green, expenses in red)
   - X-axis with period labels (months)
   - Y-axis with currency values
   - Legend showing Income and Expenses
21. Hover over a data point on the chart (if possible)
22. **Verify** tooltip shows:
   - Period/Month name
   - Income value for that period
   - Expense value for that period

### Test: Category Breakdown Table

23. Locate the category breakdown table section
24. Take a screenshot of the category breakdown table
25. **Verify** table displays:
   - Title "Category Breakdown" or similar
   - Column headers: Category, Amount, Percentage, Type
   - Rows for each category with data
26. Click on "Expenses" tab/filter (if tabbed interface)
27. **Verify** table shows only expense categories
28. Click on "Income" tab/filter (if tabbed interface)
29. **Verify** table shows only income categories
30. Take a screenshot of filtered table

### Test: CSV Export

31. Locate the "Export CSV" button
32. Take a screenshot showing the export button
33. Click the "Export CSV" button
34. **Verify** file download initiates
35. **Verify** downloaded file:
   - Has .csv extension
   - Filename includes date range (e.g., transactions_2024-01-01_2024-01-31.csv)
36. Take a screenshot after export completes (success message if any)

### Test: Empty State (No Data in Range)

37. Select a date range with no transactions (e.g., far future dates)
38. Take a screenshot of empty state
39. **Verify** empty state displays:
   - Summary cards show $0.00 for all metrics
   - Chart shows appropriate empty state message
   - Table shows "No data" message
   - Export button may be disabled or show warning

### Test: Entity Switching

40. Select a different entity from the EntitySelector
41. Take a screenshot after entity switch
42. **Verify** all report data updates:
   - Summary cards show new entity's totals
   - Chart updates with new entity's data
   - Table updates with new entity's categories
   - Loading indicator shown during data fetch

### Test: Loading State

43. Refresh the reports page
44. **Verify** loading indicators appear while data is being fetched:
   - Skeleton loaders or CircularProgress for summary cards
   - Loading indicator for chart
   - Loading indicator for table
45. **Verify** data appears after loading completes

## Success Criteria

- Reports page loads without errors at `/reports`
- Date range picker allows selecting custom start and end dates
- Quick select buttons work for common date ranges (This Month, Last 3 Months, Last 6 Months, This Year)
- Four summary cards display correctly:
  - Total Income (green, with income icon)
  - Total Expenses (red, with expense icon)
  - Net Balance (blue, calculated as income - expenses)
  - Transaction Count (neutral)
- Currency values are properly formatted with $ symbol and commas
- Line chart shows income vs expenses over selected period
- Category breakdown table shows all categories with amounts and percentages
- Category breakdown can be filtered by type (Income/Expense)
- CSV export downloads a file with transaction data
- Reports update when entity is changed
- Empty state is handled gracefully
- Loading state shows appropriate indicators
- Console shows expected INFO log messages:
  - "INFO [ReportsPage]: Fetching reports for entity..."
  - "INFO [ReportService]: Reports data fetched successfully"
  - "INFO [useReports]: Reports loaded for entity..."

## Technical Verification

- Check browser console for:
  - INFO log messages for reports operations
  - No JavaScript errors
  - No React warnings
- Check network requests:
  - GET to `/api/reports/data?entity_id=...&start_date=...&end_date=...` on load
  - GET to `/api/reports/export/csv?entity_id=...&start_date=...&end_date=...` on export
  - Authorization header present in requests
  - Correct entity_id and date parameters sent
- Verify API response contains:
  - summary object with totals
  - income_expense_comparison array
  - category_breakdown array

## Notes

- If the backend is not running, reports page will show error state
- Charts require Recharts library to render
- Summary values depend on transactions existing in the database
- Date range defaults to "This Month" on initial load
- CSV export uses blob download for file handling
- Large date ranges may take longer to load
- Currency formatting should handle large numbers with commas
