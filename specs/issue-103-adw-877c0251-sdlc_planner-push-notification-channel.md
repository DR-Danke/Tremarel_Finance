# Feature: Push Notification Channel

## Metadata
issue_number: `103`
adw_id: `877c0251`
issue_json: ``

## Feature Description
Add push notifications as the third notification channel alongside WhatsApp (#91) and Email (#92) in the RestaurantOS notification system. Push notifications use web push via Firebase Cloud Messaging (FCM) for browser/mobile delivery. The implementation follows the existing `NotificationAdapter` interface pattern for plug-and-play integration with the `NotificationService`. This includes a backend adapter, Person model extension with `push_token`, dispatcher integration, and a minimal frontend service worker for push reception.

## User Story
As a restaurant manager
I want to receive push notifications in my browser for restaurant events and tasks
So that I get instant alerts without relying on email or WhatsApp

## Problem Statement
The notification system currently supports only WhatsApp and Email channels. Some users prefer browser push notifications for immediate, low-friction alerts — especially on desktop where they are already working. Without push support, users must check email or WhatsApp separately for restaurant alerts.

## Solution Statement
Create a `PushNotificationAdapter` that implements the existing `NotificationAdapter` ABC, register it with the `NotificationService` singleton, extend the Person model with a `push_token` field, update the `EventNotificationDispatcher` to route "push" channel notifications, and add a minimal Firebase messaging service worker on the frontend for push reception.

## Relevant Files
Use these files to implement the feature:

**Backend - Core notification system (understand existing patterns):**
- `apps/Server/src/core/services/notification_service.py` — `NotificationAdapter` ABC and `NotificationService` class. The push adapter must implement the same `send(recipient, message)` interface.
- `apps/Server/src/core/services/notification_scheduler.py` — Creates the `NotificationService` singleton with registered adapters, contains `_determine_channel()` and `_send_via_channel()` helpers. Must register push adapter and update channel determination.
- `apps/Server/src/core/services/event_dispatcher.py` — `EventNotificationDispatcher` that routes events to notification channels. Must add push channel routing alongside WhatsApp/Email.

**Backend - Existing adapter patterns (follow same structure):**
- `apps/Server/src/adapter/whatsapp_adapter.py` — WhatsApp adapter pattern to follow (stub mode, validation, singleton export).
- `apps/Server/src/adapter/email_adapter.py` — Email adapter pattern to follow (SMTP/stub mode, validation, settings-based initialization).

**Backend - Person model and DTOs (extend with push_token):**
- `apps/Server/src/models/person.py` — Person SQLAlchemy model. Add `push_token` column.
- `apps/Server/src/interface/person_dto.py` — Person Pydantic DTOs. Add `push_token` to Create/Update/Response DTOs.
- `apps/Server/src/repository/person_repository.py` — Person repository. Update `create()` to accept `push_token`.
- `apps/Server/src/core/services/person_service.py` — Person service. Update to pass `push_token` through.

**Backend - Configuration:**
- `apps/Server/src/config/settings.py` — Add `FCM_SERVER_KEY` setting.

**Backend - Database migration:**
- `apps/Server/database/create_person_table.sql` — Reference for person table schema.

**Backend - Tests (extend with push adapter tests):**
- `apps/Server/tests/test_notification_service.py` — Existing notification tests. Add push adapter tests here.

**Frontend - Types (already has push option):**
- `apps/Client/src/types/person.ts` — Person TypeScript types. Add `push_token` field.
- `apps/Client/src/types/event.ts` — Already has `{ value: 'push', label: 'Push' }` in `NOTIFICATION_CHANNEL_OPTIONS`.

**Frontend - Forms (update person form):**
- `apps/Client/src/components/forms/TRPersonForm.tsx` — Person form. No changes needed for push_token (read-only backend field).

**Frontend - Pages:**
- `apps/Client/src/pages/restaurantos/RestaurantOSPersonsPage.tsx` — Person management page. Show push_token status in table.

**Documentation (read for context):**
- `app_docs/feature-879ccc05-whatsapp-notification-integration.md` — WhatsApp notification patterns
- `app_docs/feature-c53dc15a-email-notification-integration.md` — Email notification patterns
- `app_docs/feature-c57bcb02-event-notification-dispatcher.md` — Dispatcher patterns
- `app_docs/feature-14633eae-person-entity-crud-backend.md` — Person entity patterns

**E2E test references:**
- `.claude/commands/test_e2e.md` — How to create and run E2E tests
- `.claude/commands/e2e/test_whatsapp_notification.md` — WhatsApp notification E2E test (pattern to follow for push)

### New Files
- `apps/Server/src/adapter/push_adapter.py` — Push notification adapter implementing `NotificationAdapter`
- `apps/Server/database/alter_person_add_push_token.sql` — SQL migration to add push_token column
- `apps/Client/public/firebase-messaging-sw.js` — Firebase messaging service worker for push reception
- `.claude/commands/e2e/test_push_notification.md` — E2E test specification for push notification validation

## Implementation Plan
### Phase 1: Foundation
Extend the Person model and database with `push_token` field. Add `FCM_SERVER_KEY` to settings. These are prerequisites for both the adapter and the dispatcher.

### Phase 2: Core Implementation
Create the `PushNotificationAdapter` following the existing adapter pattern (WhatsApp/Email). Register it with the `NotificationService` singleton. Update `_determine_channel()` to include push as a channel option. Update the `EventNotificationDispatcher` to route push notifications.

### Phase 3: Integration
Add a minimal frontend service worker for push reception. Update frontend types and the persons page to display push token status. Write unit tests for the push adapter. Create E2E test specification.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_whatsapp_notification.md` to understand the E2E test format
- Create `.claude/commands/e2e/test_push_notification.md` following the same pattern as `test_whatsapp_notification.md`
- The E2E test should validate:
  - Create an Event with `notification_channel = "push"` and a Person with a `push_token` via API
  - Trigger notification dispatch via `POST /api/notifications/dispatch` → verify push notification logged
  - Query `GET /api/notifications/log?channel=push` → verify push log entries exist
  - Test with missing `FCM_SERVER_KEY` → verify graceful skip (status "sent" in stub mode)
  - Test with person without `push_token` → verify skipped
  - Test unauthorized access → verify 401/403

### Step 2: Create Database Migration
- Create `apps/Server/database/alter_person_add_push_token.sql`:
  ```sql
  ALTER TABLE person ADD COLUMN push_token TEXT;
  ```
- This adds an optional push_token column to store FCM device tokens

### Step 3: Update Person Model
- Edit `apps/Server/src/models/person.py`:
  - Add `push_token: Optional[str] = Column(String(500), nullable=True)` field after the `whatsapp` field

### Step 4: Update Person DTOs
- Edit `apps/Server/src/interface/person_dto.py`:
  - Add `push_token: Optional[str] = Field(None, max_length=500, description="FCM push notification device token")` to `PersonCreateDTO`
  - Add `push_token: Optional[str] = Field(None, max_length=500, description="FCM push notification device token")` to `PersonUpdateDTO`
  - Add `push_token: Optional[str] = Field(None, description="FCM push notification device token")` to `PersonResponseDTO`

### Step 5: Update Person Repository
- Edit `apps/Server/src/repository/person_repository.py`:
  - Add `push_token: Optional[str]` parameter to `create()` method
  - Pass `push_token=push_token` to the `Person()` constructor

### Step 6: Update Person Service
- Read `apps/Server/src/core/services/person_service.py`
- Update `create_person()` to accept and pass `push_token` parameter
- Update `update_person()` to handle `push_token` in update fields

### Step 7: Add FCM_SERVER_KEY to Settings
- Edit `apps/Server/src/config/settings.py`:
  - Add `FCM_SERVER_KEY: str = ""` field in the Settings class, after the SMTP settings block

### Step 8: Create Push Notification Adapter
- Create `apps/Server/src/adapter/push_adapter.py` following the pattern from `whatsapp_adapter.py` and `email_adapter.py`:
  - Import `NotificationAdapter` from `src.core.services.notification_service`
  - Import `httpx` for HTTP calls and `get_settings` from `src.config.settings`
  - Create `PushNotificationAdapter` class implementing `NotificationAdapter`
  - Constructor takes `fcm_server_key: str`, sets `stub_mode = not bool(fcm_server_key)`, stores `fcm_url = "https://fcm.googleapis.com/fcm/send"`
  - `send(recipient, message)` method:
    - Validate recipient is non-empty (raise `ValueError` if empty/None)
    - In stub mode: log and return `{"status": "sent", "recipient": recipient[:20]}`
    - In live mode: POST to FCM with `Authorization: key={fcm_server_key}`, payload with `to`, `notification.title="Restaurant OS"`, `notification.body=message[:200]`, `data.full_message=message`
    - Handle response: check `status_code == 200` and `result.success > 0`
    - Log at each step with `print(f"INFO [PushAdapter]: ...")`
  - Create singleton instance: `_settings = get_settings()` then `push_adapter = PushNotificationAdapter(fcm_server_key=_settings.FCM_SERVER_KEY)`

### Step 9: Register Push Adapter with NotificationService
- Edit `apps/Server/src/core/services/notification_scheduler.py`:
  - Add import: `from src.adapter.push_adapter import push_adapter`
  - Add `"push": push_adapter` to the `adapters` dictionary in the `NotificationService` constructor call
  - Update `_determine_channel()` function:
    - Add `has_push = bool(getattr(person, "push_token", None) and getattr(person, "push_token", "").strip())`
    - Return logic: if all three → "all", if email+whatsapp → "both", if email+push → "email_push", if whatsapp+push → "whatsapp_push", individual channels, or "none"
    - NOTE: Keep backward compatibility — "both" still means email+whatsapp. The dispatcher will need to check for push separately.
  - ALTERNATIVE simpler approach: Keep `_determine_channel()` returning existing values ("both", "email", "whatsapp", "none"), and add a separate check for push_token in the send functions. This avoids breaking existing channel routing.
  - **Preferred approach**: Keep `_determine_channel()` unchanged for backward compatibility. Instead, after sending via email/whatsapp, add a separate push check: if person has `push_token`, also send via "push" channel. This is additive and non-breaking.

### Step 10: Update EventNotificationDispatcher for Push Channel
- Edit `apps/Server/src/core/services/event_dispatcher.py`:
  - In `process_due_events()`, after the existing whatsapp/email send blocks, add a push notification block:
    - Check if `notification_channel == "push"` or person has a `push_token` (when notification_channel is "push")
    - Build push message using the plain-text WhatsApp message (push notifications use short text)
    - Call `_send_via_channel("push", push_token, message, ...)`
  - Add a `_build_push_message()` method that returns a short plain-text message (reuses `_build_whatsapp_message()` logic since push notifications use short text)

### Step 11: Update notification_scheduler Send Functions for Push
- Edit `apps/Server/src/core/services/notification_scheduler.py`:
  - In `send_morning_task_summaries()`, after the whatsapp/email blocks, add a push block:
    - Check if person has `push_token`
    - If so, send via "push" channel with the plain-text formatted message
  - In `process_document_expiration_alerts()`, similarly add push support after existing channel sends

### Step 12: Update Frontend Person Type
- Edit `apps/Client/src/types/person.ts`:
  - Add `push_token: string | null` to the `Person` interface
  - Add `push_token?: string` to `PersonCreate` and `PersonUpdate` interfaces

### Step 13: Update Persons Page to Show Push Token Status
- Edit `apps/Client/src/pages/restaurantos/RestaurantOSPersonsPage.tsx`:
  - Add a "Push" column header to the table after the "WhatsApp" column
  - Add a table cell that shows push_token status: a check icon if push_token exists, "—" if not

### Step 14: Create Firebase Messaging Service Worker
- Create `apps/Client/public/firebase-messaging-sw.js`:
  - Minimal service worker that handles `push` events
  - On push event: extract notification data and display via `self.registration.showNotification()`
  - On notification click: open the app URL via `clients.openWindow()`
  - Include comments explaining this is a stub — full Firebase SDK integration requires `firebase-app` and `firebase-messaging` npm packages and configuration

### Step 15: Write Unit Tests for Push Adapter
- Edit `apps/Server/tests/test_notification_service.py`:
  - Add tests for `PushNotificationAdapter`:
    - `test_push_adapter_stub_mode_success`: Create adapter with empty key, send → expect `{"status": "sent"}`
    - `test_push_adapter_invalid_recipient`: Create adapter, send with empty recipient → expect `ValueError`
    - `test_push_adapter_message_truncation`: Verify message is truncated to 200 chars for FCM body
  - Add test for NotificationService with push adapter registered:
    - `test_send_notification_push_channel`: Register push mock adapter, send via "push" → expect success

### Step 16: Run Validation Commands
- Run all validation commands to ensure zero regressions

## Testing Strategy
### Unit Tests
- **PushNotificationAdapter stub mode**: Verify sends succeed in stub mode (no FCM key)
- **PushNotificationAdapter validation**: Verify empty/None recipient raises ValueError
- **PushNotificationAdapter live mode**: Mock httpx to verify correct FCM payload structure
- **NotificationService with push**: Verify "push" channel routes to push adapter
- **NotificationService unknown channel**: Verify non-existent channels still return failed gracefully
- **Channel determination with push_token**: Verify push_token presence is detected correctly

### Edge Cases
- Person with `push_token` but no email/whatsapp — push is the only available channel
- Person with all three contact methods — push should fire alongside other channels when requested
- Empty `FCM_SERVER_KEY` — adapter runs in stub mode, logs warning, returns success
- Invalid/expired push_token — FCM returns failure response, logged but no crash
- Very long message — truncated to 200 chars for FCM notification body, full message in data payload
- `notification_channel = "push"` on event but person has no push_token — skip gracefully
- Concurrent push sends — httpx.AsyncClient handles async correctly

## Acceptance Criteria
- [ ] `PushNotificationAdapter` class exists at `apps/Server/src/adapter/push_adapter.py` and implements `NotificationAdapter` ABC
- [ ] Push adapter validates recipient (non-empty) and raises `ValueError` on invalid input
- [ ] Push adapter runs in stub mode when `FCM_SERVER_KEY` is empty (logs and returns success)
- [ ] Push adapter is registered in `NotificationService` singleton with channel name "push"
- [ ] `NotificationService.send_notification("push", token, message)` routes to push adapter
- [ ] Person model has optional `push_token` column (String, nullable)
- [ ] PersonCreateDTO, PersonUpdateDTO, and PersonResponseDTO include `push_token` field
- [ ] Person repository and service accept and persist `push_token`
- [ ] `EventNotificationDispatcher` sends push notifications when `notification_channel = "push"` and person has `push_token`
- [ ] Morning task summaries and document expiration alerts also send via push when person has `push_token`
- [ ] Graceful skip when person has no `push_token` but channel is "push" (log warning, increment skipped_count)
- [ ] Frontend `Person` type includes `push_token` field
- [ ] Persons page shows push token status column
- [ ] Firebase messaging service worker file exists at `apps/Client/public/firebase-messaging-sw.js`
- [ ] `FCM_SERVER_KEY` setting exists in application settings
- [ ] SQL migration file exists at `apps/Server/database/alter_person_add_push_token.sql`
- [ ] All unit tests pass including new push adapter tests
- [ ] Logging at every step follows `print(f"INFO [PushAdapter]: ...")` format
- [ ] E2E test specification exists at `.claude/commands/e2e/test_push_notification.md`

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest tests/ -v` — Run all Server tests including new push adapter tests
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate TypeScript changes
- `cd apps/Client && npm run build` — Run Client build to validate frontend compiles without errors

Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_push_notification.md` E2E test to validate push notification functionality works end-to-end.

## Notes
- The push adapter follows the same stub-mode pattern as WhatsApp and Email adapters — it logs sends without calling FCM when `FCM_SERVER_KEY` is empty. This allows development and testing without Firebase credentials.
- The `NOTIFICATION_CHANNEL_OPTIONS` in `apps/Client/src/types/event.ts` already includes `{ value: 'push', label: 'Push' }`, so the event form already supports selecting "push" as a notification channel.
- The existing `_determine_channel()` function should be kept backward-compatible. Push is additive — the dispatcher checks for push_token and sends via push in addition to or instead of other channels based on the event's `notification_channel` setting.
- `httpx` is already in the project dependencies (used by other adapters/services). No new library installation needed.
- Future enhancements: Firebase SDK integration on the frontend for token management, push permission dialogs, and topic-based subscriptions. The current implementation is the minimal viable push channel.
- The FCM legacy HTTP API (`fcm.googleapis.com/fcm/send`) is used for simplicity. Migration to FCM v1 (`fcm.googleapis.com/v1/projects/*/messages:send`) can be done later when full Firebase project configuration is available.
