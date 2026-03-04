# RestaurantOS - User Manual

RestaurantOS is a comprehensive restaurant operations management module within the Finance Tracker application. It provides tools for managing employees, inventory, recipes, documents, events/tasks, notifications, and operational dashboards across one or more restaurants.

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Restaurant Selector](#2-restaurant-selector)
3. [Operational Dashboard](#3-operational-dashboard)
4. [Personas (People Management)](#4-personas-people-management)
5. [Documentos (Document Management)](#5-documentos-document-management)
6. [Eventos / Tareas (Events & Tasks)](#6-eventos--tareas-events--tasks)
7. [Recursos / Inventario (Resources & Inventory)](#7-recursos--inventario-resources--inventory)
8. [Recetas (Recipe Management)](#8-recetas-recipe-management)
9. [Notifications](#9-notifications)
10. [Alerts](#10-alerts)

---

## 1. Getting Started

### Accessing RestaurantOS

1. Log in to the Finance Tracker application
2. In the left sidebar, expand the **POCs** section
3. Click any item under the **RestaurantOS** subsection

### Navigation

The RestaurantOS section appears in the sidebar with six pages:

| Menu Item | Description |
|-----------|-------------|
| **Dashboard** | Operational overview with stats and alerts |
| **Personas** | Manage employees, suppliers, and owners |
| **Documentos** | Track documents, permits, and licenses |
| **Eventos / Tareas** | Manage tasks, deadlines, and scheduled events |
| **Recursos / Inventario** | Track inventory items and stock movements |
| **Recetas** | Manage recipes with ingredient costing |

### First-Time Setup

If no restaurants exist, a prompt will ask you to create your first restaurant. Click **"Crear Restaurante"** and enter:
- **Name** (required): The restaurant name
- **Address** (optional): Physical address

---

## 2. Restaurant Selector

The restaurant selector appears at the top of the sidebar when navigating any RestaurantOS page.

### Switching Restaurants

- **Expanded sidebar**: Click the dropdown and select a restaurant from the list
- **Collapsed sidebar**: Shows the first letter of the current restaurant name

All data displayed on RestaurantOS pages is scoped to the currently selected restaurant. Switching restaurants refreshes all data automatically.

### Managing Restaurants

You can create, rename, or delete restaurants from the selector. Your selection is remembered across sessions.

---

## 3. Operational Dashboard

**Path**: RestaurantOS > Dashboard

The dashboard provides a real-time operational overview of the current restaurant.

### Stat Cards

Four summary cards at the top:

| Card | Description |
|------|-------------|
| **Empleados** | Total number of employees |
| **Recursos** | Total inventory items tracked |
| **Documentos Activos** | Number of active documents |
| **Tareas Completadas Hoy** | Tasks marked as completed today |

### Today's Tasks

The left panel lists all tasks and events scheduled for today, grouped by the responsible person. Each task shows:
- Description
- Scheduled time
- Status badge (Pendiente, Completado, or Vencido)

### Alerts Panel

The right panel shows active alerts in three categories:

- **Document Expirations**: Documents expiring soon with days remaining
- **Low Stock Items**: Resources below their minimum stock level, showing current vs. minimum quantities
- **Pending Alerts**: Stock alerts, profitability alerts, and expiration alerts that haven't been addressed

### Recent Inventory Movements

A table at the bottom shows the most recent inventory entries and exits with:
- Date and time
- Movement type (Entrada / Salida) with color-coded chips
- Quantity
- Reason (Compra, Uso, Produccion, Merma, Receta, Ajuste)
- Notes

---

## 4. Personas (People Management)

**Path**: RestaurantOS > Personas

Manage all people associated with your restaurant: employees, suppliers, and owners.

### Viewing People

The page displays a searchable, filterable table with columns:
- **Name**
- **Role** (job title)
- **Type** (Empleado, Proveedor, Dueno)
- **Email**
- **WhatsApp**
- **Push** (indicates if push notifications are configured)
- **Actions** (Edit, Delete)

### Filtering

- **Search**: Type a name in the search field to filter results
- **Type filter**: Select from Todos, Empleado, Proveedor, or Dueno

### Adding a Person

1. Click the **add button** (+ icon) in the page header
2. Fill in the form:
   - **Nombre** (required): Full name
   - **Rol**: Job title or role description
   - **Tipo**: Select Empleado, Proveedor, or Dueno
   - **Email**: Email address (used for email notifications)
   - **WhatsApp**: Phone number with country code (used for WhatsApp notifications)
   - **Push Token**: Device token for push notifications
3. Click **"Agregar Persona"** to save

### Editing a Person

1. Click the **pencil icon** on the person's row
2. Modify any fields in the pre-populated form
3. Click **"Actualizar Persona"** to save

### Deleting a Person

1. Click the **trash icon** on the person's row
2. Confirm the deletion in the dialog

### Person Types

| Type | Spanish Label | Description |
|------|--------------|-------------|
| employee | Empleado | Restaurant staff member |
| supplier | Proveedor | External supplier or vendor |
| owner | Dueno | Restaurant owner |

---

## 5. Documentos (Document Management)

**Path**: RestaurantOS > Documentos

Track permits, licenses, contracts, invoices, and other documents with automatic expiration monitoring.

### Viewing Documents

The table shows all documents with columns:
- **Type**: Document category
- **Description**: Brief description
- **Person**: Associated person (if any)
- **Issue Date**: When the document was issued
- **Expiration Date**: When the document expires
- **Status**: Expiration status badge
- **Actions**: Edit, Delete

### Expiration Status Badges

| Badge | Color | Meaning |
|-------|-------|---------|
| Vigente | Green | Valid, not expiring soon |
| Por Vencer | Yellow | Expiring within 30 days |
| Vencido | Red | Already expired |

### Filtering

- **Type filter**: Filter by document type (Contrato, Permiso, Factura, etc.)
- **Status filter**: Filter by Todos, Vigente, Por Vencer, or Vencido

### Adding a Document

1. Click **"Agregar Documento"**
2. Fill in the form:
   - **Tipo** (required): Select document type
   - **Descripcion**: Description text
   - **Fecha de Emision**: Issue date
   - **Fecha de Vencimiento**: Expiration date
   - **Persona**: Associated person (select from dropdown)
   - **File**: Upload a document file (optional)
3. Click **"Agregar Documento"** to save

### Document Types

| Type | Spanish Label |
|------|--------------|
| contrato | Contrato |
| permiso | Permiso |
| factura | Factura |
| licencia | Licencia |
| factura_proveedor | Factura Proveedor |
| certificado | Certificado |
| manipulacion_alimentos | Cert. Manipulacion de Alimentos |
| bomberos | Permiso de Bomberos |
| camara_comercio | Reg. Camara de Comercio |
| extintor | Servicio de Extintores |
| sanidad | Cert. Inspeccion Sanitaria |
| otro | Otro |

### Permit Presets

When adding permit-type documents, you can select from pre-configured presets that automatically set alert schedules. For example, a health inspection certificate might auto-configure alerts at 45 days and 15 days before expiration.

---

## 6. Eventos / Tareas (Events & Tasks)

**Path**: RestaurantOS > Eventos / Tareas

Create and manage tasks, deadlines, payments, shifts, and checklists with optional recurrence and notification channels.

### Viewing Events

Events are displayed in a table grouped by date, with columns:
- **Time**: Scheduled time
- **Type**: Event category
- **Description**: Event details
- **Responsible**: Assigned person
- **Status**: Status badge
- **Actions**: Quick-complete, Edit, Delete

Overdue events are highlighted with a red background.

### Status Badges

| Badge | Color | Meaning |
|-------|-------|---------|
| Pendiente | Blue | Pending, not yet completed |
| Completado | Green | Marked as completed |
| Vencido | Red | Past due date, not completed |

### Filtering

- **Type filter**: Tarea, Vencimiento, Pago, Turno, Checklist
- **Status filter**: Todos, Pendiente, Completado, Vencido
- **Responsible filter**: Filter by assigned person
- **Date range**: From date (Desde) and To date (Hasta)

### Adding an Event

1. Click **"Agregar Evento"**
2. Fill in the form:
   - **Tipo** (required): Select event type
   - **Descripcion**: Description text
   - **Fecha** (required): Date and time
   - **Frecuencia**: Recurrence pattern
   - **Responsable**: Assigned person (required for Tarea type)
   - **Canal de Notificacion**: Email, WhatsApp, or Push
3. Click **"Agregar Evento"** to save

### Event Types

| Type | Spanish Label | Description |
|------|--------------|-------------|
| tarea | Tarea | Task assigned to a person |
| vencimiento | Vencimiento | Expiration deadline |
| pago | Pago | Payment due date |
| turno | Turno | Work shift |
| checklist | Checklist | Checklist item |

System-generated types (not shown in the create form):
- **alerta_stock**: Low stock alert (auto-created when stock drops below minimum)
- **alerta_rentabilidad**: Profitability alert (auto-created when recipe margin is low)

### Recurrence

Events can be set to repeat automatically:

| Frequency | Description |
|-----------|-------------|
| Sin repeticion | One-time event |
| Diario | Repeats daily |
| Semanal | Repeats weekly |
| Mensual | Repeats monthly |
| Anual | Repeats yearly |

Recurring events create a parent event that generates child instances on scheduled dates. Each child has independent status tracking.

### Quick-Complete

Click the **checkmark icon** on any pending event to immediately mark it as completed without opening the edit form.

### Editing an Event

1. Click the **pencil icon** on the event's row
2. Modify fields in the pre-populated form (title shows "Editar Evento")
3. Click **"Actualizar Evento"** to save

### Deleting an Event

1. Click the **trash icon** on the event's row
2. Confirm with **"Eliminar"** in the confirmation dialog

---

## 7. Recursos / Inventario (Resources & Inventory)

**Path**: RestaurantOS > Recursos / Inventario

Track all inventory items, monitor stock levels, and record all movements (entries and exits).

### Viewing Resources

The table shows all resources with columns:
- **Name**: Resource name
- **Type**: Product, Asset, or Service
- **Unit**: Measurement unit (kg, L, units, etc.)
- **Current Stock**: Current quantity on hand
- **Min Stock**: Minimum stock threshold
- **Last Cost**: Last known unit cost (COP)
- **Status**: Stock level indicator
- **Actions**: View, Edit, Delete

Low stock items show a red **"Stock Bajo"** badge. Items at or above minimum show a green **"OK"** badge.

### Filtering

- **Search**: Filter by resource name
- **Type filter**: Todos, Producto, Activo, Servicio

### Resource Types

| Type | Spanish Label | Description |
|------|--------------|-------------|
| producto | Producto | Consumable ingredient or supply |
| activo | Activo | Equipment or fixed asset |
| servicio | Servicio | External service |

### Adding a Resource

1. Click **"Agregar Recurso"**
2. Fill in the form:
   - **Nombre** (required): Resource name
   - **Tipo**: Select Producto, Activo, or Servicio
   - **Unidad**: Measurement unit (e.g., kg, L, und)
   - **Stock Actual**: Current quantity on hand
   - **Stock Minimo**: Threshold for low stock alerts
   - **Ultimo Costo Unitario**: Last purchase price per unit (COP)
3. Click to save

### Resource Detail Drawer

Click any resource row to open a detail drawer showing:
- Full resource information (name, type, unit, stock levels, cost)
- Stock status badge
- **Movement History Table**: Complete history of all inventory entries and exits for this resource, with date, type, quantity, reason, person, and notes

### Registering an Inventory Movement

1. Click **"Registrar Movimiento"** in the page header
2. Fill in the movement form:
   - **Recurso** (required): Select the resource
   - **Tipo** (required): Entrada (entry) or Salida (exit)
   - **Cantidad** (required): Quantity moved
   - **Razon**: Reason for movement
   - **Fecha**: Date of movement (defaults to now)
   - **Persona**: Person responsible
   - **Notas**: Additional notes
3. Submit to record the movement

The resource's current stock updates automatically when a movement is recorded.

### Movement Types

| Type | Spanish Label | Color | Effect |
|------|--------------|-------|--------|
| entry | Entrada | Green | Increases stock |
| exit | Salida | Red | Decreases stock |

### Movement Reasons

| Reason | Spanish Label | Description |
|--------|--------------|-------------|
| compra | Compra | Purchase from supplier |
| uso | Uso | Used in daily operations |
| produccion | Produccion | Used for production |
| merma | Merma | Waste, spoilage, or loss |
| receta | Receta | Used in recipe production |
| ajuste | Ajuste | Manual stock adjustment |

---

## 8. Recetas (Recipe Management)

**Path**: RestaurantOS > Recetas

Define recipes with ingredients, track food costs, calculate profit margins, and produce portions that automatically deduct inventory.

### Viewing Recipes

The table shows all recipes with columns:
- **Name**: Recipe name
- **Sale Price**: Selling price (COP)
- **Current Cost**: Calculated ingredient cost (COP)
- **Margin %**: Profit margin percentage
- **Profitability**: Rentable (green) or No Rentable (red) badge with margin %
- **Status**: Activa (green) or Inactiva (gray)
- **Actions**: Edit, Delete, Produce

Non-profitable recipes (margin below 60%) are highlighted with a red background.

### Searching

Type a recipe name in the search field to filter results.

### Adding a Recipe

1. Click **"Agregar Receta"**
2. Fill in the form:
   - **Nombre** (required): Recipe name
   - **Precio de Venta**: Sale price in COP
   - **Activa**: Toggle active/inactive status
   - **Ingredientes**: Add ingredient items:
     - Select a resource from the dropdown
     - Enter quantity needed per portion
     - Specify the unit
     - Click add to include more ingredients
3. Save to create the recipe

The system automatically calculates:
- **Current Cost**: Sum of (ingredient quantity x resource's last unit cost) for all ingredients
- **Margin %**: ((Sale Price - Current Cost) / Sale Price) x 100
- **Is Profitable**: True if margin is 60% or above

### Recipe Detail Drawer

Click any recipe row to open a detail drawer showing:
- Recipe name, sale price, current cost, margin percentage
- Profitability badge
- **Ingredients Table**: All resources used in the recipe with quantity, unit, and unit cost

### Producing Portions

The produce feature deducts ingredients from inventory based on recipe quantities:

1. Click the **play icon** on a recipe row
2. Enter the number of portions to produce (minimum 1)
3. Confirm production

**What happens:**
- For each ingredient in the recipe, the system creates an exit movement with reason "receta"
- Quantities deducted = ingredient quantity x number of portions
- Resource stock levels update automatically
- If any ingredient stock drops below minimum, a low stock alert is generated

### Cost Recalculation

Recipe costs update automatically when ingredient prices change. The system recalculates:
- Current cost from the latest `last_unit_cost` of each ingredient resource
- Margin percentage
- Profitability status

If a recipe transitions from profitable to non-profitable (or vice versa), a profitability alert event is automatically created.

---

## 9. Notifications

RestaurantOS supports three notification channels for event reminders, alerts, and daily summaries.

### Notification Channels

| Channel | Setup | Description |
|---------|-------|-------------|
| **Email** | Add email to person's profile | Sends HTML-formatted notifications |
| **WhatsApp** | Add WhatsApp number with country code (e.g., +57300...) | Sends text messages via WhatsApp |
| **Push** | Configure push token in person's profile | Sends mobile push notifications via FCM |

### How Notifications Work

1. When creating an event, select a **Canal de Notificacion** (notification channel)
2. The system sends notifications to the responsible person via the selected channel
3. Notifications are logged in the notification log for audit purposes

### Daily Task Summaries

The system can send daily summaries to all employees with pending or overdue tasks. Each summary includes:
- Count of pending tasks
- Count of overdue tasks
- List of tasks with descriptions and times

### Notification Log

All notification attempts (successful or failed) are recorded with:
- Channel used
- Recipient
- Message content
- Status (sent/failed)
- Error message (if failed)
- Timestamp

---

## 10. Alerts

RestaurantOS automatically generates alerts for critical operational events.

### Alert Types

#### Document Expiration Alerts
- Triggered when documents approach their expiration date
- Configurable alert windows (e.g., 45 days, 15 days, 1 day before)
- Appear on the dashboard and as events of type "vencimiento"

#### Low Stock Alerts
- Automatically generated when a resource's `current_stock` drops below `minimum_stock`
- Created as events of type "alerta_stock"
- Show on the dashboard with current vs. minimum quantities
- Linked to the specific resource via `related_resource_id`

#### Profitability Alerts
- Generated when a recipe's margin drops below 60%
- Created as events of type "alerta_rentabilidad"
- Include the recipe name and current margin in the description
- Triggered when ingredient costs change and recipe is recalculated

### Viewing Alerts

Alerts appear in three places:
1. **Dashboard Alerts Panel**: Shows all active alerts organized by category
2. **Events / Tareas page**: Alert events can be filtered and managed like regular events
3. **Resource detail drawer**: Low stock status shown per resource

### Resolving Alerts

- Stock alerts resolve when inventory is replenished above minimum levels
- Expiration alerts can be dismissed by renewing documents and updating expiration dates
- Profitability alerts resolve when recipe prices are adjusted or ingredient costs decrease
- All alert events can be marked as completed via quick-complete

---

## Keyboard & Navigation Tips

- The sidebar is **collapsible**: click the collapse button to switch between full and icon-only modes
- Sidebar section expansion state is **remembered** between sessions
- The selected restaurant is **persisted** across sessions via localStorage
- Click any **table row** (on Resources or Recipes pages) to open a detail drawer
- Use **filters and search** to quickly find specific items in large datasets
- **Status badges** are color-coded consistently across all pages (green = good, yellow = warning, red = critical)
