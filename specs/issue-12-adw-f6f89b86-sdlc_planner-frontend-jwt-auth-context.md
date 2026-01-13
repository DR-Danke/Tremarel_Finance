# Feature: Frontend JWT Authentication with AuthContext

## Metadata
issue_number: `12`
adw_id: `f6f89b86`
issue_json: `{"number":12,"title":"[FinanceTracker] Wave 2: Frontend Authentication","body":"## Context\n**Project:** Finance Tracker - Income & Expense Management\n**Current Wave:** Wave 2 of 6 - Authentication\n**Current Issue:** FT-005 (Issue 5 of 14)\n\n## Request\nAdd authentication to the frontend with AuthContext for managing JWT tokens and user state. Create a login page with email/password form using react-hook-form. Implement ProtectedRoute and RoleProtectedRoute components. Store JWT in localStorage and include it in all API requests via axios interceptor. Add logout functionality."}`

## Feature Description
This feature implements complete frontend authentication for the Finance Tracker application. It includes an AuthContext that manages JWT tokens and user state globally, a login page with email/password form using react-hook-form and Material-UI, protected route components for authentication and role-based access control, and integration with the existing axios interceptor to include JWT tokens in all API requests.

## User Story
As a Finance Tracker user
I want to securely log in to the application with my email and password
So that I can access my financial data and be protected from unauthorized access

## Problem Statement
The Finance Tracker frontend currently has no authentication system. Users cannot log in, and there is no way to protect routes or manage user sessions. The backend JWT authentication (FT-004) is complete, but the frontend cannot utilize it.

## Solution Statement
Implement a React Context-based authentication system that:
1. Manages JWT tokens and user state via AuthContext
2. Provides a login page with validated form inputs
3. Protects routes based on authentication status (ProtectedRoute)
4. Protects routes based on user roles (RoleProtectedRoute)
5. Automatically includes JWT tokens in API requests via the existing axios interceptor
6. Handles logout with proper token cleanup

## Relevant Files
Use these files to implement the feature:

### Existing Files to Modify
- `apps/Client/src/main.tsx`: Wrap App with AuthProvider context
- `apps/Client/src/App.tsx`: Update routing to use ProtectedRoute and add dashboard route
- `apps/Client/src/types/index.ts`: Update User interface to match backend response (add first_name, last_name, is_active; remove name)
- `apps/Client/src/api/clients/index.ts`: Already has JWT interceptor, may need minor adjustments for auth state integration

### New Files
- `apps/Client/src/contexts/AuthContext.tsx`: AuthContext with user state, token management, login/logout functions
- `apps/Client/src/hooks/useAuth.ts`: Custom hook for accessing AuthContext
- `apps/Client/src/services/authService.ts`: API calls for login, register, and /me endpoints
- `apps/Client/src/pages/LoginPage.tsx`: Login page with react-hook-form
- `apps/Client/src/pages/DashboardPage.tsx`: Protected dashboard page (placeholder)
- `apps/Client/src/components/auth/ProtectedRoute.tsx`: Route guard for authenticated users
- `apps/Client/src/components/auth/RoleProtectedRoute.tsx`: Route guard for specific roles
- `.claude/commands/e2e/test_auth_login.md`: E2E test for authentication flow

### Reference Files
- `app_docs/feature-ed4cef49-backend-jwt-auth-rbac.md`: Backend auth implementation details
- `app_docs/feature-2a0579e1-frontend-react-vite-setup.md`: Frontend setup and patterns
- `apps/Server/src/interface/auth_dto.py`: Backend DTOs defining API request/response shapes
- `apps/Server/src/adapter/rest/auth_routes.py`: Backend auth endpoints
- `.claude/commands/test_e2e.md`: E2E test runner format
- `.claude/commands/e2e/test_frontend_setup.md`: Example E2E test structure

## Implementation Plan
### Phase 1: Foundation
1. Update TypeScript types to match backend response format
2. Create auth service for API calls (login, register, /me)
3. Create AuthContext with state management

### Phase 2: Core Implementation
4. Create useAuth hook for convenient context access
5. Create login page with react-hook-form validation
6. Create ProtectedRoute component
7. Create RoleProtectedRoute component

### Phase 3: Integration
8. Wrap App with AuthProvider in main.tsx
9. Update App.tsx routing with protected routes
10. Create placeholder dashboard page
11. Create E2E test for authentication flow
12. Run validation commands

## Step by Step Tasks

### Task 1: Update TypeScript User Interface
- Open `apps/Client/src/types/index.ts`
- Update the `User` interface to match backend `UserResponseDTO`:
  - Change `name` to `first_name` and `last_name` (both optional)
  - Add `is_active: boolean`
  - Keep `id`, `email`, `role`, `createdAt`, `updatedAt`
- Add `LoginCredentials` interface: `{ email: string; password: string }`
- Add `RegisterData` interface: `{ email: string; password: string; first_name?: string; last_name?: string }`
- Add `AuthResponse` interface: `{ access_token: string; token_type: string; user: User }`

### Task 2: Create Auth Service
- Create `apps/Client/src/services/authService.ts`
- Import `apiClient` from `@/api/clients`
- Implement `login(credentials: LoginCredentials): Promise<AuthResponse>` - POST to `/auth/login`
- Implement `register(data: RegisterData): Promise<AuthResponse>` - POST to `/auth/register`
- Implement `getCurrentUser(): Promise<User>` - GET to `/auth/me`
- Add proper logging per CLAUDE.md standards (`console.log('INFO [AuthService]: ...')`)

### Task 3: Create AuthContext
- Create `apps/Client/src/contexts/AuthContext.tsx`
- Define `AuthContextType` interface with:
  - `user: User | null`
  - `token: string | null`
  - `isAuthenticated: boolean`
  - `isLoading: boolean`
  - `login: (credentials: LoginCredentials) => Promise<void>`
  - `logout: () => void`
- Create `AuthContext` with `createContext`
- Create `AuthProvider` component that:
  - Initializes token from localStorage on mount
  - Calls `/auth/me` to validate token and get user data
  - Sets `isLoading: true` during initialization
  - Provides `login` function that calls authService.login, stores token, sets user state
  - Provides `logout` function that clears token from localStorage and state
  - Export `AuthContext` and `AuthProvider`
- Add proper logging for all state changes

### Task 4: Create useAuth Hook
- Create `apps/Client/src/hooks/useAuth.ts`
- Import `useContext` from React
- Import `AuthContext` from `@/contexts/AuthContext`
- Create `useAuth` hook that returns context value
- Throw error if used outside AuthProvider

### Task 5: Create Login Page
- Create `apps/Client/src/pages/LoginPage.tsx`
- Import react-hook-form: `useForm`
- Import MUI components: `TextField`, `Button`, `Box`, `Typography`, `Container`, `Alert`, `Paper`
- Import `useAuth` hook and `useNavigate` from react-router-dom
- Create form with:
  - Email field with validation (required, valid email format)
  - Password field with validation (required, min 8 chars)
  - Submit button with loading state
  - Error display using MUI Alert
- On successful login, navigate to `/dashboard`
- If already authenticated, redirect to `/dashboard`
- Add proper logging for form submission and errors

### Task 6: Create ProtectedRoute Component
- Create `apps/Client/src/components/auth/ProtectedRoute.tsx`
- Import `Navigate`, `useLocation` from react-router-dom
- Import `useAuth` hook
- Accept `children` prop
- If `isLoading`, show loading indicator (MUI CircularProgress)
- If not authenticated, redirect to `/login` preserving the attempted location
- Otherwise render children
- Log route access attempts

### Task 7: Create RoleProtectedRoute Component
- Create `apps/Client/src/components/auth/RoleProtectedRoute.tsx`
- Import `Navigate` from react-router-dom
- Import `useAuth` hook
- Accept `children` and `allowedRoles: string[]` props
- If `isLoading`, show loading indicator
- If not authenticated, redirect to `/login`
- If authenticated but role not in allowedRoles, redirect to `/unauthorized` or show access denied
- Otherwise render children
- Log role check attempts

### Task 8: Create Dashboard Page
- Create `apps/Client/src/pages/DashboardPage.tsx`
- Create placeholder dashboard with:
  - Welcome message showing user's name/email
  - Logout button
  - Typography stating "Dashboard features coming soon"
- Import `useAuth` hook to access user data
- Use MUI components for consistent styling

### Task 9: Update main.tsx with AuthProvider
- Open `apps/Client/src/main.tsx`
- Import `AuthProvider` from `@/contexts/AuthContext`
- Wrap the App component with `AuthProvider` (inside BrowserRouter, outside ThemeProvider or around everything)
- Order: StrictMode > BrowserRouter > AuthProvider > ThemeProvider > App

### Task 10: Update App.tsx with Routes
- Open `apps/Client/src/App.tsx`
- Import `ProtectedRoute` from `@/components/auth/ProtectedRoute`
- Import `LoginPage` from `@/pages/LoginPage`
- Import `DashboardPage` from `@/pages/DashboardPage`
- Update routes:
  - Keep `/` as HomePage (public)
  - Update `/login` to use LoginPage component
  - Add `/dashboard` wrapped in ProtectedRoute with DashboardPage
- Remove the inline LoginPage function (now using separate file)

### Task 11: Create E2E Test for Authentication
- Create `.claude/commands/e2e/test_auth_login.md`
- User Story: As a user, I want to log in and access protected pages
- Test Steps:
  1. Navigate to home page, verify it loads
  2. Navigate to `/login` page
  3. Verify login form is visible with email and password fields
  4. Enter invalid credentials, submit, verify error message
  5. Navigate to `/dashboard` (should redirect to login)
  6. Log in with valid test credentials
  7. Verify redirect to dashboard
  8. Verify user info is displayed
  9. Click logout
  10. Verify redirect to login page
  11. Take screenshots at key steps
- Success Criteria: All navigation and auth flows work correctly

### Task 12: Run Validation Commands
- Run `cd apps/Client && npm run typecheck` to validate TypeScript
- Run `cd apps/Client && npm run build` to validate production build
- Run `cd apps/Client && npm run lint` to check for lint errors
- Fix any errors that arise

## Testing Strategy
### Unit Tests
- AuthContext: Test login, logout, and token persistence
- useAuth hook: Test proper context access
- ProtectedRoute: Test redirect behavior based on auth state
- RoleProtectedRoute: Test role-based access control

### Edge Cases
- Token expired: User should be redirected to login on 401 response
- Invalid token in localStorage: Should clear and redirect to login
- Network error during login: Should show appropriate error message
- Already authenticated user visiting login page: Should redirect to dashboard
- User without required role accessing protected route: Should show access denied

## Acceptance Criteria
- [ ] User can navigate to login page and see email/password form
- [ ] Form validates email format and password length (min 8 chars)
- [ ] Invalid credentials show error message
- [ ] Successful login stores JWT in localStorage
- [ ] Successful login redirects to dashboard
- [ ] User info is displayed on dashboard (email or name)
- [ ] Logout clears token and redirects to login
- [ ] Unauthenticated users cannot access `/dashboard`
- [ ] Refreshing page with valid token maintains authentication
- [ ] 401 responses clear token and redirect to login
- [ ] All TypeScript types are correct (no `any`)
- [ ] Build completes without errors

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npm install` - Install any missing dependencies
- `cd apps/Client && npm run typecheck` - Run Client type check to validate TypeScript types
- `cd apps/Client && npm run lint` - Run linting to check code quality
- `cd apps/Client && npm run build` - Run Client build to validate the feature works with zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_auth_login.md` to validate authentication flow E2E

## Notes
- The axios interceptor in `apps/Client/src/api/clients/index.ts` already handles adding the JWT token to requests and clearing it on 401 responses. The AuthContext should work with this existing behavior.
- The backend auth API returns `first_name` and `last_name` as optional fields, which differs from the original `name` field in the frontend types.
- The User interface `role` field uses the same values as the backend: 'admin', 'manager', 'user', 'viewer'.
- For E2E testing, you may need test user credentials. Either create a test user via the registration endpoint or use a known test user from the database.
- Future features will add registration form and entity context, which will expand on this auth foundation.
