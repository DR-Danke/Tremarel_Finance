# Feature: Legal Desk Database Schema (11 Tables)

## Metadata
issue_number: `138`
adw_id: `de0cefbe`
issue_json: ``

## Feature Description
Create the complete relational database schema for the Faroo Legal Desk module — a Case Management & Specialist Assignment POC. This establishes 11 PostgreSQL tables with `ld_` prefix covering clients, specialists (with expertise and jurisdictions), cases (with assignments, deliverables, messages, documents), pricing history, and specialist scores. The schema includes performance indexes, foreign key constraints, unique constraints, and `updated_at` triggers. This is Wave 1 (Foundation) of the Legal Desk implementation and has no dependencies.

## User Story
As a Legal Desk developer
I want to have a complete and well-structured database schema for all Legal Desk entities
So that Wave 2 repositories and Wave 3 services can query these tables to power case management, specialist assignment, pricing negotiation, and performance scoring

## Problem Statement
The Faroo Legal Desk module requires persistent storage for multiple interconnected domains: client management, specialist tracking (with expertise areas and jurisdictions), case lifecycle management (with assignments, deliverables, messaging, documents), pricing negotiation history, and specialist performance scoring. Without a properly designed schema, no backend functionality can be built for the Legal Desk module.

## Solution Statement
Create a single comprehensive SQL file (`apps/Server/database/create_legaldesk_tables.sql`) containing all 11 tables with the `ld_` prefix, following the project's existing SQL conventions. The schema uses SERIAL integer primary keys, TIMESTAMPTZ timestamps, proper foreign key cascading, UNIQUE constraints for junction tables, JSONB for AI classification data, and DECIMAL types for financial amounts. Performance indexes cover all frequently queried columns, and `updated_at` triggers auto-maintain timestamp accuracy.

## Relevant Files
Use these files to implement the feature:

- `CLAUDE.md` — Database architecture principles, Clean Architecture layers, and naming conventions
- `apps/Server/database/schema.sql` — Existing core Finance Tracker schema; reference for SQL conventions (trigger function `update_updated_at_column` already defined here)
- `apps/Server/database/create_restaurant_tables.sql` — Reference for multi-table SQL file pattern (CREATE TABLE, indexes, triggers in a single file)
- `app_docs/feature-db5f36c7-database-schema-tables.md` — Documentation on schema organization patterns (referenced by conditional_docs.md)

### New Files
- `apps/Server/database/create_legaldesk_tables.sql` — Complete Legal Desk schema with 11 tables, 13 indexes, and 4 update triggers

## Implementation Plan
### Phase 1: Foundation
- Review existing database SQL files to confirm conventions (timestamp types, trigger function existence, naming patterns)
- Verify the `update_updated_at_column()` trigger function already exists in `schema.sql` to avoid re-creating it

### Phase 2: Core Implementation
- Create `apps/Server/database/create_legaldesk_tables.sql` with all 11 tables in dependency order:
  1. `ld_clients` — standalone entity, no FKs
  2. `ld_specialists` — standalone entity, no FKs
  3. `ld_specialist_expertise` — FK to ld_specialists
  4. `ld_specialist_jurisdictions` — FK to ld_specialists
  5. `ld_cases` — FK to ld_clients
  6. `ld_case_specialists` — FKs to ld_cases, ld_specialists
  7. `ld_case_deliverables` — FKs to ld_cases, ld_specialists
  8. `ld_case_messages` — FK to ld_cases
  9. `ld_case_documents` — FK to ld_cases
  10. `ld_pricing_history` — FK to ld_cases
  11. `ld_specialist_scores` — FKs to ld_specialists, ld_cases
- Add all 13 indexes after table definitions
- Add `updated_at` triggers for tables with `updated_at` columns (ld_clients, ld_specialists, ld_cases, ld_case_deliverables)

### Phase 3: Integration
- Validate SQL syntax and structure
- Confirm all foreign key references resolve correctly (table creation order matters)
- Verify no conflicts with existing schema objects (all prefixed with `ld_`)

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### 1. Review Existing Schema Conventions
- Read `apps/Server/database/schema.sql` to confirm the `update_updated_at_column()` function already exists
- Read `apps/Server/database/create_restaurant_tables.sql` to confirm file structure pattern
- Note: The existing trigger function uses `NOW()` vs the issue spec uses `CURRENT_TIMESTAMP` — use `CURRENT_TIMESTAMP` as specified in the issue since both are equivalent in PostgreSQL

### 2. Create the Legal Desk Schema SQL File
- Create `apps/Server/database/create_legaldesk_tables.sql`
- Add a header comment: `-- Legal Desk Database Schema Tables` and `-- Faroo Legal Desk Wave 1: LD-001`
- Define all 11 tables using `CREATE TABLE IF NOT EXISTS` in the exact order specified:
  1. **ld_clients** — Client entity (company/individual) with contact info, country, industry
  2. **ld_specialists** — Legal specialist entity with experience, hourly rate, workload tracking, overall score
  3. **ld_specialist_expertise** — Junction: specialist ↔ legal_domain with proficiency level; UNIQUE(specialist_id, legal_domain)
  4. **ld_specialist_jurisdictions** — Junction: specialist ↔ country/region with primary flag; UNIQUE(specialist_id, country, region)
  5. **ld_cases** — Core case entity with case_number (UNIQUE, format LD-YYYYMM-NNNN), legal domain, complexity, priority, status, financial fields (budget, estimated_cost, final_quote, margin), deadline, and ai_classification (JSONB)
  6. **ld_case_specialists** — Assignment junction: case ↔ specialist with role, status, fee negotiation fields
  7. **ld_case_deliverables** — Case deliverables with status tracking and completion timestamp
  8. **ld_case_messages** — Case message thread with sender_type, internal flag
  9. **ld_case_documents** — Case document attachments with URL and upload metadata
  10. **ld_pricing_history** — Pricing negotiation audit trail per case
  11. **ld_specialist_scores** — Performance scoring per specialist per case (quality, teamwork, delivery, satisfaction)
- Use exact column definitions, types, defaults, and constraints as specified in the issue

### 3. Add Performance Indexes
- Add all 13 indexes after the table definitions:
  - `idx_ld_cases_status` — Filter cases by status
  - `idx_ld_cases_legal_domain` — Filter cases by legal domain
  - `idx_ld_cases_client` — Join cases to clients
  - `idx_ld_cases_priority` — Filter cases by priority
  - `idx_ld_case_specialists_case` — Join assignments to cases
  - `idx_ld_case_specialists_specialist` — Join assignments to specialists
  - `idx_ld_deliverables_case` — Join deliverables to cases
  - `idx_ld_messages_case` — Join messages to cases
  - `idx_ld_documents_case` — Join documents to cases
  - `idx_ld_pricing_case` — Join pricing history to cases
  - `idx_ld_scores_specialist` — Join scores to specialists
  - `idx_ld_expertise_specialist` — Join expertise to specialists
  - `idx_ld_jurisdictions_specialist` — Join jurisdictions to specialists

### 4. Add Trigger Function and Triggers
- Add `CREATE OR REPLACE FUNCTION update_updated_at_column()` — this is idempotent (`CREATE OR REPLACE`) so safe even though it exists in schema.sql
- Add 4 `updated_at` triggers for tables that have the `updated_at` column:
  - `update_ld_clients_updated_at`
  - `update_ld_specialists_updated_at`
  - `update_ld_cases_updated_at`
  - `update_ld_deliverables_updated_at`

### 5. Validate Schema File
- Run validation commands to confirm file exists, has correct table count, index count, and all expected elements

## Testing Strategy
### Unit Tests
- No unit tests required for a pure SQL schema file
- Schema will be validated by SQL syntax review and structural checks (table count, index count, constraint presence)
- Full validation occurs when the script is executed against Supabase PostgreSQL

### Edge Cases
- `CREATE TABLE IF NOT EXISTS` ensures idempotent execution (safe to re-run)
- `CREATE OR REPLACE FUNCTION` ensures trigger function doesn't conflict with existing definition in schema.sql
- UNIQUE constraints on junction tables prevent duplicate expertise/jurisdiction entries
- ON DELETE CASCADE on specialist-related tables ensures cleanup when a specialist is removed
- ON DELETE CASCADE on case-related tables ensures cleanup when a case is removed
- DECIMAL precision: (15,2) for financial amounts, (10,2) for hourly rates, (5,2) for percentages, (3,2) for scores (0.00-9.99)

## Acceptance Criteria
- [ ] `apps/Server/database/create_legaldesk_tables.sql` exists with valid PostgreSQL syntax
- [ ] All 11 tables are defined with `CREATE TABLE IF NOT EXISTS` and `ld_` prefix
- [ ] Tables created in correct dependency order (referenced tables before referencing tables)
- [ ] All foreign key constraints correctly reference parent tables with appropriate ON DELETE behavior
- [ ] UNIQUE constraints exist on ld_specialist_expertise(specialist_id, legal_domain) and ld_specialist_jurisdictions(specialist_id, country, region)
- [ ] ld_cases.case_number has UNIQUE constraint
- [ ] JSONB type used for ld_cases.ai_classification
- [ ] All 13 indexes are defined with `CREATE INDEX IF NOT EXISTS`
- [ ] Trigger function `update_updated_at_column()` is included with `CREATE OR REPLACE`
- [ ] 4 update triggers are defined for tables with `updated_at` columns
- [ ] Column types match spec exactly (SERIAL PKs, TIMESTAMPTZ timestamps, DECIMAL with specified precision, VARCHAR with specified lengths)

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `ls apps/Server/database/create_legaldesk_tables.sql` — Verify the schema file exists in the correct location
- `grep -c "CREATE TABLE" apps/Server/database/create_legaldesk_tables.sql` — Should return 11 (one per table)
- `grep -c "CREATE INDEX" apps/Server/database/create_legaldesk_tables.sql` — Should return 13 (one per index)
- `grep -c "CREATE TRIGGER" apps/Server/database/create_legaldesk_tables.sql` — Should return 4 (one per trigger)
- `grep "ld_clients" apps/Server/database/create_legaldesk_tables.sql` — Verify ld_clients table exists
- `grep "ld_specialists" apps/Server/database/create_legaldesk_tables.sql` — Verify ld_specialists table exists
- `grep "ld_cases" apps/Server/database/create_legaldesk_tables.sql` — Verify ld_cases table exists
- `grep "ld_case_specialists" apps/Server/database/create_legaldesk_tables.sql` — Verify ld_case_specialists table exists
- `grep "ld_specialist_scores" apps/Server/database/create_legaldesk_tables.sql` — Verify ld_specialist_scores table exists
- `grep "JSONB" apps/Server/database/create_legaldesk_tables.sql` — Verify JSONB type for ai_classification
- `grep "ON DELETE CASCADE" apps/Server/database/create_legaldesk_tables.sql` — Verify cascade delete constraints exist
- `grep "UNIQUE" apps/Server/database/create_legaldesk_tables.sql` — Verify unique constraints exist
- `grep "update_updated_at_column" apps/Server/database/create_legaldesk_tables.sql` — Verify trigger function is referenced
- `cd apps/Server && python -m pytest tests/ 2>/dev/null || echo "No server tests affected"` — Run Server tests to validate zero regressions

## Notes
- **Wave 1 of 6 (Foundation)**: This issue (LD-001) runs in parallel with LD-002 (Seed Data), LD-003, LD-004, LD-005. LD-002 depends on this schema existing.
- **SERIAL vs UUID**: The Legal Desk module uses SERIAL integer primary keys rather than UUIDs used by the core Finance Tracker and RestaurantOS modules. This is by design per the issue specification.
- **No Supabase Auth**: The Legal Desk tables are standalone and do not reference the core `users` table — specialist/client identity is managed independently within the `ld_` namespace.
- **Trigger function idempotency**: The `update_updated_at_column()` function already exists in `schema.sql`, but using `CREATE OR REPLACE` in this file makes the Legal Desk schema self-contained and safe to execute independently.
- **No UI components**: This is a pure database schema task — no frontend changes, no E2E tests required.
