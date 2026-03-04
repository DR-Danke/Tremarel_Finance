# E2E Test: Event List Page Load

Test that the RestaurantOS Eventos/Tareas page loads without CORS errors and renders the event list correctly.

## User Story

As a restaurant manager
I want the events page to load without errors
So that I can view and manage my restaurant's events and tasks

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials and is logged in
- At least one restaurant created in the system

## Test Steps

### Setup - Navigate to Events Page

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. If not logged in, log in with test credentials
3. Open browser console to monitor for errors
4. Navigate to `/poc/restaurant-os/events`
5. Wait for the page to finish loading (network idle)
6. Take a screenshot of the events page

### Test: Page Loads Without CORS Errors

7. **Verify** no CORS errors in the browser console (no "Access-Control-Allow-Origin" errors)
8. **Verify** no `ERR_NETWORK` or `net::ERR_FAILED` errors in the console
9. **Verify** no 500 Internal Server Error responses in the network tab
10. Take a screenshot of the browser console

### Test: Events List Renders

11. **Verify** the page heading "Eventos / Tareas" (h4) is visible
12. **Verify** one of the following states is shown:
    - Events data table with event rows, OR
    - Empty state message "No se encontraron eventos"
13. **Verify** no error alerts or error messages are displayed on the page
14. Take a screenshot showing the events list or empty state

### Test: API Response Verification

15. **Verify** the network request to `GET /api/events?restaurant_id=...` completed successfully (status 200)
16. **Verify** the response includes proper CORS headers (`Access-Control-Allow-Origin`)
17. Take a screenshot of network activity

## Success Criteria

- Events page loads at `/poc/restaurant-os/events` without any errors
- No CORS-related errors in the browser console
- No network failures (ERR_NETWORK, ERR_FAILED)
- The API endpoint `/api/events` returns a successful response (200 OK)
- CORS headers are present in the API response
- Page heading "Eventos / Tareas" is visible
- Events list or empty state renders correctly
- No JavaScript errors or React warnings in the console

## Technical Verification

- Check browser console for:
  - No CORS policy errors
  - No network errors
  - `INFO [EventService]: Fetching events for restaurant...` log message
  - `INFO [useEvents]: Fetched X events` log message
- Check network requests:
  - GET `/api/events?restaurant_id=...` returns 200
  - Response includes `Access-Control-Allow-Origin` header
  - Authorization header present in the request

## Notes

- This test was created as a regression test for a bug where the `related_resource_id` column was missing from the `event` database table, causing a `ProgrammingError` that manifested as a CORS error in the browser.
- The root cause was an unapplied database migration (`alter_event_add_related_resource_id.sql`).
- The fix was applying the migration to add the missing column.
