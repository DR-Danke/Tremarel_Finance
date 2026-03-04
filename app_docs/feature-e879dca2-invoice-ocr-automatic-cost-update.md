# Invoice OCR & Automatic Cost Update

**ADW ID:** e879dca2
**Date:** 2026-03-03
**Specification:** specs/issue-95-adw-e879dca2-sdlc_planner-invoice-ocr-automatic-cost-update.md

## Overview

Adds an OCR-based invoice processing pipeline to RestaurantOS. When a supplier invoice document (`factura_proveedor`) is submitted for processing, the system extracts line items via a pluggable OCR adapter, matches them to existing resources by name (case-insensitive), updates `last_unit_cost`, creates `entry` inventory movements, and flags unmatched items for manual review. Processing status and results are stored on the document record as JSONB.

## What Was Built

- **OCR adapter abstraction** (`OCRAdapter` ABC) for provider swappability (Google Cloud Vision, AWS Textract, etc.)
- **Stub OCR adapter** returning mock invoice data for development/testing
- **Invoice processor service** orchestrating the full pipeline: OCR extraction → resource matching → cost update → inventory movement creation
- **Two new REST endpoints**: `POST /api/documents/{id}/process-invoice` and `GET /api/documents/{id}/processing-result`
- **Document model extensions**: `processing_status` and `processing_result` (JSONB) columns
- **Resource repository enhancement**: case-insensitive `find_by_name()` lookup
- **Invoice DTOs** for typed API responses
- **SQL migration** adding processing columns with a partial index
- **Comprehensive tests**: 456 lines of API integration tests + 195 lines of model/DTO unit tests

## Technical Implementation

### Files Modified

- `apps/Server/src/models/document.py`: Added `processing_status` (String) and `processing_result` (JSON) columns
- `apps/Server/src/interface/document_dto.py`: Added processing fields to `DocumentResponseDTO` and ORM validator
- `apps/Server/src/repository/document_repository.py`: Added `update_processing_status()` method
- `apps/Server/src/repository/resource_repository.py`: Added `find_by_name()` with case-insensitive matching via `func.lower()`
- `apps/Server/src/adapter/rest/document_routes.py`: Added `process-invoice` and `processing-result` endpoints (placed before `/{document_id}` catch-all)
- `apps/Server/tests/test_document_api.py`: Added `processing_status`/`processing_result` to mock fixtures
- `apps/Server/tests/test_document_expiration_alert_api.py`: Added processing fields to mock fixtures

### New Files

- `apps/Server/src/core/services/ocr_service.py`: `OCRAdapter` ABC, `InvoiceItem` Pydantic model, `OCRService` wrapper
- `apps/Server/src/core/services/invoice_processor.py`: `InvoiceProcessor` singleton orchestrating the full pipeline
- `apps/Server/src/adapter/ocr_stub_adapter.py`: `StubOCRAdapter` with 4 mock items (last one intentionally unmatched)
- `apps/Server/src/interface/invoice_dto.py`: `InvoiceItemDTO`, `InvoiceMatchedItemDTO`, `InvoiceProcessingResultDTO`
- `apps/Server/database/alter_document_add_processing_fields.sql`: Migration adding columns + partial index
- `apps/Server/tests/test_invoice_ocr_api.py`: API integration tests (success, 400, 403, 404, OCR failure)
- `apps/Server/tests/test_invoice_ocr_model.py`: Unit tests for models, DTOs, and stub adapter

### Key Changes

- **Pluggable OCR architecture**: `OCRAdapter` ABC defines `extract_invoice_items(file_url) -> list[dict]`. `OCRService` validates raw dicts into `InvoiceItem` Pydantic models. New providers are added by implementing `OCRAdapter` and swapping the adapter in `invoice_processor.py`.
- **Processing pipeline**: `InvoiceProcessor.process_invoice_document()` fetches the document, validates type/file, runs OCR, matches items to resources via `find_by_name()`, updates `last_unit_cost`, creates inventory movements (type=`entry`, reason=`compra`), updates `current_stock`, and stores results on the document.
- **Status tracking**: Documents track `processing_status` (`pending` → `processing` → `completed`/`failed`) and store full results in `processing_result` JSONB, including matched/unmatched item details.
- **Error handling**: OCR failures set status to `failed` with error details. Wrong document type or missing file returns 400. Missing document returns 404. No restaurant access returns 403.
- **Decimal serialization**: `InvoiceItem` uses `Decimal` for quantity/price precision. Values are serialized as strings in `processing_result` JSONB for JSON compatibility.

## How to Use

1. Upload a document with type `factura_proveedor` and a `file_url` via `POST /api/documents/`
2. Trigger OCR processing: `POST /api/documents/{document_id}/process-invoice` (requires auth)
3. The system extracts line items, matches them to resources, updates costs, and creates inventory movements
4. Check results: `GET /api/documents/{document_id}/processing-result` returns status and matched/unmatched items
5. Review unmatched items manually — these are products not found in the resource catalog

## Configuration

- **OCR adapter**: Currently uses `StubOCRAdapter` (mock data). To use a real provider, implement `OCRAdapter` and replace the adapter in `apps/Server/src/core/services/invoice_processor.py`
- **Database migration**: Run `apps/Server/database/alter_document_add_processing_fields.sql` to add processing columns to the document table

## Testing

```bash
# Run all server tests (includes invoice OCR tests)
cd apps/Server && python -m pytest tests/ -v

# Run only invoice OCR tests
cd apps/Server && python -m pytest tests/test_invoice_ocr_api.py tests/test_invoice_ocr_model.py -v

# Verify module imports
cd apps/Server && python -c "from src.core.services.invoice_processor import invoice_processor; print('OK')"
```

## Notes

- The `StubOCRAdapter` returns 4 hardcoded items (Tomate, Aceite de oliva, Harina de trigo, Salsa BBQ Especial). The last item is intentionally unlikely to match, to exercise the unmatched flow.
- Inventory movements are created directly via `inventory_movement_repository.create()` (bypassing `InventoryService` auth check, since `InvoiceProcessor` already validates access).
- Future enhancements: real OCR adapter integration, frontend UI for unmatched item review, automatic recipe cost recalculation triggered by resource cost updates (Wave 7).
