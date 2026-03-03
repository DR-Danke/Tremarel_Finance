# Event Entity CRUD Backend

**ADW ID:** dc999a0b
**Date:** 2026-03-03
**Specification:** specs/issue-82-adw-dc999a0b-sdlc_planner-event-entity-crud-backend.md

## Overview

Implements the Event entity as the centralized "nervous system" for RestaurantOS. Events represent tasks, deadlines, payments, shifts, checklists, and alerts with recurring schedule support. All downstream automation flows will create Events rather than triggering side effects directly, making Event the single audit trail for all system actions.

## What Was Built

- PostgreSQL `event` table with indexes and auto-update trigger
- SQLAlchemy `Event` model with restaurant-scoped multi-tenant isolation
- Pydantic DTOs with enums for type, frequency, status and a computed `is_overdue` field
- Repository with standard CRUD plus `get_due_events`, `bulk_create`, and multi-filter support
- Service layer with restaurant-scoped authorization and recurring instance generation
- 7 REST API endpoints with JWT authentication and query filters
- Comprehensive unit tests (1029 lines) covering all endpoints and edge cases

## Technical Implementation

### Files Modified

- `apps/Server/database/create_event_table.sql`: SQL migration with table definition, 6 indexes, and update trigger
- `apps/Server/src/models/event.py`: SQLAlchemy model with UUID PK, restaurant FK (CASCADE), person FK (SET NULL), self-referencing parent FK (CASCADE)
- `apps/Server/src/interface/event_dto.py`: Pydantic DTOs — `EventType` (7 values), `EventFrequency` (5 values), `EventStatus` (3 values), Create/Update/StatusUpdate/Response DTOs
- `apps/Server/src/repository/event_repository.py`: Repository with `create`, `get_by_id`, `get_by_restaurant` (multi-filter), `update`, `delete`, `get_due_events`, `bulk_create`
- `apps/Server/src/core/services/event_service.py`: Service with authorization checks, CRUD operations, recurring instance generation via `dateutil.relativedelta`
- `apps/Server/src/adapter/rest/event_routes.py`: 7 REST endpoints under `/api/events` with JWT auth
- `apps/Server/main.py`: Router registration
- `apps/Server/tests/test_event_api.py`: Comprehensive API tests

### Key Changes

- **Event types**: `tarea`, `vencimiento`, `pago`, `turno`, `checklist`, `alerta_stock`, `alerta_rentabilidad`
- **Recurring events**: Parent-child relationship via `parent_event_id` with auto-generation of instances (daily/weekly/monthly/yearly) using `generate_recurring_instances(days_ahead=7)`
- **Computed `is_overdue`**: `@model_validator` on `EventResponseDTO` — returns `True` when `status == 'pending'` and `date < now`
- **Restaurant-scoped authorization**: All operations verify user membership via `restaurant_repository.get_user_restaurant_role`
- **`related_document_id`**: Plain UUID without FK constraint for loose audit linking to documents

## API Endpoints

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| `POST` | `/api/events` | Create event | 201 |
| `GET` | `/api/events` | List events (with filters) | 200 |
| `GET` | `/api/events/due` | Get due events by date | 200 |
| `GET` | `/api/events/{event_id}` | Get single event | 200 |
| `PUT` | `/api/events/{event_id}` | Update event | 200 |
| `PATCH` | `/api/events/{event_id}/status` | Update status only | 200 |
| `DELETE` | `/api/events/{event_id}` | Delete event | 204 |

### Query Parameters (GET list)

- `restaurant_id` (required): Restaurant UUID
- `type`: Filter by event type
- `status`: Filter by event status
- `date_from` / `date_to`: Date range filter
- `responsible_id`: Filter by responsible person

## How to Use

1. Run the SQL migration `apps/Server/database/create_event_table.sql` against the database
2. Create an event via `POST /api/events` with JWT token and body including `restaurant_id`, `type`, and `date`
3. If `frequency` is set to anything other than `none`, recurring child instances are auto-generated for the next 7 days
4. List events with optional filters via `GET /api/events?restaurant_id=<uuid>`
5. Check due events for a date via `GET /api/events/due?restaurant_id=<uuid>&target_date=2026-03-03`
6. Update event status (e.g., mark completed) via `PATCH /api/events/{id}/status` with `{"status": "completed"}`
7. Deleting a parent event cascades to all child recurring instances

## Configuration

No additional environment variables required. The event system uses the existing database connection and JWT authentication configuration.

## Testing

```bash
cd apps/Server && python -m pytest tests/test_event_api.py -v
```

Tests cover: creation (201), unauthenticated (401), no restaurant access (403), list with filters, get/update/delete (200/404), status update (PATCH), due events query, and `is_overdue` computed field validation.

## Notes

- Backend-only feature — no frontend UI components included
- `related_document_id` has no FK constraint intentionally (loose link for audit purposes)
- Downstream consumers (issues #101, #94, #98) will create Events of types `alerta_stock`, `vencimiento`, and `alerta_rentabilidad`
- Wave 3 will build task assignment and recurrence enhancements on top of this entity
- Wave 5 will wire notification sending for due events using the `notification_channel` field
