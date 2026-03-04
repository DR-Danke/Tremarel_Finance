# Low Stock Alert Automation

**ADW ID:** 8035b22e
**Date:** 2026-03-04
**Specification:** specs/issue-101-adw-8035b22e-sdlc_planner-low-stock-alert-automation.md

## Overview

Automatic low-stock alert Events are now created when an inventory movement causes a resource's `current_stock` to drop below its `minimum_stock`. The system creates `alerta_stock` Events linked to the affected resource, prevents duplicate alerts, and auto-resolves pending alerts when stock recovers above the minimum threshold.

## What Was Built

- Automatic `alerta_stock` Event creation on exit movements that drop stock below minimum
- Duplicate alert prevention (only one pending alert per resource at a time)
- Auto-resolution of pending alerts when entry movements bring stock back above minimum
- `related_resource_id` column on the Event model to link alerts to specific resources
- Full DTO and repository support for the new field
- 521 lines of unit tests covering all alert scenarios and edge cases

## Technical Implementation

### Files Modified

- `apps/Server/database/alter_event_add_related_resource_id.sql`: New migration adding `related_resource_id UUID` column with FK to `resource(id)` and index
- `apps/Server/src/models/event.py`: Added `related_resource_id` column (`UUID FK → resource.id, ON DELETE SET NULL, nullable`)
- `apps/Server/src/interface/event_dto.py`: Added `related_resource_id` field to `EventCreateDTO`, `EventUpdateDTO`, `EventResponseDTO`, and ORM→dict conversion
- `apps/Server/src/repository/event_repository.py`: Added `related_resource_id` param to `create()`, plus new `get_pending_alerts_by_resource()` and `resolve_alerts_by_resource()` methods
- `apps/Server/src/core/services/event_service.py`: Passes `related_resource_id` through `create_event()`, `update_event()`, and `generate_recurring_instances()`
- `apps/Server/src/core/services/inventory_service.py`: Added `_create_low_stock_alert()` and `_resolve_low_stock_alerts()` private methods, wired into `create_movement()` after stock update
- `apps/Server/tests/test_low_stock_alert.py`: New comprehensive test file (521 lines)
- `apps/Server/tests/test_inventory_movement_api.py`: Updated mocks for new event dependencies
- `apps/Server/tests/test_document_expiration_alert_api.py`: Minor mock update
- `apps/Server/tests/test_event_api.py`: Minor mock update
- `apps/Server/tests/test_permit_presets_api.py`: Minor mock update

### Key Changes

- **Alert creation flow**: After `create_movement()` updates resource stock, if `current_stock < minimum_stock`, `_create_low_stock_alert()` checks for existing pending alerts (dedup), then creates an `EventCreateDTO` with `type=ALERTA_STOCK`, Spanish description, `notification_channel="whatsapp"`, and `related_resource_id`
- **Auto-resolution flow**: If after a movement `current_stock >= minimum_stock`, `_resolve_low_stock_alerts()` bulk-updates all pending `alerta_stock` events for that resource to `status="completed"` with `completed_at` timestamp
- **Circular import avoidance**: `event_service` is imported inside `_create_low_stock_alert()` to prevent circular dependency between inventory and event services
- **Repository queries**: `get_pending_alerts_by_resource()` filters by `restaurant_id`, `type="alerta_stock"`, `status="pending"`, and `related_resource_id`; `resolve_alerts_by_resource()` uses the same filter with a bulk `.update()` call

## How to Use

1. **Run the migration** to add the `related_resource_id` column:
   ```sql
   -- Execute alter_event_add_related_resource_id.sql against the database
   ALTER TABLE event ADD COLUMN related_resource_id UUID REFERENCES resource(id) ON DELETE SET NULL;
   CREATE INDEX idx_event_related_resource ON event(related_resource_id);
   ```
2. **Create inventory movements** as normal via `POST /api/inventory-movements`
3. When an exit movement drops a resource below minimum stock, an `alerta_stock` Event is automatically created
4. When an entry movement brings stock back above minimum, any pending alerts for that resource are automatically resolved
5. View alerts via `GET /api/events` filtered by `type=alerta_stock`

## Configuration

- **Alert threshold**: Triggers when `current_stock < minimum_stock` (strictly below, not equal)
- **Notification channel**: Defaults to `"whatsapp"` for stock alerts
- **Description language**: Spanish (e.g., `"Stock bajo: Harina - Actual: 3.0 kg, Mínimo: 5.0 kg"`)
- **Dedup scope**: One pending `alerta_stock` per resource per restaurant

## Testing

Run the low-stock alert tests:
```bash
cd apps/Server && uv run pytest tests/test_low_stock_alert.py -v
```

Test classes and scenarios covered:
- `TestLowStockAlertCreation`: Exit below minimum creates alert, exit above minimum skips alert
- `TestDuplicateAlertPrevention`: No duplicate when pending alert exists
- `TestAlertAutoResolution`: Entry above minimum resolves alerts, entry still below minimum does not resolve
- `TestAlertContent`: Spanish description format, whatsapp channel, related_resource_id linkage
- `TestEdgeCases`: Stock equals minimum (no alert), minimum_stock=0, large decimal quantities, multiple resources independently tracked, rapid sequential movements

## Notes

- This follows the same automation pattern as document expiration alerts (`feature-327dae14`) where document lifecycle events automatically create `vencimiento` events
- The Event Notification Dispatcher (future issue) will process these `alerta_stock` Events and send actual WhatsApp notifications — this feature only creates the Events
- The `related_resource_id` column sits alongside the existing `related_document_id`, maintaining a clean linking model for different alert types
- `EventType.ALERTA_STOCK` already existed in the enum — no new type was needed
