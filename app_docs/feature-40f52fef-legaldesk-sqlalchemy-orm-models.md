# Legal Desk SQLAlchemy ORM Models

**ADW ID:** 40f52fef
**Date:** 2026-03-04
**Specification:** specs/issue-140-adw-40f52fef-sdlc_planner-sqlalchemy-orm-models.md

## Overview

Eleven SQLAlchemy ORM models were created for the Legal Desk module, mapping 1:1 to the `ld_` database tables defined in `create_legaldesk_tables.sql`. These models form the Wave 1 (Foundation) data access layer that Wave 2 repositories will use for typed queries, relationship navigation, and CRUD operations on cases, specialists, clients, and related entities.

## What Was Built

- **LdClient** — Client entity model (companies/individuals)
- **LdSpecialist** — Legal specialist model with experience, rates, and workload tracking
- **LdSpecialistExpertise** — Specialist-to-legal-domain junction with proficiency levels
- **LdSpecialistJurisdiction** — Specialist-to-country/region junction with primary flag
- **LdCase** — Core case entity with financials, AI classification (JSONB), and status tracking
- **LdCaseSpecialist** — Case-specialist assignment junction with fee negotiation
- **LdCaseDeliverable** — Case deliverable tracking with status and due dates
- **LdCaseMessage** — Case message thread with sender type and internal flag
- **LdCaseDocument** — Case document attachments with file metadata (BigInteger for file size)
- **LdPricingHistory** — Pricing audit trail per case
- **LdSpecialistScore** — Per-case specialist performance scoring (quality, teamwork, delivery, satisfaction)
- **Model registry** — All 11 models registered in `__init__.py` with grouped imports

## Technical Implementation

### Files Modified

- `apps/Server/src/models/__init__.py`: Added imports and `__all__` entries for all 11 Legal Desk models
- `apps/Server/src/models/ld_client.py`: New — `LdClient` model (38 lines)
- `apps/Server/src/models/ld_specialist.py`: New — `LdSpecialist` model (44 lines)
- `apps/Server/src/models/ld_specialist_expertise.py`: New — `LdSpecialistExpertise` model (34 lines)
- `apps/Server/src/models/ld_specialist_jurisdiction.py`: New — `LdSpecialistJurisdiction` model (35 lines)
- `apps/Server/src/models/ld_case.py`: New — `LdCase` model (54 lines)
- `apps/Server/src/models/ld_case_specialist.py`: New — `LdCaseSpecialist` model (39 lines)
- `apps/Server/src/models/ld_case_deliverable.py`: New — `LdCaseDeliverable` model (42 lines)
- `apps/Server/src/models/ld_case_message.py`: New — `LdCaseMessage` model (33 lines)
- `apps/Server/src/models/ld_case_document.py`: New — `LdCaseDocument` model (34 lines)
- `apps/Server/src/models/ld_pricing_history.py`: New — `LdPricingHistory` model (36 lines)
- `apps/Server/src/models/ld_specialist_score.py`: New — `LdSpecialistScore` model (39 lines)

### Key Changes

- **Integer primary keys**: Legal Desk models use `Integer` PKs (SQL SERIAL) unlike existing Finance Tracker models that use UUIDs, matching the `create_legaldesk_tables.sql` schema
- **JSONB column**: `LdCase.ai_classification` uses `sqlalchemy.dialects.postgresql.JSONB` for structured AI classification data
- **BigInteger for file size**: `LdCaseDocument.file_size_bytes` uses `BigInteger` to match SQL `BIGINT`
- **Unique constraints**: `LdSpecialistExpertise` enforces `(specialist_id, legal_domain)` uniqueness; `LdSpecialistJurisdiction` enforces `(specialist_id, country, region)` uniqueness
- **Cascade deletes**: Foreign keys use `ondelete="CASCADE"` matching the SQL schema, except `LdCaseDeliverable.specialist_id` which uses `ondelete="SET NULL"`
- **Relationship navigation**: Parent models define `relationship()` with `backref` for bidirectional ORM navigation (e.g., `LdCase.specialists` ↔ `LdCaseSpecialist.case`)

## How to Use

1. Import models from the central registry:
   ```python
   from src.models import LdClient, LdCase, LdSpecialist
   ```

2. Use in repository queries:
   ```python
   from sqlalchemy.orm import Session

   def get_case_by_number(db: Session, case_number: str) -> LdCase:
       return db.query(LdCase).filter(LdCase.case_number == case_number).first()
   ```

3. Navigate relationships:
   ```python
   case = db.query(LdCase).get(1)
   client_name = case.client.name          # via backref
   specialists = case.specialists           # list of LdCaseSpecialist
   deliverables = case.deliverables         # list of LdCaseDeliverable
   ```

4. Access JSONB data:
   ```python
   case = db.query(LdCase).get(1)
   classification = case.ai_classification  # dict from JSONB
   ```

## Configuration

No additional configuration required. All models use the existing `Base` class from `src.config.database` and the existing PostgreSQL connection via `DATABASE_URL`.

## Testing

Validate all models import correctly:
```bash
cd apps/Server && python -c "from src.models import LdClient, LdSpecialist, LdSpecialistExpertise, LdSpecialistJurisdiction, LdCase, LdCaseSpecialist, LdCaseDeliverable, LdCaseMessage, LdCaseDocument, LdPricingHistory, LdSpecialistScore; print('All 11 Legal Desk models imported successfully')"
```

Run the full test suite:
```bash
cd apps/Server && pytest tests/
```

## Notes

- These models are Wave 1 (Foundation) of the Legal Desk module (Issue LD-003). Wave 2 repositories will import these models directly for database queries.
- The `ld_` table prefix distinguishes Legal Desk tables from existing Finance Tracker and RestaurantOS tables.
- Models with no `updated_at` column (`LdCaseMessage`, `LdCaseDocument`, `LdPricingHistory`, `LdSpecialistScore`) correctly omit `onupdate` triggers.
- Runs in parallel with LD-001 (schema SQL), LD-002, LD-004, LD-005 with no blocking dependencies.
