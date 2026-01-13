# E2E Test: Client React Vite Setup

Test that the Finance Tracker Client application is properly configured and renders correctly.

## User Story

As a developer
I want to verify that the Finance Tracker Client application loads correctly
So that I can confirm the React + TypeScript + Vite setup is working

## Test Steps

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. Take a screenshot of the initial state
3. **Verify** the page title is "Finance Tracker"
4. **Verify** core UI elements are present on the home page:
   - "Finance Tracker" heading (h1 or h2)
   - Welcome message or description text
   - Material-UI styling is applied (check for MUI classes)

5. Take a screenshot of the home page
6. Navigate to the login page by going to `/login`
7. Take a screenshot of the login page
8. **Verify** the login page displays:
   - "Login" heading
   - Placeholder message about authentication

9. Navigate back to the home page (`/`)
10. **Verify** React Router navigation works (page renders without errors)
11. Take a final screenshot of the home page

## Success Criteria
- Application loads without JavaScript errors
- Home page displays "Finance Tracker" title
- Material-UI theme is applied (primary color visible or MUI components rendered)
- React Router navigation works between `/` and `/login`
- No console errors related to missing dependencies
- 4 screenshots are taken (initial, home, login, final home)

## Technical Verification
- Check browser console for:
  - "INFO [Main]: Initializing Finance Tracker application" log message
  - "INFO [Main]: Finance Tracker application mounted" log message
  - "INFO [App]: Route changed to /" log message
  - No React errors or warnings
