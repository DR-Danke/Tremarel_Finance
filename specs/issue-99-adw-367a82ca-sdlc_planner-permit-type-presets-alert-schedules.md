# Feature: Permit Type Presets with Custom Alert Schedules

## Metadata
issue_number: `99`
adw_id: `367a82ca`
issue_json: ``

## Feature Description
Provide preset document types for common restaurant permits (e.g., Certificado de Manipulación de Alimentos, Permiso de Bomberos, Certificado de Inspección Sanitaria) with pre-configured alert schedules. When a document of a preset type is created, the appropriate alert schedule is automatically applied instead of the default 30/7/0 day windows. Each preset defines its own alert windows and preferred notification channel. Custom alert schedules can override presets on a per-document basis, giving restaurant managers full flexibility.

## User Story
As a restaurant manager
I want preset document types with pre-configured alert schedules for common permits
So that I get the right alerts at the right intervals for each permit type without manual configuration, while still being able to customize alert windows when needed

## Problem Statement
Currently, all documents use the same hardcoded `DEFAULT_ALERT_WINDOWS = [30, 7, 0]` regardless of document type. Different permits have different urgency levels and renewal cadences — a fire department permit (Permiso de Bomberos) may only need a day-of reminder, while a health inspection certificate (Certificado de Inspección Sanitaria) needs more frequent alerts at 30/14/7 days. There is no way for managers to customize alert schedules per document.

## Solution Statement
1. Create a permit presets configuration file defining 5 common Costa Rican/Colombian restaurant permit types with their specific alert windows and notification channels.
2. Extend the document creation and update flow to accept an optional `custom_alert_windows` parameter.
3. Modify `create_expiration_alerts()` to use preset-based windows when the document type matches a preset, custom windows when explicitly provided, or the default windows as fallback.
4. Add a `GET /api/documents/permit-presets` endpoint so the frontend can fetch available presets.
5. Update `TRDocumentForm` to show permit preset types in the type dropdown, display the preset's default alert schedule when a preset type is selected, and allow the user to override with custom alert windows.

## Relevant Files
Use these files to implement the feature:

**Backend:**
- `apps/Server/src/core/services/document_service.py` — Contains `create_expiration_alerts()` and `DEFAULT_ALERT_WINDOWS`. Must be modified to support preset-based and custom alert windows, and to use preset notification channels.
- `apps/Server/src/adapter/rest/document_routes.py` — Document API endpoints. Must add `custom_alert_windows` form parameter to create endpoint and add the new `GET /permit-presets` endpoint.
- `apps/Server/src/interface/document_dto.py` — Document DTOs. Must add `custom_alert_windows` field to `DocumentCreateDTO`.
- `apps/Server/src/config/settings.py` — Existing config module (reference for config patterns).
- `apps/Server/src/repository/event_repository.py` — Event repository (reference for event creation pattern).
- `apps/Server/tests/test_document_expiration_alert_api.py` — Existing alert tests. Must add new tests for preset and custom alert windows.

**Frontend:**
- `apps/Client/src/types/document.ts` — Document TypeScript types and `DOCUMENT_TYPES` constant. Must add permit preset types to the dropdown options and add `custom_alert_windows` to `DocumentCreate`.
- `apps/Client/src/components/forms/TRDocumentForm.tsx` — Document form component. Must add preset alert schedule display and custom alert windows input.
- `apps/Client/src/services/documentService.ts` — Document API service. Must add `getPermitPresets()` method and pass `custom_alert_windows` in create.
- `apps/Client/src/pages/restaurantos/RestaurantOSDocumentsPage.tsx` — Documents page (reference for form integration).

**Documentation (from conditional_docs.md):**
- `app_docs/feature-327dae14-document-expiration-alert-automation.md` — Read when working with document expiration alerts, `DEFAULT_ALERT_WINDOWS`, or vencimiento event creation.
- `app_docs/feature-26972c6e-document-management-page.md` — Read when working with `TRDocumentForm`, `useDocuments`, or `documentService`.
- `.claude/commands/test_e2e.md` — Read to understand how to create and run E2E test files.
- `.claude/commands/e2e/test_document_expiration_alerts.md` — Read as reference for existing E2E expiration alert test pattern.

### New Files
- `apps/Server/src/config/permit_presets.py` — Permit presets configuration with alert windows and notification channels.
- `apps/Server/tests/test_permit_presets_api.py` — Tests for preset endpoint and preset-based alert creation.
- `.claude/commands/e2e/test_permit_type_presets.md` — E2E test specification for permit type presets feature.

## Implementation Plan
### Phase 1: Foundation
Create the permit presets configuration file and the new API endpoint. This establishes the data contract that both backend service logic and frontend will consume.

### Phase 2: Core Implementation
Modify `create_expiration_alerts()` to support three-tier alert window resolution: custom > preset > default. Add `custom_alert_windows` parameter to the create document route and DTO. Update event descriptions to use the preset's display name when available.

### Phase 3: Integration
Update the frontend document type dropdown with permit preset types, display the preset's alert schedule when a preset type is selected, add a chip-based UI for custom alert windows, and wire the `custom_alert_windows` field through the form and service layer.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_document_expiration_alerts.md` to understand E2E test patterns
- Create `.claude/commands/e2e/test_permit_type_presets.md` with these test cases:
  1. Navigate to Documents page
  2. Open "Agregar Documento" form
  3. Verify permit preset types appear in the Tipo dropdown (Certificado de Manipulación de Alimentos, Permiso de Bomberos, Registro de Cámara de Comercio, Servicio de Extintores, Certificado de Inspección Sanitaria)
  4. Select "Certificado de Inspección Sanitaria" preset type
  5. Verify the preset alert schedule is displayed (30, 14, 7 días)
  6. Set an expiration date 60 days ahead
  7. Submit the document
  8. Navigate to Events page and verify 3 vencimiento events were created with descriptions using the preset name
  9. Navigate back to Documents page, create another document with "Permiso de Bomberos" preset (alert_windows: [0])
  10. Verify only 1 vencimiento event was created (day-of only)
  11. Test custom override: create a document with preset type but enter custom alert windows (e.g., [45, 15])
  12. Verify the custom windows were used instead of the preset defaults

### Step 2: Create Permit Presets Configuration
- Create `apps/Server/src/config/permit_presets.py` with the `PERMIT_PRESETS` dictionary
- Define 5 presets: `manipulacion_alimentos`, `bomberos`, `camara_comercio`, `extintor`, `sanidad`
- Each preset has: `name` (Spanish display name), `alert_windows` (list of days before expiration), `notification_channel` ("whatsapp" or "email")

### Step 3: Add Permit Presets API Endpoint
- Add `GET /api/documents/permit-presets` endpoint in `apps/Server/src/adapter/rest/document_routes.py`
- Import `PERMIT_PRESETS` from the config module
- Return a list of `{"type_key": key, "name": preset["name"], "alert_windows": preset["alert_windows"], "notification_channel": preset["notification_channel"]}` objects
- Endpoint requires JWT authentication
- Place the route BEFORE the `/{document_id}` route to avoid path conflicts

### Step 4: Update Document Service for Preset and Custom Alert Windows
- Modify `create_expiration_alerts()` in `apps/Server/src/core/services/document_service.py`:
  - Add parameters: `document_type: str = ""`, `custom_alert_windows: list[int] | None = None`
  - Resolution order: custom_alert_windows > PERMIT_PRESETS[document_type] > DEFAULT_ALERT_WINDOWS
  - Use the preset's `notification_channel` when using a preset, default to "whatsapp" otherwise
  - Use the preset's `name` in event descriptions when available (e.g., "Certificado de Inspección Sanitaria vence en 30 dias")
  - Log which alert source is being used (preset, custom, or default)
- Update calls to `create_expiration_alerts()` in `create_document()` and `update_document()` to pass `document_type` and `custom_alert_windows`

### Step 5: Update Document DTO and Route for Custom Alert Windows
- Add `custom_alert_windows: Optional[list[int]] = Field(None)` to `DocumentCreateDTO` in `apps/Server/src/interface/document_dto.py`
- Add validation: all values must be non-negative integers
- Add `custom_alert_windows: Optional[str] = Form(None)` parameter to the `create_document` route in `document_routes.py`
- Parse the JSON string to a list of ints and pass it through to the DTO
- Pass `custom_alert_windows` from the DTO to `create_document()` in the service, which passes it to `create_expiration_alerts()`

### Step 6: Write Backend Tests
- Create `apps/Server/tests/test_permit_presets_api.py` with tests:
  1. `test_get_permit_presets_returns_all_presets` — GET /api/documents/permit-presets returns 5 presets with correct structure
  2. `test_get_permit_presets_requires_auth` — 401 without token
  3. `test_create_document_with_preset_type_uses_preset_windows` — Creating a document with type "sanidad" and expiration 60 days ahead creates 3 events (at 30, 14, 7 days) instead of default 3 (at 30, 7, 0 days)
  4. `test_create_document_with_preset_type_uses_preset_notification_channel` — Verify "camara_comercio" uses "email" notification_channel
  5. `test_create_document_with_custom_alert_windows_overrides_preset` — Creating a document with type "sanidad" and custom_alert_windows=[45, 15] creates exactly 2 events
  6. `test_create_document_with_non_preset_type_uses_defaults` — Creating a document with type "contrato" uses DEFAULT_ALERT_WINDOWS
  7. `test_preset_event_descriptions_use_preset_name` — Verify event descriptions include the preset display name
- Follow the existing test patterns from `test_document_expiration_alert_api.py` (mock-based, asyncio, httpx)

### Step 7: Update Frontend Document Types
- In `apps/Client/src/types/document.ts`:
  - Add new permit preset type keys to `DocumentType` union: `'manipulacion_alimentos' | 'bomberos' | 'camara_comercio' | 'extintor' | 'sanidad'`
  - Add the 5 preset entries to `DOCUMENT_TYPES` array with Spanish labels
  - Add `custom_alert_windows?: number[]` to `DocumentCreate` interface
  - Add `PermitPreset` interface: `{ type_key: string; name: string; alert_windows: number[]; notification_channel: string }`

### Step 8: Update Frontend Document Service
- In `apps/Client/src/services/documentService.ts`:
  - Add `getPermitPresets()` method: `GET /documents/permit-presets` returning `PermitPreset[]`
  - Update `create()` method: if `data.custom_alert_windows` is provided and non-empty, append `custom_alert_windows` as JSON string to FormData

### Step 9: Update TRDocumentForm with Preset Alert Display and Custom Override
- In `apps/Client/src/components/forms/TRDocumentForm.tsx`:
  - Accept `permitPresets` as a prop (fetched by the parent page)
  - When the user selects a document type that matches a permit preset key, display an info box below the type dropdown showing:
    - Preset name
    - Default alert schedule as chips (e.g., "30 días", "14 días", "7 días")
    - Notification channel
  - Add a "Personalizar alertas" toggle (checkbox). When enabled, show a text field where the user can enter comma-separated days (e.g., "45, 15, 3"). Parse these into `custom_alert_windows` on submit.
  - Validate custom alert windows: must be non-negative integers
  - Pass `custom_alert_windows` through to the `onSubmit` callback in the `DocumentCreate` data

### Step 10: Update RestaurantOSDocumentsPage to Fetch Presets
- In `apps/Client/src/pages/restaurantos/RestaurantOSDocumentsPage.tsx`:
  - Fetch permit presets on mount using `documentService.getPermitPresets()`
  - Pass the presets to `TRDocumentForm` as a `permitPresets` prop

### Step 11: Run Validation Commands
- Run all validation commands to ensure zero regressions

## Testing Strategy
### Unit Tests
- **Preset configuration**: Verify all 5 presets exist with correct structure (name, alert_windows, notification_channel)
- **Alert window resolution**: Test that custom > preset > default priority works correctly
- **Preset API endpoint**: Test it returns all presets with correct format
- **Preset-based event creation**: Verify correct number of events with correct descriptions and notification channels
- **Custom override**: Verify custom_alert_windows takes precedence over preset
- **Non-preset type**: Verify fallback to DEFAULT_ALERT_WINDOWS
- **Validation**: Verify negative numbers are rejected in custom_alert_windows

### Edge Cases
- Document type matches a preset key but custom_alert_windows is explicitly provided (custom should win)
- Document type is a non-preset type like "contrato" with no custom_alert_windows (default should apply)
- Custom alert windows with a single value (e.g., [0] for day-of only)
- Empty custom alert windows list (should fall through to preset or default)
- All alert dates would be in the past (no events should be created)
- Document created without expiration_date (no alerts regardless of preset)
- Update document from a preset type to a non-preset type (alerts should use default windows on refresh)

## Acceptance Criteria
1. A `GET /api/documents/permit-presets` endpoint returns 5 preset types with their names, alert windows, and notification channels
2. Creating a document with type "sanidad" and expiration_date 60 days ahead creates 3 vencimiento events at 30, 14, and 7 days before expiration (not the default 30, 7, 0)
3. Creating a document with type "bomberos" and expiration_date 60 days ahead creates 1 vencimiento event at day-of only
4. Event descriptions include the preset display name (e.g., "Certificado de Inspección Sanitaria vence en 30 dias")
5. Events for "camara_comercio" preset use notification_channel "email" instead of "whatsapp"
6. Providing `custom_alert_windows=[45, 15]` on a preset type overrides the preset's alert windows
7. Non-preset document types still use DEFAULT_ALERT_WINDOWS [30, 7, 0]
8. Frontend document type dropdown includes the 5 preset types with Spanish labels
9. Selecting a preset type in the form shows the preset's alert schedule and notification channel
10. The "Personalizar alertas" toggle allows overriding alert windows with custom values
11. All existing tests pass (zero regressions)
12. TypeScript compilation succeeds with no errors
13. Frontend build succeeds

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest tests/test_permit_presets_api.py -v` — Run new permit presets tests
- `cd apps/Server && uv run pytest tests/test_document_expiration_alert_api.py -v` — Run existing alert tests to verify no regressions
- `cd apps/Server && uv run pytest` — Run all Server tests to validate zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate no TypeScript errors
- `cd apps/Client && npm run build` — Run Client build to validate no build errors
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_permit_type_presets.md` E2E test to validate this functionality works end-to-end

## Notes
- Permit presets are defined as a Python configuration constant (not database-stored) for simplicity. Future enhancement could move them to a database table for per-restaurant customization.
- The `custom_alert_windows` field is passed as a JSON-encoded string in the multipart form data since the create endpoint uses `Form()` parameters. The route handler parses it.
- Alert descriptions switch from generic "Documento vence en X dias" to preset-specific names (e.g., "Certificado de Inspección Sanitaria vence en 30 dias") when a preset type is used.
- No database migration is needed — alert windows are resolved at creation time and stored as individual Event records.
- The preset notification_channel ("email" vs "whatsapp") is used when creating alert events. This does not change the notification dispatch mechanism itself.
- UI text is in Spanish (Colombian) as per project convention.
- No new library dependencies are required.
