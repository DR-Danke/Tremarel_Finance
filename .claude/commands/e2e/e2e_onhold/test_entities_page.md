# E2E Test: Entidades Page Load Without Infinite Loop

Test that the RAG Entidades page loads correctly without entering an infinite loading loop.

## User Story

As a user
I want to navigate to the Entidades page in the Intelligence module
So that I can view and filter extracted business entities without experiencing infinite loading loops

## Test Steps

1. Navigate to the `Application URL` (http://localhost:5173)
2. Take a screenshot of the login page
3. Log in with valid credentials:
   - Email: valid test user
   - Password: valid test password
4. **Verify** successful login and redirect to home page
5. Take a screenshot of the home page

6. Navigate to Intelligence > Entidades (or directly to `/intelligence/entities`)
7. Take a screenshot immediately after navigation
8. **Verify** the page header displays "Explorador de Entidades"
9. **Verify** the subtitle displays "Navega y filtra entidades de negocio extraidas de documentos"

10. Open browser DevTools Network tab
11. Filter network requests to show only `/api/rag/entities` calls
12. **Verify** only ONE initial request to `/api/rag/entities` is made (NOT multiple rapid requests)
13. Take a screenshot of the Network tab showing single request
14. Wait 3 seconds and **verify** no additional requests are made automatically

15. **Verify** the page displays one of the following:
    - Entities list in a DataGrid (if entities exist in database)
    - Empty state message (if no entities exist)
16. **Verify** NO error message "Error al cargar las entidades. Por favor, intente de nuevo." appears
17. **Verify** the page is NOT continuously blinking or reloading
18. Take a screenshot of the stable page state

19. **Verify** filter controls are present:
    - Search input field
    - "Tipo de Entidad" dropdown
    - "Compania" text field
    - "Confianza minima" slider
20. Take a screenshot of the filter panel

21. Test filter interaction:
    - Click on "Tipo de Entidad" dropdown
    - Select any entity type (e.g., "Pain Points")
    - **Verify** exactly ONE new request to `/api/rag/entities` is made
    - **Verify** the page updates without entering a loop
22. Take a screenshot of the Network tab after filter change
23. Take a screenshot of the filtered results

24. Test search functionality:
    - Clear the entity type filter
    - Type "test" in the search input
    - Wait 400ms for debounce
    - **Verify** exactly ONE new request to `/api/rag/entities` is made
    - **Verify** no infinite requests occur
25. Take a screenshot of the Network tab after search

26. Click the "Actualizar" (refresh) button in the top-right
27. **Verify** exactly ONE request to `/api/rag/entities` is made
28. **Verify** the page refreshes without errors
29. Take a screenshot of the refreshed page

30. **Verify** the summary statistics section displays:
    - Total entities count chip
    - Consolidated count chip
    - Average confidence chip
    - Top entity type chips (if available)
31. Take a screenshot of the statistics summary

## Success Criteria

- Page loads successfully on first navigation
- Only ONE initial API request to `/api/rag/entities` is made
- NO infinite loop or continuous requests occur
- NO error message appears during normal operation
- Page displays entities list OR empty state (both are valid)
- Filter controls are present and functional
- Applying a filter triggers exactly ONE new API request
- Search input triggers exactly ONE API request after debounce
- Refresh button works and triggers exactly ONE API request
- No continuous blinking or reloading occurs
- Network tab shows clean, single requests for each user action
- 11+ screenshots are taken proving stable behavior

## Expected Network Behavior

**Before the fix:**
- Multiple rapid requests to `/api/rag/entities` within seconds
- Continuous requests without user interaction
- Network tab shows 10+ requests in first few seconds

**After the fix:**
- Single request on page load
- Single request per filter change
- Single request after search debounce
- Single request on refresh button click
- No automatic repeated requests

## Error Handling

- If entities fail to load due to backend error, an error message should appear
- Error message should NOT trigger infinite reload loop
- User should be able to dismiss error and retry manually
