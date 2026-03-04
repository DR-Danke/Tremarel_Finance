# Feature: Legal Desk Seed Data for Development

## Metadata
issue_number: `139`
adw_id: `7950ad87`
issue_json: ``

## Feature Description
Create seed data SQL for the Legal Desk module covering all core entities: 5 specialists with varied expertise and jurisdictions, 3 clients (company and individual types), and 2 cases at different pipeline stages with deliverables, messages, and pricing history. This data enables meaningful testing of the assignment engine's matching and scoring logic during development.

## User Story
As a developer working on the Legal Desk module
I want pre-populated seed data covering specialists, clients, cases, and related entities
So that I can test the assignment engine's domain/jurisdiction matching and scoring logic with realistic data

## Problem Statement
The Legal Desk schema (LD-001) defines 11 tables but contains no data. Without seed data, developers cannot test repositories, services, or the specialist assignment engine during Wave 2+ implementation. Manual data entry is error-prone and time-consuming.

## Solution Statement
Create a single idempotent SQL seed script (`seed_legaldesk_data.sql`) that inserts realistic data across all core Legal Desk tables in correct foreign key order. The script uses explicit IDs and a wrapping transaction with conflict handling to be safely re-runnable.

## Relevant Files
Use these files to implement the feature:

- `apps/Server/database/create_legaldesk_tables.sql` — The schema definition for all 11 `ld_` tables. Required to understand exact column names, types, constraints, and foreign key relationships for writing valid INSERT statements.
- `app_docs/feature-de0cefbe-legaldesk-database-schema.md` — Legal Desk schema documentation with design decisions, enum values, and table relationships.

### New Files
- `apps/Server/database/seed_legaldesk_data.sql` — The seed data SQL script containing all INSERT statements for Legal Desk development data.

## Implementation Plan
### Phase 1: Foundation
- Read and understand the complete Legal Desk schema (11 tables, all columns, constraints, foreign keys)
- Map the correct insertion order based on foreign key dependencies
- Define realistic seed data values that support assignment engine testing (domain/jurisdiction diversity)

### Phase 2: Core Implementation
- Write the seed SQL script with INSERT statements in dependency order:
  1. `ld_clients` (3 records)
  2. `ld_specialists` (5 records)
  3. `ld_specialist_expertise` (12-15 records, 2-3 per specialist)
  4. `ld_specialist_jurisdictions` (8-10 records, 1-2 per specialist)
  5. `ld_cases` (2 records)
  6. `ld_case_specialists` (2 records)
  7. `ld_case_deliverables` (6 records, 3 per case)
  8. `ld_case_messages` (5 records, 2-3 per case)
  9. `ld_pricing_history` (2 records, 1 per case)
- Wrap in a transaction for atomicity
- Use `ON CONFLICT DO NOTHING` or guard clauses for idempotency

### Phase 3: Integration
- Validate the script parses without syntax errors
- Verify foreign key references are consistent (specialist IDs match expertise/jurisdiction inserts, case IDs match deliverables/messages)
- Ensure data diversity supports assignment engine testing scenarios

## Step by Step Tasks

### Step 1: Read the Legal Desk Schema
- Read `apps/Server/database/create_legaldesk_tables.sql` to confirm all table definitions, column names, types, and constraints
- Read `app_docs/feature-de0cefbe-legaldesk-database-schema.md` for domain context

### Step 2: Create the Seed Data SQL Script
- Create `apps/Server/database/seed_legaldesk_data.sql` with the following structure:
- Add a header comment explaining the purpose and dependencies (requires schema from LD-001)
- Wrap all inserts in `BEGIN; ... COMMIT;` transaction block
- Insert data in this exact order:

**ld_clients (3 records):**
- Client 1: Large tech company (e.g., "TechNova Solutions S.A.S."), client_type='company', country='Colombia', industry='technology'
- Client 2: Mid-size finance company (e.g., "Grupo Financiero Atlas"), client_type='company', country='Mexico', industry='finance'
- Client 3: Individual (e.g., "María Elena Rodríguez"), client_type='individual', country='Colombia'

**ld_specialists (5 records):**
- Specialist 1: Corporate domain, individual type, 15 years exp, hourly_rate=250, max_concurrent_cases=5
- Specialist 2: IP domain, boutique_firm type, 20 years exp, hourly_rate=350, max_concurrent_cases=3
- Specialist 3: Labor domain, individual type, 8 years exp, hourly_rate=180, max_concurrent_cases=6
- Specialist 4: Tax domain, boutique_firm type, 12 years exp, hourly_rate=200, max_concurrent_cases=4
- Specialist 5: Litigation domain, individual type, 3 years exp, hourly_rate=120, max_concurrent_cases=8

**ld_specialist_expertise (12 records, 2-3 per specialist):**
- Specialist 1: corporate (expert), mergers_acquisitions (senior)
- Specialist 2: ip (expert), trademark (senior), patent (intermediate)
- Specialist 3: labor (senior), employment_contracts (intermediate)
- Specialist 4: tax (expert), corporate_tax (senior), international_tax (intermediate)
- Specialist 5: litigation (intermediate), civil_litigation (junior), arbitration (junior)

**ld_specialist_jurisdictions (9 records, 1-2 per specialist):**
- Specialist 1: Colombia (primary), USA
- Specialist 2: Mexico (primary), Spain
- Specialist 3: Colombia (primary)
- Specialist 4: Colombia (primary), Mexico
- Specialist 5: Spain (primary), USA

**ld_cases (2 records):**
- Case 1: case_number='LD-202603-0001', client_id=client 1 (tech company), legal_domain='corporate', complexity='medium', status='new', priority='medium', budget=15000.00
- Case 2: case_number='LD-202603-0002', client_id=client 2 (finance company), legal_domain='ip', complexity='high', status='in_progress', priority='high', budget=30000.00

**ld_case_specialists (2 records):**
- Case 1 + Specialist 1: role='lead', status='proposed', proposed_fee=5000.00
- Case 2 + Specialist 2: role='lead', status='active', proposed_fee=8000.00, agreed_fee=7500.00

**ld_case_deliverables (6 records, 3 per case):**
- Case 1: "Legal Due Diligence Report" (pending), "Corporate Structure Analysis" (pending), "Regulatory Compliance Memo" (pending)
- Case 2: "IP Portfolio Assessment" (completed), "Trademark Registration Filing" (in_progress), "Patent Landscape Analysis" (pending)

**ld_case_messages (5 records):**
- Case 1: 2 messages (1 from client, 1 from specialist)
- Case 2: 3 messages (1 from client, 1 from specialist, 1 internal)

**ld_pricing_history (2 records):**
- Case 1: action='initial_quote', new_amount=15000.00
- Case 2: action='negotiation', previous_amount=8000.00, new_amount=7500.00

### Step 3: Validate the SQL Script
- Review the SQL for syntax correctness
- Verify all foreign key references are internally consistent
- Ensure unique constraints are honored (specialist emails, expertise domain pairs, case numbers)
- Confirm DECIMAL precision fits column definitions (e.g., overall_score DECIMAL(3,2) values ≤ 9.99)

### Step 4: Run Validation Commands
- Run all validation commands listed below to confirm zero regressions

## Testing Strategy
### Unit Tests
- No unit tests required — this is a pure SQL seed data script
- Validation is done by confirming the SQL parses correctly and respects all schema constraints

### Edge Cases
- Idempotency: Script should be re-runnable without errors (use ON CONFLICT DO NOTHING or conditional inserts)
- Foreign key order: Inserts must follow dependency order to avoid FK violations
- DECIMAL(3,2) scores must be ≤ 9.99 (3 total digits, 2 decimal)
- VARCHAR lengths must not exceed defined limits (e.g., case_number VARCHAR(20))
- Unique constraints: no duplicate (specialist_id, legal_domain) in expertise, no duplicate emails

## Acceptance Criteria
- `apps/Server/database/seed_legaldesk_data.sql` exists and contains valid SQL
- Script inserts exactly: 3 clients, 5 specialists, 12+ expertise entries, 9+ jurisdiction entries, 2 cases, 2 case_specialist assignments, 6 deliverables, 5 messages, 2 pricing_history entries
- All foreign key references are internally consistent
- Data covers all 5 required legal domains: corporate, ip, labor, tax, litigation
- Data covers 4 jurisdictions: Colombia, Mexico, USA, Spain
- Case 1 has status 'new' with corporate domain and medium complexity
- Case 2 has status 'in_progress' with ip domain and high complexity
- Case specialist assignments include one 'proposed' and one 'active' status
- Deliverables span different statuses: pending, in_progress, completed
- Script is wrapped in a transaction for atomicity
- Script is idempotent (re-runnable without errors)

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Server && python -c "import sqlparse; stmts = sqlparse.parse(open('database/seed_legaldesk_data.sql').read()); print(f'Parsed {len(stmts)} SQL statements successfully')"` — Validate SQL syntax parses correctly (install sqlparse if needed via `uv add sqlparse`)
- `cd apps/Server && uv run pytest` — Run Server tests to validate zero regressions
- `cd apps/Client && npm run tsc --noEmit` — Run Client type check to validate zero regressions
- `cd apps/Client && npm run build` — Run Client build to validate zero regressions

## Notes
- This script depends on the LD-001 schema (`create_legaldesk_tables.sql`) being executed first. The schema must exist before running seed data.
- The seed data is designed specifically to support testing the assignment engine's matching logic: specialists have overlapping but distinct domain expertise and jurisdictions, enabling tests for best-match scoring.
- Case numbers use format LD-YYYYMM-NNNN as specified in the schema documentation.
- All monetary values use EUR as the default currency per schema defaults.
- The `ld_case_documents` and `ld_specialist_scores` tables are intentionally not seeded — documents require actual file URLs, and scores should be generated after case completion by the scoring engine.
- If `sqlparse` is not available, the SQL validation step can be replaced with a simple `python -c "open('database/seed_legaldesk_data.sql').read()"` to confirm the file is readable.
