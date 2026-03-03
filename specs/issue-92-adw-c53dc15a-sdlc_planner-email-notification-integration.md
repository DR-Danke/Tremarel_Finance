# Feature: Email Notification Integration

## Metadata
issue_number: `92`
adw_id: `c53dc15a`
issue_json: ``

## Feature Description
Integrate email sending as a secondary notification channel for the RestaurantOS module. The system already has a WhatsApp notification adapter with an abstract `NotificationAdapter` interface and a `NotificationService` dispatcher. This feature adds an `EmailAdapter` that implements the same interface, HTML email templates for all notification types (daily task summaries, document expiration alerts, low stock alerts), and channel routing logic so the scheduler can send via email, WhatsApp, or both channels based on the event's `notification_channel` field.

Email content is formatted as readable, mobile-friendly HTML in Spanish (Colombian). The adapter uses Python's built-in `smtplib` for SMTP delivery (stub mode when credentials are not configured, mirroring the WhatsApp adapter pattern).

## User Story
As a restaurant manager
I want to receive daily task summaries and operational alerts via email
So that I can stay informed about my restaurant's operations even when I prefer email over WhatsApp

## Problem Statement
Currently, the notification system only supports WhatsApp as a delivery channel. Employees and managers who prefer email notifications, or who do not have WhatsApp, cannot receive automated alerts. The Event model already has a `notification_channel` field (defaulting to "email") and the Person model already has an `email` field, but no email adapter exists to use them.

## Solution Statement
Create a pluggable `EmailAdapter` implementing the existing `NotificationAdapter` ABC, with HTML email templates for all notification types. Register the adapter alongside the WhatsApp adapter in the `NotificationService`. Update the `notification_scheduler` to route notifications based on each summary's preferred channel — supporting "email", "whatsapp", and "both" routing modes. Add SMTP configuration to `settings.py` with sensible defaults for stub mode.

## Relevant Files
Use these files to implement the feature:

**Core notification system (read to understand patterns):**
- `apps/Server/src/core/services/notification_service.py` — `NotificationAdapter` ABC and `NotificationService` dispatcher. The email adapter must implement the same `async send(recipient, message) -> dict` interface.
- `apps/Server/src/core/services/notification_scheduler.py` — Current WhatsApp-only scheduler with message formatters. Must be updated to support channel routing and register the email adapter.
- `apps/Server/src/adapter/whatsapp_adapter.py` — Reference implementation for creating the email adapter. Follow the same patterns (validation, stub mode, logging, singleton).

**Configuration:**
- `apps/Server/src/config/settings.py` — Add SMTP environment variables (SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL).

**Models (read-only, for context):**
- `apps/Server/src/models/event.py` — Has `notification_channel` field (String(50), default="email") used for routing.
- `apps/Server/src/models/person.py` — Has `email` field (String(255), nullable) for recipient address.

**DTOs:**
- `apps/Server/src/interface/notification_dto.py` — Existing DTOs already support any channel (no changes needed).

**Routes:**
- `apps/Server/src/adapter/rest/notification_routes.py` — Existing endpoints already generic (no changes needed).

**Repository:**
- `apps/Server/src/repository/notification_log_repository.py` — Already supports any channel value (no changes needed).

**Existing tests (extend with email tests):**
- `apps/Server/tests/test_notification_service.py` — Add EmailAdapter tests and updated scheduler tests.
- `apps/Server/tests/test_notification_api.py` — May need minor updates for email channel filtering.

**Conditional documentation (read before implementing):**
- `app_docs/feature-879ccc05-whatsapp-notification-integration.md` — WhatsApp notification integration docs (closest pattern reference).
- `app_docs/feature-dc999a0b-event-entity-crud-backend.md` — Event model with notification_channel field.
- `app_docs/feature-206ba84f-daily-employee-task-summary.md` — Daily task summary service details.

**E2E test references (read to understand E2E format):**
- `.claude/commands/test_e2e.md` — E2E test runner instructions.
- `.claude/commands/e2e/test_whatsapp_notification.md` — WhatsApp E2E test (pattern reference for email E2E test).
- `.claude/commands/e2e/test_basic_query.md` — Basic E2E test format reference.

### New Files
- `apps/Server/src/adapter/email_adapter.py` — EmailAdapter implementing NotificationAdapter with SMTP sending and email validation.
- `apps/Server/src/adapter/email_templates.py` — HTML email template formatters for daily tasks, document expiration, and low stock alerts.
- `.claude/commands/e2e/test_email_notification.md` — E2E test specification for email notification integration.

## Implementation Plan
### Phase 1: Foundation
Add SMTP configuration to `settings.py` so the email adapter can read SMTP credentials from environment variables. Create the `EmailAdapter` class implementing the `NotificationAdapter` ABC with email address validation, stub mode (when SMTP credentials are empty), and proper logging.

### Phase 2: Core Implementation
Create HTML email templates in `email_templates.py` with mobile-friendly, clean HTML styling in Spanish (Colombian) for three notification types: daily task summaries (HTML table), document expiration alerts, and low stock alerts. Then update `notification_scheduler.py` to register the email adapter, add channel routing logic, and format messages as HTML when sending via email.

### Phase 3: Integration
Wire the email adapter into the `NotificationService` alongside the WhatsApp adapter. Update `send_morning_task_summaries` to determine the notification channel per employee and route through the correct adapter(s). Write comprehensive unit tests and create an E2E test specification. Validate with the full test suite.

## Step by Step Tasks

### Step 1: Add SMTP Configuration to Settings
- Open `apps/Server/src/config/settings.py`
- Add the following environment variables to the `Settings` class:
  - `SMTP_HOST: str = ""` (empty = stub mode)
  - `SMTP_PORT: int = 587`
  - `SMTP_USERNAME: str = ""`
  - `SMTP_PASSWORD: str = ""`
  - `SMTP_FROM_EMAIL: str = "noreply@restaurant-os.com"`

### Step 2: Create the Email Adapter
- Create `apps/Server/src/adapter/email_adapter.py`
- Import `NotificationAdapter` from `src.core.services.notification_service`
- Implement `EmailAdapter(NotificationAdapter)`:
  - `__init__(smtp_host, smtp_port, username, password, from_email)` — store config, log stub mode status
  - `async send(recipient: str, message: str) -> dict` — validate email format (regex), send via `smtplib.SMTP` with `starttls()`, or log stub send when credentials are empty
  - Email validation: use `re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", recipient)`, raise `ValueError` on invalid
  - Create `MIMEMultipart("alternative")` with Subject: "Restaurant OS - Notificacion", From, To headers
  - Attach message as `MIMEText(message, "html")`
  - Return `{"status": "sent", "recipient": recipient}` on success
  - Logging: `INFO [EmailAdapter]: Sending email to {recipient}`, `INFO [EmailAdapter]: Email sent to {recipient} (stub mode)` or `(smtp mode)`, `ERROR [EmailAdapter]: Failed to send email to {recipient}: {e}`
- Create singleton: `email_adapter = EmailAdapter()` using `get_settings()` for config values
- Follow the same patterns as `whatsapp_adapter.py` (validation, stub mode, logging, error handling)

### Step 3: Create HTML Email Templates
- Create `apps/Server/src/adapter/email_templates.py`
- Implement `format_daily_tasks_html(summary: dict) -> str`:
  - HTML document with inline CSS for mobile-friendly display
  - Header with greeting and date
  - HTML table with task rows (description, time, status)
  - Overdue tasks highlighted in red
  - Footer with motivational message
  - All text in Spanish (Colombian)
- Implement `format_expiration_alert_html(document_name: str, expiry_date: str, days_until: int) -> str`:
  - Urgency indicator (red if <=7 days, yellow otherwise)
  - Document name, expiry date, days remaining
  - Action request
- Implement `format_low_stock_alert_html(resource_name: str, current_stock: float, min_stock: float) -> str`:
  - Warning header
  - Resource name with current vs minimum stock levels
  - Action request
- All templates use inline CSS (no external stylesheets) for email client compatibility
- Base styling: max-width 600px, sans-serif font, responsive padding

### Step 4: Create E2E Test Specification
- Create `.claude/commands/e2e/test_email_notification.md`
- Model it after `.claude/commands/e2e/test_whatsapp_notification.md` (same structure)
- User Story: As a restaurant manager, validate that email notification pipeline works end-to-end via API
- Prerequisites: Backend running, test user with JWT, restaurant with employee who has `email` field set, task assigned for today
- Test Steps:
  - Setup: Obtain JWT, identify restaurant_id
  - Trigger daily summaries and verify response counts
  - Verify notification logs include entries with `channel == "email"`
  - Filter logs by channel "email" and verify results
  - Filter by status and verify results
  - Test pagination on email logs
  - Error handling: missing restaurant_id (422), no auth (401/403), no access (403)
- Success Criteria: Email log entries created with correct channel, recipient (valid email), message (HTML content), status
- Technical Verification: Console logs show `INFO [EmailAdapter]: Sending email to ...`

### Step 5: Update Notification Scheduler with Channel Routing
- Open `apps/Server/src/core/services/notification_scheduler.py`
- Import `email_adapter` from `src.adapter.email_adapter`
- Import HTML email formatters from `src.adapter.email_templates`
- Register email adapter in the `NotificationService` adapters dict:
  ```python
  notification_service = NotificationService(
      adapters={
          "whatsapp": whatsapp_adapter,
          "email": email_adapter,
      }
  )
  ```
- Update `send_morning_task_summaries` to support channel routing:
  - For each person/summary, determine the notification channel. Use a helper function `_determine_channel(person)` that returns "email", "whatsapp", or "both" based on available contact info:
    - If person has both email and whatsapp → "both"
    - If person has only email → "email"
    - If person has only whatsapp → "whatsapp"
    - If person has neither → skip
  - For "whatsapp" channel: format with existing `format_daily_tasks_message()`, send via "whatsapp"
  - For "email" channel: format with `format_daily_tasks_html()`, send via "email"
  - For "both": send via both channels (format appropriately for each)
  - Log each attempt with the correct channel name
  - Update notification_log entries with the correct channel per send

### Step 6: Write Unit Tests for Email Adapter
- Open `apps/Server/tests/test_notification_service.py`
- Add EmailAdapter test section after WhatsAppAdapter tests:
  - `test_email_adapter_valid_recipient` — send to "test@example.com", verify status "sent"
  - `test_email_adapter_invalid_recipient_no_at` — reject "invalid-email", expect ValueError
  - `test_email_adapter_invalid_recipient_empty` — reject "", expect ValueError
  - `test_email_adapter_stub_mode` — verify adapter works in stub mode (no SMTP credentials)
- Follow the same test patterns as WhatsAppAdapter tests

### Step 7: Write Unit Tests for HTML Email Templates
- In `apps/Server/tests/test_notification_service.py`, add email template test section:
  - `test_format_daily_tasks_html_normal` — verify HTML contains person name, date, task descriptions, times
  - `test_format_daily_tasks_html_empty_tasks` — verify HTML shows no-tasks message
  - `test_format_daily_tasks_html_overdue` — verify HTML highlights overdue tasks
  - `test_format_expiration_alert_html_normal` — verify HTML with days > 7 (attention level)
  - `test_format_expiration_alert_html_urgent` — verify HTML with days <= 7 (urgent level)
  - `test_format_low_stock_alert_html` — verify HTML contains resource name, stock levels

### Step 8: Write Unit Tests for Updated Scheduler Channel Routing
- In `apps/Server/tests/test_notification_service.py`, update scheduler tests:
  - `test_send_morning_task_summaries_email_channel` — person with email but no WhatsApp sends via email
  - `test_send_morning_task_summaries_both_channels` — person with both email and WhatsApp sends via both
  - `test_send_morning_task_summaries_skip_no_contact` — person with neither email nor WhatsApp is skipped
  - Keep existing WhatsApp-only tests working (person with WhatsApp but no email)

### Step 9: Run Validation Commands
- Run all validation commands to ensure zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_email_notification.md` E2E test

## Testing Strategy
### Unit Tests
- **EmailAdapter**: Valid/invalid email formats, stub mode behavior, send success/failure
- **HTML Templates**: All three template functions produce valid HTML with correct Spanish content, proper styling, and correct data rendering
- **Channel Routing**: Scheduler correctly routes to email, WhatsApp, or both based on person's available contact info
- **NotificationService**: Email adapter registered and dispatches correctly (covered by existing generic service tests)

### Edge Cases
- Person with email but no WhatsApp → sends only via email
- Person with WhatsApp but no email → sends only via WhatsApp
- Person with both → sends via both channels
- Person with neither → skipped entirely
- Invalid email format (missing @, no domain) → ValueError raised
- Empty email string → treated as no email (skipped)
- SMTP credentials not configured → stub mode (logs send, returns success)
- SMTP connection failure → adapter raises exception, NotificationService retries once

## Acceptance Criteria
- EmailAdapter implements NotificationAdapter ABC with `async send(recipient, message) -> dict`
- EmailAdapter validates email format and raises ValueError for invalid addresses
- EmailAdapter works in stub mode (no real SMTP call) when credentials are empty
- HTML email templates produce clean, mobile-friendly HTML in Spanish (Colombian)
- Three HTML templates exist: daily tasks (table), document expiration, low stock alert
- SMTP configuration added to settings.py (SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL)
- Email adapter registered in NotificationService alongside WhatsApp adapter
- Notification scheduler routes to email, WhatsApp, or both based on person's contact info
- Notification logs correctly record "email" as channel for email sends
- All existing WhatsApp notification tests continue to pass
- New unit tests cover EmailAdapter, HTML templates, and channel routing
- E2E test specification created for email notification validation

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest tests/test_notification_service.py -v` — Run notification service tests (includes new email adapter and template tests)
- `cd apps/Server && uv run pytest tests/test_notification_api.py -v` — Run notification API tests (verify no regressions)
- `cd apps/Server && uv run pytest` — Run all Server tests to validate zero regressions
- `cd apps/Client && npm run tsc --noEmit` — Run Client type check to validate no regressions
- `cd apps/Client && npm run build` — Run Client build to validate no regressions

Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_email_notification.md` E2E test to validate this functionality works.

## Notes
- The EmailAdapter uses Python's built-in `smtplib` and `email.mime` — no additional dependencies are needed.
- The adapter follows a stub pattern (like WhatsAppAdapter): when SMTP credentials are empty, it logs the send but does not make a real SMTP connection. This enables testing without an email server.
- HTML email templates use inline CSS only (no `<link>` or `<style>` blocks in `<head>`) for maximum email client compatibility.
- The `notification_channel` field on the Event model is not directly used for routing in this implementation. Instead, routing is based on the person's available contact info (email/whatsapp fields). This is a pragmatic choice because daily task summaries aggregate across multiple events that may have different channel preferences. Future iterations could add per-event channel preferences.
- All messages are in Spanish (Colombian) to match the existing WhatsApp notification format.
- Wave 6 will use the email adapter for document expiration alerts via `format_expiration_alert_html`.
