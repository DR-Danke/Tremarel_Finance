# Conditional Documentation Guide

This prompt helps you determine what documentation you should read based on the specific changes you need to make in the codebase. Review the conditions below and read the relevant documentation before proceeding with your task.

## Instructions
- Review the task you've been asked to perform
- Check each documentation path in the Conditional Documentation section
- For each path, evaluate if any of the listed conditions apply to your task
  - IMPORTANT: Only read the documentation if any one of the conditions match your task
- IMPORTANT: You don't want to excessively read documentation. Only read the documentation if it's relevant to your task.

## Conditional Documentation

- README.md
  - Conditions:
    - When operating on anything under Server
    - When operating on anything under Client
    - When first understanding the project structure
    - When you want to learn the commands to start or stop the Server or Client

- apps/Client/src/style.css
  - Conditions:
    - When you need to make changes to the Client's style

- .claude/commands/classify_adw.md
  - Conditions:
    - When adding or removing new `adws/adw_*.py` files

- adws/README.md
  - Conditions:
    - When you're operating in the `adws/` directory

- app_docs/feature-0f0d4c36-fastapi-backend-setup.md
  - Conditions:
    - When setting up or modifying the FastAPI Server project structure
    - When working with apps/Server/main.py or application entry point
    - When configuring CORS, environment variables, or settings
    - When adding new routers or API endpoints to the Server
    - When troubleshooting Server startup or configuration issues

- app_docs/feature-2a0579e1-frontend-react-vite-setup.md
  - Conditions:
    - When setting up or modifying the Client folder structure
    - When working with Vite configuration or path aliases
    - When configuring Material-UI theming for the application
    - When troubleshooting axios interceptor or JWT token handling
    - When deploying the Client to Vercel
    - When adding new React dependencies or updating package.json

- app_docs/feature-db5f36c7-database-schema-tables.md
  - Conditions:
    - When working with Finance Tracker database tables or schema
    - When implementing user authentication or JWT-based auth
    - When working with entities, categories, transactions, or budgets tables
    - When modifying apps/Server/database/schema.sql
    - When troubleshooting foreign key constraints or database relationships
    - When implementing multi-entity support (family/startup separation)

- app_docs/feature-ed4cef49-backend-jwt-auth-rbac.md
  - Conditions:
    - When working with backend authentication (login, registration, JWT)
    - When implementing or modifying protected routes
    - When working with role-based access control (RBAC)
    - When troubleshooting authentication or authorization errors
    - When adding new auth endpoints or modifying auth_routes.py
    - When working with the User model or user_repository

- app_docs/feature-f6f89b86-frontend-jwt-auth-context.md
  - Conditions:
    - When working with frontend authentication (login, logout, JWT tokens)
    - When implementing or modifying AuthContext or useAuth hook
    - When adding or modifying ProtectedRoute or RoleProtectedRoute components
    - When troubleshooting frontend authentication or session issues
    - When adding new pages that require authentication
    - When working with the LoginPage or authentication flow

- app_docs/feature-a201d4c8-main-layout-collapsible-sidebar.md
  - Conditions:
    - When working with the main application layout or navigation
    - When modifying or creating components in apps/Client/src/components/layout/
    - When implementing EntityContext or useEntity hook
    - When adding new navigation items to the sidebar
    - When working with entity switching functionality
    - When troubleshooting sidebar collapse/expand behavior
    - When adding new protected pages that need the main layout

- app_docs/feature-d6d0f56d-entity-management-crud.md
  - Conditions:
    - When working with entity management (create, update, delete entities)
    - When implementing or modifying EntityContext or useEntity hook
    - When adding entity switching functionality
    - When working with multi-entity support (family/startup separation)
    - When implementing features that need to filter by current entity
    - When troubleshooting entity-related access control or permissions
    - When working with TREntitySelector or EntitiesPage components

- app_docs/feature-a2d71086-category-management-crud.md
  - Conditions:
    - When working with categories (income/expense categories)
    - When implementing hierarchical/tree data structures
    - When working with CategoriesPage or category_routes
    - When modifying TRCategoryForm or TRCategoryTree components
    - When troubleshooting category creation, hierarchy, or deletion issues
    - When working with the categories table or CategoryService

- app_docs/feature-bda418fa-transaction-crud-management.md
  - Conditions:
    - When working with transactions (income/expense records)
    - When implementing or modifying transaction CRUD operations
    - When working with TransactionsPage, TRTransactionForm, or TRTransactionTable
    - When using the useTransactions hook or transactionService
    - When adding filters for date range, category, or transaction type
    - When troubleshooting transaction API endpoints

- app_docs/feature-7fcd6a6a-dashboard-summary-stats-charts.md
  - Conditions:
    - When working with DashboardPage or dashboard statistics
    - When implementing or modifying financial summary visualizations
    - When working with TRStatCard, TRMonthlyTrendChart, or TRExpenseBreakdownChart components
    - When using the useDashboard hook or dashboardService
    - When working with Recharts for financial data visualization
    - When troubleshooting dashboard API endpoint or aggregations

- app_docs/feature-901a8a52-budget-management-crud.md
  - Conditions:
    - When working with budgets (spending limits per category)
    - When implementing or modifying budget CRUD operations
    - When working with BudgetsPage, TRBudgetForm, or TRBudgetCard
    - When using the useBudgets hook or budgetService
    - When implementing progress bars or spending tracking visualizations
    - When troubleshooting budget API endpoints or spending calculations
    - When working with period types (monthly, quarterly, yearly)

- app_docs/feature-d110d3f0-reports-export-csv.md
  - Conditions:
    - When working with ReportsPage or financial reports
    - When implementing date range filtering for reports
    - When working with TRReportDateRangePicker, TRIncomeExpenseChart, or TRCategoryBreakdownTable components
    - When using the useReports hook or reportService
    - When implementing CSV export functionality
    - When troubleshooting reports API endpoints or data aggregations

- app_docs/feature-e44986c8-recurring-transactions.md
  - Conditions:
    - When working with recurring transactions or recurring templates
    - When implementing or modifying RecurringTemplatesPage
    - When working with TRRecurringTemplateForm or TRRecurringTemplateTable components
    - When using the useRecurringTemplates hook or recurringTemplateService
    - When working with the recurring_templates table or recurring_template_routes
    - When linking transactions to recurring templates via recurring_template_id
    - When troubleshooting recurring transaction template CRUD operations
