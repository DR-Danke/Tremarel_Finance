# Patch: Add error handling to legaldesk_routes.py endpoints

## Metadata
adw_id: `75b6035d`
review_change_request: `{number:193,title:[CI] legaldesk_routes.py endpoints lack error handling for service/repo failures}`

## Issue Summary
**Original Spec:** N/A (Continuous Improvement finding)
**Issue:** Most legaldesk_routes.py endpoints (~33 endpoints) have minimal or no error handling. Endpoints that directly call repositories (deliverables, messages, documents) are the highest risk — a foreign key violation or database exception returns a raw 500 instead of a meaningful 400/404. Endpoints going through services catch only ValueError but miss IntegrityError and other database exceptions.
**Solution:** Add try/except blocks to all unprotected endpoints. Catch `IntegrityError` (SQLAlchemy) for FK/unique constraint violations and `ValueError` for validation failures. Wrap both direct-repo calls and service calls consistently.

## Files to Modify

- `apps/Server/src/adapter/rest/legaldesk_routes.py` — Add error handling to all endpoints lacking it

## Implementation Steps
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add IntegrityError import
- Add `from sqlalchemy.exc import IntegrityError` to the imports section (after the existing sqlalchemy import on line 13)

### Step 2: Add error handling to direct-repository endpoints (highest risk)
These endpoints bypass the service layer and call repositories directly — they have zero error handling today:

- **`list_deliverables`** (line 284): Wrap `ld_deliverable_repository.get_by_case()` in try/except catching `IntegrityError` → 400 and `Exception` → 500 with logged message
- **`create_deliverable`** (line 296): Wrap `ld_deliverable_repository.create()` in try/except catching `IntegrityError` → 404 ("Case not found or invalid reference") and `ValueError` → 400
- **`update_deliverable`** (line 310): Wrap `ld_deliverable_repository.update()` in try/except catching `IntegrityError` → 400
- **`update_deliverable_status`** (line 326): Wrap `ld_deliverable_repository.update_status()` in try/except catching `ValueError` → 400
- **`get_messages`** (line 347): Wrap `ld_message_repository.get_by_case()` in try/except catching `Exception` → 500 with logged message
- **`create_message`** (line 360): Wrap `ld_message_repository.create()` in try/except catching `IntegrityError` → 404 ("Case not found or invalid reference") and `ValueError` → 400
- **`list_documents`** (line 380): Wrap `ld_document_repository.get_by_case()` in try/except catching `Exception` → 500 with logged message
- **`create_document`** (line 392): Wrap `ld_document_repository.create()` in try/except catching `IntegrityError` → 404 ("Case not found or invalid reference") and `ValueError` → 400

### Step 3: Add error handling to service-layer endpoints (lower risk but still needed)
These endpoints call services but lack any try/except:

- **`create_case`** (line 114): Wrap in try/except catching `IntegrityError` → 400 and `ValueError` → 400
- **`list_cases`** (line 126): Wrap in try/except catching `Exception` → 500 with logged error
- **`get_case_detail`** (line 151): Add `ValueError` → 404 catch (already has None check)
- **`update_case`** (line 165): Add `IntegrityError` → 400 and `ValueError` → 400 catches
- **`get_pricing_history`** (line 412): Wrap in try/except catching `Exception` → 500 with logged error
- **`list_specialists`** (line 501): Wrap in try/except catching `Exception` → 500 with logged error
- **`create_specialist`** (line 526): Wrap in try/except catching `IntegrityError` → 400 (e.g., duplicate email) and `ValueError` → 400
- **`get_specialist_detail`** (line 538): Add `ValueError` → 404 catch
- **`update_specialist`** (line 552): Add `IntegrityError` → 400 and `ValueError` → 400 catches
- **`add_expertise`** (line 567): Wrap in try/except catching `IntegrityError` → 400 (duplicate expertise) and `ValueError` → 400
- **`add_jurisdiction`** (line 586): Wrap in try/except catching `IntegrityError` → 400 (duplicate jurisdiction) and `ValueError` → 400
- **`submit_score`** (line 605): Wrap in try/except catching `IntegrityError` → 404 and `ValueError` → 400
- **`list_clients`** (line 624): Wrap in try/except catching `Exception` → 500 with logged error
- **`create_client`** (line 635): Wrap in try/except catching `IntegrityError` → 400 and `ValueError` → 400
- **`get_client`** (line 647): Add `ValueError` → 404 catch
- **`update_client`** (line 661): Add `IntegrityError` → 400 and `ValueError` → 400 catches
- **`get_dashboard_stats`** (line 681): Wrap in try/except catching `Exception` → 500 with logged error

### Step 4: Ensure consistent error pattern
Use this consistent pattern across all endpoints:

```python
try:
    # existing logic
except IntegrityError as e:
    print(f"ERROR [LegalDeskRoutes]: Database integrity error: {e}")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reference or duplicate entry")
except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
```

For create endpoints with case_id FK, use a more specific IntegrityError message:
```python
except IntegrityError as e:
    print(f"ERROR [LegalDeskRoutes]: Integrity error creating deliverable for case {case_id}: {e}")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case {case_id} not found")
```

For read-only list endpoints, catch broadly:
```python
except Exception as e:
    print(f"ERROR [LegalDeskRoutes]: Failed to list items: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve data")
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
**Lines of code to change:** ~120 (adding try/except blocks to ~24 endpoints + 1 import line)
**Risk level:** low
**Testing required:** Server syntax check, ruff linting, pytest — no frontend changes needed (steps 4-5 are for full regression only)
