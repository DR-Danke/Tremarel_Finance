# E2E Test: Category Management CRUD

Test that the Finance Tracker category management works correctly, including creating, viewing, editing, and deleting income/expense categories with hierarchical structure.

## User Story

As a Finance Tracker user
I want to create, view, edit, and delete income and expense categories with optional subcategories
So that I can organize my financial transactions by category

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials
- At least one entity exists for the test user

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

9. Navigate to `/categories` page
10. Take a screenshot of the categories page
11. **Verify** categories page loads with:
    - Page title "Categories" visible
    - "Add Category" button visible
    - Category tree section visible (may be empty)

12. Click the "Add Category" button
13. Take a screenshot of the category form
14. **Verify** category form displays with:
    - Name input field
    - Type select dropdown (income/expense)
    - Parent category select (optional)
    - Description field (optional)
    - Submit button
    - Cancel button

15. Create a new income category:
    - Enter name: "Salary"
    - Select type: "income"
    - Leave parent empty (root category)
    - Click Submit
16. Take a screenshot
17. **Verify** category created:
    - Success message displayed
    - "Salary" appears in the category tree
    - Category shows as income type (green indicator)

18. Create a new expense category:
    - Click "Add Category" button
    - Enter name: "Food"
    - Select type: "expense"
    - Leave parent empty (root category)
    - Click Submit
19. Take a screenshot
20. **Verify** category created:
    - Success message displayed
    - "Food" appears in the category tree
    - Category shows as expense type (red indicator)

21. Create a subcategory:
    - Click "Add Category" button
    - Enter name: "Groceries"
    - Select type: "expense" (should match parent type)
    - Select parent: "Food"
    - Click Submit
22. Take a screenshot
23. **Verify** subcategory created:
    - Success message displayed
    - "Groceries" appears under "Food" in the tree
    - Hierarchical indentation is visible

24. Create another subcategory:
    - Click "Add Category" button
    - Enter name: "Restaurants"
    - Select type: "expense"
    - Select parent: "Food"
    - Click Submit
25. Take a screenshot
26. **Verify** subcategory created:
    - "Restaurants" appears under "Food" in the tree
    - Both "Groceries" and "Restaurants" are children of "Food"

27. Edit a category:
    - Click the edit button (pencil icon) on "Groceries"
28. Take a screenshot of edit form
29. **Verify** edit form displays with:
    - Current name "Groceries" pre-filled
    - Type select disabled (cannot change type)
    - Current parent "Food" selected

30. Update the category name:
    - Change name from "Groceries" to "Supermarket"
    - Click Submit
31. Take a screenshot
32. **Verify** category updated:
    - Success message displayed
    - "Supermarket" appears in tree (instead of "Groceries")
    - Still under "Food" parent

33. Delete a category without children:
    - Click the delete button (trash icon) on "Restaurants"
    - Confirm deletion in dialog
34. Take a screenshot
35. **Verify** category deleted:
    - Success message displayed
    - "Restaurants" no longer appears in tree
    - "Food" still exists with "Supermarket" child

36. Attempt to delete a category with children:
    - Click the delete button on "Food" (has "Supermarket" child)
37. Take a screenshot
38. **Verify** deletion prevented:
    - Error message displayed
    - Message indicates category has children
    - "Food" still exists in tree

39. Expand and collapse category tree:
    - Click collapse button on "Food"
40. Take a screenshot
41. **Verify** category collapsed:
    - Children of "Food" are hidden

42. Click expand button on "Food"
43. **Verify** category expanded:
    - "Supermarket" is visible again under "Food"

44. Navigate away and back to verify persistence:
    - Navigate to `/dashboard`
    - Navigate back to `/categories`
45. Take a screenshot
46. **Verify** categories persisted:
    - "Salary" (income) still visible
    - "Food" (expense) still visible
    - "Supermarket" still under "Food"

## Success Criteria

- Categories page loads without errors
- Category form displays all required fields
- Can create root income category
- Can create root expense category
- Can create subcategory with parent
- Subcategory type matches parent type
- Category tree displays hierarchical structure
- Can edit category name
- Can delete category without children
- Cannot delete category with children (error shown)
- Tree expand/collapse works correctly
- Categories persist after navigation
- All CRUD operations show appropriate success/error messages
- Console shows expected INFO log messages:
  - "INFO [CategoryService]: Creating category..."
  - "INFO [CategoryService]: Updating category..."
  - "INFO [CategoryService]: Deleting category..."

## Technical Verification

- Check browser console for:
  - INFO log messages for category operations
  - No JavaScript errors
  - No React warnings
- Check network requests:
  - POST to `/api/categories` on create
  - GET to `/api/categories/entity/{id}/tree` on load
  - PUT to `/api/categories/{id}` on update
  - DELETE to `/api/categories/{id}` on delete
  - Authorization header present in all requests

## Notes

- If backend is not running, API calls will fail with network error
- Test user must have access to at least one entity
- Categories are entity-specific - only categories for current entity should display
- Parent selection dropdown should only show categories of same type
- Color and icon fields are optional and may not be visible in basic form
