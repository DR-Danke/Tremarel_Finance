# Feature: Recurring Transactions

## Metadata
issue_number: `27`
adw_id: `e44986c8`
issue_json: `{"number":27,"title":"[FinanceTracker] Wave 5: Recurring Transactions","body":"..."}`

## Feature Description
Implement recurring transactions functionality that allows users to create transaction templates with recurrence patterns (daily, weekly, monthly, yearly). Users can manage these templates and view which transactions were generated from recurring templates. This feature helps track regular income (like salary) and regular expenses (like subscriptions, rent, utilities) automatically.

The feature consists of:
1. **Recurring Transaction Templates**: Database model and CRUD operations for storing recurring transaction patterns
2. **Recurrence Patterns**: Support for daily, weekly, monthly, and yearly frequencies
3. **Template Management UI**: Frontend page to view, create, edit, and deactivate recurring templates
4. **Transaction Association**: Link generated transactions to their source template for tracking
5. **Visual Indicators**: Show which transactions came from recurring templates in the transaction list

## User Story
As a Finance Tracker user
I want to mark transactions as recurring with a pattern (daily, weekly, monthly, yearly)
So that I can easily track regular income like salary or regular expenses like subscriptions without manually creating each transaction

## Problem Statement
Users with regular recurring financial activities (salary payments, rent, subscriptions, loan payments) must manually create the same transaction repeatedly. This is time-consuming, error-prone, and makes it difficult to distinguish regular predictable transactions from one-time transactions.

## Solution Statement
Create a recurring transaction template system that:
1. Stores transaction templates with recurrence patterns (frequency and next occurrence date)
2. Allows users to manage (create, view, edit, deactivate) recurring templates
3. Links generated transactions to their source template via a `recurring_template_id` field
4. Displays visual indicators in the transaction list showing which transactions are from recurring templates
5. Provides a dedicated page for managing all recurring transaction templates

## Relevant Files
Use these files to implement the feature:

### Backend Files
- `apps/Server/database/schema.sql` - Add new `recurring_templates` table and modify `transactions` table with `recurring_template_id` column
- `apps/Server/src/models/transaction.py` - Add `recurring_template_id` field to Transaction model
- `apps/Server/src/interface/transaction_dto.py` - Update DTOs to include `recurring_template_id`
- `apps/Server/src/repository/transaction_repository.py` - Reference for repository pattern
- `apps/Server/src/core/services/transaction_service.py` - Reference for service layer pattern
- `apps/Server/src/adapter/rest/transaction_routes.py` - Reference for API route patterns
- `apps/Server/main.py` - Register new recurring template router
- `apps/Server/tests/test_transactions.py` - Reference for test patterns

### Frontend Files
- `apps/Client/src/types/index.ts` - Add RecurringTemplate types
- `apps/Client/src/App.tsx` - Add route for recurring templates page
- `apps/Client/src/services/transactionService.ts` - Reference for service pattern
- `apps/Client/src/pages/TransactionsPage.tsx` - Reference for page patterns, update to show recurring indicators
- `apps/Client/src/hooks/useTransactions.ts` - Reference for hook patterns
- `apps/Client/src/components/forms/TRTransactionForm.tsx` - Reference for form patterns
- `apps/Client/src/components/ui/TRTransactionTable.tsx` - Update to show recurring template indicator
- `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx` - Add navigation item for recurring templates

### Documentation Files
- `.claude/commands/test_e2e.md` - Understand E2E test execution process
- `.claude/commands/e2e/test_transaction_crud.md` - Reference for E2E test format

### New Files
- `apps/Server/src/models/recurring_template.py` - SQLAlchemy model for recurring templates
- `apps/Server/src/interface/recurring_template_dto.py` - Pydantic DTOs for recurring templates
- `apps/Server/src/repository/recurring_template_repository.py` - Data access layer for recurring templates
- `apps/Server/src/core/services/recurring_template_service.py` - Business logic for recurring templates
- `apps/Server/src/adapter/rest/recurring_template_routes.py` - REST API endpoints for recurring templates
- `apps/Server/tests/test_recurring_templates.py` - Unit tests for recurring templates
- `apps/Client/src/services/recurringTemplateService.ts` - API client for recurring templates
- `apps/Client/src/pages/RecurringTemplatesPage.tsx` - Page component for managing recurring templates
- `apps/Client/src/hooks/useRecurringTemplates.ts` - State management hook for recurring templates
- `apps/Client/src/components/forms/TRRecurringTemplateForm.tsx` - Form for creating/editing templates
- `apps/Client/src/components/ui/TRRecurringTemplateTable.tsx` - Table for displaying templates
- `.claude/commands/e2e/test_recurring_transactions.md` - E2E test for recurring transactions feature

## Implementation Plan

### Phase 1: Foundation (Database & Backend Models)
1. Design and create the `recurring_templates` database table with fields for recurrence pattern storage
2. Add `recurring_template_id` nullable foreign key to `transactions` table
3. Create SQLAlchemy RecurringTemplate model
4. Create Pydantic DTOs for recurring template CRUD operations

### Phase 2: Core Implementation (Backend Services)
1. Implement RecurringTemplateRepository with CRUD operations
2. Implement RecurringTemplateService with business logic
3. Create REST API endpoints for recurring template management
4. Update Transaction model and DTOs to include recurring template reference
5. Write comprehensive unit tests for all new backend components

### Phase 3: Integration (Frontend Implementation)
1. Add TypeScript types for recurring templates
2. Create recurringTemplateService for API communication
3. Implement useRecurringTemplates hook for state management
4. Create TRRecurringTemplateForm component
5. Create TRRecurringTemplateTable component
6. Create RecurringTemplatesPage
7. Update TRTransactionTable to show recurring indicator
8. Add navigation item to sidebar
9. Add route in App.tsx
10. Create E2E test specification

## Step by Step Tasks

### Step 1: Create E2E Test Specification
- Create `.claude/commands/e2e/test_recurring_transactions.md` with test steps for the recurring transactions feature
- Include tests for creating, viewing, editing, and deactivating recurring templates
- Include tests for verifying recurring indicator on transactions

### Step 2: Update Database Schema
- Add SQL for `recurring_templates` table with columns: `id`, `entity_id`, `category_id`, `name`, `amount`, `type`, `description`, `notes`, `frequency` (daily/weekly/monthly/yearly), `start_date`, `end_date` (optional), `is_active`, `created_at`, `updated_at`
- Add `recurring_template_id` nullable foreign key column to `transactions` table
- Add appropriate indexes and constraints

### Step 3: Create Backend Recurring Template Model
- Create `apps/Server/src/models/recurring_template.py` with SQLAlchemy RecurringTemplate model
- Follow patterns from existing Transaction model
- Include proper type hints and docstrings

### Step 4: Create Backend Recurring Template DTOs
- Create `apps/Server/src/interface/recurring_template_dto.py` with Pydantic models:
  - `RecurringTemplateCreateDTO`
  - `RecurringTemplateUpdateDTO`
  - `RecurringTemplateResponseDTO`
  - `RecurringTemplateListResponseDTO`
- Follow patterns from transaction_dto.py

### Step 5: Create Backend Recurring Template Repository
- Create `apps/Server/src/repository/recurring_template_repository.py`
- Implement CRUD operations: create, get_by_id, get_by_entity, update, delete
- Follow patterns from transaction_repository.py
- Include logging statements

### Step 6: Create Backend Recurring Template Service
- Create `apps/Server/src/core/services/recurring_template_service.py`
- Implement business logic for CRUD operations
- Include entity ownership validation
- Follow patterns from transaction_service.py

### Step 7: Create Backend Recurring Template Routes
- Create `apps/Server/src/adapter/rest/recurring_template_routes.py`
- Implement endpoints: POST /, GET /, GET /{id}, PUT /{id}, DELETE /{id}
- Follow patterns from transaction_routes.py
- Apply authentication and RBAC (delete restricted to admin/manager)

### Step 8: Update Transaction Model and DTOs
- Add `recurring_template_id` optional field to `apps/Server/src/models/transaction.py`
- Update `apps/Server/src/interface/transaction_dto.py` DTOs to include `recurring_template_id`

### Step 9: Register Router and Run Backend Tests
- Register recurring template router in `apps/Server/main.py`
- Create `apps/Server/tests/test_recurring_templates.py` with comprehensive unit tests
- Run `cd Server && uv run pytest` to verify all backend tests pass

### Step 10: Add Frontend TypeScript Types
- Update `apps/Client/src/types/index.ts` with:
  - `RecurrenceFrequency` type ('daily' | 'weekly' | 'monthly' | 'yearly')
  - `RecurringTemplate` interface
  - `RecurringTemplateCreate` interface
  - `RecurringTemplateUpdate` interface
  - `RecurringTemplateListResponse` interface
- Add `recurring_template_id` to Transaction interface

### Step 11: Create Frontend Recurring Template Service
- Create `apps/Client/src/services/recurringTemplateService.ts`
- Implement API client methods: create, list, get, update, delete
- Follow patterns from transactionService.ts

### Step 12: Create Frontend useRecurringTemplates Hook
- Create `apps/Client/src/hooks/useRecurringTemplates.ts`
- Implement state management for recurring templates
- Follow patterns from useTransactions.ts

### Step 13: Create TRRecurringTemplateForm Component
- Create `apps/Client/src/components/forms/TRRecurringTemplateForm.tsx`
- Include fields: name, amount, type, category, frequency, start_date, end_date (optional), description, notes
- Use react-hook-form with Material-UI
- Follow patterns from TRTransactionForm.tsx

### Step 14: Create TRRecurringTemplateTable Component
- Create `apps/Client/src/components/ui/TRRecurringTemplateTable.tsx`
- Display template name, amount, type, frequency, start date, status, actions
- Include edit and deactivate/delete actions
- Follow patterns from TRTransactionTable.tsx

### Step 15: Create RecurringTemplatesPage
- Create `apps/Client/src/pages/RecurringTemplatesPage.tsx`
- Include list view with table
- Include dialogs for create/edit
- Follow patterns from TransactionsPage.tsx

### Step 16: Update TRTransactionTable
- Modify `apps/Client/src/components/ui/TRTransactionTable.tsx` to show recurring indicator
- Add icon/chip for transactions with `recurring_template_id`
- Show tooltip with template name on hover if possible

### Step 17: Update Navigation and Routing
- Add "Recurring" navigation item to `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`
- Add route for `/recurring` in `apps/Client/src/App.tsx`

### Step 18: Run Frontend Type Check and Build
- Run `cd Client && npm run typecheck` to verify TypeScript types
- Run `cd Client && npm run build` to verify build succeeds

### Step 19: Run Validation Commands
- Run `cd Server && uv run pytest` to verify all backend tests pass
- Run `cd Client && npm run typecheck` to verify TypeScript compilation
- Run `cd Client && npm run build` to verify production build
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_recurring_transactions.md` to validate E2E functionality

## Testing Strategy

### Unit Tests
- **RecurringTemplate CRUD**: Test create, read, update, delete operations
- **Validation**: Test invalid frequency values, negative amounts, missing required fields
- **Authorization**: Test unauthenticated access returns 401
- **RBAC**: Test delete restricted to admin/manager roles
- **Entity Ownership**: Test templates are scoped to correct entity
- **Transaction Link**: Test transactions can reference recurring templates

### Edge Cases
- Creating template with end_date before start_date (should fail validation)
- Creating template with invalid frequency value (should return 422)
- Deleting template that has associated transactions (should soft-delete/deactivate only)
- Updating template frequency after transactions generated
- Viewing templates for entity user doesn't have access to (should return 403 or empty)
- Empty template list for new entity

## Acceptance Criteria
- Users can create recurring transaction templates with daily/weekly/monthly/yearly frequency
- Users can view a list of all recurring templates for their current entity
- Users can edit existing recurring templates
- Users can deactivate recurring templates (soft delete)
- Admins/managers can hard-delete recurring templates
- Transaction list displays a visual indicator for transactions from recurring templates
- Sidebar includes navigation link to recurring templates page
- All backend endpoints are protected by authentication
- All new code follows existing Clean Architecture patterns
- All unit tests pass
- Frontend TypeScript compilation succeeds
- Frontend production build succeeds
- E2E test validates the full workflow

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest` - Run Server tests to validate the feature works with zero regressions
- `cd apps/Client && npm run typecheck` - Run Client type check to validate the feature compiles correctly
- `cd apps/Client && npm run build` - Run Client build to validate production build succeeds
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_recurring_transactions.md` to validate this functionality works end-to-end

## Notes
- This feature does NOT implement automatic transaction generation on a schedule. It only provides the template management and tracking infrastructure. Automatic generation could be a future enhancement via a background job.
- The recurring_template_id on transactions allows manual or future automated linking - initially transactions will be created manually but linked to templates
- Consider future enhancements:
  - Background scheduler to auto-generate transactions from templates
  - Dashboard widget showing upcoming recurring transactions
  - Notifications for upcoming recurring expenses
- The `frequency` field uses a simple string enum for clarity. More complex patterns (e.g., "every 2 weeks") could be added later
- Soft delete (is_active=false) is preferred over hard delete to maintain transaction history integrity
