# E2E Test: Authentication Login Flow

Test that the Finance Tracker authentication flow works correctly, including login, protected routes, and logout.

## User Story

As a Finance Tracker user
I want to securely log in with my email and password
So that I can access my financial data and protected features

## Prerequisites

- Backend server running at http://localhost:8000
- Frontend server running at http://localhost:5173
- A test user account exists with valid credentials

## Test Steps

1. Navigate to the `Application URL` (default: http://localhost:5173)
2. Take a screenshot of the home page
3. **Verify** the home page loads with:
   - "Finance Tracker" heading
   - "Sign In" button is visible
   - "Dashboard" button is visible

4. Click the "Dashboard" button (without logging in)
5. Take a screenshot
6. **Verify** redirect to login page (`/login`)
7. **Verify** login form is displayed with:
   - "Login" heading
   - Email input field
   - Password input field
   - "Sign In" submit button

8. Test form validation - submit with empty fields
9. Take a screenshot
10. **Verify** validation errors are displayed:
    - "Email is required" error message
    - "Password is required" error message

11. Enter invalid email format (e.g., "invalid-email")
12. Enter a password less than 8 characters (e.g., "short")
13. Take a screenshot
14. **Verify** validation errors are displayed:
    - "Invalid email address" error message
    - "Password must be at least 8 characters" error message

15. Clear form and enter valid test credentials:
    - Email: test@example.com (or a valid test user email)
    - Password: testpassword123 (or valid test password)

16. Click "Sign In" button
17. Take a screenshot
18. **Verify** one of these outcomes:
    - Success: Redirected to dashboard page (`/dashboard`)
    - Error: Error message displayed (if test credentials invalid)

19. If login successful:
    - **Verify** dashboard page displays:
      - Welcome message with user name or email
      - User role displayed
      - "Logout" button visible
    - Take a screenshot of dashboard

20. Click the "Logout" button
21. Take a screenshot
22. **Verify** redirect to login page
23. **Verify** user is logged out (token cleared)

24. Navigate directly to `/dashboard`
25. Take a screenshot
26. **Verify** redirect to login page (protected route working)

## Success Criteria

- Home page loads without errors
- Login form displays all required fields
- Form validation works correctly for:
  - Empty fields (required validation)
  - Invalid email format
  - Password too short
- Protected routes redirect unauthenticated users to login
- Login preserves attempted location for redirect after auth
- Dashboard displays user information after login
- Logout clears authentication and redirects to login
- Console shows expected INFO log messages:
  - "INFO [App]: Route changed to /login"
  - "INFO [AuthContext]: Login attempt for: ..."
  - "INFO [AuthContext]: Login successful..."
  - "INFO [AuthContext]: Logging out user..."

## Technical Verification

- Check browser console for:
  - INFO log messages for auth state changes
  - No JavaScript errors
  - No React warnings
- Check localStorage:
  - Token stored after login
  - Token cleared after logout
- Check network requests:
  - POST to `/api/auth/login` on login attempt
  - Authorization header present in subsequent requests

## Notes

- If the backend is not running, the login will fail with a network error
- Test user credentials depend on the backend database state
- Screenshots should be taken at key steps to document the flow
