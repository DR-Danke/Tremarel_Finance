# Task Assignment with Recurrence

**ADW ID:** 07ac42cd
**Date:** 2026-03-03
**Specification:** specs/issue-84-adw-07ac42cd-sdlc_planner-task-assignment-recurrence.md

## Overview

Extends the existing Event entity with task-specific functionality. Tasks are Events with `type="tarea"` that require a responsible person, reject past due dates, support recurring instance generation, and track completion timestamps. Adds bulk overdue detection and status transition validation.

## What Was Built

- **Task creation endpoint** (`POST /api/events/tasks`) — Creates events with type=tarea, validates responsible_id is required, rejects past dates, auto-generates recurring instances
- **Task query endpoint** (`GET /api/events/tasks`) — Lists only tarea-type events with filtering by restaurant, responsible person, date range, and status
- **Bulk overdue flagging endpoint** (`POST /api/events/tasks/flag-overdue`) — Bulk-updates pending events past their due date to overdue status
- **Status transition validation** — Enforces allowed transitions: pending->completed, pending->overdue, overdue->completed; blocks completed->* and overdue->pending
- **Completion timestamp tracking** — `completed_at` column set automatically when a task is marked completed
- **Comprehensive test suite** — 18+ new tests covering all task endpoints and business logic

## Technical Implementation

### Files Modified

- `apps/Server/src/models/event.py`: Added `completed_at` nullable DateTime column to Event model
- `apps/Server/database/create_event_table.sql`: Added `completed_at TIMESTAMP WITH TIME ZONE` column to schema
- `apps/Server/src/interface/event_dto.py`: Added `TaskCreateDTO` (with required `responsible_id`, no `type` field), added `completed_at` to `EventResponseDTO` and its ORM-to-dict conversion
- `apps/Server/src/repository/event_repository.py`: Added `update_overdue()` method for bulk status updates of pending events past cutoff time
- `apps/Server/src/core/services/event_service.py`: Added `create_task()`, `get_tasks()`, `flag_overdue_events()` methods; enhanced `update_event_status()` with transition validation and completed_at management
- `apps/Server/src/adapter/rest/event_routes.py`: Added three new REST endpoints under `/tasks`; enhanced status update error handling to distinguish 404 vs 400
- `apps/Server/tests/test_event_api.py`: Added 18+ tests covering task creation, querying, overdue flagging, and status transition validation

### Key Changes

- **TaskCreateDTO** omits the `type` field (forced to `tarea` in the service layer) and makes `responsible_id` required (not Optional), enforcing task-specific business rules at the DTO level
- **Route ordering** places `/tasks` and `/tasks/flag-overdue` before `/{event_id}` to prevent FastAPI from matching "tasks" as a UUID path parameter
- **Status transition validation** in `update_event_status()` now checks current status before allowing changes: completed tasks are final, overdue cannot revert to pending
- **`completed_at` auto-management**: set to `datetime.utcnow()` on completion, cleared to `None` on any other transition
- **`update_overdue()` repository method** uses a bulk `.update()` query with `synchronize_session="fetch"` for efficient batch operations

## How to Use

1. **Create a task**: `POST /api/events/tasks` with body containing `restaurant_id`, `date` (future), `responsible_id`, optional `description`, `frequency`, and `notification_channel`
2. **List tasks**: `GET /api/events/tasks?restaurant_id=<uuid>` with optional filters: `responsible_id`, `date_from`, `date_to`, `status`
3. **Flag overdue tasks**: `POST /api/events/tasks/flag-overdue?restaurant_id=<uuid>` to bulk-update pending tasks past their due date
4. **Complete a task**: `PATCH /api/events/<id>/status` with `{"status": "completed"}` — sets `completed_at` automatically
5. **Recurring tasks**: Set `frequency` to `daily`, `weekly`, `monthly`, or `yearly` during creation to auto-generate recurring instances

## Configuration

No new environment variables or configuration required. The feature extends existing Event infrastructure.

## Testing

Run the event-specific test suite:

```bash
cd apps/Server && uv run pytest tests/test_event_api.py -v
```

Run the full backend test suite to confirm zero regressions:

```bash
cd apps/Server && uv run pytest
```

Run linter checks:

```bash
cd apps/Server && uv run ruff check src/ tests/
```

## Notes

- **Status transition rules**: pending->completed, pending->overdue, overdue->completed are allowed. completed->* and overdue->pending are rejected.
- **Backward compatibility**: The existing Event API (`POST /api/events`, `GET /api/events`, etc.) is unchanged. New task endpoints are additive.
- **No new dependencies**: Uses existing `python-dateutil` for recurring instance generation.
- **Wave 4 dependency**: The daily task summary service (ROS-009) will consume `get_tasks()` and `flag_overdue_events()`. The Event/Task frontend page (ROS-012) will use both existing event and new task endpoints.
