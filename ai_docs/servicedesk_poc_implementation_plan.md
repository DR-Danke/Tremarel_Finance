# ServiceDesk POC Implementation Plan

## Context

The system-zero repo has a mature ServiceDesk IT ticketing module. The goal is to port it as a full-stack POC into Tremarel_Finance, following the existing RestaurantOS POC patterns (routes under `/poc/servicedesk/*`, `TR` component prefix, SQLAlchemy repos, custom JWT auth).

**Source:** `/mnt/c/Users/user/danke_apps/system-zero/backend/src/core/servicios/servicedesk/` + `frontend/src/`
**Target:** `/mnt/c/Users/user/danke_apps/Tremarel_Finance/`

## Scope

**Include:** Ticket CRUD + status workflow, AI classification (GPT-4o-mini), tiered categories (L1->L2), knowledge base, SLA tracking, analytics dashboard, satisfaction surveys, messages, technician management, auto-assignment.

**Simplify:** KB search (ILIKE instead of vector), SLA (compute on-read, no background jobs), auto-assignment (lowest workload), file attachments (metadata-only, no upload).

**Drop:** Chatbot/Chatbase, VIP, problem management, audit trail, work logs, notification preferences, service catalog, CMDB integration, email/WhatsApp notifications, KB import/generation, similar ticket search.

## Key Architectural Differences

| Aspect | system-zero | Tremarel_Finance |
|--------|------------|-----------------|
| DB access | Supabase Python client | SQLAlchemy ORM with `db: Session` |
| Auth | Supabase JWT | Custom JWT (`get_current_user`) |
| Component prefix | `S0` | `TR` |
| Backend paths | `core/servicios/`, `repositorio/` | `core/services/`, `repository/` |
| MUI version | 7 | 5 |
| Settings | `OPENAI_API_KEY` via Supabase config | Add to `settings.py` |

---

## Phase 1: Database (2 files)

### 1.1 Create tables migration
**New file:** `apps/Server/database/create_servicedesk_tables.sql`

7 tables (simplified from source's ~15+):

| Table | Purpose |
|-------|---------|
| `sd_categories` | Tiered L1/L2 hierarchy (code, name, tier, parent_id) |
| `sd_technicians` | Support staff (user_id FK to `users`, role, status, support_level, workload) |
| `sd_tickets` | Core tickets (status workflow, priority, category, ticket_type, SLA fields, ai_classification JSONB) |
| `sd_ticket_messages` | Conversation thread per ticket |
| `sd_ticket_attachments` | File metadata (URL-only, no binary upload) |
| `sd_knowledge_articles` | KB articles (title, content, status, visibility) |
| `sd_satisfaction_feedback` | Post-resolution ratings |

Indexes on: status, priority, requester_email, technician FK, ticket_id FKs, category tier.

**Dropped tables vs source:** sd_organizations, sd_departments, sd_ticket_patterns, sd_assignment_history, sd_work_logs, sd_audit_logs, sd_sla_configurations, sd_notification_preferences, sd_chatbot_interactions, sd_vip_users, sd_critical_types, sd_service_catalog, sd_technician_expertises, sd_locations.

### 1.2 Seed categories
**New file:** `apps/Server/database/seed_servicedesk_categories.sql`

5 L1 categories: Hardware, Software, SAP, Telecomunicaciones, Otros
~5 L2 subcategories per L1 parent (25 total)

---

## Phase 2: Backend Models (7 files)

All in `apps/Server/src/models/`, following existing pattern from `apps/Server/src/models/event.py`:

| File | Model | Table |
|------|-------|-------|
| `sd_category.py` | `SdCategory` | `sd_categories` |
| `sd_technician.py` | `SdTechnician` | `sd_technicians` |
| `sd_ticket.py` | `SdTicket` | `sd_tickets` |
| `sd_message.py` | `SdMessage` | `sd_ticket_messages` |
| `sd_attachment.py` | `SdAttachment` | `sd_ticket_attachments` |
| `sd_knowledge_article.py` | `SdKnowledgeArticle` | `sd_knowledge_articles` |
| `sd_feedback.py` | `SdFeedback` | `sd_satisfaction_feedback` |

**Modify:** `apps/Server/src/models/__init__.py` -- register new models

---

## Phase 3: Backend DTOs (1 file)

**New file:** `apps/Server/src/interface/servicedesk_dto.py`

Port and simplify from source `backend/src/interface/servicedesk_dtos.py`:

**Enums (~12):**
- TicketStatus, TicketPriority, TicketCategory, TicketType, TicketChannel
- ImpactLevel, UrgencyLevel, CategoryTier
- TechnicianStatus, TechnicianRole
- FeedbackRating, ArticleStatus, ArticleVisibility

**Request/Response DTOs (~30 Pydantic models, down from source's ~80+):**
- Ticket: Create, Update, Response, ListResponse, Filter, Assign
- Message: Create, Response
- Technician: Create, Update, Response, ListResponse
- Article: Create, Update, Response, ListResponse
- Category: Response, TreeResponse
- Feedback: Create, Response
- Analytics: DashboardStats
- Classification: ClassifyResponse, CategorySuggestionResponse

---

## Phase 4: Backend Repositories (5 files)

All in `apps/Server/src/repository/`, using SQLAlchemy `db: Session` pattern.

**Reference pattern:** `apps/Server/src/repository/event_repository.py`

| File | Key Methods |
|------|-------------|
| `sd_ticket_repository.py` | create, get, list (with filters), update, get_by_requester, get_backlog, create_message, get_messages, generate_ticket_number |
| `sd_technician_repository.py` | create, get, list, update, update_status, get_available (for auto-assignment) |
| `sd_category_repository.py` | list_all, get_tree (L1 with children), get_by_code |
| `sd_knowledge_repository.py` | create, get, list, update, search (ILIKE on title+content) |
| `sd_analytics_repository.py` | count_by_status, count_by_priority, count_by_category, avg_resolution_time, sla_compliance_rate |

---

## Phase 5: Backend Services (5 files)

All in `apps/Server/src/core/services/`:

| File | Responsibility | Source Reference |
|------|---------------|-----------------|
| `sd_ticket_service.py` | Status transition validation, SLA deadline calc (static matrix), ticket number gen, auto-assignment (lowest workload) | `system-zero/.../ticket_service.py` + `sla_service.py` |
| `sd_classification_service.py` | OpenAI GPT-4o-mini classification, L1 category prompts, entity extraction, rule-based fallback with Spanish keywords | `system-zero/.../classification_service.py` + `classification_config.py` |
| `sd_knowledge_service.py` | Article CRUD, keyword-based search & suggestions | `system-zero/.../knowledge_service.py` |
| `sd_analytics_service.py` | Dashboard stats aggregation | `system-zero/.../analytics_service.py` |
| `sd_satisfaction_service.py` | Feedback submission, ticket-resolved validation | `system-zero/.../satisfaction_service.py` |

### SLA Matrix (static, embedded in ticket service)
| Priority | Response Time | Resolution Time |
|----------|--------------|-----------------|
| Critical | 15 min | 4 hours |
| High | 1 hour | 8 hours |
| Medium | 4 hours | 24 hours |
| Low | 8 hours | 48 hours |

### Status Transitions (ported from source)
```
new -> open, in_progress, closed
open -> in_progress, pending_customer, resolved, closed
in_progress -> pending_customer, resolved, closed
pending_customer -> in_progress, resolved, closed
resolved -> closed, reopened
closed -> reopened
reopened -> open, in_progress
```

---

## Phase 6: Backend Routes + Registration (1 new + 2 modified)

**New file:** `apps/Server/src/adapter/rest/servicedesk_routes.py`

Router prefix: `/api/servicedesk`, tags: `["ServiceDesk"]`

~25 endpoints (down from source's ~80+):

| Group | Endpoints |
|-------|-----------|
| Tickets | POST /tickets, GET /tickets, GET /tickets/{id}, PUT /tickets/{id}, PUT /tickets/{id}/status, POST /tickets/{id}/assign, GET /tickets/my, GET /tickets/backlog |
| Messages | POST /tickets/{id}/messages, GET /tickets/{id}/messages |
| Classification | POST /tickets/{id}/classify, POST /classify/suggest-category |
| Technicians | GET /technicians, POST /technicians, PUT /technicians/{id} |
| Knowledge | GET /knowledge, POST /knowledge, GET /knowledge/{id}, PUT /knowledge/{id}, GET /knowledge/search, GET /knowledge/suggest/{ticket_id} |
| Categories | GET /categories, GET /categories/tree |
| Analytics | GET /analytics/dashboard |
| Feedback | POST /tickets/{id}/feedback |

Auth: `Depends(get_current_user)` + `Depends(get_db)` on all endpoints.

**Modify:** `apps/Server/main.py` -- import and register `servicedesk_router`
**Modify:** `apps/Server/src/config/settings.py` -- add `OPENAI_API_KEY: str = ""` field

---

## Phase 7: Frontend Types + Service (2 new + 1 modified)

**New file:** `apps/Client/src/types/servicedesk.ts`

Type unions and interfaces (~20):
- Enums as string literal unions: TicketStatus, TicketPriority, TicketCategory, TicketType, TicketChannel, TechnicianStatus, SLAStatus, FeedbackRating, ArticleStatus
- Interfaces: Ticket, TicketCreate, TicketUpdate, TicketListResponse, TicketDetail, TicketFilters, Message, MessageCreate, Technician, TechnicianCreate, KnowledgeArticle, ArticleCreate, CategoryItem, CategoryTree, DashboardStats, FeedbackSubmit, ClassificationResult, CategorySuggestion

**Modify:** `apps/Client/src/types/index.ts` -- re-export servicedesk types

**New file:** `apps/Client/src/services/servicedeskService.ts`

API client following `restaurantService.ts` pattern with methods for: tickets CRUD, messages, classification, technicians, knowledge, categories, analytics, feedback.

---

## Phase 8: Frontend Hooks (5 files)

All in `apps/Client/src/hooks/`, following `useEvents.ts` pattern:

| File | Returns |
|------|---------|
| `useServicedeskTickets.ts` | tickets[], isLoading, error, filters, createTicket, updateTicket, assignTicket |
| `useServicedeskTicketDetail.ts` | ticket, messages, isLoading, addMessage, updateStatus, classifyTicket |
| `useServicedeskKnowledge.ts` | articles[], isLoading, createArticle, searchArticles |
| `useServicedeskDashboard.ts` | stats, isLoading, error |
| `useServicedeskCategories.ts` | categories[], tree[], isLoading |

---

## Phase 9: Frontend UI Components (4 files)

All in `apps/Client/src/components/ui/`:

| File | Component | Purpose |
|------|-----------|---------|
| `TRTicketStatusBadge.tsx` | `TRTicketStatusBadge` | Colored MUI Chip for ticket status |
| `TRTicketPriorityBadge.tsx` | `TRTicketPriorityBadge` | Colored MUI Chip for priority level |
| `TRSLABar.tsx` | `TRSLABar` | Linear progress bar for SLA countdown |
| `TRTieredCategorySelector.tsx` | `TRTieredCategorySelector` | L1/L2 dropdown selector with icons |

---

## Phase 10: Frontend Forms (2 files)

In `apps/Client/src/components/forms/`, following `TREventForm.tsx` pattern:

| File | Component | Features |
|------|-----------|----------|
| `TRServicedeskTicketForm.tsx` | `TRServicedeskTicketForm` | react-hook-form, AI category suggestion, tiered category selector, priority, impact/urgency, ticket type |
| `TRServicedeskArticleForm.tsx` | `TRServicedeskArticleForm` | react-hook-form, title, content, category, status, visibility |

---

## Phase 11: Frontend Pages (5 files)

All in `apps/Client/src/pages/servicedesk/`:

| File | Route | Description |
|------|-------|-------------|
| `ServicedeskDashboardPage.tsx` | `/poc/servicedesk/dashboard` | Overview stat cards (Recharts), ticket list table with filters, status/priority/category breakdown |
| `ServicedeskNewTicketPage.tsx` | `/poc/servicedesk/new-ticket` | Ticket creation form + "my tickets" tab for end users |
| `ServicedeskTicketDetailPage.tsx` | `/poc/servicedesk/tickets/:id` | Ticket detail panel, conversation thread, status actions, assignment, SLA bar |
| `ServicedeskKnowledgePage.tsx` | `/poc/servicedesk/knowledge` | Article list, search bar, create/edit dialog, category filter |
| `ServicedeskTechniciansPage.tsx` | `/poc/servicedesk/technicians` | Technician table, create/edit dialog, status management |

---

## Phase 12: Frontend Routing + Navigation (2 modified files)

**Modify:** `apps/Client/src/App.tsx` -- add 6 routes under `/poc/servicedesk/*`:
- `/poc/servicedesk` -> redirect to `/poc/servicedesk/dashboard`
- `/poc/servicedesk/dashboard`
- `/poc/servicedesk/new-ticket`
- `/poc/servicedesk/tickets/:id`
- `/poc/servicedesk/knowledge`
- `/poc/servicedesk/technicians`

**Modify:** `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx` -- add ServiceDesk subsection to POCs:
- Dashboard, Nuevo Ticket, Base de Conocimiento, Tecnicos

---

## File Summary

| Category | New Files | Modified Files | Total |
|----------|-----------|----------------|-------|
| Database | 2 | 0 | 2 |
| Backend Models | 7 | 1 | 8 |
| Backend DTOs | 1 | 0 | 1 |
| Backend Repos | 5 | 0 | 5 |
| Backend Services | 5 | 0 | 5 |
| Backend Routes | 1 | 2 | 3 |
| Frontend Types | 1 | 1 | 2 |
| Frontend Service | 1 | 0 | 1 |
| Frontend Hooks | 5 | 0 | 5 |
| Frontend UI | 4 | 0 | 4 |
| Frontend Forms | 2 | 0 | 2 |
| Frontend Pages | 5 | 0 | 5 |
| Frontend Routing | 0 | 2 | 2 |
| **Total** | **39** | **6** | **45** |

---

## Verification

### After backend complete (Phase 6):
1. Run SQL migrations on Supabase DB
2. Start backend: `cd apps/Server && python -m uvicorn main:app --reload --port 8000`
3. Verify `/docs` shows all ServiceDesk endpoints
4. Test flow: create technician -> create ticket -> get ticket -> classify -> assign -> add message -> update status -> submit feedback -> get dashboard stats

### After frontend complete (Phase 12):
1. Start frontend: `cd apps/Client && npm run dev`
2. Type check: `cd apps/Client && npx tsc --noEmit`
3. Build: `cd apps/Client && npm run build`
4. Navigate sidebar -> POCs -> ServiceDesk
5. End-to-end: create ticket -> view in list -> click detail -> add message -> assign -> resolve -> submit feedback -> check dashboard

### Key Reference Files
- **Target route pattern:** `apps/Server/src/adapter/rest/restaurant_routes.py`
- **Target repo pattern:** `apps/Server/src/repository/event_repository.py`
- **Target page pattern:** `apps/Client/src/pages/restaurantos/RestaurantOSEventsPage.tsx`
- **Target form pattern:** `apps/Client/src/components/forms/TREventForm.tsx`
- **Target hook pattern:** `apps/Client/src/hooks/useEvents.ts`
- **Source classification logic:** `system-zero/backend/src/core/servicios/servicedesk/classification_service.py`
- **Source classification config:** `system-zero/backend/src/core/servicios/servicedesk/classification_config.py`
- **Source DTOs:** `system-zero/backend/src/interface/servicedesk_dtos.py`
