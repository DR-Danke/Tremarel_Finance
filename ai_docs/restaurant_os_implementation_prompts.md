# Restaurant Operating System - ADW Implementation Prompts

## Overview

This plan contains GitHub issue prompts for implementing the Restaurant Operating System using `adw_sdlc_iso.py`. Each prompt will trigger the `/feature` command which handles technical planning.

**Source:** Product vision and architecture document describing a centralized operational management platform for small restaurants.
**Requirements Doc:** `ai_docs/prds/prd-ef2d72c2-restaurant-operating-system.md`

**Project Goal:** Build a centralized "restaurant operating system" that replaces the disorganized workflow of WhatsApp, notebooks, and disconnected tools used by small restaurants. The platform is built on four universal entities (Person, Document, Event, Resource) and an event-driven architecture. Phase 1 delivers employee management, task assignment with WhatsApp notifications, document tracking with expiration alerts, and basic inventory. Phase 2 adds recipe management, automated cost calculation from scanned invoices (OCR), and profitability alerts.

**Key Concepts:**
1. **Universal Entities** — Person, Document, Event, Resource form the data backbone; all business functions are composed from these entities plus business rules
2. **Event as Central Orchestrator** — Events represent tasks, deadlines, payments, shifts, checklists, and alerts; all time-based triggers flow through Events
3. **Restaurant Multi-Tenancy** — All data is scoped by `restaurant_id`, mirroring the existing Finance Tracker `entity_id` pattern
4. **Recurring Event Generation** — Tasks and alerts with a frequency auto-generate individual event instances
5. **Notification Channels** — WhatsApp and email notifications triggered by due Events

**Execution**: `uv run adw_sdlc_iso.py <issue-number>`

**Parallelization**: Issues within the same wave can run simultaneously in separate worktrees (up to 15 concurrent).

**Naming Conventions:**
- Component prefix: `TR` (TRPersonForm, TRDocumentForm, TREventForm, TRResourceForm)
- Database table prefix: none (restaurant, person, document, event, resource, inventory_movement)
- Route prefix: `/api/` (backend), follows existing Finance Tracker patterns
- All new models, repositories, services, and routes follow existing Clean Architecture patterns in apps/Server/

**Terminology:**
- **Person** = Employee, supplier, or owner within a restaurant
- **Document** = Legal/administrative artifact (contract, permit, invoice, license)
- **Event** = Time-based trigger (task, expiration, payment, shift, checklist, alert)
- **Resource** = Physical item (product/ingredient, asset/equipment, service)
- **Inventory Movement** = Stock change record (entry/exit with reason)
- **Recipe** = Menu dish with ingredients, sale price, and calculated cost/margin
- **Flete** = Not applicable (this is restaurant domain, not transport)

---

## Wave 1: Foundation Core Entities (Run in Parallel)

These three requirements establish the restaurant multi-tenant scope and the two independent universal entities (Person and Resource). They have zero cross-dependencies and can run simultaneously.

### ROS-001: Restaurant Multi-Tenant Entity

**Title:** `[RestaurantOS] Wave 1: Restaurant Multi-Tenant Entity`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** Create the `restaurant` table that serves as the multi-tenant scope for all data. A restaurant represents a single location/business. All other entities (Person, Document, Event, Resource) will be scoped to a restaurant via restaurant_id. This maps to the existing "entity" concept in the Finance Tracker but specialized for restaurant operations. Users can belong to multiple restaurants.

**Current Wave:** Wave 1 of 7 — Foundation Core Entities
**Current Issue:** ROS-001 (Issue 1 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-002 and ROS-003.

**Dependencies:** None
**What comes next:** All downstream entities (Person, Document, Event, Resource, Inventory Movement) will use restaurant_id as a foreign key for multi-tenant scoping.

## Request
Create the restaurant entity with full backend CRUD and multi-restaurant user membership.

### 1. Database Migration
Create migration file `apps/Server/database/create_restaurant_tables.sql`:
```sql
CREATE TABLE restaurant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    address TEXT,
    owner_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_restaurants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    restaurant_id UUID NOT NULL REFERENCES restaurant(id),
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, restaurant_id)
);
```

### 2. SQLAlchemy Model
Create `apps/Server/src/models/restaurant_model.py`:
- `RestaurantModel` with columns: id, name, address, owner_id, created_at, updated_at
- `UserRestaurantModel` with columns: id, user_id, restaurant_id, role, created_at

### 3. Pydantic DTOs
Create `apps/Server/src/interface/restaurant_dto.py`:
- `RestaurantCreateDTO`: name (required), address (optional)
- `RestaurantUpdateDTO`: name (optional), address (optional)
- `RestaurantResponseDTO`: id, name, address, owner_id, created_at, updated_at
- `RestaurantListDTO`: list of RestaurantResponseDTO

### 4. Repository
Create `apps/Server/src/repository/restaurant_repository.py`:
- `create(data, owner_id)` — creates restaurant and user_restaurant entry
- `get_by_id(restaurant_id)` — returns restaurant
- `get_by_user(user_id)` — returns all restaurants for a user
- `update(restaurant_id, data)` — updates restaurant
- `delete(restaurant_id)` — deletes restaurant

### 5. Service
Create `apps/Server/src/core/services/restaurant_service.py`:
- Business logic layer calling repository
- Validation: user must be owner or admin to update/delete

### 6. REST Routes
Create `apps/Server/src/adapter/rest/restaurant_routes.py`:
- `GET /api/restaurants` — returns restaurants for authenticated user
- `POST /api/restaurants` — creates a new restaurant
- `GET /api/restaurants/{id}` — returns restaurant detail
- `PUT /api/restaurants/{id}` — updates restaurant
- `DELETE /api/restaurants/{id}` — deletes restaurant
- All endpoints require JWT authentication

### 7. Register Router
Add restaurant router to `apps/Server/main.py`.

**UI Language:** N/A (backend only)
**Validation:** name is required, max 255 chars. All downstream entities must filter by restaurant_id.
```

---

### ROS-002: Person Entity Data Model & CRUD

**Title:** `[RestaurantOS] Wave 1: Person Entity Data Model & CRUD`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** Create the `person` database table and full backend CRUD. A Person represents employees, suppliers, or owners within a restaurant. This is the first of four universal entities and is referenced by Documents (owner), Events (responsible), and Inventory Movements (performer).

**Current Wave:** Wave 1 of 7 — Foundation Core Entities
**Current Issue:** ROS-002 (Issue 2 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-001 and ROS-003.

**Dependencies:** None (restaurant_id FK will be added; if restaurant table doesn't exist yet, use a VARCHAR placeholder that will be migrated)
**What comes next:** Wave 2 creates Document and Event entities that reference Person via foreign keys. Wave 3 builds task assignment on top of Person.

## Request
Create the Person entity with full backend CRUD following Clean Architecture.

### 1. Database Migration
Create `apps/Server/database/create_person_table.sql`:
```sql
CREATE TABLE person (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    whatsapp VARCHAR(50),
    type VARCHAR(50) NOT NULL DEFAULT 'employee',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_person_restaurant ON person(restaurant_id);
CREATE INDEX idx_person_type ON person(type);
```
- role values: chef, mesero, dueño, proveedor, etc.
- type values: employee, supplier, owner

### 2. SQLAlchemy Model
Create `apps/Server/src/models/person_model.py`:
- `PersonModel` with all columns from migration

### 3. Pydantic DTOs
Create `apps/Server/src/interface/person_dto.py`:
```python
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class PersonType(str, Enum):
    EMPLOYEE = "employee"
    SUPPLIER = "supplier"
    OWNER = "owner"

class PersonCreateDTO(BaseModel):
    restaurant_id: UUID
    name: str = Field(..., max_length=255)
    role: str = Field(..., max_length=100)
    email: Optional[str] = None
    whatsapp: Optional[str] = None
    type: PersonType = PersonType.EMPLOYEE

class PersonUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    role: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = None
    whatsapp: Optional[str] = None
    type: Optional[PersonType] = None

class PersonResponseDTO(BaseModel):
    id: UUID
    restaurant_id: UUID
    name: str
    role: str
    email: Optional[str]
    whatsapp: Optional[str]
    type: str
    created_at: datetime
    updated_at: datetime
```

### 4. Repository
Create `apps/Server/src/repository/person_repository.py`:
- `create(data)` — insert person
- `get_by_id(person_id)` — get single person
- `get_by_restaurant(restaurant_id, type_filter=None)` — list with optional type filter
- `update(person_id, data)` — update person
- `delete(person_id)` — delete person
- `search(restaurant_id, query)` — search by name

### 5. Service
Create `apps/Server/src/core/services/person_service.py`:
- Wraps repository with business logic and logging
- All operations print INFO/ERROR logs

### 6. REST Routes
Create `apps/Server/src/adapter/rest/person_routes.py`:
- `GET /api/persons?restaurant_id={id}` — filtered list with optional `type` query param
- `POST /api/persons` — create person
- `GET /api/persons/{id}` — get person detail
- `PUT /api/persons/{id}` — update person
- `DELETE /api/persons/{id}` — delete person
- All endpoints require JWT authentication

### 7. Register Router
Add person router to `apps/Server/main.py`.

**UI Language:** N/A (backend only)
**Validation:** name and role are required. email should be validated if provided. whatsapp should accept international format.
```

---

### ROS-003: Resource Entity Data Model & CRUD

**Title:** `[RestaurantOS] Wave 1: Resource Entity Data Model & CRUD`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** Create the `resource` database table and full backend CRUD. A Resource represents any physical item: products (ingredients), assets (equipment), or services. Resources track current stock levels and minimum thresholds. When stock falls below the minimum, a low-stock alert Event is automatically created.

**Current Wave:** Wave 1 of 7 — Foundation Core Entities
**Current Issue:** ROS-003 (Issue 3 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-001 and ROS-002.

**Dependencies:** None
**What comes next:** Wave 2 creates Inventory Movement (ROS-006) that tracks stock changes for resources. Wave 4 builds recipe management referencing resources as ingredients.

## Request
Create the Resource entity with full backend CRUD and low-stock alert logic.

### 1. Database Migration
Create `apps/Server/database/create_resource_table.sql`:
```sql
CREATE TABLE resource (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'producto',
    name VARCHAR(255) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    current_stock DECIMAL(12,4) NOT NULL DEFAULT 0,
    minimum_stock DECIMAL(12,4) NOT NULL DEFAULT 0,
    last_unit_cost DECIMAL(12,4) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_resource_restaurant ON resource(restaurant_id);
CREATE INDEX idx_resource_type ON resource(type);
```
- type values: producto, activo, servicio
- unit values: kg, litros, unidades, etc.

### 2. SQLAlchemy Model
Create `apps/Server/src/models/resource_model.py`:
- `ResourceModel` with all columns

### 3. Pydantic DTOs
Create `apps/Server/src/interface/resource_dto.py`:
```python
from enum import Enum

class ResourceType(str, Enum):
    PRODUCTO = "producto"
    ACTIVO = "activo"
    SERVICIO = "servicio"

class ResourceCreateDTO(BaseModel):
    restaurant_id: UUID
    type: ResourceType = ResourceType.PRODUCTO
    name: str = Field(..., max_length=255)
    unit: str = Field(..., max_length=50)
    current_stock: Decimal = Decimal("0")
    minimum_stock: Decimal = Decimal("0")
    last_unit_cost: Decimal = Decimal("0")

class ResourceResponseDTO(BaseModel):
    id: UUID
    restaurant_id: UUID
    type: str
    name: str
    unit: str
    current_stock: Decimal
    minimum_stock: Decimal
    last_unit_cost: Decimal
    is_low_stock: bool  # calculated: current_stock < minimum_stock
    created_at: datetime
    updated_at: datetime
```

### 4. Repository
Create `apps/Server/src/repository/resource_repository.py`:
- `create(data)` — insert resource
- `get_by_id(resource_id)` — get single resource
- `get_by_restaurant(restaurant_id, type_filter=None)` — list with optional type filter
- `update(resource_id, data)` — update resource
- `delete(resource_id)` — delete resource
- `get_low_stock(restaurant_id)` — resources where current_stock < minimum_stock

### 5. Service
Create `apps/Server/src/core/services/resource_service.py`:
- Business logic with low-stock detection
- When stock drops below minimum after any update, log a warning (Event creation will be wired in Wave 2 when Event entity exists)

### 6. REST Routes
Create `apps/Server/src/adapter/rest/resource_routes.py`:
- `GET /api/resources?restaurant_id={id}` — filtered list with optional `type` query param
- `POST /api/resources` — create resource
- `GET /api/resources/{id}` — get resource detail
- `PUT /api/resources/{id}` — update resource
- `DELETE /api/resources/{id}` — delete resource
- All endpoints require JWT authentication

### 7. Register Router
Add resource router to `apps/Server/main.py`.

**UI Language:** N/A (backend only)
**Validation:** name and unit are required. current_stock and minimum_stock must be >= 0. last_unit_cost must be >= 0.
```

---

## Wave 2: Foundation Extended Entities (Run in Parallel)

With Person and Resource in place, this wave creates Document, Event, and Inventory Movement. These three depend on Wave 1 entities but not on each other, so they run in parallel.

### ROS-004: Document Entity Data Model & CRUD

**Title:** `[RestaurantOS] Wave 2: Document Entity Data Model & CRUD`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** Create the `document` table and full backend CRUD. A Document represents any legal or administrative artifact: contracts, permits, invoices, licenses. Documents can be linked to a person and have expiration dates. File upload support is required. When a document with an expiration date is created, the system should prepare for expiration alert automation (wired in later waves).

**Current Wave:** Wave 2 of 7 — Foundation Extended Entities
**Current Issue:** ROS-004 (Issue 4 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-005 and ROS-006.

**Dependencies:** ROS-002 (Person entity for person_id FK)
**What comes next:** Wave 4 builds the Document Management frontend page. Wave 6 adds document expiration alert automation.

## Request
Create the Document entity with full backend CRUD and file upload support.

### 1. Database Migration
Create `apps/Server/database/create_document_table.sql`:
```sql
CREATE TABLE document (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL,
    type VARCHAR(100) NOT NULL,
    file_url TEXT,
    issue_date DATE,
    expiration_date DATE,
    person_id UUID REFERENCES person(id) ON DELETE SET NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_document_restaurant ON document(restaurant_id);
CREATE INDEX idx_document_type ON document(type);
CREATE INDEX idx_document_expiration ON document(expiration_date);
CREATE INDEX idx_document_person ON document(person_id);
```
- type values: contrato, permiso, factura, licencia, factura_proveedor, etc.

### 2. SQLAlchemy Model
Create `apps/Server/src/models/document_model.py`:
- `DocumentModel` with all columns

### 3. Pydantic DTOs
Create `apps/Server/src/interface/document_dto.py`:
```python
class DocumentCreateDTO(BaseModel):
    restaurant_id: UUID
    type: str = Field(..., max_length=100)
    issue_date: Optional[date] = None
    expiration_date: Optional[date] = None
    person_id: Optional[UUID] = None
    description: Optional[str] = None

class DocumentResponseDTO(BaseModel):
    id: UUID
    restaurant_id: UUID
    type: str
    file_url: Optional[str]
    issue_date: Optional[date]
    expiration_date: Optional[date]
    person_id: Optional[UUID]
    description: Optional[str]
    expiration_status: str  # calculated: valid, expiring_soon, expired
    created_at: datetime
    updated_at: datetime
```

### 4. Repository
Create `apps/Server/src/repository/document_repository.py`:
- `create(data, file_url=None)` — insert document
- `get_by_id(document_id)` — get single document
- `get_by_restaurant(restaurant_id, type_filter=None)` — list with optional filters
- `update(document_id, data)` — update document metadata
- `delete(document_id)` — delete document
- `get_expiring(restaurant_id, days_ahead=30)` — documents expiring within N days

### 5. Service
Create `apps/Server/src/core/services/document_service.py`:
- Business logic with expiration status calculation
- `expiration_status`: "valid" (> 30 days), "expiring_soon" (≤ 30 days), "expired" (past date)
- File upload handling (store file, get URL)

### 6. REST Routes
Create `apps/Server/src/adapter/rest/document_routes.py`:
- `GET /api/documents?restaurant_id={id}` — list with optional type and expiration_status filters
- `POST /api/documents` — create document with file upload (multipart/form-data)
- `GET /api/documents/{id}` — get document detail
- `PUT /api/documents/{id}` — update document metadata
- `DELETE /api/documents/{id}` — delete document
- All endpoints require JWT authentication

### 7. Register Router
Add document router to `apps/Server/main.py`.

**UI Language:** N/A (backend only)
**Validation:** type is required. expiration_date must be after issue_date if both provided. File upload max size should be configurable (default 10MB).
```

---

### ROS-005: Event Entity Data Model & CRUD

**Title:** `[RestaurantOS] Wave 2: Event Entity Data Model & CRUD`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** Create the `event` table and full backend CRUD. Event is the system's nervous system — it represents tasks, deadlines, payments, shifts, checklists, and alerts. Events can be recurring (daily, weekly, monthly, yearly) and auto-generate individual instances. Each event has a responsible person and a notification channel preference.

**Current Wave:** Wave 2 of 7 — Foundation Extended Entities
**Current Issue:** ROS-005 (Issue 5 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-004 and ROS-006.

**Dependencies:** ROS-002 (Person entity for responsible_id FK)
**What comes next:** Wave 3 builds task assignment and recurrence on top of Event. Wave 5 wires notification sending for due events.

## Request
Create the Event entity with full backend CRUD and recurring event instance generation.

### 1. Database Migration
Create `apps/Server/database/create_event_table.sql`:
```sql
CREATE TABLE event (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL,
    type VARCHAR(100) NOT NULL,
    description TEXT,
    date TIMESTAMP NOT NULL,
    frequency VARCHAR(50) NOT NULL DEFAULT 'none',
    responsible_id UUID REFERENCES person(id) ON DELETE SET NULL,
    notification_channel VARCHAR(50) DEFAULT 'email',
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    related_document_id UUID,
    parent_event_id UUID REFERENCES event(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_event_restaurant ON event(restaurant_id);
CREATE INDEX idx_event_type ON event(type);
CREATE INDEX idx_event_date ON event(date);
CREATE INDEX idx_event_status ON event(status);
CREATE INDEX idx_event_responsible ON event(responsible_id);
CREATE INDEX idx_event_parent ON event(parent_event_id);
```
- type values: tarea, vencimiento, pago, turno, checklist, alerta_stock, alerta_rentabilidad
- frequency values: none, daily, weekly, monthly, yearly
- notification_channel values: email, push, whatsapp
- status values: pending, completed, overdue
- parent_event_id links generated instances to their recurring parent

### 2. SQLAlchemy Model
Create `apps/Server/src/models/event_model.py`:
- `EventModel` with all columns

### 3. Pydantic DTOs
Create `apps/Server/src/interface/event_dto.py`:
```python
from enum import Enum

class EventType(str, Enum):
    TAREA = "tarea"
    VENCIMIENTO = "vencimiento"
    PAGO = "pago"
    TURNO = "turno"
    CHECKLIST = "checklist"
    ALERTA_STOCK = "alerta_stock"
    ALERTA_RENTABILIDAD = "alerta_rentabilidad"

class EventFrequency(str, Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class EventStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"

class EventCreateDTO(BaseModel):
    restaurant_id: UUID
    type: EventType
    description: Optional[str] = None
    date: datetime
    frequency: EventFrequency = EventFrequency.NONE
    responsible_id: Optional[UUID] = None
    notification_channel: str = "email"
    related_document_id: Optional[UUID] = None

class EventResponseDTO(BaseModel):
    id: UUID
    restaurant_id: UUID
    type: str
    description: Optional[str]
    date: datetime
    frequency: str
    responsible_id: Optional[UUID]
    notification_channel: str
    status: str
    related_document_id: Optional[UUID]
    parent_event_id: Optional[UUID]
    is_overdue: bool  # calculated: status=pending and date < now
    created_at: datetime
    updated_at: datetime
```

### 4. Repository
Create `apps/Server/src/repository/event_repository.py`:
- `create(data)` — insert event
- `get_by_id(event_id)` — get single event
- `get_by_restaurant(restaurant_id, filters)` — list with optional type, status, date_range, responsible_id filters
- `update(event_id, data)` — update event
- `update_status(event_id, status)` — update just the status field
- `delete(event_id)` — delete event
- `get_due_events(restaurant_id, date)` — events due on a specific date
- `bulk_create(events)` — for generating recurring instances

### 5. Service
Create `apps/Server/src/core/services/event_service.py`:
- Business logic with recurring event generation
- `generate_recurring_instances(event_id, days_ahead=7)` — for recurring events, generate individual instances for the upcoming period
- Each generated instance has parent_event_id pointing to the recurring event
- Overdue detection: events with status=pending and date < now are flagged

### 6. REST Routes
Create `apps/Server/src/adapter/rest/event_routes.py`:
- `GET /api/events?restaurant_id={id}` — list with optional type, status, date_from, date_to, responsible_id filters
- `POST /api/events` — create event (auto-generates recurring instances if frequency != none)
- `GET /api/events/{id}` — get event detail
- `PUT /api/events/{id}` — update event
- `PATCH /api/events/{id}/status` — update status (pending → completed)
- `DELETE /api/events/{id}` — delete event
- All endpoints require JWT authentication

### 7. Register Router
Add event router to `apps/Server/main.py`.

**UI Language:** N/A (backend only)
**Validation:** type and date are required. If frequency != none, responsible_id should be provided. Status transitions: pending → completed, pending → overdue (system-managed).
```

---

### ROS-006: Inventory Movement Tracking

**Title:** `[RestaurantOS] Wave 2: Inventory Movement Tracking`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** Create the `inventory_movement` table and API for tracking all stock changes. Each movement records a resource, type (entry/exit), quantity, reason, and the person who performed it. Every movement automatically updates the resource's current_stock. Negative stock is prevented.

**Current Wave:** Wave 2 of 7 — Foundation Extended Entities
**Current Issue:** ROS-006 (Issue 6 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-004 and ROS-005.

**Dependencies:** ROS-003 (Resource entity), ROS-002 (Person entity)
**What comes next:** Wave 4 builds the frontend Resource & Inventory page. Wave 6 adds recipe-based inventory deduction and invoice OCR auto-entry.

## Request
Create the Inventory Movement tracking system with automatic stock updates.

### 1. Database Migration
Create `apps/Server/database/create_inventory_movement_table.sql`:
```sql
CREATE TABLE inventory_movement (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource_id UUID NOT NULL REFERENCES resource(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL,
    quantity DECIMAL(12,4) NOT NULL,
    reason VARCHAR(100) NOT NULL,
    date TIMESTAMP NOT NULL DEFAULT NOW(),
    person_id UUID REFERENCES person(id) ON DELETE SET NULL,
    restaurant_id UUID NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_inv_movement_resource ON inventory_movement(resource_id);
CREATE INDEX idx_inv_movement_restaurant ON inventory_movement(restaurant_id);
CREATE INDEX idx_inv_movement_date ON inventory_movement(date);
```
- type values: entry, exit
- reason values: compra, uso, produccion, merma, receta, ajuste

### 2. SQLAlchemy Model
Create `apps/Server/src/models/inventory_movement_model.py`:
- `InventoryMovementModel` with all columns

### 3. Pydantic DTOs
Create `apps/Server/src/interface/inventory_movement_dto.py`:
```python
from enum import Enum

class MovementType(str, Enum):
    ENTRY = "entry"
    EXIT = "exit"

class MovementReason(str, Enum):
    COMPRA = "compra"
    USO = "uso"
    PRODUCCION = "produccion"
    MERMA = "merma"
    RECETA = "receta"
    AJUSTE = "ajuste"

class InventoryMovementCreateDTO(BaseModel):
    resource_id: UUID
    type: MovementType
    quantity: Decimal = Field(..., gt=0)
    reason: MovementReason
    date: Optional[datetime] = None
    person_id: Optional[UUID] = None
    restaurant_id: UUID
    notes: Optional[str] = None
```

### 4. Repository
Create `apps/Server/src/repository/inventory_movement_repository.py`:
- `create(data)` — insert movement
- `get_by_resource(resource_id, date_from=None, date_to=None)` — movement history for a resource
- `get_by_restaurant(restaurant_id, filters)` — all movements with optional date range and reason filters

### 5. Service
Create `apps/Server/src/core/services/inventory_service.py`:
- `create_movement(data)`:
  1. Validate resource exists
  2. For exit movements: check current_stock >= quantity (prevent negative stock)
  3. Create movement record
  4. Update resource.current_stock: increment for entry, decrement for exit
  5. Check if resource is now below minimum_stock → log warning (Event creation for low-stock alerts will be wired when both Event and Resource services are available)
- All operations with INFO/ERROR logging

### 6. REST Routes
Create `apps/Server/src/adapter/rest/inventory_movement_routes.py`:
- `POST /api/inventory-movements` — create movement and update stock
- `GET /api/inventory-movements?resource_id={id}` — movement history for a resource
- `GET /api/inventory-movements?restaurant_id={id}` — all movements with optional date_from, date_to, reason filters
- All endpoints require JWT authentication

### 7. Register Router
Add inventory movement router to `apps/Server/main.py`.

**UI Language:** N/A (backend only)
**Validation:** quantity must be > 0. Exit quantity cannot exceed resource's current_stock. resource_id must reference a valid resource.
```

---

## Wave 3: Task Engine & Frontend Shell (Run in Parallel)

With all backend entities in place, this wave builds the task assignment layer on top of Events and creates the restaurant selector/navigation shell for the frontend. These are independent and run in parallel.

### ROS-007: Task Assignment with Recurrence

**Title:** `[RestaurantOS] Wave 3: Task Assignment with Recurrence`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** Build a task management layer on top of the Event entity. Tasks are Events with type="tarea". A manager can create a task, assign it to a person, set a date and frequency, and add a description. Recurring tasks auto-generate daily event instances. Tasks can be marked completed individually. Overdue detection flags past-due tasks.

**Current Wave:** Wave 3 of 7 — Task Engine & Frontend Shell
**Current Issue:** ROS-007 (Issue 7 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-008.

**Dependencies:** ROS-005 (Event entity), ROS-002 (Person entity)
**What comes next:** Wave 4 creates the daily task summary service (ROS-009) and the Event/Task frontend page (ROS-012).

## Request
Extend the Event service with task-specific functionality including recurrence and overdue detection.

### 1. Task Creation Enhancement
In `apps/Server/src/core/services/event_service.py`, add or enhance:
```python
async def create_task(self, data: EventCreateDTO) -> EventResponseDTO:
    """Create a task (Event with type=tarea) and generate recurring instances"""
    print(f"INFO [EventService]: Creating task for person {data.responsible_id}")

    # Force type to tarea
    data.type = EventType.TAREA

    # Create the parent/master event
    event = await self.event_repository.create(data)

    # Generate recurring instances if frequency is set
    if data.frequency != EventFrequency.NONE:
        instances = self._generate_instances(event, days_ahead=7)
        if instances:
            await self.event_repository.bulk_create(instances)
            print(f"INFO [EventService]: Generated {len(instances)} recurring instances")

    return event
```

### 2. Recurring Instance Generation
Add method to event service:
```python
def _generate_instances(self, parent_event: dict, days_ahead: int = 7) -> list:
    """Generate individual event instances for recurring events"""
    instances = []
    current_date = parent_event["date"]
    end_date = datetime.utcnow() + timedelta(days=days_ahead)

    while current_date <= end_date:
        instances.append({
            "restaurant_id": parent_event["restaurant_id"],
            "type": parent_event["type"],
            "description": parent_event["description"],
            "date": current_date,
            "frequency": "none",  # instances are non-recurring
            "responsible_id": parent_event["responsible_id"],
            "notification_channel": parent_event["notification_channel"],
            "status": "pending",
            "parent_event_id": parent_event["id"],
        })
        current_date = self._next_occurrence(current_date, parent_event["frequency"])

    return instances
```

### 3. Task Query Endpoint
Add to `apps/Server/src/adapter/rest/event_routes.py`:
```python
@router.get("/api/events/tasks")
async def get_tasks(
    restaurant_id: UUID,
    responsible_id: Optional[UUID] = None,
    date: Optional[str] = None,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get tasks (events of type=tarea) with filtering"""
    print(f"INFO [EventRoutes]: Fetching tasks for restaurant {restaurant_id}")
    return await event_service.get_tasks(restaurant_id, responsible_id, date, status)
```

### 4. Overdue Detection
Add a method to event service that flags events as overdue:
```python
async def flag_overdue_events(self, restaurant_id: UUID) -> int:
    """Mark past-due pending events as overdue"""
    count = await self.event_repository.update_overdue(restaurant_id, datetime.utcnow())
    print(f"INFO [EventService]: Flagged {count} overdue events for restaurant {restaurant_id}")
    return count
```

### 5. Task Completion
Ensure `PATCH /api/events/{id}/status` works for completing tasks:
- Validate status transition: pending → completed
- Update completed_at timestamp
- Log completion

**UI Language:** N/A (backend only)
**Validation:** Tasks require a responsible_id. Frequency must be a valid EventFrequency. Date must not be in the past for new tasks.
```

---

### ROS-008: Restaurant Selector & Multi-Tenant Navigation

**Title:** `[RestaurantOS] Wave 3: Restaurant Selector & Multi-Tenant Navigation`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** Add restaurant selection to the application shell. Users who belong to multiple restaurants can switch between them. All data views filter by the currently selected restaurant. This mirrors the existing EntityContext pattern in the Finance Tracker. The sidebar navigation is updated to include restaurant-specific sections.

**Current Wave:** Wave 3 of 7 — Task Engine & Frontend Shell
**Current Issue:** ROS-008 (Issue 8 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-007.

**Dependencies:** ROS-001 (Restaurant entity backend API)
**What comes next:** Wave 4 builds all frontend entity management pages that use this RestaurantContext for data scoping.

## Request
Create the RestaurantContext, restaurant selector UI, and updated sidebar navigation.

### 1. TypeScript Types
Create `apps/Client/src/types/restaurant.ts`:
```typescript
export interface Restaurant {
  id: string;
  name: string;
  address?: string;
  owner_id: string;
  created_at: string;
  updated_at: string;
}
```

### 2. Restaurant Service
Create `apps/Client/src/services/restaurantService.ts`:
```typescript
import { apiClient } from '@/api/clients/apiClient';
import { Restaurant } from '@/types/restaurant';

export const restaurantService = {
  getAll: async (): Promise<Restaurant[]> => {
    console.log('INFO [RestaurantService]: Fetching restaurants for user');
    const response = await apiClient.get('/restaurants');
    return response.data;
  },
  getById: async (id: string): Promise<Restaurant> => {
    const response = await apiClient.get(`/restaurants/${id}`);
    return response.data;
  },
  create: async (data: Partial<Restaurant>): Promise<Restaurant> => {
    const response = await apiClient.post('/restaurants', data);
    return response.data;
  },
};
```

### 3. RestaurantContext
Create `apps/Client/src/contexts/RestaurantContext.tsx`:
- Follows the same pattern as existing EntityContext
- Provides: `currentRestaurant`, `restaurants`, `switchRestaurant`, `loading`
- Persists selected restaurant in localStorage
- Loads restaurants on auth

### 4. Restaurant Selector Component
Create `apps/Client/src/components/layout/TRRestaurantSelector.tsx`:
- Dropdown/select in the top navbar showing current restaurant name
- List of user's restaurants to switch between
- Shows restaurant name prominently

### 5. Updated Sidebar Navigation
Update `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`:
- Add new navigation items under a "Restaurante" section:
  - Dashboard (existing)
  - Personas (links to PersonsPage)
  - Documentos (links to DocumentsPage)
  - Eventos / Tareas (links to EventsPage)
  - Recursos / Inventario (links to ResourcesPage)
- Keep existing Finance Tracker navigation sections

### 6. Route Registration
Update `apps/Client/src/App.tsx`:
- Add routes for new pages (the pages themselves will be built in Wave 4):
  - `/restaurant/persons` → PersonsPage
  - `/restaurant/documents` → DocumentsPage
  - `/restaurant/events` → EventsPage
  - `/restaurant/resources` → ResourcesPage
- Wrap restaurant routes in RestaurantContext provider
- Create placeholder pages that show "Coming Soon" until Wave 4 completes

### 7. Context Provider Integration
Wrap the restaurant module routes with RestaurantContext.Provider in `App.tsx`.

**UI Language:** Spanish (Colombian). Sidebar labels: "Personas", "Documentos", "Eventos / Tareas", "Recursos / Inventario". Selector label: "Restaurante".
**Validation:** User must have at least one restaurant. If no restaurant exists, show a prompt to create one.
```

---

## Wave 4: Daily Tasks & Frontend Entity Pages (Run in Parallel)

This wave builds the daily task summary service and all four frontend entity management pages. All items depend only on Wave 1-3 outputs and have no intra-wave dependencies.

### ROS-009: Daily Employee Task Summary

**Title:** `[RestaurantOS] Wave 4: Daily Employee Task Summary`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** Build a service that generates a daily summary of tasks for each employee. This summary aggregates all pending Events of type="tarea" for a given person and date. The summary is used by the notification system (Wave 5) to send each person their task list for the day via WhatsApp or email.

**Current Wave:** Wave 4 of 7 — Daily Tasks & Frontend Entity Pages
**Current Issue:** ROS-009 (Issue 9 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-010, ROS-011, ROS-012, ROS-013.

**Dependencies:** ROS-007 (Task Assignment with Recurrence)
**What comes next:** Wave 5 uses this summary to send WhatsApp/email notifications to employees each morning.

## Request
Create a daily task summary service and API endpoint.

### 1. Summary Service Method
Add to `apps/Server/src/core/services/event_service.py`:
```python
async def get_daily_task_summary(self, person_id: UUID, date: date) -> dict:
    """Get all pending tasks for a person on a specific date"""
    print(f"INFO [EventService]: Generating daily summary for person {person_id} on {date}")

    tasks = await self.event_repository.get_by_restaurant(
        restaurant_id=None,  # filter by person instead
        filters={
            "type": "tarea",
            "responsible_id": person_id,
            "date_from": datetime.combine(date, time.min),
            "date_to": datetime.combine(date, time.max),
            "status": ["pending", "overdue"],
        }
    )

    summary = {
        "person_id": str(person_id),
        "date": str(date),
        "total_tasks": len(tasks),
        "overdue_count": sum(1 for t in tasks if t.get("status") == "overdue"),
        "tasks": [
            {
                "id": str(t["id"]),
                "description": t.get("description", ""),
                "time": t.get("date").strftime("%H:%M") if t.get("date") else None,
                "status": t["status"],
                "is_overdue": t.get("status") == "overdue",
            }
            for t in tasks
        ]
    }

    print(f"INFO [EventService]: Summary for person {person_id}: {summary['total_tasks']} tasks, {summary['overdue_count']} overdue")
    return summary
```

### 2. Summary DTO
Add to `apps/Server/src/interface/event_dto.py`:
```python
class TaskSummaryItemDTO(BaseModel):
    id: UUID
    description: str
    time: Optional[str]
    status: str
    is_overdue: bool

class DailyTaskSummaryDTO(BaseModel):
    person_id: UUID
    date: date
    total_tasks: int
    overdue_count: int
    tasks: list[TaskSummaryItemDTO]
```

### 3. REST Endpoint
Add to `apps/Server/src/adapter/rest/event_routes.py`:
```python
@router.get("/api/persons/{person_id}/daily-tasks")
async def get_daily_tasks(
    person_id: UUID,
    date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get daily task summary for a person"""
    target_date = datetime.strptime(date, "%Y-%m-%d").date() if date else datetime.utcnow().date()
    summary = await event_service.get_daily_task_summary(person_id, target_date)
    return summary
```

### 4. Batch Summary for All Employees
Add method for generating summaries for all employees in a restaurant (used by notification cron):
```python
async def get_all_daily_summaries(self, restaurant_id: UUID, date: date) -> list[dict]:
    """Get daily task summaries for all persons in a restaurant"""
    persons = await self.person_repository.get_by_restaurant(restaurant_id, type_filter="employee")
    summaries = []
    for person in persons:
        summary = await self.get_daily_task_summary(person["id"], date)
        if summary["total_tasks"] > 0:
            summaries.append(summary)
    return summaries
```

**UI Language:** N/A (backend only)
**Validation:** date parameter must be a valid date string (YYYY-MM-DD). person_id must reference a valid person.
```

---

### ROS-010: Person Management Page

**Title:** `[RestaurantOS] Wave 4: Person Management Page`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** Create a frontend page for listing, creating, editing, and deleting persons (employees, suppliers, owners). The page uses a data table with search/filter capabilities. Forms use react-hook-form with MUI. All components use the TR prefix.

**Current Wave:** Wave 4 of 7 — Daily Tasks & Frontend Entity Pages
**Current Issue:** ROS-010 (Issue 10 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-009, ROS-011, ROS-012, ROS-013.

**Dependencies:** ROS-002 (Person backend API), ROS-008 (RestaurantContext and navigation)
**What comes next:** Person data is used in Document, Event, and Inventory forms for person selection dropdowns.

## Request
Build the Person Management frontend page with CRUD operations.

### 1. Person Service
Create `apps/Client/src/services/personService.ts`:
```typescript
import { apiClient } from '@/api/clients/apiClient';

export interface Person {
  id: string;
  restaurant_id: string;
  name: string;
  role: string;
  email?: string;
  whatsapp?: string;
  type: 'employee' | 'supplier' | 'owner';
  created_at: string;
  updated_at: string;
}

export const personService = {
  getAll: async (restaurantId: string, type?: string): Promise<Person[]> => {
    console.log(`INFO [PersonService]: Fetching persons for restaurant ${restaurantId}`);
    const params = new URLSearchParams({ restaurant_id: restaurantId });
    if (type) params.append('type', type);
    const response = await apiClient.get(`/persons?${params}`);
    return response.data;
  },
  create: async (data: Partial<Person>): Promise<Person> => {
    const response = await apiClient.post('/persons', data);
    return response.data;
  },
  update: async (id: string, data: Partial<Person>): Promise<Person> => {
    const response = await apiClient.put(`/persons/${id}`, data);
    return response.data;
  },
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/persons/${id}`);
  },
};
```

### 2. Person Types
Create `apps/Client/src/types/person.ts`:
- Export `Person` interface and `PersonType` type

### 3. TRPersonForm Component
Create `apps/Client/src/components/forms/TRPersonForm.tsx`:
- Use react-hook-form with MUI fields
- Fields: name (required), role (required), email (optional), whatsapp (optional), type (select: Empleado/Proveedor/Dueño)
- Validation: name max 255 chars, email format if provided
- Mode: create and edit (pre-populate for edit)

### 4. PersonsPage
Create `apps/Client/src/pages/PersonsPage.tsx`:
- Data table showing all persons for current restaurant (from RestaurantContext)
- Columns: Nombre, Rol, Tipo, Email, WhatsApp, Acciones
- Filter by type (dropdown: Todos, Empleados, Proveedores, Dueños)
- Search by name (text input)
- Add button opens TRPersonForm dialog
- Edit button on each row opens TRPersonForm with pre-filled data
- Delete button with confirmation dialog
- Loading and empty states

### 5. Route Registration
Update `apps/Client/src/App.tsx`:
- Replace placeholder for `/restaurant/persons` with PersonsPage

**UI Language:** Spanish (Colombian). Labels: "Personas", "Nombre", "Rol", "Tipo", "Correo Electrónico", "WhatsApp", "Agregar Persona", "Editar", "Eliminar". Type options: "Empleado", "Proveedor", "Dueño". Confirmation: "¿Está seguro que desea eliminar esta persona?"
**Validation:** name and role are required fields. email validated as email format.
```

---

### ROS-011: Document Management Page

**Title:** `[RestaurantOS] Wave 4: Document Management Page`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** Create a frontend page for uploading, listing, and managing documents. Documents display expiration status with color-coded indicators (green=valid, yellow=expiring soon, red=expired). File upload with drag-and-drop support. Filter by document type and expiration status.

**Current Wave:** Wave 4 of 7 — Daily Tasks & Frontend Entity Pages
**Current Issue:** ROS-011 (Issue 11 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-009, ROS-010, ROS-012, ROS-013.

**Dependencies:** ROS-004 (Document backend API), ROS-008 (RestaurantContext)
**What comes next:** Wave 6 adds document expiration alert automation that auto-creates Events.

## Request
Build the Document Management frontend page with file upload and expiration indicators.

### 1. Document Service
Create `apps/Client/src/services/documentService.ts`:
- `getAll(restaurantId, typeFilter?, statusFilter?)` — list documents
- `create(formData: FormData)` — create with file upload (multipart)
- `update(id, data)` — update metadata
- `delete(id)` — delete document
- `download(id)` — get download URL

### 2. Document Types
Create `apps/Client/src/types/document.ts`:
```typescript
export interface Document {
  id: string;
  restaurant_id: string;
  type: string;
  file_url?: string;
  issue_date?: string;
  expiration_date?: string;
  person_id?: string;
  description?: string;
  expiration_status: 'valid' | 'expiring_soon' | 'expired';
  created_at: string;
  updated_at: string;
}

export const DOCUMENT_TYPES = [
  'contrato', 'permiso', 'factura', 'licencia',
  'factura_proveedor', 'certificado', 'otro'
] as const;
```

### 3. TRDocumentForm Component
Create `apps/Client/src/components/forms/TRDocumentForm.tsx`:
- Use react-hook-form with MUI
- Fields: type (select from DOCUMENT_TYPES), issue_date, expiration_date, person_id (select from persons), description, file upload
- File upload area with drag-and-drop using MUI styled dropzone
- Mode: create and edit

### 4. TRExpirationBadge Component
Create `apps/Client/src/components/ui/TRExpirationBadge.tsx`:
- Color-coded chip: green ("Vigente"), yellow ("Por Vencer"), red ("Vencido")
- Based on expiration_status field

### 5. DocumentsPage
Create `apps/Client/src/pages/DocumentsPage.tsx`:
- Data table with columns: Tipo, Descripción, Persona, Fecha Emisión, Fecha Vencimiento, Estado, Acciones
- TRExpirationBadge in the Estado column
- Filters: type dropdown, expiration status dropdown
- Add button opens TRDocumentForm dialog
- Clicking a document row opens detail view with download link
- Delete with confirmation

### 6. Route Registration
Update route for `/restaurant/documents` with DocumentsPage.

**UI Language:** Spanish (Colombian). Labels: "Documentos", "Tipo", "Descripción", "Fecha de Emisión", "Fecha de Vencimiento", "Estado", "Subir Documento", "Agregar Documento". Status: "Vigente", "Por Vencer", "Vencido". Types: "Contrato", "Permiso", "Factura", "Licencia", "Factura Proveedor", "Certificado", "Otro".
**Validation:** type is required. expiration_date must be after issue_date. File size max 10MB.
```

---

### ROS-012: Event / Task Management Page

**Title:** `[RestaurantOS] Wave 4: Event / Task Management Page`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** Create a frontend page for viewing and managing events and tasks. Display as a list view grouped by date. Tasks can be filtered by responsible person, type, status, and date range. Quick-action button to mark tasks as completed. Overdue tasks are visually highlighted.

**Current Wave:** Wave 4 of 7 — Daily Tasks & Frontend Entity Pages
**Current Issue:** ROS-012 (Issue 12 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-009, ROS-010, ROS-011, ROS-013.

**Dependencies:** ROS-005 (Event backend API), ROS-007 (Task Assignment), ROS-008 (RestaurantContext)
**What comes next:** This page will be enhanced as notification features (Wave 5) and document expiration alerts (Wave 6) are added.

## Request
Build the Event/Task Management frontend page with list view and quick actions.

### 1. Event Service
Create `apps/Client/src/services/eventService.ts`:
- `getAll(restaurantId, filters?)` — list events with optional type, status, dateFrom, dateTo, responsibleId
- `create(data)` — create event/task
- `update(id, data)` — update event
- `updateStatus(id, status)` — mark as completed
- `delete(id)` — delete event
- `getDailyTasks(personId, date?)` — get daily task summary

### 2. Event Types
Create `apps/Client/src/types/event.ts`:
```typescript
export type EventType = 'tarea' | 'vencimiento' | 'pago' | 'turno' | 'checklist' | 'alerta_stock' | 'alerta_rentabilidad';
export type EventFrequency = 'none' | 'daily' | 'weekly' | 'monthly' | 'yearly';
export type EventStatus = 'pending' | 'completed' | 'overdue';

export interface Event {
  id: string;
  restaurant_id: string;
  type: EventType;
  description?: string;
  date: string;
  frequency: EventFrequency;
  responsible_id?: string;
  notification_channel: string;
  status: EventStatus;
  related_document_id?: string;
  is_overdue: boolean;
  created_at: string;
  updated_at: string;
}
```

### 3. TREventForm Component
Create `apps/Client/src/components/forms/TREventForm.tsx`:
- Fields: type (select), description, date (datetime picker), frequency (select), responsible_id (person selector), notification_channel (select: email/whatsapp/push)
- For type="tarea": show recurrence options and person assignment prominently
- Validation: date and type required, responsible_id required for tasks

### 4. TREventStatusBadge Component
Create `apps/Client/src/components/ui/TREventStatusBadge.tsx`:
- Chips: green ("Completado"), blue ("Pendiente"), red ("Vencido")

### 5. EventsPage
Create `apps/Client/src/pages/EventsPage.tsx`:
- List view grouped by date
- Columns: Fecha, Tipo, Descripción, Responsable, Estado, Acciones
- Overdue events highlighted with red background/border
- Filters: type dropdown, responsible person dropdown, status dropdown, date range picker
- Add button opens TREventForm dialog
- Quick-complete button (checkmark icon) on pending tasks
- Edit and delete actions

### 6. Route Registration
Update route for `/restaurant/events` with EventsPage.

**UI Language:** Spanish (Colombian). Labels: "Eventos / Tareas", "Fecha", "Tipo", "Descripción", "Responsable", "Estado", "Agregar Evento". Type options: "Tarea", "Vencimiento", "Pago", "Turno", "Checklist". Status: "Pendiente", "Completado", "Vencido". Frequency: "Sin repetición", "Diario", "Semanal", "Mensual", "Anual".
**Validation:** type and date are required. responsible_id required for type=tarea.
```

---

### ROS-013: Resource & Inventory Page

**Title:** `[RestaurantOS] Wave 4: Resource & Inventory Page`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** Create a frontend page for managing resources (products, assets, services) and recording inventory movements. Show current stock levels with low-stock indicators. Movement history viewable per resource in a detail drawer.

**Current Wave:** Wave 4 of 7 — Daily Tasks & Frontend Entity Pages
**Current Issue:** ROS-013 (Issue 13 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-009, ROS-010, ROS-011, ROS-012.

**Dependencies:** ROS-003 (Resource backend API), ROS-006 (Inventory Movement API), ROS-008 (RestaurantContext)
**What comes next:** Wave 6 adds recipe-based inventory deduction and invoice OCR that auto-create movements.

## Request
Build the Resource & Inventory Management frontend page with stock tracking.

### 1. Resource Service
Create `apps/Client/src/services/resourceService.ts`:
- `getAll(restaurantId, type?)` — list resources
- `create(data)` — create resource
- `update(id, data)` — update resource
- `delete(id)` — delete resource

### 2. Inventory Movement Service
Create `apps/Client/src/services/inventoryMovementService.ts`:
- `create(data)` — create movement (auto-updates stock)
- `getByResource(resourceId, dateFrom?, dateTo?)` — movement history
- `getAll(restaurantId, filters?)` — all movements

### 3. Resource & Movement Types
Create `apps/Client/src/types/resource.ts`:
```typescript
export type ResourceType = 'producto' | 'activo' | 'servicio';

export interface Resource {
  id: string;
  restaurant_id: string;
  type: ResourceType;
  name: string;
  unit: string;
  current_stock: number;
  minimum_stock: number;
  last_unit_cost: number;
  is_low_stock: boolean;
  created_at: string;
  updated_at: string;
}

export type MovementType = 'entry' | 'exit';
export type MovementReason = 'compra' | 'uso' | 'produccion' | 'merma' | 'receta' | 'ajuste';

export interface InventoryMovement {
  id: string;
  resource_id: string;
  type: MovementType;
  quantity: number;
  reason: MovementReason;
  date: string;
  person_id?: string;
  notes?: string;
  created_at: string;
}
```

### 4. TRResourceForm Component
Create `apps/Client/src/components/forms/TRResourceForm.tsx`:
- Fields: name, type (select: Producto/Activo/Servicio), unit (text), current_stock, minimum_stock, last_unit_cost
- Validation: name and unit required, stock values >= 0

### 5. TRInventoryMovementForm Component
Create `apps/Client/src/components/forms/TRInventoryMovementForm.tsx`:
- Fields: type (select: Entrada/Salida), quantity, reason (select: Compra/Uso/Producción/Merma/Ajuste), person_id (person selector), notes
- Validation: quantity > 0, show warning if exit would cause stock < 0

### 6. ResourcesPage
Create `apps/Client/src/pages/ResourcesPage.tsx`:
- Data table with columns: Nombre, Tipo, Unidad, Stock Actual, Stock Mínimo, Último Costo, Estado, Acciones
- Low-stock items (current_stock < minimum_stock) highlighted with red chip "Stock Bajo"
- Filter by type dropdown
- Add Resource button opens TRResourceForm dialog
- "Registrar Movimiento" button opens TRInventoryMovementForm
- Clicking a resource opens a detail drawer/panel showing:
  - Resource details
  - Movement history table (date, type, quantity, reason, person)

### 7. Route Registration
Update route for `/restaurant/resources` with ResourcesPage.

**UI Language:** Spanish (Colombian). Labels: "Recursos / Inventario", "Nombre", "Tipo", "Unidad", "Stock Actual", "Stock Mínimo", "Último Costo Unitario", "Agregar Recurso", "Registrar Movimiento". Type options: "Producto", "Activo", "Servicio". Movement types: "Entrada", "Salida". Reasons: "Compra", "Uso", "Producción", "Merma", "Ajuste". Status: "Stock Bajo".
**Validation:** name and unit required. Stock values must be >= 0. Movement quantity must be > 0.
```

---

## Wave 5: Notification System & Recipe Model (Run in Parallel)

This wave adds WhatsApp and email notification integrations and creates the recipe data model. These are independent: notifications build on Events/Tasks while recipes build on Resources.

### ROS-014: WhatsApp Notification Integration

**Title:** `[RestaurantOS] Wave 5: WhatsApp Notification Integration`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** Integrate with a WhatsApp Business API to send automated messages. The system sends: (1) daily task lists to each employee every morning, (2) document expiration alerts before due dates, (3) low-stock alerts. Messages are triggered by Events whose notification_channel includes "whatsapp". The specific WhatsApp provider (Twilio, Meta Cloud API, etc.) should be abstracted behind a service interface for swappability.

**Current Wave:** Wave 5 of 7 — Notification System & Recipe Model
**Current Issue:** ROS-014 (Issue 14 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-015 and ROS-016.

**Dependencies:** ROS-005 (Event entity), ROS-009 (Daily Task Summary)
**What comes next:** Wave 6 wires document expiration alerts to automatically trigger notifications.

## Request
Create the notification service with WhatsApp adapter and scheduled task triggers.

### 1. Notification Service Interface
Create `apps/Server/src/core/services/notification_service.py`:
```python
from abc import ABC, abstractmethod

class NotificationAdapter(ABC):
    @abstractmethod
    async def send(self, recipient: str, message: str) -> dict:
        """Send a notification and return delivery status"""
        pass

class NotificationService:
    def __init__(self, whatsapp_adapter: NotificationAdapter, email_adapter: NotificationAdapter = None):
        self.adapters = {
            "whatsapp": whatsapp_adapter,
            "email": email_adapter,
        }

    async def send_notification(self, channel: str, recipient: str, message: str) -> dict:
        adapter = self.adapters.get(channel)
        if not adapter:
            print(f"ERROR [NotificationService]: No adapter for channel {channel}")
            return {"status": "error", "reason": f"Unknown channel: {channel}"}

        try:
            result = await adapter.send(recipient, message)
            print(f"INFO [NotificationService]: Sent {channel} to {recipient}: {result['status']}")
            return result
        except Exception as e:
            print(f"ERROR [NotificationService]: Failed to send {channel} to {recipient}: {e}")
            # Retry once
            try:
                result = await adapter.send(recipient, message)
                return result
            except Exception as retry_e:
                print(f"ERROR [NotificationService]: Retry failed: {retry_e}")
                return {"status": "failed", "error": str(retry_e)}
```

### 2. WhatsApp Adapter
Create `apps/Server/src/adapter/whatsapp_adapter.py`:
```python
class WhatsAppAdapter(NotificationAdapter):
    def __init__(self, api_key: str, phone_number_id: str):
        self.api_key = api_key
        self.phone_number_id = phone_number_id

    async def send(self, recipient: str, message: str) -> dict:
        print(f"INFO [WhatsAppAdapter]: Sending message to {recipient}")
        # TODO: Implement actual API call to chosen provider (Twilio/Meta/etc.)
        # For now, log and return success for development
        print(f"INFO [WhatsAppAdapter]: Message sent to {recipient}: {message[:100]}...")
        return {"status": "sent", "recipient": recipient}
```

### 3. Daily Summary Notification Trigger
Create `apps/Server/src/core/services/notification_scheduler.py`:
```python
async def send_morning_task_summaries(restaurant_id: UUID):
    """Send daily task summaries to all employees via their preferred channel"""
    summaries = await event_service.get_all_daily_summaries(restaurant_id, date.today())

    for summary in summaries:
        person = await person_service.get_by_id(summary["person_id"])
        if not person or not person.get("whatsapp"):
            continue

        message = format_daily_tasks_message(summary)
        await notification_service.send_notification(
            channel="whatsapp",
            recipient=person["whatsapp"],
            message=message
        )
```

### 4. Message Formatter
Add message formatting functions:
```python
def format_daily_tasks_message(summary: dict) -> str:
    lines = [f"Buenos días! Estas son tus tareas para hoy ({summary['date']}):"]
    for i, task in enumerate(summary["tasks"], 1):
        status = "⚠️ ATRASADA" if task["is_overdue"] else "📋"
        time_str = f" ({task['time']})" if task.get("time") else ""
        lines.append(f"{i}. {status} {task['description']}{time_str}")
    lines.append(f"\nTotal: {summary['total_tasks']} tareas")
    if summary["overdue_count"] > 0:
        lines.append(f"⚠️ {summary['overdue_count']} tarea(s) atrasada(s)")
    return "\n".join(lines)
```

### 5. Notification Log Table
Create `apps/Server/database/create_notification_log_table.sql`:
```sql
CREATE TABLE notification_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL,
    channel VARCHAR(50) NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    message TEXT,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 6. API Endpoint for Manual Trigger
Add to REST routes:
- `POST /api/notifications/send-daily-summaries?restaurant_id={id}` — manually trigger daily summaries (for testing and cron job)

**UI Language:** Messages in Spanish (Colombian).
**Validation:** WhatsApp number must be in international format. Message length should respect WhatsApp limits.
```

---

### ROS-015: Email Notification Integration

**Title:** `[RestaurantOS] Wave 5: Email Notification Integration`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** Integrate email sending as a secondary notification channel. Same triggers as WhatsApp but for users who prefer email notifications. Email content is formatted as readable HTML. Uses the same NotificationService interface with a pluggable email adapter.

**Current Wave:** Wave 5 of 7 — Notification System & Recipe Model
**Current Issue:** ROS-015 (Issue 15 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-014 and ROS-016.

**Dependencies:** ROS-005 (Event entity), ROS-009 (Daily Task Summary)
**What comes next:** Wave 6 uses email notifications for document expiration alerts.

## Request
Create the email notification adapter and HTML email formatting.

### 1. Email Adapter
Create `apps/Server/src/adapter/email_adapter.py`:
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailAdapter(NotificationAdapter):
    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str, from_email: str):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email

    async def send(self, recipient: str, message: str) -> dict:
        print(f"INFO [EmailAdapter]: Sending email to {recipient}")
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Restaurant OS - Notificación"
            msg["From"] = self.from_email
            msg["To"] = recipient
            msg.attach(MIMEText(message, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            print(f"INFO [EmailAdapter]: Email sent to {recipient}")
            return {"status": "sent", "recipient": recipient}
        except Exception as e:
            print(f"ERROR [EmailAdapter]: Failed to send email to {recipient}: {e}")
            raise
```

### 2. HTML Email Templates
Create `apps/Server/src/adapter/email_templates.py`:
- `format_daily_tasks_html(summary)` — HTML table of tasks
- `format_expiration_alert_html(document, days_until)` — document expiration warning
- `format_low_stock_alert_html(resources)` — low stock resource list
- Clean, mobile-friendly HTML styling

### 3. Environment Variables
Add to `.env` and document:
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=app-password
SMTP_FROM_EMAIL=noreply@restaurant-os.com
```

### 4. Wire Email Adapter
In service initialization (or dependency injection), create and register the EmailAdapter with the NotificationService alongside the WhatsApp adapter.

### 5. Notification Channel Routing
Update NotificationService to route by event's `notification_channel` field:
- "email" → EmailAdapter
- "whatsapp" → WhatsAppAdapter
- "both" → send via both channels

**UI Language:** Email content in Spanish (Colombian).
**Validation:** Email address must be valid format. SMTP credentials must be configured for email to work.
```

---

### ROS-016: Recipe Data Model & CRUD

**Title:** `[RestaurantOS] Wave 5: Recipe Data Model & CRUD`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** Create `recipe` and `recipe_item` tables. A Recipe represents a menu dish with a sale price. Recipe_Item links a recipe to its ingredients (resources) with quantities. The recipe's cost is calculated as the sum of (ingredient quantity x resource last_unit_cost). Margin and profitability status are derived from cost vs sale price.

**Current Wave:** Wave 5 of 7 — Notification System & Recipe Model
**Current Issue:** ROS-016 (Issue 16 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-014 and ROS-015.

**Dependencies:** ROS-003 (Resource entity for ingredient references)
**What comes next:** Wave 6 adds invoice OCR auto-cost update, recipe-based inventory deduction, recipe frontend page, and automatic cost recalculation.

## Request
Create the Recipe entity with ingredient management and automatic cost/margin calculation.

### 1. Database Migration
Create `apps/Server/database/create_recipe_tables.sql`:
```sql
CREATE TABLE recipe (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restaurant_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    sale_price DECIMAL(12,2) NOT NULL,
    current_cost DECIMAL(12,2) NOT NULL DEFAULT 0,
    margin_percent DECIMAL(5,2) NOT NULL DEFAULT 0,
    is_profitable BOOLEAN NOT NULL DEFAULT true,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE recipe_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipe_id UUID NOT NULL REFERENCES recipe(id) ON DELETE CASCADE,
    resource_id UUID NOT NULL REFERENCES resource(id) ON DELETE RESTRICT,
    quantity DECIMAL(12,4) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_recipe_restaurant ON recipe(restaurant_id);
CREATE INDEX idx_recipe_item_recipe ON recipe_item(recipe_id);
CREATE INDEX idx_recipe_item_resource ON recipe_item(resource_id);
```

### 2. SQLAlchemy Models
Create `apps/Server/src/models/recipe_model.py`:
- `RecipeModel` and `RecipeItemModel`

### 3. Pydantic DTOs
Create `apps/Server/src/interface/recipe_dto.py`:
```python
class RecipeItemCreateDTO(BaseModel):
    resource_id: UUID
    quantity: Decimal = Field(..., gt=0)
    unit: str

class RecipeCreateDTO(BaseModel):
    restaurant_id: UUID
    name: str = Field(..., max_length=255)
    sale_price: Decimal = Field(..., gt=0)
    is_active: bool = True
    items: list[RecipeItemCreateDTO]

class RecipeResponseDTO(BaseModel):
    id: UUID
    restaurant_id: UUID
    name: str
    sale_price: Decimal
    current_cost: Decimal
    margin_percent: Decimal
    is_profitable: bool
    is_active: bool
    items: list[RecipeItemResponseDTO]
    created_at: datetime
    updated_at: datetime
```

### 4. Repository
Create `apps/Server/src/repository/recipe_repository.py`:
- `create(data, items)` — insert recipe and recipe_items
- `get_by_id(recipe_id)` — with items joined
- `get_by_restaurant(restaurant_id)` — list all recipes
- `update(recipe_id, data, items)` — update recipe and replace items
- `delete(recipe_id)` — delete recipe (cascades to items)
- `get_by_resource(resource_id)` — find recipes that use a specific resource

### 5. Service
Create `apps/Server/src/core/services/recipe_service.py`:
```python
async def calculate_cost(self, recipe_id: UUID) -> dict:
    """Calculate recipe cost from ingredient costs"""
    recipe = await self.recipe_repository.get_by_id(recipe_id)
    total_cost = Decimal("0")

    for item in recipe["items"]:
        resource = await self.resource_repository.get_by_id(item["resource_id"])
        item_cost = item["quantity"] * resource["last_unit_cost"]
        total_cost += item_cost

    margin = ((recipe["sale_price"] - total_cost) / recipe["sale_price"] * 100) if recipe["sale_price"] > 0 else 0
    is_profitable = margin >= 60  # default threshold

    await self.recipe_repository.update_cost(recipe_id, total_cost, margin, is_profitable)
    return {"current_cost": total_cost, "margin_percent": margin, "is_profitable": is_profitable}
```

### 6. REST Routes
Create `apps/Server/src/adapter/rest/recipe_routes.py`:
- `GET /api/recipes?restaurant_id={id}` — list recipes with calculated cost/margin
- `POST /api/recipes` — create recipe with ingredients (auto-calculates cost)
- `GET /api/recipes/{id}` — recipe detail with ingredient breakdown
- `PUT /api/recipes/{id}` — update recipe and ingredients
- `DELETE /api/recipes/{id}` — delete recipe
- `POST /api/recipes/{id}/recalculate` — force cost recalculation
- All endpoints require JWT authentication

### 7. Register Router
Add recipe router to `apps/Server/main.py`.

**UI Language:** N/A (backend only)
**Validation:** name and sale_price required. sale_price > 0. Each recipe must have at least one item. item quantity > 0. Profitability threshold default: 60% margin.
```

---

## Wave 6: Alerts, OCR & Recipe Features (Run in Parallel)

This wave adds document expiration alert automation, invoice OCR processing, recipe-based inventory deduction, and the recipe management frontend. All depend on earlier waves but not on each other.

### ROS-017: Document Expiration Alert Automation

**Title:** `[RestaurantOS] Wave 6: Document Expiration Alert Automation`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** When a document with an expiration date is created or updated, the system automatically creates Event records of type="vencimiento" with configurable advance alert periods. Default alerts: 30 days before, 7 days before, and day-of expiration. When the alert event date arrives, the notification system sends alerts via the configured channel.

**Current Wave:** Wave 6 of 7 — Alerts, OCR & Recipe Features
**Current Issue:** ROS-017 (Issue 17 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-018, ROS-019, ROS-020.

**Dependencies:** ROS-004 (Document entity), ROS-005 (Event entity), ROS-014 (WhatsApp notifications)
**What comes next:** Wave 7 adds permit type presets that customize alert schedules per document type.

## Request
Wire document creation/update to automatically create expiration alert Events.

### 1. Alert Event Creation
Update `apps/Server/src/core/services/document_service.py`:
```python
DEFAULT_ALERT_WINDOWS = [30, 7, 0]  # days before expiration

async def create_expiration_alerts(self, document_id: UUID, expiration_date: date, restaurant_id: UUID, person_id: UUID = None):
    """Create expiration alert events for a document"""
    print(f"INFO [DocumentService]: Creating expiration alerts for document {document_id}")

    for days_before in DEFAULT_ALERT_WINDOWS:
        alert_date = expiration_date - timedelta(days=days_before)
        if alert_date <= date.today():
            continue  # Skip past alerts

        event_data = EventCreateDTO(
            restaurant_id=restaurant_id,
            type=EventType.VENCIMIENTO,
            description=f"Documento vence en {days_before} días" if days_before > 0 else "Documento vence hoy",
            date=datetime.combine(alert_date, time(8, 0)),  # 8 AM
            frequency=EventFrequency.NONE,
            responsible_id=person_id,
            notification_channel="whatsapp",
            related_document_id=document_id,
        )
        await self.event_service.create(event_data)

    print(f"INFO [DocumentService]: Created {len(DEFAULT_ALERT_WINDOWS)} alert events for document {document_id}")
```

### 2. Hook into Document Create
When a document is created with an `expiration_date`, call `create_expiration_alerts()`.

### 3. Hook into Document Update
When a document's `expiration_date` is updated:
1. Delete existing expiration events for that document (related_document_id)
2. Create new expiration events with updated dates

### 4. Event Processing
Add to notification scheduler:
```python
async def process_due_events(restaurant_id: UUID):
    """Check for events due today and send notifications"""
    due_events = await event_service.get_due_events(restaurant_id, date.today())
    for event in due_events:
        if event["responsible_id"]:
            person = await person_service.get_by_id(event["responsible_id"])
            channel = event["notification_channel"]
            recipient = person.get("whatsapp") if channel == "whatsapp" else person.get("email")
            if recipient:
                await notification_service.send_notification(channel, recipient, event["description"])
```

### 5. Notification Scheduling Endpoint
Add `POST /api/notifications/process-due-events?restaurant_id={id}` for cron/manual trigger.

**UI Language:** Alert messages in Spanish (Colombian): "Documento vence en 30 días", "Documento vence en 7 días", "Documento vence hoy".
**Validation:** Alert events must have notification_channel set based on the responsible person's preference. Updating expiration_date must clean up old alerts before creating new ones.
```

---

### ROS-018: Invoice OCR & Automatic Cost Update

**Title:** `[RestaurantOS] Wave 6: Invoice OCR & Automatic Cost Update`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** When a supplier invoice document (type="factura_proveedor") is uploaded, use OCR/AI to extract line items: supplier name, product names, quantities, and unit prices. For each detected item, match to an existing Resource, update its last_unit_cost, and create an inventory entry movement. Unmatched items are flagged for manual review. The OCR service is abstracted behind an interface for provider swappability.

**Current Wave:** Wave 6 of 7 — Alerts, OCR & Recipe Features
**Current Issue:** ROS-018 (Issue 18 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-017, ROS-019, ROS-020.

**Dependencies:** ROS-004 (Document entity), ROS-003 (Resource entity), ROS-006 (Inventory Movement)
**What comes next:** Wave 7 adds automatic recipe cost recalculation triggered by resource cost updates from OCR.

## Request
Create the invoice OCR pipeline with resource matching and automatic inventory entry.

### 1. OCR Service Interface
Create `apps/Server/src/core/services/ocr_service.py`:
```python
from abc import ABC, abstractmethod

class OCRAdapter(ABC):
    @abstractmethod
    async def extract_invoice_items(self, file_url: str) -> list[dict]:
        """Extract line items from an invoice image/PDF"""
        pass

class InvoiceItem(BaseModel):
    product_name: str
    quantity: Decimal
    unit: str
    unit_price: Decimal
    supplier_name: Optional[str] = None

class OCRService:
    def __init__(self, adapter: OCRAdapter):
        self.adapter = adapter

    async def process_invoice(self, file_url: str) -> list[InvoiceItem]:
        print(f"INFO [OCRService]: Processing invoice from {file_url}")
        raw_items = await self.adapter.extract_invoice_items(file_url)
        return [InvoiceItem(**item) for item in raw_items]
```

### 2. Resource Matching Service
Create `apps/Server/src/core/services/invoice_processor.py`:
```python
class InvoiceProcessor:
    async def process_invoice_document(self, document_id: UUID) -> dict:
        """Process a supplier invoice: OCR → match resources → update costs → create movements"""
        document = await self.document_service.get_by_id(document_id)
        items = await self.ocr_service.process_invoice(document["file_url"])

        matched = []
        unmatched = []

        for item in items:
            resource = await self.resource_service.find_by_name(
                document["restaurant_id"], item.product_name
            )
            if resource:
                # Update resource cost
                await self.resource_service.update_cost(resource["id"], item.unit_price)
                # Create inventory entry movement
                await self.inventory_service.create_movement(InventoryMovementCreateDTO(
                    resource_id=resource["id"],
                    type=MovementType.ENTRY,
                    quantity=item.quantity,
                    reason=MovementReason.COMPRA,
                    restaurant_id=document["restaurant_id"],
                    notes=f"Auto-entry from invoice {document_id}",
                ))
                matched.append({"item": item, "resource_id": resource["id"]})
            else:
                unmatched.append(item)

        # Store processing results with document
        result = {"matched": len(matched), "unmatched": len(unmatched), "unmatched_items": unmatched}
        await self.document_service.update_processing_status(document_id, result)
        return result
```

### 3. Stub OCR Adapter
Create `apps/Server/src/adapter/ocr_stub_adapter.py`:
- Returns mock data for development/testing
- TODO comment for real OCR integration (Google Cloud Vision, AWS Textract, etc.)

### 4. Document Processing Trigger
Update document creation in `document_service.py`:
- When a document of type "factura_proveedor" is created with a file, trigger OCR processing asynchronously

### 5. Processing Status Fields
Add to document table/model:
- `processing_status` VARCHAR: 'pending', 'processing', 'completed', 'failed'
- `processing_result` JSONB: stores matched/unmatched details

### 6. REST Endpoint
Add to document routes:
- `POST /api/documents/{id}/process-invoice` — manually trigger OCR processing
- `GET /api/documents/{id}/processing-result` — get processing results with unmatched items

### 7. Resource Name Matching
Add to resource repository:
- `find_by_name(restaurant_id, name)` — fuzzy/exact match by name for resource lookup

**UI Language:** N/A (backend processing)
**Validation:** Only documents of type "factura_proveedor" can be processed. File must exist. Unmatched items must be returned for manual review.
```

---

### ROS-019: Recipe-Based Inventory Deduction

**Title:** `[RestaurantOS] Wave 6: Recipe-Based Inventory Deduction`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** When a dish is sold or produced, automatically deduct the corresponding ingredient quantities from inventory. Create inventory exit movements (type=exit, reason=receta) for each recipe item. Insufficient stock for any ingredient prevents the operation.

**Current Wave:** Wave 6 of 7 — Alerts, OCR & Recipe Features
**Current Issue:** ROS-019 (Issue 19 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-017, ROS-018, ROS-020.

**Dependencies:** ROS-016 (Recipe entity), ROS-006 (Inventory Movement)
**What comes next:** This enables tracking real vs. theoretical consumption and identifying waste/shrinkage.

## Request
Add recipe production endpoint that deducts ingredients from inventory.

### 1. Produce Endpoint
Add to `apps/Server/src/adapter/rest/recipe_routes.py`:
```python
@router.post("/api/recipes/{recipe_id}/produce")
async def produce_recipe(
    recipe_id: UUID,
    quantity: int = 1,
    current_user: dict = Depends(get_current_user)
):
    """Produce a recipe: deduct all ingredients from inventory"""
    print(f"INFO [RecipeRoutes]: Producing {quantity}x recipe {recipe_id}")
    result = await recipe_service.produce(recipe_id, quantity, current_user["id"])
    return result
```

### 2. Service Method
Add to `apps/Server/src/core/services/recipe_service.py`:
```python
async def produce(self, recipe_id: UUID, quantity: int, produced_by_id: str) -> dict:
    """Deduct recipe ingredients from inventory"""
    recipe = await self.recipe_repository.get_by_id(recipe_id)

    # Pre-check: verify all ingredients have sufficient stock
    for item in recipe["items"]:
        resource = await self.resource_repository.get_by_id(item["resource_id"])
        required = item["quantity"] * quantity
        if resource["current_stock"] < required:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para {resource['name']}: necesita {required} {item['unit']}, disponible {resource['current_stock']}"
            )

    # Deduct all ingredients
    movements = []
    for item in recipe["items"]:
        movement = await self.inventory_service.create_movement(InventoryMovementCreateDTO(
            resource_id=item["resource_id"],
            type=MovementType.EXIT,
            quantity=item["quantity"] * quantity,
            reason=MovementReason.RECETA,
            restaurant_id=recipe["restaurant_id"],
            notes=f"Producción: {recipe['name']} x{quantity}",
        ))
        movements.append(movement)

    print(f"INFO [RecipeService]: Produced {quantity}x {recipe['name']}, {len(movements)} ingredients deducted")
    return {"recipe_id": recipe_id, "quantity": quantity, "movements_created": len(movements)}
```

**UI Language:** Error messages in Spanish (Colombian): "Stock insuficiente para {nombre}: necesita {cantidad} {unidad}, disponible {stock}".
**Validation:** quantity must be >= 1. All ingredients must have sufficient stock before any deductions begin (atomic operation).
```

---

### ROS-020: Recipe Management Frontend

**Title:** `[RestaurantOS] Wave 6: Recipe Management Frontend`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** Create a frontend page for managing recipes — listing all dishes with their current cost, margin, and profitability status. Ability to add/edit recipes with ingredient selection from existing resources. Visual indicators for unprofitable dishes. Production action button to deduct ingredients.

**Current Wave:** Wave 6 of 7 — Alerts, OCR & Recipe Features
**Current Issue:** ROS-020 (Issue 20 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-017, ROS-018, ROS-019.

**Dependencies:** ROS-016 (Recipe backend API)
**What comes next:** Wave 7 adds automatic cost recalculation on ingredient price changes.

## Request
Build the Recipe Management frontend page.

### 1. Recipe Service
Create `apps/Client/src/services/recipeService.ts`:
- `getAll(restaurantId)` — list recipes with cost/margin
- `create(data)` — create recipe with ingredients
- `update(id, data)` — update recipe
- `delete(id)` — delete recipe
- `produce(id, quantity)` — trigger production/deduction
- `recalculate(id)` — force cost recalculation

### 2. Recipe Types
Create `apps/Client/src/types/recipe.ts`:
```typescript
export interface RecipeItem {
  id?: string;
  resource_id: string;
  resource_name?: string;
  quantity: number;
  unit: string;
  item_cost?: number;
}

export interface Recipe {
  id: string;
  restaurant_id: string;
  name: string;
  sale_price: number;
  current_cost: number;
  margin_percent: number;
  is_profitable: boolean;
  is_active: boolean;
  items: RecipeItem[];
  created_at: string;
  updated_at: string;
}
```

### 3. TRRecipeForm Component
Create `apps/Client/src/components/forms/TRRecipeForm.tsx`:
- Fields: name, sale_price, is_active toggle
- Dynamic ingredient rows: resource selector (from existing resources), quantity, unit
- "Agregar Ingrediente" button to add rows
- Remove ingredient button per row
- Show calculated cost and margin in real-time as ingredients are added

### 4. TRProfitabilityBadge Component
Create `apps/Client/src/components/ui/TRProfitabilityBadge.tsx`:
- Green chip: "Rentable" (margin >= 60%)
- Red chip: "No Rentable" (margin < 60%)
- Show margin percentage

### 5. RecipesPage
Create `apps/Client/src/pages/RecipesPage.tsx`:
- Data table: Nombre, Precio Venta, Costo Actual, Margen %, Rentabilidad, Estado, Acciones
- TRProfitabilityBadge in Rentabilidad column
- Unprofitable recipes visually highlighted
- Add Recipe button opens TRRecipeForm
- "Producir" button per recipe opens quantity dialog, then triggers produce API
- Click recipe row to see ingredient breakdown detail

### 6. Sidebar Navigation
Add "Recetas" to the restaurant section in sidebar navigation.

### 7. Route Registration
Add `/restaurant/recipes` → RecipesPage route.

**UI Language:** Spanish (Colombian). Labels: "Recetas", "Nombre", "Precio de Venta", "Costo Actual", "Margen %", "Rentabilidad", "Agregar Receta", "Agregar Ingrediente", "Producir". Status: "Rentable", "No Rentable". Production dialog: "¿Cuántas porciones producir?"
**Validation:** name and sale_price required. sale_price > 0. At least one ingredient required. Ingredient quantity > 0.
```

---

## Wave 7: Cost Intelligence & Compliance (Run in Parallel)

The final wave adds automatic recipe cost recalculation when ingredient prices change and permit type presets with custom alert schedules. These are independent features.

### ROS-021: Automatic Recipe Cost Recalculation

**Title:** `[RestaurantOS] Wave 7: Automatic Recipe Cost Recalculation`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** Whenever a resource's `last_unit_cost` changes (e.g., after invoice OCR processing), automatically recalculate the cost of all recipes that use that resource. Update the recipe's current_cost, margin_percent, and is_profitable fields. If any recipe becomes unprofitable (margin below threshold), trigger a profitability alert Event that notifies the restaurant owner.

**Current Wave:** Wave 7 of 7 — Cost Intelligence & Compliance
**Current Issue:** ROS-021 (Issue 21 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-022.

**Dependencies:** ROS-016 (Recipe entity), ROS-018 (Invoice OCR that triggers cost updates)
**What comes next:** This completes the cost intelligence loop: Invoice → OCR → Cost Update → Recipe Recalculation → Profitability Alert.

## Request
Wire resource cost changes to automatic recipe recalculation and profitability alerts.

### 1. Cost Change Hook
Update `apps/Server/src/core/services/resource_service.py`:
```python
async def update_cost(self, resource_id: UUID, new_cost: Decimal) -> dict:
    """Update resource cost and trigger recipe recalculation"""
    old_resource = await self.resource_repository.get_by_id(resource_id)
    old_cost = old_resource["last_unit_cost"]

    if new_cost != old_cost:
        await self.resource_repository.update(resource_id, {"last_unit_cost": new_cost})
        print(f"INFO [ResourceService]: Cost updated for resource {resource_id}: {old_cost} → {new_cost}")

        # Trigger recipe recalculation
        await self.recipe_service.recalculate_by_resource(resource_id)

    return {"resource_id": resource_id, "old_cost": old_cost, "new_cost": new_cost}
```

### 2. Batch Recipe Recalculation
Add to `apps/Server/src/core/services/recipe_service.py`:
```python
async def recalculate_by_resource(self, resource_id: UUID):
    """Recalculate all recipes that use a specific resource"""
    recipes = await self.recipe_repository.get_by_resource(resource_id)
    print(f"INFO [RecipeService]: Recalculating {len(recipes)} recipes affected by resource {resource_id}")

    for recipe in recipes:
        result = await self.calculate_cost(recipe["id"])

        # Check profitability
        if not result["is_profitable"]:
            print(f"WARNING [RecipeService]: Recipe '{recipe['name']}' is no longer profitable (margin: {result['margin_percent']}%)")
            await self._create_profitability_alert(recipe, result)

async def _create_profitability_alert(self, recipe: dict, cost_result: dict):
    """Create a profitability alert Event"""
    restaurant = await self.restaurant_repository.get_by_id(recipe["restaurant_id"])
    owner_person = await self.person_repository.find_owner(recipe["restaurant_id"])

    event_data = EventCreateDTO(
        restaurant_id=recipe["restaurant_id"],
        type=EventType.ALERTA_RENTABILIDAD,
        description=(
            f"Alerta de rentabilidad: {recipe['name']} - "
            f"Costo: ${cost_result['current_cost']}, "
            f"Precio venta: ${recipe['sale_price']}, "
            f"Margen: {cost_result['margin_percent']:.1f}%"
        ),
        date=datetime.utcnow(),
        frequency=EventFrequency.NONE,
        responsible_id=owner_person["id"] if owner_person else None,
        notification_channel="whatsapp",
    )
    await self.event_service.create(event_data)
    print(f"INFO [RecipeService]: Profitability alert created for recipe '{recipe['name']}'")
```

### 3. Person Repository: Find Owner
Add to `apps/Server/src/repository/person_repository.py`:
- `find_owner(restaurant_id)` — find person of type="owner" for a restaurant

### 4. Configurable Threshold
Add profitability threshold configuration:
```python
# In restaurant settings or environment
PROFITABILITY_THRESHOLD = float(os.getenv("PROFITABILITY_THRESHOLD", "60"))
```
- Default: 60% margin
- Used in `is_profitable` calculation

**UI Language:** Alert messages in Spanish (Colombian): "Alerta de rentabilidad: {nombre} - Costo: ${costo}, Precio venta: ${precio}, Margen: {margen}%"
**Validation:** Only create alerts when profitability status changes (from profitable to unprofitable), not on every recalculation.
```

---

### ROS-022: Permit Type Presets with Custom Alert Schedules

**Title:** `[RestaurantOS] Wave 7: Permit Type Presets with Custom Alert Schedules`

**Body:**
```markdown
## Context
**Project:** Restaurant Operating System — Centralized operational management platform for small restaurants
**Overview:** Provide preset document types for common restaurant permits with pre-configured alert schedules. When a document of a preset type is created, the appropriate alert schedule is automatically applied instead of the default 30/7/0 day windows. Custom alert schedules can override presets on a per-document basis.

**Current Wave:** Wave 7 of 7 — Cost Intelligence & Compliance
**Current Issue:** ROS-022 (Issue 22 of 22)
**Parallel Execution:** YES — This issue runs in parallel with ROS-021.

**Dependencies:** ROS-004 (Document entity), ROS-017 (Document Expiration Alert Automation)
**What comes next:** This completes Phase 1 and Phase 2 of the Restaurant Operating System. Future phases may add AI-powered predictions and analysis.

## Request
Create permit type presets and wire them to the document expiration alert system.

### 1. Permit Presets Configuration
Create `apps/Server/src/config/permit_presets.py`:
```python
PERMIT_PRESETS = {
    "manipulacion_alimentos": {
        "name": "Certificado de Manipulación de Alimentos",
        "alert_windows": [30, 7, 0],  # days before expiration
        "notification_channel": "whatsapp",
    },
    "bomberos": {
        "name": "Permiso de Bomberos",
        "alert_windows": [0],  # alert only at expiration
        "notification_channel": "whatsapp",
    },
    "camara_comercio": {
        "name": "Registro de Cámara de Comercio",
        "alert_windows": [30],  # annual alert, 30 days before
        "notification_channel": "email",
    },
    "extintor": {
        "name": "Servicio de Extintores",
        "alert_windows": [30, 7],  # alert before recharge date
        "notification_channel": "whatsapp",
    },
    "sanidad": {
        "name": "Certificado de Inspección Sanitaria",
        "alert_windows": [30, 14, 7],  # more frequent alerts
        "notification_channel": "whatsapp",
    },
}
```

### 2. Update Document Service
Modify `create_expiration_alerts()` in `apps/Server/src/core/services/document_service.py`:
```python
async def create_expiration_alerts(self, document_id: UUID, document_type: str, expiration_date: date, restaurant_id: UUID, person_id: UUID = None, custom_alert_windows: list[int] = None):
    """Create expiration alerts using preset or custom windows"""

    # Determine alert windows
    if custom_alert_windows:
        alert_windows = custom_alert_windows
    elif document_type in PERMIT_PRESETS:
        preset = PERMIT_PRESETS[document_type]
        alert_windows = preset["alert_windows"]
        notification_channel = preset.get("notification_channel", "whatsapp")
        print(f"INFO [DocumentService]: Using preset alerts for {preset['name']}: {alert_windows}")
    else:
        alert_windows = DEFAULT_ALERT_WINDOWS

    for days_before in alert_windows:
        alert_date = expiration_date - timedelta(days=days_before)
        if alert_date <= date.today():
            continue

        event_data = EventCreateDTO(
            restaurant_id=restaurant_id,
            type=EventType.VENCIMIENTO,
            description=f"{PERMIT_PRESETS.get(document_type, {}).get('name', 'Documento')} vence en {days_before} días" if days_before > 0 else f"{PERMIT_PRESETS.get(document_type, {}).get('name', 'Documento')} vence hoy",
            date=datetime.combine(alert_date, time(8, 0)),
            frequency=EventFrequency.NONE,
            responsible_id=person_id,
            notification_channel=notification_channel if document_type in PERMIT_PRESETS else "whatsapp",
            related_document_id=document_id,
        )
        await self.event_service.create(event_data)
```

### 3. Preset API Endpoint
Add to document routes:
```python
@router.get("/api/documents/permit-presets")
async def get_permit_presets(current_user: dict = Depends(get_current_user)):
    """Return available permit type presets"""
    return [
        {"type_key": key, "name": preset["name"], "alert_windows": preset["alert_windows"]}
        for key, preset in PERMIT_PRESETS.items()
    ]
```

### 4. Frontend: Preset Selection in Document Form
Update `TRDocumentForm` (from ROS-011):
- When document type matches a permit preset, show the preset name and default alert schedule
- Allow user to override with custom alert windows
- Add preset types to the document type dropdown

### 5. Seed or Migration
Ensure permit presets are available as configuration (no database seed needed since they're defined in code).

**UI Language:** Spanish (Colombian). Permit names: "Certificado de Manipulación de Alimentos", "Permiso de Bomberos", "Registro de Cámara de Comercio", "Servicio de Extintores", "Certificado de Inspección Sanitaria".
**Validation:** Custom alert windows must contain positive integers. Preset type must exist in PERMIT_PRESETS if specified.
```

---
