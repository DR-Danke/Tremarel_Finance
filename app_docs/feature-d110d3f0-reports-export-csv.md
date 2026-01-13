# Reports and CSV Export

**ADW ID:** d110d3f0
**Date:** 2026-01-13
**Specification:** specs/issue-26-adw-d110d3f0-sdlc_planner-reports-export-csv.md

## Overview

A comprehensive Reports page that provides financial analysis and data export capabilities for the Finance Tracker application. The feature includes date range filtering, income vs expense comparison charts, category breakdown tables, and CSV export functionality for external data analysis.

## What Was Built

- **ReportsPage**: Main page displaying financial reports with summary cards and visualizations
- **TRReportDateRangePicker**: Date range selection component with quick select options
- **TRIncomeExpenseChart**: Line chart comparing income vs expenses over time
- **TRCategoryBreakdownTable**: Table showing category-based spending/income distribution
- **Reports API endpoints**: Backend routes for fetching report data and CSV export
- **Reports service**: Business logic for aggregating financial data
- **useReports hook**: Frontend data fetching and state management

## Technical Implementation

### Files Modified

- `apps/Client/src/App.tsx`: Added ReportsPage route import
- `apps/Client/src/types/index.ts`: Added report-related TypeScript interfaces
- `apps/Server/main.py`: Registered reports router

### New Files

**Backend:**
- `apps/Server/src/adapter/rest/reports_routes.py`: API endpoints for report data and CSV export
- `apps/Server/src/core/services/reports_service.py`: Business logic for report generation
- `apps/Server/src/interface/reports_dto.py`: Pydantic DTOs for report data
- `apps/Server/tests/test_reports.py`: Unit tests for reports functionality

**Frontend:**
- `apps/Client/src/pages/ReportsPage.tsx`: Main reports page component
- `apps/Client/src/services/reportService.ts`: API client for reports
- `apps/Client/src/hooks/useReports.ts`: Data fetching hook
- `apps/Client/src/components/ui/TRReportDateRangePicker.tsx`: Date range picker
- `apps/Client/src/components/ui/TRIncomeExpenseChart.tsx`: Income vs expense chart
- `apps/Client/src/components/ui/TRCategoryBreakdownTable.tsx`: Category breakdown table

### Key Changes

- **Monthly income/expense comparison**: Aggregates transactions by month using SQLAlchemy's `extract` function with GROUP BY year/month
- **Category breakdown with percentages**: Calculates percentage distribution within each transaction type (income/expense)
- **CSV export via StreamingResponse**: Memory-efficient CSV generation using Python's built-in csv module
- **Quick select date ranges**: Predefined options for This Month, Last 3/6 Months, and This Year
- **Blob-based file download**: Frontend handles CSV download via blob response and dynamic anchor creation

## How to Use

1. Navigate to `/reports` in the application (requires authentication)
2. Select a date range using the quick select buttons or custom date inputs
3. View summary cards showing Total Income, Total Expenses, Net Balance, and Transaction Count
4. Analyze the Income vs Expenses chart for monthly trends
5. Review the Category Breakdown table for spending/income distribution by category
6. Click "Export CSV" to download transaction data for the selected date range

## Configuration

No additional configuration required. The feature uses existing:
- Entity context for filtering by current entity
- JWT authentication for protected endpoints
- Database connection for transaction queries

## API Endpoints

### GET /api/reports/data
Returns complete report data including summary, monthly comparison, and category breakdown.

**Query Parameters:**
- `entity_id` (UUID, required): Entity to generate report for
- `start_date` (date, required): Start of report period
- `end_date` (date, required): End of report period

### GET /api/reports/export/csv
Downloads transactions as CSV file.

**Query Parameters:**
- `entity_id` (UUID, required): Entity to export data for
- `start_date` (date, required): Start of export period
- `end_date` (date, required): End of export period

**CSV Columns:** Date, Type, Category, Amount, Description, Notes

## Testing

**Backend tests:**
```bash
cd apps/Server && uv run pytest tests/test_reports.py -v
```

**Frontend validation:**
```bash
cd apps/Client && npm run typecheck
cd apps/Client && npm run lint
cd apps/Client && npm run build
```

**E2E test:**
See `.claude/commands/e2e/test_reports_export_csv.md` for end-to-end test specification.

## Notes

- Date range defaults to "This Month" on initial page load
- Empty states are displayed when no transactions exist in the selected period
- Category breakdown percentages are calculated separately for income and expense types
- CSV export includes all transactions in date range, sorted by date descending
