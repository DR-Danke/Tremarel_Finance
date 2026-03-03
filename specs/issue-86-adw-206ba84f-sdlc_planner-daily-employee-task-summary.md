# Feature: Daily Employee Task Summary

## Metadata
issue_number: `86`
adw_id: `206ba84f`
issue_json: ``

## Feature Description
Build a backend service that generates a daily summary of tasks for each employee in a restaurant. The service aggregates all pending and overdue Events of type="tarea" for a given person and date, producing a structured summary with task counts and details. A batch endpoint generates summaries for all employees in a restaurant simultaneously. This summary data will be consumed by Wave 5's notification system to send daily WhatsApp/email task lists to employees.

## User Story
As a restaurant manager or automated notification system
I want to retrieve a daily summary of tasks assigned to each employee
So that employees know exactly what they need to do each day and overdue tasks are surfaced

## Problem Statement
There is currently no way to get a consolidated view of an employee's daily task load. The existing `GET /api/events/tasks` endpoint returns raw task lists without aggregation or summary statistics. The notification system (Wave 5) needs a structured summary format with counts, overdue flags, and organized task details to generate meaningful daily messages.

## Solution Statement
Add two new service methods to `EventService` — one for individual employee summaries and one for batch summaries across all employees in a restaurant. Expose these via two new REST endpoints under `/api/events/tasks/daily-summary`. Create corresponding Pydantic DTOs for structured response validation. The implementation reuses the existing `event_repository.get_by_restaurant()` method which already supports all required filters (type, responsible_id, date range, status).

## Relevant Files
Use these files to implement the feature:

- `apps/Server/src/core/services/event_service.py` — Add `get_daily_task_summary()` and `get_all_daily_summaries()` methods. Already contains `get_tasks()`, `flag_overdue_events()`, and `get_due_events()` which demonstrate the patterns to follow.
- `apps/Server/src/interface/event_dto.py` — Add `TaskSummaryItemDTO` and `DailyTaskSummaryDTO` response DTOs. Contains existing DTOs like `EventResponseDTO` that show the DTO pattern.
- `apps/Server/src/adapter/rest/event_routes.py` — Add two new endpoints for individual and batch daily summaries. Contains existing task endpoints (`/tasks`, `/tasks/flag-overdue`) that demonstrate routing patterns. **Critical:** new routes must be placed before `/{event_id}` to avoid path conflicts.
- `apps/Server/src/repository/event_repository.py` — Reference only, no changes needed. The `get_by_restaurant()` method already supports all required filters (type_filter, responsible_id_filter, date_from, date_to).
- `apps/Server/src/repository/person_repository.py` — Reference only, no changes needed. The `get_by_restaurant()` method with `type_filter="employee"` provides the employee list for batch summaries.
- `apps/Server/src/models/event.py` — Reference only. Defines the Event model with `responsible_id`, `status`, `type`, `date` fields.
- `apps/Server/src/models/person.py` — Reference only. Defines the Person model with `name`, `type` fields.
- `apps/Server/tests/test_event_api.py` — Add tests for the two new endpoints. Contains existing test patterns with mock setup helpers (`create_mock_user`, `create_mock_event`, `get_auth_token`).
- `apps/Server/tests/test_person_api.py` — Reference only. Contains `create_mock_person()` helper to copy/adapt for summary tests.
- `app_docs/feature-07ac42cd-task-assignment-recurrence.md` — Reference documentation for task assignment patterns and status transition rules.
- `app_docs/feature-14633eae-person-entity-crud-backend.md` — Reference documentation for Person entity and repository patterns.

### New Files
No new files are needed. All changes go into existing files.

## Implementation Plan
### Phase 1: Foundation
Add the Pydantic DTOs (`TaskSummaryItemDTO` and `DailyTaskSummaryDTO`) to `event_dto.py`. These define the response contract for the summary endpoints and must exist before the service and route layers reference them.

### Phase 2: Core Implementation
Add the `person_repository` import and two new service methods to `event_service.py`:
1. `get_daily_task_summary(db, user_id, restaurant_id, person_id, summary_date)` — Fetches tasks for one person on one date, computes counts, returns structured summary.
2. `get_all_daily_summaries(db, user_id, restaurant_id, summary_date)` — Fetches all employees in a restaurant, calls `get_daily_task_summary` for each, filters out employees with zero tasks.

Both methods reuse the existing `get_by_restaurant()` repository method with type_filter="tarea", responsible_id_filter, and date range boundaries.

### Phase 3: Integration
Add two new REST endpoints to `event_routes.py`:
1. `GET /api/events/tasks/daily-summary` — Single employee summary (query params: `restaurant_id`, `person_id`, `summary_date`)
2. `GET /api/events/tasks/daily-summary/all` — Batch summary for all employees (query params: `restaurant_id`, `summary_date`)

Both endpoints follow the existing auth and error handling patterns. Route declarations must appear before `/{event_id}` to avoid path conflicts.

Add comprehensive tests covering both endpoints, including empty task lists, mixed statuses, and batch summaries.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Add Summary DTOs to event_dto.py
- Read `apps/Server/src/interface/event_dto.py` to understand existing DTO patterns
- Add `TaskSummaryItemDTO` with fields: `id` (UUID), `description` (str), `time` (Optional[str]), `status` (str), `is_overdue` (bool)
- Add `DailyTaskSummaryDTO` with fields: `person_id` (UUID), `person_name` (str), `date` (date), `total_tasks` (int), `overdue_count` (int), `tasks` (list[TaskSummaryItemDTO])
- Both DTOs use `BaseModel` from Pydantic, consistent with existing DTOs
- Import `date` from `datetime` module (already imported in the file for EventResponseDTO)

### Step 2: Add Service Methods to event_service.py
- Read `apps/Server/src/core/services/event_service.py` to understand existing patterns
- Add import: `from src.repository.person_repository import person_repository`
- Add `get_daily_task_summary(self, db, user_id, restaurant_id, person_id, summary_date)` method:
  - Call `self._check_restaurant_access(db, user_id, restaurant_id)` for authorization
  - Compute day boundaries: `date_from = datetime.combine(summary_date, time.min)`, `date_to = datetime.combine(summary_date, time.max)`
  - Call `self.event_repository.get_by_restaurant(db, restaurant_id, type_filter="tarea", responsible_id_filter=person_id, date_from=date_from, date_to=date_to)`
  - Filter results to only `pending` and `overdue` status in Python (since `get_by_restaurant` only supports single status filter)
  - Build and return summary dict with `person_id`, `person_name` (from person_repository.get_by_id), `date`, `total_tasks`, `overdue_count`, and `tasks` list
  - Add INFO logging per project conventions
- Add `get_all_daily_summaries(self, db, user_id, restaurant_id, summary_date)` method:
  - Call `self._check_restaurant_access(db, user_id, restaurant_id)` for authorization
  - Fetch employees: `person_repository.get_by_restaurant(db, restaurant_id, type_filter="employee")`
  - Loop through each employee, call `get_daily_task_summary` for each (skip auth check since already done)
  - Filter out employees with `total_tasks == 0`
  - Return list of summaries
  - Add INFO logging per project conventions

### Step 3: Add REST Endpoints to event_routes.py
- Read `apps/Server/src/adapter/rest/event_routes.py` to understand existing route patterns and ordering
- Add import for new DTOs: `TaskSummaryItemDTO`, `DailyTaskSummaryDTO`
- Add `GET /tasks/daily-summary` endpoint (placed after `/tasks/flag-overdue` and before `/{event_id}`):
  - Query params: `restaurant_id: UUID = Query(...)`, `person_id: UUID = Query(...)`, `summary_date: date = Query(...)`
  - Auth: `current_user: dict = Depends(get_current_user)`
  - Call `event_service.get_daily_task_summary(db, user_id, restaurant_id, person_id, summary_date)`
  - Return summary dict directly
  - Follow existing try/except pattern for PermissionError (403) and ValueError (404)
- Add `GET /tasks/daily-summary/all` endpoint (placed after `/tasks/daily-summary` and before `/{event_id}`):
  - Query params: `restaurant_id: UUID = Query(...)`, `summary_date: date = Query(...)`
  - Auth: `current_user: dict = Depends(get_current_user)`
  - Call `event_service.get_all_daily_summaries(db, user_id, restaurant_id, summary_date)`
  - Return list of summaries
  - Follow existing try/except pattern

### Step 4: Add Tests for Daily Summary Endpoints
- Read `apps/Server/tests/test_event_api.py` to understand existing test patterns
- Read `apps/Server/tests/test_person_api.py` to find `create_mock_person` helper pattern
- Add a `create_mock_person` helper to `test_event_api.py` (or copy pattern from test_person_api.py)
- Add test: `test_get_daily_task_summary_success` — mock person and events, verify response structure, counts, and task details
- Add test: `test_get_daily_task_summary_no_tasks` — verify empty summary when no tasks exist for the date
- Add test: `test_get_daily_task_summary_mixed_statuses` — verify only pending/overdue tasks included, completed tasks excluded
- Add test: `test_get_daily_task_summary_overdue_count` — verify overdue_count matches actual overdue tasks
- Add test: `test_get_all_daily_summaries_success` — mock multiple employees with tasks, verify batch response
- Add test: `test_get_all_daily_summaries_excludes_zero_tasks` — verify employees with no tasks are excluded
- Add test: `test_get_daily_task_summary_unauthorized` — verify 403 when user lacks restaurant access
- All tests follow existing pattern: patch auth repos + event_repository + person_repository, use AsyncClient, assert status codes and response body
- Each test ends with `print("INFO [TestEventAPI]: test_name - PASSED")`

### Step 5: Run Validation Commands
- Run `cd apps/Server && uv run pytest` to validate all tests pass with zero regressions
- Run `cd apps/Client && npx tsc --noEmit` to validate no TypeScript regressions (no client changes expected, but verify)
- Run `cd apps/Client && npm run build` to validate client build succeeds

## Testing Strategy
### Unit Tests
- **DTO validation**: Verify `TaskSummaryItemDTO` and `DailyTaskSummaryDTO` accept valid data and reject invalid data (wrong types, missing required fields)
- **Service logic**: Via API integration tests, verify summary computation (total_tasks count, overdue_count, task filtering by status)
- **Endpoint integration**: Full request/response cycle tests for both summary endpoints with mocked repositories

### Edge Cases
- **No tasks for date**: Employee has no tasks on the requested date — return summary with `total_tasks: 0` and empty tasks list
- **All tasks completed**: Employee has tasks but all are completed — they should be excluded from the summary (only pending/overdue shown)
- **No employees in restaurant**: Batch summary returns empty list
- **Invalid person_id**: Person not found — service should handle gracefully
- **Date boundary precision**: Tasks at exactly midnight (00:00:00) and end of day (23:59:59) must be included
- **Mixed statuses**: Tasks with pending, overdue, and completed statuses — verify only pending and overdue are included

## Acceptance Criteria
- `GET /api/events/tasks/daily-summary?restaurant_id=<uuid>&person_id=<uuid>&summary_date=2026-03-03` returns a structured summary with `person_id`, `person_name`, `date`, `total_tasks`, `overdue_count`, and `tasks` list
- `GET /api/events/tasks/daily-summary/all?restaurant_id=<uuid>&summary_date=2026-03-03` returns summaries for all employees with at least one pending/overdue task
- Summary only includes tasks with status `pending` or `overdue` (completed tasks are excluded)
- `overdue_count` accurately reflects the number of overdue tasks in the summary
- Each task item includes `id`, `description`, `time` (HH:MM format), `status`, and `is_overdue` flag
- Both endpoints require JWT authentication and restaurant membership
- Unauthorized access returns HTTP 403
- All existing tests continue to pass with zero regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest tests/test_event_api.py -v` — Run event-specific tests including new daily summary tests
- `cd apps/Server && uv run pytest` — Run full Server test suite to validate zero regressions
- `cd apps/Server && uv run ruff check src/ tests/` — Run linter to check code quality
- `cd apps/Client && npx tsc --noEmit` — Run Client type check (no client changes expected, verify no regressions)
- `cd apps/Client && npm run build` — Run Client build to validate no regressions

## Notes
- **No new dependencies required** — all functionality uses existing libraries (FastAPI, Pydantic, SQLAlchemy)
- **Route ordering is critical** — the `/tasks/daily-summary` and `/tasks/daily-summary/all` endpoints MUST be declared before `/{event_id}` in event_routes.py to prevent FastAPI from interpreting "tasks" as a UUID path parameter
- **Status filtering** — The existing `get_by_restaurant()` repository method only supports a single `status_filter` parameter, so filtering for both "pending" and "overdue" statuses must be done in the service layer by fetching tasks without status filter and filtering in Python, or by making two repository calls. The recommended approach is to fetch all tasks for the person/date and filter in Python since task counts per employee per day will be small.
- **Wave 5 integration** — The batch summary method (`get_all_daily_summaries`) is specifically designed for the notification cron job that will send WhatsApp/email messages. The response structure should remain stable.
- **Person name inclusion** — The issue spec doesn't include `person_name` in the summary, but it's added for readability in API responses and notification messages. Retrieved via `person_repository.get_by_id()`.
- **Endpoint path adaptation** — The issue spec suggests `GET /api/persons/{person_id}/daily-tasks` but this has been adapted to `GET /api/events/tasks/daily-summary` with query params to maintain consistency with the existing event routing architecture where all task endpoints live under `/api/events/tasks/`.
