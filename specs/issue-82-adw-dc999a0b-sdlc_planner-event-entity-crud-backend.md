# Feature: Event Entity Data Model & CRUD Backend

## Metadata
issue_number: `82`
adw_id: `dc999a0b`
issue_json: ``

## Feature Description
Create the Event entity with full backend CRUD for the RestaurantOS module. Event is the system's "nervous system" — it represents tasks, deadlines, payments, shifts, checklists, and alerts. Events can be recurring (daily, weekly, monthly, yearly) and auto-generate individual instances linked to a parent event via `parent_event_id`. Each event has a responsible person and a notification channel preference. All downstream automation flows (document expiry, low stock, profitability, tasks) will create Events rather than triggering side effects directly, making Event the single audit trail for all system actions.

## User Story
As a restaurant manager
I want to create and manage events (tasks, deadlines, payments, shifts, checklists, alerts) with recurring schedules
So that I have a centralized nervous system tracking all operational actions and deadlines for my restaurant

## Problem Statement
The RestaurantOS currently lacks a centralized event/task management entity. Without it, automation flows (document expiry alerts, low stock alerts, profitability alerts) have no standardized way to record actions, and there is no unified audit trail for system-generated or user-created tasks.

## Solution Statement
Implement a full backend CRUD for the Event entity following the established RestaurantOS Clean Architecture patterns. The solution includes:
- Database table with recurring event support via parent-child relationships
- SQLAlchemy model with all required columns
- Pydantic DTOs with enums for type, frequency, status and a computed `is_overdue` field
- Repository with standard CRUD plus `get_due_events`, `bulk_create`, and filter support
- Service layer with restaurant-scoped authorization and recurring instance generation logic
- REST API routes with JWT authentication and optional query filters
- Comprehensive unit tests following the existing test patterns

## Relevant Files
Use these files to implement the feature:

- `apps/Server/main.py` — Entry point where the event router must be registered (import + `app.include_router` + log message)
- `apps/Server/src/config/database.py` — Base class for SQLAlchemy models
- `apps/Server/src/adapter/rest/dependencies.py` — `get_current_user` and `get_db` dependency injectors used by all routes
- `apps/Server/src/repository/restaurant_repository.py` — `get_user_restaurant_role` method used for authorization checks in services
- `apps/Server/src/models/document.py` — Reference model pattern (UUID PK, restaurant_id FK, datetime columns, `__repr__`)
- `apps/Server/src/interface/document_dto.py` — Reference DTO pattern (Create/Update/Response DTOs, computed field via `@model_validator`, `from_attributes`)
- `apps/Server/src/repository/document_repository.py` — Reference repository pattern (CRUD methods, logging, singleton)
- `apps/Server/src/core/services/document_service.py` — Reference service pattern (`_check_restaurant_access`, CRUD with authorization, singleton)
- `apps/Server/src/adapter/rest/document_routes.py` — Reference routes pattern (`_to_response` helper, error handling, Query params, status codes)
- `apps/Server/tests/test_document_api.py` — Reference test pattern (mock DB, mock user, auth token, patch paths, comprehensive CRUD tests)
- `apps/Server/database/create_document_table.sql` — Reference SQL migration pattern (indexes, triggers)
- `app_docs/feature-a692d2db-restaurant-multi-tenant-entity.md` — Restaurant multi-tenant scoping documentation (read for restaurant authorization patterns)
- `app_docs/feature-95deee5d-document-entity-crud-backend.md` — Document entity documentation (closest reference for Event implementation)

### New Files
- `apps/Server/database/create_event_table.sql` — SQL migration for event table
- `apps/Server/src/models/event.py` — SQLAlchemy Event model
- `apps/Server/src/interface/event_dto.py` — Pydantic DTOs (EventType, EventFrequency, EventStatus enums + Create/Update/Response DTOs)
- `apps/Server/src/repository/event_repository.py` — Event repository with CRUD + `get_due_events` + `bulk_create`
- `apps/Server/src/core/services/event_service.py` — Event service with authorization + recurring instance generation
- `apps/Server/src/adapter/rest/event_routes.py` — REST API routes for Event CRUD
- `apps/Server/tests/test_event_api.py` — Comprehensive API tests

## Implementation Plan
### Phase 1: Foundation
Set up the database schema and ORM model:
- Create the SQL migration with all columns, indexes, and update trigger
- Create the SQLAlchemy model mapping to the event table
- Create the Pydantic DTOs with enums for type, frequency, status and a computed `is_overdue` field

### Phase 2: Core Implementation
Build the data access and business logic layers:
- Create the repository with standard CRUD methods plus `get_due_events`, `bulk_create`, and multi-filter `get_by_restaurant`
- Create the service with restaurant-scoped authorization, recurring instance generation (`generate_recurring_instances`), and overdue detection

### Phase 3: Integration
Wire up the REST API and register with the application:
- Create the REST routes with all 6 endpoints (list, create, get, update, patch status, delete) plus JWT authentication
- Register the event router in `main.py`
- Create comprehensive tests covering all endpoints and edge cases

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create SQL Migration
- Create `apps/Server/database/create_event_table.sql`
- Define the `event` table with all columns: `id` (UUID PK), `restaurant_id` (UUID FK to restaurant), `type` (VARCHAR 100), `description` (TEXT), `date` (TIMESTAMP), `frequency` (VARCHAR 50, default 'none'), `responsible_id` (UUID FK to person, ON DELETE SET NULL), `notification_channel` (VARCHAR 50, default 'email'), `status` (VARCHAR 50, default 'pending'), `related_document_id` (UUID, no FK constraint), `parent_event_id` (UUID self-referencing FK, ON DELETE CASCADE), `created_at` and `updated_at` (TIMESTAMP WITH TIME ZONE)
- Add `ON DELETE CASCADE` for `restaurant_id` FK (consistent with document/resource patterns)
- Create indexes: `idx_event_restaurant`, `idx_event_type`, `idx_event_date`, `idx_event_status`, `idx_event_responsible`, `idx_event_parent`
- Add the `update_event_updated_at` trigger

### Step 2: Create SQLAlchemy Model
- Create `apps/Server/src/models/event.py`
- Follow the Document model pattern: UUID PK with `default=uuid.uuid4`, `restaurant_id` FK, all columns with type hints
- Include `parent_event_id` as self-referencing FK: `ForeignKey("event.id")`
- Include `responsible_id` FK: `ForeignKey("person.id")`
- Add `__repr__` method

### Step 3: Create Pydantic DTOs
- Create `apps/Server/src/interface/event_dto.py`
- Define enums: `EventType` (tarea, vencimiento, pago, turno, checklist, alerta_stock, alerta_rentabilidad), `EventFrequency` (none, daily, weekly, monthly, yearly), `EventStatus` (pending, completed, overdue)
- Create `EventCreateDTO` with required fields: `restaurant_id`, `type` (EventType), `date` (datetime); optional fields: `description`, `frequency` (default NONE), `responsible_id`, `notification_channel` (default "email"), `related_document_id`
- Create `EventUpdateDTO` with all fields optional for partial updates: `type`, `description`, `date`, `frequency`, `responsible_id`, `notification_channel`, `related_document_id`
- Create `EventStatusUpdateDTO` with required `status: EventStatus`
- Create `EventResponseDTO` with all fields plus computed `is_overdue` (bool) via `@model_validator(mode="before")` — calculated as `status == 'pending' and date < now`
- Use `model_config = {"from_attributes": True}`

### Step 4: Create Repository
- Create `apps/Server/src/repository/event_repository.py`
- Implement `create(db, restaurant_id, event_type, description, date, frequency, responsible_id, notification_channel, related_document_id, parent_event_id)` — insert event
- Implement `get_by_id(db, event_id)` — get single event by UUID
- Implement `get_by_restaurant(db, restaurant_id, type_filter, status_filter, date_from, date_to, responsible_id_filter)` — list with multiple optional filters
- Implement `update(db, event)` — update event (add + commit + refresh pattern)
- Implement `delete(db, event_id)` — delete event by UUID
- Implement `get_due_events(db, restaurant_id, target_date)` — get events due on a specific date
- Implement `bulk_create(db, events_data)` — bulk insert for recurring instance generation
- Follow singleton pattern: `event_repository = EventRepository()`
- Add INFO logging to all methods

### Step 5: Create Service
- Create `apps/Server/src/core/services/event_service.py`
- Implement `_check_restaurant_access(db, user_id, restaurant_id)` — verify user membership via `restaurant_repository.get_user_restaurant_role`
- Implement `create_event(db, user_id, data: EventCreateDTO)` — create event with authorization; if `frequency != 'none'`, auto-generate recurring instances via `generate_recurring_instances`
- Implement `get_events(db, user_id, restaurant_id, type_filter, status_filter, date_from, date_to, responsible_id_filter)` — list events with authorization and filters
- Implement `get_event(db, user_id, event_id)` — get single event with authorization
- Implement `update_event(db, user_id, event_id, data: EventUpdateDTO)` — update event with authorization, apply fields conditionally
- Implement `update_event_status(db, user_id, event_id, data: EventStatusUpdateDTO)` — update just the status field with authorization
- Implement `delete_event(db, user_id, event_id)` — delete event with authorization
- Implement `generate_recurring_instances(db, event_id, days_ahead=7)` — for a recurring event, generate individual instances for the upcoming period; each instance gets `parent_event_id` pointing to the recurring event, `frequency='none'`, and the computed next date based on the parent's frequency
- Follow singleton pattern: `event_service = EventService()`
- Add INFO/ERROR/WARNING logging throughout

### Step 6: Create REST Routes
- Create `apps/Server/src/adapter/rest/event_routes.py`
- Define `router = APIRouter(prefix="/api/events", tags=["Events"])`
- Implement `_to_response(event)` helper using `EventResponseDTO.model_validate(event, from_attributes=True)`
- `POST ""` — create event (status 201); accept `EventCreateDTO` as JSON body; catch PermissionError (403)
- `GET ""` — list events; require `restaurant_id: UUID = Query(...)`, optional `type`, `status`, `date_from`, `date_to`, `responsible_id` query params; catch PermissionError (403)
- `GET "/due"` — get due events; require `restaurant_id: UUID = Query(...)` and `target_date: date = Query(...)`; catch PermissionError (403). Place BEFORE `/{event_id}` to avoid path conflict
- `GET "/{event_id}"` — get single event; catch PermissionError (403) and ValueError (404)
- `PUT "/{event_id}"` — update event; accept `EventUpdateDTO` as JSON body; catch PermissionError (403) and ValueError (404)
- `PATCH "/{event_id}/status"` — update event status; accept `EventStatusUpdateDTO` as JSON body; catch PermissionError (403) and ValueError (404)
- `DELETE "/{event_id}"` — delete event (status 204); catch PermissionError (403) and ValueError (404)
- All endpoints use `Depends(get_current_user)` and `Depends(get_db)`
- Add INFO/ERROR logging to all endpoints

### Step 7: Register Router in main.py
- Add import: `from src.adapter.rest.event_routes import router as event_router`
- Add `app.include_router(event_router)` after the document router line
- Add `print("INFO [Main]: Event router registered")` after the document log line

### Step 8: Create API Tests
- Create `apps/Server/tests/test_event_api.py`
- Follow the `test_document_api.py` pattern exactly:
  - Mock DB setup with `get_mock_db` and `app.dependency_overrides`
  - `create_mock_user` helper
  - `create_mock_event` helper (with all Event fields including `parent_event_id`, `status`, `frequency`)
  - `get_auth_token` helper
- Test sections:
  - **Creation tests**: success (201), unauthenticated (401), no restaurant access (403)
  - **List tests**: success (200), unauthenticated (401), no access (403), with type filter, with status filter
  - **Get tests**: success (200), not found (404), unauthenticated (401), no access (403)
  - **Update tests**: success (200), not found (404), unauthenticated (401), no access (403)
  - **Status update tests**: success (200), not found (404), unauthenticated (401), no access (403)
  - **Delete tests**: success (204), not found (404), unauthenticated (401), no access (403)
  - **Due events tests**: success (200), unauthenticated (401), no access (403)
- Verify `is_overdue` computed field is present in responses
- Add `print("INFO [TestEventAPI]: test_name - PASSED")` logging to all tests

### Step 9: Run Validation Commands
- Run all validation commands listed below to verify zero regressions

## Testing Strategy
### Unit Tests
- Test all 6 REST endpoints (POST, GET list, GET single, PUT, PATCH status, DELETE) plus the GET `/due` endpoint
- Test authentication: unauthenticated requests return 401
- Test authorization: users without restaurant access get 403
- Test not found: nonexistent event_id returns 404
- Test computed field: `is_overdue` is present in all response DTOs
- Test filters: type and status query parameters filter correctly
- Test status update: PATCH endpoint correctly updates only the status field

### Edge Cases
- Creating an event with `frequency != 'none'` triggers recurring instance generation
- Deleting a parent event cascades to child instances (via `ON DELETE CASCADE` on `parent_event_id`)
- `is_overdue` computation: event with status=pending and date < now returns `is_overdue=True`
- `is_overdue` for completed events: always `False` regardless of date
- Events with `responsible_id` referencing a deleted person get `responsible_id = NULL` (ON DELETE SET NULL)
- Bulk create for recurring instances: multiple events created in a single transaction
- Date range filtering: `date_from` and `date_to` correctly bound event queries
- Status transition validation: only `pending → completed` and `pending → overdue` are valid

## Acceptance Criteria
- [ ] Event table created with all columns, indexes, and update trigger
- [ ] SQLAlchemy EventModel maps to event table with all columns
- [ ] EventType enum includes: tarea, vencimiento, pago, turno, checklist, alerta_stock, alerta_rentabilidad
- [ ] EventFrequency enum includes: none, daily, weekly, monthly, yearly
- [ ] EventStatus enum includes: pending, completed, overdue
- [ ] Every Event has a notification_channel field (email, push, whatsapp)
- [ ] related_document_id field exists for linking to source documents
- [ ] Parent-child relationship (parent_event_id) supports recurring event instances
- [ ] EventResponseDTO includes computed `is_overdue` boolean field
- [ ] Repository supports CRUD + `get_due_events` + `bulk_create` + multi-filter listing
- [ ] Service enforces restaurant-scoped authorization on all operations
- [ ] Service generates recurring instances when frequency != 'none'
- [ ] All 7 REST endpoints work with JWT authentication
- [ ] PATCH endpoint updates only status field
- [ ] Event router registered in main.py
- [ ] All tests pass with zero regressions
- [ ] Event status transitions: pending → completed | overdue

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -m pytest tests/test_event_api.py -v` — Run Event-specific tests to validate the new feature
- `cd apps/Server && python -m pytest tests/ -v` — Run all Server tests to validate zero regressions
- `cd apps/Server && python -c "from src.models.event import Event; print('Event model imports OK')"` — Verify Event model imports correctly
- `cd apps/Server && python -c "from src.interface.event_dto import EventCreateDTO, EventUpdateDTO, EventResponseDTO, EventStatusUpdateDTO, EventType, EventFrequency, EventStatus; print('Event DTOs import OK')"` — Verify Event DTOs import correctly
- `cd apps/Server && python -c "from src.repository.event_repository import event_repository; print('Event repository imports OK')"` — Verify Event repository imports correctly
- `cd apps/Server && python -c "from src.core.services.event_service import event_service; print('Event service imports OK')"` — Verify Event service imports correctly
- `cd apps/Server && python -c "from src.adapter.rest.event_routes import router; print('Event routes import OK')"` — Verify Event routes import correctly

## Notes
- This is a backend-only feature (no UI components). No E2E tests needed.
- The Event entity is the central nervous system of RestaurantOS. All future automation flows (Wave 3+) will create Events.
- `related_document_id` is stored as a plain UUID without a FK constraint, since the document table may not always have the referenced record (it serves as a loose link for audit purposes).
- The `generate_recurring_instances` method should calculate next dates based on the parent event's `date` and `frequency`:
  - `daily`: add 1 day per instance
  - `weekly`: add 7 days per instance
  - `monthly`: add 1 month per instance (use `dateutil.relativedelta` or manual month arithmetic)
  - `yearly`: add 1 year per instance
- For monthly/yearly recurrence, consider using `from dateutil.relativedelta import relativedelta` — this is already available via `python-dateutil` (dependency of many packages). If not installed, add it via `pip install python-dateutil` and update `requirements.txt`.
- Downstream consumers (issues #101, #94, #98) will create Events of types `alerta_stock`, `vencimiento`, and `alerta_rentabilidad` respectively.
- Wave 3 will build task assignment and recurrence enhancements on top of this Event entity.
- Wave 5 will wire notification sending for due events using the `notification_channel` field.
