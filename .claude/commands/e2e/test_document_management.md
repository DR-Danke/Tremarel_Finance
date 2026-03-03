# E2E Test: Document Management

Test that the RestaurantOS document management page works correctly, including listing, creating, editing, filtering, and deleting documents (contracts, permits, invoices, licenses, etc.) with expiration status tracking.

## User Story

As a restaurant manager
I want to upload, list, and manage documents with expiration tracking
So that I can keep track of contracts, permits, licenses, and other important documents and know at a glance which ones need renewal

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials and is logged in
- At least one restaurant created in the system

## Test Steps

### Setup - Navigate to Documents Page

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. If not logged in, log in with test credentials
3. Navigate to `/poc/restaurant-os/documents`
4. Take a screenshot of the documents page
5. **Verify** page loads with:
   - "Documentos" heading (h4)
   - Current restaurant name displayed (h6)
   - "Agregar Documento" button is visible
   - Empty state message "No se encontraron documentos" or existing documents table

### Test: Empty State

6. **Verify** if no documents exist:
   - Empty state message "No se encontraron documentos" is displayed
7. Take a screenshot of empty state

### Test: Create Document - Form Validation

8. Click "Agregar Documento" button
9. Take a screenshot of the add document dialog
10. **Verify** dialog displays with title "Agregar Documento" and form fields:
    - Tipo (select, required: Contrato/Permiso/Factura/Licencia/Factura Proveedor/Certificado/Otro)
    - Fecha de Emisión (date, optional)
    - Fecha de Vencimiento (date, optional)
    - Persona (select, optional)
    - Descripción (text, optional, multiline)
    - Archivo (file upload with drag-and-drop zone)
    - "Cancelar" and "Agregar Documento" buttons

11. Submit the form without filling required fields
12. Take a screenshot
13. **Verify** validation error displayed:
    - "El tipo es obligatorio" error on Tipo field

### Test: Create First Document (without file)

14. Fill in the document form:
    - Tipo: Select "Contrato"
    - Fecha de Emisión: "2025-01-15"
    - Fecha de Vencimiento: "2027-01-15"
    - Descripción: "Contrato de arrendamiento local"

15. Click "Agregar Documento" submit button
16. Take a screenshot
17. **Verify** dialog closes
18. **Verify** document appears in the data table with:
    - Tipo: "Contrato"
    - Descripción: "Contrato de arrendamiento local"
    - Estado: "Vigente" (green badge, since expiration is in the future)
    - Edit and Delete action buttons visible

### Test: Create Second Document (with file)

19. Click "Agregar Documento" button
20. Fill in:
    - Tipo: Select "Permiso"
    - Fecha de Emisión: "2025-06-01"
    - Fecha de Vencimiento: Set to a date within 30 days from today
    - Descripción: "Permiso sanitario"
    - Archivo: Upload a test file (if available)
21. Click "Agregar Documento" submit button
22. Take a screenshot
23. **Verify** both documents visible in the table

### Test: Create Third Document (expired)

24. Click "Agregar Documento" button
25. Fill in:
    - Tipo: Select "Licencia"
    - Fecha de Emisión: "2024-01-01"
    - Fecha de Vencimiento: "2025-01-01" (past date)
    - Descripción: "Licencia de funcionamiento vencida"
26. Click "Agregar Documento" submit button
27. Take a screenshot
28. **Verify** document appears with Estado: "Vencido" (red badge)

### Test: Expiration Badge Colors

29. **Verify** expiration badges display correct colors:
    - "Vigente" badge is green (success color) for valid documents
    - "Por Vencer" badge is yellow/orange (warning color) for expiring soon documents
    - "Vencido" badge is red (error color) for expired documents
30. Take a screenshot showing different badge colors

### Test: Filter by Type

31. Locate the "Filtrar por tipo" select dropdown
32. Select "Contrato" from the type filter
33. Take a screenshot
34. **Verify** only contract documents appear in the table

35. Select "Licencia" from the type filter
36. Take a screenshot
37. **Verify** only license documents appear

38. Select "Todos" to reset the filter
39. **Verify** all documents visible again

### Test: Filter by Expiration Status

40. Locate the "Filtrar por estado" select dropdown
41. Select "Vigente" from the status filter
42. Take a screenshot
43. **Verify** only documents with "Vigente" badge appear

44. Select "Vencido" from the status filter
45. Take a screenshot
46. **Verify** only documents with "Vencido" badge appear

47. Select "Todos" to reset the filter
48. **Verify** all documents visible again

### Test: Combined Filters

49. Select "Contrato" from type filter AND "Vigente" from status filter
50. Take a screenshot
51. **Verify** only valid contract documents appear
52. Reset both filters to "Todos"

### Test: Edit Document

53. Click the Edit button (pencil icon) on the first document
54. Take a screenshot of the edit dialog
55. **Verify** dialog title is "Editar Documento"
56. **Verify** form is pre-populated with document data:
    - Tipo field shows current type
    - Date fields show current dates
    - Descripción shows current description
57. **Verify** file upload field is NOT shown in edit mode

58. Change Descripción to "Contrato de arrendamiento actualizado"
59. Click "Actualizar Documento" submit button
60. Take a screenshot
61. **Verify** dialog closes
62. **Verify** table shows updated description

### Test: Delete Document

63. Click the Delete button (trash icon) on the expired document
64. Take a screenshot of the delete confirmation dialog
65. **Verify** dialog title is "Eliminar Documento"
66. **Verify** confirmation text: "¿Está seguro que desea eliminar este documento?"
67. **Verify** "Cancelar" and "Eliminar" buttons visible

68. Click "Cancelar" to abort deletion
69. **Verify** document still in the table

70. Click Delete button on the same document again
71. Click "Eliminar" to confirm
72. Take a screenshot
73. **Verify** document removed from table

### Test: Date Validation

74. Click "Agregar Documento" button
75. Fill in:
    - Tipo: Select "Factura"
    - Fecha de Emisión: "2025-06-01"
    - Fecha de Vencimiento: "2025-01-01" (before issue date)
76. Submit the form
77. **Verify** validation error: "La fecha de vencimiento debe ser posterior a la fecha de emisión"
78. Click "Cancelar"

### Test: No Restaurant State

79. If possible, test with no restaurant selected
80. **Verify** `TRNoRestaurantPrompt` component is shown instead of the documents page

## Success Criteria

- Document management page loads at `/poc/restaurant-os/documents` with "Documentos" heading
- Page shows current restaurant name from RestaurantContext
- No-restaurant state shows TRNoRestaurantPrompt component
- Data table displays documents with columns: Tipo, Descripción, Persona, Fecha de Emisión, Fecha de Vencimiento, Estado, Acciones
- TRExpirationBadge shows correct colors: green (Vigente), yellow (Por Vencer), red (Vencido)
- Type filter dropdown filters documents by document type (server-side)
- Expiration status filter dropdown filters documents by status (server-side)
- "Agregar Documento" button opens dialog with TRDocumentForm
- Form fields: Tipo (required select), Fecha de Emisión, Fecha de Vencimiento, Persona (optional select), Descripción, Archivo (file upload with drag-and-drop)
- Form validation: type is required, expiration_date must be after issue_date, file max 10MB
- Creating a document adds it to the table
- Edit button opens form pre-populated with document data (no file upload in edit mode)
- Updating a document reflects changes in the table
- Delete button shows confirmation dialog with Spanish text
- Confirming delete removes document from table
- All UI labels are in Spanish (Colombian)
- Console shows INFO log messages for all operations

## Technical Verification

- Check browser console for:
  - INFO log messages for document operations
  - `INFO [DocumentService]: Fetching documents for restaurant...`
  - `INFO [useDocuments]: Fetched X documents`
  - `INFO [TRDocumentForm]: Submitting document form`
  - `INFO [RestaurantOSDocumentsPage]: Creating document`
  - No JavaScript errors
  - No React warnings
- Check network requests:
  - GET `/api/documents?restaurant_id=...` on page load
  - POST `/api/documents` (multipart/form-data) on create
  - PUT `/api/documents/{id}` (JSON) on update
  - DELETE `/api/documents/{id}` on delete
  - Authorization header present in all requests

## Notes

- The backend Document API is fully implemented (all CRUD endpoints operational)
- Document type values are stored as lowercase Spanish (`contrato`, `permiso`, `factura`, `licencia`, `factura_proveedor`, `certificado`, `otro`) and displayed with capitalized labels
- The `expiration_status` field is computed server-side — the frontend only reads it
- The create endpoint uses multipart/form-data (supports file upload); the update endpoint uses JSON
- Both type and expiration_status filters are server-side (passed as query parameters)
- Route `/poc/restaurant-os/documents` is already registered in App.tsx
