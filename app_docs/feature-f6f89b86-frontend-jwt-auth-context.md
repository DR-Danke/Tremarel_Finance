# Frontend JWT Authentication with AuthContext

**ADW ID:** f6f89b86
**Date:** 2026-01-12
**Specification:** specs/issue-12-adw-f6f89b86-sdlc_planner-frontend-jwt-auth-context.md

## Overview

This feature implements complete frontend authentication for the Finance Tracker application. It includes an AuthContext for global JWT token and user state management, a login page with validated form inputs using react-hook-form, and protected route components for authentication and role-based access control.

## What Was Built

- **AuthContext**: Global state management for user authentication, token storage, and login/logout functions
- **AuthService**: API service for login, register, and /me endpoint calls
- **LoginPage**: Login form with email/password validation using react-hook-form and Material-UI
- **ProtectedRoute**: Route guard that redirects unauthenticated users to login
- **RoleProtectedRoute**: Route guard that restricts access based on user roles
- **DashboardPage**: Protected placeholder dashboard page
- **useAuth Hook**: Convenient hook for accessing AuthContext
- **TypeScript Types**: Updated User interface and added auth-related types

## Technical Implementation

### Files Modified

- `apps/Client/src/main.tsx`: Wrapped App with AuthProvider context
- `apps/Client/src/App.tsx`: Updated routing to use ProtectedRoute and added login/dashboard routes
- `apps/Client/src/types/index.ts`: Updated User interface to match backend (first_name, last_name, is_active) and added LoginCredentials, RegisterData, AuthResponse interfaces

### New Files Created

- `apps/Client/src/contexts/AuthContext.tsx`: AuthProvider component with state management
- `apps/Client/src/contexts/authContextDef.ts`: AuthContext and AuthContextType definitions
- `apps/Client/src/hooks/useAuth.ts`: Custom hook for accessing AuthContext
- `apps/Client/src/services/authService.ts`: API calls for login, register, and /me
- `apps/Client/src/pages/LoginPage.tsx`: Login form component
- `apps/Client/src/pages/DashboardPage.tsx`: Protected dashboard page
- `apps/Client/src/components/auth/ProtectedRoute.tsx`: Authentication route guard
- `apps/Client/src/components/auth/RoleProtectedRoute.tsx`: Role-based route guard
- `.claude/commands/e2e/test_auth_login.md`: E2E test for authentication flow

### Key Changes

- JWT token is stored in localStorage with key `token`
- AuthContext validates stored token on mount by calling `/auth/me` endpoint
- Login form validates email format and password length (min 8 chars)
- ProtectedRoute preserves attempted location for redirect after login
- RoleProtectedRoute shows "Access Denied" UI for unauthorized roles
- All components include logging per CLAUDE.md standards

## How to Use

1. **Navigate to login page**: Go to `/login` to access the login form
2. **Enter credentials**: Provide email and password (min 8 characters)
3. **Access protected routes**: After login, you'll be redirected to `/dashboard`
4. **Logout**: Click the logout button on the dashboard to clear the session

### Using Protected Routes

```typescript
// Basic authentication protection
<ProtectedRoute>
  <DashboardPage />
</ProtectedRoute>

// Role-based protection
<RoleProtectedRoute allowedRoles={['admin', 'manager']}>
  <SettingsPage />
</RoleProtectedRoute>
```

### Using the Auth Hook

```typescript
const { user, isAuthenticated, login, logout, isLoading } = useAuth();

// Check authentication
if (!isAuthenticated) {
  return <Navigate to="/login" />;
}

// Login user
await login({ email: 'user@example.com', password: 'password123' });

// Logout user
logout();
```

## Configuration

The authentication system uses the following localStorage key:
- `token`: Stores the JWT access token

No additional environment variables are required. The authService uses the existing `apiClient` which already has the JWT interceptor configured.

## Testing

Run the E2E test for authentication flow:

```bash
# Read and execute the E2E test
.claude/commands/e2e/test_auth_login.md
```

Manual testing steps:
1. Navigate to `/login` and verify the form renders
2. Submit empty form to verify validation errors
3. Submit invalid credentials to verify error message
4. Submit valid credentials to verify successful login and redirect
5. Refresh page to verify session persistence
6. Click logout to verify session termination

## Notes

- The axios interceptor in `apps/Client/src/api/clients/index.ts` handles adding JWT tokens to requests and clearing them on 401 responses
- User roles: 'admin', 'manager', 'user', 'viewer'
- The User interface uses `first_name` and `last_name` (optional) instead of `name`
- Future features will add registration form and entity context
