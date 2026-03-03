# Document Management Page

**ADW ID:** 26972c6e
**Date:** 2026-03-03
**Specification:** specs/issue-88-adw-26972c6e-sdlc_planner-document-management-page.md

## Overview

A full CRUD Document Management frontend page for the RestaurantOS module that allows restaurant managers to upload, list, filter, and manage documents (contracts, permits, invoices, licenses, etc.). Documents display color-coded expiration status indicators (green/yellow/red) and support file upload with drag-and-drop. Integrates with the existing backend Document API (ROS-004).

## What Was Built

- **TypeScript type definitions** (`document.ts`) matching backend DTOs with document type/expiration status constants
- **TRExpirationBadge** reusable UI component for color-coded expiration status chips (Vigente/Por Vencer/Vencido)
- **documentService** API service layer with CRUD operations including multipart/form-data file upload
- **useDocuments** state management hook with filter support and auto-fetch
- **TRDocumentForm** form component with react-hook-form, file drag-and-drop upload zone, and create/edit modes
- **RestaurantOSDocumentsPage** full CRUD page with data table, filter dropdowns, and dialog-based forms
- **E2E test specification** for document management validation

## Technical Implementation

### Files Modified

- `apps/Client/src/types/document.ts`: New file — TypeScript interfaces (Document, DocumentCreate, DocumentUpdate, DocumentFilters) and constants (DOCUMENT_TYPES, EXPIRATION_STATUS_OPTIONS)
- `apps/Client/src/components/ui/TRExpirationBadge.tsx`: New file — MUI Chip component with color mapping (success/warning/error) for expiration status display
- `apps/Client/src/services/documentService.ts`: New file — API service with getAll (with filters), create (FormData/multipart), update (JSON), delete methods
- `apps/Client/src/hooks/useDocuments.ts`: New file — State management hook with documents, filters, loading, error state and CRUD callbacks
- `apps/Client/src/components/forms/TRDocumentForm.tsx`: New file — Form with react-hook-form Controller, file drag-and-drop zone, date validation, person dropdown
- `apps/Client/src/pages/restaurantos/RestaurantOSDocumentsPage.tsx`: Modified — Replaced placeholder with full CRUD page including table, filters, and dialogs
- `.claude/commands/e2e/test_document_management.md`: New file — E2E test specification

### Key Changes

- **Multipart file upload**: The create endpoint uses `FormData` with `Content-Type: multipart/form-data` to support file uploads alongside document metadata. The update endpoint uses standard JSON (file updates not supported via update).
- **Server-side filtering**: Both type and expiration status filters are passed as query parameters to `GET /documents`, enabling server-side filtering without client-side data manipulation.
- **Expiration status is computed server-side**: The `expiration_status` field (valid/expiring_soon/expired) is calculated by the backend `DocumentResponseDTO` validator — the frontend only reads and displays it via TRExpirationBadge.
- **Drag-and-drop file upload**: Implemented with native HTML5 drag events (onDragOver, onDragEnter, onDragLeave, onDrop) on a styled MUI Box with a hidden file input — no external library required. Max file size is 10MB with client-side validation.
- **Person integration**: The usePersons hook is used alongside useDocuments to populate the person dropdown in TRDocumentForm, allowing documents to be linked to restaurant persons.

## How to Use

1. Navigate to `/poc/restaurant-os/documents` in the application
2. Select a restaurant from the restaurant selector (if not already selected)
3. The page displays a table of documents for the current restaurant with columns: Tipo, Descripcion, Persona, Fecha de Emision, Fecha de Vencimiento, Estado, Acciones
4. Use the "Filtrar por tipo" dropdown to filter by document type (Contrato, Permiso, Factura, etc.)
5. Use the "Filtrar por estado" dropdown to filter by expiration status (Vigente, Por Vencer, Vencido)
6. Click "Agregar Documento" to open the create dialog:
   - Select document type (required)
   - Optionally set issue date, expiration date, linked person, and description
   - Optionally drag-and-drop or click to upload a file (max 10MB)
   - Click "Agregar Documento" to save
7. Click the edit (pencil) icon to modify a document's metadata
8. Click the delete (trash) icon to remove a document with confirmation

## Configuration

- No additional environment variables required
- The route `/poc/restaurant-os/documents` is already registered in `App.tsx`
- Backend Document API must be available at `/api/documents`
- Restaurant context must be configured (RestaurantProvider)

## Testing

- **TypeScript check**: `cd apps/Client && npx tsc --noEmit`
- **Production build**: `cd apps/Client && npm run build`
- **Backend tests**: `cd apps/Server && python -m pytest tests/ -x -q`
- **E2E tests**: Run the E2E test specification at `.claude/commands/e2e/test_document_management.md`

## Notes

- All UI labels are in Spanish (Colombian) as per project convention
- Document types are stored as lowercase Spanish values (`contrato`, `permiso`, `factura`, `licencia`, `factura_proveedor`, `certificado`, `otro`)
- The page follows the same CRUD pattern as RestaurantOSPersonsPage for consistency
- File upload is only available during document creation, not during edit
- Documents with no expiration date default to "valid" (green) status
- The expiration_date form field validates that it must be after issue_date when both are provided
