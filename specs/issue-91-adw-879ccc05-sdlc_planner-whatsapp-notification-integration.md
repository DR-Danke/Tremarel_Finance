# Feature: WhatsApp Notification Integration

## Metadata
issue_number: `91`
adw_id: `879ccc05`
issue_json: ``

## Feature Description
Integrate a WhatsApp Business API notification system into the RestaurantOS module. The system sends automated messages triggered by events whose `notification_channel` includes "whatsapp". It supports three notification types: (1) daily task lists sent to each employee every morning, (2) document expiration alerts before due dates, and (3) low-stock alerts. The WhatsApp provider (Twilio, Meta Cloud API, etc.) is abstracted behind a `NotificationAdapter` interface for swappability. A `notification_log` table stores all notification attempts for auditability. A manual trigger endpoint enables testing and cron-driven scheduling. This is a backend-focused feature — no new frontend UI pages are required, though the existing Event/Task management page already supports setting `notification_channel` to "whatsapp".

## User Story
As a restaurant manager
I want daily task summaries and operational alerts sent to employees' WhatsApp numbers automatically
So that my team stays informed about their daily duties, approaching document expirations, and low-stock items without needing to check the app

## Problem Statement
Restaurant employees often miss assigned tasks, document expiration deadlines, and low-stock situations because they don't actively check the management platform. There is no push notification mechanism to proactively reach employees on the communication channel they use most — WhatsApp. The event system already tracks `notification_channel` preferences but has no infrastructure to actually dispatch messages through those channels.

## Solution Statement
Build a notification service layer with an abstract `NotificationAdapter` interface, a concrete `WhatsAppAdapter` implementation (stub for now, ready for provider integration), a `NotificationScheduler` that triggers daily task summary sends, message formatting utilities for Spanish (Colombian) messages, a `notification_log` database table for audit trails, and a REST endpoint for manual trigger / cron invocation. The architecture follows Clean Architecture: adapter layer for WhatsApp API, core service layer for notification orchestration, repository layer for logging, and REST routes for the trigger endpoint.

## Relevant Files
Use these files to implement the feature:

**Backend — Existing services (dependencies)**
- `apps/Server/src/core/services/event_service.py` — Contains `get_daily_task_summary()` and `get_all_daily_summaries()` methods that provide the data for WhatsApp daily task messages. The NotificationScheduler will call these methods.
- `apps/Server/src/core/services/person_service.py` — Contains `get_person()` and `get_persons()` for fetching employee WhatsApp numbers from the `whatsapp` field.
- `apps/Server/src/interface/event_dto.py` — DTOs for events and daily task summaries (`DailyTaskSummaryDTO`, `TaskSummaryItemDTO`). Used to type the data flowing into message formatters.
- `apps/Server/src/interface/person_dto.py` — Person DTOs with `whatsapp` field.
- `apps/Server/src/models/event.py` — Event model with `notification_channel` field (already supports "whatsapp").
- `apps/Server/src/models/person.py` — Person model with `whatsapp` field (international format phone number).
- `apps/Server/src/repository/event_repository.py` — Event data access with filtering by restaurant, type, date, responsible_id.
- `apps/Server/src/repository/person_repository.py` — Person data access for fetching employees with WhatsApp numbers.

**Backend — Entry point and routing**
- `apps/Server/main.py` — Application entry point where the new notification router must be registered.
- `apps/Server/src/adapter/rest/dependencies.py` — Shared dependencies (`get_db`, `get_current_user`) used by all routes.
- `apps/Server/src/adapter/rest/event_routes.py` — Existing event routes (reference for REST patterns, authorization, logging).

**Backend — Configuration**
- `apps/Server/src/config/settings.py` — Application settings; new WhatsApp API config vars will be added here.

**Backend — Database schemas (reference for SQL patterns)**
- `apps/Server/database/create_event_table.sql` — Reference for table creation patterns (UUID PKs, restaurant_id FK, timestamps).
- `apps/Server/database/create_person_table.sql` — Person table with `whatsapp` field.

**Backend — Tests (reference for test patterns)**
- `apps/Server/tests/test_event_api.py` — Reference for mock patterns, test fixtures, AsyncClient usage.

**Documentation (conditional)**
- `app_docs/feature-dc999a0b-event-entity-crud-backend.md` — Event entity documentation (notification channel support).
- `app_docs/feature-14633eae-person-entity-crud-backend.md` — Person entity documentation (whatsapp field).
- `app_docs/feature-206ba84f-daily-employee-task-summary.md` — Daily task summary service documentation.
- `app_docs/feature-07ac42cd-task-assignment-recurrence.md` — Task assignment and recurrence documentation.
- `app_docs/feature-0f0d4c36-fastapi-backend-setup.md` — Server setup documentation (adding new routers).

**E2E test references**
- `.claude/commands/test_e2e.md` — How to create and run E2E tests.
- `.claude/commands/e2e/test_event_task_management.md` — Reference E2E test for event/task management page (includes notification channel field).

### New Files
- `apps/Server/src/core/services/notification_service.py` — NotificationAdapter abstract interface and NotificationService orchestrator with retry logic.
- `apps/Server/src/adapter/whatsapp_adapter.py` — WhatsAppAdapter concrete implementation (stub for provider API).
- `apps/Server/src/core/services/notification_scheduler.py` — Scheduled task triggers (send_morning_task_summaries, format_daily_tasks_message, format_low_stock_alert_message, format_document_expiry_message).
- `apps/Server/src/models/notification_log.py` — SQLAlchemy model for the notification_log table.
- `apps/Server/src/repository/notification_log_repository.py` — Repository for creating and querying notification log entries.
- `apps/Server/src/interface/notification_dto.py` — DTOs for notification requests and responses.
- `apps/Server/src/adapter/rest/notification_routes.py` — REST routes for manual trigger endpoint and notification log queries.
- `apps/Server/database/create_notification_log_table.sql` — SQL DDL for the notification_log table.
- `apps/Server/tests/test_notification_api.py` — Tests for notification API endpoints.
- `apps/Server/tests/test_notification_service.py` — Tests for NotificationService and NotificationScheduler business logic.
- `.claude/commands/e2e/test_whatsapp_notification.md` — E2E test spec for validating the notification trigger endpoint works via the API.

## Implementation Plan
### Phase 1: Foundation
Set up the notification_log database table, SQLAlchemy model, and repository. Define the DTOs for notification requests/responses. Create the abstract NotificationAdapter interface and NotificationService with retry logic. These are the foundational building blocks that all other components depend on.

### Phase 2: Core Implementation
Build the WhatsAppAdapter stub implementation. Implement the NotificationScheduler with daily task summary sending logic and message formatting functions (Spanish/Colombian). The scheduler wires together EventService (for daily summaries), PersonService (for WhatsApp numbers), and NotificationService (for dispatch). Add the notification log repository to persist all send attempts.

### Phase 3: Integration
Create the REST notification routes and register them in main.py. Add the manual trigger endpoint for daily summaries. Add notification log query endpoint. Write comprehensive unit tests. Create the E2E test spec for API-level validation.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create the E2E Test Specification
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_event_task_management.md` to understand the E2E test format.
- Create `.claude/commands/e2e/test_whatsapp_notification.md` with test steps for:
  - Calling `POST /api/notifications/send-daily-summaries?restaurant_id={id}` to trigger daily summary sends.
  - Verifying the response includes notification results (sent count, skipped count).
  - Calling `GET /api/notifications/log?restaurant_id={id}` to verify notification log entries were created.
  - Verifying log entries contain channel="whatsapp", correct recipient, message content, and status.
- This is an API-level test (no UI page required) — test steps should use API calls.

### Step 2: Create the notification_log Database Table
- Create `apps/Server/database/create_notification_log_table.sql` with:
  - `id` UUID PRIMARY KEY DEFAULT gen_random_uuid()
  - `restaurant_id` UUID NOT NULL (FK to restaurant with ON DELETE CASCADE)
  - `channel` VARCHAR(50) NOT NULL (e.g., "whatsapp", "email")
  - `recipient` VARCHAR(255) NOT NULL (phone number or email)
  - `message` TEXT (message body)
  - `status` VARCHAR(50) NOT NULL (e.g., "sent", "failed", "pending")
  - `error_message` TEXT (null on success, error details on failure)
  - `event_id` UUID (optional FK to event, for traceability)
  - `created_at` TIMESTAMP WITH TIME ZONE DEFAULT NOW()
  - Indexes on restaurant_id, channel, status, created_at
- Follow existing SQL patterns from `create_event_table.sql`.

### Step 3: Create the NotificationLog SQLAlchemy Model
- Create `apps/Server/src/models/notification_log.py` with:
  - SQLAlchemy model mapping to `notification_log` table.
  - Fields: id (UUID), restaurant_id (UUID), channel (String), recipient (String), message (Text), status (String), error_message (Text nullable), event_id (UUID nullable), created_at (DateTime with timezone).
- Follow existing model patterns from `apps/Server/src/models/event.py`.

### Step 4: Create Notification DTOs
- Create `apps/Server/src/interface/notification_dto.py` with:
  - `NotificationSendDTO` — Input for sending a notification (channel, recipient, message).
  - `NotificationLogResponseDTO` — Response DTO for notification log entries (id, restaurant_id, channel, recipient, message, status, error_message, event_id, created_at).
  - `DailySummaryTriggerResponseDTO` — Response for the manual trigger endpoint (total_employees, sent_count, skipped_count, results list).
- Follow existing DTO patterns from `apps/Server/src/interface/event_dto.py`.

### Step 5: Create the NotificationLog Repository
- Create `apps/Server/src/repository/notification_log_repository.py` with:
  - `create(db, restaurant_id, channel, recipient, message, status, error_message, event_id)` — Insert a new log entry.
  - `get_by_restaurant(db, restaurant_id, channel_filter, status_filter, limit, offset)` — Query logs with optional filters and pagination.
  - `get_by_id(db, log_id)` — Get a single log entry by ID.
- Follow existing repository patterns from `apps/Server/src/repository/event_repository.py`.
- Include proper logging with `print(f"INFO [NotificationLogRepository]: ...")`.

### Step 6: Create the NotificationAdapter Interface and NotificationService
- Create `apps/Server/src/core/services/notification_service.py` with:
  - `NotificationAdapter` abstract base class with `async def send(self, recipient: str, message: str) -> dict` method.
  - `NotificationService` class with:
    - Constructor accepting adapters dict (`{"whatsapp": adapter, "email": adapter}`).
    - `async def send_notification(self, channel, recipient, message) -> dict` — Looks up adapter, calls send, retries once on failure, returns result dict.
    - Proper logging for all operations (INFO for success, ERROR for failures).
  - Instantiate a module-level `notification_service` singleton (similar to `event_service` pattern).
- The NotificationService does NOT depend on the database directly — logging is done by the caller (routes/scheduler).

### Step 7: Create the WhatsAppAdapter
- Create `apps/Server/src/adapter/whatsapp_adapter.py` with:
  - `WhatsAppAdapter(NotificationAdapter)` class.
  - Constructor accepting `api_key: str` and `phone_number_id: str`.
  - `async def send(self, recipient, message) -> dict` — Validates recipient format (international format, starts with "+"), logs the send attempt, returns `{"status": "sent", "recipient": recipient}` (stub implementation).
  - Validate message length (WhatsApp limit: 4096 characters). Truncate with "..." if exceeded.
  - Validate recipient is in international format (starts with "+" followed by digits).
  - Include TODO comment for actual API call implementation (Twilio/Meta Cloud API).
  - Proper logging with `print(f"INFO [WhatsAppAdapter]: ...")`.

### Step 8: Create the NotificationScheduler with Message Formatters
- Create `apps/Server/src/core/services/notification_scheduler.py` with:
  - `format_daily_tasks_message(summary: dict) -> str` — Formats a daily task summary into a Spanish WhatsApp message. Includes greeting, date, task list with overdue indicators, totals.
  - `format_low_stock_alert_message(resource_name: str, current_stock: float, min_stock: float) -> str` — Formats a low-stock alert message in Spanish.
  - `format_document_expiry_message(document_name: str, expiry_date: str, days_remaining: int) -> str` — Formats a document expiration alert in Spanish.
  - `async def send_morning_task_summaries(db: Session, user_id: UUID, restaurant_id: UUID) -> dict` — Main orchestration function:
    1. Call `event_service.get_all_daily_summaries(db, user_id, restaurant_id, date.today())` to get all employee summaries.
    2. For each summary, fetch the person via `person_service.get_person(db, user_id, summary["person_id"])`.
    3. Skip persons without a `whatsapp` field.
    4. Format the message using `format_daily_tasks_message()`.
    5. Call `notification_service.send_notification("whatsapp", person.whatsapp, message)`.
    6. Log each attempt to `notification_log_repository.create(...)`.
    7. Return aggregated results: `{"total_employees": N, "sent_count": M, "skipped_count": K, "results": [...]}`.
  - Proper logging throughout.

### Step 9: Update Application Settings for WhatsApp Config
- Edit `apps/Server/src/config/settings.py` to add:
  - `WHATSAPP_API_KEY: str = ""` (default empty, stub mode).
  - `WHATSAPP_PHONE_NUMBER_ID: str = ""` (default empty).
- These are read from environment variables but default to empty strings (stub adapter works without them).

### Step 10: Create the Notification REST Routes
- Create `apps/Server/src/adapter/rest/notification_routes.py` with:
  - Router prefix: `/api/notifications`, tags: `["Notifications"]`.
  - `POST /api/notifications/send-daily-summaries` — Manual trigger endpoint:
    - Query param: `restaurant_id: UUID` (required).
    - Requires authentication (`get_current_user` dependency).
    - Calls `send_morning_task_summaries(db, user_id, restaurant_id)`.
    - Returns `DailySummaryTriggerResponseDTO`.
    - Handles `PermissionError` (403), `ValueError` (400), general exceptions (500).
  - `GET /api/notifications/log` — Query notification logs:
    - Query params: `restaurant_id: UUID` (required), `channel: Optional[str]`, `status: Optional[str]`, `limit: int = 50`, `offset: int = 0`.
    - Requires authentication.
    - Returns list of `NotificationLogResponseDTO`.
  - Follow existing route patterns from `apps/Server/src/adapter/rest/event_routes.py`.
  - Include proper logging with `print(f"INFO [NotificationRoutes]: ...")`.

### Step 11: Register the Notification Router in main.py
- Edit `apps/Server/main.py` to:
  - Import the notification router: `from src.adapter.rest.notification_routes import router as notification_router`.
  - Register it: `app.include_router(notification_router)`.
  - Add log line: `print("INFO [Main]: Notification router registered")`.
- Follow the existing pattern of imports and router registrations.

### Step 12: Write Unit Tests for NotificationService
- Create `apps/Server/tests/test_notification_service.py` with tests for:
  - `NotificationService.send_notification()` — success case, unknown channel, adapter failure with retry, retry failure.
  - `WhatsAppAdapter.send()` — valid recipient, invalid recipient format, message truncation.
  - `format_daily_tasks_message()` — normal summary, empty tasks, overdue tasks, mixed tasks.
  - `format_low_stock_alert_message()` — normal case.
  - `format_document_expiry_message()` — normal case.
- Use `unittest.mock` for mocking adapters.
- Follow test patterns from `apps/Server/tests/test_event_api.py`.

### Step 13: Write Unit Tests for Notification API
- Create `apps/Server/tests/test_notification_api.py` with tests for:
  - `POST /api/notifications/send-daily-summaries` — success with summaries, no summaries (empty restaurant), permission denied, missing restaurant_id.
  - `GET /api/notifications/log` — list logs, filter by channel, filter by status, empty results.
- Mock `event_service`, `person_service`, `notification_service`, and `notification_log_repository`.
- Use `httpx.AsyncClient` with `ASGITransport` pattern from existing tests.

### Step 14: Run Validation Commands
- Run all backend tests to ensure zero regressions.
- Run frontend type check and build to confirm no breakage.
- Read `.claude/commands/test_e2e.md`, then read and execute the new `.claude/commands/e2e/test_whatsapp_notification.md` E2E test to validate the feature works end-to-end.

## Testing Strategy
### Unit Tests
- **NotificationService**: Test send_notification with valid channel, unknown channel, adapter exception (triggers retry), retry success, retry failure. Verify correct adapter is selected from the adapters dict.
- **WhatsAppAdapter**: Test send with valid international format number, reject invalid format (no "+" prefix), message truncation at 4096 chars, logging output.
- **NotificationScheduler**: Test send_morning_task_summaries orchestration — mock event_service.get_all_daily_summaries to return summaries, mock person_service to return persons with/without whatsapp, verify notification_service.send_notification called for persons with whatsapp only, verify notification_log_repository.create called for each attempt.
- **Message Formatters**: Test format_daily_tasks_message with normal tasks, overdue tasks, zero tasks. Test format_low_stock_alert_message and format_document_expiry_message output.
- **Notification Routes**: Test POST trigger endpoint returns correct counts. Test GET log endpoint returns filtered results. Test auth requirements (401 without token, 403 without restaurant access).
- **NotificationLogRepository**: Test create and query operations with mock database session.

### Edge Cases
- Person has no `whatsapp` field (null) — should be skipped, not cause error.
- Person has empty string `whatsapp` — should be skipped.
- Restaurant has no employees with tasks today — should return `sent_count: 0`.
- WhatsApp number in wrong format (no "+" prefix) — adapter should reject gracefully.
- Message exceeds 4096 characters — should be truncated.
- Adapter raises exception on send — service retries once then logs failure.
- Adapter raises exception on retry — service returns `{"status": "failed"}` and logs.
- Restaurant does not exist or user lacks access — returns 403.
- No notification adapters configured — returns error for unknown channel.

## Acceptance Criteria
- `NotificationAdapter` abstract interface exists with `send(recipient, message)` method.
- `NotificationService` orchestrates dispatch through adapters with single-retry on failure.
- `WhatsAppAdapter` validates international phone format and message length, logs all operations (stub implementation for actual API call).
- `notification_log` table stores all notification attempts with restaurant_id, channel, recipient, message, status, error_message, event_id, created_at.
- `POST /api/notifications/send-daily-summaries?restaurant_id={id}` triggers sending daily task summaries to all employees with WhatsApp numbers.
- `GET /api/notifications/log?restaurant_id={id}` returns paginated notification log entries with optional channel/status filters.
- Daily task summary messages are formatted in Spanish (Colombian) with task descriptions, overdue indicators, and totals.
- Employees without a `whatsapp` field are skipped (not errored).
- All notification attempts are logged to the `notification_log` table.
- All backend tests pass with zero regressions.
- Frontend type check and build succeed with zero regressions.

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest tests/test_notification_service.py -v` — Run notification service unit tests
- `cd apps/Server && uv run pytest tests/test_notification_api.py -v` — Run notification API unit tests
- `cd apps/Server && uv run pytest` — Run ALL Server tests to validate zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate zero regressions
- `cd apps/Client && npm run build` — Run Client build to validate zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_whatsapp_notification.md` to validate this functionality works end-to-end.

## Notes
- **Stub Implementation**: The WhatsAppAdapter is a stub — it logs sends but does not call a real API. This is intentional per the issue spec. A TODO comment marks where the actual Twilio/Meta Cloud API call should go. The adapter is designed to be swapped out when a provider is chosen.
- **Wave 6 Integration**: Wave 6 will wire document expiration alerts to automatically trigger notifications via this service. The `format_document_expiry_message()` formatter is already provided for that use case.
- **Wave 8 Dispatcher**: Wave 8 (#102) adds a general Event Notification Dispatcher that processes ALL due events and dispatches via the appropriate channel. This feature provides the foundation that dispatcher will use.
- **No New Frontend Pages**: This feature is entirely backend. The existing Event/Task management page already has a "Canal de Notificacion" dropdown that supports "WhatsApp". No new navigation items or UI pages are needed.
- **Cron Integration**: The `POST /api/notifications/send-daily-summaries` endpoint is designed to be called by an external cron job (e.g., Render Cron Job, GitHub Actions scheduled workflow) every morning. The implementation does not include the cron setup itself — that is infrastructure configuration.
- **No New Libraries Required**: All dependencies (FastAPI, SQLAlchemy, Pydantic, httpx for future API calls) are already in the project.
