# Feature: Frontend React + Vite Project Setup

## Metadata
issue_number: `2`
adw_id: `3571938c`
issue_json: `{"number":2,"title":"[FinanceTracker] Wave 1: Frontend Project Setup","body":"..."}`

## Feature Description
Create the foundational frontend project structure for the Finance Tracker application using React 19.2.3, TypeScript 5.x, and Vite as the build tool. This includes setting up Material-UI for UI components, React Router for navigation, react-hook-form for form handling, axios for HTTP requests, and recharts for data visualization. The project will follow Clean Architecture principles with a clear folder structure for components, pages, services, hooks, contexts, types, and theme configuration.

## User Story
As a developer
I want a well-structured React frontend project with all necessary dependencies
So that I can build the Finance Tracker application with consistent patterns and best practices

## Problem Statement
The Finance Tracker application needs a frontend foundation that supports:
- Modern React 19.2.3 with TypeScript for type safety
- Fast development experience with Vite
- Consistent UI components with Material-UI
- Client-side routing with React Router
- Form handling with react-hook-form
- HTTP communication with axios (JWT interceptor ready)
- Data visualization with recharts
- Deployment to Vercel

## Solution Statement
Create a complete React + TypeScript + Vite project in the `Client/` folder with:
1. All required dependencies installed and configured
2. Clean Architecture folder structure (pages, components, services, hooks, contexts, types, theme)
3. MUI theme configuration with Finance Tracker branding
4. Basic App component with React Router setup
5. Vercel deployment configuration (vercel.json)
6. Environment variable setup for API URL
7. Path alias configuration (@/) for clean imports

## Relevant Files
Use these files to implement the feature:

- `CLAUDE.md` - Project instructions with technology stack details (React 19.2.3, MUI 5.x, React Router 6.x, etc.)
- `README.md` - Project overview explaining the Agent Layer Primitives structure
- `apps/main.ts` - Existing TypeScript placeholder showing minimal setup pattern
- `.claude/commands/test_e2e.md` - E2E test runner documentation to understand how to create E2E tests
- `.claude/commands/e2e/e2e_onhold/test_basic_query.md` - Example E2E test format

### New Files
The following files will be created in the `Client/` folder:

**Configuration Files:**
- `Client/package.json` - NPM package configuration with all dependencies
- `Client/tsconfig.json` - TypeScript configuration with strict mode
- `Client/tsconfig.node.json` - TypeScript config for Vite node environment
- `Client/vite.config.ts` - Vite configuration with path aliases
- `Client/vercel.json` - Vercel deployment configuration with SPA routing
- `Client/.env.example` - Example environment variables
- `Client/.gitignore` - Git ignore rules for Node projects
- `Client/index.html` - Entry HTML file for Vite

**Source Files:**
- `Client/src/main.tsx` - Application entry point (ENTRY POINT)
- `Client/src/App.tsx` - Root component with React Router setup
- `Client/src/vite-env.d.ts` - Vite environment type declarations

**Folder Structure Placeholders:**
- `Client/src/api/clients/.gitkeep` - HTTP clients folder placeholder
- `Client/src/components/layout/.gitkeep` - Layout components placeholder
- `Client/src/components/forms/.gitkeep` - Form components (FK-prefixed)
- `Client/src/components/ui/.gitkeep` - Reusable UI components (FK-prefixed)
- `Client/src/components/auth/.gitkeep` - Auth components (ProtectedRoute)
- `Client/src/contexts/.gitkeep` - React contexts (AuthContext, EntityContext)
- `Client/src/hooks/.gitkeep` - Custom hooks (useAuth, etc.)
- `Client/src/pages/.gitkeep` - Route pages
- `Client/src/services/.gitkeep` - Business logic/API services
- `Client/src/types/.gitkeep` - TypeScript interfaces
- `Client/src/theme/index.ts` - MUI theme configuration
- `Client/src/utils/.gitkeep` - Utility functions

**E2E Test File:**
- `.claude/commands/e2e/test_frontend_setup.md` - E2E test for frontend setup validation

## Implementation Plan
### Phase 1: Foundation
1. Create the `Client/` folder structure
2. Initialize npm project with package.json containing all dependencies
3. Configure TypeScript with tsconfig.json
4. Configure Vite with path aliases

### Phase 2: Core Implementation
1. Create index.html entry point
2. Create main.tsx as the application entry point
3. Create App.tsx with React Router setup
4. Create MUI theme configuration
5. Set up environment variables

### Phase 3: Integration
1. Create folder structure with .gitkeep files
2. Add Vercel deployment configuration
3. Validate build and type checking
4. Create E2E test for validation

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Create Client Folder Structure
- Create `Client/` directory in the project root
- Create `Client/src/` subdirectory for source code

### 2. Initialize Package.json with Dependencies
- Create `Client/package.json` with:
  - React 19.2.3 and React DOM
  - TypeScript 5.x
  - Vite 5.x with React plugin
  - Material-UI 5.x (@mui/material, @mui/icons-material, @emotion/react, @emotion/styled)
  - React Router 6.x (react-router-dom)
  - react-hook-form
  - axios
  - recharts
  - Development dependencies (TypeScript, ESLint, Vite, @types/node)
- Add npm scripts: dev, build, preview, lint, typecheck

### 3. Configure TypeScript
- Create `Client/tsconfig.json` with strict mode enabled
- Configure path alias `@/*` mapping to `./src/*`
- Include React JSX support
- Create `Client/tsconfig.node.json` for Vite configuration

### 4. Configure Vite
- Create `Client/vite.config.ts` with:
  - React plugin (@vitejs/plugin-react)
  - Path alias resolution (@/ -> src/)
  - Server configuration for port 5173

### 5. Create HTML Entry Point
- Create `Client/index.html` with:
  - Root div element
  - Script module pointing to main.tsx
  - Proper meta tags and title

### 6. Create Application Entry Point
- Create `Client/src/main.tsx` with:
  - React 19 createRoot
  - StrictMode wrapper
  - App component import
  - Console log for agent debugging

### 7. Create MUI Theme Configuration
- Create `Client/src/theme/index.ts` with:
  - Custom color palette (primary, secondary)
  - Typography configuration
  - Component overrides for consistent styling
  - Export createTheme result

### 8. Create App Component with Router
- Create `Client/src/App.tsx` with:
  - BrowserRouter from React Router
  - ThemeProvider with custom theme
  - CssBaseline for consistent styling
  - Basic Routes setup with placeholder Home route
  - Console log for agent debugging

### 9. Create Vite Environment Types
- Create `Client/src/vite-env.d.ts` with Vite client types reference

### 10. Create Environment Configuration
- Create `Client/.env.example` with:
  - VITE_API_URL=http://localhost:8000/api
  - VITE_APP_NAME=Finance Tracker

### 11. Create Git Ignore
- Create `Client/.gitignore` with Node.js/Vite ignore patterns

### 12. Create Folder Structure with Placeholders
- Create all subdirectories with .gitkeep files:
  - `Client/src/api/clients/`
  - `Client/src/components/layout/`
  - `Client/src/components/forms/`
  - `Client/src/components/ui/`
  - `Client/src/components/auth/`
  - `Client/src/contexts/`
  - `Client/src/hooks/`
  - `Client/src/pages/`
  - `Client/src/services/`
  - `Client/src/types/`
  - `Client/src/utils/`

### 13. Create Vercel Configuration
- Create `Client/vercel.json` with:
  - Build output configuration
  - SPA routing (rewrites to index.html)
  - Framework detection settings

### 14. Create E2E Test File
- Create `.claude/commands/e2e/test_frontend_setup.md` with:
  - User story for frontend setup validation
  - Test steps to verify the dev server starts
  - Verify homepage loads with correct title
  - Verify MUI theme is applied
  - Capture screenshots of initial state

### 15. Install Dependencies and Build
- Run `cd Client && npm install` to install dependencies
- Run `cd Client && npm run build` to verify production build

### 16. Run Validation Commands
- Execute all validation commands to ensure zero regressions

## Testing Strategy
### Unit Tests
- Not applicable for initial project setup (no business logic yet)
- Future tests will go in `Client/src/__tests__/` directory

### Edge Cases
- Verify path aliases work correctly with TypeScript
- Verify environment variables are accessible in code
- Verify Vercel build succeeds with SPA routing

## Acceptance Criteria
- [ ] Client folder exists with complete folder structure
- [ ] All dependencies installed successfully (npm install exits with code 0)
- [ ] TypeScript compilation succeeds (npm run typecheck exits with code 0)
- [ ] Production build succeeds (npm run build exits with code 0)
- [ ] Dev server starts on port 5173 (npm run dev works)
- [ ] MUI theme is configured and exported
- [ ] React Router is configured in App.tsx
- [ ] Path alias @/ works for imports
- [ ] vercel.json is configured for SPA deployment
- [ ] E2E test file created for frontend validation

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd Client && npm install` - Install all dependencies
- `cd Client && npm run typecheck` - Run TypeScript type checking to verify no type errors
- `cd Client && npm run build` - Run production build to verify bundle generation
- `ls -la Client/src/` - Verify source folder structure exists
- `ls -la Client/src/components/` - Verify components folder structure
- `ls -la Client/src/theme/` - Verify theme folder with index.ts

## Notes
- React 19.2.3 is specified per CLAUDE.md requirements
- Material-UI 5.x is used for consistent UI components
- The FK prefix convention for components will be applied in future implementations
- Path alias @/ is configured to reduce relative import complexity
- Vercel configuration uses rewrites for SPA client-side routing
- The E2E test validates the dev server and basic page load (no complex interactions yet since this is just setup)
- Future waves will add authentication, transactions, and other features on top of this foundation
