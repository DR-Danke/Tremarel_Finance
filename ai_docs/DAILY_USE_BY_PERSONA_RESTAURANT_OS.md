# RestaurantOS - Daily Use by Persona

## Purpose & How to Use This Document

This document describes how each persona uses RestaurantOS throughout a typical workday. It is organized by **role** and **time of day**, providing a workflow narrative that complements the feature-reference style of [USER_GUIDE_RESTAURANT_OS.md](./USER_GUIDE_RESTAURANT_OS.md).

**Use this document when you need to understand:**
- What each role does first thing in the morning, during service, and at end of day
- Which pages and features each persona relies on most
- How personas interact with each other through the system
- How WhatsApp notifications fit into daily operations

**Use the User Guide when you need:**
- Step-by-step instructions for a specific feature
- Field definitions, filter options, and form details
- Technical details about alert types, event recurrence, or movement reasons

---

## Personas Overview

| Persona | System Role | Primary Pages | Notification Channels | Daily Goal |
|---------|-------------|---------------|----------------------|------------|
| Restaurant Owner (Dueno) | owner | Dashboard, Recetas, Recursos | WhatsApp, Email | Monitor profitability, ensure compliance, strategic decisions |
| Restaurant Manager | employee (manager role) | Dashboard, Eventos/Tareas, Personas, Recursos | WhatsApp, Email | Coordinate staff, manage inventory, complete daily tasks |
| Kitchen Staff / Chef | employee (chef/cocinero role) | Dashboard, Recetas, Recursos | WhatsApp | Execute recipes, report stock issues, complete assigned tasks |
| Administrative / Compliance Officer | employee (admin role) | Dashboard, Documentos, Eventos/Tareas | Email, WhatsApp | Track permits/licenses, ensure renewals, maintain compliance |

> **Note:** Suppliers (Proveedores) are data records in the Personas page, not system users. They do not log in or receive notifications directly through RestaurantOS.

---

## Persona 1: Restaurant Owner (Dueno)

The owner's primary concern is profitability, compliance, and high-level operational health. They may not be on-site every day but need instant visibility into how the restaurant is performing.

### Morning (Before Service)

1. **Receive WhatsApp daily summary** — The system sends a morning message listing any pending or overdue tasks assigned to the owner. Format: personalized greeting with task count and descriptions.

2. **Open Dashboard** — The dashboard greets the owner with a time-appropriate message ("Buenos dias", "Buenas tardes", or "Buenas noches") and a briefing summary. The owner scans:
   - **Stat cards**: Employee count, resource count (with low stock indicator), active documents, tasks completed today, overdue tasks (red highlight when > 0)
   - **Alerts panel**: Document expirations (yellow = >7 days, red = <=7 days), low stock items, profitability alerts
   - **Today's tasks**: Any owner-assigned tasks grouped by responsible person
   - **Quick actions**: "Nueva Tarea" and "Registrar Movimiento" buttons for fast data entry

3. **Check profitability alerts** — If any recipe's margin dropped below 60%, the dashboard shows a profitability alert. The owner navigates to **Recetas** to review the affected recipe's current cost vs. sale price and decides whether to adjust pricing or source cheaper ingredients.

4. **Review document expirations** — If the alerts panel shows expiring documents, the owner either delegates renewal to the compliance officer or navigates to **Documentos** to check details (see [User Guide: Documentos](./USER_GUIDE_RESTAURANT_OS.md#5-documentos-document-management)).

### Midday (During Service)

5. **Spot-check inventory** — If a low stock alert appeared in the morning, the owner checks **Recursos/Inventario** to see current stock levels and recent movements. They may contact a supplier or instruct the manager to place an order.

6. **Monitor task completion** — Return to the Dashboard to see how many tasks have been completed today vs. what remains pending.

### End of Day

7. **Review recipe margins** — Open **Recetas** to scan the profitability column. Recipes with margin below 60% show a red "No Rentable" badge. Click any recipe to open the detail drawer showing an ingredient cost distribution pie chart, helping identify which ingredients drive the most cost. The owner may adjust sale prices or flag recipes for ingredient review.

8. **Check recent inventory movements** — The Dashboard's "Recent Inventory Movements" table shows the day's entries and exits, giving the owner a quick audit trail.

### Weekly Activities

- **Review all document statuses** — Filter **Documentos** by "Por Vencer" (expiring soon) and "Vencido" (expired) to ensure nothing critical is missed.
- **Analyze resource costs** — Review "Ultimo Costo" column in **Recursos/Inventario** to identify cost trends across ingredients.
- **Staff review** — Check **Personas** for completeness of employee records (WhatsApp numbers, roles) to ensure notifications reach everyone.

---

## Persona 2: Restaurant Manager

The manager is the operational backbone — they coordinate daily tasks, manage inventory flows, and ensure the team executes smoothly. They are on-site daily.

### Morning (Before Service)

1. **Receive WhatsApp daily summary** — Morning message with the manager's own pending and overdue tasks.

2. **Open Dashboard** — Scan the briefing:
   - **Today's tasks** (left panel): Review all tasks for the day, grouped by responsible person. Identify any overdue tasks (highlighted in red).
   - **Low stock items**: Note which ingredients need restocking before service.
   - **Recent movements**: Check if yesterday's expected deliveries were registered.

3. **Assign and create tasks** — Navigate to **Eventos/Tareas** to:
   - Create new tasks ("Tarea" type) for the day, assigning them to specific employees
   - Set notification channel to WhatsApp so employees receive their assignments
   - Review and reschedule any overdue tasks from previous days
   - Use the weekly calendar view to visualize the week's workload at a glance
   - (See [User Guide: Eventos/Tareas](./USER_GUIDE_RESTAURANT_OS.md#6-eventos--tareas-events--tasks))

4. **Register morning deliveries** — When suppliers deliver ingredients, go to **Recursos/Inventario** and click "Registrar Movimiento":
   - Select the resource, type "Entrada", reason "Compra"
   - Enter quantity and associate the supplier as the responsible person
   - Stock levels update automatically; low stock alerts resolve if stock rises above minimum

### Midday (During Service)

5. **Quick-complete tasks** — As employees finish tasks, use the checkmark icon on **Eventos/Tareas** to mark them completed. The Dashboard's "Tareas Completadas Hoy" counter updates in real time.

6. **Handle stock issues** — If kitchen staff reports a shortage:
   - Check the resource in **Recursos/Inventario** to verify current stock
   - Register any waste/spoilage as an exit movement with reason "Merma"
   - If stock drops below minimum, a low stock alert is automatically generated

7. **Register inventory exits** — Record significant ingredient usage:
   - Type "Salida", reason "Uso" for general consumption
   - Type "Salida", reason "Merma" for waste or spoilage

### End of Day

8. **Task completion review** — Filter **Eventos/Tareas** by today's date and status "Pendiente" to identify incomplete tasks. Follow up with responsible employees or reschedule.

9. **Inventory reconciliation** — Compare physical counts against system stock in **Recursos/Inventario**. Register adjustments using movement type "Entrada" or "Salida" with reason "Ajuste".

10. **Plan tomorrow** — Create recurring tasks or one-time events for the next day in **Eventos/Tareas**.

---

## Persona 3: Kitchen Staff / Chef

Kitchen staff interact with RestaurantOS primarily through WhatsApp notifications and brief system check-ins. Their focus is executing recipes, managing ingredient usage, and completing assigned tasks.

### Start of Shift

1. **Receive WhatsApp daily summary** — Morning message listing today's tasks: prep work, production targets, cleaning checklists, etc. Overdue tasks from previous days are flagged.

2. **Check Dashboard** — Quick scan of:
   - **Today's tasks**: See personal assignments with times and descriptions
   - **Low stock alerts**: Know which ingredients are running low before starting prep

3. **Review recipe details** — Open **Recetas** and click on today's recipes to see:
   - Ingredient list with quantities per portion
   - Current cost and margin
   - (See [User Guide: Recetas](./USER_GUIDE_RESTAURANT_OS.md#8-recetas-recipe-management))

### During Service

4. **Produce recipe portions** — When preparing menu items, use the produce feature (play icon) on the **Recetas** page:
   - Enter the number of portions produced
   - System automatically deducts ingredient quantities from inventory
   - If any ingredient drops below minimum stock, a low stock alert is generated

5. **Report stock issues** — When an ingredient runs out or runs low:
   - Check **Recursos/Inventario** for the resource's current stock
   - Notify the manager (who will register the appropriate movement or place an order)

6. **Complete tasks** — Use the quick-complete checkmark on **Eventos/Tareas** as prep tasks, cleaning tasks, or checklists are finished.

### End of Shift

7. **Final task check** — Verify all assigned tasks for the shift are marked complete.

8. **Report waste** — Inform the manager of any spoilage or waste so they can register "Merma" exit movements.

---

## Persona 4: Administrative / Compliance Officer

The compliance officer ensures the restaurant's legal documents, permits, and licenses are current. They work primarily with documents and expiration alerts, often on a less frequent cadence than daily operations staff.

### Morning

1. **Check expiration alerts** — Open the **Dashboard** and focus on the Alerts panel:
   - **Red alerts (URGENTE)**: Documents expiring within 7 days — require immediate action
   - **Yellow alerts (Atencion)**: Documents expiring in more than 7 days — plan renewal
   - WhatsApp/email notifications also arrive for expiring documents with urgency formatting

2. **Review Documentos page** — Navigate to **Documentos** and filter by:
   - Status "Por Vencer" to see all documents approaching expiration
   - Status "Vencido" to see already-expired documents
   - (See [User Guide: Documentos](./USER_GUIDE_RESTAURANT_OS.md#5-documentos-document-management))

### Core Work

3. **Initiate renewals** — For expiring documents:
   - Note the document type, associated person, and expiration date
   - Contact the relevant authority or vendor to begin the renewal process
   - Track progress via the Eventos/Tareas page by creating follow-up tasks

4. **Register new documents** — When renewed documents arrive:
   - Edit the existing document in **Documentos** to update the expiration date, or
   - Add a new document with the updated information and file upload
   - The system automatically creates new expiration alert events based on the updated date

5. **Manage permit presets** — When adding permit-type documents, use pre-configured presets that automatically set alert schedules. Built-in presets include:
   - Food handling certificate (manipulacion_alimentos): alerts at 30, 7, and 0 days
   - Fire department permit (bomberos): alert at expiration day only
   - Commerce chamber registration (camara_comercio): alerts at 30 and 14 days
   - Fire extinguisher service (extintor): alerts at 30 and 7 days
   - Health inspection certificate (sanidad): alerts at 30, 14, and 7 days

6. **Create compliance tasks** — In **Eventos/Tareas**, create tasks of type "Vencimiento" or "Tarea" to assign renewal responsibilities to specific people, with appropriate notification channels.

### Weekly / Monthly Activities

- **Full document audit** — Review all documents across all types (Contrato, Permiso, Licencia, Certificado, etc.) to ensure completeness.
- **Verify person-document associations** — Check that documents linked to specific employees (e.g., food handling certificates) are up to date in **Personas** cross-referenced with **Documentos**.
- **Report to owner** — Summarize compliance status: how many documents are current, expiring soon, or expired. The Dashboard's "Documentos Activos" stat card provides a quick count.

---

## Cross-Persona Interaction Patterns

### Owner -> Manager -> Kitchen Staff (Delegation Chain)

```
Owner sees profitability alert on Dashboard
  -> Owner decides to change recipe or sourcing
    -> Manager creates tasks in Eventos/Tareas for kitchen staff
      -> Kitchen staff receives WhatsApp notification
        -> Kitchen staff executes updated recipe via Recetas
          -> System updates inventory and recalculates margins
```

### Compliance Officer -> Owner (Escalation Chain)

```
System generates document expiration alert (7 days or fewer)
  -> Compliance officer receives WhatsApp/email notification
    -> Compliance officer reviews in Documentos page
      -> If renewal requires owner approval/signature:
        -> Creates task assigned to owner in Eventos/Tareas
          -> Owner receives WhatsApp notification
            -> Owner takes action and marks task complete
```

### Manager -> Kitchen Staff (Daily Operations)

```
Manager reviews Dashboard morning briefing
  -> Creates/assigns daily tasks in Eventos/Tareas
    -> Kitchen staff receives WhatsApp daily summary
      -> Kitchen staff completes tasks (quick-complete)
        -> Manager monitors completion on Dashboard
```

### System -> All Personas (Automated Alerts)

```
Inventory movement causes stock < minimum
  -> System creates alerta_stock event
    -> Low stock alert appears on Dashboard for all users
    -> WhatsApp notification sent to relevant persons

Recipe cost recalculation causes margin < 60%
  -> System creates alerta_rentabilidad event
    -> Profitability alert appears on Dashboard
    -> WhatsApp notification sent to owner
```

---

## WhatsApp as an Operational Channel

### 8.1 Current Outbound Capabilities (Implemented)

RestaurantOS uses WhatsApp as a primary notification channel, reflecting the real-world communication habits of small restaurant teams in Latin America.

**Architecture:** `NotificationService` -> `WhatsAppAdapter` (currently in stub mode, ready for Twilio or Meta Cloud API integration). Messages are capped at 4,096 characters. Phone numbers must include country code (e.g., `+573001234567`).

**Outbound message types:**

| Message Type | Trigger | Format |
|-------------|---------|--------|
| **Daily task summary** | `POST /api/notifications/send-daily-summaries` | Personalized greeting, task count, numbered task list with times, overdue flags |
| **Document expiration alert** | `POST /api/notifications/process-expiration-alerts` | Urgency indicator (red <=7 days, yellow >7 days), document name, expiry date, days remaining |
| **Low stock alert** | Automatic when `current_stock < minimum_stock` | Resource name, current vs. minimum stock levels |
| **Profitability alert** | Automatic when recipe margin drops below 60% | Recipe name, cost, sale price, margin percentage |
| **Event dispatch** | `POST /api/notifications/dispatch` or `/dispatch-all` | Event-specific notification based on type and channel |

**Daily summary WhatsApp format (Spanish):**
```
Buenos dias, {name}! (sunrise emoji)
(clipboard emoji) *Resumen de tareas para {date}*

Tienes *{count} tarea(s)* pendiente(s)
(warning emoji) *{overdue} tarea(s) vencida(s)*

1. {description} - {time} (warning emoji) *VENCIDA*
2. {description} - {time}

Que tengas un excelente dia! (flexed biceps emoji)
```

**Document expiration WhatsApp format:**
```
(red circle emoji) *URGENTE* - Documento por vencer     [<=7 days]
(yellow circle emoji) *Atencion* - Documento por vencer  [>7 days]

El documento *{name}* vence el *{date}*.
(alarm clock emoji) Quedan *{days} dia(s)*.

Por favor, gestiona la renovacion a tiempo.
```

### 8.2 Two-Way WhatsApp Interaction Use Cases (Future / Proposed)

These scenarios describe how each persona could interact with RestaurantOS by replying to WhatsApp messages, using a simple keyword-based command pattern (not NLP).

**Owner:**
- Reply `resumen` -> Receive instant dashboard summary: employee count, active documents, low stock items, profitability alerts
- Reply with a recipe name -> Get current margin info (cost, sale price, margin %)
- Receive profitability alert, reply `subir precio [receta] [nuevo_precio]` -> Update recipe sale price

**Manager:**
- Reply `completar [tarea_id]` -> Mark a task as completed
- Reply `stock [recurso]` -> Check current stock level for a resource
- Reply `entrada [recurso] [cantidad]` -> Register an inventory entry (reason: Compra)
- Forward supplier invoice photo -> OCR processing to auto-register inventory entry

**Kitchen Staff:**
- Reply `listo` -> Mark current/most recent assigned task as completed
- Reply `falta [ingrediente]` -> Report low stock to manager
- Reply `producir [receta] [porciones]` -> Trigger recipe production and inventory deduction

**Compliance Officer:**
- Reply `vencimientos` -> Get list of documents expiring within 30 days
- Reply `renovado [documento_id]` -> Mark a document as renewed (pending file upload via web)

### 8.3 Implementation Considerations

- **Webhook endpoint:** `POST /api/notifications/whatsapp/webhook` to receive inbound messages
- **Message parsing:** Simple keyword-based command router (no NLP or multi-turn conversations)
- **Authentication:** Match incoming WhatsApp number to a Person record's `whatsapp` field to resolve identity and restaurant context
- **Security:** Only registered persons with matching WhatsApp numbers can interact
- **Conversation model:** Stateless command-response pattern (no session tracking)
- **Provider support:** Both Twilio and Meta Cloud API support incoming webhook callbacks

---

## System-Generated Daily Rhythm

RestaurantOS creates a natural operational cadence through automated notifications and alerts.

### Morning Notifications

| Time | Action | Recipients | Channel |
|------|--------|-----------|---------|
| Early morning | Send daily task summaries | All employees with pending/overdue tasks | WhatsApp, Email |
| Early morning | Process document expiration alerts | Persons associated with expiring documents | WhatsApp, Email |
| Early morning | Dispatch due event notifications | All persons with events due today | Per event's configured channel |

Triggered via: `POST /api/notifications/send-daily-summaries`, `POST /api/notifications/process-expiration-alerts`, `POST /api/notifications/dispatch-all`

### Event-Driven Alerts (Any Time)

| Trigger | Alert Type | Dashboard Location |
|---------|-----------|-------------------|
| Stock drops below minimum after movement | `alerta_stock` | Alerts panel: "Low Stock Items" |
| Recipe margin drops below 60% after cost recalculation | `alerta_rentabilidad` | Alerts panel: "Pending Alerts" |
| Document approaches expiration date | `vencimiento` event | Alerts panel: "Document Expirations" |

### Overdue Flagging

- Events past their scheduled date with status "Pendiente" are automatically flagged as "Vencido" (overdue)
- Overdue events display a red background on the Eventos/Tareas page
- Overdue tasks are included in daily summaries with a "VENCIDA" indicator
- The Dashboard groups overdue tasks visibly for immediate attention

---

## Quick Reference: Persona-to-Page Mapping

| Page | Owner | Manager | Kitchen Staff | Compliance Officer |
|------|-------|---------|---------------|-------------------|
| **Dashboard** | Daily (morning scan, alerts) | Daily (morning briefing, task monitoring) | Daily (quick task check) | Daily (expiration alerts) |
| **Personas** | Weekly (staff review) | As needed (add/edit employees) | Rarely | As needed (verify contacts) |
| **Documentos** | Weekly (compliance review) | Rarely | Never | Daily (core workflow) |
| **Eventos / Tareas** | As needed (view delegated tasks) | Daily (create, assign, complete) | Daily (view and complete tasks) | As needed (create renewal tasks) |
| **Recursos / Inventario** | As needed (spot-check, cost review) | Daily (register movements, reconcile) | As needed (check stock, produce) | Never |
| **Recetas** | Weekly (margin review, price adjustments) | As needed (verify costs) | Daily (recipe reference, produce) | Never |

---

## Appendix: Notification Timing by Persona

| Persona | Primary Channel | Morning Summary | Expiration Alerts | Stock Alerts | Profitability Alerts |
|---------|----------------|-----------------|-------------------|-------------|---------------------|
| Owner | WhatsApp | Yes (own tasks) | Yes (all documents) | Yes (all resources) | Yes (all recipes) |
| Manager | WhatsApp | Yes (own tasks) | Occasionally (if assigned) | Yes (all resources) | Occasionally |
| Kitchen Staff | WhatsApp | Yes (own tasks) | No | When triggered by production | No |
| Compliance Officer | Email + WhatsApp | Yes (own tasks) | Yes (all documents) | No | No |

**Alert urgency formatting:**
- **WhatsApp:** Red circle + `*URGENTE*` (<=7 days) or Yellow circle + `*Atencion*` (>7 days)
- **Email:** Dark red header (#d32f2f) for urgent, amber header (#f9a825) for warning
- **Dashboard:** Red "Vencido" badge for expired, yellow "Por Vencer" badge for expiring within 30 days
