# Feature: Reports and CSV Export

## Metadata
issue_number: `26`
adw_id: `d110d3f0`
issue_json: `{"number":26,"title":"[FinanceTracker] Wave 5: Reports and Export","body":"..."}`

## Feature Description
Create a comprehensive Reports page for the Finance Tracker application that provides financial analysis and data export capabilities. The feature includes:
- Date range picker to filter report data by custom time periods
- Income vs expense comparison visualization showing financial health over time
- Category breakdown table showing spending/income distribution by category
- Trend charts displaying monthly financial patterns using Recharts
- CSV export functionality to download transaction data for external analysis
- Summary reports that can be filtered by entity or show consolidated view

This feature transforms financial data into actionable insights through visual reports and provides data portability through CSV export.

## User Story
As a Finance Tracker user
I want to view comprehensive financial reports and export my transaction data
So that I can analyze my financial health over time, identify spending patterns, and use my data in external tools like spreadsheets

## Problem Statement
Users need visibility into their financial data beyond basic transaction lists. They need:
1. Historical trend analysis to understand financial patterns over time
2. Category-based breakdowns to identify where money is going
3. Comparison of income vs expenses to assess financial health
4. Ability to export data for tax preparation, external analysis, or backup purposes
5. Flexible date filtering to analyze specific time periods

Currently, the dashboard only shows current month statistics. Users lack the ability to analyze longer time periods or export their data.

## Solution Statement
Implement a dedicated Reports page that:
1. Provides a date range picker component for selecting custom report periods
2. Displays income vs expense comparison using a line chart (reusing/extending existing chart patterns)
3. Shows category breakdown in both chart and table formats
4. Implements CSV export endpoint that generates downloadable transaction data
5. Integrates with EntityContext for entity-specific or consolidated reporting
6. Follows existing Clean Architecture patterns (routes → services → repositories)

## Relevant Files
Use these files to implement the feature:

### Backend Reference Files (patterns to follow)
- `apps/Server/src/adapter/rest/dashboard_routes.py` - Pattern for API endpoints with entity filtering
- `apps/Server/src/core/services/dashboard_service.py` - Pattern for aggregation services with SQL queries
- `apps/Server/src/interface/dashboard_dto.py` - Pattern for response DTOs with Decimal types
- `apps/Server/src/repository/transaction_repository.py` - Pattern for filtering transactions by date range
- `apps/Server/main.py` - Register new reports router

### Frontend Reference Files (patterns to follow)
- `apps/Client/src/pages/DashboardPage.tsx` - Pattern for page with charts and entity context
- `apps/Client/src/pages/TransactionsPage.tsx` - Pattern for page with filters and data tables
- `apps/Client/src/services/dashboardService.ts` - Pattern for API service
- `apps/Client/src/hooks/useDashboard.ts` - Pattern for data fetching hook
- `apps/Client/src/components/ui/TRMonthlyTrendChart.tsx` - Pattern for Recharts line chart
- `apps/Client/src/components/ui/TRExpenseBreakdownChart.tsx` - Pattern for Recharts pie chart
- `apps/Client/src/types/index.ts` - Add report-related TypeScript interfaces
- `apps/Client/src/App.tsx` - Update ReportsPage import (currently inline placeholder)

### E2E Test Reference Files
- `.claude/commands/test_e2e.md` - E2E test runner instructions
- `.claude/commands/e2e/test_dashboard_summary_stats.md` - Example E2E test for charts/statistics

### New Files
- `apps/Server/src/adapter/rest/reports_routes.py` - Reports API endpoints
- `apps/Server/src/core/services/reports_service.py` - Reports business logic
- `apps/Server/src/interface/reports_dto.py` - Reports DTOs
- `apps/Server/tests/test_reports.py` - Backend unit tests
- `apps/Client/src/pages/ReportsPage.tsx` - Full Reports page implementation
- `apps/Client/src/services/reportService.ts` - Reports API client
- `apps/Client/src/hooks/useReports.ts` - Reports data hook
- `apps/Client/src/components/ui/TRReportDateRangePicker.tsx` - Date range picker component
- `apps/Client/src/components/ui/TRIncomeExpenseChart.tsx` - Income vs Expense comparison chart
- `apps/Client/src/components/ui/TRCategoryBreakdownTable.tsx` - Category breakdown table
- `.claude/commands/e2e/test_reports_export_csv.md` - E2E test specification

## Implementation Plan

### Phase 1: Foundation
1. Create backend DTOs for report requests and responses
2. Implement reports service with aggregation methods
3. Create reports API endpoints
4. Add backend unit tests

### Phase 2: Core Implementation
1. Create frontend TypeScript types for reports
2. Implement reportService for API calls
3. Create useReports hook for data management
4. Build ReportsPage with date range picker and filters
5. Implement chart components for income/expense comparison
6. Create category breakdown table component

### Phase 3: Integration
1. Implement CSV export endpoint
2. Add CSV download functionality to frontend
3. Connect ReportsPage to EntityContext
4. Create E2E test specification
5. Validate all features work together

## Step by Step Tasks

### Step 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_dashboard_summary_stats.md` to understand E2E test format
- Create `.claude/commands/e2e/test_reports_export_csv.md` with test steps for:
  - Navigating to Reports page
  - Selecting date range
  - Viewing income vs expense chart
  - Viewing category breakdown table
  - Exporting data to CSV
  - Verifying downloaded file

### Step 2: Create Backend DTOs
- Create `apps/Server/src/interface/reports_dto.py` with:
  - `ReportFilterDTO` - Input parameters (start_date, end_date, type, category_ids)
  - `IncomeExpenseComparisonDTO` - Period with income and expense totals
  - `CategorySummaryDTO` - Category breakdown with totals and percentages
  - `ReportSummaryDTO` - Overall totals for the report period
  - `ReportDataResponseDTO` - Complete response with all report data
- Use Decimal for financial values, match existing DTO patterns

### Step 3: Create Backend Reports Service
- Create `apps/Server/src/core/services/reports_service.py` with:
  - `get_income_expense_comparison(db, entity_id, start_date, end_date)` - Monthly breakdown
  - `get_category_summary(db, entity_id, start_date, end_date, type)` - Category totals
  - `get_report_summary(db, entity_id, start_date, end_date)` - Overall totals
  - `get_report_data(db, entity_id, filters)` - Combined report data
  - `export_transactions_csv(db, entity_id, start_date, end_date)` - CSV generation
- Use SQLAlchemy aggregations (SUM, GROUP BY) following dashboard_service patterns
- Add INFO logging for all operations

### Step 4: Create Backend Reports Routes
- Create `apps/Server/src/adapter/rest/reports_routes.py` with:
  - `GET /api/reports/data` - Main report data endpoint
  - `GET /api/reports/export/csv` - CSV export endpoint (returns StreamingResponse)
- Apply authentication dependency (`get_current_user`)
- Filter by entity_id query parameter
- Register router in `main.py`

### Step 5: Add Backend Unit Tests
- Create `apps/Server/tests/test_reports.py` with test cases:
  - Test report data with valid entity and date range
  - Test report with only income transactions
  - Test report with only expense transactions
  - Test empty state (no transactions in date range)
  - Test CSV export generates valid CSV format
  - Test unauthorized access
  - Test invalid date range (start > end)
- Run `cd apps/Server && uv run pytest tests/test_reports.py -v`

### Step 6: Create Frontend TypeScript Types
- Update `apps/Client/src/types/index.ts` to add:
  - `ReportFilter` interface (startDate, endDate, type, categoryIds)
  - `IncomeExpenseComparison` interface (period, month, income, expenses)
  - `CategorySummary` interface (categoryId, categoryName, amount, percentage, type)
  - `ReportSummary` interface (totalIncome, totalExpenses, netBalance, transactionCount)
  - `ReportData` interface (summary, incomeExpenseComparison, categoryBreakdown)

### Step 7: Create Frontend Report Service
- Create `apps/Client/src/services/reportService.ts` with:
  - `getReportData(entityId, filters)` - Fetch report data
  - `exportCsv(entityId, filters)` - Download CSV (handle blob response)
- Follow dashboardService patterns
- Add console logging for operations

### Step 8: Create useReports Hook
- Create `apps/Client/src/hooks/useReports.ts` with:
  - State for: reportData, filters, isLoading, error
  - `setFilters` function to update filter state
  - `refresh` function to refetch data
  - `exportToCsv` function to trigger download
- Follow useDashboard patterns
- Auto-fetch when entity or filters change

### Step 9: Create TRReportDateRangePicker Component
- Create `apps/Client/src/components/ui/TRReportDateRangePicker.tsx` with:
  - Start date and end date TextField inputs (type="date")
  - Quick select buttons: "This Month", "Last 3 Months", "Last 6 Months", "This Year"
  - Apply and Clear buttons
  - onChange callback with selected date range
- Use MUI TextField with type="date" for date inputs
- Responsive layout using MUI Grid

### Step 10: Create TRIncomeExpenseChart Component
- Create `apps/Client/src/components/ui/TRIncomeExpenseChart.tsx` with:
  - Recharts LineChart showing income vs expenses over time
  - Two lines: green for income, red for expenses
  - Custom tooltip showing period, income, and expense amounts
  - Empty state message when no data
  - Title: "Income vs Expenses"
- Follow TRMonthlyTrendChart patterns

### Step 11: Create TRCategoryBreakdownTable Component
- Create `apps/Client/src/components/ui/TRCategoryBreakdownTable.tsx` with:
  - MUI Table showing category breakdown
  - Columns: Category, Amount, Percentage, Type
  - Sorting by amount (descending)
  - Type chips (green for income, red for expense)
  - Empty state message when no data
- Use MUI Table, TableHead, TableBody, TableRow, TableCell

### Step 12: Implement ReportsPage
- Update `apps/Client/src/pages/ReportsPage.tsx` (replace placeholder):
  - Import useAuth, useEntity, useReports hooks
  - Display TRReportDateRangePicker at top
  - Show ReportSummary cards (Total Income, Total Expenses, Net Balance, Transaction Count)
  - Display TRIncomeExpenseChart below summary
  - Show TRCategoryBreakdownTable with tabs for "Income" and "Expense" categories
  - Add "Export CSV" button that triggers download
  - Handle loading, error, and empty states
- Update `apps/Client/src/App.tsx` to import ReportsPage from file instead of inline

### Step 13: Run Frontend Validation
- Run `cd apps/Client && npm run typecheck` to verify TypeScript
- Run `cd apps/Client && npm run lint` to check for lint errors
- Run `cd apps/Client && npm run build` to verify production build

### Step 14: Run Full Validation Suite
- Run all backend tests: `cd apps/Server && uv run pytest`
- Run frontend type check: `cd apps/Client && npm run typecheck`
- Run frontend build: `cd apps/Client && npm run build`
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_reports_export_csv.md` to validate E2E functionality

## Testing Strategy

### Unit Tests
- Backend: Test reports service methods with mocked database
- Backend: Test CSV generation format and content
- Backend: Test date range filtering logic
- Backend: Test aggregation calculations (sums, percentages)
- Frontend: TypeScript compilation validates type correctness

### Edge Cases
- Empty date range (no transactions in period)
- Single transaction in period
- Only income or only expense transactions
- Very large date ranges (multiple years)
- Category with no transactions
- Invalid date range (start date after end date)
- No entity selected (should show error)
- Large number of categories (pagination/scrolling)

## Acceptance Criteria
- [ ] Reports page is accessible at `/reports` when authenticated
- [ ] Date range picker allows selecting custom start and end dates
- [ ] Quick select buttons work for common date ranges (This Month, Last 3 Months, Last 6 Months, This Year)
- [ ] Income vs Expense chart displays comparison over selected period with monthly granularity
- [ ] Category breakdown table shows all categories with amounts and percentages
- [ ] Category breakdown can be filtered by type (Income/Expense)
- [ ] Report summary shows Total Income, Total Expenses, Net Balance, and Transaction Count
- [ ] CSV export downloads a file with all transactions in the selected date range
- [ ] CSV file includes columns: Date, Type, Category, Amount, Description, Notes
- [ ] All data is filtered by the currently selected entity
- [ ] Loading states are shown while data is being fetched
- [ ] Error states are displayed when API calls fail
- [ ] Empty states are shown when no data exists for the selected criteria
- [ ] Console shows appropriate INFO log messages for all operations

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Backend tests
cd apps/Server && uv run pytest tests/test_reports.py -v

# All backend tests (check for regressions)
cd apps/Server && uv run pytest

# Frontend type check
cd apps/Client && npm run typecheck

# Frontend lint
cd apps/Client && npm run lint

# Frontend build
cd apps/Client && npm run build
```

- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_reports_export_csv.md` to validate the Reports page functionality end-to-end

## Notes

### CSV Export Implementation
The CSV export will use Python's built-in `csv` module and FastAPI's `StreamingResponse` for memory-efficient streaming:
```python
from fastapi.responses import StreamingResponse
import csv
import io

def generate_csv(transactions):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Type', 'Category', 'Amount', 'Description', 'Notes'])
    for t in transactions:
        writer.writerow([t.date, t.type, t.category_name, t.amount, t.description, t.notes])
    return output.getvalue()
```

### Frontend CSV Download
Use blob response handling for file download:
```typescript
const response = await apiClient.get('/reports/export/csv', { responseType: 'blob' })
const url = window.URL.createObjectURL(new Blob([response.data]))
const link = document.createElement('a')
link.href = url
link.download = `transactions_${startDate}_${endDate}.csv`
link.click()
```

### Date Range Defaults
- Default to "This Month" when page loads
- Store last selected date range in component state (not persisted)
- Use ISO date format (YYYY-MM-DD) for API communication

### Dependencies
No new libraries required:
- Recharts already installed for charts
- MUI already installed for date inputs and tables
- Python csv module is built-in

### Future Considerations
- PDF export could be added using a library like ReportLab
- Scheduled email reports could be added later
- Multi-entity consolidated reports could aggregate across entities
- Custom report builder could allow users to select which data to include
