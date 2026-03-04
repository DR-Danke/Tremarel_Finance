# Feature: Low Stock Alert Automation

## Metadata
issue_number: `101`
adw_id: `8035b22e`
issue_json: ``

## Feature Description
When an inventory movement causes a resource's `current_stock` to drop below its `minimum_stock`, the system automatically creates an Event of type `alerta_stock`. This wires together the Resource entity (#80), Inventory Movement (#83), and Event entity (#82) to complete the low-stock alert flow. When stock recovers above minimum via an entry movement, pending alerts are auto-resolved. Duplicate alerts are prevented — only one pending `alerta_stock` per resource at a time.

## User Story
As a restaurant manager
I want the system to automatically create low-stock alert Events when inventory drops below minimum thresholds
So that I'm notified before running out of critical resources and alerts auto-clear when stock is replenished

## Problem Statement
Currently, when a resource's stock drops below minimum after an inventory movement, the system only logs a warning message (line 94-95 of `inventory_service.py`). There is no actionable Event created that could trigger notifications or be tracked by the user. The Event entity already supports `alerta_stock` type but nothing creates these events automatically.

## Solution Statement
Modify `InventoryService.create_movement()` to:
1. After updating stock, check if `current_stock < minimum_stock` and create an `alerta_stock` Event
2. Prevent duplicate alerts by checking for existing pending `alerta_stock` events for the same resource
3. Auto-resolve pending alerts when an entry movement brings stock back above minimum
4. Add `related_resource_id` column to the Event model/schema to link alerts to specific resources

## Relevant Files
Use these files to implement the feature:

**Backend Service Layer (Core Changes):**
- `apps/Server/src/core/services/inventory_service.py` — Main integration point. Add low-stock alert creation and auto-resolution logic after stock update in `create_movement()`
- `apps/Server/src/core/services/event_service.py` — Used to create `alerta_stock` events. The `create_event()` method will be called from InventoryService

**Backend Model Layer:**
- `apps/Server/src/models/event.py` — Add `related_resource_id` column (UUID FK to resource.id, nullable, ON DELETE SET NULL)

**Backend DTO Layer:**
- `apps/Server/src/interface/event_dto.py` — Add `related_resource_id` field to `EventCreateDTO`, `EventUpdateDTO`, and `EventResponseDTO`

**Backend Repository Layer:**
- `apps/Server/src/repository/event_repository.py` — Add `related_resource_id` parameter to `create()` method; add `get_pending_alerts_by_resource()` method for dedup checking; add `resolve_alerts_by_resource()` method for bulk status update

**Database Schema:**
- `apps/Server/database/create_event_table.sql` — Update with `related_resource_id` column and index (reference only)

**Tests:**
- `apps/Server/tests/test_inventory_movement_api.py` — Existing tests, need to update mocks for new event_service dependency
- `apps/Server/tests/test_low_stock_alert.py` — New test file for low-stock alert unit tests

**Documentation References (read before implementing):**
- `app_docs/feature-02529be1-inventory-movement-tracking.md` — Inventory movement service patterns and stock update logic
- `app_docs/feature-dc999a0b-event-entity-crud-backend.md` — Event entity patterns, service, and repository architecture
- `app_docs/feature-8d28116a-resource-entity-crud-backend.md` — Resource model with minimum_stock field
- `app_docs/feature-327dae14-document-expiration-alert-automation.md` — Similar automation pattern (document expiration → vencimiento events)

### New Files
- `apps/Server/tests/test_low_stock_alert.py` — Unit tests for low-stock alert creation, dedup, and auto-resolution
- `apps/Server/database/alter_event_add_related_resource_id.sql` — Migration script to add related_resource_id column

## Implementation Plan
### Phase 1: Foundation
Add `related_resource_id` to the Event entity across all layers:
1. Create SQL migration script for `related_resource_id` column on event table
2. Update Event SQLAlchemy model with the new column
3. Update Event DTOs (Create, Update, Response) with the new field
4. Update EventRepository.create() to accept and pass `related_resource_id`
5. Update EventService.create_event() to pass `related_resource_id` to repository

### Phase 2: Core Implementation
Add alert automation methods to InventoryService:
1. Import event_service and event_repository singletons
2. Add `_create_low_stock_alert()` private method that:
   - Checks for existing pending alerta_stock for the resource (dedup)
   - Creates EventCreateDTO with type=ALERTA_STOCK, Spanish description, whatsapp channel
   - Calls event_service.create_event() (reusing authorization since user already validated)
3. Add `_resolve_low_stock_alerts()` private method that:
   - Queries pending alerta_stock events for the resource
   - Bulk-updates their status to "completed"
4. Wire both methods into `create_movement()` after stock update

### Phase 3: Integration
Ensure existing tests still pass and add new tests:
1. Update existing inventory movement test mocks to account for new event_service dependency
2. Add unit tests for alert creation on exit movement below minimum
3. Add unit tests for duplicate prevention
4. Add unit tests for auto-resolution on entry movement above minimum
5. Add edge case tests (stock equals minimum, already-resolved alerts)

## Step by Step Tasks

### Step 1: Read Reference Documentation
- Read `app_docs/feature-02529be1-inventory-movement-tracking.md` for inventory movement patterns
- Read `app_docs/feature-dc999a0b-event-entity-crud-backend.md` for event entity patterns
- Read `app_docs/feature-327dae14-document-expiration-alert-automation.md` for similar automation pattern (document → event)

### Step 2: Create Database Migration Script
- Create `apps/Server/database/alter_event_add_related_resource_id.sql` with:
  ```sql
  ALTER TABLE event ADD COLUMN related_resource_id UUID REFERENCES resource(id) ON DELETE SET NULL;
  CREATE INDEX idx_event_related_resource ON event(related_resource_id);
  ```

### Step 3: Update Event SQLAlchemy Model
- Edit `apps/Server/src/models/event.py`:
  - Add `related_resource_id` column: `Column(UUID(as_uuid=True), ForeignKey("resource.id", ondelete="SET NULL"), nullable=True)`
  - Place it after `related_document_id`

### Step 4: Update Event DTOs
- Edit `apps/Server/src/interface/event_dto.py`:
  - Add `related_resource_id: Optional[UUID] = Field(None, description="Related resource UUID for stock alerts")` to:
    - `EventCreateDTO`
    - `EventUpdateDTO`
    - `EventResponseDTO`
  - In `EventResponseDTO.compute_is_overdue` model_validator, add `related_resource_id` to the ORM→dict conversion

### Step 5: Update Event Repository
- Edit `apps/Server/src/repository/event_repository.py`:
  - Add `related_resource_id: Optional[UUID] = None` parameter to `create()` method
  - Pass `related_resource_id` to Event constructor
  - Add `get_pending_alerts_by_resource()` method:
    ```python
    def get_pending_alerts_by_resource(self, db: Session, restaurant_id: UUID, resource_id: UUID) -> list[Event]:
        """Get pending alerta_stock events for a specific resource."""
        return db.query(Event).filter(
            Event.restaurant_id == restaurant_id,
            Event.type == "alerta_stock",
            Event.status == "pending",
            Event.related_resource_id == resource_id,
        ).all()
    ```
  - Add `resolve_alerts_by_resource()` method:
    ```python
    def resolve_alerts_by_resource(self, db: Session, restaurant_id: UUID, resource_id: UUID) -> int:
        """Resolve all pending alerta_stock events for a resource."""
        count = db.query(Event).filter(
            Event.restaurant_id == restaurant_id,
            Event.type == "alerta_stock",
            Event.status == "pending",
            Event.related_resource_id == resource_id,
        ).update({"status": "completed", "completed_at": datetime.utcnow()}, synchronize_session="fetch")
        db.commit()
        return count
    ```
  - Add `related_resource_id` to the `bulk_create` data handling (it already uses `**data` so it will pass through automatically)
  - Update the `generate_recurring_instances` data dict in EventService to include `related_resource_id` if present on parent

### Step 6: Update Event Service
- Edit `apps/Server/src/core/services/event_service.py`:
  - Update `create_event()` to pass `related_resource_id=data.related_resource_id` to `event_repository.create()`
  - Update `generate_recurring_instances()` to include `related_resource_id` from parent event in recurring instance data dict

### Step 7: Wire Low-Stock Alerts into Inventory Service
- Edit `apps/Server/src/core/services/inventory_service.py`:
  - Add imports:
    ```python
    from src.interface.event_dto import EventCreateDTO, EventType, EventFrequency
    from src.repository.event_repository import event_repository
    from src.core.services.event_service import event_service
    ```
  - Add `_create_low_stock_alert()` private method:
    - Accept `db: Session`, `user_id: UUID`, `resource: Resource`, `restaurant_id: UUID`
    - Query `event_repository.get_pending_alerts_by_resource()` for dedup
    - If existing alerts found, log and return
    - Build `EventCreateDTO` with:
      - `type=EventType.ALERTA_STOCK`
      - `description=f"Stock bajo: {resource.name} - Actual: {resource.current_stock} {resource.unit}, Mínimo: {resource.minimum_stock} {resource.unit}"`
      - `date=datetime.utcnow()`
      - `frequency=EventFrequency.NONE`
      - `notification_channel="whatsapp"`
      - `related_resource_id=resource.id`
    - Call `event_service.create_event(db, user_id, event_data)`
    - Log WARNING with resource name, current and minimum stock
  - Add `_resolve_low_stock_alerts()` private method:
    - Accept `db: Session`, `resource_id: UUID`, `restaurant_id: UUID`
    - Call `event_repository.resolve_alerts_by_resource()`
    - Log resolved count
  - Modify `create_movement()`:
    - After line 95 (existing low-stock warning), replace/extend with:
      ```python
      if resource.current_stock < resource.minimum_stock:
          print(f"WARNING [InventoryService]: Resource '{resource.name}' is below minimum stock...")
          self._create_low_stock_alert(db, user_id, resource, data.restaurant_id)
      elif resource.current_stock >= resource.minimum_stock:
          self._resolve_low_stock_alerts(db, resource.id, data.restaurant_id)
      ```

### Step 8: Create Unit Tests for Low-Stock Alert Automation
- Create `apps/Server/tests/test_low_stock_alert.py` with tests:
  1. `test_exit_movement_below_minimum_creates_alert` — Exit drops stock below minimum → alerta_stock Event created with correct type, description, notification_channel, related_resource_id
  2. `test_exit_movement_above_minimum_no_alert` — Exit keeps stock above minimum → no alert created
  3. `test_duplicate_alert_prevention` — Second exit while alert exists → no duplicate alert
  4. `test_entry_movement_resolves_alerts` — Entry brings stock above minimum → pending alerts resolved
  5. `test_entry_movement_below_minimum_no_resolution` — Entry but still below minimum → alert not resolved, new alert not duplicated
  6. `test_alert_description_in_spanish` — Verify description format includes resource name, current stock, minimum, and unit in Spanish
  7. `test_alert_notification_channel_whatsapp` — Verify default channel is "whatsapp"
- Follow existing test patterns from `test_inventory_movement_api.py` (mock patching, async client)

### Step 9: Update Existing Inventory Movement Tests
- Update mock patching in `apps/Server/tests/test_inventory_movement_api.py`:
  - Add patches for `src.core.services.inventory_service.event_repository` and `src.core.services.inventory_service.event_service` in tests that create movements
  - Set `event_repository.get_pending_alerts_by_resource.return_value = []` (no existing alerts)
  - Set `event_service.create_event.return_value = MagicMock()` (mock event creation)
  - Ensure existing tests still pass with the new dependencies

### Step 10: Run Validation Commands
- Run all validation commands to ensure zero regressions

## Testing Strategy
### Unit Tests
- **Alert creation**: Verify alerta_stock Event is created when exit movement drops stock below minimum
- **Dedup prevention**: Verify no duplicate alert when pending alert already exists for the resource
- **Auto-resolution**: Verify pending alerts are resolved when entry movement brings stock above minimum
- **Alert content**: Verify description format, notification_channel, related_resource_id, type, and frequency
- **Integration with existing tests**: Ensure all existing inventory movement tests pass with updated mocks

### Edge Cases
- Stock exactly equals minimum (should NOT trigger alert — only when strictly below)
- Multiple exit movements in sequence (only first creates alert)
- Entry movement that doesn't fully recover stock (still below minimum — no resolution)
- Resource with minimum_stock = 0 (should never trigger alert)
- Large decimal quantities (12,4 precision)

## Acceptance Criteria
- [ ] Exit movement that drops stock below minimum creates an `alerta_stock` Event
- [ ] Duplicate alerts are prevented (only one pending alert per resource)
- [ ] Entry movement that brings stock above minimum auto-resolves pending alerts
- [ ] Alert Event description includes resource name, current stock, and minimum in Spanish
- [ ] Alert Event has `notification_channel = "whatsapp"` by default
- [ ] `related_resource_id` field exists on Event model, DTOs, and is populated for stock alerts
- [ ] Logging output at each step for agent debugging
- [ ] All existing tests pass without regressions

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && uv run pytest tests/ -v` — Run all Server tests to validate the feature works with zero regressions
- `cd apps/Client && npx tsc --noEmit` — Run Client type check to validate no type regressions
- `cd apps/Client && npm run build` — Run Client build to validate no build regressions

## Notes
- The Event model already has `EventType.ALERTA_STOCK = "alerta_stock"` in the enum — no new type needed
- The `EventService.create_event()` requires `user_id` for restaurant access authorization. Since the inventory movement is triggered by an authenticated user, we pass that same `user_id` through to event creation — the user already has restaurant access (validated at the top of `create_movement()`)
- This follows the same automation pattern as document expiration alerts (`feature-327dae14`) where document lifecycle events automatically create vencimiento events
- The `related_resource_id` column is added alongside the existing `related_document_id` to maintain a clean linking model. Future alert types (e.g., `alerta_rentabilidad`) can also use this field
- The Event Notification Dispatcher (ROS-024, parallel issue) will process these alert Events and send WhatsApp notifications — this issue only creates the Events
