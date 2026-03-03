# Feature: Document Expiration Alert Automation

## Metadata
issue_number: `94`
adw_id: `327dae14`
issue_json: ``

## Feature Description
When a document with an expiration date is created or updated in RestaurantOS, the system automatically creates Event records of type `vencimiento` with configurable advance alert periods. Default alerts fire at 30 days before, 7 days before, and on the day of expiration. When those alert event dates arrive, a notification processing endpoint sends alerts via the responsible person's preferred channel (WhatsApp or email). This eliminates manual tracking of permit, contract, and license expirations — critical for restaurant regulatory compliance.

## User Story
As a restaurant manager
I want the system to automatically create expiration alert events when I upload or update documents with expiration dates
So that I never miss a permit, license, or contract renewal deadline

## Problem Statement
Currently, when a document with an `expiration_date` is created, the system only logs a warning if it expires within 30 days. There is no automated mechanism to create alert events or send notifications ahead of expiration. Managers must manually track document deadlines, which is error-prone and risks regulatory non-compliance.

## Solution Statement
Wire the `DocumentService.create_document()` and `update_document()` methods to automatically create `vencimiento`-type Event records at 30-day, 7-day, and same-day intervals before expiration. Add a repository method to find/delete events by `related_document_id` for the update flow. Add a `process_document_expiration_alerts()` function in the notification scheduler that fetches due vencimiento events, resolves the responsible person, and dispatches notifications via the existing adapter infrastructure. Expose this via a `POST /api/notifications/process-expiration-alerts` endpoint for cron or manual triggering.

## Relevant Files
Use these files to implement the feature:

**Backend Service Layer (modify)**
- `apps/Server/src/core/services/document_service.py` — Add `create_expiration_alerts()` method and hook into `create_document()` and `update_document()`. Currently has a WARNING log for near-expiry but no event creation.
- `apps/Server/src/core/services/notification_scheduler.py` — Add `process_document_expiration_alerts()` function following `send_morning_task_summaries()` pattern. Already has `format_document_expiry_message()`, `_determine_channel()`, and `_send_via_channel()` helpers.
- `apps/Server/src/core/services/event_service.py` — Reference for `create_event()` and `get_due_events()` signatures.
- `apps/Server/src/core/services/person_service.py` — Reference for `get_person()` to look up responsible person's contact info.
- `apps/Server/src/core/services/notification_service.py` — Reference for `send_notification()` adapter pattern.

**Repository Layer (modify)**
- `apps/Server/src/repository/event_repository.py` — Add `delete_by_related_document()` method to find and delete existing vencimiento events for a document (needed for update flow).

**REST Adapter Layer (modify)**
- `apps/Server/src/adapter/rest/notification_routes.py` — Add `POST /api/notifications/process-expiration-alerts` endpoint.

**DTOs and Models (read-only reference)**
- `apps/Server/src/interface/event_dto.py` — `EventCreateDTO`, `EventType.VENCIMIENTO`, `EventFrequency.NONE`, `EventStatus`.
- `apps/Server/src/interface/document_dto.py` — `DocumentCreateDTO`, `DocumentUpdateDTO` with `expiration_date` and `person_id` fields.
- `apps/Server/src/models/event.py` — Event SQLAlchemy model with `related_document_id` column.
- `apps/Server/src/models/document.py` — Document SQLAlchemy model.

**Existing Tests (reference for patterns)**
- `apps/Server/tests/test_document_api.py` — Existing document test patterns: mock setup, auth helper, `create_mock_document()`.
- `apps/Server/tests/test_event_api.py` — Existing event test patterns: `create_mock_event()`.
- `apps/Server/tests/test_notification_api.py` — Existing notification test patterns: `AsyncMock` for scheduler functions.

**Conditional Documentation (read for context)**
- `app_docs/feature-95deee5d-document-entity-crud-backend.md` — Document entity architecture reference.
- `app_docs/feature-dc999a0b-event-entity-crud-backend.md` — Event entity architecture reference.
- `app_docs/feature-879ccc05-whatsapp-notification-integration.md` — Notification system architecture reference.
- `app_docs/feature-206ba84f-daily-employee-task-summary.md` — Daily task summary pattern reference.

**E2E Test References (read for format)**
- `.claude/commands/test_e2e.md` — E2E test format and execution instructions.
- `.claude/commands/e2e/test_document_management.md` — Document management E2E reference.
- `.claude/commands/e2e/test_event_task_management.md` — Event management E2E reference.

### New Files
- `apps/Server/tests/test_document_expiration_alert_api.py` — Integration tests for the expiration alert automation (document create/update triggering events, notification processing endpoint).
- `.claude/commands/e2e/test_document_expiration_alerts.md` — E2E test spec validating the full alert automation flow through the UI.

## Implementation Plan
### Phase 1: Foundation
Add the `delete_by_related_document()` method to `EventRepository` so the update flow can clean up old alerts before creating new ones. This is the only new data access method required — all other repository methods already exist.

### Phase 2: Core Implementation
1. Add `create_expiration_alerts()` to `DocumentService` that creates 3 vencimiento events (30d, 7d, 0d) for a given document, skipping any alert dates that are already past.
2. Hook `create_expiration_alerts()` into `create_document()` — call it after successful document creation when `expiration_date` is set.
3. Hook into `update_document()` — when `expiration_date` changes, delete existing vencimiento events via `delete_by_related_document()`, then create new ones.
4. Add `process_document_expiration_alerts()` to `notification_scheduler.py` that fetches due vencimiento events, resolves responsible persons, and dispatches notifications.

### Phase 3: Integration
1. Add `POST /api/notifications/process-expiration-alerts` endpoint in `notification_routes.py` following the `send-daily-summaries` pattern.
2. Write integration tests covering: document create triggers events, document update replaces events, past-date alerts are skipped, notification processing endpoint works.
3. Create E2E test spec for manual validation through the UI.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Read Conditional Documentation
- Read these files for full context before implementation:
  - `app_docs/feature-95deee5d-document-entity-crud-backend.md`
  - `app_docs/feature-dc999a0b-event-entity-crud-backend.md`
  - `app_docs/feature-879ccc05-whatsapp-notification-integration.md`
  - `app_docs/feature-206ba84f-daily-employee-task-summary.md`

### Step 2: Read Existing Source Files
- Read these files to understand current implementations:
  - `apps/Server/src/core/services/document_service.py`
  - `apps/Server/src/core/services/event_service.py`
  - `apps/Server/src/core/services/notification_scheduler.py`
  - `apps/Server/src/core/services/person_service.py`
  - `apps/Server/src/repository/event_repository.py`
  - `apps/Server/src/adapter/rest/notification_routes.py`
  - `apps/Server/src/interface/event_dto.py`
  - `apps/Server/src/interface/document_dto.py`
  - `apps/Server/src/models/event.py`

### Step 3: Create E2E Test Spec
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_document_management.md` to understand the E2E test format
- Create `.claude/commands/e2e/test_document_expiration_alerts.md` with:
  - **User Story**: Restaurant manager creates a document with expiration date and verifies alert events are auto-created
  - **Test Steps**:
    1. Navigate to `/poc/restaurant-os/documents`, verify page loads
    2. Create a new document with `type=permiso`, `expiration_date` set to 60 days from today, and a responsible person
    3. Verify document appears in the list with "Vigente" badge
    4. Navigate to `/poc/restaurant-os/events`
    5. Filter events by type `vencimiento` — verify 3 alert events exist (30-day, 7-day, day-of) linked to the document
    6. Go back to documents, edit the document to change `expiration_date` to 10 days from today
    7. Navigate to events, filter by `vencimiento` — verify old alerts replaced with new ones (only 2: 7-day and day-of, since 30-day would be in the past)
    8. Delete the document — verify alert events are also cleaned up
  - **Success Criteria**: Alert events auto-created on document create, replaced on update, cleaned up on delete
  - **Technical Verification**: Console logs show INFO messages from DocumentService, network requests show POST to events API

### Step 4: Add `delete_by_related_document()` to EventRepository
- Edit `apps/Server/src/repository/event_repository.py`
- Add method `delete_by_related_document(self, db: Session, document_id: UUID) -> int`:
  - Query `Event` where `related_document_id == document_id` and `type == "vencimiento"`
  - Delete all matching records
  - Return count of deleted events
  - Add print log: `INFO [EventRepository]: Deleted {count} vencimiento events for document {document_id}`

### Step 5: Add Expiration Alert Logic to DocumentService
- Edit `apps/Server/src/core/services/document_service.py`
- Add imports: `from datetime import timedelta, datetime, time` and `from src.repository.event_repository import event_repository` and `from src.interface.event_dto import EventType, EventFrequency`
- Add module constant: `DEFAULT_ALERT_WINDOWS = [30, 7, 0]`
- Add method `create_expiration_alerts(self, db: Session, document_id: UUID, expiration_date: date, restaurant_id: UUID, person_id: UUID = None) -> int`:
  - Loop through `DEFAULT_ALERT_WINDOWS`
  - For each `days_before`, compute `alert_date = expiration_date - timedelta(days=days_before)`
  - Skip if `alert_date <= date.today()` (past alerts)
  - Call `event_repository.create()` with:
    - `restaurant_id=restaurant_id`
    - `event_type="vencimiento"`
    - `description=f"Documento vence en {days_before} días"` (or `"Documento vence hoy"` for 0)
    - `event_date=datetime.combine(alert_date, time(8, 0))` (8 AM)
    - `frequency="none"`
    - `responsible_id=person_id`
    - `notification_channel="whatsapp"`
    - `related_document_id=document_id`
  - Return count of created alerts
  - Log: `INFO [DocumentService]: Created {count} expiration alerts for document {document_id}`

- Add method `delete_expiration_alerts(self, db: Session, document_id: UUID) -> int`:
  - Call `event_repository.delete_by_related_document(db, document_id)`
  - Return count of deleted events
  - Log: `INFO [DocumentService]: Deleted {count} expiration alerts for document {document_id}`

### Step 6: Hook Alert Creation into Document Create
- Edit `apps/Server/src/core/services/document_service.py` → `create_document()` method
- After the document is successfully created and before returning:
  - Check if `document.expiration_date is not None`
  - If yes, call `self.create_expiration_alerts(db, document.id, document.expiration_date, document.restaurant_id, document.person_id)`
- Replace the existing WARNING log about near-expiry with the new automation (the alerts now handle this)

### Step 7: Hook Alert Recreation into Document Update
- Edit `apps/Server/src/core/services/document_service.py` → `update_document()` method
- Before updating, fetch the existing document to compare `expiration_date`
- After the document is successfully updated:
  - If `expiration_date` changed (new value differs from old value, or was added/removed):
    - Call `self.delete_expiration_alerts(db, document.id)` to remove old alerts
    - If new `expiration_date` is not None, call `self.create_expiration_alerts(db, document.id, document.expiration_date, document.restaurant_id, document.person_id)`
  - Log: `INFO [DocumentService]: Refreshed expiration alerts for document {document_id}`

### Step 8: Hook Alert Cleanup into Document Delete
- Edit `apps/Server/src/core/services/document_service.py` → `delete_document()` method
- Before or after deleting the document, call `self.delete_expiration_alerts(db, document_id)` to clean up orphaned events
- Log: `INFO [DocumentService]: Cleaned up expiration alerts for deleted document {document_id}`

### Step 9: Add Expiration Alert Processing to Notification Scheduler
- Edit `apps/Server/src/core/services/notification_scheduler.py`
- Add function `process_document_expiration_alerts(db: Session, user_id: UUID, restaurant_id: UUID, target_date: date = None) -> dict`:
  - Default `target_date` to `date.today()` if not provided
  - Call `event_service.get_due_events(db, user_id, restaurant_id, target_date)` to get all due events
  - Filter to events where `type == "vencimiento"` and `related_document_id is not None`
  - For each matching event:
    - Look up the document via `document_repository.get_by_id(db, event.related_document_id)` to get document type/details
    - If `event.responsible_id`, look up person via `person_service.get_person(db, user_id, event.responsible_id)`
    - Determine channel via `_determine_channel(person)`
    - Compute `days_remaining` from the document's `expiration_date` and `target_date`
    - Format message using existing `format_document_expiry_message(document_type, expiration_date, days_remaining)`
    - Send via `_send_via_channel()` (which also logs to notification_log)
  - Return summary dict: `{"processed": N, "sent": N, "skipped": N, "failed": N}`
  - Log: `INFO [NotificationScheduler]: Processed {N} expiration alerts for restaurant {restaurant_id}`

### Step 10: Add Notification Processing Endpoint
- Edit `apps/Server/src/adapter/rest/notification_routes.py`
- Import `process_document_expiration_alerts` from `notification_scheduler`
- Add endpoint `POST /api/notifications/process-expiration-alerts`:
  - Query params: `restaurant_id: UUID` (required), `target_date: date = None` (optional)
  - Requires authentication via `get_current_user`
  - Calls `process_document_expiration_alerts(db, user_id, restaurant_id, target_date)`
  - Returns the summary dict with status 200
  - Log: `INFO [NotificationRoutes]: Processing expiration alerts for restaurant {restaurant_id}`

### Step 11: Write Integration Tests
- Read existing test files for patterns:
  - `apps/Server/tests/test_document_api.py`
  - `apps/Server/tests/test_event_api.py`
  - `apps/Server/tests/test_notification_api.py`
- Create `apps/Server/tests/test_document_expiration_alert_api.py` with tests:
  1. **test_create_document_with_expiration_creates_alerts** — Create document with `expiration_date` 60 days ahead → verify `event_repository.create` called 3 times with correct dates and type=vencimiento
  2. **test_create_document_without_expiration_skips_alerts** — Create document without `expiration_date` → verify no event creation calls
  3. **test_create_document_with_near_expiration_skips_past_alerts** — Create document with `expiration_date` 5 days ahead → verify only 2 alerts created (7-day alert is past, so only 0-day created; actually 5 days ahead means 30-day is past, 7-day is past, only 0-day created)
  4. **test_update_document_expiration_replaces_alerts** — Update document's `expiration_date` → verify old events deleted and new ones created
  5. **test_update_document_without_changing_expiration_no_alert_change** — Update document description only → verify no event deletion/creation
  6. **test_delete_document_cleans_up_alerts** — Delete document → verify `delete_by_related_document` called
  7. **test_process_expiration_alerts_endpoint** — POST to `/api/notifications/process-expiration-alerts` → verify scheduler function called and result returned
  - Follow existing mock patterns: `MagicMock(spec=Session)`, `app.dependency_overrides`, mock repositories
  - Each test prints `INFO [TestDocumentExpirationAlert]: test_name - PASSED`

### Step 12: Run Validation Commands
- `cd apps/Server && uv run pytest` — Run all Server tests to validate zero regressions
- `cd apps/Client && npm run tsc --noEmit` — Type check Client (no client changes expected, but verify)
- `cd apps/Client && npm run build` — Build Client (no client changes expected, but verify)
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_document_expiration_alerts.md` E2E test

## Testing Strategy
### Unit Tests
- **DocumentService.create_expiration_alerts()**: Verify correct number of events created based on expiration date distance, verify skipping of past alerts, verify correct event field values (type=vencimiento, frequency=none, notification_channel=whatsapp, related_document_id set).
- **DocumentService create/update/delete hooks**: Verify `create_expiration_alerts` called when `expiration_date` present on create, verify `delete_expiration_alerts` + `create_expiration_alerts` called when `expiration_date` changes on update, verify `delete_expiration_alerts` called on delete.
- **EventRepository.delete_by_related_document()**: Verify correct SQL filter on `related_document_id` and `type=vencimiento`, verify return count.
- **process_document_expiration_alerts()**: Verify filtering of due events to vencimiento type, verify person lookup and channel determination, verify notification dispatch via `_send_via_channel`, verify summary dict counts.
- **Notification endpoint**: Verify authentication required, verify scheduler function called with correct params, verify response format.

### Edge Cases
- Document created with `expiration_date` in the past → all 3 alerts skipped (0 events created)
- Document created with `expiration_date` exactly today → only the 0-day alert has `alert_date == today`, which is skipped by `<=` check → 0 events created
- Document created with `expiration_date` tomorrow → only the 0-day alert has `alert_date == tomorrow` (future) → 1 event created
- Document created with `expiration_date` 8 days ahead → 7-day alert is tomorrow (future), 0-day is 8 days ahead → 2 events created
- Document created with `expiration_date` 31 days ahead → all 3 alerts are future → 3 events created
- Document updated to remove `expiration_date` (set to None) → old alerts deleted, no new ones created
- Document with no `person_id` → events created with `responsible_id=None`, notifications skipped during processing
- Processing alerts when responsible person has no WhatsApp/email → notification skipped
- Processing alerts when no vencimiento events are due → empty result, no errors

## Acceptance Criteria
1. Creating a document with `expiration_date` auto-creates up to 3 vencimiento events at 30-day, 7-day, and 0-day intervals
2. Alert events that would fall on or before today are not created
3. Each alert event has `type=vencimiento`, `frequency=none`, `notification_channel=whatsapp`, and `related_document_id` set to the document ID
4. Alert descriptions are in Spanish: "Documento vence en 30 días", "Documento vence en 7 días", "Documento vence hoy"
5. Updating a document's `expiration_date` deletes all old vencimiento events for that document and creates new ones
6. Deleting a document cleans up associated vencimiento events
7. `POST /api/notifications/process-expiration-alerts?restaurant_id={id}` processes due vencimiento events and sends notifications via the responsible person's preferred channel
8. The endpoint requires JWT authentication
9. All operations produce INFO-level print logs for agent debugging
10. All existing tests continue to pass (zero regressions)

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest` — Run Server tests to validate the feature works with zero regressions
- `cd apps/Client && npm run tsc --noEmit` — Run Client type check to validate the feature works with zero regressions
- `cd apps/Client && npm run build` — Run Client build to validate the feature works with zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_document_expiration_alerts.md` E2E test to validate this functionality works

## Notes
- The `related_document_id` column on the `event` table has no FK constraint (loose link by design). This means orphaned events won't cause integrity errors if documents are deleted without cleanup — but the cleanup step in `delete_document()` ensures no orphans.
- The `format_document_expiry_message()` function already exists in `notification_scheduler.py` and formats Spanish messages with emoji. Reuse it in `process_document_expiration_alerts()`.
- The WhatsApp adapter is currently a stub (logs sends, no external API call). This is expected — real provider integration (Twilio/Meta Cloud API) is handled separately.
- Wave 7 will add permit type presets that customize alert schedules per document type. The current `DEFAULT_ALERT_WINDOWS = [30, 7, 0]` constant is designed to be easily replaceable with per-type configuration.
- No new dependencies are needed. All required imports are already available in the codebase.
- No frontend changes are required for this feature — alert events appear automatically in the existing events page. The E2E test validates this through the existing UI.
