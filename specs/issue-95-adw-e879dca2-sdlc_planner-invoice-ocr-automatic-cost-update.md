# Feature: Invoice OCR & Automatic Cost Update

## Metadata
issue_number: `95`
adw_id: `e879dca2`
issue_json: ``

## Feature Description
When a supplier invoice document (type="factura_proveedor") is uploaded to RestaurantOS, the system uses an OCR/AI pipeline to extract line items (product names, quantities, unit prices, supplier name). For each extracted item, the system matches it to an existing Resource by name, updates the resource's `last_unit_cost`, and creates an inventory entry movement. Unmatched items are flagged for manual review. The OCR service is abstracted behind an interface (`OCRAdapter`) for provider swappability (Google Cloud Vision, AWS Textract, etc.). A stub adapter returns mock data for development/testing.

The document model gains two new fields: `processing_status` (pending/processing/completed/failed) and `processing_result` (JSONB with matched/unmatched details). Two new REST endpoints allow manual OCR trigger and result retrieval.

## User Story
As a restaurant manager
I want supplier invoices to be automatically processed via OCR to update resource costs and create inventory entries
So that I can keep resource pricing and stock levels accurate without manual data entry

## Problem Statement
Restaurant managers manually enter invoice line items into the system — updating resource costs and recording inventory entries one by one. This is time-consuming, error-prone, and delays accurate cost tracking. There is no automated way to extract data from supplier invoices and apply it to the resource/inventory system.

## Solution Statement
Implement an OCR processing pipeline that:
1. Accepts a document of type "factura_proveedor" for processing
2. Extracts line items via a pluggable OCR adapter (stub for now)
3. Matches extracted items to existing resources by name (case-insensitive)
4. Updates `last_unit_cost` on matched resources
5. Creates `entry` inventory movements with reason `compra` for matched items
6. Returns matched/unmatched results and stores them on the document record
7. Flags unmatched items for manual review

## Relevant Files
Use these files to implement the feature:

**Existing files to modify:**
- `apps/Server/src/models/document.py` — Add `processing_status` and `processing_result` columns to the Document model
- `apps/Server/src/interface/document_dto.py` — Add processing fields to `DocumentResponseDTO` and update `compute_expiration_status` model validator
- `apps/Server/src/repository/document_repository.py` — Add `update_processing_status()` method
- `apps/Server/src/repository/resource_repository.py` — Add `find_by_name()` method for case-insensitive name lookup
- `apps/Server/src/adapter/rest/document_routes.py` — Add `POST /{id}/process-invoice` and `GET /{id}/processing-result` endpoints

**Existing files to reference (read-only patterns):**
- `apps/Server/src/core/services/document_service.py` — Understand service patterns, singleton instance, `_check_restaurant_access`
- `apps/Server/src/core/services/resource_service.py` — Understand resource update patterns, `update_resource` method
- `apps/Server/src/core/services/inventory_service.py` — Understand `create_movement` flow, stock update logic
- `apps/Server/src/interface/inventory_movement_dto.py` — `InventoryMovementCreateDTO`, `MovementType`, `MovementReason` enums
- `apps/Server/src/interface/resource_dto.py` — `ResourceResponseDTO` pattern with model validators
- `apps/Server/main.py` — Router registration pattern (no changes needed since we add to existing document router)
- `apps/Server/src/models/__init__.py` — Model registration (no changes needed)
- `apps/Server/tests/test_document_api.py` — Test patterns: mock DB, mock user, auth token, patch singletons
- `apps/Server/database/create_document_table.sql` — Existing document table schema

**Conditional documentation to read:**
- `app_docs/feature-95deee5d-document-entity-crud-backend.md` — Document entity patterns
- `app_docs/feature-8d28116a-resource-entity-crud-backend.md` — Resource entity patterns
- `app_docs/feature-02529be1-inventory-movement-tracking.md` — Inventory movement patterns

### New Files
- `apps/Server/src/core/services/ocr_service.py` — OCR adapter interface (ABC) + `InvoiceItem` Pydantic model + `OCRService` wrapper
- `apps/Server/src/core/services/invoice_processor.py` — `InvoiceProcessor` service: OCR → match → update cost → create movement pipeline
- `apps/Server/src/adapter/ocr_stub_adapter.py` — Stub OCR adapter returning mock invoice data for development/testing
- `apps/Server/src/interface/invoice_dto.py` — DTOs for invoice processing requests/responses (`InvoiceProcessingResultDTO`, etc.)
- `apps/Server/database/alter_document_add_processing_fields.sql` — SQL migration to add `processing_status` and `processing_result` columns
- `apps/Server/tests/test_invoice_ocr_api.py` — API integration tests for invoice OCR endpoints
- `apps/Server/tests/test_invoice_ocr_model.py` — Unit tests for OCR DTOs and InvoiceItem model

## Implementation Plan
### Phase 1: Foundation
Add the database/model layer changes needed to support invoice processing:
- Add `processing_status` (VARCHAR) and `processing_result` (JSONB) columns to the document table via SQL migration
- Update the Document SQLAlchemy model with the new columns
- Update the DocumentResponseDTO to include the new fields
- Add `find_by_name()` to ResourceRepository for case-insensitive resource lookup
- Add `update_processing_status()` to DocumentRepository

### Phase 2: Core Implementation
Build the OCR service abstraction and invoice processing pipeline:
- Create the `OCRAdapter` abstract base class and `InvoiceItem` Pydantic model
- Create the `OCRService` wrapper that uses the adapter
- Create the `StubOCRAdapter` returning mock invoice data
- Create the `InvoiceProcessor` service that orchestrates: OCR → match → update cost → create movement
- Create invoice processing DTOs for API responses

### Phase 3: Integration
Wire everything together via REST endpoints:
- Add `POST /api/documents/{id}/process-invoice` to manually trigger OCR processing
- Add `GET /api/documents/{id}/processing-result` to retrieve processing results
- Add validation: only `factura_proveedor` documents can be processed, file must exist
- Write comprehensive tests for all new code

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create SQL Migration for Processing Fields
- Create `apps/Server/database/alter_document_add_processing_fields.sql`
- Add `processing_status VARCHAR(20) DEFAULT NULL` column to document table
- Add `processing_result JSONB DEFAULT NULL` column to document table
- Add index on `processing_status` for efficient filtering

### Step 2: Update Document Model
- Edit `apps/Server/src/models/document.py`
- Add `processing_status: Optional[str] = Column(String(20), nullable=True)` column
- Add `processing_result = Column(JSON, nullable=True)` column (use `sqlalchemy.types.JSON` for JSONB)
- Import `JSON` from `sqlalchemy` types

### Step 3: Update Document DTOs
- Edit `apps/Server/src/interface/document_dto.py`
- Add `processing_status: Optional[str]` and `processing_result: Optional[dict]` to `DocumentResponseDTO`
- Update the `compute_expiration_status` model validator to include the new fields in the ORM-to-dict conversion

### Step 4: Update Document Repository
- Edit `apps/Server/src/repository/document_repository.py`
- Add `update_processing_status(db, document_id, status, result)` method
- This method fetches the document, sets `processing_status` and `processing_result`, commits, and returns the updated document

### Step 5: Add find_by_name to Resource Repository
- Edit `apps/Server/src/repository/resource_repository.py`
- Add `find_by_name(db, restaurant_id, name)` method
- Use case-insensitive comparison: `func.lower(Resource.name) == name.lower()`
- Import `func` from `sqlalchemy`
- Return `Optional[Resource]`

### Step 6: Create Invoice DTOs
- Create `apps/Server/src/interface/invoice_dto.py`
- Define `InvoiceItemDTO` with fields: `product_name: str`, `quantity: Decimal`, `unit: str`, `unit_price: Decimal`, `supplier_name: Optional[str]`
- Define `InvoiceMatchedItemDTO` with fields: `item: InvoiceItemDTO`, `resource_id: UUID`
- Define `InvoiceProcessingResultDTO` with fields: `document_id: UUID`, `matched_count: int`, `unmatched_count: int`, `matched_items: list[InvoiceMatchedItemDTO]`, `unmatched_items: list[InvoiceItemDTO]`, `processing_status: str`

### Step 7: Create OCR Service Interface
- Create `apps/Server/src/core/services/ocr_service.py`
- Define `OCRAdapter(ABC)` with abstract method `async def extract_invoice_items(self, file_url: str) -> list[dict]`
- Define `InvoiceItem` Pydantic BaseModel with fields: `product_name: str`, `quantity: Decimal`, `unit: str`, `unit_price: Decimal`, `supplier_name: Optional[str]`
- Define `OCRService` class with `__init__(self, adapter: OCRAdapter)` and `process_invoice(self, file_url: str) -> list[InvoiceItem]`
- Add proper logging with `print(f"INFO [OCRService]: ...")`

### Step 8: Create Stub OCR Adapter
- Create `apps/Server/src/adapter/ocr_stub_adapter.py`
- Implement `StubOCRAdapter(OCRAdapter)` that returns hardcoded mock invoice data
- Mock data should include 3-4 items with realistic product names (e.g., "Tomate", "Aceite de oliva", "Harina de trigo", "Salsa BBQ Especial")
- The last item ("Salsa BBQ Especial") should be a name unlikely to match any resource, to test the unmatched flow
- Add a TODO comment for real OCR integration (Google Cloud Vision, AWS Textract)
- Add logging

### Step 9: Create Invoice Processor Service
- Create `apps/Server/src/core/services/invoice_processor.py`
- Define `InvoiceProcessor` class
- Import singleton instances: `document_repository`, `resource_repository`, `inventory_movement_repository` from their respective modules
- Import `restaurant_repository` for access checks
- Implement `_check_restaurant_access(self, db, user_id, restaurant_id)` following existing pattern
- Implement `process_invoice_document(self, db: Session, user_id: UUID, document_id: UUID) -> dict`:
  1. Fetch document via `document_repository.get_by_id()`; raise `ValueError` if not found
  2. Check restaurant access via `_check_restaurant_access()`
  3. Validate `document.type == "factura_proveedor"`; raise `ValueError` if not
  4. Validate `document.file_url is not None`; raise `ValueError` if not
  5. Update `processing_status` to `"processing"` via `document_repository`
  6. Call `ocr_service.process_invoice(document.file_url)` to extract items
  7. For each item, call `resource_repository.find_by_name(db, document.restaurant_id, item.product_name)`
  8. If matched: update `resource.last_unit_cost = item.unit_price` via `resource_repository.update()`, then create inventory movement via `inventory_movement_repository.create()` with type=`"entry"`, reason=`"compra"`, and update `resource.current_stock` via `resource_repository.update()`
  9. If not matched: add to unmatched list
  10. Build result dict with `matched_count`, `unmatched_count`, `matched_items`, `unmatched_items`
  11. Update document `processing_status` to `"completed"` and `processing_result` to the result dict
  12. Return the result
- Handle exceptions: wrap OCR call in try/except, set status to `"failed"` on error
- Create singleton instance: `invoice_processor = InvoiceProcessor()`
- Initialize with `StubOCRAdapter` by default: `ocr_service = OCRService(StubOCRAdapter())`
- Add extensive logging

### Step 10: Add REST Endpoints to Document Routes
- Edit `apps/Server/src/adapter/rest/document_routes.py`
- Import `invoice_processor` from `src.core.services.invoice_processor`
- Import `InvoiceProcessingResultDTO` from `src.interface.invoice_dto`
- Add `POST /api/documents/{document_id}/process-invoice` endpoint:
  - Requires auth (`get_current_user`)
  - Calls `invoice_processor.process_invoice_document(db, user_id, document_id)`
  - Returns `InvoiceProcessingResultDTO`
  - Maps `PermissionError` → 403, `ValueError` → 400/404
- Add `GET /api/documents/{document_id}/processing-result` endpoint:
  - Requires auth
  - Fetches document via `document_service.get_document()`
  - Returns processing status and result from document fields
  - Place these endpoints BEFORE `/{document_id}` route to avoid path collision

### Step 11: Create Model/DTO Unit Tests
- Create `apps/Server/tests/test_invoice_ocr_model.py`
- Test `InvoiceItem` model validation (valid data, missing fields, negative values)
- Test `InvoiceItemDTO` and `InvoiceProcessingResultDTO` serialization
- Test `StubOCRAdapter` returns expected mock data format
- Follow existing test pattern with `print("INFO [TestInvoiceOCR]: test_name - PASSED")`

### Step 12: Create API Integration Tests
- Create `apps/Server/tests/test_invoice_ocr_api.py`
- Follow `test_document_api.py` patterns exactly: mock DB, mock user, auth token, patch singletons
- Test `POST /api/documents/{id}/process-invoice`:
  - Success case: document exists, type is "factura_proveedor", file_url exists, resources match
  - Error case: document not found (404)
  - Error case: document type is not "factura_proveedor" (400)
  - Error case: document has no file_url (400)
  - Error case: no restaurant access (403)
- Test `GET /api/documents/{id}/processing-result`:
  - Success case: document with processing results
  - Error case: document not found (404)
  - Error case: no restaurant access (403)
- Patch targets: `src.core.services.invoice_processor.document_repository`, `src.core.services.invoice_processor.resource_repository`, `src.core.services.invoice_processor.inventory_movement_repository`, `src.core.services.invoice_processor.restaurant_repository`, `src.core.services.invoice_processor.ocr_service`

### Step 13: Run Validation Commands
- Run all validation commands listed below to ensure zero regressions

## Testing Strategy
### Unit Tests
- `InvoiceItem` Pydantic model: valid creation, missing required fields, invalid decimal values
- `InvoiceProcessingResultDTO`: correct serialization of matched/unmatched counts and items
- `StubOCRAdapter.extract_invoice_items()`: returns well-formed list of dicts
- `OCRService.process_invoice()`: transforms raw dicts into `InvoiceItem` instances
- `ResourceRepository.find_by_name()`: case-insensitive match, no match returns None
- `DocumentRepository.update_processing_status()`: sets fields and commits

### Edge Cases
- Document type is NOT "factura_proveedor" — should reject with 400
- Document has no `file_url` — should reject with 400
- All OCR items match existing resources — `unmatched_count` should be 0
- No OCR items match any resource — `matched_count` should be 0, all in unmatched
- OCR adapter raises exception — `processing_status` should be set to "failed"
- Same resource name with different casing — should still match (case-insensitive)
- Document already processed (processing_status = "completed") — should allow re-processing
- Resource stock update after movement — `current_stock` should increase by `quantity`
- Multiple items matching the same resource — each should create its own movement and update cost

## Acceptance Criteria
- A `POST /api/documents/{id}/process-invoice` endpoint exists and processes supplier invoices
- A `GET /api/documents/{id}/processing-result` endpoint returns processing results
- Only documents of type "factura_proveedor" can be processed (400 otherwise)
- Documents without a `file_url` cannot be processed (400 otherwise)
- Matched items update `last_unit_cost` on the corresponding resource
- Matched items create an `entry` inventory movement with reason `compra`
- Resource `current_stock` is incremented by the movement quantity
- Unmatched items are returned in the processing result for manual review
- Processing status is tracked: pending → processing → completed/failed
- Processing results are stored as JSONB on the document record
- OCR adapter is abstracted behind an interface for future provider swappability
- All existing tests pass with zero regressions
- New tests cover success and error paths for both endpoints

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/ -v` — Run all Server tests to validate the feature works with zero regressions
- `cd apps/Server && python -c "from src.core.services.ocr_service import OCRService, InvoiceItem, OCRAdapter; print('OCR service imports OK')"` — Verify OCR service module imports correctly
- `cd apps/Server && python -c "from src.core.services.invoice_processor import invoice_processor; print('Invoice processor imports OK')"` — Verify invoice processor module imports correctly
- `cd apps/Server && python -c "from src.adapter.ocr_stub_adapter import StubOCRAdapter; print('Stub adapter imports OK')"` — Verify stub adapter module imports correctly
- `cd apps/Server && python -c "from src.interface.invoice_dto import InvoiceItemDTO, InvoiceProcessingResultDTO; print('Invoice DTOs imports OK')"` — Verify invoice DTO imports correctly
- `cd apps/Server && python -c "from src.models.document import Document; assert hasattr(Document, 'processing_status'); assert hasattr(Document, 'processing_result'); print('Document model has processing fields')"` — Verify Document model has new columns

## Notes
- The `StubOCRAdapter` is intentionally simple — it returns hardcoded mock data. Real OCR integration (Google Cloud Vision, AWS Textract, OpenAI Vision) should be implemented as a separate adapter class implementing `OCRAdapter`.
- The `InvoiceProcessor` creates inventory movements by directly calling `inventory_movement_repository.create()` and updating `resource.current_stock` manually (same pattern as `InventoryService.create_movement()`). This avoids the auth check in `InventoryService` since the processor already validated access.
- Wave 7 will add automatic recipe cost recalculation triggered by resource cost updates from this OCR pipeline.
- A frontend UI for reviewing and resolving unmatched OCR items should be considered as a future enhancement issue.
- No new dependencies are needed — the feature uses only existing libraries (Pydantic, SQLAlchemy, FastAPI).
- The `processing_result` JSONB field serializes `Decimal` values as strings for JSON compatibility. The `InvoiceProcessingResultDTO` handles deserialization.
