# E2E Test: Entity Management

Test that the Finance Tracker entity management flow works correctly, including creating, viewing, switching between, and managing entities.

## User Story

As a Finance Tracker user
I want to create and switch between different entities like Family and Startup
So that I can keep my personal finances separate from my business finances

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials and is logged in

## Test Steps

### Entity List and Creation

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. Log in with valid test credentials
3. Navigate to the Entities page (`/entities`)
4. Take a screenshot of the entities page
5. **Verify** the entities page loads with:
   - "Entities" or "Entity Management" heading
   - "Create Entity" button is visible
   - Entity list section (may be empty for new user)

6. Click the "Create Entity" button
7. Take a screenshot of the create entity form/modal
8. **Verify** the create entity form displays:
   - Entity name input field
   - Entity type selector (Family/Startup)
   - Description textarea (optional)
   - "Create" or "Save" submit button
   - "Cancel" button

9. Test form validation - submit with empty name
10. Take a screenshot
11. **Verify** validation error is displayed:
    - "Name is required" or similar error message

12. Fill in valid entity data:
    - Name: "My Family Budget"
    - Type: Select "Family"
    - Description: "Family financial tracking"

13. Click "Create" button
14. Take a screenshot
15. **Verify** entity creation success:
    - Success message or toast notification
    - New entity appears in the entity list
    - Entity card/row shows name, type, and description

### Entity Switching

16. Create a second entity:
    - Name: "My Startup"
    - Type: Select "Startup"
    - Description: "Startup financial tracking"

17. Take a screenshot of the entity list with two entities
18. **Verify** both entities are displayed in the list

19. Locate the entity selector component (in header/navbar/sidebar)
20. Take a screenshot showing the entity selector
21. **Verify** entity selector displays:
    - Current entity name
    - Dropdown with all user entities

22. Click on the entity selector
23. Take a screenshot of the dropdown options
24. **Verify** dropdown shows both entities

25. Select a different entity
26. Take a screenshot
27. **Verify** entity switch:
    - Entity selector updates to show new entity name
    - Page content updates to reflect selected entity context

28. Refresh the page
29. Take a screenshot
30. **Verify** entity persistence:
    - Selected entity is restored from localStorage
    - Entity selector shows the previously selected entity

### Entity Update

31. Navigate back to the Entities page (`/entities`)
32. Find the edit button/icon for one of the entities
33. Click the edit button
34. Take a screenshot of the edit form/modal
35. **Verify** edit form displays:
    - Pre-filled entity name
    - Current entity type (may be read-only)
    - Pre-filled description

36. Update the entity name to "Updated Family Budget"
37. Click "Save" or "Update" button
38. Take a screenshot
39. **Verify** entity update success:
    - Success message displayed
    - Entity list shows updated name

### Entity Deletion (Optional - if implemented)

40. Find the delete button/icon for an entity
41. Click the delete button
42. Take a screenshot of the confirmation dialog
43. **Verify** confirmation dialog displays:
    - Warning about deleting the entity
    - "Confirm" and "Cancel" buttons

44. Click "Cancel" to abort deletion
45. **Verify** entity is not deleted

46. Click delete again and confirm deletion
47. Take a screenshot
48. **Verify** entity deletion success:
    - Success message displayed
    - Entity removed from the list

### Error Handling

49. Test accessing entity that user doesn't belong to (if possible via URL manipulation)
50. Take a screenshot
51. **Verify** error handling:
    - Appropriate error message displayed
    - User redirected or access denied message shown

## Success Criteria

- Entities page loads without errors
- Create entity form displays all required fields
- Form validation works correctly for empty/invalid inputs
- Entity creation works and entity appears in list
- Entity selector component displays current entity
- Entity switching updates the application context
- Selected entity persists across page refresh (localStorage)
- Entity update works for authorized users
- Entity deletion shows confirmation and works correctly
- Console shows expected INFO log messages:
  - "INFO [EntityContext]: Fetching entities for user..."
  - "INFO [EntityContext]: Entities loaded successfully"
  - "INFO [EntityContext]: Switching to entity..."
  - "INFO [EntityService]: Creating entity..."

## Technical Verification

- Check browser console for:
  - INFO log messages for entity operations
  - No JavaScript errors
  - No React warnings
- Check localStorage:
  - `currentEntityId` stored after entity selection
  - Value persists across sessions
- Check network requests:
  - GET `/api/entities` on page load
  - POST `/api/entities` on entity creation
  - PUT `/api/entities/{id}` on entity update
  - DELETE `/api/entities/{id}` on entity deletion
  - Authorization header present in all requests

## Notes

- If the backend is not running, entity operations will fail with network errors
- Entity type is constrained to 'family' or 'startup' per database schema
- When a user creates an entity, they automatically become the admin
- Users must be authenticated to access entity management features
- Screenshots should be taken at key steps to document the flow
