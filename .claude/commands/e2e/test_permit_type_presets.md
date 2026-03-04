# E2E Test: Permit Type Presets with Custom Alert Schedules

Test that permit type presets automatically apply preset-specific alert schedules when documents are created, and that custom alert windows can override preset defaults.

## User Story

As a restaurant manager
I want preset document types with pre-configured alert schedules for common permits
So that I get the right alerts at the right intervals for each permit type without manual configuration, while still being able to customize alert windows when needed

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

### Test: Verify Permit Preset Types in Dropdown

6. Click "Agregar Documento" button
7. Click the "Tipo" dropdown
8. Take a screenshot
9. **Verify** the following permit preset types appear in the dropdown:
   - Certificado de Manipulación de Alimentos
   - Permiso de Bomberos
   - Registro de Cámara de Comercio
   - Servicio de Extintores
   - Certificado de Inspección Sanitaria

### Test: Select Preset Type and Verify Alert Schedule Display

10. Select "Certificado de Inspección Sanitaria" from the Tipo dropdown
11. Take a screenshot
12. **Verify** an info box appears below the type dropdown showing:
    - Preset name: "Certificado de Inspección Sanitaria"
    - Alert schedule chips: "30 días", "14 días", "7 días"
    - Notification channel: "whatsapp"

### Test: Create Document with Preset Type (Sanidad)

13. Set Fecha de Vencimiento to 60 days from today
14. Optionally select a Persona
15. Set Descripcion to "Certificado sanitario con preset"
16. Click "Agregar Documento" submit button
17. Take a screenshot
18. **Verify** document appears in the list

### Test: Verify Preset Alert Events Created (Sanidad - 3 events)

19. Navigate to `/poc/restaurant-os/events`
20. Take a screenshot
21. Filter events by type `vencimiento` if filter is available
22. Take a screenshot
23. **Verify** 3 alert events were created with descriptions using the preset name:
    - "Certificado de Inspección Sanitaria vence en 30 dias"
    - "Certificado de Inspección Sanitaria vence en 14 dias"
    - "Certificado de Inspección Sanitaria vence en 7 dias"

### Test: Create Document with Bomberos Preset (1 event only)

24. Navigate back to `/poc/restaurant-os/documents`
25. Click "Agregar Documento" button
26. Select "Permiso de Bomberos" from the Tipo dropdown
27. Take a screenshot
28. **Verify** alert schedule shows only "0 días" (day-of)
29. Set Fecha de Vencimiento to 60 days from today
30. Set Descripcion to "Permiso bomberos con preset"
31. Click "Agregar Documento" submit button
32. Take a screenshot

### Test: Verify Bomberos Alert Events (1 event)

33. Navigate to `/poc/restaurant-os/events`
34. Take a screenshot
35. **Verify** only 1 vencimiento event was created for the Bomberos document:
    - "Permiso de Bomberos vence hoy"

### Test: Custom Override of Preset Alert Windows

36. Navigate back to `/poc/restaurant-os/documents`
37. Click "Agregar Documento" button
38. Select "Certificado de Inspección Sanitaria" from the Tipo dropdown
39. **Verify** preset alert schedule is displayed (30, 14, 7 días)
40. Enable the "Personalizar alertas" toggle/checkbox
41. Enter custom alert windows: "45, 15" in the custom alert input
42. Take a screenshot
43. Set Fecha de Vencimiento to 60 days from today
44. Set Descripcion to "Sanitario con alertas personalizadas"
45. Click "Agregar Documento" submit button
46. Take a screenshot

### Test: Verify Custom Alert Windows Override

47. Navigate to `/poc/restaurant-os/events`
48. Take a screenshot
49. **Verify** exactly 2 vencimiento events were created for the custom override document:
    - "Certificado de Inspección Sanitaria vence en 45 dias"
    - "Certificado de Inspección Sanitaria vence en 15 dias"
50. **Verify** the preset default windows (30, 14, 7) were NOT used

## Success Criteria

- Permit preset types appear in the document type dropdown with Spanish labels
- Selecting a preset type displays the preset's alert schedule and notification channel
- Creating a document with "sanidad" preset creates 3 vencimiento events at 30, 14, 7 days
- Creating a document with "bomberos" preset creates 1 vencimiento event at day-of only
- Event descriptions include the preset display name (e.g., "Certificado de Inspección Sanitaria vence en 30 dias")
- Custom alert windows override preset defaults when provided
- The "Personalizar alertas" toggle allows entering custom comma-separated day values

## Technical Verification

- Check browser console for:
  - `INFO [DocumentService]: Created X expiration alerts for document ...`
  - `INFO [DocumentService]: Using preset alert windows for type ...` or `INFO [DocumentService]: Using custom alert windows ...`
  - No JavaScript errors
- Check network requests:
  - GET `/api/documents/permit-presets` returns 5 presets
  - POST `/api/documents` with preset type creates correct number of events
  - POST `/api/documents` with custom_alert_windows uses custom windows

## Notes

- Permit presets are defined server-side as configuration constants
- The preset notification_channel ("email" vs "whatsapp") is used when creating alert events
- Custom alert windows are passed as a JSON-encoded string in multipart form data
- Non-preset document types (e.g., "contrato") still use the default [30, 7, 0] alert windows
