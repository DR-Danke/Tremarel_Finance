# Document Entity CRUD Backend

**ADW ID:** 95deee5d
**Date:** 2026-03-03
**Specification:** specs/issue-81-adw-95deee5d-sdlc_planner-document-entity-crud-backend.md

## Overview

Full backend CRUD implementation for the Document entity in RestaurantOS Wave 2. Documents represent legal and administrative artifacts (contracts, permits, invoices, licenses) with file upload support via multipart/form-data, person linking via FK, and automatic expiration status tracking (valid, expiring_soon, expired).

## What Was Built

- PostgreSQL `document` table with UUID PK, restaurant/person FKs, expiration tracking, and indexed columns
- SQLAlchemy `Document` model with full column mapping including Date fields
- Pydantic DTOs with computed `expiration_status` field and date validation
- Repository with CRUD operations plus `get_expiring()` query for expiration alerts
- Service layer with restaurant-scoped authorization, file upload handling, and expiration status filtering
- REST API routes with multipart/form-data create, query filters, and JWT authentication
- Comprehensive unit tests (DTO validation, computed fields) and API integration tests

## Technical Implementation

### Files Modified

- `apps/Server/main.py`: Registered document router import and `app.include_router(document_router)`
- `apps/Server/src/models/__init__.py`: Added `Document` to model exports

### Files Created

- `apps/Server/database/create_document_table.sql`: SQL migration with table, indexes, and `updated_at` trigger
- `apps/Server/src/models/document.py`: SQLAlchemy model with UUID PK, restaurant_id FK (CASCADE), person_id FK (SET NULL), type, file_url, dates, description, timestamps
- `apps/Server/src/interface/document_dto.py`: `DocumentCreateDTO` (with date validation), `DocumentUpdateDTO` (partial), `DocumentResponseDTO` (with computed `expiration_status`)
- `apps/Server/src/repository/document_repository.py`: CRUD + `get_expiring()` query filtering by date range
- `apps/Server/src/core/services/document_service.py`: Business logic with `_check_restaurant_access`, file upload to `uploads/documents/`, expiration warnings, status post-filtering
- `apps/Server/src/adapter/rest/document_routes.py`: 6 REST endpoints with JWT auth
- `apps/Server/tests/test_document_model.py`: 340 lines of DTO/model unit tests
- `apps/Server/tests/test_document_api.py`: 734 lines of API integration tests

### Key Changes

- **Expiration status computation**: `DocumentResponseDTO` uses a `@model_validator(mode="before")` to compute `expiration_status` from `expiration_date` — "expired" if past, "expiring_soon" if within 30 days, "valid" otherwise (or if no date set)
- **File upload via multipart/form-data**: The POST endpoint accepts `Form(...)` fields for metadata and `File(None)` for optional file upload. Files are saved to `uploads/documents/` with UUID-based filenames to prevent collisions
- **ON DELETE SET NULL for person_id**: Unlike `restaurant_id` (CASCADE), deleting a person preserves their documents by setting `person_id` to NULL
- **Expiring documents query**: Repository `get_expiring()` filters documents where `expiration_date` is between today and today + N days, exposed via `GET /api/documents/expiring`
- **Service-level status filtering**: `get_documents()` supports optional `expiration_status_filter` that post-filters results by computing each document's status in-memory

## How to Use

1. **Create a document** — `POST /api/documents` with multipart/form-data:
   - Required fields: `restaurant_id` (UUID), `type` (string, 1-100 chars)
   - Optional fields: `issue_date`, `expiration_date`, `person_id`, `description`, `file` (upload)
   - Returns 201 with `DocumentResponseDTO` including computed `expiration_status`

2. **List documents** — `GET /api/documents?restaurant_id=<uuid>`:
   - Optional filters: `type` (exact match), `expiration_status` (valid | expiring_soon | expired)

3. **Get expiring documents** — `GET /api/documents/expiring?restaurant_id=<uuid>&days_ahead=30`:
   - Returns documents with expiration dates within the specified window

4. **Get single document** — `GET /api/documents/{document_id}`

5. **Update document** — `PUT /api/documents/{document_id}` with JSON body (partial update)

6. **Delete document** — `DELETE /api/documents/{document_id}` returns 204

All endpoints require JWT authentication via `Authorization: Bearer <token>` header and verify restaurant membership.

## Configuration

- **File upload directory**: `uploads/documents/` (created automatically on first upload)
- **Expiration threshold**: 30 days (hardcoded in DTO validator and service layer)
- **Dependencies**: `python-multipart` (already in `requirements.txt`)
- No new environment variables required

## Testing

```bash
# Run document DTO/model unit tests
cd apps/Server && python -m pytest tests/test_document_model.py -v

# Run document API integration tests
cd apps/Server && python -m pytest tests/test_document_api.py -v

# Run all server tests (verify zero regressions)
cd apps/Server && python -m pytest tests/ -v
```

## Notes

- **Backend only**: No frontend components in this wave. Wave 4 will build the Document Management frontend page
- **Free-text document type**: Uses VARCHAR(100) instead of enum for flexibility — suggested values include contrato, permiso, factura, licencia, factura_proveedor
- **Local file storage**: Files stored locally in `uploads/documents/`. A future wave may migrate to cloud storage (S3, Supabase Storage). The service layer abstracts file handling for easy migration
- **Expiration alerts foundation**: The `get_expiring` query and `expiration_status` computed field prepare for Wave 6 alert automation
- **Parallel Wave 2 entity**: Runs alongside ROS-005 (Event) and ROS-006 (Inventory Movement). Shared files (`main.py`, `models/__init__.py`) may require merge coordination
