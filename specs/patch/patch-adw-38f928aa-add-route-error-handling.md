# Patch: Add error handling to transaction and reports routes

## Metadata
adw_id: `38f928aa`
review_change_request: `{number:190,title:[CI] transaction_routes.py and reports_routes.py lack error handling}`

## Issue Summary
**Original Spec:** N/A
**Issue:** `transaction_routes.py` and `reports_routes.py` lack try/except blocks around service calls. If services raise `ValueError` or `PermissionError`, users get raw 500 errors with no structured message and no ERROR log line. All other route files in the codebase consistently use try/except with `PermissionError -> 403`, `ValueError -> 400/404` patterns.
**Solution:** Wrap service calls in both files with try/except blocks following the established codebase pattern (see `category_routes.py`, `budget_routes.py` as references). Add ERROR logging in except blocks.

## Files to Modify

- `apps/Server/src/adapter/rest/transaction_routes.py`
- `apps/Server/src/adapter/rest/reports_routes.py`

## Implementation Steps
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add try/except to transaction_routes.py endpoints

Wrap the service calls in each endpoint with try/except blocks:

**create_transaction (line 46):** Wrap `transaction_service.create_transaction()` call:
```python
try:
    transaction = transaction_service.create_transaction(db, user_id, data)
except PermissionError as e:
    print(f"ERROR [TransactionRoutes]: Access denied: {str(e)}")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
except ValueError as e:
    print(f"ERROR [TransactionRoutes]: Transaction creation failed: {str(e)}")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
```

**list_transactions (line 92-98):** Wrap `transaction_service.list_transactions()` call:
```python
try:
    transactions, total = transaction_service.list_transactions(...)
except ValueError as e:
    print(f"ERROR [TransactionRoutes]: Failed to list transactions: {str(e)}")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
```

**get_transaction (line 131):** Wrap `transaction_service.get_transaction()` call:
```python
try:
    transaction = transaction_service.get_transaction(db, transaction_id, entity_id)
except PermissionError as e:
    print(f"ERROR [TransactionRoutes]: Access denied: {str(e)}")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
except ValueError as e:
    print(f"ERROR [TransactionRoutes]: Failed to get transaction: {str(e)}")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
```
Keep existing `if not transaction` check inside the try block.

**update_transaction (line 169):** Wrap `transaction_service.update_transaction()` call:
```python
try:
    transaction = transaction_service.update_transaction(db, transaction_id, entity_id, data)
except PermissionError as e:
    print(f"ERROR [TransactionRoutes]: Access denied: {str(e)}")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
except ValueError as e:
    print(f"ERROR [TransactionRoutes]: Transaction update failed: {str(e)}")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
```
Keep existing `if not transaction` check inside the try block.

**delete_transaction (line 205):** Wrap `transaction_service.delete_transaction()` call:
```python
try:
    success = transaction_service.delete_transaction(db, transaction_id, entity_id)
except PermissionError as e:
    print(f"ERROR [TransactionRoutes]: Access denied: {str(e)}")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
except ValueError as e:
    print(f"ERROR [TransactionRoutes]: Transaction deletion failed: {str(e)}")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
```
Keep existing `if not success` check inside the try block.

### Step 2: Add try/except to reports_routes.py endpoints

Add `HTTPException` and `status` to the import from fastapi (currently missing):
```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
```

**get_report_data (line 47-49):** Wrap `reports_service.get_report_data()` call:
```python
try:
    report_data = reports_service.get_report_data(db, entity_id, start_date, end_date)
except PermissionError as e:
    print(f"ERROR [ReportsRoutes]: Access denied: {str(e)}")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
except ValueError as e:
    print(f"ERROR [ReportsRoutes]: Report data request failed: {str(e)}")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
```

**export_csv (line 83-85):** Wrap `reports_service.export_transactions_csv()` call:
```python
try:
    csv_content = reports_service.export_transactions_csv(db, entity_id, start_date, end_date)
except PermissionError as e:
    print(f"ERROR [ReportsRoutes]: Access denied: {str(e)}")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
except ValueError as e:
    print(f"ERROR [ReportsRoutes]: CSV export failed: {str(e)}")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
```

## Validation
Execute every command to validate the patch is complete with zero regressions.

1. **Python Syntax Check**
   ```bash
   cd apps/Server && .venv/bin/python -m py_compile main.py src/**/*.py
   ```

2. **Server Code Quality Check**
   ```bash
   cd apps/Server && .venv/bin/ruff check .
   ```

3. **All Server Tests**
   ```bash
   cd apps/Server && .venv/bin/pytest tests/ -v --tb=short
   ```

4. **TypeScript Type Check**
   ```bash
   cd apps/Client && npm run tsc --noEmit
   ```

5. **Client Build**
   ```bash
   cd apps/Client && npm run build
   ```

## Patch Scope
**Lines of code to change:** ~50
**Risk level:** low
**Testing required:** Backend syntax check, linting, and existing tests must pass. No frontend changes.
