# Feature: General Event Notification Dispatcher

## Metadata
issue_number: `102`
adw_id: `c57bcb02`
issue_json: ``

## Feature Description
Create a general-purpose event notification dispatcher that processes ALL due Events and dispatches notifications through the appropriate channel (WhatsApp, Email, Push). Currently, the system has separate, type-specific dispatchers for `tarea` (morning task summaries) and `vencimiento` (document expiration alerts), but lacks a unified dispatcher that handles ALL event types — including `alerta_stock`, `alerta_rentabilidad`, and any future event types. This dispatcher completes the core Event → Notification Engine → Channel architectural flow, so that any code creating an Event with a date and notification_channel automatically gets notification delivery with no additional wiring.

## User Story
As a restaurant administrator
I want all due events to automatically trigger notifications through the appropriate channel
So that staff are alerted about stock issues, document expirations, profitability concerns, and tasks without requiring separate dispatch logic for each event type

## Problem Statement
The current notification system handles events in a piecemeal fashion — `send_morning_task_summaries` processes only `tarea` events as daily batches, and `process_document_expiration_alerts` processes only `vencimiento` events. Low-stock alerts (`alerta_stock`), profitability alerts (`alerta_rentabilidad`), and other event types have no automated notification dispatch. Each new event type requires writing a new dedicated dispatcher function, violating the DRY principle and the Event-driven architecture's promise that "creating an Event with a notification_channel is sufficient for delivery."

## Solution Statement
Create a unified `EventNotificationDispatcher` service that:
1. Queries ALL pending events with `date <= now()` for a given restaurant
2. For each event, builds an appropriate notification message using type-specific templates (with a generic fallback)
3. Resolves the recipient from the event's `responsible_id` (with fallback to restaurant owner)
4. Dispatches via the event's `notification_channel` using the existing `NotificationService`
5. Logs each attempt to `notification_log` with `event_id` for traceability
6. Marks successfully notified events as `completed`
7. Exposes API endpoints for manual triggering and a cron-friendly dispatch-all endpoint

## Relevant Files
Use these files to implement the feature:

- `apps/Server/src/core/services/notification_scheduler.py` — Contains existing dispatchers (`send_morning_task_summaries`, `process_document_expiration_alerts`), message formatters, `_determine_channel`, `_send_via_channel`, and the `notification_service` singleton. The new dispatcher will import shared helpers from here.
- `apps/Server/src/core/services/notification_service.py` — Defines `NotificationService` and `NotificationAdapter` ABC. The dispatcher uses `notification_service.send_notification()`.
- `apps/Server/src/core/services/event_service.py` — `EventService` with `get_due_events()`, `get_events()`, `update_event_status()`. The dispatcher queries events through this service.
- `apps/Server/src/adapter/rest/notification_routes.py` — Existing notification endpoints. New dispatch endpoints will be added here.
- `apps/Server/src/adapter/email_templates.py` — HTML email templates. New templates for profitability alerts and general events will be added.
- `apps/Server/src/adapter/email_adapter.py` — `EmailAdapter` singleton.
- `apps/Server/src/adapter/whatsapp_adapter.py` — `WhatsAppAdapter` singleton.
- `apps/Server/src/repository/event_repository.py` — `EventRepository` with `get_by_restaurant()`, `get_due_events()`, `update()`. Used for querying and updating events.
- `apps/Server/src/repository/person_repository.py` — `PersonRepository` with `get_by_id()`, `find_owner()`. Used for recipient resolution.
- `apps/Server/src/repository/resource_repository.py` — `ResourceRepository` with `get_by_id()`. Used for enriching `alerta_stock` messages.
- `apps/Server/src/repository/document_repository.py` — `DocumentRepository` with `get_by_id()`. Used for enriching `vencimiento` messages.
- `apps/Server/src/repository/notification_log_repository.py` — `NotificationLogRepository` for logging notification attempts with `event_id`.
- `apps/Server/src/interface/notification_dto.py` — DTOs for notification responses. New DTOs for dispatch results will be added.
- `apps/Server/src/interface/event_dto.py` — Event DTOs and enums (EventType, EventStatus).
- `apps/Server/src/models/event.py` — Event SQLAlchemy model.
- `apps/Server/src/models/notification_log.py` — NotificationLog model with `event_id` field.
- `apps/Server/main.py` — Router registration (no changes needed, notification_routes already registered).
- `apps/Server/tests/test_notification_service.py` — Existing tests for notification service and formatters. Pattern reference for new tests.
- `apps/Server/tests/test_notification_api.py` — Existing API tests for notification routes. Pattern reference for new endpoint tests.
- Read `.claude/commands/conditional_docs.md` — Check for additional documentation requirements.
- Read `app_docs/feature-879ccc05-whatsapp-notification-integration.md` — WhatsApp adapter patterns and NotificationService architecture.
- Read `app_docs/feature-c53dc15a-email-notification-integration.md` — Email adapter and HTML template patterns.
- Read `app_docs/feature-dc999a0b-event-entity-crud-backend.md` — Event entity architecture and types.
- Read `app_docs/feature-8035b22e-low-stock-alert-automation.md` — Low-stock alert event creation pattern.
- Read `app_docs/feature-327dae14-document-expiration-alert-automation.md` — Document expiration alert pattern.

### New Files
- `apps/Server/src/core/services/event_dispatcher.py` — General event notification dispatcher service
- `apps/Server/tests/test_event_dispatcher.py` — Unit tests for the dispatcher

## Implementation Plan
### Phase 1: Foundation
Extend the existing notification infrastructure with missing message templates and update the `_send_via_channel` helper to support `event_id` traceability. Add profitability alert and general event message formatters (both WhatsApp plain-text and HTML email variants).

### Phase 2: Core Implementation
Create the `EventNotificationDispatcher` service that:
- Queries pending events with date <= now using existing `event_repository.get_by_restaurant()`
- For each event, builds type-specific messages using existing formatters (`format_low_stock_alert_message`, `format_document_expiry_message`, `format_daily_tasks_message`) and new formatters
- Resolves recipients via person lookup with owner fallback
- Dispatches through the existing `notification_service`
- Logs to `notification_log` with `event_id`
- Updates event status to `completed` on success

### Phase 3: Integration
Add REST API endpoints for manual dispatch triggering and cron-friendly dispatch-all endpoint. Wire the general dispatcher into the existing notification routes. Add comprehensive unit tests.

## Step by Step Tasks

### Step 1: Add profitability alert message formatters
- Add `format_profitability_alert_message(description: str) -> str` to `notification_scheduler.py` — WhatsApp plain-text format for `alerta_rentabilidad` events
- Add `format_general_event_message(event_type: str, description: str) -> str` to `notification_scheduler.py` — Generic fallback for unknown event types
- Add `format_profitability_alert_html(description: str) -> str` to `email_templates.py` — HTML email template for profitability alerts
- Add `format_general_event_html(event_type: str, description: str) -> str` to `email_templates.py` — Generic HTML fallback template

### Step 2: Update `_send_via_channel` to support event_id traceability
- Modify `_send_via_channel` in `notification_scheduler.py` to accept an optional `event_id: Optional[UUID] = None` parameter
- Pass `event_id` to `notification_log_repository.create()` for traceability
- Ensure existing callers (`send_morning_task_summaries`, `process_document_expiration_alerts`) continue to work without changes (parameter is optional with default None)

### Step 3: Create the EventNotificationDispatcher service
- Create `apps/Server/src/core/services/event_dispatcher.py`
- Implement `EventNotificationDispatcher` class with:
  - `__init__` taking no arguments (uses module-level singletons like existing services)
  - `async process_due_events(self, db, user_id, restaurant_id, target_date=None) -> dict` — main entry point
  - `_build_whatsapp_message(self, event, db) -> str` — builds plain-text message by event type using existing formatters
  - `_build_email_message(self, event, db) -> str` — builds HTML message by event type using existing HTML templates
  - `_resolve_recipient(self, event, db, user_id) -> tuple[Optional[Person], str]` — resolves the responsible person with owner fallback
- The dispatcher should:
  - Use `event_service.get_due_events(db, user_id, restaurant_id, target_date)` to fetch due events
  - Filter to only `status == "pending"` events (get_due_events returns all statuses for a date)
  - For each pending event with a `notification_channel`:
    - Resolve the recipient person (responsible_id → person, or fallback to restaurant owner via `person_repository.find_owner()`)
    - Determine actual channels via `_determine_channel(person)` (respects person's available contact info)
    - Build appropriate message (WhatsApp or HTML email) based on event type:
      - `vencimiento` → use `format_document_expiry_message` / `format_expiration_alert_html` (enrich with document data via `document_repository`)
      - `alerta_stock` → use `format_low_stock_alert_message` / `format_low_stock_alert_html` (enrich with resource data via `resource_repository`)
      - `alerta_rentabilidad` → use new `format_profitability_alert_message` / `format_profitability_alert_html`
      - `tarea` → skip (handled by morning summary system)
      - Other types → use `format_general_event_message` / `format_general_event_html`
    - Send via `_send_via_channel()` with `event_id` for traceability
    - On success, update event status to `completed` via `event_service.update_event_status()`
  - Return results dict: `{"processed": N, "sent": N, "skipped": N, "failed": N}`
- Create singleton: `event_dispatcher = EventNotificationDispatcher()`

### Step 4: Add dispatch API endpoints
- Add to `apps/Server/src/adapter/rest/notification_routes.py`:
  - `POST /api/notifications/dispatch` — Manually trigger dispatch for a restaurant. Requires `restaurant_id` query param. Protected by `get_current_user`. Calls `event_dispatcher.process_due_events()`.
  - `GET /api/notifications/pending` — Get count and list of pending due events for a restaurant. Requires `restaurant_id` query param. Protected by `get_current_user`. Uses `event_service.get_due_events()` filtered to pending status.
  - `POST /api/notifications/dispatch-all` — Cron-friendly endpoint that iterates over all restaurants and dispatches. Protected by `get_current_user`. Uses `restaurant_repository.get_all()` to iterate.
- Add `EventDispatchResponseDTO` to `notification_dto.py`:
  ```python
  class EventDispatchResponseDTO(BaseModel):
      processed: int
      sent: int
      skipped: int
      failed: int
  ```
- Add `PendingEventsResponseDTO` to `notification_dto.py`:
  ```python
  class PendingEventsResponseDTO(BaseModel):
      pending_count: int
      events: List[EventResponseDTO]
  ```

### Step 5: Add `run_scheduled_dispatch` to notification_scheduler.py
- Add a new function `run_scheduled_dispatch(db, user_id, restaurant_id) -> dict` that orchestrates:
  1. `send_morning_task_summaries(db, user_id, restaurant_id)` — existing daily summaries
  2. `event_dispatcher.process_due_events(db, user_id, restaurant_id)` — general event dispatch
- This provides a single entry point for scheduled execution

### Step 6: Write unit tests for the event dispatcher
- Create `apps/Server/tests/test_event_dispatcher.py` following patterns from `test_notification_service.py`:
  - **test_process_due_events_sends_notifications** — Mock due events of various types, verify messages sent via correct channels, verify event status updated to completed
  - **test_process_due_events_skips_tarea** — Verify `tarea` events are skipped by the general dispatcher
  - **test_process_due_events_skips_no_channel** — Events without notification_channel are skipped
  - **test_process_due_events_no_recipient_fallback_to_owner** — Events without responsible_id fall back to restaurant owner
  - **test_process_due_events_no_recipient_no_owner** — Events with no responsible and no owner are skipped
  - **test_process_due_events_failed_notification** — Verify failed notifications are logged but don't block remaining events
  - **test_process_due_events_empty** — No due events returns zeros
  - **test_build_message_vencimiento** — Verify document expiry message built correctly with document enrichment
  - **test_build_message_alerta_stock** — Verify stock alert message built correctly with resource enrichment
  - **test_build_message_alerta_rentabilidad** — Verify profitability alert message
  - **test_build_message_unknown_type** — Verify generic fallback message
  - **test_format_profitability_alert_message** — Test new WhatsApp formatter
  - **test_format_profitability_alert_html** — Test new HTML template
  - **test_format_general_event_message** — Test generic WhatsApp formatter
  - **test_format_general_event_html** — Test generic HTML template

### Step 7: Write API endpoint tests
- Add tests to `apps/Server/tests/test_notification_api.py`:
  - **test_dispatch_due_events_endpoint** — POST /api/notifications/dispatch returns dispatch results
  - **test_dispatch_due_events_unauthorized** — Verify auth required
  - **test_get_pending_events_endpoint** — GET /api/notifications/pending returns count and events
  - **test_dispatch_all_endpoint** — POST /api/notifications/dispatch-all iterates restaurants

### Step 8: Run validation commands
- Run all Server tests to verify zero regressions
- Run Client type check and build to verify no breakage

## Testing Strategy
### Unit Tests
- **EventNotificationDispatcher.process_due_events**: Mock `event_service`, `person_service`, `notification_service`, `notification_log_repository`, `document_repository`, `resource_repository`. Verify correct message building, channel routing, event status updates, and logging for each event type.
- **Message formatters**: Test each new formatter produces expected output strings.
- **API endpoints**: Mock the dispatcher service, verify HTTP status codes, response shapes, and auth requirements.
- **_send_via_channel with event_id**: Verify event_id is passed to notification_log_repository.create().

### Edge Cases
- Event with no `responsible_id` and no restaurant owner → skipped with warning
- Event with `responsible_id` pointing to person with no email or whatsapp → skipped
- Event with future date → not included in due events query
- Event already `completed` or `overdue` → not processed (only `pending` events)
- `alerta_stock` event with deleted resource (related_resource_id not found) → use description fallback
- `vencimiento` event with deleted document (related_document_id not found) → use description fallback
- Multiple events for same person → each dispatched independently
- Notification send failure → logged as failed, event status unchanged, processing continues
- Empty restaurant (no events) → returns all-zero results

## Acceptance Criteria
- [ ] Dispatcher finds all Events with `status = pending` and `date <= now()`
- [ ] Each event type produces an appropriate notification message template (vencimiento, alerta_stock, alerta_rentabilidad, tarea is skipped, generic fallback for others)
- [ ] Notifications sent via the event's `notification_channel` (whatsapp, email), respecting person's available contact info
- [ ] Event status updated to `completed` after successful notification
- [ ] Failed notifications logged but don't block processing of remaining events
- [ ] Manual trigger endpoint `POST /api/notifications/dispatch` available for testing
- [ ] Pending events endpoint `GET /api/notifications/pending` returns count and list
- [ ] Cron-friendly `POST /api/notifications/dispatch-all` iterates all restaurants
- [ ] `run_scheduled_dispatch` orchestrates morning summaries + general dispatch
- [ ] All notification log entries include `event_id` for traceability
- [ ] Recipient resolution falls back to restaurant owner when no responsible_id
- [ ] Logging at each step for debugging (INFO/WARNING/ERROR prefixed with [EventDispatcher])
- [ ] All existing tests pass with zero regressions
- [ ] New unit tests cover all event types, edge cases, and API endpoints

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest tests/ -v` — Run all Server tests to validate the feature works with zero regressions
- `cd apps/Server && uv run pytest tests/test_event_dispatcher.py -v` — Run dispatcher-specific tests
- `cd apps/Server && uv run pytest tests/test_notification_api.py -v` — Run notification API tests
- `cd apps/Server && uv run pytest tests/test_notification_service.py -v` — Run notification service tests (regression check)

## Notes
- The `notification_service` singleton is created in `notification_scheduler.py` (not `notification_service.py`) to avoid circular imports. The new `event_dispatcher.py` should import it from there.
- The existing `_send_via_channel` does NOT currently pass `event_id` to `notification_log_repository.create()`. Step 2 fixes this for all future calls while maintaining backward compatibility.
- `event_repository.get_due_events()` queries by date range (start_of_day to end_of_day) and returns ALL statuses. The dispatcher must filter to `status == "pending"` in application code.
- `tarea` events are explicitly skipped by the general dispatcher since they're handled by the separate `send_morning_task_summaries` batch system which aggregates per-person summaries.
- `person_repository.find_owner(db, restaurant_id)` already exists and returns the `type == "owner"` person — perfect for the fallback recipient logic.
- No new dependencies required — all functionality uses existing libraries.
- No frontend changes needed — this is a backend-only feature (no UI components).
- The `POST /api/notifications/dispatch-all` endpoint is designed to be called by an external cron service (e.g., Render cron job) every 15 minutes.
