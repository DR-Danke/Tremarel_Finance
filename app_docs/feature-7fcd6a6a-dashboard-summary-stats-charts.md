# Dashboard with Summary Stats and Charts

**ADW ID:** 7fcd6a6a
**Date:** 2026-01-13
**Specification:** specs/issue-23-adw-7fcd6a6a-sdlc_planner-dashboard-summary-stats-charts.md

## Overview

This feature transforms the placeholder Dashboard page into a fully functional financial summary dashboard. It displays key financial metrics (total income, total expenses, net balance) for the current month, visualizes income vs expense trends over 6 months using a line chart, and shows expense breakdown by category using a pie chart.

## What Was Built

- Backend API endpoint (`GET /api/dashboard/stats`) for aggregating financial statistics
- Three stat cards showing current month totals (Income, Expenses, Net Balance)
- Line chart showing 6-month income vs expense trends using Recharts
- Pie chart showing expense breakdown by category for the current month
- Quick action buttons for adding transactions and managing categories
- Loading, error, and empty states for better UX

## Technical Implementation

### Files Modified

- `apps/Server/main.py`: Registered dashboard router
- `apps/Server/requirements.txt`: Added python-dateutil dependency
- `apps/Client/src/pages/DashboardPage.tsx`: Transformed from placeholder to full dashboard
- `apps/Client/src/pages/TransactionsPage.tsx`: Minor updates for navigation
- `apps/Client/src/types/index.ts`: Added dashboard-related TypeScript interfaces

### New Backend Files

- `apps/Server/src/interface/dashboard_dto.py`: Pydantic DTOs for dashboard responses
  - `CurrentMonthSummaryDTO`: Total income, expenses, and net balance
  - `MonthlyTotalDTO`: Monthly aggregates for trend chart
  - `CategoryBreakdownDTO`: Category-wise expense breakdown with percentages
  - `DashboardStatsResponseDTO`: Complete dashboard response

- `apps/Server/src/core/services/dashboard_service.py`: Business logic for data aggregation
  - `get_current_month_summary()`: Aggregates income/expenses for current month
  - `get_monthly_trends()`: Generates 6-month income vs expense trends
  - `get_expense_breakdown()`: Groups expenses by category with percentages
  - `get_dashboard_stats()`: Combines all dashboard data

- `apps/Server/src/adapter/rest/dashboard_routes.py`: REST API endpoint
  - `GET /api/dashboard/stats?entity_id={uuid}`: Returns complete dashboard statistics

- `apps/Server/tests/test_dashboard.py`: Comprehensive unit tests (461 lines)

### New Frontend Files

- `apps/Client/src/services/dashboardService.ts`: API client for dashboard endpoint
- `apps/Client/src/hooks/useDashboard.ts`: State management hook for dashboard data
- `apps/Client/src/components/ui/TRStatCard.tsx`: Reusable stat card component with variants (income/expense/balance)
- `apps/Client/src/components/ui/TRMonthlyTrendChart.tsx`: Line chart using Recharts
- `apps/Client/src/components/ui/TRExpenseBreakdownChart.tsx`: Pie chart using Recharts

### Key Changes

- Dashboard service queries transactions table with date filtering and SQL aggregation (SUM, GROUP BY)
- Monthly trends include all 6 months, showing zero for months with no data
- Expense breakdown calculates percentages and includes category colors
- Frontend components use MUI Skeleton for loading states
- Charts are responsive using Recharts ResponsiveContainer
- All data is filtered by the currently selected entity from EntityContext

## How to Use

1. Log in to the application
2. Select an entity from the dropdown (or create one if none exist)
3. Navigate to the Dashboard page (default landing page)
4. View the three stat cards showing current month financial summary:
   - Total Income (green)
   - Total Expenses (red)
   - Net Balance (blue/positive green, negative red)
5. View the 6-month trend line chart comparing income vs expenses
6. View the pie chart showing expense breakdown by category
7. Use quick action buttons to add transactions or manage categories

## Configuration

No additional configuration required. The dashboard uses:
- Existing JWT authentication for protected access
- EntityContext for filtering data by current entity
- Recharts (already installed in package.json as ^2.10.0)

## API Reference

### GET /api/dashboard/stats

**Query Parameters:**
- `entity_id` (required): UUID of the entity to fetch stats for

**Response:**
```json
{
  "current_month_summary": {
    "total_income": "5000.00",
    "total_expenses": "3500.00",
    "net_balance": "1500.00"
  },
  "monthly_trends": [
    {
      "month": "Aug 2025",
      "year": 2025,
      "month_number": 8,
      "income": "4500.00",
      "expenses": "3200.00"
    }
  ],
  "expense_breakdown": [
    {
      "category_id": "uuid",
      "category_name": "Food",
      "amount": "800.00",
      "percentage": 22.9,
      "color": "#FF5722"
    }
  ]
}
```

## Testing

### Backend Tests
```bash
cd apps/Server && uv run pytest tests/test_dashboard.py -v
```

Tests cover:
- Dashboard stats with valid entity_id
- Empty state (no transactions)
- Only income transactions
- Only expense transactions
- Multiple months of data
- Unauthorized access

### E2E Test
```bash
# Run the dashboard E2E test
/test_e2e e2e:test_dashboard_summary_stats
```

## Notes

- The dashboard only shows data for the currently selected entity
- Monthly trends always show 6 months, with zero values for months without transactions
- Expense breakdown only includes expense transactions (not income)
- Category colors are displayed in the pie chart if defined in the category
- Quick action button navigates to /transactions page for adding new transactions
