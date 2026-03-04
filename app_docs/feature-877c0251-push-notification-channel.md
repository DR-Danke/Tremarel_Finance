# Push Notification Channel

**ADW ID:** 877c0251
**Date:** 2026-03-04
**Specification:** specs/issue-103-adw-877c0251-sdlc_planner-push-notification-channel.md

## Overview

Adds push notifications as the third notification channel alongside WhatsApp and Email in the RestaurantOS notification system. Push notifications use Firebase Cloud Messaging (FCM) for browser/mobile delivery, following the existing `NotificationAdapter` interface pattern for plug-and-play integration with the `NotificationService`.

## What Was Built

- **PushNotificationAdapter** — Backend adapter implementing `NotificationAdapter` ABC with stub/live FCM modes
- **Person model extension** — Added `push_token` column for storing FCM device tokens
- **Dispatcher integration** — EventNotificationDispatcher routes `notification_channel = "push"` events via push
- **Scheduler integration** — Morning task summaries and document expiration alerts also send via push when person has a `push_token`
- **Firebase service worker** — Minimal frontend service worker for receiving and displaying push notifications
- **Frontend UI** — Push token status column on the Persons management page
- **Unit tests** — Push adapter stub mode, validation, message truncation, and NotificationService routing tests
- **E2E test spec** — Test specification for push notification validation

## Technical Implementation

### Files Modified

- `apps/Server/src/adapter/push_adapter.py`: New push notification adapter with FCM legacy HTTP API support and stub mode
- `apps/Server/src/config/settings.py`: Added `FCM_SERVER_KEY` setting for Firebase Cloud Messaging
- `apps/Server/src/models/person.py`: Added `push_token` column (String(500), nullable)
- `apps/Server/src/interface/person_dto.py`: Added `push_token` to PersonCreateDTO, PersonUpdateDTO, PersonResponseDTO
- `apps/Server/src/repository/person_repository.py`: Added `push_token` parameter to `create()` method
- `apps/Server/src/core/services/person_service.py`: Pass `push_token` through create and update operations
- `apps/Server/src/core/services/notification_scheduler.py`: Registered push adapter, added push sending to morning summaries and document expiration alerts
- `apps/Server/src/core/services/event_dispatcher.py`: Added push channel routing for event notifications
- `apps/Server/database/alter_person_add_push_token.sql`: SQL migration to add `push_token` column
- `apps/Client/public/firebase-messaging-sw.js`: Firebase messaging service worker for push reception
- `apps/Client/src/types/person.ts`: Added `push_token` to Person, PersonCreate, PersonUpdate types
- `apps/Client/src/pages/restaurantos/RestaurantOSPersonsPage.tsx`: Added Push status column with check icon
- `apps/Server/tests/test_notification_service.py`: Added push adapter and push channel routing tests
- `.claude/commands/e2e/test_push_notification.md`: E2E test specification

### Key Changes

- **Adapter pattern**: `PushNotificationAdapter` follows the same pattern as WhatsApp and Email adapters — validates recipient, runs in stub mode when `FCM_SERVER_KEY` is empty, sends via FCM legacy HTTP API when configured
- **Backward-compatible dispatcher**: The `_determine_channel()` function is unchanged. Push is handled as a separate check — when `notification_channel = "push"`, the dispatcher sends via push instead of email/whatsapp. Morning summaries and expiration alerts additionally send via push when a person has a `push_token`
- **Message truncation**: FCM notification body is truncated to 200 characters; the full message is sent in the `data.full_message` payload field
- **Graceful skip**: When a person has no `push_token` but the channel is "push", the event is skipped with a log warning and incremented `skipped_count`
- **Singleton**: The push adapter is instantiated as a module-level singleton using `get_settings().FCM_SERVER_KEY`

## How to Use

1. **Set FCM_SERVER_KEY** (optional): Add `FCM_SERVER_KEY=your-firebase-server-key` to the backend `.env` file. Without it, the adapter runs in stub mode (logs sends without calling FCM)
2. **Run the database migration**: Execute `apps/Server/database/alter_person_add_push_token.sql` on the database to add the `push_token` column
3. **Store push tokens**: Set a person's `push_token` field via the Person API (`POST /api/persons` or `PATCH /api/persons/{id}`) with a valid FCM device token
4. **Create events with push channel**: When creating events, set `notification_channel = "push"` to route notifications via push (the "Push" option already exists in the frontend event form)
5. **Dispatch notifications**: Trigger `POST /api/notifications/dispatch` — events with `notification_channel = "push"` will be sent to persons with a `push_token`

## Configuration

| Variable | Description | Default |
|---|---|---|
| `FCM_SERVER_KEY` | Firebase Cloud Messaging server key | `""` (stub mode) |

When `FCM_SERVER_KEY` is empty, the adapter operates in stub mode — it validates inputs, logs the send, and returns `{"status": "sent"}` without calling the FCM API.

## Testing

- **Unit tests**: `cd apps/Server && uv run pytest tests/test_notification_service.py -v` — includes push adapter stub mode, validation, truncation, and routing tests
- **All tests**: `cd apps/Server && uv run pytest tests/ -v`
- **Type check**: `cd apps/Client && npx tsc --noEmit`
- **Build**: `cd apps/Client && npm run build`
- **E2E**: See `.claude/commands/e2e/test_push_notification.md` for end-to-end test specification

## Notes

- The FCM legacy HTTP API (`fcm.googleapis.com/fcm/send`) is used for simplicity. Migration to FCM v1 API can be done when full Firebase project configuration is available.
- The frontend service worker (`firebase-messaging-sw.js`) is a minimal stub. Full Firebase SDK integration (token management, permission dialogs, topic subscriptions) requires `firebase-app` and `firebase-messaging` npm packages.
- The `NOTIFICATION_CHANNEL_OPTIONS` in `apps/Client/src/types/event.ts` already included `{ value: 'push', label: 'Push' }` before this feature — the event form already supported selecting push as a channel.
- `httpx` (used for FCM HTTP calls) was already in project dependencies.
