# Finance Tracker - ADW Implementation Prompts

## Overview

This plan contains GitHub issue prompts for implementing the Finance Tracker application using `adw_sdlc_iso.py`. Each prompt will trigger the `/feature` command which handles technical planning.

**Execution**: `uv run adw_sdlc_iso.py <issue-number>`

**Parallelization**: Issues within the same wave can run simultaneously in separate worktrees (up to 15 concurrent).

---

## Wave 1: Foundation (Run in Parallel)

These three issues establish the base infrastructure and can run simultaneously since they're independent.

### FT-001: Backend Project Setup

**Title:** `[FinanceTracker] Wave 1: Backend Project Setup`

**Body:**
```markdown
## Context
**Project:** Finance Tracker - Income & Expense Management
**Overview:** We are building a full-stack income/expense tracking application for family and startup company management. The system includes multi-entity support (family/startup separation), custom JWT authentication, transaction management, budgeting, reporting with charts, and CSV export. Frontend deploys to Vercel, backend to Render, database on Supabase PostgreSQL.

**Current Wave:** Wave 1 of 6 - Foundation
**Current Issue:** FT-001 (Issue 1 of 14)
**Parallel Execution:** YES - This issue runs in parallel with FT-002 (Frontend Setup) and FT-003 (Database Schema). All three are independent foundation pieces.

**What comes next:** After Wave 1 completes, Wave 2 begins with sequential authentication implementation (FT-004 Backend Auth, then FT-005 Frontend Auth).

## Request
Create the Server folder with a FastAPI application. Include the basic project structure with folders for routes, services, repositories, models, and configuration. Set up the main entry point, health check endpoint, CORS configuration, and requirements.txt with all necessary dependencies. The backend should be ready to run with uvicorn.
```

---

### FT-002: Frontend Project Setup

**Title:** `[FinanceTracker] Wave 1: Frontend Project Setup`

**Body:**
```markdown
## Context
**Project:** Finance Tracker - Income & Expense Management
**Overview:** We are building a full-stack income/expense tracking application for family and startup company management. The system includes multi-entity support (family/startup separation), custom JWT authentication, transaction management, budgeting, reporting with charts, and CSV export. Frontend deploys to Vercel, backend to Render, database on Supabase PostgreSQL.

**Current Wave:** Wave 1 of 6 - Foundation
**Current Issue:** FT-002 (Issue 2 of 14)
**Parallel Execution:** YES - This issue runs in parallel with FT-001 (Backend Setup) and FT-003 (Database Schema). All three are independent foundation pieces.

**What comes next:** After Wave 1 completes, Wave 2 begins with sequential authentication implementation (FT-004 Backend Auth, then FT-005 Frontend Auth).

## Request
Create the Client folder with a React 19.2.3 + TypeScript + Vite application. Include Material-UI, React Router, react-hook-form, axios, and recharts. Set up the basic project structure with folders for components, pages, services, hooks, contexts, types, and theme. Configure the MUI theme and create a basic App component with routing setup. Include vercel.json for deployment.
```

---

### FT-003: Database Schema

**Title:** `[FinanceTracker] Wave 1: Database Schema`

**Body:**
```markdown
## Context
**Project:** Finance Tracker - Income & Expense Management
**Overview:** We are building a full-stack income/expense tracking application for family and startup company management. The system includes multi-entity support (family/startup separation), custom JWT authentication, transaction management, budgeting, reporting with charts, and CSV export. Frontend deploys to Vercel, backend to Render, database on Supabase PostgreSQL.

**Current Wave:** Wave 1 of 6 - Foundation
**Current Issue:** FT-003 (Issue 3 of 14)
**Parallel Execution:** YES - This issue runs in parallel with FT-001 (Backend Setup) and FT-002 (Frontend Setup). All three are independent foundation pieces.

**What comes next:** After Wave 1 completes, Wave 2 begins with sequential authentication implementation (FT-004 Backend Auth, then FT-005 Frontend Auth).

## Request
Create the database schema file in Server/database/schema.sql with all tables needed for the finance tracker: users (with password_hash for custom auth), entities (family/startup), user_entities (many-to-many with roles), categories (hierarchical with parent_id), transactions, and budgets. Include appropriate indexes for performance.
```

---

## Wave 2: Authentication (Run Sequentially)

Authentication must be built after Wave 1 completes. Run these two in sequence.

### FT-004: Backend Authentication

**Title:** `[FinanceTracker] Wave 2: Backend Authentication`

**Body:**
```markdown
## Context
**Project:** Finance Tracker - Income & Expense Management
**Overview:** We are building a full-stack income/expense tracking application for family and startup company management. The system includes multi-entity support (family/startup separation), custom JWT authentication, transaction management, budgeting, reporting with charts, and CSV export. Frontend deploys to Vercel, backend to Render, database on Supabase PostgreSQL.

**Current Wave:** Wave 2 of 6 - Authentication
**Current Issue:** FT-004 (Issue 4 of 14)
**Parallel Execution:** NO - This issue must complete before FT-005 (Frontend Auth) can begin. Backend auth endpoints are required for frontend integration.

**Dependencies:** Requires Wave 1 completion (FT-001 Backend Setup, FT-003 Database Schema).
**What comes next:** After this issue, FT-005 (Frontend Authentication) implements the login UI and auth context.

## Request
Add user authentication to the backend with registration and login endpoints. Use bcrypt for password hashing and python-jose for JWT tokens. Create the auth service, user repository, and auth routes. Include JWT validation middleware and role-based access control dependencies. Users should have roles: admin, manager, user, viewer.
```

---

### FT-005: Frontend Authentication

**Title:** `[FinanceTracker] Wave 2: Frontend Authentication`

**Body:**
```markdown
## Context
**Project:** Finance Tracker - Income & Expense Management
**Overview:** We are building a full-stack income/expense tracking application for family and startup company management. The system includes multi-entity support (family/startup separation), custom JWT authentication, transaction management, budgeting, reporting with charts, and CSV export. Frontend deploys to Vercel, backend to Render, database on Supabase PostgreSQL.

**Current Wave:** Wave 2 of 6 - Authentication
**Current Issue:** FT-005 (Issue 5 of 14)
**Parallel Execution:** NO - This issue requires FT-004 (Backend Auth) to be complete first.

**Dependencies:** Requires FT-004 (Backend Authentication) for API endpoints.
**What comes next:** After Wave 2 completes, Wave 3 begins with 4 parallel features: Layout (FT-006), Entity Management (FT-007), Categories (FT-008), and Transactions (FT-009).

## Request
Add authentication to the frontend with AuthContext for managing JWT tokens and user state. Create a login page with email/password form using react-hook-form. Implement ProtectedRoute and RoleProtectedRoute components. Store JWT in localStorage and include it in all API requests via axios interceptor. Add logout functionality.
```

---

## Wave 3: Layout & Core Features (Run in Parallel)

After authentication is complete, these can all run in parallel.

### FT-006: Main Layout with Collapsible Sidebar

**Title:** `[FinanceTracker] Wave 3: Main Layout with Collapsible Sidebar`

**Body:**
```markdown
## Context
**Project:** Finance Tracker - Income & Expense Management
**Overview:** We are building a full-stack income/expense tracking application for family and startup company management. The system includes multi-entity support (family/startup separation), custom JWT authentication, transaction management, budgeting, reporting with charts, and CSV export. Frontend deploys to Vercel, backend to Render, database on Supabase PostgreSQL.

**Current Wave:** Wave 3 of 6 - Layout & Core Features
**Current Issue:** FT-006 (Issue 6 of 14)
**Parallel Execution:** YES - This issue runs in parallel with FT-007 (Entity Management), FT-008 (Categories), and FT-009 (Transactions). All four are independent features.

**Dependencies:** Requires Wave 2 completion (authentication must be in place).
**What comes next:** After Wave 3 completes, Wave 4 implements the Dashboard (FT-010).

## Request
Build the main application shell with a collapsible sidebar navigation and top navbar. The sidebar should show navigation links to Dashboard, Transactions, Categories, Budgets, Reports, and Settings. Include an entity switcher in the sidebar to switch between Family and Startup. The layout should be responsive and the sidebar should collapse to icons on smaller screens.
```

---

### FT-007: Entity Management

**Title:** `[FinanceTracker] Wave 3: Entity Management`

**Body:**
```markdown
## Context
**Project:** Finance Tracker - Income & Expense Management
**Overview:** We are building a full-stack income/expense tracking application for family and startup company management. The system includes multi-entity support (family/startup separation), custom JWT authentication, transaction management, budgeting, reporting with charts, and CSV export. Frontend deploys to Vercel, backend to Render, database on Supabase PostgreSQL.

**Current Wave:** Wave 3 of 6 - Layout & Core Features
**Current Issue:** FT-007 (Issue 7 of 14)
**Parallel Execution:** YES - This issue runs in parallel with FT-006 (Layout), FT-008 (Categories), and FT-009 (Transactions). All four are independent features.

**Dependencies:** Requires Wave 2 completion (authentication must be in place).
**What comes next:** After Wave 3 completes, Wave 4 implements the Dashboard (FT-010).

## Request
Implement entity management allowing users to create and switch between different entities like Family and Startup. Each entity has its own transactions, categories, and budgets. Add backend endpoints for entity CRUD and user-entity membership. Create EntityContext in frontend to track the current entity. All data queries should filter by the selected entity.
```

---

### FT-008: Category Management

**Title:** `[FinanceTracker] Wave 3: Category Management`

**Body:**
```markdown
## Context
**Project:** Finance Tracker - Income & Expense Management
**Overview:** We are building a full-stack income/expense tracking application for family and startup company management. The system includes multi-entity support (family/startup separation), custom JWT authentication, transaction management, budgeting, reporting with charts, and CSV export. Frontend deploys to Vercel, backend to Render, database on Supabase PostgreSQL.

**Current Wave:** Wave 3 of 6 - Layout & Core Features
**Current Issue:** FT-008 (Issue 8 of 14)
**Parallel Execution:** YES - This issue runs in parallel with FT-006 (Layout), FT-007 (Entity Management), and FT-009 (Transactions). All four are independent features.

**Dependencies:** Requires Wave 2 completion (authentication must be in place).
**What comes next:** After Wave 3 completes, Wave 4 implements the Dashboard (FT-010).

## Request
Implement income and expense categories with optional parent-child hierarchy. Users can create categories like "Food" with subcategories "Groceries" and "Restaurants". Add backend endpoints for category CRUD. Create a Categories page in frontend with a form to add/edit categories and a list view showing the category tree. Categories are entity-specific.
```

---

### FT-009: Transaction Management

**Title:** `[FinanceTracker] Wave 3: Transaction Management`

**Body:**
```markdown
## Context
**Project:** Finance Tracker - Income & Expense Management
**Overview:** We are building a full-stack income/expense tracking application for family and startup company management. The system includes multi-entity support (family/startup separation), custom JWT authentication, transaction management, budgeting, reporting with charts, and CSV export. Frontend deploys to Vercel, backend to Render, database on Supabase PostgreSQL.

**Current Wave:** Wave 3 of 6 - Layout & Core Features
**Current Issue:** FT-009 (Issue 9 of 14)
**Parallel Execution:** YES - This issue runs in parallel with FT-006 (Layout), FT-007 (Entity Management), and FT-008 (Categories). All four are independent features.

**Dependencies:** Requires Wave 2 completion (authentication must be in place).
**What comes next:** After Wave 3 completes, Wave 4 implements the Dashboard (FT-010).

## Request
Implement the core transaction functionality for recording income and expenses. Add backend endpoints for transaction CRUD with filtering by date range, category, and type. Create a Transactions page with a form to add transactions (amount, date, category, description, type) and a data table listing all transactions with sorting and filtering. Transactions belong to the current entity.
```

---

## Wave 4: Dashboard (Run After Wave 3)

The dashboard depends on transactions existing.

### FT-010: Dashboard with Summary Stats

**Title:** `[FinanceTracker] Wave 4: Dashboard with Summary Stats`

**Body:**
```markdown
## Context
**Project:** Finance Tracker - Income & Expense Management
**Overview:** We are building a full-stack income/expense tracking application for family and startup company management. The system includes multi-entity support (family/startup separation), custom JWT authentication, transaction management, budgeting, reporting with charts, and CSV export. Frontend deploys to Vercel, backend to Render, database on Supabase PostgreSQL.

**Current Wave:** Wave 4 of 6 - Dashboard
**Current Issue:** FT-010 (Issue 10 of 14)
**Parallel Execution:** NO - This issue runs alone as it integrates data from transactions and categories built in Wave 3.

**Dependencies:** Requires Wave 3 completion (transactions and categories must exist for dashboard data).
**What comes next:** After this issue, Wave 5 begins with 3 parallel advanced features: Budgets (FT-011), Reports (FT-012), and Recurring Transactions (FT-013).

## Request
Build a dashboard page showing financial summary for the current entity. Display stat cards for total income, total expenses, and net balance for the current month. Show a line chart of income vs expenses over the last 6 months. Include a pie chart breaking down expenses by category. Add quick action buttons to add new transaction.
```

---

## Wave 5: Advanced Features (Run in Parallel)

These can run in parallel after the dashboard is complete.

### FT-011: Budget Management

**Title:** `[FinanceTracker] Wave 5: Budget Management`

**Body:**
```markdown
## Context
**Project:** Finance Tracker - Income & Expense Management
**Overview:** We are building a full-stack income/expense tracking application for family and startup company management. The system includes multi-entity support (family/startup separation), custom JWT authentication, transaction management, budgeting, reporting with charts, and CSV export. Frontend deploys to Vercel, backend to Render, database on Supabase PostgreSQL.

**Current Wave:** Wave 5 of 6 - Advanced Features
**Current Issue:** FT-011 (Issue 11 of 14)
**Parallel Execution:** YES - This issue runs in parallel with FT-012 (Reports & Export) and FT-013 (Recurring Transactions). All three are independent advanced features.

**Dependencies:** Requires Wave 4 completion (core transaction flow must be working).
**What comes next:** After Wave 5 completes, Wave 6 finalizes deployment configuration (FT-014).

## Request
Implement budget management allowing users to set spending limits per category or overall. Add backend endpoints for budget CRUD. Create a Budgets page showing all budgets with progress bars comparing actual spending vs budget amount. Show visual indicators when approaching or exceeding budget limits. Budgets can be monthly, quarterly, or yearly.
```

---

### FT-012: Reports and Export

**Title:** `[FinanceTracker] Wave 5: Reports and Export`

**Body:**
```markdown
## Context
**Project:** Finance Tracker - Income & Expense Management
**Overview:** We are building a full-stack income/expense tracking application for family and startup company management. The system includes multi-entity support (family/startup separation), custom JWT authentication, transaction management, budgeting, reporting with charts, and CSV export. Frontend deploys to Vercel, backend to Render, database on Supabase PostgreSQL.

**Current Wave:** Wave 5 of 6 - Advanced Features
**Current Issue:** FT-012 (Issue 12 of 14)
**Parallel Execution:** YES - This issue runs in parallel with FT-011 (Budget Management) and FT-013 (Recurring Transactions). All three are independent advanced features.

**Dependencies:** Requires Wave 4 completion (core transaction flow must be working).
**What comes next:** After Wave 5 completes, Wave 6 finalizes deployment configuration (FT-014).

## Request
Create a Reports page with comprehensive financial analysis. Include date range picker to filter data. Show income vs expense comparison, category breakdown table, and trend charts. Add ability to export transaction data to CSV format. Include a summary report that can be filtered by entity or show consolidated view across all entities.
```

---

### FT-013: Recurring Transactions

**Title:** `[FinanceTracker] Wave 5: Recurring Transactions`

**Body:**
```markdown
## Context
**Project:** Finance Tracker - Income & Expense Management
**Overview:** We are building a full-stack income/expense tracking application for family and startup company management. The system includes multi-entity support (family/startup separation), custom JWT authentication, transaction management, budgeting, reporting with charts, and CSV export. Frontend deploys to Vercel, backend to Render, database on Supabase PostgreSQL.

**Current Wave:** Wave 5 of 6 - Advanced Features
**Current Issue:** FT-013 (Issue 13 of 14)
**Parallel Execution:** YES - This issue runs in parallel with FT-011 (Budget Management) and FT-012 (Reports & Export). All three are independent advanced features.

**Dependencies:** Requires Wave 4 completion (core transaction flow must be working).
**What comes next:** After Wave 5 completes, Wave 6 finalizes deployment configuration (FT-014).

## Request
Allow users to mark transactions as recurring with a pattern (daily, weekly, monthly, yearly). Create a way to view and manage recurring transaction templates. When viewing transactions, show which ones are from recurring templates. This helps track regular income like salary or regular expenses like subscriptions.
```

---

## Wave 6: Polish & Deploy (Run Sequentially at End)

### FT-014: Deployment Configuration

**Title:** `[FinanceTracker] Wave 6: Deployment Configuration`

**Body:**
```markdown
## Context
**Project:** Finance Tracker - Income & Expense Management
**Overview:** We are building a full-stack income/expense tracking application for family and startup company management. The system includes multi-entity support (family/startup separation), custom JWT authentication, transaction management, budgeting, reporting with charts, and CSV export. Frontend deploys to Vercel, backend to Render, database on Supabase PostgreSQL.

**Current Wave:** Wave 6 of 6 - Polish & Deploy
**Current Issue:** FT-014 (Issue 14 of 14)
**Parallel Execution:** NO - This is the final issue that prepares the application for production deployment.

**Dependencies:** Requires all previous waves to be complete.
**What comes next:** After this issue, the application is ready for production deployment!

## Request
Finalize deployment configuration. Ensure vercel.json is correct for the Client folder. Add any needed Render configuration for the Server folder. Create .env.sample files documenting all required environment variables. Update README with deployment instructions. Verify CORS is configured for production URLs.
```

---

## Execution Plan

```
Wave 1 (Parallel - 3 worktrees):
├── FT-001: Backend Setup
├── FT-002: Frontend Setup
└── FT-003: Database Schema

Wave 2 (Sequential):
├── FT-004: Backend Auth
└── FT-005: Frontend Auth

Wave 3 (Parallel - 4 worktrees):
├── FT-006: Layout & Sidebar
├── FT-007: Entity Management
├── FT-008: Category Management
└── FT-009: Transaction Management

Wave 4 (Sequential):
└── FT-010: Dashboard

Wave 5 (Parallel - 3 worktrees):
├── FT-011: Budgets
├── FT-012: Reports & Export
└── FT-013: Recurring Transactions

Wave 6 (Sequential):
└── FT-014: Deployment
```

## Commands to Run

```bash
cd adws/

# Wave 1 - Run all 3 in parallel
uv run adw_sdlc_iso.py 1 &
uv run adw_sdlc_iso.py 2 &
uv run adw_sdlc_iso.py 3 &
wait

# Wave 2 - Run sequentially
uv run adw_sdlc_iso.py 4
uv run adw_sdlc_iso.py 5

# Wave 3 - Run all 4 in parallel
uv run adw_sdlc_iso.py 6 &
uv run adw_sdlc_iso.py 7 &
uv run adw_sdlc_iso.py 8 &
uv run adw_sdlc_iso.py 9 &
wait

# Wave 4 - Sequential
uv run adw_sdlc_iso.py 10

# Wave 5 - Run all 3 in parallel
uv run adw_sdlc_iso.py 11 &
uv run adw_sdlc_iso.py 12 &
uv run adw_sdlc_iso.py 13 &
wait

# Wave 6 - Sequential
uv run adw_sdlc_iso.py 14
```

## Notes

- Each issue becomes a GitHub issue that triggers `/feature` planning
- The ADW system handles technical details, testing, review, and documentation
- Parallel execution uses separate git worktrees (max 15 concurrent)
- After each wave, merge PRs before starting next wave to avoid conflicts
- Total: 14 issues across 6 waves
