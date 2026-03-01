# Meeting Record Data Model

**ADW ID:** 17ff3ddf
**Date:** 2026-02-28
**Specification:** specs/issue-49-adw-17ff3ddf-sdlc_planner-meeting-record-data-model.md

## Overview

Adds the data model layer for storing processed meeting records linked to CRM prospects. Each meeting record holds a transcript reference, structured summary, extracted action items, participant list, and downloadable HTML output. This is CRM-003 in Wave 1, providing the storage target for the transcript processing pipeline (Wave 3) and the foundation for CRUD API endpoints (CRM-005).

## What Was Built

- `meeting_records` PostgreSQL table with full schema (columns, constraints, indexes, trigger)
- `MeetingRecord` SQLAlchemy model (entity-scoped, prospect-linked, soft-deletable)
- Five Pydantic DTOs: Create, Update, Response, ListResponse, Filter
- Comprehensive unit tests covering all DTOs and model basics

## Technical Implementation

### Files Modified

- `apps/Server/database/schema.sql`: Appended `meeting_records` table with UUID PK, FK constraints to `entities` and `prospects` (CASCADE), 4 indexes, and `updated_at` trigger
- `apps/Server/src/models/meeting_record.py`: New SQLAlchemy model mapping all columns with type annotations, FK cascade rules, and `__repr__`
- `apps/Server/src/models/__init__.py`: Registered `MeetingRecord` in model exports and `__all__`
- `apps/Server/src/interface/meeting_record_dto.py`: Five Pydantic DTOs with Field validators and descriptions
- `apps/Server/tests/test_meeting_record_model.py`: 14 unit tests covering DTO validation, edge cases, and model checks

### Key Changes

- **Entity-scoped + prospect-linked**: `entity_id` (FK → entities) and `prospect_id` (FK → prospects) with CASCADE deletes, matching the StageTransition pattern
- **JSON-as-Text strategy**: `action_items` and `participants` stored as `Text` columns (JSON strings) to avoid JSONB complexity. CreateDTO accepts `List[str]` for ergonomic input; ResponseDTO returns raw `str` for client-side parsing
- **Soft delete**: `is_active` boolean flag with dedicated index for filtered queries
- **Composite index**: `(entity_id, prospect_id)` for efficient entity+prospect scoped queries
- **Title constraints**: `min_length=1, max_length=500` enforced at DTO level; `transcript_ref` capped at 1000 chars

## How to Use

1. Import the model: `from src.models.meeting_record import MeetingRecord`
2. Import DTOs: `from src.interface.meeting_record_dto import MeetingRecordCreateDTO, MeetingRecordResponseDTO, ...`
3. Create a meeting record using `MeetingRecordCreateDTO` with required fields: `entity_id`, `prospect_id`, `title`
4. Filter meeting records using `MeetingRecordFilterDTO` with optional: `prospect_id`, `is_active`, `meeting_date_from`, `meeting_date_to`
5. Map ORM objects to responses via `MeetingRecordResponseDTO.model_validate(record, from_attributes=True)`

## Configuration

No new environment variables or configuration required. Uses existing PostgreSQL connection and SQLAlchemy Base.

## Testing

```bash
# Run meeting record tests only
cd apps/Server && uv run pytest tests/test_meeting_record_model.py -v

# Run full server test suite
cd apps/Server && uv run pytest
```

## Notes

- **Backend-only data model** — no UI components, no API endpoints, no service/repository layer yet. CRM-005 will add CRUD API endpoints.
- `transcript_ref` is a string reference (file path or URL), not the full transcript text, keeping the table lean.
- `html_output` stores complete formatted HTML for direct download serving without re-rendering.
- `meeting_date` uses `DATE` type (not `DATETIME`) — meeting-level precision is sufficient.
- No new library dependencies required.
