# E2E Test: Prospect Card Drag-and-Drop

Test that prospect cards can be dragged between pipeline stage columns on the Kanban board, with optimistic UI updates and API persistence.

## User Story

As a CRM user managing a sales pipeline
I want to drag prospect cards between stage columns on the Kanban board
So that I can quickly update deal stages without opening edit dialogs

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials
- At least one entity exists for the test user
- At least one prospect exists (or will be created during the test)

## Test Steps

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. Take a screenshot of the home page
3. **Verify** the home page loads with:
   - "Finance Tracker" heading
   - "Sign In" button is visible

4. Click the "Sign In" button to navigate to login page
5. Enter valid test credentials:
   - Email: test@example.com (or a valid test user email)
   - Password: testpassword123 (or valid test password)
6. Click "Sign In" button
7. Take a screenshot after login
8. **Verify** login successful (redirected to dashboard or home)

9. Navigate to `/prospects`
10. Take a screenshot of the prospects page
11. **Verify** prospects page loads with:
    - "Prospects" page title visible
    - "Add Prospect" button visible
    - Kanban board with pipeline stage columns visible

12. **Verify** Kanban board renders with pipeline stage columns:
    - At least these columns visible: Lead, Contacted, Qualified, Proposal, Negotiation, Won, Lost
    - Each column shows a stage name header and prospect count badge

13. If no prospect card exists in the "Lead" column, create one:
    - Click "Add Prospect" button
    - Fill in: Company Name: "DnD Test Corp", Contact Name: "Jane Drag", Estimated Value: "75000", Source: "website"
    - Click "Add Prospect" submit button
    - **Verify** dialog closes and "DnD Test Corp" card appears in the "Lead" column
    - Take a screenshot after creation

14. Identify a prospect card in the "Lead" column
15. Drag the prospect card from the "Lead" column to the "Contacted" column:
    - Use Playwright drag-and-drop API to move the card element
    - The card should be dragged from its current position to the "Contacted" column drop zone
16. Take a screenshot after the drag operation
17. **Verify** the card now appears in the "Contacted" column:
    - The prospect card is visible within the "Contacted" column
    - The "Lead" column no longer contains this card
    - The prospect count badges updated accordingly

18. **Verify** the API call was made:
    - A PATCH request to `/api/prospects/{id}/stage` was fired
    - The request body contains `{ "new_stage": "contacted" }`

19. Navigate away to `/dashboard`
20. Navigate back to `/prospects`
21. Take a screenshot after navigation
22. **Verify** the prospect card persists in the "Contacted" column after page reload:
    - The moved card is still in the "Contacted" column (not back in "Lead")

23. **Verify** console shows expected INFO log messages:
    - "INFO [ProspectsPage]: Dragging prospect" log message present

## Success Criteria

- Kanban board loads with all pipeline stage columns
- Prospect cards are draggable between columns
- On drop, the card moves immediately to the destination column (optimistic update)
- A PATCH `/api/prospects/{id}/stage` API call fires with the new stage
- Data persists after navigation (API update was successful)
- Dropping a card on the same column produces no API call
- Console shows `INFO [ProspectsPage]: Dragging prospect...` log messages
- No JavaScript errors in console
- No React warnings in console

## Technical Verification

- Check browser console for:
  - INFO log messages for drag operations
  - No JavaScript errors
  - No React warnings
- Check network requests:
  - GET to `/api/pipeline-stages/?entity_id={id}` on page load
  - GET to `/api/prospects/?entity_id={id}` on page load
  - PATCH to `/api/prospects/{id}/stage` on drag-and-drop
  - Authorization header present in all requests

## Notes

- Uses `@hello-pangea/dnd` library for drag-and-drop functionality
- Optimistic updates move the card immediately; rollback occurs on API failure
- Within-column reordering is not persisted (no order field on prospects)
- The drag-and-drop test requires Playwright's drag-and-drop API support
