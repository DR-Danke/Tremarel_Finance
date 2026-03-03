# E2E Test: WhatsApp Notification Integration

## User Story
As a restaurant manager, I want to trigger daily task summary notifications via the API and verify that notification logs are created, so that I can confirm the WhatsApp notification pipeline works end-to-end.

## Prerequisites
- Backend server running at the configured port (default: 8000)
- Test user logged in with valid JWT token
- At least one restaurant created with the test user as a member
- At least one person (type=employee) created in the restaurant with a `whatsapp` field set (e.g., "+573001234567")
- At least one task (event with type=tarea) assigned to the employee for today's date

## Test Steps

### Setup
1. Obtain a valid JWT token by calling `POST /api/auth/login` with test credentials.
2. Store the token for use in Authorization headers.
3. Identify the test restaurant_id from the test user's restaurants.

### Trigger Daily Summary Notifications
4. Call `POST /api/notifications/send-daily-summaries?restaurant_id={restaurant_id}` with Authorization header.
5. Verify the response status code is 200.
6. Verify the response body contains `total_employees` (integer >= 0).
7. Verify the response body contains `sent_count` (integer >= 0).
8. Verify the response body contains `skipped_count` (integer >= 0).
9. Verify the response body contains `results` (array).
10. Verify `total_employees` equals `sent_count + skipped_count`.
11. If employees with WhatsApp numbers and tasks exist, verify `sent_count` >= 1.

### Verify Notification Log Entries
12. Call `GET /api/notifications/log?restaurant_id={restaurant_id}` with Authorization header.
13. Verify the response status code is 200.
14. Verify the response body is an array.
15. If `sent_count` > 0 from step 4, verify at least one log entry exists.
16. For each log entry, verify it contains: `id` (UUID), `restaurant_id`, `channel`, `recipient`, `message`, `status`, `created_at`.
17. Verify log entries have `channel` equal to "whatsapp".
18. Verify log entries have `recipient` starting with "+".
19. Verify log entries have `message` containing Spanish text (e.g., "Tareas" or "Buenos").
20. Verify log entries have `status` equal to "sent" or "failed".

### Filter Notification Logs by Channel
21. Call `GET /api/notifications/log?restaurant_id={restaurant_id}&channel=whatsapp` with Authorization header.
22. Verify the response status code is 200.
23. Verify all returned entries have `channel` equal to "whatsapp".

### Filter Notification Logs by Status
24. Call `GET /api/notifications/log?restaurant_id={restaurant_id}&status=sent` with Authorization header.
25. Verify the response status code is 200.
26. Verify all returned entries have `status` equal to "sent".

### Pagination
27. Call `GET /api/notifications/log?restaurant_id={restaurant_id}&limit=1&offset=0` with Authorization header.
28. Verify the response status code is 200.
29. Verify at most 1 entry is returned.

### Error Handling: Missing restaurant_id
30. Call `POST /api/notifications/send-daily-summaries` without restaurant_id query parameter.
31. Verify the response status code is 422 (validation error).

### Error Handling: Unauthorized Access
32. Call `POST /api/notifications/send-daily-summaries?restaurant_id={restaurant_id}` without Authorization header.
33. Verify the response status code is 401 or 403.

### Error Handling: No Access to Restaurant
34. Call `POST /api/notifications/send-daily-summaries?restaurant_id={random_uuid}` with Authorization header.
35. Verify the response status code is 403.

## Success Criteria
- `POST /api/notifications/send-daily-summaries` returns correct counts for sent/skipped employees.
- Notification log entries are created for each send attempt.
- Log entries contain correct channel ("whatsapp"), recipient (international format), message (Spanish), and status.
- Log filtering by channel and status works correctly.
- Pagination (limit/offset) works correctly.
- Missing restaurant_id returns 422.
- Unauthenticated requests return 401/403.
- Unauthorized restaurant access returns 403.

## Technical Verification
- Console should show `INFO [NotificationRoutes]: Send daily summaries request` on trigger.
- Console should show `INFO [NotificationScheduler]: Sending morning task summaries` during processing.
- Console should show `INFO [WhatsAppAdapter]: Sending message to +57...` for each recipient.
- Console should show `INFO [NotificationLogRepository]: Creating notification log entry` for each log write.
- Network requests include `Authorization: Bearer <token>` header.

## Notes
- This is an API-level test — no UI pages are involved.
- The WhatsAppAdapter is a stub implementation; it logs sends but does not call a real API.
- Messages are formatted in Spanish (Colombian) with task descriptions and overdue indicators.
- Employees without a `whatsapp` field are skipped (counted in `skipped_count`).
