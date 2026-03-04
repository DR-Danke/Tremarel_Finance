# Event Notification Dispatcher

**ADW ID:** c57bcb02
**Date:** 2026-03-04
**Specification:** specs/issue-102-adw-c57bcb02-sdlc_planner-event-notification-dispatcher.md

## Overview

A unified event notification dispatcher that automatically processes all due events (stock alerts, document expirations, profitability warnings) and dispatches notifications through the appropriate channel (WhatsApp, Email). This replaces the previous piecemeal approach where each event type required its own dedicated dispatcher, completing the core Event → Notification Engine → Channel architectural flow.

## What Was Built

- **EventNotificationDispatcher service** — Unified processor that queries pending events, builds type-specific messages, resolves recipients, and dispatches via the correct channel
- **Profitability alert formatters** — WhatsApp plain-text and HTML email templates for `alerta_rentabilidad` events
- **Generic event formatters** — Fallback WhatsApp and HTML templates for unknown/future event types
- **Event traceability** — `_send_via_channel` updated to pass `event_id` to notification logs
- **REST API endpoints** — Manual dispatch trigger, pending events query, and cron-friendly dispatch-all
- **Scheduled dispatch orchestrator** — `run_scheduled_dispatch` combining morning summaries with general event dispatch
- **DTOs** — `EventDispatchResponseDTO` and `PendingEventsResponseDTO` for API responses
- **Comprehensive tests** — 20 unit tests for the dispatcher and 12 API endpoint tests

## Technical Implementation

### Files Modified

- `apps/Server/src/core/services/event_dispatcher.py` (new): `EventNotificationDispatcher` class with `process_due_events`, message builders, and recipient resolution
- `apps/Server/src/core/services/notification_scheduler.py`: Added `format_profitability_alert_message`, `format_general_event_message`, `run_scheduled_dispatch`; updated `_send_via_channel` with optional `event_id` parameter
- `apps/Server/src/adapter/email_templates.py` (new): Added `format_profitability_alert_html`, `format_general_event_html`, plus `format_daily_tasks_html`, `format_expiration_alert_html`, `format_low_stock_alert_html`
- `apps/Server/src/adapter/rest/notification_routes.py`: Added `POST /dispatch`, `GET /pending`, `POST /dispatch-all` endpoints
- `apps/Server/src/interface/notification_dto.py`: Added `EventDispatchResponseDTO`, `PendingEventsResponseDTO`
- `apps/Server/tests/test_event_dispatcher.py` (new): 20 unit tests covering all event types, edge cases, and message builders
- `apps/Server/tests/test_notification_api.py`: Added 4 dispatch endpoint tests

### Key Changes

- **Unified dispatch loop**: `process_due_events` fetches all pending events with `date <= now()`, filters out `tarea` events (handled separately by morning summaries), and processes each through a build-resolve-send-update pipeline
- **Type-specific message building**: `_build_whatsapp_message` and `_build_email_message` route to the correct formatter based on event type (`vencimiento`, `alerta_stock`, `alerta_rentabilidad`, or generic fallback), enriching messages with document/resource data when available
- **Recipient resolution with fallback**: `_resolve_recipient` first checks the event's `responsible_id`, then falls back to the restaurant owner via `person_repository.find_owner()`
- **Event traceability**: Every notification logged with `event_id` for full audit trail; events marked `completed` on successful dispatch
- **Backward-compatible `_send_via_channel`**: The `event_id` parameter defaults to `None`, preserving existing callers

## How to Use

1. **Manual dispatch for a restaurant**: `POST /api/notifications/dispatch?restaurant_id=<uuid>` — triggers processing of all pending due events
2. **Check pending events**: `GET /api/notifications/pending?restaurant_id=<uuid>` — returns count and list of pending due events
3. **Cron dispatch for all restaurants**: `POST /api/notifications/dispatch-all` — iterates all restaurants the authenticated user has access to and dispatches each
4. **Scheduled orchestration**: Call `run_scheduled_dispatch(db, user_id, restaurant_id)` to run morning task summaries followed by general event dispatch in a single call
5. **Automatic flow**: Any code that creates an Event with a `date` and `notification_channel` will have notifications dispatched automatically when the dispatch endpoint or cron job runs

## Configuration

- No new environment variables required
- All functionality uses existing `NotificationService`, `WhatsAppAdapter`, and `EmailAdapter` singletons
- The `POST /api/notifications/dispatch-all` endpoint is designed to be called by an external cron service (e.g., Render cron job) every 15 minutes
- `tarea` events are explicitly skipped by the general dispatcher (handled by `send_morning_task_summaries`)

## Testing

```bash
# Run dispatcher-specific tests
cd apps/Server && uv run pytest tests/test_event_dispatcher.py -v

# Run notification API tests
cd apps/Server && uv run pytest tests/test_notification_api.py -v

# Run all Server tests (regression check)
cd apps/Server && uv run pytest tests/ -v
```

## Notes

- The dispatcher imports `notification_service` from `notification_scheduler.py` (not `notification_service.py`) to avoid circular imports
- `event_repository.get_due_events()` returns all statuses for a date range; the dispatcher filters to `status == "pending"` in application code
- Events with no `responsible_id` and no restaurant owner are skipped with a warning log
- Failed notifications are logged but don't block processing of remaining events — the event status remains `pending` for retry on next dispatch cycle
- No frontend changes — this is a backend-only feature
