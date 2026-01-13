# Frontend React + Vite Setup

**ADW ID:** 2a0579e1
**Date:** 2026-01-12
**Specification:** specs/issue-2-adw-2a0579e1-sdlc_planner-frontend-react-vite-setup.md

## Overview

Foundational React + TypeScript + Vite frontend application setup for the Finance Tracker project. This establishes the Client folder structure with all necessary dependencies (Material-UI, React Router, react-hook-form, axios, recharts) and configures the project for production deployment on Vercel.

## What Was Built

- Complete React 19 + TypeScript + Vite project scaffold
- Material-UI 5.x theming with custom color palette
- React Router 6.x with placeholder routes (home, login)
- Axios HTTP client with JWT interceptor
- Clean Architecture folder structure
- Vercel deployment configuration
- E2E test for frontend setup validation

## Technical Implementation

### Files Modified

- `Client/package.json`: NPM configuration with React 19, MUI 5, React Router 6, axios, recharts dependencies
- `Client/tsconfig.json`: TypeScript strict mode with `@/` path alias
- `Client/vite.config.ts`: Vite with React plugin and path alias resolution
- `Client/vercel.json`: SPA deployment configuration for Vercel
- `Client/src/main.tsx`: Application entry point with providers (ThemeProvider, BrowserRouter, StrictMode)
- `Client/src/App.tsx`: Root component with React Router setup and placeholder pages
- `Client/src/theme/index.ts`: Material-UI theme (primary: blue #1976d2, secondary: teal #009688)
- `Client/src/api/clients/index.ts`: Axios instance with JWT interceptor and error handling
- `Client/src/types/index.ts`: Base TypeScript interfaces (ApiResponse, User, AuthState)
- `.claude/commands/e2e/test_frontend_setup.md`: E2E test for validating the setup

### Key Changes

- **React 19 with StrictMode**: Uses latest React with createRoot API
- **Path alias `@/`**: Configured in both TypeScript and Vite for clean imports
- **JWT interceptor**: Automatically attaches Bearer token from localStorage to all API requests
- **Console logging**: All operations include INFO/ERROR logging per CLAUDE.md standards
- **Placeholder directories**: `.gitkeep` files in components/auth, components/forms, components/layout, components/ui, contexts, hooks, pages, services, utils

## How to Use

1. Navigate to the Client directory: `cd Client`
2. Install dependencies: `npm install`
3. Start development server: `npm run dev` (runs on http://localhost:5173)
4. Build for production: `npm run build`
5. Run type checking: `npm run typecheck`
6. Run linting: `npm run lint`

## Configuration

### Environment Variables (Client/.env)

```bash
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=Finance Tracker
```

### Theme Customization

The MUI theme is defined in `Client/src/theme/index.ts`:
- Primary color: Blue (#1976d2)
- Secondary color: Teal (#009688)
- Light mode default
- Custom component overrides (rounded buttons/cards)

### Path Alias

Use `@/` prefix for imports from the src directory:
```typescript
import { apiClient } from '@/api/clients'
import theme from '@/theme'
```

## Testing

Run the E2E test to validate the frontend setup:
1. Read `.claude/commands/test_e2e.md` for the test runner format
2. Execute `.claude/commands/e2e/test_frontend_setup.md`

Validation commands:
```bash
cd Client && npm install
cd Client && npm run typecheck
cd Client && npm run build
cd Client && npm run lint
```

## Notes

- Authentication context (AuthContext) and entity context (EntityContext) are not implemented - they will be added in subsequent features
- The login page is a placeholder - full authentication will be implemented later
- All TR-prefixed components will be added in future features
- The axios client includes 401 handling that clears tokens and logs the user out
