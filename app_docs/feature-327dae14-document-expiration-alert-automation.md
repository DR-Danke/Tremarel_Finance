# Document Expiration Alert Automation

**ADW ID:** 327dae14
**Date:** 2026-03-03
**Specification:** specs/issue-94-adw-327dae14-sdlc_planner-document-expiration-alert-automation.md

## Overview

Automated document expiration alert system for RestaurantOS. When a document with an expiration date is created or updated, the system automatically creates `vencimiento`-type Event records at configurable intervals (30 days, 7 days, and day-of). A notification processing endpoint dispatches alerts to the responsible person via their preferred channel (WhatsApp or email).

## What Was Built

- **Automatic alert event creation** on document create/update/delete lifecycle
- **Configurable alert windows** at 30-day, 7-day, and 0-day intervals before expiration (`DEFAULT_ALERT_WINDOWS`)
- **Smart past-date skipping** — alerts that would fall on or before today are not created
- **Event cleanup** on document update (old alerts replaced) and delete (orphan cleanup)
- **Notification processing endpoint** (`POST /api/notifications/process-expiration-alerts`) for cron or manual triggering
- **Full integration test suite** (7 test classes covering all flows and edge cases)
- **E2E test specification** for UI validation

## Technical Implementation

### Files Modified

- `apps/Server/src/repository/event_repository.py`: Added `delete_by_related_document()` method to delete all vencimiento events linked to a document
- `apps/Server/src/core/services/document_service.py`: Added `create_expiration_alerts()` and `delete_expiration_alerts()` methods; hooked into `create_document()`, `update_document()`, and `delete_document()` lifecycle
- `apps/Server/src/core/services/notification_scheduler.py`: Added `process_document_expiration_alerts()` async function that fetches due vencimiento events, resolves responsible persons, and dispatches notifications
- `apps/Server/src/adapter/rest/notification_routes.py`: Added `POST /api/notifications/process-expiration-alerts` endpoint with JWT auth, restaurant_id and optional target_date params

### New Files

- `apps/Server/tests/test_document_expiration_alert_api.py`: 483-line test suite covering alert creation, update replacement, deletion cleanup, past-date skipping, and notification processing
- `.claude/commands/e2e/test_document_expiration_alerts.md`: E2E test spec for UI validation of the full alert automation flow

### Key Changes

- **Document create**: Replaced the old WARNING log for near-expiry with automatic vencimiento event creation at 30/7/0-day intervals
- **Document update**: When `expiration_date` changes, all existing vencimiento events for that document are deleted and recreated with new dates
- **Document delete**: All associated vencimiento events are cleaned up before document deletion
- **Notification processing**: Filters due events to `type=vencimiento`, looks up document details and responsible person, formats Spanish-language messages using existing `format_document_expiry_message()`, and sends via `_send_via_channel()`
- **Event descriptions** are in Spanish: "Documento vence en 30 dias", "Documento vence en 7 dias", "Documento vence hoy"

## How to Use

1. **Create a document** with an `expiration_date` via the Documents page or API — alert events are created automatically
2. **Update a document's** expiration date — old alerts are replaced with new ones matching the updated date
3. **Delete a document** — associated alert events are automatically cleaned up
4. **Process due alerts** by calling `POST /api/notifications/process-expiration-alerts?restaurant_id={uuid}` (optionally with `target_date` query param)
5. **View alert events** on the Events page filtered by type `vencimiento`

## Configuration

- `DEFAULT_ALERT_WINDOWS = [30, 7, 0]` in `document_service.py` — controls how many days before expiration each alert fires
- Alert events are created with `notification_channel="whatsapp"` by default
- All alert events use `frequency="none"` (one-time events)
- Alert time is set to 8:00 AM on the alert date

## Testing

### Integration Tests
Run the full test suite:
```bash
cd apps/Server && uv run pytest tests/test_document_expiration_alert_api.py -v
```

Tests cover:
- Document creation with expiration triggers 3 alert events
- Document creation without expiration creates no alerts
- Near-expiration documents skip past alert dates
- Document update replaces old alerts with new ones
- Document update without expiration change leaves alerts untouched
- Document deletion cleans up associated alerts
- Notification processing endpoint returns correct summary

### E2E Test
Run via the E2E test skill:
```
/e2e:test_document_expiration_alerts
```

## Notes

- The `related_document_id` column on the Event table has no FK constraint (loose link by design) — cleanup in `delete_document()` prevents orphans
- The WhatsApp adapter is currently a stub (logs sends, no external API call) — real provider integration is handled separately
- No frontend changes were required — alert events appear automatically in the existing Events page
- Future enhancement: per-document-type alert schedules (e.g., different windows for permits vs contracts)
