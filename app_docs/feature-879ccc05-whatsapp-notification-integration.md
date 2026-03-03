# WhatsApp Notification Integration

**ADW ID:** 879ccc05
**Date:** 2026-03-03
**Specification:** specs/issue-91-adw-879ccc05-sdlc_planner-whatsapp-notification-integration.md

## Overview

Backend notification system that sends automated WhatsApp messages triggered by RestaurantOS events. Supports daily task summaries, low-stock alerts, and document expiration warnings. The WhatsApp provider is abstracted behind a `NotificationAdapter` interface for swappability, with a stub implementation ready for Twilio or Meta Cloud API integration.

## What Was Built

- **NotificationAdapter** abstract interface and **NotificationService** dispatcher with single-retry on failure
- **WhatsAppAdapter** stub implementation with phone format validation and message length enforcement (4096 char limit)
- **NotificationScheduler** orchestrator that sends morning task summaries to all employees with WhatsApp numbers
- **Message formatters** for daily tasks, low-stock alerts, and document expiration alerts (Spanish/Colombian)
- **notification_log** database table and repository for full audit trail of all notification attempts
- **REST API endpoints** for manual trigger (`POST /api/notifications/send-daily-summaries`) and log queries (`GET /api/notifications/log`)
- **Pydantic DTOs** for notification requests, log responses, and trigger results
- **Comprehensive tests** for service logic, adapter validation, message formatting, and API endpoints

## Technical Implementation

### Files Modified

- `apps/Server/main.py`: Registered notification router
- `apps/Server/src/config/settings.py`: Added `WHATSAPP_API_KEY` and `WHATSAPP_PHONE_NUMBER_ID` settings

### Files Created

- `apps/Server/database/create_notification_log_table.sql`: DDL for notification_log table with indexes
- `apps/Server/src/models/notification_log.py`: SQLAlchemy model for notification audit trail
- `apps/Server/src/interface/notification_dto.py`: Pydantic DTOs (NotificationSendDTO, NotificationLogResponseDTO, DailySummaryTriggerResponseDTO)
- `apps/Server/src/repository/notification_log_repository.py`: Repository with create, get_by_restaurant (paginated/filtered), get_by_id
- `apps/Server/src/core/services/notification_service.py`: NotificationAdapter ABC and NotificationService with retry logic
- `apps/Server/src/adapter/whatsapp_adapter.py`: WhatsAppAdapter stub with phone validation and message truncation
- `apps/Server/src/core/services/notification_scheduler.py`: Orchestrator + message formatters (daily tasks, low stock, document expiry)
- `apps/Server/src/adapter/rest/notification_routes.py`: REST routes for trigger and log endpoints
- `apps/Server/tests/test_notification_service.py`: Unit tests for service, adapter, and formatters
- `apps/Server/tests/test_notification_api.py`: Unit tests for API endpoints
- `.claude/commands/e2e/test_whatsapp_notification.md`: E2E test specification

### Key Changes

- **Abstract adapter pattern**: `NotificationAdapter` ABC allows swapping WhatsApp providers (Twilio, Meta Cloud API) without changing business logic
- **Single-retry dispatch**: `NotificationService.send_notification()` retries once on adapter failure before returning a failed status
- **Spanish message formatting**: All messages use Colombian Spanish with emoji indicators for overdue tasks, urgency levels, and stock warnings
- **Audit logging**: Every notification attempt (sent, failed, skipped) is persisted to `notification_log` table with channel, recipient, message, status, and error details
- **Cron-ready endpoint**: `POST /api/notifications/send-daily-summaries` is designed for external cron invocation (Render Cron, GitHub Actions)

## How to Use

1. **Trigger daily summaries manually** via the API:
   ```
   POST /api/notifications/send-daily-summaries?restaurant_id={uuid}
   Authorization: Bearer <token>
   ```
   Returns counts of sent/skipped notifications and per-employee results.

2. **Query notification logs**:
   ```
   GET /api/notifications/log?restaurant_id={uuid}&channel=whatsapp&status=sent&limit=50&offset=0
   Authorization: Bearer <token>
   ```
   Returns paginated, filterable log entries.

3. **Set up cron** (external): Configure a scheduled job to call the trigger endpoint every morning for each restaurant.

4. **Connect a real provider**: Replace the stub in `WhatsAppAdapter.send()` with Twilio or Meta Cloud API calls. The adapter already validates phone format and message length.

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `WHATSAPP_API_KEY` | `""` (stub mode) | WhatsApp Business API key |
| `WHATSAPP_PHONE_NUMBER_ID` | `""` (stub mode) | WhatsApp Business phone number ID |

When both are empty, the adapter runs in stub mode (logs sends but does not call an external API).

## Database

Run `apps/Server/database/create_notification_log_table.sql` to create the `notification_log` table:

| Column | Type | Description |
|---|---|---|
| id | UUID PK | Auto-generated |
| restaurant_id | UUID FK | Restaurant scope |
| channel | VARCHAR(50) | "whatsapp", "email", etc. |
| recipient | VARCHAR(255) | Phone number or email |
| message | TEXT | Message body |
| status | VARCHAR(50) | "sent", "failed", "pending" |
| error_message | TEXT | Error details (null on success) |
| event_id | UUID FK | Optional event traceability |
| created_at | TIMESTAMPTZ | Auto-generated |

Indexes on: restaurant_id, channel, status, created_at.

## Testing

```bash
# Unit tests for service, adapter, and formatters
cd apps/Server && uv run pytest tests/test_notification_service.py -v

# Unit tests for API endpoints
cd apps/Server && uv run pytest tests/test_notification_api.py -v

# All backend tests (regression check)
cd apps/Server && uv run pytest
```

## Notes

- **Stub implementation**: The WhatsAppAdapter logs sends but does not call a real API. A TODO comment marks where provider integration should go.
- **No frontend changes**: This is entirely backend. The existing Event/Task management page already supports setting `notification_channel` to "whatsapp".
- **Wave 6 ready**: `format_document_expiry_message()` is provided for future document expiration alert automation.
- **Wave 8 foundation**: This service provides the dispatch infrastructure that the general Event Notification Dispatcher (Wave 8) will use.
- **Phone format**: Recipients must use international format starting with "+" (e.g., "+573001234567"). Invalid formats are rejected by the adapter.
- **Message limit**: Messages exceeding 4096 characters are automatically truncated with "..." appended.
