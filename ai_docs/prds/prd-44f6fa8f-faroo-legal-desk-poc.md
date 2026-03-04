# PRD: Faroo Legal Desk - Case Management & Specialist Assignment POC

## Meeting Metadata
- **Date**: Not specified
- **Participants**: Not specified (Faroo Legal stakeholders, Tremarel team)
- **Duration**: Not specified
- **Context**: Discovery and proof-of-concept scoping session for Faroo Legal, a global legal services platform ("Uber for Legal") connecting clients with 400-500 specialist lawyers. The meeting identified core operational bottlenecks in specialist assignment, pricing, and case management — all currently handled via WhatsApp, email, and Notion.

## Executive Summary

Faroo Legal needs a centralized platform to replace manual operations across four key areas: intelligent specialist-to-case assignment, pricing negotiation with margin management, case lifecycle tracking with deliverables, and specialist performance scoring. The POC adapts the existing ServiceDesk ticketing pattern (Tickets → Cases, Technicians → Specialists, IT Categories → Legal Domains, SLAs → Deadlines, Auto-assignment → Assignment Engine) while introducing new domain-specific concepts: a Pricing Engine, multi-specialist assignments per case, deliverables tracking, client management, and specialist scoring.

POC simplifications include: no CRM integration (Go High Level stays separate), documents as metadata-only (no file upload), no notifications, no chatbot, scoring via simple form input, and semi-automatic assignment (system proposes candidates, human approves). The system uses an `ld_` table prefix for all 11 database tables and follows the existing Clean Architecture patterns established in Tremarel_Finance.

## Work Streams

### Stream 1: Database Foundation
Establish the relational schema for all Legal Desk entities, with proper indexing, foreign keys, and seed data for development.

#### Requirements

##### REQ-001: Legal Desk Database Schema
- **Type**: architecture_decision
- **Priority**: P0
- **Description**: Create 11 PostgreSQL tables with `ld_` prefix covering the full Legal Desk domain: `ld_clients`, `ld_specialists`, `ld_specialist_expertise`, `ld_specialist_jurisdictions`, `ld_cases`, `ld_case_specialists`, `ld_case_deliverables`, `ld_case_messages`, `ld_case_documents`, `ld_pricing_history`, `ld_specialist_scores`. Include indexes on status, legal_domain, and all foreign keys. Add `update_updated_at_column()` triggers on clients, specialists, cases, and deliverables.
- **Affected Modules**: `apps/Server/database/create_legaldesk_tables.sql`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] SQL file creates all 11 tables with correct columns, types, and constraints
  - [ ] All foreign key relationships are properly defined
  - [ ] UNIQUE constraints exist on `(specialist_id, legal_domain)` in expertise and `(specialist_id, country, region)` in jurisdictions
  - [ ] `ld_cases.case_number` follows format `LD-YYYYMM-NNNN`
  - [ ] `ld_cases.ai_classification` is JSONB type
  - [ ] Indexes exist on status, legal_domain, client_id, specialist_id, case_id columns
  - [ ] `updated_at` triggers fire on clients, specialists, cases, deliverables tables
  - [ ] Script executes successfully on Supabase PostgreSQL

##### REQ-002: Legal Desk Seed Data
- **Type**: feature
- **Priority**: P1
- **Description**: Create seed data SQL with 5 specialists (each with expertise and jurisdiction entries), 3 clients, and 2 cases with deliverables. Seed data should cover multiple legal domains and jurisdictions to enable meaningful testing of the assignment engine.
- **Affected Modules**: `apps/Server/database/seed_legaldesk_data.sql`
- **Dependencies**: REQ-001
- **Acceptance Criteria**:
  - [ ] 5 specialists with varied legal domains, proficiency levels, and jurisdictions
  - [ ] 3 clients with mix of company and individual types
  - [ ] 2 cases at different pipeline stages with deliverables assigned
  - [ ] Script executes successfully after schema creation

---

### Stream 2: Backend Data Layer (Models + DTOs)
Define SQLAlchemy ORM models and Pydantic DTOs with all enums, validation rules, and status transition logic.

#### Requirements

##### REQ-003: SQLAlchemy ORM Models
- **Type**: feature
- **Priority**: P0
- **Description**: Create 11 SQLAlchemy model files following the `event.py` pattern: `LdClient`, `LdSpecialist`, `LdSpecialistExpertise`, `LdSpecialistJurisdiction`, `LdCase`, `LdCaseSpecialist`, `LdCaseDeliverable`, `LdCaseMessage`, `LdCaseDocument`, `LdPricingHistory`, `LdSpecialistScore`. Register all models in `__init__.py`.
- **Affected Modules**: `apps/Server/src/models/ld_client.py`, `ld_specialist.py`, `ld_specialist_expertise.py`, `ld_specialist_jurisdiction.py`, `ld_case.py`, `ld_case_specialist.py`, `ld_case_deliverable.py`, `ld_case_message.py`, `ld_case_document.py`, `ld_pricing_history.py`, `ld_specialist_score.py`, `apps/Server/src/models/__init__.py`
- **Dependencies**: REQ-001
- **Acceptance Criteria**:
  - [ ] Each model maps to its corresponding `ld_` table
  - [ ] All column types, defaults, and nullable flags match the schema
  - [ ] Relationships defined between models (e.g., Case → Client, CaseSpecialist → Specialist)
  - [ ] All 11 models registered in `__init__.py`
  - [ ] Models follow the existing `event.py` pattern (Base class, table name, columns)

##### REQ-004: Pydantic DTOs and Enums
- **Type**: feature
- **Priority**: P0
- **Description**: Create a comprehensive DTO file with 14 enums and ~40 Pydantic models covering all CRUD operations, filters, responses, and specialized DTOs for the assignment engine, classification, pricing, and analytics. Include the case status transition map as a constant dictionary for validation.
- **Affected Modules**: `apps/Server/src/interface/legaldesk_dto.py`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] 14 enums defined: CaseStatus (11 values), CaseType (2), LegalDomain (10), CaseComplexity (4), CasePriority (4), OriginationChannel (2), SpecialistStatus (3), SpecialistType (2), ProficiencyLevel (3), AssignmentRole (4), AssignmentStatus (5), DeliverableStatus (5), PricingAction (6), ClientType (2)
  - [ ] CASE_STATUS_TRANSITIONS dict maps each status to its valid next statuses
  - [ ] DTOs exist for: Cases (6), Specialists (6), Clients (3), Assignments (2), Deliverables (3), Messages (2), Documents (2), Pricing (2), Scoring (2), Assignment Engine (2), Classification (1), Analytics (1)
  - [ ] All DTOs use proper Pydantic v2 syntax with type hints
  - [ ] CaseFilterDTO supports filtering by status, legal_domain, priority, case_type, client_id

---

### Stream 3: Backend Repositories
Implement data access layer with repository classes for all Legal Desk entities.

#### Requirements

##### REQ-005: Case Repository
- **Type**: feature
- **Priority**: P0
- **Description**: Repository for legal case CRUD with filtering, status updates, and case number generation. Methods: create, get_by_id, list_cases(filters), update, update_status, generate_case_number (format: `LD-YYYYMM-NNNN`), get_by_client, count_by_status.
- **Affected Modules**: `apps/Server/src/repository/ld_case_repository.py`
- **Dependencies**: REQ-003, REQ-004
- **Acceptance Criteria**:
  - [ ] CRUD operations work correctly with database session
  - [ ] `list_cases` supports filtering by status, legal_domain, priority, case_type, client_id
  - [ ] `generate_case_number` produces sequential numbers in `LD-YYYYMM-NNNN` format
  - [ ] `update_status` persists the new status
  - [ ] Follows `restaurant_repository.py` pattern

##### REQ-006: Specialist Repository
- **Type**: feature
- **Priority**: P0
- **Description**: Repository for specialist CRUD with availability filtering and score management. Methods: create, get_by_id, list_all, update, update_status, get_available(domain, jurisdiction), update_workload, update_overall_score.
- **Affected Modules**: `apps/Server/src/repository/ld_specialist_repository.py`
- **Dependencies**: REQ-003, REQ-004
- **Acceptance Criteria**:
  - [ ] `get_available` filters by legal_domain expertise, jurisdiction match, active status, and workload capacity
  - [ ] `update_workload` increments/decrements current_workload
  - [ ] `update_overall_score` recalculates from specialist_scores table

##### REQ-007: Client Repository
- **Type**: feature
- **Priority**: P1
- **Description**: Repository for client CRUD and search. Methods: create, get_by_id, list_all, update, search_by_name.
- **Affected Modules**: `apps/Server/src/repository/ld_client_repository.py`
- **Dependencies**: REQ-003, REQ-004
- **Acceptance Criteria**:
  - [ ] CRUD operations work correctly
  - [ ] `search_by_name` performs case-insensitive partial matching

##### REQ-008: Assignment Repository
- **Type**: feature
- **Priority**: P0
- **Description**: Repository for case-specialist assignments. Methods: create_assignment, get_case_specialists, get_specialist_cases, update_assignment_status, update_fees.
- **Affected Modules**: `apps/Server/src/repository/ld_assignment_repository.py`
- **Dependencies**: REQ-003, REQ-004
- **Acceptance Criteria**:
  - [ ] Assignments link cases to specialists with role and status
  - [ ] Fee fields (proposed_fee, agreed_fee, fee_type) are correctly persisted and updated
  - [ ] Can query both directions: specialists for a case, cases for a specialist

##### REQ-009: Deliverable Repository
- **Type**: feature
- **Priority**: P1
- **Description**: Repository for case deliverables/milestones. Methods: create, get_by_case, update, update_status.
- **Affected Modules**: `apps/Server/src/repository/ld_deliverable_repository.py`
- **Dependencies**: REQ-003, REQ-004
- **Acceptance Criteria**:
  - [ ] Deliverables are associated with a case and optionally a specialist
  - [ ] Status transitions (pending → in_progress → review → completed/cancelled) work

##### REQ-010: Message Repository
- **Type**: feature
- **Priority**: P1
- **Description**: Repository for case communication threads. Methods: create, get_by_case(include_internal).
- **Affected Modules**: `apps/Server/src/repository/ld_message_repository.py`
- **Dependencies**: REQ-003, REQ-004
- **Acceptance Criteria**:
  - [ ] Messages store sender_type (faroo_staff/specialist/client/system)
  - [ ] `include_internal` flag controls visibility of internal messages

##### REQ-011: Analytics Repository
- **Type**: feature
- **Priority**: P2
- **Description**: Repository for dashboard analytics queries. Methods: count_cases_by_status, count_cases_by_domain, revenue_pipeline, specialist_performance_rankings, avg_case_duration.
- **Affected Modules**: `apps/Server/src/repository/ld_analytics_repository.py`
- **Dependencies**: REQ-003, REQ-004
- **Acceptance Criteria**:
  - [ ] Aggregation queries return correct counts grouped by status and domain
  - [ ] Revenue pipeline sums estimated_cost and final_quote for active cases
  - [ ] Specialist performance returns ranked list by overall_score

---

### Stream 4: Backend Business Logic (Services)
Implement core business services including the Specialist Assignment Engine, Pricing Engine, and AI Classification.

#### Requirements

##### REQ-012: Case Lifecycle Service
- **Type**: feature
- **Priority**: P0
- **Description**: Service managing case creation, updates, and status transitions. Validates status changes against CASE_STATUS_TRANSITIONS map. Provides `get_case_with_details` joining specialists, deliverables, messages, and documents.
- **Affected Modules**: `apps/Server/src/core/services/ld_case_service.py`
- **Dependencies**: REQ-004, REQ-005
- **Acceptance Criteria**:
  - [ ] `create_case` generates case_number and persists all fields
  - [ ] `update_case_status` rejects invalid transitions (e.g., closed → active)
  - [ ] `get_case_with_details` returns case with all related entities joined
  - [ ] INFO-level logging on all operations

##### REQ-013: Specialist Assignment Engine
- **Type**: feature
- **Priority**: P0
- **Description**: Core differentiator — intelligent specialist matching algorithm. `suggest_specialists(case_id)` performs: (1) mandatory filter by legal_domain expertise match, (2) jurisdiction coverage filter if case has jurisdiction, (3) availability filter (active status, current_workload < max_workload), (4) scoring on 0-100 scale: expertise_proficiency 30pts, overall_score 25pts, workload_availability 20pts, jurisdiction_match 15pts, years_experience 10pts, (5) returns top 5 ranked candidates with match_score and match_reasons. Also handles assign_specialist, update_assignment_status, get_case_specialists.
- **Affected Modules**: `apps/Server/src/core/services/ld_assignment_service.py`
- **Dependencies**: REQ-004, REQ-005, REQ-006, REQ-008
- **Acceptance Criteria**:
  - [ ] `suggest_specialists` filters mandatory domain match correctly
  - [ ] Jurisdiction filter applies only when case has jurisdiction set
  - [ ] Availability filter excludes inactive or overloaded specialists
  - [ ] Scoring weights sum to 100: expertise (30), score (25), workload (20), jurisdiction (15), experience (10)
  - [ ] Returns top 5 candidates sorted by match_score descending
  - [ ] Each candidate includes match_reasons array explaining the score
  - [ ] `assign_specialist` creates assignment and updates specialist workload

##### REQ-014: Pricing Engine
- **Type**: feature
- **Priority**: P0
- **Description**: Manages pricing negotiation lifecycle: initial proposal, counter-offers, acceptance, rejection. Calculates Faroo margin as `margin_pct = ((client_price - specialist_cost) / client_price) * 100`. Acceptance locks `final_quote` on the case. All actions logged in pricing_history.
- **Affected Modules**: `apps/Server/src/core/services/ld_pricing_service.py`
- **Dependencies**: REQ-004, REQ-005
- **Acceptance Criteria**:
  - [ ] `create_proposal` stores initial specialist_cost, client_price, and calculated margin
  - [ ] `submit_counter` records counter-offer in pricing_history
  - [ ] `accept_pricing` locks final_quote and faroo_margin_pct on the case record
  - [ ] `reject_pricing` records rejection in history
  - [ ] Margin calculation is correct: `((client_price - specialist_cost) / client_price) * 100`
  - [ ] Full audit trail maintained in ld_pricing_history

##### REQ-015: AI Case Classification
- **Type**: feature
- **Priority**: P1
- **Description**: Classifies cases by analyzing title and description using OpenAI GPT-4o-mini. Returns suggested legal_domain, case_type, complexity, confidence score, and reasoning. Falls back to keyword-based classification when API is unavailable.
- **Affected Modules**: `apps/Server/src/core/services/ld_classification_service.py`, `apps/Server/src/config/settings.py`
- **Dependencies**: REQ-004, REQ-005
- **Acceptance Criteria**:
  - [ ] Sends case title + description to OpenAI GPT-4o-mini
  - [ ] Returns ClassificationResultDTO with legal_domain, case_type, complexity, confidence, reasoning
  - [ ] Keyword-based fallback works when OpenAI API is unavailable or errors
  - [ ] Classification result stored in case's `ai_classification` JSONB field
  - [ ] OPENAI_API_KEY added to settings.py if not present

##### REQ-016: Specialist Service (CRUD + Scoring)
- **Type**: feature
- **Priority**: P1
- **Description**: Specialist CRUD plus expertise/jurisdiction management and performance scoring. `submit_score` records per-case scores (quality, teamwork, delivery, satisfaction) and recalculates the specialist's overall_score as the average of all their scores.
- **Affected Modules**: `apps/Server/src/core/services/ld_specialist_service.py`
- **Dependencies**: REQ-004, REQ-006
- **Acceptance Criteria**:
  - [ ] CRUD operations for specialists work correctly
  - [ ] `add_expertise` adds legal domain proficiency entries
  - [ ] `add_jurisdiction` adds geographic coverage entries
  - [ ] `submit_score` stores per-case scores and recalculates overall_score
  - [ ] `get_specialist_detail` returns specialist with expertise[], jurisdictions[], and scores[]

##### REQ-017: Client Service
- **Type**: feature
- **Priority**: P1
- **Description**: Client CRUD service with search capability. Methods: create, update, get, list, search.
- **Affected Modules**: `apps/Server/src/core/services/ld_client_service.py`
- **Dependencies**: REQ-004, REQ-007
- **Acceptance Criteria**:
  - [ ] CRUD operations work correctly
  - [ ] Search by name returns matching clients

##### REQ-018: Analytics Service
- **Type**: feature
- **Priority**: P2
- **Description**: Dashboard aggregation service. `get_dashboard_stats` returns cases_by_status, cases_by_domain, revenue_summary, specialist_performance rankings, and recent_cases list.
- **Affected Modules**: `apps/Server/src/core/services/ld_analytics_service.py`
- **Dependencies**: REQ-004, REQ-011
- **Acceptance Criteria**:
  - [ ] Returns correct case counts grouped by status and legal domain
  - [ ] Revenue summary includes pipeline value and closed revenue
  - [ ] Specialist performance returns ranked list with scores
  - [ ] Recent cases list returns latest cases with basic info

---

### Stream 5: Backend API Layer (Routes)
Expose all Legal Desk functionality through RESTful API endpoints.

#### Requirements

##### REQ-019: Legal Desk API Routes
- **Type**: feature
- **Priority**: P0
- **Description**: Single route file with ~33 endpoints under `/api/legaldesk` prefix. All endpoints require authentication (`Depends(get_current_user)`) and database session (`Depends(get_db)`). Endpoint groups: Cases (6), Assignments (4), Deliverables (4), Messages (2), Documents (2), Pricing (5), Specialists (7), Clients (4), Analytics (1).
- **Affected Modules**: `apps/Server/src/adapter/rest/legaldesk_routes.py`
- **Dependencies**: REQ-012, REQ-013, REQ-014, REQ-015, REQ-016, REQ-017, REQ-018
- **Acceptance Criteria**:
  - [ ] All ~33 endpoints are accessible under `/api/legaldesk/`
  - [ ] Every endpoint requires JWT authentication
  - [ ] Case endpoints: POST /cases, GET /cases, GET /cases/{id}, PUT /cases/{id}, PATCH /cases/{id}/status, POST /cases/{id}/classify
  - [ ] Assignment endpoints: GET /cases/{id}/specialists, POST /cases/{id}/specialists, GET /cases/{id}/specialists/suggest, PATCH /cases/{id}/specialists/{aid}/status
  - [ ] Deliverable endpoints: GET /cases/{id}/deliverables, POST /cases/{id}/deliverables, PUT /cases/{id}/deliverables/{did}, PATCH /cases/{id}/deliverables/{did}/status
  - [ ] Message endpoints: GET /cases/{id}/messages, POST /cases/{id}/messages
  - [ ] Document endpoints: GET /cases/{id}/documents, POST /cases/{id}/documents
  - [ ] Pricing endpoints: GET /cases/{id}/pricing, POST /cases/{id}/pricing/propose, POST /cases/{id}/pricing/counter, POST /cases/{id}/pricing/accept, POST /cases/{id}/pricing/reject
  - [ ] Specialist endpoints: GET /specialists, POST /specialists, GET /specialists/{id}, PUT /specialists/{id}, POST /specialists/{id}/expertise, POST /specialists/{id}/jurisdictions, POST /specialists/{id}/scores
  - [ ] Client endpoints: GET /clients, POST /clients, GET /clients/{id}, PUT /clients/{id}
  - [ ] Analytics endpoint: GET /analytics/dashboard
  - [ ] All endpoints visible in `/docs` Swagger UI

##### REQ-020: Backend Route Registration
- **Type**: feature
- **Priority**: P0
- **Description**: Register the legaldesk_router in the FastAPI application entry point and ensure OPENAI_API_KEY is available in settings.
- **Affected Modules**: `apps/Server/main.py`, `apps/Server/src/config/settings.py`
- **Dependencies**: REQ-019
- **Acceptance Criteria**:
  - [ ] `legaldesk_router` is included in `main.py` app router registration
  - [ ] OPENAI_API_KEY config available in settings (optional, for classification)
  - [ ] Backend starts without errors with all Legal Desk routes loaded

---

### Stream 6: Frontend Data Layer (Types + Service + Hooks)
Define TypeScript interfaces, API service client, and React hooks for all Legal Desk data operations.

#### Requirements

##### REQ-021: Frontend TypeScript Types
- **Type**: feature
- **Priority**: P0
- **Description**: Define all Legal Desk TypeScript types: string literal unions for all 14 enums, ~25 interfaces (LdCase, LdSpecialist, LdClient, CaseDetail, CaseSpecialist, CaseDeliverable, CaseMessage, CaseDocument, PricingHistoryEntry, SpecialistCandidate, DashboardStats, etc.), and label/color maps (CASE_STATUS_LABELS, CASE_STATUS_COLORS, LEGAL_DOMAIN_LABELS, PRIORITY_COLORS). Re-export from index.
- **Affected Modules**: `apps/Client/src/types/legaldesk.ts`, `apps/Client/src/types/index.ts`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] All 14 enums represented as TypeScript string literal unions
  - [ ] ~25 interfaces cover all API response and request shapes
  - [ ] Label maps provide human-readable names for all enum values
  - [ ] Color maps provide MUI-compatible colors for status, priority, domain
  - [ ] Types re-exported from `index.ts`
  - [ ] No `any` types used

##### REQ-022: Frontend API Service
- **Type**: feature
- **Priority**: P0
- **Description**: Complete API client with ~35 methods covering all Legal Desk endpoints. Follows `restaurantService.ts` pattern using the authenticated Axios client.
- **Affected Modules**: `apps/Client/src/services/legaldeskService.ts`
- **Dependencies**: REQ-021
- **Acceptance Criteria**:
  - [ ] Methods exist for all ~33 API endpoints
  - [ ] Uses authenticated Axios client with JWT interceptor
  - [ ] Proper TypeScript typing on all request/response parameters
  - [ ] Error handling with console.error logging
  - [ ] Follows existing service file patterns

##### REQ-023: Frontend React Hooks
- **Type**: feature
- **Priority**: P0
- **Description**: 6 custom hooks encapsulating Legal Desk data operations: `useLegaldeskCases` (cases list + filters + CRUD), `useLegaldeskCaseDetail` (full case detail with all tabs), `useLegaldeskSpecialists` (list + CRUD + scoring), `useLegaldeskClients` (list + CRUD), `useLegaldeskDashboard` (stats), `useLegaldeskPricing` (pricing workflow).
- **Affected Modules**: `apps/Client/src/hooks/useLegaldeskCases.ts`, `useLegaldeskCaseDetail.ts`, `useLegaldeskSpecialists.ts`, `useLegaldeskClients.ts`, `useLegaldeskDashboard.ts`, `useLegaldeskPricing.ts`
- **Dependencies**: REQ-022
- **Acceptance Criteria**:
  - [ ] Each hook returns loading state, error handling, and data
  - [ ] `useLegaldeskCases` supports filtering by status, domain, priority, type
  - [ ] `useLegaldeskCaseDetail` fetches and manages all case sub-entities (specialists, deliverables, messages, documents, pricing)
  - [ ] `useLegaldeskPricing` exposes propose, counter, accept, reject actions
  - [ ] Hooks follow `useEvents.ts` pattern

---

### Stream 7: Frontend UI Components
Build reusable UI components for Legal Desk status badges, score displays, pricing timeline, and deliverable checklist.

#### Requirements

##### REQ-024: Legal Desk UI Components
- **Type**: feature
- **Priority**: P1
- **Description**: 6 reusable MUI-based UI components: `TRCaseStatusBadge` (colored Chip for case status), `TRCasePriorityBadge` (colored Chip for priority), `TRLegalDomainBadge` (Chip with domain label), `TRSpecialistScoreDisplay` (5-star rating with numeric score), `TRPricingTimeline` (MUI Timeline showing negotiation history), `TRDeliverableChecklist` (checklist with status chips).
- **Affected Modules**: `apps/Client/src/components/ui/TRCaseStatusBadge.tsx`, `TRCasePriorityBadge.tsx`, `TRLegalDomainBadge.tsx`, `TRSpecialistScoreDisplay.tsx`, `TRPricingTimeline.tsx`, `TRDeliverableChecklist.tsx`
- **Dependencies**: REQ-021
- **Acceptance Criteria**:
  - [ ] All components use TR prefix naming convention
  - [ ] Badge components render correct colors from type color maps
  - [ ] `TRSpecialistScoreDisplay` shows 5-star visual and numeric score
  - [ ] `TRPricingTimeline` renders chronological negotiation history entries
  - [ ] `TRDeliverableChecklist` shows deliverables with status chips and due dates
  - [ ] All components are properly typed with TypeScript interfaces

---

### Stream 8: Frontend Forms
Build react-hook-form based forms for case creation, specialist management, and client management.

#### Requirements

##### REQ-025: Legal Case Form
- **Type**: feature
- **Priority**: P0
- **Description**: `TRLegalCaseForm` with fields: title, description, client_id (autocomplete from clients list), legal_domain (select), case_type (select), complexity (select), origination_channel (select), client_budget (number), deadline (date picker), jurisdiction (text), priority (select). Uses react-hook-form with MUI, validation rules, and error display.
- **Affected Modules**: `apps/Client/src/components/forms/TRLegalCaseForm.tsx`
- **Dependencies**: REQ-021, REQ-023
- **Acceptance Criteria**:
  - [ ] All fields rendered with proper MUI components
  - [ ] Client selection uses autocomplete with search
  - [ ] Required field validation (title, legal_domain, client)
  - [ ] react-hook-form manages all form state
  - [ ] Error messages display via MUI helperText
  - [ ] Form supports both create and edit modes

##### REQ-026: Legal Specialist Form
- **Type**: feature
- **Priority**: P1
- **Description**: `TRLegalSpecialistForm` with fields: name, type (individual/boutique_firm), email, phone, country, city, years_experience, hourly_rate, plus sub-sections for adding expertise (domain + proficiency) and jurisdictions (country + region + is_primary).
- **Affected Modules**: `apps/Client/src/components/forms/TRLegalSpecialistForm.tsx`
- **Dependencies**: REQ-021, REQ-023
- **Acceptance Criteria**:
  - [ ] Core fields with proper validation
  - [ ] Expertise sub-section allows adding multiple domain/proficiency pairs
  - [ ] Jurisdiction sub-section allows adding multiple country/region pairs
  - [ ] react-hook-form with MUI integration

##### REQ-027: Legal Client Form
- **Type**: feature
- **Priority**: P1
- **Description**: `TRLegalClientForm` with fields: name, type (company/individual), contact_email, contact_phone, country, industry.
- **Affected Modules**: `apps/Client/src/components/forms/TRLegalClientForm.tsx`
- **Dependencies**: REQ-021, REQ-023
- **Acceptance Criteria**:
  - [ ] All fields with proper validation
  - [ ] Email format validation
  - [ ] react-hook-form with MUI integration

---

### Stream 9: Frontend Pages
Build all Legal Desk pages: dashboard, case management (list, create, detail), specialists, clients, and analytics.

#### Requirements

##### REQ-028: Legal Desk Dashboard Page
- **Type**: feature
- **Priority**: P1
- **Description**: Dashboard at `/poc/legal-desk/dashboard` showing: stat cards (Active Cases, Pipeline Value, Specialists Active, Avg Duration), Cases by Status pie chart, Cases by Domain bar chart, Recent Cases table, and Top Specialists ranking.
- **Affected Modules**: `apps/Client/src/pages/legaldesk/LegalDeskDashboardPage.tsx`
- **Dependencies**: REQ-023, REQ-024
- **Acceptance Criteria**:
  - [ ] 4 summary stat cards render with correct values
  - [ ] Pie chart shows case distribution by status
  - [ ] Bar chart shows case distribution by legal domain
  - [ ] Recent cases table shows latest cases with status badges
  - [ ] Top specialists section shows ranked performers

##### REQ-029: Cases List Page
- **Type**: feature
- **Priority**: P0
- **Description**: Cases list at `/poc/legal-desk/cases` with filterable table (status, domain, priority, type filters), case status badges, and "New Case" button navigating to creation page.
- **Affected Modules**: `apps/Client/src/pages/legaldesk/LegalDeskCasesPage.tsx`
- **Dependencies**: REQ-023, REQ-024
- **Acceptance Criteria**:
  - [ ] Table displays cases with case_number, title, client, domain, status, priority
  - [ ] Filter controls for status, legal_domain, priority, case_type
  - [ ] Status rendered using TRCaseStatusBadge
  - [ ] "New Case" button navigates to `/poc/legal-desk/cases/new`
  - [ ] Clicking a case row navigates to case detail

##### REQ-030: New Case Page
- **Type**: feature
- **Priority**: P0
- **Description**: Case creation page at `/poc/legal-desk/cases/new` rendering TRLegalCaseForm. On successful submission, redirects to the new case's detail page.
- **Affected Modules**: `apps/Client/src/pages/legaldesk/LegalDeskNewCasePage.tsx`
- **Dependencies**: REQ-025
- **Acceptance Criteria**:
  - [ ] Renders TRLegalCaseForm
  - [ ] On submit, creates case via API and redirects to `/poc/legal-desk/cases/:id`
  - [ ] Shows loading state during submission
  - [ ] Displays error on failure

##### REQ-031: Case Detail Page
- **Type**: feature
- **Priority**: P0
- **Description**: Most complex page at `/poc/legal-desk/cases/:id` with tabbed interface: **Overview** (case info, client, status, classification), **Specialists** (assigned specialists + "Suggest Specialists" button showing ranked candidates with scores and reasons, approve/assign actions), **Deliverables** (TRDeliverableChecklist with add/update), **Pricing** (TRPricingTimeline + propose/counter/accept/reject actions), **Messages** (thread with internal toggle), **Documents** (metadata list with add). Status action bar shows valid transitions based on current status.
- **Affected Modules**: `apps/Client/src/pages/legaldesk/LegalDeskCaseDetailPage.tsx`
- **Dependencies**: REQ-023, REQ-024, REQ-025
- **Acceptance Criteria**:
  - [ ] All 6 tabs render and switch correctly
  - [ ] Overview shows case details with status badge, domain badge, priority badge
  - [ ] Specialists tab shows current assignments and "Suggest" button triggers assignment engine
  - [ ] Suggested candidates display with match_score and match_reasons
  - [ ] Deliverables tab shows checklist with add and status update
  - [ ] Pricing tab shows timeline and negotiation action buttons
  - [ ] Messages tab shows threaded messages with internal toggle
  - [ ] Documents tab shows metadata list with add form
  - [ ] Status bar shows only valid next-status transitions as buttons

##### REQ-032: Specialists Page
- **Type**: feature
- **Priority**: P1
- **Description**: Specialists management at `/poc/legal-desk/specialists` showing card grid or table with domain chips, star ratings, workload indicators. "Add Specialist" opens dialog with TRLegalSpecialistForm.
- **Affected Modules**: `apps/Client/src/pages/legaldesk/LegalDeskSpecialistsPage.tsx`
- **Dependencies**: REQ-023, REQ-024, REQ-026
- **Acceptance Criteria**:
  - [ ] Lists all specialists with key info (name, domains, score, workload)
  - [ ] Domain expertise shown as TRLegalDomainBadge chips
  - [ ] Score shown via TRSpecialistScoreDisplay
  - [ ] Workload indicator (current/max)
  - [ ] "Add Specialist" dialog with form

##### REQ-033: Clients Page
- **Type**: feature
- **Priority**: P1
- **Description**: Client management at `/poc/legal-desk/clients` with table listing all clients and "Add Client" dialog using TRLegalClientForm.
- **Affected Modules**: `apps/Client/src/pages/legaldesk/LegalDeskClientsPage.tsx`
- **Dependencies**: REQ-023, REQ-027
- **Acceptance Criteria**:
  - [ ] Table lists clients with name, type, email, country, industry
  - [ ] "Add Client" dialog with TRLegalClientForm

##### REQ-034: Analytics Page
- **Type**: feature
- **Priority**: P2
- **Description**: Analytics dashboard at `/poc/legal-desk/analytics` with revenue cards, charts (cases over time, revenue by domain, specialist utilization), and performance rankings table.
- **Affected Modules**: `apps/Client/src/pages/legaldesk/LegalDeskAnalyticsPage.tsx`
- **Dependencies**: REQ-023, REQ-024
- **Acceptance Criteria**:
  - [ ] Revenue summary cards (pipeline value, closed revenue, avg margin)
  - [ ] At least 2 charts using Recharts
  - [ ] Specialist performance rankings table

---

### Stream 10: Frontend Routing & Navigation
Integrate Legal Desk pages into the application routing and sidebar navigation.

#### Requirements

##### REQ-035: Legal Desk Route Registration
- **Type**: feature
- **Priority**: P0
- **Description**: Add 8 routes under `/poc/legal-desk/*` in App.tsx: dashboard, cases, cases/new, cases/:id, specialists, clients, analytics. All wrapped in ProtectedRoute.
- **Affected Modules**: `apps/Client/src/App.tsx`
- **Dependencies**: REQ-028, REQ-029, REQ-030, REQ-031, REQ-032, REQ-033, REQ-034
- **Acceptance Criteria**:
  - [ ] All 7+ routes registered and navigable
  - [ ] Routes protected by authentication
  - [ ] Lazy loading of page components (if pattern exists)

##### REQ-036: Sidebar Navigation
- **Type**: feature
- **Priority**: P0
- **Description**: Add Legal Desk subsection to TRCollapsibleSidebar under POCs section with items: Dashboard (GavelIcon), Cases (BusinessCenterIcon), Specialists (PersonSearchIcon), Clients (GroupsIcon), Analytics (AnalyticsIcon).
- **Affected Modules**: `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] Legal Desk section visible in sidebar
  - [ ] 5 navigation items with correct icons
  - [ ] Navigation links point to correct routes
  - [ ] Active state highlights current page

---

## Implementation Waves

### Wave 1: Foundation
**REQ IDs**: REQ-001, REQ-002, REQ-003, REQ-004, REQ-021
**Rationale**: Database schema, ORM models, DTOs, and frontend types have no runtime dependencies. They define the data contracts that all other layers depend on. Can be built and validated independently.

### Wave 2: Backend Data Access
**REQ IDs**: REQ-005, REQ-006, REQ-007, REQ-008, REQ-009, REQ-010, REQ-011
**Rationale**: All 7 repositories depend on models (Wave 1) and provide the data access layer needed by services. No inter-repository dependencies.

### Wave 3: Backend Business Logic
**REQ IDs**: REQ-012, REQ-013, REQ-014, REQ-015, REQ-016, REQ-017, REQ-018
**Rationale**: Services depend on repositories (Wave 2). Build simpler services first (REQ-017 client, REQ-016 specialist), then case lifecycle (REQ-012), then the core differentiators (REQ-013 assignment engine, REQ-014 pricing engine), then AI classification (REQ-015), and finally analytics (REQ-018).

### Wave 4: Backend API
**REQ IDs**: REQ-019, REQ-020
**Rationale**: Routes depend on all services (Wave 3). Single route file plus app registration. Backend is fully testable after this wave.

### Wave 5: Frontend Data Layer
**REQ IDs**: REQ-022, REQ-023
**Rationale**: API service depends on types (Wave 1), hooks depend on service. These provide the data layer for all UI components.

### Wave 6: Frontend UI
**REQ IDs**: REQ-024, REQ-025, REQ-026, REQ-027, REQ-028, REQ-029, REQ-030, REQ-031, REQ-032, REQ-033, REQ-034, REQ-035, REQ-036
**Rationale**: All UI components, forms, pages, and routing depend on types (Wave 1) and hooks (Wave 5). Build reusable components first, then forms, then pages, then wire up routing and navigation last.

## Cross-Cutting Concerns

### ServiceDesk Pattern Adaptation
The entire Legal Desk POC is modeled after the existing ServiceDesk ticketing system. Key mappings: Tickets → Cases, Technicians → Specialists, IT Categories → Legal Domains, SLAs → Deadlines, Auto-assignment → Assignment Engine. New concepts beyond ServiceDesk: Pricing Engine (negotiation + margin), multi-specialist assignments per case, deliverables tracking, client entity management, and specialist performance scoring.

### Authentication & Authorization
All API endpoints require JWT authentication via `Depends(get_current_user)`. No additional RBAC roles are specified for the POC — any authenticated user can access Legal Desk features. This may need refinement post-POC.

### Database Prefix Convention
All tables use `ld_` prefix to namespace Legal Desk data within the shared PostgreSQL database, following the pattern established by ServiceDesk (`sd_` prefix).

### AI Integration
OpenAI GPT-4o-mini is used for case classification. The integration is optional — a keyword-based fallback ensures the system works without an API key. The `OPENAI_API_KEY` environment variable must be added to settings.

### Multi-Entity Scope
The PRD does not explicitly address multi-entity scoping for Legal Desk data. If Faroo Legal operates as a single entity, this may not be needed for the POC. If multi-entity is required, all repositories will need entity_id filtering.

### Pricing Margin Formula
The standard margin calculation is: `margin_pct = ((client_price - specialist_cost) / client_price) * 100`. This is a percentage of the client price, not a markup on cost.

## Open Questions

- **Q1**: Should Legal Desk data be scoped by entity_id (multi-entity), or does Faroo Legal operate as a single tenant? — Context: "Multi-Entity Support: Users can belong to multiple entities" is a core platform feature, but the Legal Desk plan does not reference entity_id in any table.

- **Q2**: What RBAC roles should govern Legal Desk access? Should all authenticated users see Legal Desk, or should it be restricted to specific roles? — Context: "All endpoints: `Depends(get_current_user)` + `Depends(get_db)`" — no role-based restrictions specified.

- **Q3**: How should the assignment engine handle cases where no specialists match all mandatory filters? Should it relax criteria (e.g., drop jurisdiction requirement) or return an empty result with guidance? — Context: "Filter: legal_domain expertise match (mandatory)" and "Filter: jurisdiction coverage (if case has jurisdiction)"

- **Q4**: Should the sidebar Legal Desk section be visible to all users or gated behind a feature flag / role check, similar to how RestaurantOS is restricted? — Context: "restrict sidebar to RestaurantOS-only for users without entities" (recent commit)

- **Q5**: What is the expected behavior when the OpenAI API key is not configured? Should the classify endpoint return an error, silently use the fallback, or indicate that classification is unavailable? — Context: "Keyword-based fallback when API unavailable"

- **Q6**: Are there specific legal domain values beyond the 10 listed that Faroo Legal needs? The list (corporate, ip, labor, tax, litigation, real_estate, immigration, regulatory, data_privacy, commercial) may not cover all 400-500 specialists' practice areas. — Context: "connecting clients with 400-500 specialist lawyers across geographies and legal domains"
