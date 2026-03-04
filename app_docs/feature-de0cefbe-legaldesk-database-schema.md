# Legal Desk Database Schema (11 Tables)

**ADW ID:** de0cefbe
**Date:** 2026-03-04
**Specification:** specs/issue-138-adw-de0cefbe-sdlc_planner-legaldesk-database-schema-tables.md

## Overview

Complete relational database schema for the Faroo Legal Desk module — a Case Management & Specialist Assignment POC. This is Wave 1 (Foundation) establishing 11 PostgreSQL tables with `ld_` prefix covering clients, specialists, cases, deliverables, messaging, documents, pricing history, and specialist scoring.

## What Was Built

- 11 PostgreSQL tables with `ld_` prefix in dependency order
- 13 performance indexes on frequently queried columns
- 4 `updated_at` auto-triggers for tables with mutable timestamps
- Idempotent trigger function (`CREATE OR REPLACE`) for self-contained execution
- UNIQUE constraints on junction tables and case numbers
- JSONB column for AI classification data on cases
- Foreign key cascading (CASCADE for owned entities, SET NULL for optional references)

## Technical Implementation

### Files Modified

- `apps/Server/database/create_legaldesk_tables.sql`: New 301-line SQL schema file with all 11 tables, 13 indexes, and 4 triggers

### Table Dependency Order

1. **ld_clients** — Client entity (company/individual), standalone
2. **ld_specialists** — Legal specialist with rates, workload, scoring
3. **ld_specialist_expertise** — Junction: specialist ↔ legal_domain (UNIQUE constraint)
4. **ld_specialist_jurisdictions** — Junction: specialist ↔ country/region (UNIQUE constraint)
5. **ld_cases** — Core case entity with case_number (UNIQUE, format LD-YYYYMM-NNNN), financials, AI classification (JSONB)
6. **ld_case_specialists** — Assignment junction: case ↔ specialist with fee negotiation
7. **ld_case_deliverables** — Deliverables with status tracking and completion timestamp
8. **ld_case_messages** — Message thread with sender_type and internal flag
9. **ld_case_documents** — Document attachments with URL and upload metadata
10. **ld_pricing_history** — Pricing negotiation audit trail
11. **ld_specialist_scores** — Performance scoring (quality, teamwork, delivery, satisfaction)

### Key Design Decisions

- **SERIAL PKs** instead of UUIDs (by design, differs from core Finance Tracker)
- **TIMESTAMPTZ** for all timestamps with `CURRENT_TIMESTAMP` defaults
- **DECIMAL precision**: (15,2) for financial amounts, (10,2) for hourly rates, (5,2) for percentages, (3,2) for scores
- **ON DELETE CASCADE** on specialist/case-related tables for automatic cleanup
- **ON DELETE SET NULL** on deliverables→specialists (preserves deliverable if specialist removed)
- **No references to core `users` table** — specialist/client identity managed within `ld_` namespace

### Indexes

13 indexes covering: case status, legal_domain, client_id, priority, case-specialist joins, deliverable/message/document/pricing/score lookups, and expertise/jurisdiction specialist lookups.

## How to Use

1. Execute the SQL file against your PostgreSQL database:
   ```bash
   psql $DATABASE_URL -f apps/Server/database/create_legaldesk_tables.sql
   ```
2. All tables use `CREATE TABLE IF NOT EXISTS` — safe to re-run
3. The trigger function uses `CREATE OR REPLACE` — no conflict with existing `schema.sql` definition

## Configuration

No environment variables or application configuration required. This is a pure SQL schema file executed directly against the database.

## Testing

- Validate file exists: `ls apps/Server/database/create_legaldesk_tables.sql`
- Count tables: `grep -c "CREATE TABLE" apps/Server/database/create_legaldesk_tables.sql` → 11
- Count indexes: `grep -c "CREATE INDEX" apps/Server/database/create_legaldesk_tables.sql` → 13
- Count triggers: `grep -c "CREATE TRIGGER" apps/Server/database/create_legaldesk_tables.sql` → 4
- Verify JSONB: `grep "JSONB" apps/Server/database/create_legaldesk_tables.sql`
- Verify cascades: `grep "ON DELETE CASCADE" apps/Server/database/create_legaldesk_tables.sql`

## Notes

- **Wave 1 of 6**: This schema is the foundation. Wave 2 (Seed Data) depends on these tables existing.
- **No UI components**: Pure database schema — no frontend changes required.
- **No backend code**: Repository, service, and route layers will be implemented in subsequent waves.
- **Standalone module**: The Legal Desk tables are independent of core Finance Tracker and RestaurantOS schemas.
