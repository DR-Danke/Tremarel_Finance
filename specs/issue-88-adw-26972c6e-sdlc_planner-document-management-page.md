# Feature: Document Management Page

## Metadata
issue_number: `88`
adw_id: `26972c6e`
issue_json: ``

## Feature Description
Build a Document Management frontend page for the RestaurantOS module that allows restaurant managers to upload, list, filter, and manage documents (contracts, permits, invoices, licenses, etc.). Documents display color-coded expiration status indicators: green for valid, yellow for expiring soon (within 30 days), and red for expired. The page includes file upload with drag-and-drop support, type and expiration status filters, and full CRUD operations via dialog-based forms. The backend API is already fully implemented (ROS-004) and supports multipart/form-data file uploads, expiration status computation, and restaurant-scoped authorization.

## User Story
As a restaurant manager
I want to upload, list, and manage documents with expiration tracking
So that I can keep track of contracts, permits, licenses, and other important documents and know at a glance which ones need renewal

## Problem Statement
Restaurant managers need to manage many types of documents (contracts, permits, invoices, licenses, certificates) and track their expiration dates. Without a centralized document management page, documents may expire without notice, leading to compliance issues and operational disruptions.

## Solution Statement
Create a Document Management frontend page that mirrors the existing Person Management page pattern. The page will integrate with the existing backend Document API to provide CRUD operations, file upload support, and color-coded expiration status badges. Type and status filter dropdowns allow managers to quickly find relevant documents. The TRDocumentForm component uses react-hook-form with MUI for consistent form handling, while the TRExpirationBadge component provides visual expiration status at a glance.

## Relevant Files
Use these files to implement the feature:

**Reference files (follow these patterns):**
- `apps/Client/src/pages/restaurantos/RestaurantOSPersonsPage.tsx` — Reference page pattern for CRUD page with dialogs, table, filters
- `apps/Client/src/components/forms/TRPersonForm.tsx` — Reference form pattern with react-hook-form, Controller, MUI, create/edit modes
- `apps/Client/src/services/personService.ts` — Reference service pattern with apiClient, logging, error handling
- `apps/Client/src/hooks/usePersons.ts` — Reference hook pattern with state, CRUD callbacks, auto-fetch
- `apps/Client/src/types/person.ts` — Reference type definitions pattern
- `apps/Client/src/api/clients/index.ts` — API client with JWT interceptor (used by all services)
- `apps/Client/src/hooks/useRestaurant.ts` — Restaurant context hook for current restaurant
- `apps/Client/src/pages/restaurantos/TRNoRestaurantPrompt.tsx` — No-restaurant fallback component
- `apps/Client/src/App.tsx` — Route registration (document route already registered at `/poc/restaurant-os/documents`)

**Backend reference (already implemented, API contract):**
- `apps/Server/src/adapter/rest/document_routes.py` — Backend API endpoints (POST multipart, GET with filters, PUT, DELETE)
- `apps/Server/src/interface/document_dto.py` — Backend DTOs showing field names, types, validation, expiration_status computation
- `apps/Server/src/models/document.py` — Database model for reference

**Documentation files to read:**
- `app_docs/feature-de82eb81-person-management-page.md` — Person management page implementation details (pattern to follow)
- `app_docs/feature-95deee5d-document-entity-crud-backend.md` — Document backend API details
- `app_docs/feature-342b3948-restaurant-selector-multitenant-navigation.md` — RestaurantContext integration details
- `.claude/commands/test_e2e.md` — E2E test runner instructions
- `.claude/commands/e2e/test_person_management.md` — Reference E2E test pattern for CRUD pages

**Files to modify:**
- `apps/Client/src/pages/restaurantos/RestaurantOSDocumentsPage.tsx` — Replace placeholder with full CRUD page

### New Files
- `apps/Client/src/types/document.ts` — Document TypeScript interfaces and constants
- `apps/Client/src/services/documentService.ts` — Document API service with CRUD operations
- `apps/Client/src/hooks/useDocuments.ts` — Document state management hook
- `apps/Client/src/components/forms/TRDocumentForm.tsx` — Document form with file upload and drag-and-drop
- `apps/Client/src/components/ui/TRExpirationBadge.tsx` — Color-coded expiration status chip
- `.claude/commands/e2e/test_document_management.md` — E2E test specification

## Implementation Plan
### Phase 1: Foundation
Create the TypeScript type definitions that match the backend DTOs (Document, DocumentCreate, DocumentUpdate, DocumentFilters), the document constants (DOCUMENT_TYPES with Spanish labels), and the TRExpirationBadge UI component. These are foundational types and components needed by all subsequent layers.

### Phase 2: Core Implementation
Build the document service layer (documentService.ts) with CRUD methods including multipart/form-data support for file uploads, the useDocuments hook for state management with filter support, and the TRDocumentForm component with react-hook-form, file upload drag-and-drop zone, and create/edit modes.

### Phase 3: Integration
Replace the placeholder RestaurantOSDocumentsPage with the full CRUD page integrating all components: data table with columns (Tipo, Descripcion, Persona, Fecha Emision, Fecha Vencimiento, Estado, Acciones), TRExpirationBadge in the Estado column, filter dropdowns for type and expiration status, and Add/Edit/Delete dialogs. The route is already registered in App.tsx.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_person_management.md` to understand the E2E test pattern
- Create `.claude/commands/e2e/test_document_management.md` following the person management E2E test pattern
- Include test steps for: page load, empty state, form validation, create document with file, create document without file, filter by type, filter by expiration status, edit document, delete document, expiration badge color verification
- Include success criteria and technical verification sections

### Step 2: Create Document TypeScript Types
- Create `apps/Client/src/types/document.ts`
- Define `DocumentType` as a union type of: `'contrato' | 'permiso' | 'factura' | 'licencia' | 'factura_proveedor' | 'certificado' | 'otro'`
- Define `ExpirationStatus` as: `'valid' | 'expiring_soon' | 'expired'`
- Define `DOCUMENT_TYPES` constant array with value/label pairs for Spanish display: Contrato, Permiso, Factura, Licencia, Factura Proveedor, Certificado, Otro
- Define `EXPIRATION_STATUS_OPTIONS` constant with value/label pairs: Vigente, Por Vencer, Vencido
- Define `Document` interface matching `DocumentResponseDTO` fields: id, restaurant_id, type, file_url (string | null), issue_date (string | null), expiration_date (string | null), person_id (string | null), description (string | null), expiration_status (ExpirationStatus), created_at (string), updated_at (string | null)
- Define `DocumentCreate` interface: restaurant_id, type, issue_date?, expiration_date?, person_id?, description?
- Define `DocumentUpdate` interface: type?, issue_date?, expiration_date?, person_id?, description?
- Define `DocumentFilters` interface: type? (DocumentType), expiration_status? (ExpirationStatus)

### Step 3: Create TRExpirationBadge Component
- Create `apps/Client/src/components/ui/TRExpirationBadge.tsx`
- Accept `status` prop of type `ExpirationStatus`
- Use MUI `Chip` component with color mapping:
  - `valid` → green color (success), label "Vigente"
  - `expiring_soon` → yellow/orange color (warning), label "Por Vencer"
  - `expired` → red color (error), label "Vencido"
- Small size chip for table usage
- Log rendering: `console.log('INFO [TRExpirationBadge]: Rendering status:', status)`

### Step 4: Create Document Service
- Create `apps/Client/src/services/documentService.ts`
- Follow `personService.ts` pattern exactly
- Import `apiClient` from `@/api/clients`
- Import types from `@/types/document`
- Implement methods:
  - `getAll(restaurantId: string, type?: string, expirationStatus?: string): Promise<Document[]>` — GET `/documents?restaurant_id=...&type=...&expiration_status=...`
  - `create(data: DocumentCreate, file?: File): Promise<Document>` — POST `/documents` with FormData (multipart/form-data). Use `FormData` object, append all fields, append file if present. Set header `Content-Type: multipart/form-data`
  - `update(id: string, data: DocumentUpdate): Promise<Document>` — PUT `/documents/{id}` with JSON body
  - `delete(id: string): Promise<void>` — DELETE `/documents/{id}`
- Add comprehensive INFO/ERROR logging for every operation

### Step 5: Create useDocuments Hook
- Create `apps/Client/src/hooks/useDocuments.ts`
- Follow `usePersons.ts` pattern exactly
- Accept `restaurantId: string | null` parameter
- State: `documents` (Document[]), `isLoading`, `error`, `filters` (DocumentFilters)
- Callbacks: `fetchDocuments`, `createDocument(data: DocumentCreate, file?: File)`, `updateDocument(id, data)`, `deleteDocument(id)`, `setFilters`
- Guard on null restaurantId
- Auto-fetch on mount and when restaurantId or filters change
- Error messages in Spanish: "Error al cargar documentos", "Error al crear documento", etc.
- Log all operations with `INFO [useDocuments]:` prefix

### Step 6: Create TRDocumentForm Component
- Create `apps/Client/src/components/forms/TRDocumentForm.tsx`
- Follow `TRPersonForm.tsx` pattern with react-hook-form and Controller
- Props: `onSubmit`, `initialData?` (Document), `restaurantId`, `onCancel`, `isSubmitting?`, `persons` (Person[] for person_id dropdown)
- Form fields:
  - **Tipo** (required): Select from DOCUMENT_TYPES constant. Use Controller with FormControl/Select/MenuItem
  - **Fecha de Emision** (optional): TextField type="date" with InputLabelProps shrink
  - **Fecha de Vencimiento** (optional): TextField type="date" with InputLabelProps shrink. Custom validation: must be after issue_date if both provided
  - **Persona** (optional): Select from persons prop. Show "Ninguna" as empty option
  - **Descripcion** (optional): TextField multiline, 3 rows
  - **Archivo** (optional, create mode only): File input with drag-and-drop styled zone using MUI Box with dashed border. Accept any file type. Max 10MB validation. Show file name after selection. Use a hidden `<input type="file">` with a styled drop zone that responds to drag events (onDragOver, onDragLeave, onDrop) and click to browse
- Submit button: "Agregar Documento" (create) / "Actualizar Documento" (edit)
- Cancel button
- Loading states with CircularProgress
- Log form submission: `INFO [TRDocumentForm]: Submitting document form`

### Step 7: Replace RestaurantOSDocumentsPage
- Replace the placeholder content in `apps/Client/src/pages/restaurantos/RestaurantOSDocumentsPage.tsx`
- Follow `RestaurantOSPersonsPage.tsx` pattern exactly
- Import and use: `useRestaurant`, `useDocuments`, `usePersons` (for person dropdown in form), `TRDocumentForm`, `TRExpirationBadge`, `TRNoRestaurantPrompt`
- **Header**: "Documentos" title (h4), current restaurant name (h6), "Agregar Documento" button with Add icon
- **Error display**: Alert component for error state
- **Filters row**: Two dropdowns side by side:
  - "Filtrar por tipo" — Select with "Todos" + DOCUMENT_TYPES options (Spanish labels)
  - "Filtrar por estado" — Select with "Todos" + EXPIRATION_STATUS_OPTIONS (Vigente/Por Vencer/Vencido)
- **Data table** with columns:
  - Tipo — Display Spanish label from DOCUMENT_TYPES mapping
  - Descripcion — Show description or "—"
  - Persona — Look up person name from persons list by person_id, or "—"
  - Fecha de Emision — Format date or "—"
  - Fecha de Vencimiento — Format date or "—"
  - Estado — TRExpirationBadge component
  - Acciones — Edit (pencil) and Delete (trash) IconButtons
- **Empty state**: "No se encontraron documentos" when no documents match filters
- **Loading state**: CircularProgress while fetching
- **Add Dialog**: Dialog with TRDocumentForm (create mode), pass persons list
- **Edit Dialog**: Dialog with TRDocumentForm (edit mode), pre-populated with selected document data
- **Delete Confirmation Dialog**: "Eliminar Documento" title, "¿Está seguro que desea eliminar este documento?" message, Cancelar/Eliminar buttons
- **DOCUMENT_TYPE_LABELS** mapping: contrato → "Contrato", permiso → "Permiso", factura → "Factura", licencia → "Licencia", factura_proveedor → "Factura Proveedor", certificado → "Certificado", otro → "Otro"
- Log all dialog open/close and CRUD operations with `INFO [RestaurantOSDocumentsPage]:` prefix

### Step 8: Run Validation Commands
- Run all validation commands listed below to confirm zero regressions

## Testing Strategy
### Unit Tests
- No new backend tests needed (backend is already implemented and tested)
- Frontend validation is done through TypeScript type checking, build validation, and E2E testing

### Edge Cases
- No restaurant selected → TRNoRestaurantPrompt displayed
- Empty documents list → "No se encontraron documentos" message
- Document with no expiration_date → status is "valid" (green badge)
- Document with expiration_date in the past → status is "expired" (red badge)
- Document with expiration_date within 30 days → status is "expiring_soon" (yellow badge)
- File upload exceeding 10MB → client-side validation error
- expiration_date before issue_date → form validation error
- Document with no person_id → "—" in Persona column
- Document with no description → "—" in Descripcion column
- Multiple filter combinations (type + status) applied simultaneously
- Create document without file upload (metadata only)
- Create document with file upload (multipart)

## Acceptance Criteria
- Document management page loads at `/poc/restaurant-os/documents` with "Documentos" heading
- Page shows current restaurant name from RestaurantContext
- No-restaurant state shows TRNoRestaurantPrompt component
- Data table displays documents with columns: Tipo, Descripcion, Persona, Fecha de Emision, Fecha de Vencimiento, Estado, Acciones
- TRExpirationBadge shows correct colors: green (Vigente), yellow (Por Vencer), red (Vencido)
- Type filter dropdown filters documents by document type (server-side)
- Expiration status filter dropdown filters documents by status (server-side)
- "Agregar Documento" button opens dialog with TRDocumentForm
- Form fields: Tipo (required select), Fecha de Emision, Fecha de Vencimiento, Persona (optional select), Descripcion, Archivo (file upload with drag-and-drop)
- Form validation: type is required, expiration_date must be after issue_date, file max 10MB
- Creating a document adds it to the table
- Edit button opens form pre-populated with document data
- Updating a document reflects changes in the table
- Delete button shows confirmation dialog with Spanish text
- Confirming delete removes document from table
- All UI labels are in Spanish (Colombian)
- Console shows INFO log messages for all operations
- TypeScript compilation passes with no errors
- Production build completes successfully

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/ -x -q` — Run Server tests to validate zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate the feature compiles with zero type errors
- `cd apps/Client && npm run build` — Run Client production build to validate the feature builds successfully

Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_document_management.md` E2E test file to validate this functionality works.

## Notes
- The backend Document API is fully implemented (all CRUD endpoints operational at `/api/documents`)
- The backend uses `Form(...)` fields for document creation (multipart/form-data) since it supports file upload. The frontend must send FormData, not JSON, for the create endpoint
- The update endpoint (`PUT /documents/{id}`) uses JSON body (DocumentUpdateDTO), not FormData — file updates are not supported via update
- Document type values are stored as lowercase Spanish (`contrato`, `permiso`, `factura`, `licencia`, `factura_proveedor`, `certificado`, `otro`) and displayed with capitalized Spanish labels
- The `expiration_status` field is computed server-side by the `DocumentResponseDTO` model validator — the frontend only reads it, never sends it
- The route `/poc/restaurant-os/documents` is already registered in `App.tsx` — no routing changes needed
- The `usePersons` hook should be used alongside `useDocuments` to populate the person dropdown in TRDocumentForm
- Both type and expiration_status filters are server-side (passed as query parameters to the GET `/documents` API)
- Date fields in the form should use native HTML date inputs (`TextField type="date"`) with `InputLabelProps={{ shrink: true }}` for proper MUI label behavior
- The drag-and-drop file upload zone should be implemented with native HTML5 drag events (onDragOver, onDragEnter, onDragLeave, onDrop) on a styled MUI Box, plus a hidden file input triggered on click — no external library needed
