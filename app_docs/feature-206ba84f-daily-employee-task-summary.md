# Daily Employee Task Summary

**ADW ID:** 206ba84f
**Date:** 2026-03-03
**Specification:** specs/issue-86-adw-206ba84f-sdlc_planner-daily-employee-task-summary.md

## Overview

Backend service that generates daily task summaries for restaurant employees. Aggregates all pending and overdue tasks (type="tarea") per person per date, producing structured summaries with counts and details. Includes a batch endpoint for generating summaries across all employees in a restaurant, designed for consumption by Wave 5's notification system (WhatsApp/email daily task lists).

## What Was Built

- **TaskSummaryItemDTO** and **DailyTaskSummaryDTO** Pydantic response DTOs for structured summary validation
- **`get_daily_task_summary()`** service method for single-employee task aggregation
- **`get_all_daily_summaries()`** service method for batch summaries across all restaurant employees
- **`GET /api/events/tasks/daily-summary`** endpoint for individual employee summaries
- **`GET /api/events/tasks/daily-summary/all`** endpoint for batch restaurant-wide summaries
- **7 integration tests** covering success cases, edge cases, and authorization

## Technical Implementation

### Files Modified

- `apps/Server/src/interface/event_dto.py`: Added `TaskSummaryItemDTO` (id, description, time, status, is_overdue) and `DailyTaskSummaryDTO` (person_id, person_name, date, total_tasks, overdue_count, tasks list)
- `apps/Server/src/core/services/event_service.py`: Added `get_daily_task_summary()` and `get_all_daily_summaries()` methods with person_repository import; filters tasks to pending/overdue statuses in Python
- `apps/Server/src/adapter/rest/event_routes.py`: Added two new GET endpoints under `/tasks/daily-summary` and `/tasks/daily-summary/all`, placed before `/{event_id}` to avoid path conflicts
- `apps/Server/tests/test_event_api.py`: Added `create_mock_person` helper and 7 new test cases

### Key Changes

- **Status filtering in service layer**: Since `event_repository.get_by_restaurant()` only supports a single `status_filter`, both pending and overdue tasks are fetched without status filter and filtered in Python (`e.status in ("pending", "overdue")`)
- **Date boundaries**: Uses `datetime.combine(summary_date, time.min)` and `datetime.combine(summary_date, time.max)` for precise day-range queries
- **Batch optimization**: `get_all_daily_summaries()` fetches all employees via `person_repository.get_by_restaurant(type_filter="employee")`, then queries events per employee; employees with zero active tasks are excluded from results
- **Route ordering**: New endpoints declared before `/{event_id}` catch-all to prevent FastAPI from interpreting path segments as UUID parameters
- **Person name enrichment**: Summaries include `person_name` retrieved via `person_repository.get_by_id()` for readability in API responses and notification messages

## How to Use

1. **Single employee summary**: Send a GET request to `/api/events/tasks/daily-summary` with query parameters:
   - `restaurant_id` (UUID) - the restaurant to query
   - `person_id` (UUID) - the employee to summarize
   - `summary_date` (YYYY-MM-DD) - the date to summarize
   - Authorization header with valid JWT token

2. **Batch summary for all employees**: Send a GET request to `/api/events/tasks/daily-summary/all` with query parameters:
   - `restaurant_id` (UUID) - the restaurant to query
   - `summary_date` (YYYY-MM-DD) - the date to summarize
   - Authorization header with valid JWT token

3. **Response structure** (single employee):
   ```json
   {
     "person_id": "uuid",
     "person_name": "John Chef",
     "date": "2026-03-03",
     "total_tasks": 3,
     "overdue_count": 1,
     "tasks": [
       {
         "id": "uuid",
         "description": "Prep salads",
         "time": "09:00",
         "status": "pending",
         "is_overdue": false
       }
     ]
   }
   ```

4. **Batch response**: Returns a list of the above structure, only including employees with at least one pending/overdue task.

## Configuration

No additional configuration required. Uses existing JWT authentication and restaurant membership authorization. Both endpoints require the user to have access to the specified restaurant.

## Testing

Run the event-specific tests:
```bash
cd apps/Server && uv run pytest tests/test_event_api.py -v
```

Test cases cover:
- Successful summary with correct structure and counts
- Empty summary when no tasks exist
- Mixed statuses (completed tasks excluded)
- Accurate overdue count
- Batch summary for multiple employees
- Zero-task employees excluded from batch
- Unauthorized access returns 403

## Notes

- **Wave 5 dependency**: The batch endpoint is specifically designed for the notification cron job that will send daily WhatsApp/email task lists to employees
- **Only pending/overdue tasks**: Completed and other statuses are excluded from summaries
- **Endpoint path convention**: Uses `/api/events/tasks/daily-summary` with query params instead of `/api/persons/{id}/daily-tasks` to maintain consistency with existing event routing architecture
- **No new dependencies**: All functionality uses existing FastAPI, Pydantic, and SQLAlchemy libraries
