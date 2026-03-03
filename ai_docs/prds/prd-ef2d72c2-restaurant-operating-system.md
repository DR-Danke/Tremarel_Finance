# PRD: Restaurant Operating System for Small Restaurants

## Meeting Metadata
- **Date**: Not specified
- **Participants**: Not specified (product owner / stakeholder presenting project vision)
- **Duration**: Not specified
- **Context**: A product vision and architecture document describing a centralized operational management platform for small restaurants — covering people, documents, tasks, inventory, events, recipes, and cost intelligence. The document outlines an MVP (Phase 1), a recipe/cost extension (Phase 2), and an AI-driven intelligence layer (Phase 3).

## Executive Summary
The stakeholder proposes a centralized "restaurant operating system" that replaces the current disorganized workflow of WhatsApp, notebooks, and disconnected tools used by small restaurants. The platform is built on four universal entities (Person, Document, Event, Resource) and an event-driven architecture where all business functions (contracts, permits, checklists, inventory, payments, payroll) are composed from these entities plus business rules and views. Phase 1 delivers employee management, task assignment with WhatsApp notifications, document tracking with expiration alerts, and basic inventory. Phase 2 adds recipe management, automated cost calculation from scanned invoices (OCR), profitability alerts, and digital contracts. Phase 3 introduces AI-powered predictions and analysis.

## Work Streams

### Stream 1: Core Data Model & Universal Entities
Build the foundational database schema and backend CRUD for the four universal entities (Person, Document, Event, Resource) and the Inventory_Movement table. This is the backbone upon which all features are composed.

#### Requirements

##### REQ-001: Person Entity Data Model & CRUD
- **Type**: feature
- **Priority**: P0
- **Description**: Create the `person` database table and full backend CRUD (model, repository, service, REST routes). A Person represents employees, suppliers, or owners within a restaurant. Fields: id, nombre (name), rol (role — e.g., chef, mesero, dueño, proveedor), email, whatsapp, tipo (type — employee, supplier, owner). Persons are scoped to a restaurant (restaurant_id foreign key).
- **Affected Modules**: `apps/Server/src/models/`, `apps/Server/src/repository/`, `apps/Server/src/core/services/`, `apps/Server/src/adapter/rest/`, `apps/Server/src/interface/`, `apps/Server/database/`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] `person` table exists in PostgreSQL with columns: id, restaurant_id, name, role, email, whatsapp, type, created_at, updated_at
  - [ ] SQLAlchemy model `PersonModel` is defined
  - [ ] Pydantic DTOs for create, update, list, and response are defined
  - [ ] `GET /api/persons?restaurant_id={id}` returns filtered list
  - [ ] `POST /api/persons` creates a new person
  - [ ] `GET /api/persons/{id}` returns person detail
  - [ ] `PUT /api/persons/{id}` updates person
  - [ ] `DELETE /api/persons/{id}` deletes a person
  - [ ] All endpoints require JWT authentication

##### REQ-002: Document Entity Data Model & CRUD
- **Type**: feature
- **Priority**: P0
- **Description**: Create the `document` table and full backend CRUD. A Document represents any legal or administrative artifact: contracts, permits, invoices, licenses, etc. Fields: id, tipo (type — contrato, permiso, factura, licencia, etc.), archivo (file URL/path), fecha_emision (issue date), fecha_vencimiento (expiration date), persona_id (optional FK to person), restaurant_id. File upload support is required.
- **Affected Modules**: `apps/Server/src/models/`, `apps/Server/src/repository/`, `apps/Server/src/core/services/`, `apps/Server/src/adapter/rest/`, `apps/Server/src/interface/`, `apps/Server/database/`
- **Dependencies**: REQ-001
- **Acceptance Criteria**:
  - [ ] `document` table exists with columns: id, restaurant_id, type, file_url, issue_date, expiration_date, person_id (nullable FK), created_at, updated_at
  - [ ] File upload endpoint accepts document files and stores them (Supabase Storage or similar)
  - [ ] `GET /api/documents?restaurant_id={id}` returns filtered list with optional type filter
  - [ ] `POST /api/documents` creates a document with file upload
  - [ ] `GET /api/documents/{id}` returns document detail
  - [ ] `PUT /api/documents/{id}` updates document metadata
  - [ ] `DELETE /api/documents/{id}` deletes document
  - [ ] Creating a document with an expiration date automatically creates an associated Event (see REQ-003)

##### REQ-003: Event Entity Data Model & CRUD
- **Type**: feature
- **Priority**: P0
- **Description**: Create the `event` table and full backend CRUD. Event is the system's nervous system — it represents tasks, deadlines, payments, shifts, checklists, and alerts. Fields: id, tipo (type — tarea, vencimiento, pago, turno, checklist, alerta_rentabilidad), fecha (date/datetime), frecuencia (frequency — none, daily, weekly, monthly, yearly), responsable_id (FK to person), canal_notificacion (notification channel — email, push, whatsapp), estado (status — pending, completed, overdue), restaurant_id. Recurring events with a frequency should auto-generate individual event instances.
- **Affected Modules**: `apps/Server/src/models/`, `apps/Server/src/repository/`, `apps/Server/src/core/services/`, `apps/Server/src/adapter/rest/`, `apps/Server/src/interface/`, `apps/Server/database/`
- **Dependencies**: REQ-001
- **Acceptance Criteria**:
  - [ ] `event` table exists with columns: id, restaurant_id, type, date, frequency, responsible_id (FK to person), notification_channel, status, description, related_document_id (nullable FK), created_at, updated_at
  - [ ] Recurring events (frequency != none) generate individual instances for the upcoming period
  - [ ] `GET /api/events?restaurant_id={id}` returns filtered list with optional date range and type filters
  - [ ] `POST /api/events` creates an event
  - [ ] `GET /api/events/{id}` returns event detail
  - [ ] `PUT /api/events/{id}` updates event
  - [ ] `PATCH /api/events/{id}/status` updates event status (pending → completed)
  - [ ] `DELETE /api/events/{id}` deletes event

##### REQ-004: Resource Entity Data Model & CRUD
- **Type**: feature
- **Priority**: P0
- **Description**: Create the `resource` table and full backend CRUD. A Resource represents any physical item: products (ingredients), assets (equipment), or services. Fields: id, tipo (type — producto, activo, servicio), nombre (name), unidad (unit — kg, litros, unidades), stock_actual (current stock), stock_minimo (minimum stock threshold), ultimo_costo_unitario (last unit cost), restaurant_id.
- **Affected Modules**: `apps/Server/src/models/`, `apps/Server/src/repository/`, `apps/Server/src/core/services/`, `apps/Server/src/adapter/rest/`, `apps/Server/src/interface/`, `apps/Server/database/`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] `resource` table exists with columns: id, restaurant_id, type, name, unit, current_stock, minimum_stock, last_unit_cost, created_at, updated_at
  - [ ] `GET /api/resources?restaurant_id={id}` returns filtered list with optional type filter
  - [ ] `POST /api/resources` creates a resource
  - [ ] `GET /api/resources/{id}` returns resource detail
  - [ ] `PUT /api/resources/{id}` updates resource
  - [ ] `DELETE /api/resources/{id}` deletes resource
  - [ ] Low-stock alert: when stock_actual < stock_minimo, an Event of type "alerta_stock" is automatically created

##### REQ-005: Inventory Movement Tracking
- **Type**: feature
- **Priority**: P0
- **Description**: Create the `inventory_movement` table and API for tracking all stock changes. Each movement records: resource_id (FK), tipo (entry/exit), cantidad (quantity), motivo (reason — compra, uso, producción, merma, receta), fecha (date), persona_id (FK to person who performed it). Every movement updates the resource's current_stock accordingly.
- **Affected Modules**: `apps/Server/src/models/`, `apps/Server/src/repository/`, `apps/Server/src/core/services/`, `apps/Server/src/adapter/rest/`, `apps/Server/src/interface/`, `apps/Server/database/`
- **Dependencies**: REQ-004, REQ-001
- **Acceptance Criteria**:
  - [ ] `inventory_movement` table exists with columns: id, resource_id (FK), type (entry/exit), quantity, reason, date, person_id (FK), restaurant_id, created_at
  - [ ] `POST /api/inventory-movements` creates a movement and updates the corresponding resource's current_stock (increment for entry, decrement for exit)
  - [ ] `GET /api/inventory-movements?resource_id={id}` returns movement history for a resource
  - [ ] `GET /api/inventory-movements?restaurant_id={id}` returns all movements with optional date range and reason filters
  - [ ] Negative stock is prevented (exit quantity cannot exceed current_stock)

##### REQ-006: Restaurant (Multi-Tenant) Entity
- **Type**: feature
- **Priority**: P0
- **Description**: Create the `restaurant` table that serves as the multi-tenant scope for all data. A restaurant represents a single location/business. All other entities (Person, Document, Event, Resource) are scoped to a restaurant via restaurant_id. This maps to the existing "entity" concept in the Finance Tracker but specialized for restaurant operations. Users can belong to multiple restaurants.
- **Affected Modules**: `apps/Server/src/models/`, `apps/Server/src/repository/`, `apps/Server/src/core/services/`, `apps/Server/src/adapter/rest/`, `apps/Server/database/`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] `restaurant` table exists with columns: id, name, address, owner_id (FK to users), created_at, updated_at
  - [ ] `user_restaurants` join table exists for multi-restaurant user membership with role per restaurant
  - [ ] `GET /api/restaurants` returns restaurants for the authenticated user
  - [ ] `POST /api/restaurants` creates a new restaurant
  - [ ] All downstream entities filter by restaurant_id

---

### Stream 2: Task Management & Assignment
Enable restaurant owners/managers to create tasks, assign them to employees with schedules and recurrence, and track completion.

#### Requirements

##### REQ-007: Task Assignment with Recurrence
- **Type**: feature
- **Priority**: P1
- **Description**: Build a task management layer on top of the Event entity. Tasks are Events with type="tarea". A manager can create a task, assign it to a person (responsable_id), set a date and frequency (daily, weekly, monthly), and add a description. Recurring tasks auto-generate daily event instances for the responsible person. Tasks can be marked completed individually.
- **Affected Modules**: `apps/Server/src/core/services/event_service.py`, `apps/Server/src/adapter/rest/event_routes.py`
- **Dependencies**: REQ-003, REQ-001
- **Acceptance Criteria**:
  - [ ] A task can be created with a responsible person, date, frequency, and description
  - [ ] Daily recurring tasks generate events for each upcoming day (configurable window, e.g., 7 days ahead)
  - [ ] `GET /api/events?type=tarea&responsible_id={id}&date={date}` returns a person's tasks for a given day
  - [ ] Tasks can be individually marked as completed via `PATCH /api/events/{id}/status`
  - [ ] Overdue tasks (past date, status=pending) are flagged as "overdue"

##### REQ-008: Daily Employee Task Summary
- **Type**: feature
- **Priority**: P1
- **Description**: Build a service that generates a daily summary of tasks for each employee. This summary is used by the notification system (REQ-009) to send each person their task list for the day. The summary aggregates all pending Events of type="tarea" for a given person and date.
- **Affected Modules**: `apps/Server/src/core/services/`
- **Dependencies**: REQ-007
- **Acceptance Criteria**:
  - [ ] A service method `get_daily_task_summary(person_id, date)` returns all pending tasks for that person on that date
  - [ ] Summary includes: task description, time (if set), status, and overdue flag
  - [ ] `GET /api/persons/{id}/daily-tasks?date={date}` endpoint exposes this summary

---

### Stream 3: Notification System
Automated notifications via WhatsApp and email to send task reminders, document expiration alerts, and other event-triggered messages.

#### Requirements

##### REQ-009: WhatsApp Notification Integration
- **Type**: feature
- **Priority**: P1
- **Description**: Integrate with a WhatsApp Business API (e.g., Twilio, Meta Cloud API, or similar) to send automated messages. The system should send: (1) daily task lists to each employee every morning, (2) document expiration alerts before due dates, (3) low-stock alerts, and (4) profitability alerts (Phase 2). Messages are triggered by Events whose notification_channel includes "whatsapp".
- **Affected Modules**: `apps/Server/src/core/services/notification_service.py`, `apps/Server/src/adapter/` (new notification adapter)
- **Dependencies**: REQ-003, REQ-008
- **Acceptance Criteria**:
  - [ ] A `NotificationService` can send WhatsApp messages to a phone number with a text body
  - [ ] Daily cron job (or scheduled task) triggers morning task summaries for all employees
  - [ ] Event-based triggers send notifications when events are due or approaching
  - [ ] Message delivery status is logged
  - [ ] Failed deliveries are retried once and logged as errors

##### REQ-010: Email Notification Integration
- **Type**: feature
- **Priority**: P2
- **Description**: Integrate email sending (e.g., SendGrid, SES, or SMTP) as a secondary notification channel. Same triggers as WhatsApp but for users who prefer or also need email notifications.
- **Affected Modules**: `apps/Server/src/core/services/notification_service.py`
- **Dependencies**: REQ-003, REQ-008
- **Acceptance Criteria**:
  - [ ] `NotificationService` can send email notifications to a person's email address
  - [ ] Email notifications are triggered for events where canal_notificacion includes "email"
  - [ ] Email content is formatted as readable HTML

##### REQ-011: Document Expiration Alert Automation
- **Type**: feature
- **Priority**: P1
- **Description**: When a document with an expiration date is created or updated, the system must automatically create (or update) an Event of type="vencimiento" with configurable advance alert periods. Default alerts: 30 days before, 7 days before, and day-of expiration. Specific document types have custom alert schedules (e.g., food handling permits alert 30 days before, fire department permits alert at expiration, commerce chamber alerts annually).
- **Affected Modules**: `apps/Server/src/core/services/document_service.py`, `apps/Server/src/core/services/event_service.py`
- **Dependencies**: REQ-002, REQ-003, REQ-009
- **Acceptance Criteria**:
  - [ ] Creating a document with expiration_date auto-creates expiration alert Events
  - [ ] Default alert windows: 30 days, 7 days, and 0 days before expiration
  - [ ] Alert events have notification channel set based on the responsible person's preference
  - [ ] When the alert event date arrives, a notification is sent via the configured channel
  - [ ] Updating a document's expiration date updates the associated alert events

---

### Stream 4: Frontend — Core Management Views
Build the frontend pages for managing the four core entities and their interactions.

#### Requirements

##### REQ-012: Person Management Page
- **Type**: feature
- **Priority**: P1
- **Description**: Create a frontend page for listing, creating, editing, and deleting persons (employees, suppliers, owners). Use a data table with search/filter capabilities. Form uses react-hook-form with MUI. TR-prefix components.
- **Affected Modules**: `apps/Client/src/pages/`, `apps/Client/src/components/forms/`, `apps/Client/src/services/`, `apps/Client/src/types/`
- **Dependencies**: REQ-001
- **Acceptance Criteria**:
  - [ ] `PersonsPage` displays a table of all persons for the current restaurant
  - [ ] Table supports filtering by type (employee, supplier, owner) and search by name
  - [ ] `TRPersonForm` component allows creating and editing persons with validation
  - [ ] Delete confirmation dialog before removal
  - [ ] Page is accessible from the sidebar navigation

##### REQ-013: Document Management Page
- **Type**: feature
- **Priority**: P1
- **Description**: Create a frontend page for uploading, listing, and managing documents. Documents should display expiration status (valid, expiring soon, expired) with color-coded indicators. File upload with drag-and-drop support.
- **Affected Modules**: `apps/Client/src/pages/`, `apps/Client/src/components/forms/`, `apps/Client/src/services/`, `apps/Client/src/types/`
- **Dependencies**: REQ-002
- **Acceptance Criteria**:
  - [ ] `DocumentsPage` displays a table of all documents for the current restaurant
  - [ ] Documents show color-coded expiration status: green (valid), yellow (expiring within 30 days), red (expired)
  - [ ] `TRDocumentForm` supports file upload with drag-and-drop
  - [ ] Filter by document type and expiration status
  - [ ] Clicking a document opens detail view with download link

##### REQ-014: Event / Task Management Page
- **Type**: feature
- **Priority**: P1
- **Description**: Create a frontend page for viewing and managing events and tasks. Display as a calendar view and/or list view. Tasks can be filtered by responsible person, type, status, and date range. Ability to create, edit, and mark tasks as completed.
- **Affected Modules**: `apps/Client/src/pages/`, `apps/Client/src/components/forms/`, `apps/Client/src/services/`, `apps/Client/src/types/`
- **Dependencies**: REQ-003, REQ-007
- **Acceptance Criteria**:
  - [ ] `EventsPage` displays events in a list view with date grouping
  - [ ] Filter by type (task, expiration, payment, shift, checklist), responsible person, status, and date range
  - [ ] `TREventForm` allows creating and editing events/tasks with person assignment and recurrence settings
  - [ ] Quick-action button to mark tasks as completed
  - [ ] Overdue tasks are visually highlighted

##### REQ-015: Resource & Inventory Page
- **Type**: feature
- **Priority**: P1
- **Description**: Create a frontend page for managing resources (products, assets, services) and recording inventory movements. Show current stock levels with low-stock indicators. Movement history viewable per resource.
- **Affected Modules**: `apps/Client/src/pages/`, `apps/Client/src/components/forms/`, `apps/Client/src/services/`, `apps/Client/src/types/`
- **Dependencies**: REQ-004, REQ-005
- **Acceptance Criteria**:
  - [ ] `ResourcesPage` displays a table of all resources with current stock and low-stock indicators
  - [ ] Low-stock items (stock_actual < stock_minimo) are highlighted in red
  - [ ] `TRResourceForm` allows creating and editing resources
  - [ ] `TRInventoryMovementForm` allows recording entries and exits with reason selection
  - [ ] Clicking a resource shows movement history in a detail view or drawer

##### REQ-016: Restaurant Selector & Multi-Tenant Navigation
- **Type**: feature
- **Priority**: P1
- **Description**: Add restaurant selection to the application shell. Users who belong to multiple restaurants can switch between them. All data views filter by the currently selected restaurant. This mirrors the existing EntityContext pattern.
- **Affected Modules**: `apps/Client/src/contexts/`, `apps/Client/src/components/layout/`, `apps/Client/src/App.tsx`
- **Dependencies**: REQ-006
- **Acceptance Criteria**:
  - [ ] `RestaurantContext` provides current restaurant and switch functionality
  - [ ] Restaurant selector is visible in the top navbar or sidebar
  - [ ] Switching restaurant reloads all data views with the new restaurant_id
  - [ ] New sidebar navigation includes: Dashboard, Persons, Documents, Events/Tasks, Resources/Inventory

---

### Stream 5: Recipe Management & Cost Intelligence (Phase 2)
Extend the platform with recipe definitions, automated cost calculation from scanned invoices, and profitability alerts. This stream depends on Phase 1 being operational.

#### Requirements

##### REQ-017: Recipe Data Model & CRUD
- **Type**: feature
- **Priority**: P2
- **Description**: Create `recipe` and `recipe_item` tables. A Recipe represents a menu dish with a sale price. Recipe_Item links a recipe to its ingredients (resources) with quantities and units. The recipe's theoretical cost is calculated as the sum of (ingredient quantity × last unit cost). Fields — Recipe: id, nombre, precio_venta, activa (bool), costo_actual (calculated), margen (calculated %), rentable (bool), restaurant_id. Recipe_Item: id, recipe_id (FK), resource_id (FK), cantidad, unidad.
- **Affected Modules**: `apps/Server/src/models/`, `apps/Server/src/repository/`, `apps/Server/src/core/services/`, `apps/Server/src/adapter/rest/`, `apps/Server/src/interface/`, `apps/Server/database/`
- **Dependencies**: REQ-004
- **Acceptance Criteria**:
  - [ ] `recipe` and `recipe_item` tables exist with proper foreign keys
  - [ ] `POST /api/recipes` creates a recipe with its ingredients
  - [ ] `GET /api/recipes?restaurant_id={id}` returns recipes with calculated cost and margin
  - [ ] `PUT /api/recipes/{id}` updates recipe details and ingredients
  - [ ] Cost is automatically calculated as sum of (recipe_item.quantity × resource.last_unit_cost)
  - [ ] Margin is calculated as (precio_venta - costo_actual) / precio_venta × 100
  - [ ] `rentable` flag is set to false when margin drops below a configurable threshold (default: 60%)

##### REQ-018: Invoice OCR & Automatic Cost Update
- **Type**: feature
- **Priority**: P2
- **Description**: When a supplier invoice document (type="factura_proveedor") is uploaded, use OCR/AI to extract line items: supplier name, product names, quantities, and unit prices. For each detected item, match to an existing Resource, update its last_unit_cost, and create an inventory entry movement (type=entry, reason=compra). If a resource cannot be matched, flag it for manual review.
- **Affected Modules**: `apps/Server/src/core/services/document_service.py`, `apps/Server/src/core/services/resource_service.py`, `apps/Server/src/core/services/inventory_service.py`
- **Dependencies**: REQ-002, REQ-004, REQ-005
- **Acceptance Criteria**:
  - [ ] Uploading a document of type "factura_proveedor" triggers OCR processing
  - [ ] OCR extracts: supplier, product names, quantities, unit prices
  - [ ] Matched resources have their `last_unit_cost` updated
  - [ ] Inventory entry movements are automatically created for each matched item
  - [ ] Unmatched items are returned in the API response for manual review
  - [ ] Processing status and results are stored with the document record

##### REQ-019: Automatic Recipe Cost Recalculation
- **Type**: feature
- **Priority**: P2
- **Description**: Whenever a resource's `last_unit_cost` changes (e.g., after invoice processing), automatically recalculate the cost of all recipes that use that resource. Update the recipe's costo_actual, margen, and rentable fields. If any recipe becomes unprofitable (margin below threshold), trigger a profitability alert Event.
- **Affected Modules**: `apps/Server/src/core/services/recipe_service.py`, `apps/Server/src/core/services/event_service.py`
- **Dependencies**: REQ-017, REQ-018
- **Acceptance Criteria**:
  - [ ] When a resource's last_unit_cost is updated, all recipes containing that resource are recalculated
  - [ ] Recipe's costo_actual, margen, and rentable fields are updated
  - [ ] If margen < configured threshold, an Event of type "alerta_rentabilidad" is created
  - [ ] Alert Event includes: recipe name, current cost, sale price, margin percentage
  - [ ] Alert is sent to the restaurant owner via configured notification channel

##### REQ-020: Recipe-Based Inventory Deduction
- **Type**: feature
- **Priority**: P2
- **Description**: When a dish is sold or produced, automatically deduct the corresponding ingredient quantities from inventory. Create inventory exit movements (type=exit, reason=receta) for each recipe item. This enables tracking real vs. theoretical consumption and identifies waste/shrinkage.
- **Affected Modules**: `apps/Server/src/core/services/recipe_service.py`, `apps/Server/src/core/services/inventory_service.py`
- **Dependencies**: REQ-017, REQ-005
- **Acceptance Criteria**:
  - [ ] `POST /api/recipes/{id}/produce` deducts all recipe ingredients from inventory
  - [ ] Individual inventory exit movements are created for each ingredient
  - [ ] Insufficient stock for any ingredient prevents the operation and returns an error
  - [ ] Movement reason is set to "receta" with reference to the recipe

##### REQ-021: Recipe Management Frontend
- **Type**: feature
- **Priority**: P2
- **Description**: Create a frontend page for managing recipes — listing all dishes with their current cost, margin, and profitability status. Ability to add/edit recipes with ingredient selection from existing resources. Visual indicators for unprofitable dishes.
- **Affected Modules**: `apps/Client/src/pages/`, `apps/Client/src/components/forms/`, `apps/Client/src/services/`, `apps/Client/src/types/`
- **Dependencies**: REQ-017
- **Acceptance Criteria**:
  - [ ] `RecipesPage` displays all recipes with: name, sale price, current cost, margin %, profitability status
  - [ ] Unprofitable recipes are highlighted with a warning indicator
  - [ ] `TRRecipeForm` allows creating/editing recipes with dynamic ingredient rows (resource selector, quantity, unit)
  - [ ] Recipe detail view shows ingredient breakdown with individual costs

---

### Stream 6: Permit & Compliance Tracking
Specialized document management for restaurant-specific permits and regulatory compliance.

#### Requirements

##### REQ-022: Permit Type Presets with Custom Alert Schedules
- **Type**: feature
- **Priority**: P2
- **Description**: Provide preset document types for common restaurant permits with pre-configured alert schedules. Presets: Food Handling Permit (alert 30 days before), Fire Department Permit (alert at expiration), Commerce Chamber Registration (annual alert), Fire Extinguisher Service (alert at recharge date), Health Inspection Certificate (alert before inspection). When a document of a preset type is created, the appropriate alert schedule is automatically applied.
- **Affected Modules**: `apps/Server/src/core/services/document_service.py`, `apps/Server/database/`
- **Dependencies**: REQ-002, REQ-011
- **Acceptance Criteria**:
  - [ ] Preset permit types are seeded in the database or defined as configuration
  - [ ] Each preset includes: type name, default alert window(s), and notification channel
  - [ ] Creating a document with a preset type auto-creates events with the preset alert schedule
  - [ ] Custom alert schedules can override presets on a per-document basis

---

## Implementation Waves

### Wave 1: Foundation (Backend Data Layer)
**REQ IDs**: REQ-006, REQ-001, REQ-004, REQ-002, REQ-003, REQ-005

**Rationale**: These requirements establish the four universal entities, the restaurant multi-tenant scope, and inventory movements. They have no dependencies on other requirements and form the data backbone. REQ-006 (Restaurant) goes first as it provides the tenant scope, then REQ-001 (Person) and REQ-004 (Resource) in parallel (no cross-dependencies), followed by REQ-002 (Document) and REQ-003 (Event) which reference Person, and finally REQ-005 (Inventory Movement) which references both Resource and Person.

### Wave 2: Task Engine & Notifications
**REQ IDs**: REQ-007, REQ-008, REQ-009, REQ-010, REQ-011

**Rationale**: With the core entities in place, this wave builds the task management layer, daily summary generation, notification integrations (WhatsApp and email), and document expiration automation. These represent the "event-driven nervous system" that makes the platform immediately useful from day 1.

### Wave 3: Frontend Core Views
**REQ IDs**: REQ-016, REQ-012, REQ-013, REQ-014, REQ-015

**Rationale**: With all backend APIs available, this wave delivers the frontend management pages. REQ-016 (Restaurant selector) goes first as it provides the navigation shell, then the entity management pages can be built in parallel.

### Wave 4: Recipe & Cost Intelligence (Phase 2)
**REQ IDs**: REQ-017, REQ-018, REQ-019, REQ-020, REQ-021, REQ-022

**Rationale**: This wave adds Phase 2 features: recipe management, invoice OCR, automatic cost recalculation, recipe-based inventory deduction, and permit presets. These depend on a functioning Phase 1 with active inventory, resources, and document management.

## Cross-Cutting Concerns

### Multi-Tenancy via Restaurant Scope
All entities are scoped by `restaurant_id`. Every API query must filter by the current restaurant. This mirrors the existing Finance Tracker's `entity_id` pattern but uses `restaurant_id` for domain clarity.

### Database Migration Strategy
All schema changes should be managed via versioned SQL migration files in `apps/Server/database/`. The four universal entity tables, the inventory_movement table, and the restaurant/user_restaurants tables are all created in Wave 1.

### Notification Infrastructure
The notification system (WhatsApp + email) is a shared service used by multiple features (task summaries, document expiration alerts, stock alerts, profitability alerts). A unified `NotificationService` with pluggable adapters (WhatsApp, Email, Push) should be designed to avoid duplication.

### Event as Central Orchestrator
The Event entity is the unified mechanism for all time-based triggers. Document expiration, task recurrence, stock alerts, and profitability alerts all create Events. A background scheduler (cron job or task queue) must process due events and trigger notifications.

### OCR/AI Integration (Phase 2)
Invoice scanning requires an OCR service. Options include: Google Cloud Vision, AWS Textract, or Azure Document Intelligence. The integration should be abstracted behind a service interface for swappability.

### File Storage
Document file uploads need a storage solution. Supabase Storage is the natural choice given the existing Supabase PostgreSQL setup. All file URLs should be signed/expiring for security.

### Existing Codebase Integration
This project shares the same repository and tech stack as Finance Tracker. The restaurant operating system can either extend the existing application (new module) or be a separate app within the monorepo. This architectural decision needs clarification.

## Open Questions

- **Q1**: Should the restaurant operating system be a separate application within the monorepo or a new module within the existing Finance Tracker application? — Context: "Stack propuesto: Backend: Postgres (Supabase o Firebase SQL), API: REST o GraphQL, Frontend: React / FlutterFlow / similar" — The transcript proposes a generic stack but the project lives within an existing React + FastAPI monorepo.

- **Q2**: Which WhatsApp Business API provider should be used? — Context: "Enviar WhatsApp diario a cada empleado con sus tareas" and "Notificaciones: Email + WhatsApp API" — No specific provider was mentioned. Options include Twilio, Meta Cloud API, or others. Cost and regional availability (Latin America) are factors.

- **Q3**: How should the "restaurant" concept relate to the existing "entity" concept in Finance Tracker? — Context: "restaurante_id" is used throughout, but the existing system uses "entities" for multi-tenant scoping. Should restaurants be a type of entity, or a separate concept?

- **Q4**: What is the target margin threshold for profitability alerts? — Context: "margen < mínimo definido (ej. 60%)" — 60% is given as an example but it's unclear if this is a firm requirement or just illustrative. Should it be configurable per restaurant?

- **Q5**: Which OCR service should be used for invoice scanning in Phase 2? — Context: "IA (OCR) detecta: proveedor, productos, cantidades, precios unitarios" — No specific OCR service was mentioned. The choice affects cost, accuracy, and regional support for Spanish-language invoices.

- **Q6**: Should the background scheduler for event processing use an in-process solution (e.g., APScheduler) or an external task queue (e.g., Celery with Redis)? — Context: "Event llega a fecha → notificación" and "Tarea con frecuencia → genera Events diarios" — The processing model for recurring event generation and due-event notification was not specified.

- **Q7**: What is the scope of "Nómina básica" (basic payroll) mentioned in Phase 2? — Context: "Fase 2: Contratos digitales, Nómina básica, Producción / centros de costo" — Payroll was listed in Phase 2 but no detail was provided on calculations, tax handling, or payment methods.

- **Q8**: Should the API be REST or GraphQL? — Context: "API: REST o GraphQL" — The transcript lists both as options. The existing Finance Tracker uses REST, which would be more consistent.
