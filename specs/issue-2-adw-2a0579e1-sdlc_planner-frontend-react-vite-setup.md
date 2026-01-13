# Feature: Frontend Project Setup (React + TypeScript + Vite)

## Metadata
issue_number: `2`
adw_id: `2a0579e1`
issue_json: `{"number":2,"title":"[FinanceTracker] Wave 1: Frontend Project Setup","body":"..."}`

## Feature Description
Create the foundational frontend application for the Finance Tracker project using React 19.2.3, TypeScript, and Vite. This setup establishes the Client folder structure with all necessary dependencies (Material-UI 5.x, React Router 6.x, react-hook-form, axios, recharts) and configures the project for production deployment on Vercel. The application will serve as the UI layer for the full-stack income/expense tracking system supporting family and startup company financial management.

## User Story
As a developer working on the Finance Tracker project
I want to have a properly configured React + TypeScript + Vite frontend application
So that I can build UI components and pages following established patterns and deploy to Vercel

## Problem Statement
The Finance Tracker project needs a frontend application to provide the user interface for income/expense tracking. Currently, no frontend infrastructure exists. We need to establish the project structure, install all required dependencies, configure build tools, and set up deployment configuration so that subsequent development work (authentication, layout, transaction management, etc.) can build upon a solid foundation.

## Solution Statement
Create a new `Client` folder at the project root containing a Vite-based React application with TypeScript. The application will follow Clean Architecture principles with organized folders for different concerns (components, pages, services, hooks, contexts, types, theme). Configure Material-UI theming, set up React Router for navigation, and include vercel.json for deployment. This approach ensures consistency with the CLAUDE.md architecture guidelines and provides a maintainable foundation for the full application.

## Relevant Files
Use these files to implement the feature:

- `CLAUDE.md` - Contains the project architecture guidelines, technology stack requirements, folder structure patterns, and code standards that must be followed. Critical for ensuring the frontend setup matches the documented patterns.
- `ai_docs/finance_tracker_implementation_prompts.md` - Contains the full project context and wave structure. Useful for understanding how this issue fits into the broader implementation plan.
- `.claude/commands/test_e2e.md` - Template for understanding how E2E tests are executed. Read this to understand the E2E test runner format.
- `.claude/commands/e2e/e2e_onhold/test_basic_query.md` - Example E2E test file showing the expected format for test steps and success criteria.
- `.ports.env` - Port configuration file that may need updating for the frontend port.

### New Files
The following new files will be created:

**Root Configuration:**
- `Client/package.json` - NPM package configuration with all dependencies
- `Client/tsconfig.json` - TypeScript configuration
- `Client/tsconfig.node.json` - TypeScript config for Node.js (Vite config)
- `Client/vite.config.ts` - Vite build configuration with path aliases
- `Client/vercel.json` - Vercel deployment configuration
- `Client/.env.sample` - Sample environment variables
- `Client/index.html` - HTML entry point

**Source Files:**
- `Client/src/main.tsx` - Application entry point
- `Client/src/App.tsx` - Root component with routing setup
- `Client/src/vite-env.d.ts` - Vite environment type declarations

**Theme:**
- `Client/src/theme/index.ts` - Material-UI theme configuration

**Types:**
- `Client/src/types/index.ts` - Shared TypeScript interfaces

**API:**
- `Client/src/api/clients/index.ts` - Axios HTTP client with JWT interceptor

**Placeholder Directories (with .gitkeep):**
- `Client/src/components/layout/.gitkeep`
- `Client/src/components/forms/.gitkeep`
- `Client/src/components/ui/.gitkeep`
- `Client/src/components/auth/.gitkeep`
- `Client/src/pages/.gitkeep`
- `Client/src/services/.gitkeep`
- `Client/src/hooks/.gitkeep`
- `Client/src/contexts/.gitkeep`
- `Client/src/utils/.gitkeep`

**E2E Test:**
- `.claude/commands/e2e/test_frontend_setup.md` - E2E test to validate the frontend setup

## Implementation Plan
### Phase 1: Foundation
1. Create the Client directory structure
2. Initialize npm project with package.json containing all required dependencies
3. Configure TypeScript with proper settings for React and path aliases
4. Set up Vite with path alias configuration

### Phase 2: Core Implementation
1. Create the HTML entry point (index.html)
2. Create main.tsx as the application entry point
3. Create App.tsx with basic React Router setup
4. Configure Material-UI theme
5. Set up Axios HTTP client with interceptor placeholder

### Phase 3: Integration
1. Add vercel.json for deployment configuration
2. Create .env.sample documenting required environment variables
3. Verify the application builds and runs successfully
4. Create E2E test to validate the setup

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Task 1: Create Client Directory Structure
- Create the `Client` folder at the project root
- Create the following subdirectories:
  - `Client/src/components/layout`
  - `Client/src/components/forms`
  - `Client/src/components/ui`
  - `Client/src/components/auth`
  - `Client/src/pages`
  - `Client/src/services`
  - `Client/src/hooks`
  - `Client/src/contexts`
  - `Client/src/types`
  - `Client/src/theme`
  - `Client/src/api/clients`
  - `Client/src/utils`
- Add `.gitkeep` files to empty directories to ensure they're tracked in git

### Task 2: Create package.json with Dependencies
- Create `Client/package.json` with:
  - Name: `finance-tracker-client`
  - Version: `0.1.0`
  - Type: `module`
  - Scripts: `dev`, `build`, `lint`, `preview`, `typecheck`
  - Dependencies:
    - `react`: `^19.0.0`
    - `react-dom`: `^19.0.0`
    - `@mui/material`: `^5.15.0`
    - `@mui/icons-material`: `^5.15.0`
    - `@emotion/react`: `^11.11.0`
    - `@emotion/styled`: `^11.11.0`
    - `react-router-dom`: `^6.21.0`
    - `react-hook-form`: `^7.49.0`
    - `axios`: `^1.6.0`
    - `recharts`: `^2.10.0`
  - DevDependencies:
    - `@types/react`: `^19.0.0`
    - `@types/react-dom`: `^19.0.0`
    - `@vitejs/plugin-react`: `^4.2.0`
    - `typescript`: `^5.3.0`
    - `vite`: `^5.0.0`
    - `eslint`: `^8.56.0`
    - `@typescript-eslint/eslint-plugin`: `^6.0.0`
    - `@typescript-eslint/parser`: `^6.0.0`
    - `eslint-plugin-react-hooks`: `^4.6.0`
    - `eslint-plugin-react-refresh`: `^0.4.5`

### Task 3: Create TypeScript Configuration
- Create `Client/tsconfig.json` with:
  - Compiler options for React with JSX transform
  - Strict mode enabled
  - Path alias `@/*` mapping to `src/*`
  - ES2020 target with ESNext modules
  - Include `src` directory
- Create `Client/tsconfig.node.json` for Vite config file

### Task 4: Create Vite Configuration
- Create `Client/vite.config.ts` with:
  - React plugin
  - Path alias resolution for `@/`
  - Server port configuration (5173)
  - Build output to `dist`

### Task 5: Create HTML Entry Point
- Create `Client/index.html` with:
  - Standard HTML5 doctype
  - Root div with id `root`
  - Script module pointing to `/src/main.tsx`
  - Title: `Finance Tracker`
  - Meta viewport for responsive design

### Task 6: Create Application Entry Point (main.tsx)
- Create `Client/src/main.tsx` with:
  - React 19 createRoot API
  - StrictMode wrapper
  - BrowserRouter wrapper (from react-router-dom)
  - ThemeProvider wrapper (from @mui/material)
  - CssBaseline for Material-UI reset
  - Import and render App component
  - Console log for application initialization (per CLAUDE.md logging standards)

### Task 7: Create Material-UI Theme Configuration
- Create `Client/src/theme/index.ts` with:
  - Primary color palette (e.g., blue #1976d2)
  - Secondary color palette (e.g., teal #009688)
  - Typography configuration
  - Component overrides for consistent styling
  - Light theme as default

### Task 8: Create Root App Component with Routing
- Create `Client/src/App.tsx` with:
  - React Router Routes and Route components
  - Placeholder route for home page (`/`)
  - Placeholder route for login page (`/login`)
  - Basic welcome message component for home route
  - Console logging for route changes (per CLAUDE.md logging standards)

### Task 9: Create Axios HTTP Client
- Create `Client/src/api/clients/index.ts` with:
  - Axios instance with base URL from environment variable
  - Request interceptor to add JWT Authorization header
  - Response interceptor for error handling
  - Export `apiClient` instance
  - Console logging for API requests/responses (per CLAUDE.md logging standards)

### Task 10: Create TypeScript Types
- Create `Client/src/types/index.ts` with:
  - Base `ApiResponse<T>` interface
  - `User` interface placeholder
  - `AuthState` interface placeholder
  - Export all types

### Task 11: Create Vite Environment Type Declarations
- Create `Client/src/vite-env.d.ts` with:
  - Reference to vite/client types
  - ImportMetaEnv interface with VITE_API_URL and VITE_APP_NAME

### Task 12: Create Environment Sample File
- Create `Client/.env.sample` with:
  - `VITE_API_URL=http://localhost:8000/api`
  - `VITE_APP_NAME=Finance Tracker`

### Task 13: Create Vercel Deployment Configuration
- Create `Client/vercel.json` with:
  - Framework: vite
  - Build command: `npm run build`
  - Output directory: `dist`
  - SPA rewrites for client-side routing

### Task 14: Create ESLint Configuration
- Create `Client/.eslintrc.cjs` with:
  - TypeScript parser
  - React hooks plugin
  - React refresh plugin
  - Recommended rules for TypeScript and React

### Task 15: Install Dependencies and Verify Build
- Navigate to Client directory
- Run `npm install` to install all dependencies
- Run `npm run typecheck` to verify TypeScript configuration
- Run `npm run build` to verify production build works
- Fix any errors that arise

### Task 16: Create E2E Test File
- Read `.claude/commands/test_e2e.md` to understand E2E test runner format
- Read `.claude/commands/e2e/e2e_onhold/test_basic_query.md` as an example
- Create `.claude/commands/e2e/test_frontend_setup.md` with:
  - User story for validating frontend setup
  - Test steps to verify application loads
  - Verification of core UI elements
  - Success criteria
  - Screenshot capture steps

### Task 17: Run Validation Commands
- Execute all validation commands listed in the Validation Commands section
- Ensure all commands pass without errors
- Fix any issues that arise

## Testing Strategy
### Unit Tests
Since this is a project setup task, unit tests are not applicable. The validation will be done through build verification and E2E testing.

### Edge Cases
- Missing environment variables should show helpful error messages
- Application should work with both development and production builds
- Path aliases should resolve correctly in both dev and build modes
- Vercel deployment configuration should handle client-side routing correctly

## Acceptance Criteria
- [ ] Client folder exists with proper directory structure
- [ ] All required dependencies are installed (React 19, MUI 5, React Router 6, react-hook-form, axios, recharts)
- [ ] TypeScript is configured with strict mode and path aliases
- [ ] Vite is configured with React plugin and path aliases
- [ ] Material-UI theme is configured with primary and secondary colors
- [ ] App component renders with React Router setup
- [ ] Axios client is configured with JWT interceptor
- [ ] vercel.json is configured for deployment
- [ ] `npm run dev` starts the development server
- [ ] `npm run build` produces a production build without errors
- [ ] `npm run typecheck` passes without errors
- [ ] E2E test validates the application loads and renders

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd Client && npm install` - Install dependencies
- `cd Client && npm run typecheck` - Run TypeScript type check to validate types are correct
- `cd Client && npm run build` - Run production build to validate the application compiles
- `cd Client && npm run lint` - Run ESLint to check code quality
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_frontend_setup.md` to validate the application renders correctly

## Notes
- React version should be 19.x as specified in CLAUDE.md, not 19.2.3 (which doesn't exist yet). Using latest React 19 stable release.
- The Material-UI version 5.x is chosen for stability and compatibility with React 19.
- Path alias `@/` is configured to map to `src/` for cleaner imports.
- The axios client includes placeholder interceptors that will be fully implemented when authentication is added in Wave 2 (FT-005).
- Context providers (AuthContext, EntityContext) are not created in this issue - they will be added in subsequent issues.
- Console logging is included per CLAUDE.md guidelines for agentic debugging.
- All component names will follow the TR prefix convention once actual components are created.
