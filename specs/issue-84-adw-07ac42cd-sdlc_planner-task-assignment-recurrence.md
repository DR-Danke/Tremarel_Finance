# Feature: Task Assignment with Recurrence

## Metadata
issue_number: `84`
adw_id: `07ac42cd`
issue_json: ``

## Feature Description
Extend the existing Event service with task-specific functionality. Tasks are Events with `type="tarea"`. This feature adds a dedicated task creation flow that forces the tarea type, validates that a responsible person is assigned, enforces date-in-future validation, and auto-generates recurring task instances. It also adds a dedicated task query endpoint with filtering, bulk overdue detection that flags past-due pending tasks, and enhanced task completion with `completed_at` timestamp tracking and status transition validation.

The Event entity (ROS-005) already supports recurrence generation, parent-child relationships, and the `is_overdue` computed field. This feature builds on that foundation with task-specific business rules and dedicated API endpoints.

## User Story
As a restaurant manager
I want to create tasks assigned to staff with optional recurrence schedules
So that I can track daily operations, detect overdue work, and mark tasks completed with timestamps

## Problem Statement
The existing Event CRUD treats all event types uniformly. Tasks (type=tarea) need stricter validation (must have a responsible person, date cannot be in the past), a dedicated query endpoint for task-specific filtering, bulk overdue flagging to proactively detect late work, and completion timestamp tracking. Without these, managers cannot reliably create, query, and track task execution.

## Solution Statement
Add task-specific service methods (`create_task`, `get_tasks`, `flag_overdue_events`), a `completed_at` column to the event model, status transition validation in `update_event_status`, and three new REST endpoints under `/api/events/tasks`. The solution extends existing code without breaking the general-purpose Event API.

## Relevant Files
Use these files to implement the feature:

**Core files to modify:**
- `apps/Server/src/models/event.py` — Add `completed_at` column to Event model
- `apps/Server/src/interface/event_dto.py` — Add `TaskCreateDTO`, add `completed_at` to `EventResponseDTO`, add task-specific validation
- `apps/Server/src/repository/event_repository.py` — Add `update_overdue()` bulk update method
- `apps/Server/src/core/services/event_service.py` — Add `create_task()`, `get_tasks()`, `flag_overdue_events()` methods; enhance `update_event_status()` with transition validation and completed_at
- `apps/Server/src/adapter/rest/event_routes.py` — Add `POST /tasks`, `GET /tasks`, `POST /tasks/flag-overdue` endpoints
- `apps/Server/tests/test_event_api.py` — Add tests for all new task endpoints and business logic
- `apps/Server/database/create_event_table.sql` — Add `completed_at` column to schema

**Reference files (read for patterns, do not modify):**
- `apps/Server/src/core/services/person_service.py` — Reference for service patterns
- `apps/Server/src/repository/person_repository.py` — Reference for repository patterns
- `apps/Server/main.py` — Event router is already registered, no change needed

**Documentation files to read:**
- `app_docs/feature-dc999a0b-event-entity-crud-backend.md` — Event entity implementation details
- `app_docs/feature-14633eae-person-entity-crud-backend.md` — Person entity (responsible_id FK reference)
- `app_docs/feature-a692d2db-restaurant-multi-tenant-entity.md` — Restaurant-scoped authorization pattern
- `app_docs/feature-0f0d4c36-fastapi-backend-setup.md` — FastAPI router registration pattern

### New Files
No new files are created. All changes extend existing files.

## Implementation Plan
### Phase 1: Foundation
Add the `completed_at` column to the Event model and database schema. Update the EventResponseDTO to include `completed_at` in responses. Create the `TaskCreateDTO` with task-specific validation (required `responsible_id`, date-not-in-past validation).

### Phase 2: Core Implementation
Add task-specific service methods: `create_task()` forces type=tarea and validates responsible_id; `get_tasks()` delegates to the existing `get_events()` with type filter hardcoded to "tarea"; `flag_overdue_events()` bulk-updates pending events past their due date to status="overdue". Enhance `update_event_status()` to validate status transitions (only pending -> completed or pending -> overdue) and set `completed_at` timestamp on completion. Add `update_overdue()` to the repository for bulk status updates.

### Phase 3: Integration
Wire up three new REST endpoints under `/api/events/tasks` that call the new service methods. These endpoints are placed BEFORE the `/{event_id}` route in the router to avoid path conflicts (same pattern as `/due`). Add comprehensive tests covering all new functionality.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Read documentation and reference files
- Read `app_docs/feature-dc999a0b-event-entity-crud-backend.md` for the Event entity implementation details
- Read `app_docs/feature-14633eae-person-entity-crud-backend.md` for the Person entity patterns
- Read `app_docs/feature-a692d2db-restaurant-multi-tenant-entity.md` for restaurant-scoped authorization
- Read `apps/Server/src/models/event.py`, `apps/Server/src/interface/event_dto.py`, `apps/Server/src/repository/event_repository.py`, `apps/Server/src/core/services/event_service.py`, `apps/Server/src/adapter/rest/event_routes.py` to confirm current state

### Step 2: Add `completed_at` column to Event model
- In `apps/Server/src/models/event.py`, add a new column after `parent_event_id`:
  ```python
  completed_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
  ```
- In `apps/Server/database/create_event_table.sql`, add `completed_at TIMESTAMP WITH TIME ZONE` column after `parent_event_id` line

### Step 3: Update DTOs with `completed_at` and `TaskCreateDTO`
- In `apps/Server/src/interface/event_dto.py`:
  - Add `completed_at: Optional[datetime] = Field(None, description="Timestamp when task was completed")` to `EventResponseDTO` (before `is_overdue`)
  - Update the `compute_is_overdue` model validator to include `completed_at` in the ORM-to-dict conversion
  - Add a new `TaskCreateDTO` class:
    ```python
    class TaskCreateDTO(BaseModel):
        """DTO for task creation request. Tasks are events with type=tarea."""
        restaurant_id: UUID = Field(..., description="Restaurant UUID this task belongs to")
        date: datetime = Field(..., description="Task due date and time")
        description: Optional[str] = Field(None, description="Task description")
        frequency: EventFrequency = Field(EventFrequency.NONE, description="Recurrence frequency")
        responsible_id: UUID = Field(..., description="Person UUID responsible for this task (required)")
        notification_channel: str = Field("email", description="Notification channel")
    ```
  - Note: `TaskCreateDTO` does NOT include `type` (forced to tarea in service) and `responsible_id` is required (not Optional)

### Step 4: Add `update_overdue()` method to EventRepository
- In `apps/Server/src/repository/event_repository.py`, add a new method:
  ```python
  def update_overdue(self, db: Session, restaurant_id: UUID, cutoff_time: datetime) -> int:
      """Bulk update pending events with date before cutoff to overdue status."""
  ```
- Implementation: query events where `restaurant_id` matches, `status == "pending"`, and `date < cutoff_time`, then update their status to "overdue"
- Return the count of updated rows
- Use `db.query(Event).filter(...).update({"status": "overdue"})` with `synchronize_session="fetch"` then `db.commit()`
- Include proper logging

### Step 5: Add task-specific service methods to EventService
- In `apps/Server/src/core/services/event_service.py`:
  - Import `TaskCreateDTO` from the DTOs
  - Add `create_task()` method:
    - Accepts `db`, `user_id`, `data: TaskCreateDTO`
    - Checks restaurant access
    - Validates `data.date` is not in the past (raise `ValueError` if it is)
    - Creates the event using `event_repository.create()` with `event_type="tarea"` hardcoded
    - If `data.frequency` is not "none", calls `self.generate_recurring_instances(db, event.id)`
    - Returns the created Event
  - Add `get_tasks()` method:
    - Accepts `db`, `user_id`, `restaurant_id`, optional `responsible_id`, `date_from`, `date_to`, `status_filter`
    - Checks restaurant access
    - Calls `event_repository.get_by_restaurant()` with `type_filter="tarea"` hardcoded plus the passed filters
    - Returns list of Events
  - Add `flag_overdue_events()` method:
    - Accepts `db`, `user_id`, `restaurant_id`
    - Checks restaurant access
    - Calls `event_repository.update_overdue(db, restaurant_id, datetime.utcnow())`
    - Returns the count of flagged events
  - Enhance `update_event_status()`:
    - After fetching the event, validate the status transition:
      - Only allow: pending → completed, pending → overdue
      - If current status is "completed", raise `ValueError("Cannot change status of a completed task")`
      - If current status is "overdue" and target is "completed", allow it (overdue tasks can still be completed)
    - When new status is "completed", set `event.completed_at = datetime.utcnow()`
    - When new status is not "completed", set `event.completed_at = None` (clear it)

### Step 6: Add task-specific REST endpoints to event_routes.py
- In `apps/Server/src/adapter/rest/event_routes.py`:
  - Import `TaskCreateDTO` from the DTOs
  - Add three new endpoints BEFORE the `/{event_id}` GET route (to avoid path conflicts):
  - `POST /tasks` — Create a task:
    - Accepts `TaskCreateDTO` body
    - Calls `event_service.create_task(db, user_id, data)`
    - Returns `EventResponseDTO` with status 201
    - Catches `PermissionError` → 403, `ValueError` → 400
  - `GET /tasks` — List tasks with filtering:
    - Query params: `restaurant_id` (required), `responsible_id` (optional), `date_from` (optional), `date_to` (optional), `status` (optional)
    - Calls `event_service.get_tasks()`
    - Returns `List[EventResponseDTO]`
    - Catches `PermissionError` → 403
  - `POST /tasks/flag-overdue` — Flag overdue events:
    - Query param: `restaurant_id` (required)
    - Calls `event_service.flag_overdue_events()`
    - Returns `{"flagged_count": N}`
    - Catches `PermissionError` → 403

### Step 7: Add tests for new task functionality
- In `apps/Server/tests/test_event_api.py`, add new test sections:
  - **Task Creation Tests:**
    - `test_create_task_success` — Valid task creation returns 201 with type=tarea
    - `test_create_task_missing_responsible_id` — Returns 422 (Pydantic validation) since responsible_id is required
    - `test_create_task_past_date` — Returns 400 for date in the past
    - `test_create_task_with_recurrence` — Creates task with frequency=daily and verifies recurring instances generated
    - `test_create_task_unauthenticated` — Returns 401
    - `test_create_task_no_access` — Returns 403
  - **Task Query Tests:**
    - `test_get_tasks_success` — Returns only tarea-type events
    - `test_get_tasks_filter_by_responsible` — Filters by responsible_id
    - `test_get_tasks_filter_by_status` — Filters by status
    - `test_get_tasks_unauthenticated` — Returns 401
    - `test_get_tasks_no_access` — Returns 403
  - **Flag Overdue Tests:**
    - `test_flag_overdue_events_success` — Returns flagged_count
    - `test_flag_overdue_events_unauthenticated` — Returns 401
    - `test_flag_overdue_events_no_access` — Returns 403
  - **Task Completion Enhancement Tests:**
    - `test_complete_task_sets_completed_at` — Verify completed_at is set on completion
    - `test_complete_already_completed_task_fails` — Returns 400 for already completed task
    - `test_overdue_task_can_be_completed` — Overdue → completed is allowed
- Use the same mock patterns as existing tests (patch `event_repository`, `restaurant_repository`, `auth_service`)
- Update `create_mock_event` helper to include `completed_at=None` attribute

### Step 8: Run validation commands
- Run all validation commands listed below to confirm zero regressions

## Testing Strategy
### Unit Tests
- Test `create_task()` service method: forces type=tarea, validates responsible_id presence, validates date not in past, generates recurring instances for non-none frequency
- Test `get_tasks()` service method: always filters by type=tarea, applies optional responsible_id/status/date filters
- Test `flag_overdue_events()` service method: calls repository `update_overdue()`, returns count
- Test `update_event_status()` enhancement: validates status transitions, sets/clears `completed_at`
- Test `update_overdue()` repository method: bulk updates matching events, returns count
- Test all three new REST endpoints: success, auth, access control, validation errors

### Edge Cases
- Creating a task with date exactly at current time (boundary — should be allowed)
- Creating a task with date 1 second in the past (should be rejected)
- Flagging overdue when no events are overdue (returns count=0)
- Flagging overdue when events are already marked overdue (should not re-flag)
- Completing an overdue task (allowed — overdue → completed)
- Trying to set a completed task back to pending (rejected)
- Task with frequency="none" should not generate recurring instances
- Task with frequency="daily" and date far in the future should generate instances only within days_ahead window
- `completed_at` is None for non-completed tasks and set for completed tasks

## Acceptance Criteria
- `POST /api/events/tasks` creates an event with type=tarea, requires responsible_id, rejects past dates, and generates recurring instances when frequency is set
- `GET /api/events/tasks` returns only events with type=tarea, supports filtering by restaurant_id, responsible_id, date range, and status
- `POST /api/events/tasks/flag-overdue` bulk-updates pending events past their due date to overdue status and returns the count
- `PATCH /api/events/{id}/status` validates status transitions (pending→completed, pending→overdue, overdue→completed) and sets `completed_at` on completion
- Event model includes `completed_at` column, and `EventResponseDTO` includes `completed_at` in responses
- All new endpoints require authentication and restaurant-scoped authorization
- All existing Event API tests continue to pass with zero regressions
- All new task-specific tests pass

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest tests/test_event_api.py -v` — Run event-specific tests to validate new task functionality and zero regressions on existing event tests
- `cd apps/Server && uv run pytest` — Run all Server tests to validate zero regressions across the entire backend
- `cd apps/Server && uv run ruff check src/` — Run linter on source code to catch any style/import issues
- `cd apps/Server && uv run ruff check tests/` — Run linter on test code

## Notes
- **No new dependencies needed.** `python-dateutil` is already in `requirements.txt` for `relativedelta` used in recurring instance generation.
- **No changes to `main.py`.** The event router is already registered; all new endpoints are added to the same router.
- **Route ordering matters.** The new `/tasks` and `/tasks/flag-overdue` endpoints must be placed BEFORE the `/{event_id}` route in `event_routes.py` to avoid FastAPI matching "tasks" as an `event_id` UUID parameter. Follow the same pattern used for `/due`.
- **Backward compatibility.** The existing Event API (`POST /api/events`, `GET /api/events`, etc.) continues to work unchanged. The new task endpoints are additive.
- **Wave 4 dependency.** The daily task summary service (ROS-009) will consume `get_tasks()` and `flag_overdue_events()`. The Event/Task frontend page (ROS-012) will use both the existing event endpoints and the new task endpoints.
- **Status transition rules:**
  - `pending → completed` — Allowed (normal completion)
  - `pending → overdue` — Allowed (system/manual flagging)
  - `overdue → completed` — Allowed (late completion)
  - `completed → *` — Rejected (completed tasks are final)
  - `overdue → pending` — Rejected (cannot un-flag overdue)
