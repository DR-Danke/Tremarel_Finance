# Feature: Legal Desk Frontend TypeScript Types & Maps

## Metadata
issue_number: `142`
adw_id: `e9ee37e2`
issue_json: ``

## Feature Description
Define all Legal Desk TypeScript types for the frontend application: 14 string literal union types covering all database enums, ~25 interfaces covering all API response and request shapes (matching the 11 Legal Desk database tables), plus label and color maps for UI rendering (status badges, priority chips, domain labels, complexity indicators). All types are re-exported from the central types index file. This is a pure foundation/types task with no UI component work.

## User Story
As a frontend developer building Legal Desk UI components
I want comprehensive, type-safe TypeScript definitions for all Legal Desk entities
So that I can build type-safe services, hooks, and UI components in later waves without runtime type errors

## Problem Statement
The Legal Desk module has an 11-table database schema (ld_* tables) already created in Wave 1, but the frontend has no TypeScript type definitions to represent these entities. Without these types, Wave 5 (services/hooks) and Wave 6 (UI components) cannot be built with type safety.

## Solution Statement
Create a single comprehensive types file `apps/Client/src/types/legaldesk.ts` containing all 14 string literal unions matching database enums, ~25 interfaces matching all database table columns and API response shapes, and label/color constant maps for UI rendering. Re-export everything from the central `apps/Client/src/types/index.ts`.

## Relevant Files
Use these files to implement the feature:

- `apps/Client/src/types/index.ts` — Central re-export hub for all frontend types. Must be updated to re-export Legal Desk types. Contains existing patterns showing how type aliases, interfaces, and constants are organized and re-exported.
- `apps/Client/src/types/person.ts` — Reference for type file patterns: string literal unions, entity/create/update/filter interfaces.
- `apps/Client/src/types/restaurant.ts` — Reference for type file patterns with re-export syntax.
- `apps/Server/database/create_legaldesk_tables.sql` — The source of truth for all 11 Legal Desk tables. Each interface must match the corresponding table columns exactly (field names, optionality, types).
- `app_docs/feature-de0cefbe-legaldesk-database-schema.md` — Documentation of the Legal Desk database schema design decisions.

### New Files
- `apps/Client/src/types/legaldesk.ts` — Complete Legal Desk TypeScript types file with all unions, interfaces, and maps.

## Implementation Plan
### Phase 1: Foundation
- Read the database schema SQL (`create_legaldesk_tables.sql`) to understand all 11 tables, their columns, types, nullability, defaults, and relationships.
- Read the existing types patterns in `index.ts`, `person.ts`, and `restaurant.ts` to follow conventions.

### Phase 2: Core Implementation
- Create `apps/Client/src/types/legaldesk.ts` with:
  1. All 14 string literal union types
  2. All entity interfaces matching database tables (using `number` for SERIAL IDs)
  3. Detail/extended interfaces (e.g., `LdCaseDetail` extending `LdCase` with nested relations)
  4. Create/Update/Filter interfaces for CRUD operations
  5. Dashboard stats and candidate interfaces for specialized API responses
  6. Label and color constant maps for all enums used in UI rendering

### Phase 3: Integration
- Update `apps/Client/src/types/index.ts` to re-export all Legal Desk types using the established `export type { ... } from './legaldesk'` pattern for types and `export { ... } from './legaldesk'` for constants.
- Run TypeScript type checking to validate zero errors.

## Step by Step Tasks

### Step 1: Review Database Schema and Existing Patterns
- Read `apps/Server/database/create_legaldesk_tables.sql` to catalog all 11 tables, columns, types, and constraints.
- Read `apps/Client/src/types/index.ts`, `apps/Client/src/types/person.ts` to understand existing conventions.
- Map SQL types to TypeScript: `SERIAL` → `number`, `VARCHAR` → `string`, `TEXT` → `string`, `BOOLEAN` → `boolean`, `DECIMAL` → `number`, `INTEGER` → `number`, `BIGINT` → `number`, `DATE` → `string`, `TIMESTAMPTZ` → `string`, `JSONB` → `Record<string, unknown>`.

### Step 2: Create Legal Desk Types File
- Create `apps/Client/src/types/legaldesk.ts` with the following sections in order:

**2a. String Literal Union Types (14):**
- `CaseStatus` — 11 values: new, classifying, open, assigning, active, in_progress, review, negotiating, completed, closed, archived
- `CaseType` — 2 values: advisory, litigation
- `LegalDomain` — 10 values: corporate, ip, labor, tax, litigation, real_estate, immigration, regulatory, data_privacy, commercial
- `CaseComplexity` — 4 values: low, medium, high, critical
- `CasePriority` — 4 values: low, medium, high, urgent
- `OriginationChannel` — 2 values: direct, referral
- `SpecialistStatus` — 3 values: active, inactive, on_leave
- `SpecialistType` — 2 values: individual, boutique_firm
- `ProficiencyLevel` — 3 values: junior, intermediate, expert
- `AssignmentRole` — 4 values: lead, support, reviewer, consultant
- `AssignmentStatus` — 5 values: proposed, accepted, rejected, active, completed
- `DeliverableStatus` — 5 values: pending, in_progress, review, completed, cancelled
- `PricingAction` — 6 values: proposal, counter, accept, reject, adjust, final
- `ClientType` — 2 values: company, individual

**2b. Entity Interfaces (matching ld_* tables):**
- `LdClient` — matches `ld_clients` table (id, name, client_type, contact_email, contact_phone, country, industry, notes, is_active, created_at, updated_at)
- `LdSpecialist` — matches `ld_specialists` table (id, full_name, email, phone, years_experience, hourly_rate, currency, max_concurrent_cases, current_workload, overall_score, is_active, created_at, updated_at)
- `LdSpecialistExpertise` — matches `ld_specialist_expertise` (id, specialist_id, legal_domain, proficiency_level, years_in_domain, created_at)
- `LdSpecialistJurisdiction` — matches `ld_specialist_jurisdictions` (id, specialist_id, country, region, is_primary, created_at)
- `LdCase` — matches `ld_cases` table (id, case_number, title, description, client_id, legal_domain, complexity, priority, status, budget, estimated_cost, final_quote, margin_percentage, deadline, ai_classification, created_at, updated_at). Note: use `budget` not `client_budget`, `margin_percentage` not `faroo_margin_pct` — match the actual SQL column names.
- `LdCaseSpecialist` — matches `ld_case_specialists` (id, case_id, specialist_id, role, status, proposed_fee, agreed_fee, fee_currency, assigned_at, responded_at)
- `LdCaseDeliverable` — matches `ld_case_deliverables` (id, case_id, specialist_id, title, description, status, due_date, completed_at, created_at, updated_at)
- `LdCaseMessage` — matches `ld_case_messages` (id, case_id, sender_type, sender_name, message, is_internal, created_at)
- `LdCaseDocument` — matches `ld_case_documents` (id, case_id, file_name, file_url, file_type, file_size_bytes, uploaded_by, created_at)
- `LdPricingHistory` — matches `ld_pricing_history` (id, case_id, action, previous_amount, new_amount, currency, changed_by, notes, created_at)
- `LdSpecialistScore` — matches `ld_specialist_scores` (id, specialist_id, case_id, quality_score, teamwork_score, delivery_score, satisfaction_score, overall_score, feedback, scored_at)

**2c. Detail/Extended Interfaces:**
- `LdCaseDetail extends LdCase` — adds: client (LdClient optional), specialists (LdCaseSpecialist[]), deliverables (LdCaseDeliverable[]), messages (LdCaseMessage[]), documents (LdCaseDocument[]), pricing_history (LdPricingHistory[])
- `LdSpecialistDetail extends LdSpecialist` — adds: expertise (LdSpecialistExpertise[]), jurisdictions (LdSpecialistJurisdiction[]), scores (LdSpecialistScore[])

**2d. Create/Update Interfaces:**
- `LdClientCreate` — required: name; optional: client_type, contact_email, contact_phone, country, industry, notes
- `LdClientUpdate` — all optional: name, client_type, contact_email, contact_phone, country, industry, notes, is_active
- `LdSpecialistCreate` — required: full_name, email; optional: phone, years_experience, hourly_rate, currency, max_concurrent_cases
- `LdSpecialistUpdate` — all optional: full_name, email, phone, years_experience, hourly_rate, currency, max_concurrent_cases, is_active
- `LdCaseCreate` — required: title, client_id, legal_domain; optional: description, complexity, priority, budget, estimated_cost, deadline
- `LdCaseUpdate` — all optional: title, description, legal_domain, complexity, priority, status, budget, estimated_cost, final_quote, margin_percentage, deadline
- `LdCaseSpecialistCreate` — required: case_id, specialist_id; optional: role, proposed_fee, fee_currency
- `LdCaseSpecialistUpdate` — all optional: role, status, proposed_fee, agreed_fee, fee_currency
- `LdCaseDeliverableCreate` — required: case_id, title; optional: specialist_id, description, due_date
- `LdCaseDeliverableUpdate` — all optional: title, description, status, specialist_id, due_date
- `LdCaseMessageCreate` — required: case_id, sender_type, message; optional: sender_name, is_internal
- `LdCaseDocumentCreate` — required: case_id, file_name, file_url; optional: file_type, file_size_bytes, uploaded_by
- `LdPricingHistoryCreate` — required: case_id, action, new_amount; optional: previous_amount, currency, changed_by, notes
- `LdSpecialistScoreCreate` — required: specialist_id, case_id; optional: quality_score, teamwork_score, delivery_score, satisfaction_score, overall_score, feedback
- `LdSpecialistExpertiseCreate` — required: specialist_id, legal_domain; optional: proficiency_level, years_in_domain
- `LdSpecialistJurisdictionCreate` — required: specialist_id, country; optional: region, is_primary

**2e. Filter Interfaces:**
- `LdCaseFilters` — optional: status, legal_domain, priority, complexity, client_id
- `LdSpecialistFilters` — optional: is_active, legal_domain
- `LdClientFilters` — optional: client_type, is_active, country

**2f. List Response Interfaces:**
- `LdCaseListResponse` — { cases: LdCase[], total: number }
- `LdSpecialistListResponse` — { specialists: LdSpecialist[], total: number }
- `LdClientListResponse` — { clients: LdClient[], total: number }

**2g. Dashboard/Specialized Interfaces:**
- `LdDashboardStats` — { total_cases: number, active_cases: number, total_specialists: number, total_clients: number, cases_by_status: Record<CaseStatus, number>, cases_by_domain: Record<LegalDomain, number> }
- `LdSpecialistCandidate` — { specialist: LdSpecialist, expertise_match: LdSpecialistExpertise | null, availability_score: number, overall_score: number }

**2h. Label and Color Constant Maps:**
- `CASE_STATUS_LABELS: Record<CaseStatus, string>` — Human-readable labels for all 11 case statuses
- `CASE_STATUS_COLORS: Record<CaseStatus, string>` — Hex color codes for status badges (use MUI-palette-inspired colors)
- `LEGAL_DOMAIN_LABELS: Record<LegalDomain, string>` — Human-readable labels for all 10 legal domains (Corporate, Intellectual Property, Labor, Tax, Litigation, Real Estate, Immigration, Regulatory, Data Privacy, Commercial)
- `LEGAL_DOMAIN_COLORS: Record<LegalDomain, string>` — Hex color codes for domain chips
- `CASE_PRIORITY_LABELS: Record<CasePriority, string>` — Low, Medium, High, Urgent
- `CASE_PRIORITY_COLORS: Record<CasePriority, string>` — Green→Yellow→Orange→Red spectrum
- `CASE_COMPLEXITY_LABELS: Record<CaseComplexity, string>` — Low, Medium, High, Critical
- `CASE_COMPLEXITY_COLORS: Record<CaseComplexity, string>` — Blue→Yellow→Orange→Red spectrum
- `SPECIALIST_STATUS_LABELS: Record<SpecialistStatus, string>` — Active, Inactive, On Leave
- `SPECIALIST_STATUS_COLORS: Record<SpecialistStatus, string>`
- `ASSIGNMENT_STATUS_LABELS: Record<AssignmentStatus, string>` — Proposed, Accepted, Rejected, Active, Completed
- `ASSIGNMENT_STATUS_COLORS: Record<AssignmentStatus, string>`
- `DELIVERABLE_STATUS_LABELS: Record<DeliverableStatus, string>` — Pending, In Progress, Review, Completed, Cancelled
- `DELIVERABLE_STATUS_COLORS: Record<DeliverableStatus, string>`
- `PROFICIENCY_LEVEL_LABELS: Record<ProficiencyLevel, string>` — Junior, Intermediate, Expert
- `ASSIGNMENT_ROLE_LABELS: Record<AssignmentRole, string>` — Lead, Support, Reviewer, Consultant
- `CASE_TYPE_LABELS: Record<CaseType, string>` — Advisory, Litigation
- `CLIENT_TYPE_LABELS: Record<ClientType, string>` — Company, Individual
- `PRICING_ACTION_LABELS: Record<PricingAction, string>` — Proposal, Counter, Accept, Reject, Adjust, Final

### Step 3: Update Types Index Re-exports
- Update `apps/Client/src/types/index.ts` to add re-exports at the bottom:
  - Use `export type { ... } from './legaldesk'` for all type aliases and interfaces
  - Use `export { ... } from './legaldesk'` for all const maps (CASE_STATUS_LABELS, CASE_STATUS_COLORS, etc.)
  - Follow the existing pattern used for restaurant and person types

### Step 4: Run Validation Commands
- Run TypeScript type checking: `cd apps/Client && npx tsc --noEmit`
- Run build: `cd apps/Client && npm run build`
- Verify no `any` types exist in the new file
- Verify all interfaces match the SQL schema column names exactly

## Testing Strategy
### Unit Tests
No unit tests needed for this task — it is purely type definitions and constant maps with no runtime logic. TypeScript compiler validation (`tsc --noEmit`) serves as the primary validation.

### Edge Cases
- Ensure all optional fields use `?:` syntax (matching SQL columns with `DEFAULT` values or `NULL` allowance)
- Ensure `number` is used for all SERIAL, INTEGER, DECIMAL, and BIGINT columns
- Ensure `string` is used for all VARCHAR, TEXT, DATE, and TIMESTAMPTZ columns
- Ensure `Record<string, unknown>` is used for the JSONB `ai_classification` field (no `any`)
- Verify all label maps have entries for every union member (TypeScript `Record` type enforces this at compile time)
- Verify color hex codes are valid 6-digit hex format

## Acceptance Criteria
- [ ] File `apps/Client/src/types/legaldesk.ts` exists with all 14 string literal union types
- [ ] All ~25 entity interfaces match the 11 `ld_*` database table columns exactly (names, types, optionality)
- [ ] Detail interfaces (`LdCaseDetail`, `LdSpecialistDetail`) correctly extend base interfaces with nested arrays
- [ ] Create/Update interfaces exist for all entities that support CRUD operations
- [ ] Filter and ListResponse interfaces exist for primary entities (Case, Specialist, Client)
- [ ] All label maps cover every member of their respective union type
- [ ] All color maps use valid hex color codes
- [ ] `apps/Client/src/types/index.ts` re-exports all Legal Desk types and constants
- [ ] Zero `any` types in the entire file
- [ ] `npx tsc --noEmit` passes with zero errors
- [ ] `npm run build` succeeds with zero errors

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd apps/Client && npx tsc --noEmit` — Run TypeScript type check to validate all types compile correctly with zero errors
- `cd apps/Client && npm run build` — Run production build to validate no build regressions
- `grep -r "any" apps/Client/src/types/legaldesk.ts` — Verify no `any` types exist (should only match `unknown` in Record<string, unknown>)

## Notes
- This is a pure types/constants task — no runtime code, no API calls, no UI components, no E2E tests needed.
- All interfaces use `number` for IDs (SERIAL primary keys), not UUID strings — this differs from the core Finance Tracker entities.
- The issue spec mentions `client_budget` and `faroo_margin_pct` field names, but the actual SQL schema uses `budget` and `margin_percentage`. The implementation MUST match the SQL schema column names since the backend DTOs (to be created in LD-004) will serialize using those exact names.
- The `case_type` field on `LdCase` uses the `CaseType` union but is stored as VARCHAR in SQL — the issue spec includes it in the interface but it is NOT a column in the `ld_cases` SQL table. Add it as an optional field for forward compatibility since the issue spec explicitly requests it.
- Wave 5 (services/hooks) and Wave 6 (UI components) will consume these types — ensure all export names are clear, consistent, and use the `Ld` prefix to avoid collision with existing Finance Tracker types.
