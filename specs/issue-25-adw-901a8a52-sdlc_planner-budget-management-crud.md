# Feature: Budget Management CRUD

## Metadata
issue_number: `25`
adw_id: `901a8a52`
issue_json: `{"number":25,"title":"[FinanceTracker] Wave 5: Budget Management","body":"..."}`

## Feature Description
Implement a complete budget management system that allows users to set spending limits per category or overall for their financial entities. The feature includes backend CRUD operations for budgets, a frontend Budgets page with visual progress indicators, and spending tracking that compares actual expenses against budget amounts. Budgets support multiple period types: monthly, quarterly, and yearly.

Key capabilities:
- Create budgets linked to specific categories within an entity
- Support for monthly, quarterly, and yearly budget periods
- Visual progress bars showing spending vs. budget amount
- Warning indicators when approaching (>75%) or exceeding (>100%) budget limits
- Full CRUD operations with edit and delete functionality
- Integration with transaction data to calculate actual spending

## User Story
As a Finance Tracker user
I want to set spending limits per category and track my progress against them
So that I can manage my finances and stay within my spending goals

## Problem Statement
Users currently have no way to set financial targets or limits for their spending. Without budget management, they cannot:
- Define spending limits for specific expense categories
- Track whether they are staying within their financial goals
- Get warnings when they are approaching or exceeding their budgets
- Plan their finances across different time periods (monthly, quarterly, yearly)

## Solution Statement
Implement a full budget management system with:
1. Backend API endpoints for budget CRUD operations following Clean Architecture
2. Budget repository and service layers for data access and business logic
3. Spending calculation that aggregates transactions within budget periods
4. Frontend Budgets page with list view, progress bars, and status indicators
5. Form component for creating and editing budgets with validation
6. Visual feedback using color-coded progress bars and warning alerts

## Relevant Files
Use these files to implement the feature:

### Backend - Reference Files (patterns to follow)
- `apps/Server/main.py` - Entry point, router registration pattern
- `apps/Server/database/schema.sql` - Budgets table definition (already exists)
- `apps/Server/src/models/transaction.py` - SQLAlchemy model pattern
- `apps/Server/src/interface/transaction_dto.py` - Pydantic DTO pattern
- `apps/Server/src/repository/transaction_repository.py` - Repository pattern
- `apps/Server/src/core/services/transaction_service.py` - Service pattern
- `apps/Server/src/adapter/rest/transaction_routes.py` - Route pattern
- `apps/Server/src/adapter/rest/dependencies.py` - Auth dependencies
- `apps/Server/src/adapter/rest/rbac_dependencies.py` - Role-based access

### Frontend - Reference Files (patterns to follow)
- `apps/Client/src/App.tsx` - Route registration, placeholder page exists
- `apps/Client/src/types/index.ts` - TypeScript types
- `apps/Client/src/services/transactionService.ts` - Service pattern
- `apps/Client/src/hooks/useTransactions.ts` - Hook pattern
- `apps/Client/src/pages/TransactionsPage.tsx` - Page pattern with dialogs
- `apps/Client/src/components/forms/TRTransactionForm.tsx` - Form component pattern
- `apps/Client/src/components/ui/TRStatCard.tsx` - UI card component

### E2E Test References
- `.claude/commands/test_e2e.md` - E2E test runner documentation
- `.claude/commands/e2e/test_category_management.md` - E2E test pattern example

### New Files
**Backend:**
- `apps/Server/src/models/budget.py` - SQLAlchemy Budget model
- `apps/Server/src/interface/budget_dto.py` - Pydantic DTOs for budgets
- `apps/Server/src/repository/budget_repository.py` - Budget data access layer
- `apps/Server/src/core/services/budget_service.py` - Budget business logic
- `apps/Server/src/adapter/rest/budget_routes.py` - Budget REST API endpoints
- `apps/Server/tests/test_budgets.py` - Backend unit tests

**Frontend:**
- `apps/Client/src/services/budgetService.ts` - Budget API client
- `apps/Client/src/hooks/useBudgets.ts` - Budget state management hook
- `apps/Client/src/components/forms/TRBudgetForm.tsx` - Budget form component
- `apps/Client/src/components/ui/TRBudgetCard.tsx` - Budget card with progress bar
- `apps/Client/src/pages/BudgetsPage.tsx` - Main budgets page (replace placeholder)

**E2E Test:**
- `.claude/commands/e2e/test_budget_management.md` - E2E test specification

## Implementation Plan

### Phase 1: Foundation
Set up the backend infrastructure with model, DTOs, repository, and service layers:
1. Create SQLAlchemy Budget model matching the schema
2. Define Pydantic DTOs for create, update, response, and list operations
3. Implement repository with CRUD operations and spending calculation
4. Create service layer with business logic and validation

### Phase 2: Core Implementation
Build the REST API endpoints and frontend components:
1. Implement budget routes with full CRUD endpoints
2. Add spending calculation endpoint to compare actual vs budget
3. Create frontend service, hook, and form components
4. Build budget card component with progress bar visualization

### Phase 3: Integration
Connect all pieces and add visual feedback:
1. Register budget router in main.py
2. Update App.tsx with proper BudgetsPage routing
3. Implement BudgetsPage with list, add, edit, delete dialogs
4. Add color-coded progress indicators (green < 75%, yellow 75-100%, red > 100%)
5. Create and execute E2E tests

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Task 1: Create E2E Test Specification
Create the E2E test file for budget management before implementation to define acceptance criteria.

- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_category_management.md` to understand E2E test format
- Create `.claude/commands/e2e/test_budget_management.md` with:
  - User story for budget management
  - Prerequisites (server running, test user, entity with expense categories and transactions)
  - Test steps for: navigating to budgets, creating monthly/yearly budgets, viewing progress bars, editing budgets, deleting budgets
  - Success criteria including visual progress indicators
  - Technical verification for API calls

### Task 2: Create Backend Budget Model
Create the SQLAlchemy model for budgets.

- Create `apps/Server/src/models/budget.py` following `transaction.py` pattern
- Define Budget class with fields: id, entity_id, category_id, amount, period_type, start_date, end_date, is_active, created_at, updated_at
- Add UUID primary key, foreign keys to entities and categories
- Add relationship back-references

### Task 3: Create Budget DTOs
Create Pydantic DTOs for budget operations.

- Create `apps/Server/src/interface/budget_dto.py`
- Define BudgetCreateDTO with: entity_id, category_id, amount (Decimal > 0), period_type (monthly/quarterly/yearly), start_date
- Define BudgetUpdateDTO with optional fields: amount, period_type, start_date, is_active
- Define BudgetResponseDTO with all fields including calculated spending and percentage
- Define BudgetListResponseDTO with list of budgets and total count
- Define BudgetWithSpendingDTO to include actual spending amount and percentage

### Task 4: Create Budget Repository
Create the data access layer for budgets.

- Create `apps/Server/src/repository/budget_repository.py` following `transaction_repository.py` pattern
- Implement create_budget method
- Implement get_budget_by_id method
- Implement get_budgets_by_entity method with optional category filter
- Implement update_budget method
- Implement delete_budget method
- Implement calculate_spending method that sums transactions within budget period
- Add proper logging with print statements

### Task 5: Create Budget Service
Create the business logic layer for budgets.

- Create `apps/Server/src/core/services/budget_service.py` following `transaction_service.py` pattern
- Implement create_budget with validation (category must be expense type, no duplicate active budgets)
- Implement get_budget with entity ownership validation
- Implement list_budgets for an entity
- Implement get_budgets_with_spending to return budgets with calculated actual spending
- Implement update_budget with entity ownership validation
- Implement delete_budget with entity ownership validation
- Calculate budget date ranges based on period_type and start_date

### Task 6: Create Budget Routes
Create the REST API endpoints for budgets.

- Create `apps/Server/src/adapter/rest/budget_routes.py` following `transaction_routes.py` pattern
- POST `/api/budgets/` - Create budget (authenticated)
- GET `/api/budgets/` - List budgets with spending for entity (requires entity_id query param)
- GET `/api/budgets/{budget_id}` - Get single budget with spending
- PUT `/api/budgets/{budget_id}` - Update budget
- DELETE `/api/budgets/{budget_id}` - Delete budget (admin/manager only)
- Add proper error handling and logging

### Task 7: Register Budget Router
Register the budget router in main.py.

- Import budget router in `apps/Server/main.py`
- Add `app.include_router(budget_router)` after other routers
- Add logging statement for budget router registration

### Task 8: Create Backend Tests
Create comprehensive unit tests for budget functionality.

- Create `apps/Server/tests/test_budgets.py`
- Test create budget (valid, invalid amount, duplicate active)
- Test get budgets by entity
- Test get budget with spending calculation
- Test update budget
- Test delete budget (success and role validation)
- Test spending calculation across date ranges
- Mock database session and dependencies

### Task 9: Add Frontend Budget Types
Add TypeScript types for budgets.

- Update `apps/Client/src/types/index.ts` with:
  - BudgetPeriodType = 'monthly' | 'quarterly' | 'yearly'
  - Budget interface matching BudgetResponseDTO
  - BudgetWithSpending interface including spent amount and percentage
  - BudgetCreate interface
  - BudgetUpdate interface
  - BudgetListResponse interface

### Task 10: Create Budget Service
Create the frontend API client for budgets.

- Create `apps/Client/src/services/budgetService.ts` following `transactionService.ts` pattern
- Implement create(data: BudgetCreate): Promise<Budget>
- Implement list(entityId: string): Promise<BudgetListResponse>
- Implement get(budgetId: string, entityId: string): Promise<BudgetWithSpending>
- Implement update(budgetId: string, entityId: string, data: BudgetUpdate): Promise<Budget>
- Implement delete(budgetId: string, entityId: string): Promise<void>
- Add proper console logging

### Task 11: Create useBudgets Hook
Create the state management hook for budgets.

- Create `apps/Client/src/hooks/useBudgets.ts` following `useTransactions.ts` pattern
- Manage budgets state array with spending data
- Implement fetchBudgets, createBudget, updateBudget, deleteBudget
- Handle loading and error states
- Auto-fetch on entityId change

### Task 12: Create TRBudgetForm Component
Create the form component for budget creation and editing.

- Create `apps/Client/src/components/forms/TRBudgetForm.tsx` following `TRTransactionForm.tsx` pattern
- Use react-hook-form with Controller for select fields
- Category select (filtered to expense categories only)
- Amount input with validation (> 0, currency format)
- Period type select (Monthly, Quarterly, Yearly)
- Start date input
- Submit and Cancel buttons
- Handle edit mode with pre-filled values
- Display loading state during submission

### Task 13: Create TRBudgetCard Component
Create the budget card component with progress visualization.

- Create `apps/Client/src/components/ui/TRBudgetCard.tsx`
- Display category name, budget amount, period type
- Show LinearProgress bar with percentage of budget spent
- Color code progress: green (<75%), yellow (75-100%), red (>100%)
- Display spent amount / budget amount text
- Show warning icon/alert when over budget
- Include edit and delete action buttons
- Format currency and percentage values

### Task 14: Update BudgetsPage
Replace the placeholder with the full implementation.

- Update `apps/Client/src/App.tsx` BudgetsPage function with full implementation
- OR create `apps/Client/src/pages/BudgetsPage.tsx` and import it
- Use useBudgets hook for state management
- Display list of TRBudgetCard components
- Add "Add Budget" button
- Implement add/edit/delete dialogs similar to TransactionsPage
- Show summary stats (total budgeted, total spent, under/over count)
- Handle empty state with helpful message
- Filter by period type optionally

### Task 15: Run Backend Tests
Execute and verify all backend tests pass.

- Run `cd apps/Server && uv run pytest tests/test_budgets.py -v`
- Fix any failing tests
- Ensure all budget CRUD operations work correctly

### Task 16: Run Frontend Type Check and Build
Verify frontend compiles without errors.

- Run `cd apps/Client && npm run typecheck`
- Run `cd apps/Client && npm run lint`
- Run `cd apps/Client && npm run build`
- Fix any TypeScript or lint errors

### Task 17: Run Full Test Suite
Execute all validation commands to ensure zero regressions.

- Run `cd apps/Server && uv run pytest` to run all backend tests
- Run `cd apps/Client && npm run tsc --noEmit` for type checking
- Run `cd apps/Client && npm run build` for production build
- Read `.claude/commands/test_e2e.md`, then execute `.claude/commands/e2e/test_budget_management.md` E2E test

## Testing Strategy

### Unit Tests
- Budget creation validation (amount > 0, valid period type, valid category)
- Duplicate budget prevention (same entity, category, period, overlapping dates)
- Spending calculation accuracy across date ranges
- Update operations preserve unmodified fields
- Delete restrictions based on user role
- Entity ownership validation on all operations

### Edge Cases
- Creating budget for category with no transactions (0% spent)
- Budget exceeding 100% (spending > budget amount)
- Exactly at 100% spending
- Budget periods that span year boundaries
- Inactive budgets should not be included in active list
- Category that was deleted after budget creation

## Acceptance Criteria
- [ ] Backend API supports full CRUD for budgets at `/api/budgets/`
- [ ] Budgets are scoped to entities and linked to expense categories
- [ ] Period types (monthly, quarterly, yearly) correctly calculate date ranges
- [ ] Spending calculation accurately sums transactions within budget period
- [ ] Frontend Budgets page displays all budgets with progress bars
- [ ] Progress bars are color-coded: green (<75%), yellow (75-100%), red (>100%)
- [ ] Users can create new budgets with form validation
- [ ] Users can edit existing budgets
- [ ] Only admin/manager roles can delete budgets
- [ ] Warning indicators appear when approaching or exceeding limits
- [ ] All backend tests pass
- [ ] Frontend compiles without TypeScript errors
- [ ] E2E test validates complete budget workflow

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest tests/test_budgets.py -v` - Run budget-specific tests
- `cd apps/Server && uv run pytest` - Run all Server tests to validate zero regressions
- `cd apps/Client && npm run typecheck` - Run Client type check
- `cd apps/Client && npm run lint` - Run Client linter
- `cd apps/Client && npm run build` - Run Client build to validate no build errors

Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_budget_management.md` E2E test to validate budget management functionality works end-to-end.

## Notes
- The `budgets` table already exists in the database schema (`apps/Server/database/schema.sql`)
- Budgets are restricted to expense categories only (income budgets don't make semantic sense)
- The unique constraint in the schema prevents duplicate budgets for same entity/category/period/start_date
- Period type determines date range calculation:
  - Monthly: start_date to end of that month
  - Quarterly: start_date to end of 3-month period
  - Yearly: start_date to end of 12-month period
- Consider adding a summary dashboard widget in future enhancement (total budget vs total spending)
- Delete operation uses RESTRICT on category FK, so budget must be deleted before category
