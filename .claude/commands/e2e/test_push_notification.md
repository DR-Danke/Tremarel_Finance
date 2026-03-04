# E2E Test: Push Notification Integration

## User Story
As a restaurant manager, I want to receive push notifications in my browser for restaurant events and tasks, so that I get instant alerts without relying on email or WhatsApp.

## Prerequisites
- Backend server running at the configured port (default: 8000)
- Test user logged in with valid JWT token
- At least one restaurant created with the test user as a member
- At least one person (type=employee) created in the restaurant with a `push_token` field set (e.g., "fcm-test-token-abc123")
- At least one event with `notification_channel = "push"` assigned to the employee for today's date

## Test Steps

### Setup
1. Obtain a valid JWT token by calling `POST /api/auth/login` with test credentials.
2. Store the token for use in Authorization headers.
3. Identify the test restaurant_id from the test user's restaurants.

### Create Person with Push Token
4. Call `POST /api/persons?restaurant_id={restaurant_id}` with body containing `name`, `role`, `type`, and `push_token: "fcm-test-token-abc123"`.
5. Verify the response status code is 200 or 201.
6. Verify the response body contains `push_token` equal to "fcm-test-token-abc123".
7. Store the person `id` for later steps.

### Create Event with Push Notification Channel
8. Call `POST /api/events` with body containing `restaurant_id`, `type: "vencimiento"`, `date: today`, `notification_channel: "push"`, `responsible_id: {person_id}`.
9. Verify the response status code is 200 or 201.
10. Store the event `id` for later steps.

### Trigger Notification Dispatch
11. Call `POST /api/notifications/dispatch?restaurant_id={restaurant_id}` with Authorization header.
12. Verify the response status code is 200.
13. Verify the response body contains `event_dispatch` with `processed` (integer >= 0).
14. Verify the response body contains `event_dispatch` with `sent` (integer >= 0).
15. If the event was processed, verify `sent` >= 1.

### Verify Push Notification Log Entries
16. Call `GET /api/notifications/log?restaurant_id={restaurant_id}&channel=push` with Authorization header.
17. Verify the response status code is 200.
18. Verify the response body is an array.
19. If `sent` > 0 from step 11, verify at least one log entry exists.
20. For each log entry, verify it contains: `id` (UUID), `restaurant_id`, `channel`, `recipient`, `message`, `status`, `created_at`.
21. Verify log entries have `channel` equal to "push".
22. Verify log entries have `status` equal to "sent" or "failed".

### Test Stub Mode (No FCM_SERVER_KEY)
23. Verify that push notifications succeed in stub mode (status "sent") since FCM_SERVER_KEY is not configured in test environment.
24. Verify log entry `status` is "sent" (stub mode always succeeds).

### Test Person Without Push Token
25. Create a person without `push_token` via `POST /api/persons?restaurant_id={restaurant_id}`.
26. Create an event with `notification_channel: "push"` assigned to this person.
27. Call `POST /api/notifications/dispatch?restaurant_id={restaurant_id}`.
28. Verify the person without push_token was skipped (check `skipped` count or verify no push log for that person).

### Error Handling: Unauthorized Access
29. Call `POST /api/notifications/dispatch?restaurant_id={restaurant_id}` without Authorization header.
30. Verify the response status code is 401 or 403.

### Error Handling: No Access to Restaurant
31. Call `POST /api/notifications/dispatch?restaurant_id={random_uuid}` with Authorization header.
32. Verify the response status code is 403.

## Success Criteria
- `POST /api/notifications/dispatch` processes events with `notification_channel = "push"` and sends via push adapter.
- Notification log entries are created for each push send attempt.
- Log entries contain correct channel ("push"), recipient (push_token value), message (Spanish text), and status.
- Log filtering by `channel=push` returns only push entries.
- Person without `push_token` is gracefully skipped when notification_channel is "push".
- Stub mode (empty FCM_SERVER_KEY) returns status "sent" without errors.
- Unauthenticated requests return 401/403.
- Unauthorized restaurant access returns 403.

## Technical Verification
- Console should show `INFO [PushAdapter]: Sending push notification to fcm-test-token...` for each recipient.
- Console should show `INFO [PushAdapter]: Push notification sent successfully (stub mode)` in stub mode.
- Console should show `INFO [EventDispatcher]: Processing due events` during dispatch.
- Console should show `INFO [NotificationService]: Sending notification via 'push'` for push channel routing.
- Network requests include `Authorization: Bearer <token>` header.

## Notes
- This is an API-level test — no UI pages are involved.
- The PushNotificationAdapter is a stub implementation when FCM_SERVER_KEY is empty; it logs sends but does not call FCM.
- Push messages use plain-text format (same as WhatsApp messages) since push notification bodies are short.
- Persons without a `push_token` field are skipped when the notification channel is "push".
