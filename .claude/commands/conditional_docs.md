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

- app_docs/feature-75704e1f-section-based-sidebar-navigation.md
  - Conditions:
    - When adding new navigation sections or subsections to the sidebar
    - When adding a new POC module to the sidebar navigation
    - When working with sidebar section collapse/expand state or localStorage persistence
    - When modifying the NavSection interface or navigationSections data structure
    - When adding routes under /poc/ path prefix
    - When troubleshooting section-based sidebar rendering or collapsed mode behavior

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

- app_docs/chore-dcb3fc76-deployment-config.md
  - Conditions:
    - When deploying the application to production (Vercel, Render, Supabase)
    - When configuring environment variables for production
    - When setting up or modifying render.yaml or Vercel configuration
    - When troubleshooting CORS configuration or deployment issues
    - When updating .env.sample files

- app_docs/bug-dd6d412a-cors-error-category-creation.md
  - Conditions:
    - When troubleshooting CORS errors on API endpoints
    - When modifying FastAPI exception handling in main.py
    - When debugging error responses missing CORS headers
    - When working with global exception handlers in FastAPI

- app_docs/bug-74b0e4f8-network-error-category-creation.md
  - Conditions:
    - When troubleshooting network connectivity errors in the frontend
    - When improving error handling for API client requests
    - When working with form submission error handling
    - When users report "Network Error" or "ERR_CONNECTION_REFUSED" issues
    - When enhancing user feedback for backend unavailability

- app_docs/bug-NA-wsl2-backend-binding-entity-context.md
  - Conditions:
    - When troubleshooting "Cannot connect to server" errors in WSL2 environments
    - When the backend is running but frontend cannot reach it
    - When working with uvicorn host binding configuration
    - When a page uses hardcoded entity IDs instead of EntityContext
    - When adding new entity-specific pages that need current entity
    - When troubleshooting foreign key violations related to entity_id
    - When configuring the /start command or backend startup scripts
    - When users report connection issues only in WSL2/Windows development

- app_docs/bug-0cbd0859-recurring-templates-cors-error.md
  - Conditions:
    - When troubleshooting CORS errors with Pydantic validation
    - When adding RequestValidationError or ValidationError exception handlers
    - When working with recurring templates API endpoints
    - When serializing complex types (UUID, Decimal, datetime) in error responses
    - When debugging 500 errors that bypass CORS middleware
    - When adding null entityId guards to frontend hooks

- app_docs/feature-57f962c3-prospect-data-model.md
  - Conditions:
    - When working with the CRM pipeline or prospect features
    - When implementing prospect CRUD API endpoints or services
    - When working with the prospects table or Prospect model
    - When adding meeting records or other prospect-related entities
    - When implementing pipeline stage filtering or prospect management UI

- app_docs/feature-eb19b5cd-pipeline-stage-configuration.md
  - Conditions:
    - When working with CRM pipeline stages or Kanban board columns
    - When implementing or modifying stage transition tracking or audit trails
    - When working with pipeline_stages or stage_transitions tables
    - When seeding default pipeline stages for an entity
    - When adding prospect stage change functionality (PATCH endpoint)
    - When building CRM pipeline UI that displays configurable stages

- app_docs/feature-17ff3ddf-meeting-record-data-model.md
  - Conditions:
    - When working with meeting records or meeting tracking features
    - When implementing meeting record CRUD API endpoints or services
    - When working with the meeting_records table or MeetingRecord model
    - When linking meeting data to prospects in the CRM pipeline
    - When working with transcript processing or meeting summaries
    - When implementing action items or participant tracking for meetings

- app_docs/feature-d1b26544-meeting-record-api-endpoints.md
  - Conditions:
    - When working with meeting record REST API endpoints or routes
    - When implementing or modifying meeting_record_routes, meeting_record_service, or meeting_record_repository
    - When adding HTML download endpoints or text/html response types
    - When troubleshooting meeting record CRUD operations or entity-scoping validation
    - When building frontend UI that consumes meeting record API endpoints

- app_docs/feature-70362135-prospect-crud-api-endpoints.md
  - Conditions:
    - When working with prospect CRUD API endpoints or prospect management
    - When implementing prospect listing, filtering, or pagination
    - When working with prospect stage updates or pipeline stage transitions
    - When building the CRM prospect management frontend (Wave 2)
    - When implementing pipeline automation that creates or updates prospects (Wave 3)
    - When troubleshooting prospect API routes, service, or repository

- app_docs/feature-aa2af2a8-prospect-service-hook-types.md
  - Conditions:
    - When working with frontend prospect or meeting record services, hooks, or types
    - When building CRM UI components that consume prospect or meeting record data
    - When implementing the Kanban board, detail view, or drag-and-drop for prospects
    - When modifying useProspects or useMeetingRecords hooks
    - When troubleshooting prospect or meeting record API calls from the frontend
    - When adding new prospect pipeline stage transitions in the UI

- app_docs/feature-ab11c9f9-prospect-creation-form.md
  - Conditions:
    - When working with TRProspectForm or prospect creation/editing UI
    - When implementing or modifying the useProspects hook or prospectService
    - When integrating the prospect form into a dialog or page (e.g., Kanban Board)
    - When working with CRM prospect TypeScript types (Prospect, ProspectCreate, ProspectStage)
    - When troubleshooting prospect form validation, submission, or API integration

- app_docs/feature-6835fdde-prospect-kanban-board.md
  - Conditions:
    - When working with the Prospect Kanban board UI or ProspectsPage
    - When implementing or modifying TRKanbanBoard, TRKanbanColumn, or TRProspectCard components
    - When working with TRProspectForm or prospect create/edit dialogs
    - When using the useProspects or usePipelineStages hooks
    - When working with prospectService or pipelineStageService on the frontend
    - When adding drag-and-drop or other Kanban board enhancements
    - When troubleshooting prospect display, grouping by stage, or pipeline stage auto-seeding

- app_docs/feature-66325370-prospect-card-drag-and-drop.md
  - Conditions:
    - When working with drag-and-drop on the Kanban board or @hello-pangea/dnd integration
    - When implementing optimistic UI updates for prospect stage changes
    - When modifying TRKanbanBoard, TRKanbanColumn, or TRProspectCard drag props
    - When troubleshooting drag-and-drop behavior or rollback logic on the Prospects page
    - When working with the setProspects setter from useProspects hook

- app_docs/feature-17480a03-prospect-detail-meeting-history.md
  - Conditions:
    - When working with the prospect detail drawer or TRProspectDetailDrawer component
    - When implementing or modifying stage transition history display
    - When working with meeting history display or HTML download functionality
    - When modifying the prospect card click behavior on the Kanban board
    - When working with pipelineStageService.getTransitions or StageTransition types
    - When troubleshooting the detail drawer opening, closing, or edit-from-drawer flow

- app_docs/feature-9d184498-meeting-transcript-watcher.md
  - Conditions:
    - When working with the meeting transcript folder watcher or trigger_meeting_transcript_watch.py
    - When implementing or modifying ADW triggers that monitor folders for new files
    - When working with the meeting processing pipeline (adw_meeting_pipeline_iso.py)
    - When troubleshooting meeting transcript detection, processing, or pipeline triggering
    - When working with files in External_Requirements/meeting_transcripts/

- app_docs/feature-e924e4a7-meeting-transcript-summary-processor.md
  - Conditions:
    - When working with adw_meeting_pipeline_iso.py or the meeting transcript processing pipeline
    - When implementing or modifying the /process_meeting_transcript slash command
    - When working with meeting summary JSON/HTML output generation
    - When troubleshooting LLM-based meeting transcript parsing or structured data extraction
    - When extending the meeting processing pipeline (REQ-013 CRM updates, REQ-014 issue generation)

- app_docs/feature-a61cf509-crm-update-from-processed-transcript.md
  - Conditions:
    - When working with CRM updates triggered by transcript processing
    - When modifying the update_crm function or CrmApiClient module
    - When configuring service account credentials for pipeline-to-API communication
    - When troubleshooting automatic prospect creation or meeting record linking
    - When extending the meeting pipeline with additional CRM integration steps

- app_docs/feature-342ed7df-github-issue-generation-pipeline.md
  - Conditions:
    - When working with GitHub issue generation from the meeting pipeline
    - When modifying generate_github_issue, create_issue, or check_gh_authenticated functions
    - When working with adw_modules/github.py issue creation or label management
    - When troubleshooting automatic issue creation after transcript processing
    - When extending the meeting pipeline with additional post-processing steps
    - When working with ADW_METADATA blocks in GitHub issues

- app_docs/feature-a692d2db-restaurant-multi-tenant-entity.md
  - Conditions:
    - When working with the restaurant table or RestaurantOS multi-tenant scoping
    - When implementing RestaurantOS entities that reference restaurant_id
    - When working with restaurant CRUD API endpoints, service, or repository
    - When working with user_restaurants junction table or per-restaurant roles
    - When adding new features to the RestaurantOS module

- app_docs/feature-14633eae-person-entity-crud-backend.md
  - Conditions:
    - When working with the person table or Person model in RestaurantOS
    - When implementing RestaurantOS entities that reference person_id (Documents, Events, Inventory Movements)
    - When working with person CRUD API endpoints, service, or repository
    - When adding employee, supplier, or owner management features
    - When working with restaurant-scoped person authorization or PersonType enum

- app_docs/feature-8d28116a-resource-entity-crud-backend.md
  - Conditions:
    - When working with the resource table or Resource model in RestaurantOS
    - When implementing RestaurantOS entities that reference resource_id (Inventory Movements, Recipes)
    - When working with resource CRUD API endpoints, service, or repository
    - When implementing stock tracking, low-stock detection, or inventory features
    - When working with ResourceType enum (producto, activo, servicio)
    - When working with restaurant-scoped resource authorization

- app_docs/feature-95deee5d-document-entity-crud-backend.md
  - Conditions:
    - When working with the document table or Document model in RestaurantOS
    - When implementing RestaurantOS entities that reference document_id (Contracts, Permits, Payments)
    - When working with document CRUD API endpoints, service, or repository
    - When implementing file upload via multipart/form-data for documents
    - When working with expiration tracking, expiration_status computation, or expiring document alerts
    - When working with person-document linking (person_id FK with ON DELETE SET NULL)
    - When working with restaurant-scoped document authorization

- app_docs/feature-dc999a0b-event-entity-crud-backend.md
  - Conditions:
    - When working with the event table or Event model in RestaurantOS
    - When implementing recurring events, tasks, deadlines, or scheduled alerts
    - When working with event CRUD API endpoints, service, or repository
    - When implementing automation flows that create events (stock alerts, expiry alerts, profitability alerts)
    - When working with event types (tarea, vencimiento, pago, turno, checklist, alerta_stock, alerta_rentabilidad)
    - When working with recurring instance generation or parent-child event relationships
    - When working with restaurant-scoped event authorization or notification channels

- app_docs/feature-02529be1-inventory-movement-tracking.md
  - Conditions:
    - When working with the inventory_movement table or InventoryMovement model in RestaurantOS
    - When implementing stock entry/exit tracking or movement history
    - When working with inventory movement API endpoints, service, or repository
    - When implementing automatic current_stock updates on resources
    - When working with negative stock prevention or low-stock warning logic
    - When building inventory management frontend (Wave 4)
    - When working with MovementType or MovementReason enums

- app_docs/feature-07ac42cd-task-assignment-recurrence.md
  - Conditions:
    - When working with task creation, assignment, or recurrence in RestaurantOS
    - When implementing task-specific endpoints or business rules for events with type=tarea
    - When working with overdue detection or bulk overdue flagging
    - When implementing status transition validation (pending/completed/overdue)
    - When working with the completed_at timestamp or task completion tracking
    - When building the task management frontend (ROS-012)
    - When implementing the daily task summary service (ROS-009)

- app_docs/feature-342b3948-restaurant-selector-multitenant-navigation.md
  - Conditions:
    - When working with the RestaurantContext, useRestaurant hook, or RestaurantProvider
    - When adding or modifying RestaurantOS frontend pages under /poc/restaurant-os/
    - When working with the TRRestaurantSelector component or restaurant switching
    - When implementing RestaurantOS frontend features that need to scope data by current restaurant
    - When adding new navigation items to the RestaurantOS sidebar subsection
    - When troubleshooting restaurant selection persistence or empty-state handling

- app_docs/feature-206ba84f-daily-employee-task-summary.md
  - Conditions:
    - When working with daily task summaries or employee task aggregation
    - When implementing the notification system that sends daily task lists (Wave 5)
    - When working with /api/events/tasks/daily-summary endpoints
    - When building batch summary features across restaurant employees
    - When implementing the daily task summary service (ROS-009)

- app_docs/feature-de82eb81-person-management-page.md
  - Conditions:
    - When working with the RestaurantOS person management frontend page
    - When modifying RestaurantOSPersonsPage, TRPersonForm, usePersons, or personService
    - When adding employee, supplier, or owner management UI features
    - When implementing frontend CRUD pages that follow the person management pattern
    - When troubleshooting person list, search, type filter, or dialog-based form issues

- app_docs/feature-26972c6e-document-management-page.md
  - Conditions:
    - When working with the RestaurantOS document management frontend page
    - When modifying RestaurantOSDocumentsPage, TRDocumentForm, useDocuments, or documentService
    - When working with TRExpirationBadge or expiration status display
    - When implementing file upload with drag-and-drop or multipart/form-data submissions
    - When implementing frontend CRUD pages that follow the document management pattern
    - When troubleshooting document filters, file upload, or expiration badge issues

- app_docs/feature-9297a9a2-event-task-management-page.md
  - Conditions:
    - When working with the RestaurantOS event/task management frontend page
    - When modifying RestaurantOSEventsPage, TREventForm, TREventStatusBadge, useEvents, or eventService
    - When implementing quick-complete actions or event status transitions in the UI
    - When working with date-grouped tables or overdue event highlighting
    - When implementing frontend CRUD pages that follow the event management pattern
    - When troubleshooting event filters, conditional form validation, or status badge display

- app_docs/feature-958fff68-resource-inventory-page.md
  - Conditions:
    - When working with the RestaurantOS resource & inventory management frontend page
    - When modifying RestaurantOSResourcesPage, TRResourceForm, TRInventoryMovementForm, useResources, useInventoryMovements, resourceService, or inventoryMovementService
    - When implementing stock level indicators, low-stock warnings, or inventory movement tracking in the UI
    - When working with Resource or InventoryMovement TypeScript types and Spanish label constants
    - When implementing frontend CRUD pages that follow the resource management pattern
    - When troubleshooting resource filters, movement registration, or detail drawer issues

- app_docs/feature-879ccc05-whatsapp-notification-integration.md
  - Conditions:
    - When working with WhatsApp notifications or the notification system
    - When implementing or modifying NotificationService, NotificationAdapter, or WhatsAppAdapter
    - When working with the notification_log table or NotificationLogRepository
    - When working with notification REST routes or /api/notifications endpoints
    - When implementing message formatters for daily tasks, low stock, or document expiry alerts
    - When integrating a real WhatsApp provider (Twilio, Meta Cloud API)
    - When building the Event Notification Dispatcher (Wave 8)
    - When troubleshooting notification sending, retry logic, or audit logging

- app_docs/feature-c53dc15a-email-notification-integration.md
  - Conditions:
    - When working with email notifications or the EmailAdapter
    - When configuring SMTP settings for email delivery
    - When implementing or modifying HTML email templates for notifications
    - When working with notification channel routing (email, WhatsApp, or both)
    - When extending the notification system with new channels
    - When troubleshooting email sending, stub mode, or email validation

- app_docs/feature-3ad42112-recipe-data-model-crud.md
  - Conditions:
    - When working with the recipe table or Recipe/RecipeItem models in RestaurantOS
    - When implementing RestaurantOS entities that reference recipe_id
    - When working with recipe CRUD API endpoints, service, or repository
    - When implementing cost calculation, margin computation, or profitability tracking
    - When working with ingredient-to-recipe linking or RecipeItem management
    - When building the recipe management frontend (Wave 6)
    - When implementing automatic cost recalculation from resource price changes

- app_docs/feature-327dae14-document-expiration-alert-automation.md
  - Conditions:
    - When working with document expiration alerts or vencimiento events
    - When implementing or modifying automated event creation from document lifecycle
    - When working with the notification processing endpoint for expiration alerts
    - When modifying DEFAULT_ALERT_WINDOWS or alert scheduling logic in DocumentService
    - When troubleshooting automatic vencimiento event creation on document create/update/delete
    - When extending the notification scheduler with new alert processing functions

- app_docs/feature-e879dca2-invoice-ocr-automatic-cost-update.md
  - Conditions:
    - When working with invoice OCR processing or supplier invoice automation
    - When implementing or modifying OCRAdapter, OCRService, or InvoiceProcessor
    - When working with document processing_status or processing_result fields
    - When implementing a real OCR provider (Google Cloud Vision, AWS Textract, OpenAI Vision)
    - When working with automatic resource cost updates from invoices
    - When troubleshooting invoice processing endpoints or resource matching logic
    - When extending the invoice pipeline with recipe cost recalculation

- app_docs/feature-4801f61f-recipe-inventory-deduction.md
  - Conditions:
    - When working with recipe production or recipe-based inventory deduction
    - When implementing the POST /api/recipes/{recipe_id}/produce endpoint
    - When working with atomic stock pre-checks before inventory movements
    - When creating exit movements with reason=receta from recipe items
    - When troubleshooting insufficient stock errors during recipe production

- app_docs/feature-c332e58b-auto-recipe-cost-recalculation.md
  - Conditions:
    - When working with automatic recipe cost recalculation from resource price changes
    - When modifying ResourceService.update_resource() or cost-change detection logic
    - When working with RecipeService.recalculate_by_resource() or profitability alerts
    - When implementing or modifying alerta_rentabilidad event creation
    - When working with the PROFITABILITY_THRESHOLD configuration
    - When troubleshooting recipe cost propagation from resource updates
    - When extending the cost intelligence loop (Invoice -> OCR -> Cost -> Recipe -> Alert)

- app_docs/feature-367a82ca-permit-type-presets-alert-schedules.md
  - Conditions:
    - When working with permit type presets or pre-configured alert schedules
    - When modifying PERMIT_PRESETS configuration or adding new permit types
    - When working with custom_alert_windows on document creation
    - When modifying alert window resolution logic in DocumentService.create_expiration_alerts()
    - When working with preset-aware event descriptions or notification channel selection
    - When troubleshooting permit preset API endpoint or preset-based alert creation

- app_docs/feature-8035b22e-low-stock-alert-automation.md
  - Conditions:
    - When working with low-stock alerts or alerta_stock events
    - When modifying InventoryService.create_movement() or stock-triggered automation
    - When working with related_resource_id on the Event model or DTOs
    - When implementing or troubleshooting duplicate alert prevention for resources
    - When working with auto-resolution of stock alerts on inventory entry movements
    - When extending the inventory-to-event automation pipeline

- app_docs/feature-c57bcb02-event-notification-dispatcher.md
  - Conditions:
    - When working with the general event notification dispatcher or event-driven notifications
    - When implementing or modifying EventNotificationDispatcher or process_due_events
    - When working with the dispatch, pending, or dispatch-all notification API endpoints
    - When adding new event types that need automatic notification delivery
    - When working with notification channel routing for events (WhatsApp, Email)
    - When implementing scheduled or cron-based notification dispatch
    - When troubleshooting event-to-notification flow or event status updates after dispatch

- app_docs/feature-877c0251-push-notification-channel.md
  - Conditions:
    - When working with push notifications or the PushNotificationAdapter
    - When configuring FCM_SERVER_KEY or Firebase Cloud Messaging integration
    - When working with the push_token field on the Person model or DTOs
    - When extending the notification system with new channels
    - When working with the firebase-messaging-sw.js service worker
    - When modifying notification channel routing to include push
    - When troubleshooting push notification sending, stub mode, or FCM API calls

- app_docs/feature-28ba0bbb-restaurant-ops-dashboard.md
  - Conditions:
    - When working with the RestaurantOS operations dashboard or RestaurantOSDashboardPage
    - When modifying TRStatCard (generic mode), TRAlertsList, or useDashboardOverview
    - When working with the restaurant_dashboard_routes or RestaurantDashboardService
    - When implementing dashboard-style aggregation pages that pull from multiple entity services
    - When working with expiring document queries, low-stock queries, or daily task summaries
    - When troubleshooting the dashboard overview endpoint or dashboard data loading

- app_docs/feature-de0cefbe-legaldesk-database-schema.md
  - Conditions:
    - When working with Legal Desk database tables or the ld_ schema prefix
    - When implementing Legal Desk repositories, services, or API endpoints
    - When working with apps/Server/database/create_legaldesk_tables.sql
    - When working with cases, specialists, clients, or deliverables in the Legal Desk module
    - When troubleshooting Legal Desk foreign key constraints or table relationships
    - When implementing Wave 2+ of the Legal Desk module

- app_docs/feature-7950ad87-legaldesk-seed-data.md
  - Conditions:
    - When working with Legal Desk seed data or test data setup
    - When running or modifying apps/Server/database/seed_legaldesk_data.sql
    - When setting up a development database for the Legal Desk module
    - When testing the specialist assignment engine with sample data
    - When adding new seed data records to Legal Desk tables

- app_docs/feature-40f52fef-legaldesk-sqlalchemy-orm-models.md
  - Conditions:
    - When working with Legal Desk SQLAlchemy ORM models (LdClient, LdSpecialist, LdCase, etc.)
    - When implementing Legal Desk repositories that query ld_ tables
    - When navigating Legal Desk model relationships or backrefs
    - When adding new Legal Desk models or modifying existing ld_ model columns
    - When troubleshooting Legal Desk model imports, JSONB columns, or unique constraints

- app_docs/feature-cbc09752-legaldesk-pydantic-dtos-enums.md
  - Conditions:
    - When working with Legal Desk Pydantic DTOs, enums, or data validation
    - When implementing Legal Desk API endpoints that accept or return case, specialist, client, or deliverable data
    - When working with apps/Server/src/interface/legaldesk_dto.py
    - When implementing Legal Desk services or repositories that need input/output models
    - When working with case status transitions or workflow validation
    - When building the assignment engine, AI classification, or analytics dashboard DTOs

- app_docs/feature-e9ee37e2-legaldesk-frontend-typescript-types.md
  - Conditions:
    - When working with Legal Desk frontend TypeScript types, interfaces, or union types
    - When building Legal Desk UI components, services, or hooks that consume Ld-prefixed types
    - When using Legal Desk label or color constant maps for status badges, priority chips, or domain labels
    - When implementing Legal Desk CRUD forms or API payloads (LdCaseCreate, LdClientUpdate, etc.)
    - When adding new Legal Desk types or extending existing Legal Desk interfaces

- app_docs/feature-444abca2-legaldesk-core-repositories.md
  - Conditions:
    - When working with Legal Desk repository classes (LdCaseRepository, LdSpecialistRepository, LdClientRepository)
    - When implementing Legal Desk services that consume case, specialist, or client data access methods
    - When working with case number generation, specialist availability filtering, or client name search
    - When building Legal Desk API endpoints that need repository method signatures or usage patterns
    - When troubleshooting Legal Desk data access queries or repository singleton imports

- app_docs/feature-7febcc45-legaldesk-all-pages.md
  - Conditions:
    - When working with Legal Desk frontend pages (Dashboard, Cases, Specialists, Clients, Analytics)
    - When modifying LegalDeskDashboardPage, LegalDeskCasesPage, LegalDeskCaseDetailPage, or other Legal Desk page components
    - When working with TRCaseStatusBadge, TRLegalDomainBadge, TRCasePriorityBadge, TRDeliverableChecklist, or TRPricingTimeline components
    - When working with TRLegalCaseForm, TRLegalSpecialistForm, or TRLegalClientForm
    - When implementing Legal Desk routing or sidebar navigation (LD-016)
    - When troubleshooting Legal Desk page rendering, tab switching, or status transitions

- app_docs/feature-601d0350-legaldesk-supporting-repositories-wave2.md
  - Conditions:
    - When working with Legal Desk assignment, deliverable, message, or analytics repositories
    - When implementing Legal Desk services that consume Wave 2 repository methods
    - When working with case-specialist assignment fee negotiation or status tracking
    - When working with deliverable milestone tracking or status transitions
    - When working with case message threads or internal/external message filtering
    - When building the Legal Desk analytics dashboard or aggregation queries
    - When troubleshooting Legal Desk repository imports or singleton instances

- app_docs/feature-e846c4b4-legaldesk-ui-components-forms.md
  - Conditions:
    - When working with Legal Desk UI badge components (TRCaseStatusBadge, TRCasePriorityBadge, TRLegalDomainBadge)
    - When working with TRSpecialistScoreDisplay, TRPricingTimeline, or TRDeliverableChecklist
    - When building Legal Desk forms (TRLegalCaseForm, TRLegalClientForm, TRLegalSpecialistForm)
    - When implementing Legal Desk pages that consume these UI components or forms
    - When working with dynamic form arrays (expertise, jurisdictions) in the specialist form
    - When troubleshooting Legal Desk component rendering, form validation, or create/edit mode behavior
