# Feature: Transaction CRUD Management

## Metadata
issue_number: `17`
adw_id: `bda418fa`
issue_json: `{"number":17,"title":"[FinanceTracker] Wave 3: Transaction Management","body":"```markdown\n## Context\n**Project:** Finance Tracker - Income & Expense Management\n**Overview:** We are building a full-stack income/expense tracking application for family and startup company management. The system includes multi-entity support (family/startup separation), custom JWT authentication, transaction management, budgeting, reporting with charts, and CSV export. Frontend deploys to Vercel, backend to Render, database on Supabase PostgreSQL.\n\n**Current Wave:** Wave 3 of 6 - Layout & Core Features\n**Current Issue:** FT-009 (Issue 9 of 14)\n**Parallel Execution:** YES - This issue runs in parallel with FT-006 (Layout), FT-007 (Entity Management), and FT-008 (Categories). All four are independent features.\n\n**Dependencies:** Requires Wave 2 completion (authentication must be in place).\n**What comes next:** After Wave 3 completes, Wave 4 implements the Dashboard (FT-010).\n\n## Request\nImplement the core transaction functionality for recording income and expenses. Add backend endpoints for transaction CRUD with filtering by date range, category, and type. Create a Transactions page with a form to add transactions (amount, date, category, description, type) and a data table listing all transactions with sorting and filtering. Transactions belong to the current entity.\n```"}`

## Feature Description
This feature implements complete transaction management for the Finance Tracker application. It includes backend CRUD endpoints for transactions with filtering capabilities by date range, category, and transaction type (income/expense). The frontend provides a Transactions page with a data table listing all transactions for the current entity, a form to add new transactions using react-hook-form, and the ability to edit and delete transactions. All transactions are scoped to the current entity.

## User Story
As a Finance Tracker user
I want to add, view, edit, and delete income and expense transactions
So that I can accurately track my financial activity for my family or startup

## Problem Statement
The Finance Tracker application has no way to record or view financial transactions. Users need the ability to:
1. Add new income and expense transactions with amount, date, category, and description
2. View a list of all transactions with sorting and filtering options
3. Edit existing transactions to correct mistakes
4. Delete transactions that are no longer needed
5. Filter transactions by date range, category, and type for analysis

## Solution Statement
Implement a complete transaction management system that:
1. Provides backend CRUD endpoints for transactions with proper authentication and entity scoping
2. Supports filtering by date range, category, and transaction type
3. Creates a frontend Transactions page with a data table and add/edit form
4. Uses react-hook-form for form validation
5. Integrates with the existing authentication system to scope transactions to the current entity
6. Follows Clean Architecture patterns on both frontend and backend

## Relevant Files
Use these files to implement the feature:

### Existing Files to Modify
- `apps/Server/main.py`: Register transaction router
- `apps/Client/src/App.tsx`: Add transactions route
- `apps/Client/src/types/index.ts`: Already has Transaction interface but needs userId field

### New Files
#### Backend
- `apps/Server/src/models/transaction.py`: SQLAlchemy Transaction model
- `apps/Server/src/interface/transaction_dto.py`: Pydantic DTOs for transaction requests/responses
- `apps/Server/src/repository/transaction_repository.py`: Transaction data access layer
- `apps/Server/src/core/services/transaction_service.py`: Transaction business logic
- `apps/Server/src/adapter/rest/transaction_routes.py`: Transaction API endpoints
- `apps/Server/tests/test_transactions.py`: Transaction endpoint tests

#### Frontend
- `apps/Client/src/services/transactionService.ts`: API calls for transaction CRUD
- `apps/Client/src/pages/TransactionsPage.tsx`: Main transactions page
- `apps/Client/src/components/forms/TRTransactionForm.tsx`: Transaction add/edit form
- `apps/Client/src/components/ui/TRTransactionTable.tsx`: Transaction data table
- `apps/Client/src/hooks/useTransactions.ts`: Hook for transaction state management
- `.claude/commands/e2e/test_transaction_crud.md`: E2E test for transaction CRUD flow

### Reference Files
- `apps/Server/database/schema.sql`: Database schema with transactions table definition
- `apps/Server/src/adapter/rest/auth_routes.py`: Pattern for API routes
- `apps/Server/src/core/services/auth_service.py`: Pattern for service layer
- `apps/Server/src/repository/user_repository.py`: Pattern for repository layer
- `apps/Server/src/models/user.py`: Pattern for SQLAlchemy models
- `apps/Server/src/interface/auth_dto.py`: Pattern for Pydantic DTOs
- `apps/Client/src/pages/LoginPage.tsx`: Pattern for page components with forms
- `apps/Client/src/services/authService.ts`: Pattern for service calls
- `app_docs/feature-db5f36c7-database-schema-tables.md`: Database schema documentation
- `app_docs/feature-ed4cef49-backend-jwt-auth-rbac.md`: Backend auth patterns
- `app_docs/feature-f6f89b86-frontend-jwt-auth-context.md`: Frontend auth patterns
- `.claude/commands/test_e2e.md`: E2E test runner format
- `.claude/commands/e2e/test_auth_login.md`: Example E2E test structure

## Implementation Plan
### Phase 1: Foundation (Backend Models & Repository)
1. Create SQLAlchemy Transaction model matching the database schema
2. Create Pydantic DTOs for transaction requests and responses
3. Create transaction repository with CRUD operations and filtering

### Phase 2: Core Implementation (Backend Service & Routes)
4. Create transaction service with business logic
5. Create transaction API routes with authentication
6. Create transaction tests

### Phase 3: Frontend Implementation
7. Update TypeScript types for transactions
8. Create transaction service for API calls
9. Create transaction form component (TRTransactionForm)
10. Create transaction table component (TRTransactionTable)
11. Create useTransactions hook
12. Create TransactionsPage

### Phase 4: Integration & Testing
13. Register transaction router in main.py
14. Add transactions route to App.tsx
15. Create E2E test for transaction CRUD
16. Run validation commands

## Step by Step Tasks

### Task 1: Create Transaction Model
- Create `apps/Server/src/models/transaction.py`
- Import UUID, datetime, Decimal from appropriate modules
- Import Base from `src.config.database`
- Create Transaction class with columns matching schema.sql:
  - `id: UUID` - primary key with uuid4 default
  - `entity_id: UUID` - foreign key to entities
  - `category_id: UUID` - foreign key to categories
  - `user_id: UUID` - foreign key to users (nullable)
  - `amount: Decimal(15, 2)` - transaction amount
  - `type: str` - 'income' or 'expense'
  - `description: str` - transaction description (nullable)
  - `date: date` - transaction date
  - `notes: str` - additional notes (nullable)
  - `created_at: datetime` - timestamp
  - `updated_at: datetime` - timestamp (nullable)
- Add proper type hints and docstrings

### Task 2: Create Transaction DTOs
- Create `apps/Server/src/interface/transaction_dto.py`
- Create `TransactionCreateDTO`:
  - `entity_id: UUID`
  - `category_id: UUID`
  - `amount: Decimal` (positive, Field constraint)
  - `type: str` (Literal['income', 'expense'])
  - `description: Optional[str]`
  - `date: date`
  - `notes: Optional[str]`
- Create `TransactionUpdateDTO`:
  - All fields optional except entity_id
  - `category_id: Optional[UUID]`
  - `amount: Optional[Decimal]`
  - `type: Optional[str]`
  - `description: Optional[str]`
  - `date: Optional[date]`
  - `notes: Optional[str]`
- Create `TransactionResponseDTO`:
  - All fields from model
  - `model_config = {"from_attributes": True}`
- Create `TransactionListResponseDTO`:
  - `transactions: List[TransactionResponseDTO]`
  - `total: int`
- Create `TransactionFilterDTO`:
  - `start_date: Optional[date]`
  - `end_date: Optional[date]`
  - `category_id: Optional[UUID]`
  - `type: Optional[str]` (income/expense)

### Task 3: Create Transaction Repository
- Create `apps/Server/src/repository/transaction_repository.py`
- Import Transaction model, Session, and UUID
- Create TransactionRepository class with methods:
  - `create_transaction(db, entity_id, category_id, user_id, amount, type, description, date, notes) -> Transaction`
  - `get_transaction_by_id(db, transaction_id) -> Optional[Transaction]`
  - `get_transactions_by_entity(db, entity_id, filters: TransactionFilterDTO = None, skip: int = 0, limit: int = 100) -> List[Transaction]`
  - `count_transactions_by_entity(db, entity_id, filters: TransactionFilterDTO = None) -> int`
  - `update_transaction(db, transaction: Transaction) -> Transaction`
  - `delete_transaction(db, transaction: Transaction) -> None`
- Implement filtering by date range, category_id, and type in get_transactions_by_entity
- Add proper logging per CLAUDE.md standards
- Export singleton instance: `transaction_repository = TransactionRepository()`

### Task 4: Create Transaction Service
- Create `apps/Server/src/core/services/transaction_service.py`
- Import transaction_repository, DTOs, and models
- Create TransactionService class with methods:
  - `create_transaction(db, user_id, data: TransactionCreateDTO) -> Transaction`
  - `get_transaction(db, transaction_id, entity_id) -> Optional[Transaction]`
  - `list_transactions(db, entity_id, filters: TransactionFilterDTO, skip, limit) -> Tuple[List[Transaction], int]`
  - `update_transaction(db, transaction_id, entity_id, data: TransactionUpdateDTO) -> Optional[Transaction]`
  - `delete_transaction(db, transaction_id, entity_id) -> bool`
- Entity validation: all operations should verify entity_id matches
- Add proper logging per CLAUDE.md standards
- Export singleton instance: `transaction_service = TransactionService()`

### Task 5: Create Transaction Routes
- Create `apps/Server/src/adapter/rest/transaction_routes.py`
- Import FastAPI, Depends, HTTPException, status
- Import get_current_user, get_db from dependencies
- Import require_roles from rbac_dependencies
- Import transaction_service and DTOs
- Create router with prefix `/api/transactions` and tag "Transactions"
- Implement endpoints:
  - `POST /` - Create transaction (authenticated users)
  - `GET /` - List transactions with query params for filters (entity_id, start_date, end_date, category_id, type, skip, limit)
  - `GET /{transaction_id}` - Get single transaction by ID
  - `PUT /{transaction_id}` - Update transaction (owner or admin/manager)
  - `DELETE /{transaction_id}` - Delete transaction (admin/manager only)
- All endpoints require authentication via get_current_user
- Add proper logging per CLAUDE.md standards
- Validate entity_id belongs to current user (for now, accept any entity_id until entity context is implemented)

### Task 6: Create Transaction Tests
- Create `apps/Server/tests/test_transactions.py`
- Import TestClient, pytest, and app
- Create test fixtures for authenticated user token
- Test cases:
  - `test_create_transaction_success`: Create valid transaction
  - `test_create_transaction_invalid_type`: Reject invalid transaction type
  - `test_create_transaction_negative_amount`: Reject negative amount
  - `test_list_transactions_empty`: List returns empty for new entity
  - `test_list_transactions_with_filters`: Test date and type filtering
  - `test_get_transaction_not_found`: 404 for non-existent transaction
  - `test_update_transaction_success`: Update existing transaction
  - `test_delete_transaction_success`: Delete transaction as admin
  - `test_delete_transaction_forbidden`: 403 for regular user delete
- Use proper mocking or test database setup

### Task 7: Update TypeScript Transaction Types
- Open `apps/Client/src/types/index.ts`
- Update Transaction interface to match backend response:
  - `id: string`
  - `entity_id: string` (was entityId - use snake_case to match backend)
  - `category_id: string` (was categoryId)
  - `user_id?: string` (was missing)
  - `amount: number`
  - `type: TransactionType` ('income' | 'expense')
  - `description?: string`
  - `date: string`
  - `notes?: string`
  - `created_at: string` (was createdAt)
  - `updated_at?: string` (was updatedAt)
- Add `TransactionCreate` interface (for creating transactions)
- Add `TransactionUpdate` interface (for updating transactions)
- Add `TransactionFilters` interface (for filtering transactions)
- Add `TransactionListResponse` interface

### Task 8: Create Transaction Service (Frontend)
- Create `apps/Client/src/services/transactionService.ts`
- Import apiClient from `@/api/clients`
- Import Transaction and related types
- Create transactionService object with methods:
  - `create(data: TransactionCreate): Promise<Transaction>`
  - `list(entityId: string, filters?: TransactionFilters): Promise<TransactionListResponse>`
  - `get(transactionId: string): Promise<Transaction>`
  - `update(transactionId: string, data: TransactionUpdate): Promise<Transaction>`
  - `delete(transactionId: string): Promise<void>`
- Add proper logging per CLAUDE.md standards
- Export default transactionService

### Task 9: Create TRTransactionForm Component
- Create `apps/Client/src/components/forms/TRTransactionForm.tsx`
- Import useForm from react-hook-form
- Import MUI components: TextField, Button, MenuItem, Box, InputAdornment, FormControl, InputLabel, Select, FormHelperText
- Import DatePicker from @mui/x-date-pickers (or use native date input)
- Props interface:
  - `onSubmit: (data: TransactionCreate) => Promise<void>`
  - `initialData?: Transaction` (for edit mode)
  - `categories: Category[]` (passed from parent)
  - `entityId: string`
  - `isLoading?: boolean`
- Create form with fields:
  - Amount (number input with currency adornment, required, positive)
  - Type (select: income/expense, required)
  - Category (select from categories filtered by type, required)
  - Date (date picker, required, default today)
  - Description (text input, optional)
  - Notes (multiline text input, optional)
- Submit button with loading state
- Add proper validation messages
- Add proper logging

### Task 10: Create TRTransactionTable Component
- Create `apps/Client/src/components/ui/TRTransactionTable.tsx`
- Import MUI Table components, IconButton, Chip
- Import Edit, Delete icons from @mui/icons-material
- Props interface:
  - `transactions: Transaction[]`
  - `onEdit: (transaction: Transaction) => void`
  - `onDelete: (transactionId: string) => void`
  - `isLoading?: boolean`
- Create data table with columns:
  - Date (formatted)
  - Type (income/expense chip with color)
  - Category (category name - may need to accept category map)
  - Amount (formatted currency)
  - Description
  - Actions (Edit, Delete buttons)
- Support empty state message
- Add loading state (skeleton or spinner)
- Consider pagination props for future enhancement

### Task 11: Create useTransactions Hook
- Create `apps/Client/src/hooks/useTransactions.ts`
- Import useState, useEffect, useCallback
- Import transactionService and types
- Create useTransactions hook accepting entityId:
  - State: transactions, isLoading, error, total
  - State: filters (date range, category, type)
  - Functions:
    - `fetchTransactions()` - load transactions with current filters
    - `createTransaction(data)` - create and refresh list
    - `updateTransaction(id, data)` - update and refresh list
    - `deleteTransaction(id)` - delete and refresh list
    - `setFilters(filters)` - update filters and refetch
- Return state and functions
- Add proper logging

### Task 12: Create TransactionsPage
- Create `apps/Client/src/pages/TransactionsPage.tsx`
- Import useTransactions hook, TRTransactionForm, TRTransactionTable
- Import MUI components: Container, Typography, Box, Paper, Button, Dialog, Alert
- Import useAuth for current user
- Create page with:
  - Page title "Transactions"
  - Filter controls (date range picker, category select, type select)
  - "Add Transaction" button that opens dialog with TRTransactionForm
  - TRTransactionTable displaying transactions
  - Edit dialog with TRTransactionForm (prefilled)
  - Delete confirmation dialog
- For now, use a hardcoded entityId or get from URL params (entity context comes in parallel issue)
- Handle loading and error states
- Add proper logging

### Task 13: Register Transaction Router
- Open `apps/Server/main.py`
- Import transaction_routes router: `from src.adapter.rest.transaction_routes import router as transaction_router`
- Register router: `app.include_router(transaction_router)`
- Add log statement: `print("INFO [Main]: Transaction router registered")`

### Task 14: Add Transactions Route to App.tsx
- Open `apps/Client/src/App.tsx`
- Import TransactionsPage from `@/pages/TransactionsPage`
- Import ProtectedRoute (already imported)
- Add route for `/transactions` wrapped in ProtectedRoute:
  ```tsx
  <Route
    path="/transactions"
    element={
      <ProtectedRoute>
        <TransactionsPage />
      </ProtectedRoute>
    }
  />
  ```

### Task 15: Create E2E Test for Transaction CRUD
- Create `.claude/commands/e2e/test_transaction_crud.md`
- User Story: As a user, I want to manage my transactions (create, view, edit, delete)
- Test Steps:
  1. Navigate to Application URL and login with test credentials
  2. Navigate to `/transactions` page
  3. Take screenshot of empty transactions page
  4. Click "Add Transaction" button
  5. Take screenshot of transaction form
  6. Fill form with test data (type: expense, amount: 50.00, category: first available, date: today, description: "Test expense")
  7. Submit form
  8. Verify success message
  9. Verify transaction appears in table
  10. Take screenshot of transactions table with new transaction
  11. Click edit button on transaction
  12. Change amount to 75.00
  13. Submit edit form
  14. Verify amount updated in table
  15. Click delete button on transaction
  16. Confirm deletion
  17. Verify transaction removed from table
  18. Take final screenshot
- Success Criteria: All CRUD operations work correctly

### Task 16: Run Validation Commands
- Run `cd apps/Server && uv run pytest tests/test_transactions.py -v` - Run transaction tests
- Run `cd apps/Server && uv run pytest` - Run all Server tests
- Run `cd apps/Client && npm run tsc --noEmit` - Run Client type check
- Run `cd apps/Client && npm run lint` - Run Client linting
- Run `cd apps/Client && npm run build` - Run Client build
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_transaction_crud.md` to validate transaction CRUD E2E

## Testing Strategy
### Unit Tests
- Transaction repository: Test CRUD operations and filtering
- Transaction service: Test business logic and entity validation
- Transaction routes: Test API endpoints with authentication

### Edge Cases
- Create transaction with negative amount (should reject)
- Create transaction with invalid type (should reject)
- Create transaction with future date (should allow)
- Update non-existent transaction (should 404)
- Delete transaction without admin/manager role (should 403)
- List transactions with no results (should return empty array)
- Filter by date range that has no transactions (should return empty)
- Large number of transactions (pagination)

## Acceptance Criteria
- [ ] Backend transaction CRUD endpoints work correctly
- [ ] Transactions are scoped to entity_id
- [ ] Filtering by date range, category, and type works
- [ ] Frontend Transactions page displays transaction list
- [ ] Add Transaction form creates new transactions
- [ ] Edit Transaction form updates existing transactions
- [ ] Delete Transaction removes transactions (admin/manager only)
- [ ] Transaction table shows date, type, category, amount, description
- [ ] Type is displayed as colored chip (green for income, red for expense)
- [ ] Amount is formatted as currency
- [ ] Date is formatted in readable format
- [ ] Form validates required fields (amount, type, category, date)
- [ ] Form validates amount is positive
- [ ] Loading states are shown during API calls
- [ ] Error messages are displayed for failures
- [ ] All TypeScript types are correct (no `any`)
- [ ] Backend tests pass
- [ ] Frontend builds without errors

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest tests/test_transactions.py -v` - Run transaction-specific tests
- `cd apps/Server && uv run pytest` - Run all Server tests to validate with zero regressions
- `cd apps/Client && npm run tsc --noEmit` - Run Client type check to validate TypeScript types
- `cd apps/Client && npm run lint` - Run Client linting
- `cd apps/Client && npm run build` - Run Client build to validate the feature works with zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_transaction_crud.md` to validate transaction CRUD E2E

## Notes
- This feature runs in parallel with FT-006 (Layout), FT-007 (Entity Management), and FT-008 (Categories). Entity context is not available yet, so use a hardcoded entity_id or URL parameter for now. Integration with EntityContext will happen when that feature is complete.
- Category selection in the form depends on having categories in the database. For testing, ensure categories exist or mock them.
- The transactions table schema already exists in the database (schema.sql). No migration needed.
- The frontend Transaction type uses snake_case field names to match the backend response format.
- Delete operation is restricted to admin/manager roles per the RBAC system.
- Consider adding pagination to the transactions list in a future enhancement.
- The @mui/x-date-pickers package may need to be installed if not already present. Check package.json before using DatePicker, or use native HTML date input for simplicity.
