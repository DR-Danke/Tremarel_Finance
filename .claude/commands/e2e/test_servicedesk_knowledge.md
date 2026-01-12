# E2E Test: ServiceDesk Knowledge Base Browser

Test the knowledge base browser functionality in the ServiceDesk IT ticketing module.

## User Story

As a user experiencing an IT issue
I want to search and browse knowledge base articles by category and keywords
So that I can find solutions to my problems without waiting for technician support

## Test Steps

1. Navigate to the `Application URL`/servicedesk/knowledge
2. Take a screenshot of the initial state
3. **Verify** the page title is "Base de Conocimiento"
4. **Verify** core UI elements are present:
   - Search bar with placeholder text "Buscar articulos..."
   - Category sidebar (left side)
   - Article grid or list area
   - "Todas las categorias" option in category filter

5. Enter the search query: "problema de red" in the search bar
6. Wait for 600ms (debounce time + buffer)
7. Take a screenshot of the search results
8. **Verify** search results appear (article cards or "No se encontraron articulos" message)

9. Click on a category filter (e.g., "Hardware" or first available category)
10. Wait for filter to apply
11. Take a screenshot of the filtered results
12. **Verify** filtered results show articles matching the category or empty state

13. If articles are available, click on the first article card to view details
14. Take a screenshot of the article detail view
15. **Verify** article detail view displays:
    - Article title
    - Article content
    - "Volver" (Back) button
    - "¿Te fue util este articulo?" section with Si/No buttons

16. Click the "Si" (Helpful) button
17. **Verify** success feedback is shown (snackbar or button state change)
18. Take a screenshot of the rating feedback

19. Click the "Volver" (Back) button
20. **Verify** user returns to knowledge base browser page
21. Take a final screenshot

## Success Criteria

- Knowledge base page loads successfully at /servicedesk/knowledge
- Search bar accepts text input and triggers search after debounce
- Category sidebar displays filter options
- Article cards show title, summary, category, and view count
- Article detail view renders correctly
- Helpfulness rating buttons work and show feedback
- Back navigation returns to browser page
- Responsive layout works correctly
- 6 screenshots are taken

## Notes

- If no articles exist in the database, the test should verify empty states are handled gracefully
- Search may return no results depending on database content
- The test validates UI functionality, not specific data content
