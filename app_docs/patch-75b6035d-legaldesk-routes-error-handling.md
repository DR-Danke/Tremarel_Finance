# LegalDesk Routes Error Handling

**ADW ID:** 75b6035d
**Date:** 2026-03-07
**Specification:** specs/patch/patch-adw-75b6035d-add-legaldesk-routes-error-handling.md

## Overview

Added comprehensive error handling to all ~24 unprotected endpoints in `legaldesk_routes.py`. Previously, database exceptions (foreign key violations, unique constraint errors) and validation failures would result in raw 500 errors. Now each endpoint catches `IntegrityError`, `ValueError`, and/or `Exception` and returns appropriate HTTP status codes (400, 404, 500) with meaningful error messages and structured logging.

## What Was Built

- `IntegrityError` handling for all create/update endpoints (FK violations, duplicate entries)
- `ValueError` handling for validation failures across service and repository calls
- Broad `Exception` handling for read-only list endpoints to prevent raw 500s
- Consistent `print()` logging for all caught errors following the `ERROR [LegalDeskRoutes]` pattern

## Technical Implementation

### Files Modified

- `apps/Server/src/adapter/rest/legaldesk_routes.py`: Added `IntegrityError` import from `sqlalchemy.exc` and wrapped 24 endpoints in try/except blocks with appropriate error handling

### Key Changes

- **Import added**: `from sqlalchemy.exc import IntegrityError` for catching database constraint violations
- **Direct-repository endpoints** (deliverables, messages, documents): Added try/except for `IntegrityError` (404 for FK violations on case_id) and `Exception` (500 for list operations)
- **Service-layer endpoints** (cases, specialists, clients, pricing, analytics, dashboard): Added try/except for `IntegrityError` (400 for duplicates), `ValueError` (400/404 depending on context), and `Exception` (500 for list/read operations)
- **Three error patterns applied consistently**:
  1. Create endpoints with FK references: `IntegrityError` -> 404 ("Case/Specialist not found")
  2. Create/update endpoints: `IntegrityError` -> 400 ("Invalid reference or duplicate entry"), `ValueError` -> 400
  3. List/read-only endpoints: `Exception` -> 500 ("Failed to retrieve data") with logged error

### Endpoints Updated

| Category | Endpoints | Error Types Caught |
|---|---|---|
| Cases | create, list, get_detail, update | IntegrityError, ValueError, Exception |
| Deliverables | list, create, update, update_status | IntegrityError, ValueError, Exception |
| Messages | get, create | IntegrityError, ValueError, Exception |
| Documents | list, create | IntegrityError, ValueError, Exception |
| Pricing | get_history | Exception |
| Specialists | list, create, get_detail, update, add_expertise, add_jurisdiction, submit_score | IntegrityError, ValueError, Exception |
| Clients | list, create, get, update | IntegrityError, ValueError, Exception |
| Dashboard | get_stats | Exception |

## How to Use

1. No action required from developers or users -- error handling is automatic
2. When a database constraint violation occurs (e.g., creating a deliverable for a non-existent case), the API now returns a 404 with `"Case {case_id} not found"` instead of a raw 500
3. When a validation error occurs, the API returns a 400 with the specific validation message
4. When an unexpected error occurs on list endpoints, the API returns a 500 with `"Failed to retrieve data"` and logs the actual error server-side

## Configuration

No configuration changes required.

## Testing

- Run server syntax check: `cd apps/Server && python -m py_compile src/adapter/rest/legaldesk_routes.py`
- Run linting: `cd apps/Server && ruff check src/adapter/rest/legaldesk_routes.py`
- Run server tests: `cd apps/Server && pytest tests/ -v --tb=short`

## Notes

- This patch was identified by the Continuous Improvement Scanner (GitHub issue #193)
- The patch is backend-only; no frontend changes were required
- Error messages are intentionally generic for security (actual error details are logged server-side only)
