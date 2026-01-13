# Recurring Transactions

**ADW ID:** e44986c8
**Date:** 2026-01-13
**Specification:** specs/issue-27-adw-e44986c8-sdlc_planner-recurring-transactions.md

## Overview

Recurring transactions functionality allows users to create transaction templates with recurrence patterns (daily, weekly, monthly, yearly). Users can manage these templates from a dedicated page and track which transactions were generated from recurring templates through visual indicators in the transaction list.

## What Was Built

- **Recurring Template Model**: SQLAlchemy model for storing recurring transaction patterns
- **Recurring Template CRUD API**: Full REST API for managing recurring templates
- **Template Management UI**: Frontend page with table, create/edit dialogs, and deactivation support
- **Transaction Linking**: Transactions can reference their source template via `recurring_template_id`
- **Visual Indicators**: Recurring icon displayed in transaction table for linked transactions
- **Navigation Integration**: Sidebar link to access recurring templates page

## Technical Implementation

### Files Modified

- `apps/Server/database/schema.sql`: Added `recurring_templates` table and `recurring_template_id` column to transactions
- `apps/Server/main.py`: Registered recurring template router
- `apps/Server/src/models/transaction.py`: Added `recurring_template_id` field
- `apps/Server/src/interface/transaction_dto.py`: Updated DTOs with recurring template reference
- `apps/Client/src/App.tsx`: Added `/recurring` route
- `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`: Added navigation item
- `apps/Client/src/components/ui/TRTransactionTable.tsx`: Added recurring indicator icon
- `apps/Client/src/types/index.ts`: Added recurring template types

### New Files Created

**Backend:**
- `apps/Server/src/models/recurring_template.py`: RecurringTemplate SQLAlchemy model
- `apps/Server/src/interface/recurring_template_dto.py`: Pydantic DTOs for CRUD operations
- `apps/Server/src/repository/recurring_template_repository.py`: Data access layer
- `apps/Server/src/core/services/recurring_template_service.py`: Business logic layer
- `apps/Server/src/adapter/rest/recurring_template_routes.py`: REST API endpoints
- `apps/Server/tests/test_recurring_templates.py`: Unit tests (557 lines)

**Frontend:**
- `apps/Client/src/services/recurringTemplateService.ts`: API client
- `apps/Client/src/hooks/useRecurringTemplates.ts`: State management hook
- `apps/Client/src/components/forms/TRRecurringTemplateForm.tsx`: Create/edit form
- `apps/Client/src/components/ui/TRRecurringTemplateTable.tsx`: Template list table
- `apps/Client/src/pages/RecurringTemplatesPage.tsx`: Main page component

### Key Changes

- Database schema includes constraints for valid type (income/expense), positive amounts, valid frequency values, and date validation (end_date >= start_date)
- Soft delete pattern: Templates are deactivated (`is_active=false`) instead of hard-deleted to preserve transaction history
- Hard delete requires admin/manager role via RBAC
- API supports pagination and filtering by `include_inactive` parameter
- Frontend uses react-hook-form with Material-UI for form validation

## How to Use

1. **Navigate to Recurring Templates**: Click "Recurring" in the sidebar navigation
2. **Create Template**: Click "Add Recurring Template" button, fill in:
   - Name (e.g., "Monthly Rent")
   - Amount
   - Type (Income/Expense)
   - Category
   - Frequency (Daily/Weekly/Monthly/Yearly)
   - Start Date
   - End Date (optional)
   - Description and Notes (optional)
3. **View Templates**: Templates are displayed in a table with status, frequency, and amount
4. **Edit Template**: Click the edit icon to modify template details
5. **Deactivate Template**: Click the deactivate icon to soft-delete (preserves history)
6. **Delete Template**: Admin/manager only - permanently removes template
7. **Toggle Inactive View**: Use "Show inactive templates" switch to view deactivated templates

## Configuration

No additional environment variables required. The feature uses existing authentication and database configuration.

## Testing

**Backend Tests:**
```bash
cd apps/Server && uv run pytest tests/test_recurring_templates.py
```

**Frontend Type Check:**
```bash
cd apps/Client && npm run typecheck
```

**E2E Test:**
Read and execute `.claude/commands/e2e/test_recurring_transactions.md`

## Notes

- This feature does NOT implement automatic transaction generation on a schedule. It only provides template management and tracking infrastructure.
- The `recurring_template_id` on transactions allows manual or future automated linking
- Future enhancements could include:
  - Background scheduler to auto-generate transactions from templates
  - Dashboard widget showing upcoming recurring transactions
  - Notifications for upcoming recurring expenses
- Soft delete is preferred over hard delete to maintain transaction history integrity
