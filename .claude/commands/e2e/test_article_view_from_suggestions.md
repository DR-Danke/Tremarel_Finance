# E2E Test: Article View from Ticket Form Suggestions

Test that clicking "Ver Artículo" on knowledge base suggestions during ticket creation navigates to the article detail view without errors.

## User Story

As a user creating a support ticket
I want to click on "Ver Artículo" to view suggested knowledge base articles
So that I can read the full article content and potentially resolve my issue without submitting a ticket

## Test Steps

1. Navigate to the `Application URL` and login with test credentials
2. Navigate to the ServiceDesk ticket creation page
3. Take a screenshot of the initial form state
4. Fill in the Subject field with: "No puedo conectarme a la red VPN de la empresa"
5. Fill in the Description field with: "Desde esta mañana no puedo conectar a la VPN. He intentado reiniciar y el problema persiste. El error dice que el tiempo de conexión se agotó."
6. Wait for 1000ms to allow knowledge suggestions to load (debounce + API call)
7. Take a screenshot showing the knowledge suggestions panel
8. **Verify** at least one knowledge suggestion appears in the suggestions panel
9. **Verify** the "Ver Artículo" link is visible on the first suggestion
10. Right-click and copy the href of the "Ver Artículo" link
11. **Verify** the href contains a UUID pattern (e.g., `/servicedesk/knowledge/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
12. Click on the "Ver Artículo" link (this should open in a new tab)
13. Switch to the new tab/window
14. Take a screenshot of the article detail view
15. **Verify** NO 422 error appears - the page loads successfully
16. **Verify** article detail view displays:
    - Article title (visible and non-empty)
    - Article content section
    - "Volver" (Back) button
17. **Verify** the URL matches the pattern `/servicedesk/knowledge/{uuid}`
18. Click the "Volver" (Back) button
19. **Verify** user is navigated back to the knowledge base main page
20. Take a final screenshot

## Success Criteria

- Ticket creation form loads successfully
- Knowledge suggestions appear when user types in subject/description
- "Ver Artículo" link uses article_id (UUID) in the URL, not slug
- Clicking "Ver Artículo" opens article detail without 422 error
- Article detail view renders correctly with title and content
- No console errors related to API validation failures
- Back navigation works correctly
- 4 screenshots are taken

## Notes

- This test validates the fix for issue #122 where "Ver Artículo" was incorrectly using slug in the URL
- The backend endpoint only accepts UUID format for article_id
- If no suggestions appear, verify the database has knowledge articles with matching content
- The test may need to use different search terms based on available articles in the database
