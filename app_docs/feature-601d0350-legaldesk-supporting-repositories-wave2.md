# Legal Desk Supporting Repositories — Wave 2 (Assignment, Deliverable, Message, Analytics)

**ADW ID:** 601d0350
**Date:** 2026-03-04
**Specification:** specs/issue-144-adw-601d0350-sdlc_planner-legaldesk-supporting-repositories-wave2.md

## Overview

Implements four supporting repository classes for the Legal Desk case management module: Assignment (case-specialist links with fee negotiation), Deliverable (milestone tracking with status transitions), Message (case communication threads with internal/external filtering), and Analytics (dashboard aggregations for cases, revenue, and specialist performance). These repositories complete the Wave 2 data access layer and will be consumed by Wave 3 service classes.

## What Was Built

- **LdAssignmentRepository** — CRUD for case-specialist assignments with fee negotiation and status tracking
- **LdDeliverableRepository** — CRUD for case deliverables with status transitions and `completed_at` timestamping
- **LdMessageRepository** — CRUD for case messages with internal/external message filtering
- **LdAnalyticsRepository** — Dashboard aggregation queries (cases by status/domain, revenue pipeline, specialist rankings, average case duration)
- **Unit tests** for all four repositories using mock SQLAlchemy sessions
- **Updated `__init__.py`** to export all four new singleton instances

## Technical Implementation

### Files Modified

- `apps/Server/src/repository/__init__.py`: Added imports and `__all__` exports for `ld_assignment_repository`, `ld_deliverable_repository`, `ld_message_repository`, `ld_analytics_repository`

### Files Created

- `apps/Server/src/repository/ld_assignment_repository.py` (144 lines): `LdAssignmentRepository` class with `create_assignment`, `get_case_specialists`, `get_specialist_cases`, `update_assignment_status`, `update_fees`
- `apps/Server/src/repository/ld_deliverable_repository.py` (113 lines): `LdDeliverableRepository` class with `create`, `get_by_case`, `update` (partial), `update_status`
- `apps/Server/src/repository/ld_message_repository.py` (60 lines): `LdMessageRepository` class with `create`, `get_by_case` (supports `include_internal` flag)
- `apps/Server/src/repository/ld_analytics_repository.py` (147 lines): `LdAnalyticsRepository` class with `count_cases_by_status`, `count_cases_by_domain`, `revenue_pipeline`, `specialist_performance_rankings`, `avg_case_duration`
- `apps/Server/tests/test_ld_assignment_repository.py` (138 lines): Tests for assignment creation, querying, status updates, fee updates, and not-found cases
- `apps/Server/tests/test_ld_deliverable_repository.py` (118 lines): Tests for deliverable creation, partial update, status transitions with `completed_at`, and not-found cases
- `apps/Server/tests/test_ld_message_repository.py` (75 lines): Tests for message creation, internal filtering, and `include_internal` flag behavior
- `apps/Server/tests/test_ld_analytics_repository.py` (124 lines): Tests for all five aggregation methods including empty-result edge cases

### Key Changes

- All repositories follow the established singleton-class pattern: class with methods accepting `db: Session`, comprehensive logging with `print(f"INFO [ClassName]: ...")`, and singleton instance exported at module level
- **Assignment repository** sets `responded_at` timestamp when status transitions from `"pending"` to any other value; handles `Decimal` fee types without float conversion
- **Deliverable repository** implements partial update (only sets fields present in data dict); sets `completed_at = datetime.utcnow()` only when status transitions to `"completed"`
- **Message repository** implements `include_internal` flag on `get_by_case` — when `False`, adds an additional filter excluding `is_internal=True` records
- **Analytics repository** uses `sqlalchemy.func` for `COUNT`, `SUM`, `AVG` aggregations with `COALESCE` for null-safe revenue pipeline; computes average case duration in Python by iterating completed cases and computing `(updated_at - created_at).total_seconds() / 86400`

## How to Use

1. **Import a repository singleton:**
   ```python
   from src.repository import ld_assignment_repository
   ```

2. **Pass a database session to any method:**
   ```python
   assignment = ld_assignment_repository.create_assignment(db, {
       "case_id": 1,
       "specialist_id": 2,
       "role": "lead",
       "proposed_fee": Decimal("1500.00"),
       "fee_currency": "USD",
   })
   ```

3. **Query assignments for a case or specialist:**
   ```python
   specialists = ld_assignment_repository.get_case_specialists(db, case_id=1)
   cases = ld_assignment_repository.get_specialist_cases(db, specialist_id=2)
   ```

4. **Create and query deliverables:**
   ```python
   deliverable = ld_deliverable_repository.create(db, {"case_id": 1, "title": "Draft contract"})
   deliverables = ld_deliverable_repository.get_by_case(db, case_id=1)
   ld_deliverable_repository.update_status(db, deliverable.id, "completed")
   ```

5. **Send and retrieve case messages:**
   ```python
   ld_message_repository.create(db, {"case_id": 1, "sender_type": "specialist", "message": "Ready for review"})
   public_messages = ld_message_repository.get_by_case(db, case_id=1, include_internal=False)
   all_messages = ld_message_repository.get_by_case(db, case_id=1, include_internal=True)
   ```

6. **Get dashboard analytics:**
   ```python
   status_counts = ld_analytics_repository.count_cases_by_status(db)
   pipeline = ld_analytics_repository.revenue_pipeline(db)
   rankings = ld_analytics_repository.specialist_performance_rankings(db)
   avg_days = ld_analytics_repository.avg_case_duration(db)
   ```

## Configuration

No additional configuration required. All repositories use existing SQLAlchemy ORM models and database session infrastructure. No new dependencies added.

## Testing

Run repository tests:
```bash
cd apps/Server && python -m pytest tests/test_ld_assignment_repository.py tests/test_ld_deliverable_repository.py tests/test_ld_message_repository.py tests/test_ld_analytics_repository.py -v
```

Verify module exports:
```bash
cd apps/Server && python -c "from src.repository import ld_assignment_repository, ld_deliverable_repository, ld_message_repository, ld_analytics_repository; print('All repositories imported successfully')"
```

## Notes

- Status transition validation (e.g., preventing invalid deliverable transitions) is intentionally deferred to the Wave 3 service layer. Repositories persist data without enforcing business rules.
- The `fee_type` parameter in `update_fees` maps to the `fee_currency` column on the `LdCaseSpecialist` model.
- `avg_case_duration` uses `updated_at - created_at` since `LdCase` does not have a dedicated `completed_at` column.
- This feature was built in parallel with LD-006 (Core Repositories: Client, Specialist, Case). Both contribute to Wave 2 (Backend Data Access).
