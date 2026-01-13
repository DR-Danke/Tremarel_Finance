# Feature: Dashboard with Summary Stats and Charts

## Metadata
issue_number: `23`
adw_id: `7fcd6a6a`
issue_json: `{"number":23,"title":"[FinanceTracker] Wave 4: Dashboard with Summary Stats","body":"..."}`

## Feature Description
This feature transforms the existing placeholder Dashboard page into a fully functional financial summary dashboard for the Finance Tracker application. The dashboard displays key financial metrics (total income, total expenses, net balance) for the current month, visualizes income vs expense trends over the last 6 months using a line chart, shows expense breakdown by category using a pie chart, and provides quick action buttons for adding new transactions.

## User Story
As a Finance Tracker user
I want to see a visual summary of my financial data on the dashboard
So that I can quickly understand my financial health and take action

## Problem Statement
Currently, the DashboardPage is a placeholder that only displays user information and entity selection. Users have no way to get a quick overview of their financial status for the current entity. They must navigate to the Transactions page to see any data, which doesn't provide aggregated views or visual trends.

## Solution Statement
Replace the placeholder DashboardPage with a comprehensive financial dashboard that:
1. Creates a new backend endpoint for dashboard statistics aggregation (GET `/api/dashboard/stats`)
2. Displays three stat cards showing current month totals: Total Income, Total Expenses, Net Balance
3. Shows a line chart (Recharts) comparing income vs expenses over the last 6 months
4. Shows a pie chart (Recharts) breaking down expenses by category for the current month
5. Provides quick action buttons to navigate to Add Transaction functionality
6. All data is filtered by the currently selected entity from EntityContext

## Relevant Files
Use these files to implement the feature:

### Existing Backend Files to Reference
- `apps/Server/src/adapter/rest/transaction_routes.py` - Reference for API endpoint patterns, authentication, and entity filtering
- `apps/Server/src/core/services/transaction_service.py` - Reference for service layer patterns
- `apps/Server/src/repository/transaction_repository.py` - Reference for repository patterns and queries
- `apps/Server/src/interface/transaction_dto.py` - Reference for Pydantic DTO patterns
- `apps/Server/main.py` - Register new dashboard router here

### Existing Frontend Files to Reference/Modify
- `apps/Client/src/pages/DashboardPage.tsx` - **MODIFY**: Transform placeholder into full dashboard
- `apps/Client/src/services/transactionService.ts` - Reference for service patterns
- `apps/Client/src/services/categoryService.ts` - Reference for service patterns
- `apps/Client/src/types/index.ts` - **MODIFY**: Add dashboard-related types
- `apps/Client/src/hooks/useEntity.ts` - Use for getting currentEntity.id
- `apps/Client/src/hooks/useTransactions.ts` - Reference for hook patterns
- `apps/Client/package.json` - Already has Recharts ^2.10.0 installed

### Documentation Files
- `.claude/commands/test_e2e.md` - Instructions for E2E test execution
- `.claude/commands/e2e/test_transaction_crud.md` - Reference for E2E test format

### New Files
- `apps/Server/src/adapter/rest/dashboard_routes.py` - New REST API endpoints for dashboard
- `apps/Server/src/core/services/dashboard_service.py` - New service for dashboard aggregations
- `apps/Server/src/interface/dashboard_dto.py` - New DTOs for dashboard responses
- `apps/Server/tests/test_dashboard.py` - Unit tests for dashboard service and routes
- `apps/Client/src/services/dashboardService.ts` - New API client for dashboard endpoints
- `apps/Client/src/hooks/useDashboard.ts` - New hook for dashboard state management
- `apps/Client/src/components/ui/TRStatCard.tsx` - New reusable stat card component
- `apps/Client/src/components/ui/TRMonthlyTrendChart.tsx` - New line chart component
- `apps/Client/src/components/ui/TRExpenseBreakdownChart.tsx` - New pie chart component
- `.claude/commands/e2e/test_servicedesk_dashboard.md` - Already exists, create new one for Finance Tracker
- `.claude/commands/e2e/test_dashboard_summary_stats.md` - New E2E test specification

## Implementation Plan

### Phase 1: Foundation - Backend Dashboard API
Create the backend infrastructure to aggregate and serve dashboard statistics:
1. Create Pydantic DTOs for dashboard response data structures
2. Create dashboard service with aggregation logic (monthly totals, 6-month trends, category breakdown)
3. Create REST API endpoint at `/api/dashboard/stats` that accepts entity_id parameter
4. Register router in main.py
5. Write unit tests for service and routes

### Phase 2: Core Implementation - Frontend Dashboard
Build the frontend components and integrate with the API:
1. Add TypeScript types for dashboard data structures
2. Create dashboardService API client
3. Create useDashboard hook for state management
4. Create TRStatCard component for displaying metrics
5. Create TRMonthlyTrendChart component using Recharts LineChart
6. Create TRExpenseBreakdownChart component using Recharts PieChart
7. Transform DashboardPage to compose all components

### Phase 3: Integration - Polish and Navigation
Complete the integration and add navigation shortcuts:
1. Add quick action button to navigate to Transactions with "Add" mode
2. Handle loading and error states gracefully
3. Handle empty data states (no transactions yet)
4. Ensure responsive layout for different screen sizes

## Step by Step Tasks

### Step 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_transaction_crud.md` to understand the E2E test format
- Create `.claude/commands/e2e/test_dashboard_summary_stats.md` with test steps for:
  - Navigating to dashboard after login
  - Verifying stat cards display (Total Income, Total Expenses, Net Balance)
  - Verifying line chart displays 6-month trend
  - Verifying pie chart displays expense breakdown
  - Testing quick action button to add transaction
  - Testing empty state when no transactions exist

### Step 2: Create Backend DTOs
- Create `apps/Server/src/interface/dashboard_dto.py` with:
  - `DashboardStatsResponseDTO` - main response containing all dashboard data
  - `MonthlyTotalDTO` - monthly income/expense totals for trend chart
  - `CategoryBreakdownDTO` - category name, amount, and percentage for pie chart
  - `CurrentMonthSummaryDTO` - total_income, total_expenses, net_balance

### Step 3: Create Backend Dashboard Service
- Create `apps/Server/src/core/services/dashboard_service.py` with:
  - `get_current_month_summary(db, entity_id)` - aggregate income/expenses for current month
  - `get_monthly_trends(db, entity_id, months=6)` - aggregate by month for last N months
  - `get_expense_breakdown(db, entity_id)` - group expenses by category for current month
  - Use SQLAlchemy queries with date filtering and aggregation (SUM, GROUP BY)
  - Add proper logging with INFO prefix pattern

### Step 4: Create Backend Dashboard Routes
- Create `apps/Server/src/adapter/rest/dashboard_routes.py` with:
  - `GET /api/dashboard/stats?entity_id={uuid}` - returns DashboardStatsResponseDTO
  - Use `get_current_user` dependency for authentication
  - Add proper logging with INFO prefix pattern
- Register router in `apps/Server/main.py`

### Step 5: Create Backend Unit Tests
- Create `apps/Server/tests/test_dashboard.py` with tests for:
  - Dashboard stats with valid entity_id
  - Dashboard stats with no transactions (empty state)
  - Dashboard stats with only income transactions
  - Dashboard stats with only expense transactions
  - Unauthorized access (no token)
  - Multiple months of data for trend chart

### Step 6: Add Frontend Types
- Update `apps/Client/src/types/index.ts` with:
  - `DashboardStats` interface
  - `MonthlyTotal` interface
  - `CategoryBreakdown` interface
  - `CurrentMonthSummary` interface

### Step 7: Create Frontend Dashboard Service
- Create `apps/Client/src/services/dashboardService.ts` with:
  - `getStats(entityId: string): Promise<DashboardStats>` method
  - Use apiClient with proper error handling
  - Add INFO logging matching project patterns

### Step 8: Create useDashboard Hook
- Create `apps/Client/src/hooks/useDashboard.ts` with:
  - State: stats, isLoading, error
  - Effect to fetch stats when entityId changes
  - Refresh function for manual reload
  - Use EntityContext to get currentEntity.id

### Step 9: Create TRStatCard Component
- Create `apps/Client/src/components/ui/TRStatCard.tsx` with:
  - Props: title, value, subtitle, icon, color, trend (optional)
  - Use MUI Paper, Typography, Box for layout
  - Display formatted currency value
  - Use MUI icons (TrendingUp, TrendingDown, AccountBalance)
  - Color coding: green for income, red for expense, blue for net

### Step 10: Create TRMonthlyTrendChart Component
- Create `apps/Client/src/components/ui/TRMonthlyTrendChart.tsx` with:
  - Props: data (MonthlyTotal[])
  - Use Recharts LineChart with ResponsiveContainer
  - Two lines: income (green) and expense (red)
  - X-axis: month names (Jan, Feb, etc.)
  - Y-axis: currency values with formatter
  - Tooltip showing exact values
  - Legend showing income/expense labels
  - Handle empty data with appropriate message

### Step 11: Create TRExpenseBreakdownChart Component
- Create `apps/Client/src/components/ui/TRExpenseBreakdownChart.tsx` with:
  - Props: data (CategoryBreakdown[])
  - Use Recharts PieChart with ResponsiveContainer
  - Show category names and percentages
  - Use color palette for segments
  - Tooltip showing category name, amount, percentage
  - Legend with category names
  - Handle empty data with appropriate message

### Step 12: Transform DashboardPage
- Update `apps/Client/src/pages/DashboardPage.tsx`:
  - Import useDashboard, TRStatCard, TRMonthlyTrendChart, TRExpenseBreakdownChart
  - Remove placeholder "Dashboard features coming soon" content
  - Keep user welcome section and entity info
  - Add Grid layout with three TRStatCard components (Income, Expenses, Net Balance)
  - Add TRMonthlyTrendChart below stat cards
  - Add TRExpenseBreakdownChart next to or below line chart
  - Add "Add Transaction" quick action button (links to /transactions)
  - Handle loading state with MUI Skeleton or CircularProgress
  - Handle error state with error message
  - Handle empty state (no transactions) with appropriate message

### Step 13: Run Validation Commands
- Execute all validation commands to ensure zero regressions
- Fix any TypeScript errors, lint errors, or test failures

## Testing Strategy

### Unit Tests
- **Backend Service Tests**: Test aggregation logic with various data scenarios
  - Empty transactions
  - Only income transactions
  - Only expense transactions
  - Mixed transactions across multiple months
  - Single category vs multiple categories
- **Backend Route Tests**: Test API endpoint responses and error handling
  - Valid requests with authentication
  - Missing entity_id parameter
  - Unauthorized requests

### Edge Cases
- No transactions exist for the entity
- Transactions exist but all are from previous months (empty current month)
- Only income transactions (no expense breakdown to show)
- Only expense transactions (zero income stat)
- Single transaction in one category
- Large numbers (ensure proper formatting)
- Negative net balance display

## Acceptance Criteria
1. Dashboard displays three stat cards: Total Income, Total Expenses, Net Balance for current month
2. Stat cards show properly formatted currency values with $ symbol and commas
3. Line chart shows income vs expense trends for the last 6 months
4. Pie chart shows expense breakdown by category for the current month
5. Quick action button navigates to transaction creation
6. Dashboard updates when entity is switched via EntityContext
7. Loading state is displayed while fetching data
8. Empty state is displayed when no transactions exist
9. Error state is displayed when API call fails
10. All data is filtered by the current entity_id
11. Backend tests pass with >80% coverage for new code
12. Frontend builds without TypeScript errors
13. Frontend lint passes without warnings

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest tests/test_dashboard.py -v` - Run new dashboard tests
- `cd apps/Server && uv run pytest` - Run all Server tests to validate zero regressions
- `cd apps/Client && npm run typecheck` - Run Client type check
- `cd apps/Client && npm run lint` - Run Client lint check
- `cd apps/Client && npm run build` - Run Client build to validate production-ready

Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_dashboard_summary_stats.md` to validate the dashboard functionality works end-to-end.

## Notes
- Recharts is already installed (^2.10.0) in package.json
- The dashboard is the only feature in Wave 4, running sequentially after Wave 3 CRUD completion
- This dashboard integrates data from both transactions and categories built in Wave 3
- Consider caching dashboard stats on the frontend to reduce API calls when switching between pages
- The monthly trend chart should handle cases where some months have no data (show 0)
- Category breakdown pie chart should only show expense categories (not income)
- Future enhancement: Add date range picker to customize dashboard view period
- Future enhancement: Add comparison with previous period (MoM change indicators)
