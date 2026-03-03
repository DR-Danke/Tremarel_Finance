# E2E Test: Document Expiration Alert Automation

Test that creating, updating, or deleting documents with expiration dates automatically creates, replaces, or cleans up vencimiento alert events in RestaurantOS.

## User Story

As a restaurant manager
I want the system to automatically create expiration alert events when I upload or update documents with expiration dates
So that I never miss a permit, license, or contract renewal deadline

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials and is logged in
- At least one restaurant created in the system
- At least one person (employee) exists in the restaurant

## Test Steps

### Setup - Navigate to Documents Page

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. If not logged in, log in with test credentials
3. Navigate to `/poc/restaurant-os/documents`
4. Take a screenshot of the documents page
5. **Verify** page loads with "Documentos" heading

### Test: Create Document with Expiration Date (60 days ahead)

6. Click "Agregar Documento" button
7. Fill in the document form:
   - Tipo: Select "Permiso"
   - Fecha de Vencimiento: Set to 60 days from today
   - Persona: Select an available person (if any)
   - Descripcion: "Permiso sanitario para alerta automatica"
8. Click "Agregar Documento" submit button
9. Take a screenshot
10. **Verify** document appears in the list with "Vigente" badge

### Test: Verify Alert Events Created

11. Navigate to `/poc/restaurant-os/events`
12. Take a screenshot of the events page
13. Filter events by type `vencimiento` if filter is available
14. Take a screenshot
15. **Verify** 3 alert events exist linked to the document:
    - One with description "Documento vence en 30 dias"
    - One with description "Documento vence en 7 dias"
    - One with description "Documento vence hoy"

### Test: Update Document Expiration Date (10 days ahead)

16. Navigate back to `/poc/restaurant-os/documents`
17. Click the Edit button (pencil icon) on the created document
18. Change Fecha de Vencimiento to 10 days from today
19. Click "Actualizar Documento" submit button
20. Take a screenshot
21. **Verify** document updated in the list

### Test: Verify Alert Events Replaced

22. Navigate to `/poc/restaurant-os/events`
23. Filter events by type `vencimiento` if filter is available
24. Take a screenshot
25. **Verify** old alert events were replaced with new ones:
    - 30-day alert should NOT exist (would be in the past)
    - 7-day alert should exist (3 days from today)
    - Day-of alert should exist (10 days from today)

### Test: Delete Document Cleans Up Alerts

26. Navigate back to `/poc/restaurant-os/documents`
27. Click the Delete button (trash icon) on the document
28. Confirm deletion in the dialog
29. Take a screenshot
30. **Verify** document removed from table

31. Navigate to `/poc/restaurant-os/events`
32. Filter events by type `vencimiento` if filter is available
33. Take a screenshot
34. **Verify** alert events linked to the deleted document are also removed

## Success Criteria

- Creating a document with an expiration date auto-creates up to 3 vencimiento events (30-day, 7-day, day-of)
- Alert events that would fall on or before today are not created
- Updating a document's expiration date replaces old alert events with new ones
- Deleting a document cleans up associated vencimiento alert events
- Console shows INFO messages from DocumentService about alert creation/deletion

## Technical Verification

- Check browser console for:
  - `INFO [DocumentService]: Created X expiration alerts for document ...`
  - `INFO [DocumentService]: Deleted X expiration alerts for document ...`
  - `INFO [EventRepository]: Creating event type 'vencimiento' ...`
  - No JavaScript errors
- Check network requests:
  - POST `/api/documents` triggers event creation (visible in response or subsequent GET)
  - PUT `/api/documents/{id}` triggers alert replacement
  - DELETE `/api/documents/{id}` triggers alert cleanup

## Notes

- Alert events have type=vencimiento, frequency=none, notification_channel=whatsapp
- The related_document_id field links events to their source document
- Past alert dates (on or before today) are automatically skipped
- The WhatsApp adapter is currently a stub — notifications are logged but not actually sent
