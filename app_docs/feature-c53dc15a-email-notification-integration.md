# Email Notification Integration

**ADW ID:** c53dc15a
**Date:** 2026-03-03
**Specification:** specs/issue-92-adw-c53dc15a-sdlc_planner-email-notification-integration.md

## Overview

Adds email as a secondary notification channel alongside WhatsApp for the RestaurantOS module. The `EmailAdapter` implements the existing `NotificationAdapter` ABC, sends HTML emails via SMTP (or logs in stub mode), and the notification scheduler routes messages to email, WhatsApp, or both based on each person's available contact information.

## What Was Built

- `EmailAdapter` class implementing `NotificationAdapter` with SMTP sending and stub mode
- Three HTML email templates in Spanish (Colombian): daily task summaries, document expiration alerts, low stock alerts
- Channel routing logic in the notification scheduler (`_determine_channel` helper)
- SMTP configuration settings (SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL)
- E2E test specification for email notification validation
- Comprehensive unit tests for adapter, templates, and channel routing

## Technical Implementation

### Files Modified

- `apps/Server/src/config/settings.py`: Added 5 SMTP environment variables to the `Settings` class
- `apps/Server/src/adapter/email_adapter.py`: **New** — `EmailAdapter` class with email validation, stub mode, and SMTP sending
- `apps/Server/src/adapter/email_templates.py`: **New** — Three HTML template formatters with inline CSS for email client compatibility
- `apps/Server/src/core/services/notification_scheduler.py`: Added email adapter registration, `_determine_channel()` helper, `_send_via_channel()` helper, and multi-channel routing in `send_morning_task_summaries()`
- `apps/Server/tests/test_notification_service.py`: Added 10 new tests covering EmailAdapter, HTML templates, and channel routing
- `.claude/commands/e2e/test_email_notification.md`: **New** — E2E test specification for email notification pipeline

### Key Changes

- **EmailAdapter** follows the same pattern as `WhatsAppAdapter`: validates recipient format via regex, operates in stub mode when `SMTP_HOST` is empty, uses `smtplib.SMTP` with STARTTLS when configured
- **Channel routing** is based on person contact info (not event `notification_channel` field): persons with both email and WhatsApp get both channels, persons with only one get that channel, persons with neither are skipped
- **HTML templates** use inline CSS only (no external stylesheets) for maximum email client compatibility, max-width 600px, Spanish (Colombian) text
- **Notification logs** correctly record `channel="email"` for email sends, enabling filtering via existing `/api/notifications/log?channel=email` endpoint
- Existing WhatsApp-only tests updated with `mock_person.email = None` to maintain backward compatibility

## How to Use

1. **Configure SMTP** (optional — works in stub mode without configuration):
   ```bash
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SMTP_FROM_EMAIL=notifications@your-domain.com
   ```

2. **Ensure persons have email addresses**: Set the `email` field on Person records in the restaurant.

3. **Trigger daily summaries** via API:
   ```
   POST /api/notifications/send-daily-summaries?restaurant_id={id}
   Authorization: Bearer <token>
   ```

4. **View email notification logs**:
   ```
   GET /api/notifications/log?restaurant_id={id}&channel=email
   Authorization: Bearer <token>
   ```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `SMTP_HOST` | `""` (stub mode) | SMTP server hostname |
| `SMTP_PORT` | `587` | SMTP server port (TLS) |
| `SMTP_USERNAME` | `""` | SMTP auth username |
| `SMTP_PASSWORD` | `""` | SMTP auth password |
| `SMTP_FROM_EMAIL` | `noreply@restaurant-os.com` | Sender email address |

When `SMTP_HOST` is empty, the adapter runs in **stub mode** — it validates inputs and logs sends but does not make real SMTP connections. This mirrors the WhatsApp adapter pattern.

## Testing

**Unit tests:**
```bash
cd apps/Server && uv run pytest tests/test_notification_service.py -v
```

Tests cover:
- `EmailAdapter`: valid/invalid recipients, empty recipient, stub mode
- HTML templates: daily tasks (normal, empty, overdue), expiration alert (normal, urgent), low stock alert
- Channel routing: email-only, both channels, no contact info skip
- Existing WhatsApp tests (no regressions)

**E2E test:**
Run the E2E test specification at `.claude/commands/e2e/test_email_notification.md` via the test runner.

## Notes

- The `EmailAdapter` uses Python's built-in `smtplib` and `email.mime` — no additional dependencies required
- Channel routing is based on person contact availability, not the event's `notification_channel` field, because daily summaries aggregate across multiple events
- All notification text is in Spanish (Colombian) to match existing WhatsApp notifications
- The `format_expiration_alert_html` and `format_low_stock_alert_html` templates are ready for future use in document expiration and inventory alert workflows
