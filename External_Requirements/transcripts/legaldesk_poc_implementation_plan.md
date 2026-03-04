# Legal Desk POC - Implementation Plan

## Context

**Faroo Legal** is a global legal services platform ("Uber for Legal") connecting clients with 400-500 specialist lawyers across geographies and legal domains. Their core bottleneck is manual specialist assignment and operations management (currently WhatsApp, email, Notion). They need:
- **Specialist Assignment Engine** - intelligent matching of lawyers to cases by skills, score, workload, geography
- **Pricing Engine** - specialist fee negotiation, Faroo margin, unified client quotes
- **Case Management Pipeline** - operational tracking of specialists, deliverables, deadlines, documents per case
- **Specialist Database & Scoring** - performance tracking (quality, teamwork, delivery, satisfaction)

This plan adapts the **ServiceDesk** ticketing pattern from `system-zero` into a legal case management domain, following the existing **RestaurantOS POC** conventions in Tremarel_Finance. The mapping: Tickets → Cases, Technicians → Specialists, IT Categories → Legal Domains, SLAs → Deadlines, Auto-assignment → Assignment Engine. New concepts not in ServiceDesk: Pricing Engine, multi-specialist assignments, deliverables tracking, client management, specialist scoring.

**POC Simplifications:** No CRM integration (Go High Level stays separate), documents metadata-only (no upload), no notifications, no chatbot, scoring via simple form input, assignment is semi-automatic (proposes candidates, human approves).

---

## Phase 1: Database Schema (2 files)

### 1.1 `apps/Server/database/create_legaldesk_tables.sql`

11 tables with `ld_` prefix:

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `ld_clients` | Client companies/individuals | name, type (company/individual), contact_email, country, industry |
| `ld_specialists` | Lawyers/firms | name, type (individual/boutique_firm), country, city, years_experience, hourly_rate, status, current_workload, max_workload, overall_score |
| `ld_specialist_expertise` | Legal domain expertise matrix | specialist_id FK, legal_domain, proficiency_level (expert/advanced/competent), years_in_domain. UNIQUE(specialist_id, legal_domain) |
| `ld_specialist_jurisdictions` | Geographic coverage | specialist_id FK, country, region, is_primary. UNIQUE(specialist_id, country, region) |
| `ld_cases` | Legal cases/projects (core entity) | case_number (LD-YYYYMM-NNNN), title, description, client_id FK, legal_domain, case_type, complexity, status, origination_channel, pricing fields (client_budget, estimated_cost, final_quote, faroo_margin_pct), deadline, jurisdiction, ai_classification JSONB, priority |
| `ld_case_specialists` | Many-to-many assignments | case_id FK, specialist_id FK, role (lead/assigned/reviewer/proposed), status (proposed/accepted/rejected/active/completed), proposed_fee, agreed_fee, fee_type |
| `ld_case_deliverables` | Tasks/milestones per case | case_id FK, specialist_id FK, title, description, status (pending/in_progress/review/completed/cancelled), due_date |
| `ld_case_messages` | Communication thread | case_id FK, sender_type (faroo_staff/specialist/client/system), content, is_internal |
| `ld_case_documents` | Document metadata | case_id FK, name, document_type, file_url, notes |
| `ld_pricing_history` | Price negotiation audit trail | case_id FK, action (initial_proposal/counter_offer/accepted/rejected), specialist_cost, client_price, margin_pct |
| `ld_specialist_scores` | Performance scoring per case | specialist_id FK, case_id FK, quality_score, teamwork_score, delivery_score, satisfaction_score, overall_score |

Indexes on: status, legal_domain, client_id, specialist_id, case_id FKs.
Triggers: `update_updated_at_column()` on clients, specialists, cases, deliverables.

### 1.2 `apps/Server/database/seed_legaldesk_data.sql`

Sample data: 5 specialists with expertise/jurisdictions, 3 clients, 2 cases with deliverables.

---

## Phase 2: Backend Models (11 new + 1 modified)

All in `apps/Server/src/models/`, following `event.py` pattern:

| File | Model | Table |
|------|-------|-------|
| `ld_client.py` | `LdClient` | `ld_clients` |
| `ld_specialist.py` | `LdSpecialist` | `ld_specialists` |
| `ld_specialist_expertise.py` | `LdSpecialistExpertise` | `ld_specialist_expertise` |
| `ld_specialist_jurisdiction.py` | `LdSpecialistJurisdiction` | `ld_specialist_jurisdictions` |
| `ld_case.py` | `LdCase` | `ld_cases` |
| `ld_case_specialist.py` | `LdCaseSpecialist` | `ld_case_specialists` |
| `ld_case_deliverable.py` | `LdCaseDeliverable` | `ld_case_deliverables` |
| `ld_case_message.py` | `LdCaseMessage` | `ld_case_messages` |
| `ld_case_document.py` | `LdCaseDocument` | `ld_case_documents` |
| `ld_pricing_history.py` | `LdPricingHistory` | `ld_pricing_history` |
| `ld_specialist_score.py` | `LdSpecialistScore` | `ld_specialist_scores` |

**Modify:** `apps/Server/src/models/__init__.py` - register all 11 new models.

---

## Phase 3: Backend DTOs (1 file)

**New:** `apps/Server/src/interface/legaldesk_dto.py`

### Enums (14):
- `CaseStatus`: intake, specialist_selection, pricing, negotiation, active, in_progress, pending_client, pending_specialist, delivered, closed, cancelled
- `CaseType`: standardized_product, complex_project
- `LegalDomain`: corporate, ip, labor, tax, litigation, real_estate, immigration, regulatory, data_privacy, commercial
- `CaseComplexity`: low, medium, high, critical
- `CasePriority`: low, medium, high, urgent
- `OriginationChannel`: direct_client, specialist_referral
- `SpecialistStatus`: active, inactive, on_leave
- `SpecialistType`: individual, boutique_firm
- `ProficiencyLevel`: expert, advanced, competent
- `AssignmentRole`: lead, assigned, reviewer, proposed
- `AssignmentStatus`: proposed, accepted, rejected, active, completed
- `DeliverableStatus`: pending, in_progress, review, completed, cancelled
- `PricingAction`: initial_proposal, counter_offer, client_counter, accepted, rejected, margin_adjustment
- `ClientType`: company, individual

### Status Transition Map:
```
intake → [specialist_selection, cancelled]
specialist_selection → [pricing, cancelled]
pricing → [negotiation, active, cancelled]
negotiation → [active, cancelled]
active → [in_progress, cancelled]
in_progress → [pending_client, pending_specialist, delivered, cancelled]
pending_client → [in_progress, cancelled]
pending_specialist → [in_progress, cancelled]
delivered → [closed, in_progress]
closed → []  (terminal)
cancelled → []  (terminal)
```

### DTOs (~40 Pydantic models):
- **Cases:** CaseCreateDTO, CaseUpdateDTO, CaseStatusUpdateDTO, CaseResponseDTO, CaseListResponseDTO, CaseFilterDTO
- **Specialists:** SpecialistCreateDTO, SpecialistUpdateDTO, SpecialistResponseDTO, SpecialistDetailResponseDTO, SpecialistExpertiseDTO, SpecialistJurisdictionDTO
- **Clients:** ClientCreateDTO, ClientUpdateDTO, ClientResponseDTO
- **Assignments:** CaseAssignSpecialistDTO, CaseSpecialistResponseDTO
- **Deliverables:** DeliverableCreateDTO, DeliverableUpdateDTO, DeliverableResponseDTO
- **Messages:** CaseMessageCreateDTO, CaseMessageResponseDTO
- **Documents:** CaseDocumentCreateDTO, CaseDocumentResponseDTO
- **Pricing:** PricingProposalDTO, PricingHistoryResponseDTO
- **Scoring:** SpecialistScoreCreateDTO, SpecialistScoreResponseDTO
- **Assignment Engine:** SpecialistCandidateDTO (specialist + match_score + match_reasons[]), AssignmentSuggestionResponseDTO
- **Classification:** ClassificationResultDTO (legal_domain, case_type, complexity, confidence, reasoning)
- **Analytics:** LegalDeskDashboardStatsDTO (cases_by_status, cases_by_domain, revenue_summary, specialist_performance)

---

## Phase 4: Backend Repositories (7 files)

All in `apps/Server/src/repository/`, following `restaurant_repository.py` pattern:

| File | Key Methods |
|------|-------------|
| `ld_case_repository.py` | create, get_by_id, list_cases(filters), update, update_status, generate_case_number, get_by_client, count_by_status |
| `ld_specialist_repository.py` | create, get_by_id, list_all, update, update_status, get_available(domain, jurisdiction), update_workload, update_overall_score |
| `ld_client_repository.py` | create, get_by_id, list_all, update, search_by_name |
| `ld_assignment_repository.py` | create_assignment, get_case_specialists, get_specialist_cases, update_assignment_status, update_fees |
| `ld_deliverable_repository.py` | create, get_by_case, update, update_status |
| `ld_message_repository.py` | create, get_by_case(include_internal) |
| `ld_analytics_repository.py` | count_cases_by_status, count_cases_by_domain, revenue_pipeline, specialist_performance_rankings, avg_case_duration |

---

## Phase 5: Backend Services (7 files)

All in `apps/Server/src/core/services/`:

### `ld_case_service.py` - Case lifecycle
- create_case, get_case, list_cases, update_case
- update_case_status (validates transitions against CASE_STATUS_TRANSITIONS)
- get_case_with_details (joins specialists, deliverables, messages, documents)

### `ld_assignment_service.py` - **Specialist Assignment Engine** (core differentiator)
- **suggest_specialists(case_id)**: The matching algorithm:
  1. Filter: legal_domain expertise match (mandatory)
  2. Filter: jurisdiction coverage (if case has jurisdiction)
  3. Filter: availability (status=active, current_workload < max_workload)
  4. Score (0-100): expertise_proficiency (30pts), overall_score (25pts), workload_availability (20pts), jurisdiction_match (15pts), years_experience (10pts)
  5. Return top 5 ranked candidates
- assign_specialist, update_assignment_status, get_case_specialists

### `ld_pricing_service.py` - Pricing Engine
- create_proposal (initial proposal with specialist_cost, client_price, margin)
- submit_counter (counter-offer by either party)
- accept_pricing (locks final_quote on case)
- reject_pricing, get_pricing_history
- calculate_margin: margin_pct = ((client_price - specialist_cost) / client_price) * 100

### `ld_classification_service.py` - AI classification (OpenAI GPT-4o-mini)
- classify_case: analyzes title + description, suggests legal_domain, case_type, complexity, confidence
- Keyword-based fallback when API unavailable

### `ld_analytics_service.py` - Dashboard aggregation
- get_dashboard_stats: cases_by_status, cases_by_domain, revenue_summary, specialist_performance, recent_cases

### `ld_specialist_service.py` - Specialist CRUD + scoring
- create/update specialist, add_expertise, add_jurisdiction
- submit_score (recalculates overall_score as average of all scores)
- get_specialist_detail (specialist + expertise[] + jurisdictions[] + scores)

### `ld_client_service.py` - Client CRUD
- create/update/get/list/search clients

---

## Phase 6: Backend Routes + Registration (1 new + 2 modified)

**New:** `apps/Server/src/adapter/rest/legaldesk_routes.py`

Router prefix: `/api/legaldesk`, tags: `["LegalDesk"]`, ~33 endpoints:

| Group | Endpoints |
|-------|-----------|
| **Cases** | POST /cases, GET /cases, GET /cases/{id}, PUT /cases/{id}, PATCH /cases/{id}/status, POST /cases/{id}/classify |
| **Assignments** | GET /cases/{id}/specialists, POST /cases/{id}/specialists, GET /cases/{id}/specialists/suggest, PATCH /cases/{id}/specialists/{aid}/status |
| **Deliverables** | GET /cases/{id}/deliverables, POST /cases/{id}/deliverables, PUT /cases/{id}/deliverables/{did}, PATCH /cases/{id}/deliverables/{did}/status |
| **Messages** | GET /cases/{id}/messages, POST /cases/{id}/messages |
| **Documents** | GET /cases/{id}/documents, POST /cases/{id}/documents |
| **Pricing** | GET /cases/{id}/pricing, POST /cases/{id}/pricing/propose, POST /cases/{id}/pricing/counter, POST /cases/{id}/pricing/accept, POST /cases/{id}/pricing/reject |
| **Specialists** | GET /specialists, POST /specialists, GET /specialists/{id}, PUT /specialists/{id}, POST /specialists/{id}/expertise, POST /specialists/{id}/jurisdictions, POST /specialists/{id}/scores |
| **Clients** | GET /clients, POST /clients, GET /clients/{id}, PUT /clients/{id} |
| **Analytics** | GET /analytics/dashboard |

All endpoints: `Depends(get_current_user)` + `Depends(get_db)`.

**Modify:** `apps/Server/main.py` - register legaldesk_router
**Modify:** `apps/Server/src/config/settings.py` - add OPENAI_API_KEY if not present

---

## Phase 7: Frontend Types + Service (2 new + 1 modified)

### `apps/Client/src/types/legaldesk.ts`
- String literal unions for all enums
- ~25 interfaces: LdCase, LdSpecialist, LdClient, CaseDetail, CaseSpecialist, CaseDeliverable, CaseMessage, CaseDocument, PricingHistoryEntry, SpecialistCandidate, DashboardStats, etc.
- Label/color maps: CASE_STATUS_LABELS, CASE_STATUS_COLORS, LEGAL_DOMAIN_LABELS, PRIORITY_COLORS

### `apps/Client/src/services/legaldeskService.ts`
- Complete API client (~35 methods) for all endpoints following `restaurantService.ts` pattern

**Modify:** `apps/Client/src/types/index.ts` - re-export legaldesk types

---

## Phase 8: Frontend Hooks (6 files)

All in `apps/Client/src/hooks/`, following `useEvents.ts` pattern:

| File | Returns |
|------|---------|
| `useLegaldeskCases.ts` | cases[], isLoading, filters, setFilters, createCase, updateCase |
| `useLegaldeskCaseDetail.ts` | caseDetail, specialists, deliverables, messages, documents, pricingHistory, isLoading, addMessage, updateStatus, classifyCase, suggestSpecialists, assignSpecialist |
| `useLegaldeskSpecialists.ts` | specialists[], isLoading, createSpecialist, updateSpecialist, addExpertise, submitScore |
| `useLegaldeskClients.ts` | clients[], isLoading, createClient, updateClient |
| `useLegaldeskDashboard.ts` | stats, isLoading, error |
| `useLegaldeskPricing.ts` | pricingHistory, propose, counter, accept, reject, isLoading |

---

## Phase 9: Frontend UI Components (6 files)

All in `apps/Client/src/components/ui/`:

| File | Component | Purpose |
|------|-----------|---------|
| `TRCaseStatusBadge.tsx` | `TRCaseStatusBadge` | Colored MUI Chip for case status |
| `TRCasePriorityBadge.tsx` | `TRCasePriorityBadge` | Colored MUI Chip for priority |
| `TRLegalDomainBadge.tsx` | `TRLegalDomainBadge` | MUI Chip with legal domain label |
| `TRSpecialistScoreDisplay.tsx` | `TRSpecialistScoreDisplay` | 5-star rating display with numeric score |
| `TRPricingTimeline.tsx` | `TRPricingTimeline` | MUI Timeline showing negotiation history |
| `TRDeliverableChecklist.tsx` | `TRDeliverableChecklist` | Checklist with status chips for deliverables |

---

## Phase 10: Frontend Forms (3 files)

All in `apps/Client/src/components/forms/`, react-hook-form + MUI:

| File | Component | Key Fields |
|------|-----------|------------|
| `TRLegalCaseForm.tsx` | `TRLegalCaseForm` | title, description, client_id (autocomplete), legal_domain, case_type, complexity, origination, client_budget, deadline, jurisdiction, priority |
| `TRLegalSpecialistForm.tsx` | `TRLegalSpecialistForm` | name, type, email, phone, country, city, years_experience, hourly_rate + sub-sections for expertise and jurisdictions |
| `TRLegalClientForm.tsx` | `TRLegalClientForm` | name, type, contact fields, country, industry |

---

## Phase 11: Frontend Pages (7 files)

All in `apps/Client/src/pages/legaldesk/`:

| Page | Route | Description |
|------|-------|-------------|
| `LegalDeskDashboardPage.tsx` | `/poc/legal-desk/dashboard` | Stat cards (Active Cases, Pipeline Value, Specialists Active, Avg Duration) + Cases by Status pie + Cases by Domain bar + Recent Cases table + Top Specialists |
| `LegalDeskCasesPage.tsx` | `/poc/legal-desk/cases` | Filterable table (status, domain, priority, type) + "New Case" button |
| `LegalDeskNewCasePage.tsx` | `/poc/legal-desk/cases/new` | Full-page TRLegalCaseForm, redirects to detail on submit |
| `LegalDeskCaseDetailPage.tsx` | `/poc/legal-desk/cases/:id` | **Tabbed detail view:** Overview, Specialists (assignment engine + ranked candidates), Deliverables (checklist), Pricing (timeline + actions), Messages (thread), Documents. Status action bar with valid transitions. |
| `LegalDeskSpecialistsPage.tsx` | `/poc/legal-desk/specialists` | Card grid/table with domain chips, score stars, workload indicator + "Add Specialist" dialog |
| `LegalDeskClientsPage.tsx` | `/poc/legal-desk/clients` | Table with "Add Client" dialog |
| `LegalDeskAnalyticsPage.tsx` | `/poc/legal-desk/analytics` | Revenue cards + Charts (cases over time, revenue by domain, specialist utilization) + Performance rankings table |

---

## Phase 12: Frontend Routing + Navigation (2 modified)

**Modify:** `apps/Client/src/App.tsx` - add 8 routes under `/poc/legal-desk/*`
**Modify:** `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx` - add Legal Desk subsection:
- Dashboard (GavelIcon), Cases (BusinessCenterIcon), Specialists (PersonSearchIcon), Clients (GroupsIcon), Analytics (AnalyticsIcon)

---

## File Summary

| Category | New | Modified | Total |
|----------|-----|----------|-------|
| Database | 2 | 0 | 2 |
| Backend Models | 11 | 1 | 12 |
| Backend DTOs | 1 | 0 | 1 |
| Backend Repos | 7 | 0 | 7 |
| Backend Services | 7 | 0 | 7 |
| Backend Routes | 1 | 2 | 3 |
| Frontend Types | 1 | 1 | 2 |
| Frontend Service | 1 | 0 | 1 |
| Frontend Hooks | 6 | 0 | 6 |
| Frontend UI | 6 | 0 | 6 |
| Frontend Forms | 3 | 0 | 3 |
| Frontend Pages | 7 | 0 | 7 |
| Frontend Routing | 0 | 2 | 2 |
| **Total** | **53** | **6** | **59** |

---

## Implementation Sequence (Recommended Build Order)

### Batch 1: Foundation (database + models + DTOs)
1. `apps/Server/database/create_legaldesk_tables.sql` - Run on Supabase
2. `apps/Server/database/seed_legaldesk_data.sql` - Optional seed data
3. All 11 model files in `apps/Server/src/models/`
4. `apps/Server/src/models/__init__.py` update
5. `apps/Server/src/interface/legaldesk_dto.py`

### Batch 2: Backend logic (repos + services + routes)
6. All 7 repository files
7. `ld_client_service.py`, `ld_specialist_service.py` (simpler, no dependencies)
8. `ld_case_service.py` (depends on repos)
9. `ld_assignment_service.py` (depends on specialist + case repos)
10. `ld_pricing_service.py` (depends on case repo)
11. `ld_classification_service.py` (depends on case repo + OpenAI)
12. `ld_analytics_service.py` (depends on all repos)
13. `apps/Server/src/adapter/rest/legaldesk_routes.py`
14. `apps/Server/main.py` update
15. `apps/Server/src/config/settings.py` update (OPENAI_API_KEY)

### Batch 3: Frontend foundation (types + service + hooks)
16. `apps/Client/src/types/legaldesk.ts`
17. `apps/Client/src/types/index.ts` update
18. `apps/Client/src/services/legaldeskService.ts`
19. All 6 hook files

### Batch 4: Frontend UI (components + forms + pages + routing)
20. All 6 UI component files
21. All 3 form files
22. `LegalDeskDashboardPage.tsx`
23. `LegalDeskCasesPage.tsx` + `LegalDeskNewCasePage.tsx`
24. `LegalDeskCaseDetailPage.tsx` (most complex page)
25. `LegalDeskSpecialistsPage.tsx`
26. `LegalDeskClientsPage.tsx`
27. `LegalDeskAnalyticsPage.tsx`
28. `apps/Client/src/App.tsx` update
29. `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx` update

---

## Verification

### Backend (after Batch 2):
1. Run `create_legaldesk_tables.sql` on Supabase
2. Optionally run `seed_legaldesk_data.sql`
3. Start backend: `cd apps/Server && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`
4. Verify `/docs` shows all LegalDesk endpoints under `/api/legaldesk/`
5. Test flow:
   - Create client -> Create specialist (+ expertise + jurisdiction) -> Create case
   - Classify case (AI) -> Suggest specialists -> Assign specialist
   - Propose pricing -> Counter -> Accept
   - Add deliverables -> Update deliverable status
   - Add messages -> Add document metadata
   - Update case status through pipeline
   - Submit specialist score
   - Get dashboard stats

### Frontend (after Batch 4):
1. Start frontend: `cd apps/Client && npm run dev`
2. Type check: `cd apps/Client && npx tsc --noEmit`
3. Build: `cd apps/Client && npm run build`
4. Navigate sidebar -> POCs -> Legal Desk
5. End-to-end: Dashboard loads -> Create client -> Create specialist -> Create case -> View detail -> Tabs all work -> Assignment engine suggests -> Pricing flow -> Analytics page

---

## Key Reference Files
- **Route pattern:** `apps/Server/src/adapter/rest/restaurant_routes.py`
- **Repo pattern:** `apps/Server/src/repository/restaurant_repository.py`
- **Model pattern:** `apps/Server/src/models/event.py`
- **DTO pattern:** `apps/Server/src/interface/event_dto.py`
- **Page pattern:** `apps/Client/src/pages/restaurantos/RestaurantOSDashboardPage.tsx`
- **Form pattern:** `apps/Client/src/components/forms/TREventForm.tsx`
- **Hook pattern:** `apps/Client/src/hooks/useEvents.ts`
- **Sidebar:** `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`
- **ServiceDesk POC plan (source precedent):** `ai_docs/servicedesk_poc_implementation_plan.md`
- **Faroo Legal meeting summary:** `ai_docs/Faroo Legal - Platform Discovery & Proof of Concept Scoping (2).html`
