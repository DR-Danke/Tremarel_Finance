# Permit Type Presets with Custom Alert Schedules

**ADW ID:** 367a82ca
**Date:** 2026-03-04
**Specification:** specs/issue-99-adw-367a82ca-sdlc_planner-permit-type-presets-alert-schedules.md

## Overview

Adds preset document types for 5 common restaurant permits (e.g., Certificado de Manipulación de Alimentos, Permiso de Bomberos, Certificado de Inspección Sanitaria) with pre-configured alert schedules. When a document of a preset type is created, the appropriate alert windows and notification channel are automatically applied instead of the default 30/7/0 days. Users can also override preset alerts with custom alert windows on a per-document basis.

## What Was Built

- **Permit presets configuration** with 5 Costa Rican/Colombian restaurant permit types, each with specific alert windows and notification channels
- **GET /api/documents/permit-presets** endpoint returning available presets
- **Three-tier alert window resolution**: custom > preset > default in `create_expiration_alerts()`
- **Preset-aware event descriptions** using the preset display name (e.g., "Certificado de Inspección Sanitaria vence en 30 dias")
- **Per-preset notification channels** (email for Cámara de Comercio, WhatsApp for others)
- **Custom alert windows** support via `custom_alert_windows` parameter on document creation
- **Frontend preset display** showing alert schedule chips and notification channel when a preset type is selected
- **Custom alert override UI** with a "Personalizar alertas" toggle and comma-separated input

## Technical Implementation

### Files Modified

- `apps/Server/src/config/permit_presets.py` (new): Defines `PERMIT_PRESETS` dictionary with 5 presets
- `apps/Server/src/core/services/document_service.py`: Updated `create_expiration_alerts()` with three-tier resolution (custom > preset > default), preset-aware descriptions, and per-preset notification channels
- `apps/Server/src/adapter/rest/document_routes.py`: Added `GET /permit-presets` endpoint and `custom_alert_windows` form parameter to create endpoint
- `apps/Server/src/interface/document_dto.py`: Added `custom_alert_windows` field with non-negative validation
- `apps/Server/tests/test_permit_presets_api.py` (new): 474-line test suite covering presets API, preset-based alerts, custom overrides, and descriptions
- `apps/Client/src/types/document.ts`: Added 5 preset type keys to `DocumentType`, `PermitPreset` interface, `custom_alert_windows` to `DocumentCreate`
- `apps/Client/src/services/documentService.ts`: Added `getPermitPresets()` method and `custom_alert_windows` JSON serialization in create
- `apps/Client/src/components/forms/TRDocumentForm.tsx`: Added preset info display (Alert with Chips), "Personalizar alertas" toggle, and custom alert input
- `apps/Client/src/pages/restaurantos/RestaurantOSDocumentsPage.tsx`: Fetches permit presets on mount and passes to TRDocumentForm
- `.claude/commands/e2e/test_permit_type_presets.md` (new): E2E test specification

### Key Changes

- **Alert resolution order**: `custom_alert_windows` (explicit override) > `PERMIT_PRESETS[document_type]` (preset match) > `DEFAULT_ALERT_WINDOWS` (fallback [30, 7, 0])
- **Preset definitions**: Each preset has `name` (Spanish display), `alert_windows` (days before expiration), and `notification_channel` ("whatsapp" or "email")
- **Event descriptions**: When a preset type is used, descriptions include the preset name (e.g., "Permiso de Bomberos vence hoy") instead of generic "Documento vence en X dias"
- **`custom_alert_windows` transport**: Passed as JSON-encoded string in multipart form data, parsed by the route handler
- **No database migration**: Alert windows are resolved at creation time and stored as individual Event records

### Permit Presets

| Key | Name | Alert Windows | Channel |
|-----|------|---------------|---------|
| `manipulacion_alimentos` | Certificado de Manipulación de Alimentos | 30, 7, 0 | whatsapp |
| `bomberos` | Permiso de Bomberos | 0 | whatsapp |
| `camara_comercio` | Registro de Cámara de Comercio | 30, 14 | email |
| `extintor` | Servicio de Extintores | 30, 7 | whatsapp |
| `sanidad` | Certificado de Inspección Sanitaria | 30, 14, 7 | whatsapp |

## How to Use

1. Navigate to the **Documents** page in RestaurantOS
2. Click **Agregar Documento** to open the document creation form
3. In the **Tipo** dropdown, select one of the 5 permit preset types (e.g., "Certificado de Inspección Sanitaria")
4. An info box appears showing the preset's alert schedule (as day chips) and notification channel
5. Optionally, check **Personalizar alertas** to override the preset with custom day values (comma-separated, e.g., "45, 15, 3")
6. Set an expiration date and submit the document
7. Vencimiento events are automatically created using the resolved alert windows

### API Usage

```bash
# Get available permit presets
GET /api/documents/permit-presets
Authorization: Bearer <token>

# Create document with preset type (uses preset alert windows)
POST /api/documents/
Content-Type: multipart/form-data
restaurant_id=<uuid>&type=sanidad&expiration_date=2026-06-01

# Create document with custom alert override
POST /api/documents/
Content-Type: multipart/form-data
restaurant_id=<uuid>&type=sanidad&expiration_date=2026-06-01&custom_alert_windows=[45,15]
```

## Configuration

Presets are defined in `apps/Server/src/config/permit_presets.py` as a Python constant. To add a new preset:

```python
PERMIT_PRESETS["new_preset_key"] = {
    "name": "Display Name in Spanish",
    "alert_windows": [30, 14, 7],
    "notification_channel": "whatsapp",  # or "email"
}
```

Also add the corresponding type key and label in `apps/Client/src/types/document.ts` (`DocumentType` union and `DOCUMENT_TYPES` array).

## Testing

- **Backend unit tests**: `cd apps/Server && uv run pytest tests/test_permit_presets_api.py -v`
- **Existing alert tests**: `cd apps/Server && uv run pytest tests/test_document_expiration_alert_api.py -v`
- **TypeScript check**: `cd apps/Client && npx tsc --noEmit`
- **Frontend build**: `cd apps/Client && npm run build`
- **E2E test spec**: `.claude/commands/e2e/test_permit_type_presets.md`

## Notes

- Presets are configuration constants, not database-stored. Future enhancement could move them to a database table for per-restaurant customization.
- The `custom_alert_windows` field is passed as a JSON-encoded string in multipart form data since the create endpoint uses `Form()` parameters.
- No new library dependencies are required.
- UI text is in Spanish (Colombian) as per project convention.
- The preset `notification_channel` is used when creating alert events but does not change the notification dispatch mechanism itself.
