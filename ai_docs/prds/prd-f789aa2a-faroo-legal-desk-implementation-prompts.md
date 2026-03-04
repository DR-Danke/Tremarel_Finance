# Faroo Legal Desk - ADW Implementation Prompts

## Overview

This plan contains GitHub issue prompts for implementing the Faroo Legal Desk Case Management & Specialist Assignment POC using `adw_sdlc_iso.py`. Each prompt will trigger the `/feature` command which handles technical planning.

**Source:** Discovery and proof-of-concept scoping session with Faroo Legal stakeholders and Tremarel team.
**Requirements Doc:** `ai_docs/prds/prd-44f6fa8f-faroo-legal-desk-poc.md`

**Project Goal:** Build a centralized platform to replace Faroo Legal's manual operations (currently WhatsApp, email, Notion) across four key areas: intelligent specialist-to-case assignment, pricing negotiation with margin management, case lifecycle tracking with deliverables, and specialist performance scoring. The POC adapts the existing ServiceDesk ticketing pattern (Tickets → Cases, Technicians → Specialists) while introducing domain-specific concepts like a Pricing Engine, multi-specialist assignments, and deliverables tracking.

**Key Concepts:**
1. **Case** — A legal matter submitted by a client, tracked through an 11-stage lifecycle (from `new` to `closed`/`archived`)
2. **Specialist** — A lawyer (individual or boutique firm) from Faroo's 400-500 network, matched to cases by domain expertise, jurisdiction, and scoring
3. **Assignment Engine** — Core differentiator: intelligent matching algorithm scoring specialists on expertise (30pts), overall score (25pts), workload availability (20pts), jurisdiction (15pts), experience (10pts)
4. **Pricing Engine** — Negotiation lifecycle (propose → counter → accept/reject) with Faroo margin calculation: `margin_pct = ((client_price - specialist_cost) / client_price) * 100`
5. **Deliverables** — Milestones/work products within a case with status tracking (pending → in_progress → review → completed)
6. **AI Classification** — GPT-4o-mini classifies cases by legal domain, type, complexity, with keyword-based fallback

**Execution**: `uv run adw_sdlc_iso.py <issue-number>`

**Parallelization**: Issues within the same wave can run simultaneously in separate worktrees (up to 15 concurrent).

**Naming Conventions:**
- Component prefix: `TR` (TRLegalCaseForm, TRCaseStatusBadge, TRPricingTimeline)
- Database table prefix: `ld_` (ld_cases, ld_specialists, ld_clients)
- Route prefix: `/poc/legal-desk/*` (frontend), `/api/legaldesk/*` (backend)
- Model prefix: `Ld` (LdCase, LdSpecialist, LdClient)

**Terminology:**
- **Case** = Legal matter (equivalent to ServiceDesk Ticket)
- **Specialist** = Lawyer/firm (equivalent to ServiceDesk Technician)
- **Legal Domain** = Practice area (corporate, ip, labor, etc.)
- **Jurisdiction** = Geographic coverage (country + region)
- **Flete/Margin** = `((client_price - specialist_cost) / client_price) * 100`
- **Case Number** = Format `LD-YYYYMM-NNNN`

---

## Wave 1: Foundation (Run in Parallel)

Establish the data contracts: database schema, seed data, ORM models, Pydantic DTOs/enums, and frontend TypeScript types. These have no runtime dependencies on each other and define the interfaces that all subsequent layers build upon.

### LD-001: Legal Desk Database Schema

**Title:** `[Legal Desk] Wave 1: Database Schema (11 Tables)`

**Body:**
```markdown
## Context
**Project:** Faroo Legal Desk — Case Management & Specialist Assignment POC
**Overview:** Create the relational database schema for all Legal Desk entities. This establishes 11 PostgreSQL tables with `ld_` prefix covering clients, specialists (with expertise and jurisdictions), cases (with assignments, deliverables, messages, documents), pricing history, and specialist scores. Includes indexes, foreign keys, unique constraints, and `updated_at` triggers.

**Current Wave:** Wave 1 of 6 — Foundation
**Current Issue:** LD-001 (Issue 1 of 16)
**Parallel Execution:** YES — This issue runs in parallel with LD-002, LD-003, LD-004, LD-005.

**Dependencies:** None
**What comes next:** Wave 2 repositories and Wave 3 services will query these tables. LD-002 seed data depends on this schema existing.

## Request
Create the complete Legal Desk database schema SQL file.

### 1. Schema SQL File
Create `apps/Server/database/create_legaldesk_tables.sql` with all 11 tables:

```sql
-- ld_clients
CREATE TABLE IF NOT EXISTS ld_clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(20) NOT NULL DEFAULT 'company',  -- company | individual
    contact_email VARCHAR(200),
    contact_phone VARCHAR(50),
    country VARCHAR(100),
    industry VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ld_specialists
CREATE TABLE IF NOT EXISTS ld_specialists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    type VARCHAR(20) NOT NULL DEFAULT 'individual',  -- individual | boutique_firm
    email VARCHAR(200),
    phone VARCHAR(50),
    country VARCHAR(100),
    city VARCHAR(100),
    years_experience INTEGER DEFAULT 0,
    hourly_rate DECIMAL(10, 2),
    status VARCHAR(20) DEFAULT 'active',  -- active | inactive | on_leave
    max_workload INTEGER DEFAULT 5,
    current_workload INTEGER DEFAULT 0,
    overall_score DECIMAL(3, 2) DEFAULT 0.00,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ld_specialist_expertise
CREATE TABLE IF NOT EXISTS ld_specialist_expertise (
    id SERIAL PRIMARY KEY,
    specialist_id INTEGER NOT NULL REFERENCES ld_specialists(id) ON DELETE CASCADE,
    legal_domain VARCHAR(50) NOT NULL,
    proficiency_level VARCHAR(20) NOT NULL DEFAULT 'intermediate',  -- junior | intermediate | expert
    UNIQUE(specialist_id, legal_domain)
);

-- ld_specialist_jurisdictions
CREATE TABLE IF NOT EXISTS ld_specialist_jurisdictions (
    id SERIAL PRIMARY KEY,
    specialist_id INTEGER NOT NULL REFERENCES ld_specialists(id) ON DELETE CASCADE,
    country VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    is_primary BOOLEAN DEFAULT false,
    UNIQUE(specialist_id, country, region)
);

-- ld_cases
CREATE TABLE IF NOT EXISTS ld_cases (
    id SERIAL PRIMARY KEY,
    case_number VARCHAR(20) NOT NULL UNIQUE,  -- LD-YYYYMM-NNNN
    title VARCHAR(300) NOT NULL,
    description TEXT,
    client_id INTEGER REFERENCES ld_clients(id),
    legal_domain VARCHAR(50),
    case_type VARCHAR(20) DEFAULT 'advisory',  -- advisory | litigation
    complexity VARCHAR(20) DEFAULT 'medium',  -- low | medium | high | critical
    priority VARCHAR(20) DEFAULT 'medium',  -- low | medium | high | urgent
    origination_channel VARCHAR(20) DEFAULT 'direct',  -- direct | referral
    status VARCHAR(30) DEFAULT 'new',
    jurisdiction VARCHAR(200),
    client_budget DECIMAL(15, 2),
    estimated_cost DECIMAL(15, 2),
    final_quote DECIMAL(15, 2),
    faroo_margin_pct DECIMAL(5, 2),
    deadline DATE,
    ai_classification JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ld_case_specialists (assignments)
CREATE TABLE IF NOT EXISTS ld_case_specialists (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES ld_cases(id) ON DELETE CASCADE,
    specialist_id INTEGER NOT NULL REFERENCES ld_specialists(id),
    role VARCHAR(30) DEFAULT 'lead',  -- lead | support | reviewer | consultant
    status VARCHAR(30) DEFAULT 'proposed',  -- proposed | accepted | rejected | active | completed
    proposed_fee DECIMAL(15, 2),
    agreed_fee DECIMAL(15, 2),
    fee_type VARCHAR(20) DEFAULT 'fixed',  -- fixed | hourly | contingency | hybrid
    assigned_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMPTZ
);

-- ld_case_deliverables
CREATE TABLE IF NOT EXISTS ld_case_deliverables (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES ld_cases(id) ON DELETE CASCADE,
    specialist_id INTEGER REFERENCES ld_specialists(id),
    title VARCHAR(300) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',  -- pending | in_progress | review | completed | cancelled
    due_date DATE,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ld_case_messages
CREATE TABLE IF NOT EXISTS ld_case_messages (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES ld_cases(id) ON DELETE CASCADE,
    sender_type VARCHAR(20) NOT NULL,  -- faroo_staff | specialist | client | system
    sender_name VARCHAR(200),
    content TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ld_case_documents
CREATE TABLE IF NOT EXISTS ld_case_documents (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES ld_cases(id) ON DELETE CASCADE,
    title VARCHAR(300) NOT NULL,
    document_type VARCHAR(50),
    url VARCHAR(500),
    uploaded_by VARCHAR(200),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ld_pricing_history
CREATE TABLE IF NOT EXISTS ld_pricing_history (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES ld_cases(id) ON DELETE CASCADE,
    action VARCHAR(20) NOT NULL,  -- proposal | counter | accept | reject | adjust | final
    specialist_cost DECIMAL(15, 2),
    client_price DECIMAL(15, 2),
    margin_pct DECIMAL(5, 2),
    notes TEXT,
    created_by VARCHAR(200),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ld_specialist_scores
CREATE TABLE IF NOT EXISTS ld_specialist_scores (
    id SERIAL PRIMARY KEY,
    specialist_id INTEGER NOT NULL REFERENCES ld_specialists(id) ON DELETE CASCADE,
    case_id INTEGER REFERENCES ld_cases(id),
    quality_score DECIMAL(3, 2),
    teamwork_score DECIMAL(3, 2),
    delivery_score DECIMAL(3, 2),
    satisfaction_score DECIMAL(3, 2),
    comments TEXT,
    scored_by VARCHAR(200),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Indexes
Add indexes on frequently queried columns:
```sql
CREATE INDEX IF NOT EXISTS idx_ld_cases_status ON ld_cases(status);
CREATE INDEX IF NOT EXISTS idx_ld_cases_legal_domain ON ld_cases(legal_domain);
CREATE INDEX IF NOT EXISTS idx_ld_cases_client ON ld_cases(client_id);
CREATE INDEX IF NOT EXISTS idx_ld_cases_priority ON ld_cases(priority);
CREATE INDEX IF NOT EXISTS idx_ld_case_specialists_case ON ld_case_specialists(case_id);
CREATE INDEX IF NOT EXISTS idx_ld_case_specialists_specialist ON ld_case_specialists(specialist_id);
CREATE INDEX IF NOT EXISTS idx_ld_deliverables_case ON ld_case_deliverables(case_id);
CREATE INDEX IF NOT EXISTS idx_ld_messages_case ON ld_case_messages(case_id);
CREATE INDEX IF NOT EXISTS idx_ld_documents_case ON ld_case_documents(case_id);
CREATE INDEX IF NOT EXISTS idx_ld_pricing_case ON ld_pricing_history(case_id);
CREATE INDEX IF NOT EXISTS idx_ld_scores_specialist ON ld_specialist_scores(specialist_id);
CREATE INDEX IF NOT EXISTS idx_ld_expertise_specialist ON ld_specialist_expertise(specialist_id);
CREATE INDEX IF NOT EXISTS idx_ld_jurisdictions_specialist ON ld_specialist_jurisdictions(specialist_id);
```

### 3. Triggers
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_ld_clients_updated_at BEFORE UPDATE ON ld_clients FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ld_specialists_updated_at BEFORE UPDATE ON ld_specialists FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ld_cases_updated_at BEFORE UPDATE ON ld_cases FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ld_deliverables_updated_at BEFORE UPDATE ON ld_case_deliverables FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

**Validation:** Script must execute successfully on Supabase PostgreSQL. All 11 tables created with correct types, constraints, and relationships.
```

---

### LD-002: Legal Desk Seed Data

**Title:** `[Legal Desk] Wave 1: Seed Data for Development`

**Body:**
```markdown
## Context
**Project:** Faroo Legal Desk — Case Management & Specialist Assignment POC
**Overview:** Create seed data for development and testing: 5 specialists with varied expertise and jurisdictions, 3 clients (mix of company and individual types), and 2 cases at different pipeline stages with deliverables. This data enables meaningful testing of the assignment engine's matching and scoring logic.

**Current Wave:** Wave 1 of 6 — Foundation
**Current Issue:** LD-002 (Issue 2 of 16)
**Parallel Execution:** YES — This issue runs in parallel with LD-001, LD-003, LD-004, LD-005. However, this SQL depends on LD-001 schema existing at runtime.

**Dependencies:** LD-001 (schema must exist to insert data)
**What comes next:** Wave 2 repositories will use this data for manual testing.

## Request
Create seed data SQL covering all core Legal Desk entities.

### 1. Seed Data SQL
Create `apps/Server/database/seed_legaldesk_data.sql`:

- **5 Specialists** covering domains: corporate, ip, labor, tax, litigation. Mix of individual and boutique_firm types. Vary years_experience (3-20), hourly_rate, and max_workload. Each specialist gets 2-3 expertise entries at different proficiency levels and 1-2 jurisdiction entries across different countries (Colombia, Mexico, USA, Spain).

- **3 Clients**: one large company (tech industry), one mid-size company (finance), one individual.

- **2 Cases**: one at `new` status (corporate domain, medium complexity) and one at `in_progress` status (ip domain, high complexity) with:
  - 2 case_specialist assignments (one proposed, one active)
  - 3 deliverables per case at different statuses
  - 2-3 messages per case
  - 1 pricing_history entry per case

**Validation:** Script executes successfully after schema creation. Data supports testing the assignment engine with meaningful domain/jurisdiction matches.
```

---

### LD-003: SQLAlchemy ORM Models

**Title:** `[Legal Desk] Wave 1: SQLAlchemy ORM Models (11 Models)`

**Body:**
```markdown
## Context
**Project:** Faroo Legal Desk — Case Management & Specialist Assignment POC
**Overview:** Create 11 SQLAlchemy ORM model files mapping to the `ld_` tables. These models define the Python-level data access interface that repositories will use. Follow the existing `event.py` pattern: Base class inheritance, explicit `__tablename__`, typed columns, and relationship definitions.

**Current Wave:** Wave 1 of 6 — Foundation
**Current Issue:** LD-003 (Issue 3 of 16)
**Parallel Execution:** YES — This issue runs in parallel with LD-001, LD-002, LD-004, LD-005.

**Dependencies:** None (models map to schema from LD-001 but can be written independently)
**What comes next:** Wave 2 repositories will import these models for database queries.

## Request
Create 11 SQLAlchemy model files and register them.

### 1. Model Files
Create the following files in `apps/Server/src/models/`:

- `ld_client.py` — `LdClient` model mapping to `ld_clients`
- `ld_specialist.py` — `LdSpecialist` model mapping to `ld_specialists`
- `ld_specialist_expertise.py` — `LdSpecialistExpertise` mapping to `ld_specialist_expertise`
- `ld_specialist_jurisdiction.py` — `LdSpecialistJurisdiction` mapping to `ld_specialist_jurisdictions`
- `ld_case.py` — `LdCase` mapping to `ld_cases` (includes JSONB column for `ai_classification`)
- `ld_case_specialist.py` — `LdCaseSpecialist` mapping to `ld_case_specialists`
- `ld_case_deliverable.py` — `LdCaseDeliverable` mapping to `ld_case_deliverables`
- `ld_case_message.py` — `LdCaseMessage` mapping to `ld_case_messages`
- `ld_case_document.py` — `LdCaseDocument` mapping to `ld_case_documents`
- `ld_pricing_history.py` — `LdPricingHistory` mapping to `ld_pricing_history`
- `ld_specialist_score.py` — `LdSpecialistScore` mapping to `ld_specialist_scores`

Each model should follow the existing `event.py` pattern:
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Numeric, Text, Date
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from src.config.database import Base
from datetime import datetime

class LdCase(Base):
    __tablename__ = "ld_cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(20), unique=True, nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    client_id = Column(Integer, ForeignKey("ld_clients.id"))
    legal_domain = Column(String(50))
    # ... all columns matching schema
    ai_classification = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    client = relationship("LdClient", backref="cases")
    specialists = relationship("LdCaseSpecialist", backref="case")
    deliverables = relationship("LdCaseDeliverable", backref="case")
    messages = relationship("LdCaseMessage", backref="case")
    documents = relationship("LdCaseDocument", backref="case")
    pricing_history = relationship("LdPricingHistory", backref="case")
```

### 2. Register Models
Update `apps/Server/src/models/__init__.py` to import and register all 11 models.

**Validation:** All models map correctly to their `ld_` tables. Column types, defaults, and nullable flags match the schema. Relationships are properly defined between models.
```

---

### LD-004: Pydantic DTOs and Enums

**Title:** `[Legal Desk] Wave 1: Pydantic DTOs & Enums`

**Body:**
```markdown
## Context
**Project:** Faroo Legal Desk — Case Management & Specialist Assignment POC
**Overview:** Define the complete set of Pydantic DTOs and enums for all Legal Desk API operations. This single file contains 14 enums, ~40 Pydantic models covering CRUD, filtering, responses, and specialized DTOs for the assignment engine, classification, pricing, and analytics. Includes the case status transition map as a constant dictionary.

**Current Wave:** Wave 1 of 6 — Foundation
**Current Issue:** LD-004 (Issue 4 of 16)
**Parallel Execution:** YES — This issue runs in parallel with LD-001, LD-002, LD-003, LD-005.

**Dependencies:** None
**What comes next:** Wave 2 repositories and Wave 3 services will use these DTOs for input validation and response serialization.

## Request
Create the comprehensive DTO and enum file for Legal Desk.

### 1. DTOs and Enums
Create `apps/Server/src/interface/legaldesk_dto.py`:

**14 Enums:**
```python
from enum import Enum

class CaseStatus(str, Enum):
    NEW = "new"
    CLASSIFYING = "classifying"
    OPEN = "open"
    ASSIGNING = "assigning"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    NEGOTIATING = "negotiating"
    COMPLETED = "completed"
    CLOSED = "closed"
    ARCHIVED = "archived"

class CaseType(str, Enum):
    ADVISORY = "advisory"
    LITIGATION = "litigation"

class LegalDomain(str, Enum):
    CORPORATE = "corporate"
    IP = "ip"
    LABOR = "labor"
    TAX = "tax"
    LITIGATION = "litigation"
    REAL_ESTATE = "real_estate"
    IMMIGRATION = "immigration"
    REGULATORY = "regulatory"
    DATA_PRIVACY = "data_privacy"
    COMMERCIAL = "commercial"

class CaseComplexity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CasePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class OriginationChannel(str, Enum):
    DIRECT = "direct"
    REFERRAL = "referral"

class SpecialistStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"

class SpecialistType(str, Enum):
    INDIVIDUAL = "individual"
    BOUTIQUE_FIRM = "boutique_firm"

class ProficiencyLevel(str, Enum):
    JUNIOR = "junior"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"

class AssignmentRole(str, Enum):
    LEAD = "lead"
    SUPPORT = "support"
    REVIEWER = "reviewer"
    CONSULTANT = "consultant"

class AssignmentStatus(str, Enum):
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ACTIVE = "active"
    COMPLETED = "completed"

class DeliverableStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PricingAction(str, Enum):
    PROPOSAL = "proposal"
    COUNTER = "counter"
    ACCEPT = "accept"
    REJECT = "reject"
    ADJUST = "adjust"
    FINAL = "final"

class ClientType(str, Enum):
    COMPANY = "company"
    INDIVIDUAL = "individual"
```

**Status Transition Map:**
```python
CASE_STATUS_TRANSITIONS: dict[str, list[str]] = {
    "new": ["classifying", "open"],
    "classifying": ["open"],
    "open": ["assigning", "active"],
    "assigning": ["active", "open"],
    "active": ["in_progress", "negotiating"],
    "in_progress": ["review", "completed"],
    "review": ["in_progress", "completed"],
    "negotiating": ["active", "closed"],
    "completed": ["closed"],
    "closed": ["archived"],
    "archived": [],
}
```

**~40 DTOs covering:**
- Cases: `CaseCreateDTO`, `CaseUpdateDTO`, `CaseResponseDTO`, `CaseDetailDTO`, `CaseFilterDTO`, `CaseListItemDTO`
- Specialists: `SpecialistCreateDTO`, `SpecialistUpdateDTO`, `SpecialistResponseDTO`, `SpecialistDetailDTO`, `SpecialistFilterDTO`, `ExpertiseDTO`
- Clients: `ClientCreateDTO`, `ClientUpdateDTO`, `ClientResponseDTO`
- Assignments: `AssignmentCreateDTO`, `AssignmentResponseDTO`
- Deliverables: `DeliverableCreateDTO`, `DeliverableUpdateDTO`, `DeliverableResponseDTO`
- Messages: `MessageCreateDTO`, `MessageResponseDTO`
- Documents: `DocumentCreateDTO`, `DocumentResponseDTO`
- Pricing: `PricingProposalDTO`, `PricingHistoryResponseDTO`
- Scoring: `ScoreSubmitDTO`, `ScoreResponseDTO`
- Assignment Engine: `SpecialistCandidateDTO`, `SuggestionResponseDTO`
- Classification: `ClassificationResultDTO`
- Analytics: `DashboardStatsDTO`

All DTOs use proper Pydantic v2 syntax with type hints. `CaseFilterDTO` supports filtering by status, legal_domain, priority, case_type, client_id.

**Validation:** No `any` types. All DTOs match the database schema and API contract.
```

---

### LD-005: Frontend TypeScript Types

**Title:** `[Legal Desk] Wave 1: Frontend TypeScript Types & Maps`

**Body:**
```markdown
## Context
**Project:** Faroo Legal Desk — Case Management & Specialist Assignment POC
**Overview:** Define all Legal Desk TypeScript types: string literal unions for all 14 enums, ~25 interfaces covering all API response and request shapes, plus label and color maps for UI rendering (status badges, priority chips, domain labels). Re-export from the types index.

**Current Wave:** Wave 1 of 6 — Foundation
**Current Issue:** LD-005 (Issue 5 of 16)
**Parallel Execution:** YES — This issue runs in parallel with LD-001, LD-002, LD-003, LD-004.

**Dependencies:** None
**What comes next:** Wave 5 frontend service and hooks will use these types. Wave 6 UI components use the label/color maps.

## Request
Create the complete TypeScript types file for Legal Desk.

### 1. Types File
Create `apps/Client/src/types/legaldesk.ts`:

**String Literal Unions (14):**
```typescript
export type CaseStatus = 'new' | 'classifying' | 'open' | 'assigning' | 'active' | 'in_progress' | 'review' | 'negotiating' | 'completed' | 'closed' | 'archived';
export type CaseType = 'advisory' | 'litigation';
export type LegalDomain = 'corporate' | 'ip' | 'labor' | 'tax' | 'litigation' | 'real_estate' | 'immigration' | 'regulatory' | 'data_privacy' | 'commercial';
export type CaseComplexity = 'low' | 'medium' | 'high' | 'critical';
export type CasePriority = 'low' | 'medium' | 'high' | 'urgent';
export type OriginationChannel = 'direct' | 'referral';
export type SpecialistStatus = 'active' | 'inactive' | 'on_leave';
export type SpecialistType = 'individual' | 'boutique_firm';
export type ProficiencyLevel = 'junior' | 'intermediate' | 'expert';
export type AssignmentRole = 'lead' | 'support' | 'reviewer' | 'consultant';
export type AssignmentStatus = 'proposed' | 'accepted' | 'rejected' | 'active' | 'completed';
export type DeliverableStatus = 'pending' | 'in_progress' | 'review' | 'completed' | 'cancelled';
export type PricingAction = 'proposal' | 'counter' | 'accept' | 'reject' | 'adjust' | 'final';
export type ClientType = 'company' | 'individual';
```

**Interfaces (~25):**
```typescript
export interface LdCase {
  id: number;
  case_number: string;
  title: string;
  description?: string;
  client_id?: number;
  legal_domain?: LegalDomain;
  case_type: CaseType;
  complexity: CaseComplexity;
  priority: CasePriority;
  status: CaseStatus;
  jurisdiction?: string;
  client_budget?: number;
  estimated_cost?: number;
  final_quote?: number;
  faroo_margin_pct?: number;
  deadline?: string;
  ai_classification?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface LdCaseDetail extends LdCase {
  client?: LdClient;
  specialists: CaseSpecialist[];
  deliverables: CaseDeliverable[];
  messages: CaseMessage[];
  documents: CaseDocument[];
  pricing_history: PricingHistoryEntry[];
}

// ... all other interfaces for Specialist, Client, CaseSpecialist,
// CaseDeliverable, CaseMessage, CaseDocument, PricingHistoryEntry,
// SpecialistCandidate, DashboardStats, etc.
```

**Label & Color Maps:**
```typescript
export const CASE_STATUS_LABELS: Record<CaseStatus, string> = {
  new: 'New', classifying: 'Classifying', open: 'Open',
  assigning: 'Assigning', active: 'Active', in_progress: 'In Progress',
  review: 'Review', negotiating: 'Negotiating', completed: 'Completed',
  closed: 'Closed', archived: 'Archived',
};

export const CASE_STATUS_COLORS: Record<CaseStatus, string> = {
  new: '#2196F3', classifying: '#9C27B0', open: '#4CAF50',
  assigning: '#FF9800', active: '#00BCD4', in_progress: '#3F51B5',
  review: '#FFC107', negotiating: '#E91E63', completed: '#8BC34A',
  closed: '#607D8B', archived: '#9E9E9E',
};

export const LEGAL_DOMAIN_LABELS: Record<LegalDomain, string> = { ... };
export const PRIORITY_COLORS: Record<CasePriority, string> = { ... };
export const COMPLEXITY_LABELS: Record<CaseComplexity, string> = { ... };
```

### 2. Re-export
Update `apps/Client/src/types/index.ts` to re-export all Legal Desk types.

**Validation:** No `any` types. All interfaces match API response shapes from LD-004 DTOs.
```

---

## Wave 2: Backend Data Access (Run in Parallel)

All 7 repositories implement the data access layer. They depend on ORM models (Wave 1) but have no inter-repository dependencies, so they can all be built in parallel.

### LD-006: Case Repository + Specialist Repository + Client Repository

**Title:** `[Legal Desk] Wave 2: Core Repositories (Case, Specialist, Client)`

**Body:**
```markdown
## Context
**Project:** Faroo Legal Desk — Case Management & Specialist Assignment POC
**Overview:** Implement the three core repositories: Case (CRUD with filtering, status updates, case number generation), Specialist (CRUD with availability filtering and score management), and Client (CRUD with name search). These repositories form the data access foundation for all business services.

**Current Wave:** Wave 2 of 6 — Backend Data Access
**Current Issue:** LD-006 (Issue 6 of 16)
**Parallel Execution:** YES — This issue runs in parallel with LD-007.

**Dependencies:** LD-003 (ORM models), LD-004 (DTOs)
**What comes next:** Wave 3 services will use these repositories for business logic.

## Request
Create three repository files implementing data access for cases, specialists, and clients.

### 1. Case Repository
Create `apps/Server/src/repository/ld_case_repository.py`:
- `create(case_data: dict) -> LdCase` — Insert new case
- `get_by_id(case_id: int) -> Optional[LdCase]` — Get case with client relationship
- `list_cases(filters: CaseFilterDTO, limit: int, offset: int) -> list[LdCase]` — Filter by status, legal_domain, priority, case_type, client_id
- `update(case_id: int, data: dict) -> LdCase` — Update case fields
- `update_status(case_id: int, status: str) -> LdCase` — Update case status
- `generate_case_number() -> str` — Format: `LD-YYYYMM-NNNN` (sequential within month)
- `get_by_client(client_id: int) -> list[LdCase]`
- `count_by_status() -> dict` — Aggregation for dashboard

Follow `restaurant_repository.py` pattern for session management and query construction.

### 2. Specialist Repository
Create `apps/Server/src/repository/ld_specialist_repository.py`:
- `create(data: dict) -> LdSpecialist`
- `get_by_id(specialist_id: int) -> Optional[LdSpecialist]` — Include expertise and jurisdictions
- `list_all(filters: dict) -> list[LdSpecialist]`
- `update(specialist_id: int, data: dict) -> LdSpecialist`
- `update_status(specialist_id: int, status: str) -> LdSpecialist`
- `get_available(domain: str, jurisdiction: Optional[str]) -> list[LdSpecialist]` — Filter by domain expertise match, jurisdiction coverage, active status, workload < max_workload
- `update_workload(specialist_id: int, delta: int)` — Increment/decrement current_workload
- `update_overall_score(specialist_id: int)` — Recalculate from ld_specialist_scores average

### 3. Client Repository
Create `apps/Server/src/repository/ld_client_repository.py`:
- `create(data: dict) -> LdClient`
- `get_by_id(client_id: int) -> Optional[LdClient]`
- `list_all() -> list[LdClient]`
- `update(client_id: int, data: dict) -> LdClient`
- `search_by_name(query: str) -> list[LdClient]` — Case-insensitive partial match using ILIKE

**Validation:** All CRUD operations work correctly. Specialist availability filtering matches domain + jurisdiction + active + workload criteria. Case number generation produces sequential `LD-YYYYMM-NNNN` format.
```

---

### LD-007: Assignment, Deliverable, Message, Analytics Repositories

**Title:** `[Legal Desk] Wave 2: Supporting Repositories (Assignment, Deliverable, Message, Analytics)`

**Body:**
```markdown
## Context
**Project:** Faroo Legal Desk — Case Management & Specialist Assignment POC
**Overview:** Implement the four supporting repositories: Assignment (case-specialist links with fees), Deliverable (milestones with status tracking), Message (case communication threads), and Analytics (dashboard aggregations). These complete the data access layer.

**Current Wave:** Wave 2 of 6 — Backend Data Access
**Current Issue:** LD-007 (Issue 7 of 16)
**Parallel Execution:** YES — This issue runs in parallel with LD-006.

**Dependencies:** LD-003 (ORM models), LD-004 (DTOs)
**What comes next:** Wave 3 services will use these repositories.

## Request
Create four repository files.

### 1. Assignment Repository
Create `apps/Server/src/repository/ld_assignment_repository.py`:
- `create_assignment(data: dict) -> LdCaseSpecialist`
- `get_case_specialists(case_id: int) -> list[LdCaseSpecialist]` — All specialists assigned to a case
- `get_specialist_cases(specialist_id: int) -> list[LdCaseSpecialist]` — All cases for a specialist
- `update_assignment_status(assignment_id: int, status: str) -> LdCaseSpecialist`
- `update_fees(assignment_id: int, proposed_fee: Decimal, agreed_fee: Decimal, fee_type: str) -> LdCaseSpecialist`

### 2. Deliverable Repository
Create `apps/Server/src/repository/ld_deliverable_repository.py`:
- `create(data: dict) -> LdCaseDeliverable`
- `get_by_case(case_id: int) -> list[LdCaseDeliverable]`
- `update(deliverable_id: int, data: dict) -> LdCaseDeliverable`
- `update_status(deliverable_id: int, status: str) -> LdCaseDeliverable` — Status transitions: pending → in_progress → review → completed/cancelled

### 3. Message Repository
Create `apps/Server/src/repository/ld_message_repository.py`:
- `create(data: dict) -> LdCaseMessage` — Stores sender_type (faroo_staff/specialist/client/system)
- `get_by_case(case_id: int, include_internal: bool = False) -> list[LdCaseMessage]` — When `include_internal=False`, exclude messages where `is_internal=True`

### 4. Analytics Repository
Create `apps/Server/src/repository/ld_analytics_repository.py`:
- `count_cases_by_status() -> dict` — GROUP BY status
- `count_cases_by_domain() -> dict` — GROUP BY legal_domain
- `revenue_pipeline() -> dict` — Sum estimated_cost and final_quote for active cases
- `specialist_performance_rankings() -> list` — Ranked by overall_score
- `avg_case_duration() -> float` — Average time from created_at to completed_at for completed cases

**Validation:** Assignment fees are correctly persisted and updated. Message `include_internal` flag properly filters internal messages. Analytics aggregations return correct counts.
```

---

## Wave 3: Backend Business Logic (Run in Parallel)

Core business services including the Assignment Engine, Pricing Engine, and AI Classification. Each service depends on repositories (Wave 2) but not on other services, so they can run in parallel.

### LD-008: Case Lifecycle Service + Client Service + Specialist Service

**Title:** `[Legal Desk] Wave 3: Core Services (Case, Client, Specialist)`

**Body:**
```markdown
## Context
**Project:** Faroo Legal Desk — Case Management & Specialist Assignment POC
**Overview:** Implement the three core business services: Case Lifecycle (creation, updates, status transitions with validation), Client (CRUD + search), and Specialist (CRUD + expertise/jurisdiction management + scoring). These manage the fundamental entities of the Legal Desk domain.

**Current Wave:** Wave 3 of 6 — Backend Business Logic
**Current Issue:** LD-008 (Issue 8 of 16)
**Parallel Execution:** YES — This issue runs in parallel with LD-009, LD-010, LD-011.

**Dependencies:** LD-004 (DTOs with CASE_STATUS_TRANSITIONS), LD-006 (Case, Specialist, Client repositories)
**What comes next:** Wave 4 API routes will expose these services as endpoints.

## Request
Create three service files implementing core business logic.

### 1. Case Lifecycle Service
Create `apps/Server/src/core/services/ld_case_service.py`:
- `create_case(data: CaseCreateDTO, current_user: dict) -> CaseResponseDTO` — Generates case_number, persists all fields
- `update_case(case_id: int, data: CaseUpdateDTO) -> CaseResponseDTO`
- `update_case_status(case_id: int, new_status: str) -> CaseResponseDTO` — Validates against `CASE_STATUS_TRANSITIONS` map; rejects invalid transitions (e.g., closed → active)
- `get_case_with_details(case_id: int) -> CaseDetailDTO` — Joins specialists, deliverables, messages, documents, pricing history
- `list_cases(filters: CaseFilterDTO) -> list[CaseListItemDTO]`
- INFO-level logging on all operations using `print(f"INFO [LdCaseService]: ...")`

### 2. Client Service
Create `apps/Server/src/core/services/ld_client_service.py`:
- `create(data: ClientCreateDTO) -> ClientResponseDTO`
- `update(client_id: int, data: ClientUpdateDTO) -> ClientResponseDTO`
- `get(client_id: int) -> ClientResponseDTO`
- `list_all() -> list[ClientResponseDTO]`
- `search(query: str) -> list[ClientResponseDTO]`

### 3. Specialist Service
Create `apps/Server/src/core/services/ld_specialist_service.py`:
- `create(data: SpecialistCreateDTO) -> SpecialistResponseDTO`
- `update(specialist_id: int, data: SpecialistUpdateDTO) -> SpecialistResponseDTO`
- `get_specialist_detail(specialist_id: int) -> SpecialistDetailDTO` — Returns specialist with expertise[], jurisdictions[], scores[]
- `list_all(filters: dict) -> list[SpecialistResponseDTO]`
- `add_expertise(specialist_id: int, domain: str, proficiency: str)` — Adds legal domain proficiency entry
- `add_jurisdiction(specialist_id: int, country: str, region: str, is_primary: bool)`
- `submit_score(specialist_id: int, case_id: int, scores: ScoreSubmitDTO)` — Records per-case scores (quality, teamwork, delivery, satisfaction) and recalculates overall_score as average

**Validation:** Case status transitions are validated against CASE_STATUS_TRANSITIONS. Invalid transitions raise appropriate errors. All operations have INFO-level logging.
```

---

### LD-009: Specialist Assignment Engine

**Title:** `[Legal Desk] Wave 3: Specialist Assignment Engine`

**Body:**
```markdown
## Context
**Project:** Faroo Legal Desk — Case Management & Specialist Assignment POC
**Overview:** This is the core differentiator — an intelligent specialist matching algorithm. `suggest_specialists(case_id)` performs multi-stage filtering (domain match, jurisdiction, availability) then scores candidates on a 0-100 scale across 5 weighted factors. Returns top 5 ranked candidates with match scores and detailed reasoning. Also handles specialist assignment and status management.

**Current Wave:** Wave 3 of 6 — Backend Business Logic
**Current Issue:** LD-009 (Issue 9 of 16)
**Parallel Execution:** YES — This issue runs in parallel with LD-008, LD-010, LD-011.

**Dependencies:** LD-004 (DTOs), LD-006 (Case, Specialist repositories), LD-007 (Assignment repository)
**What comes next:** Wave 4 API routes will expose `GET /cases/{id}/specialists/suggest` endpoint.

## Request
Implement the intelligent specialist assignment service.

### 1. Assignment Service
Create `apps/Server/src/core/services/ld_assignment_service.py`:

**`suggest_specialists(case_id: int) -> SuggestionResponseDTO`:**
1. Fetch case details (legal_domain, jurisdiction)
2. **Mandatory Filter:** legal_domain expertise match — exclude specialists without matching expertise entry
3. **Jurisdiction Filter:** If case has jurisdiction set, filter by matching jurisdiction coverage (country match, or country+region match)
4. **Availability Filter:** Exclude specialists with status != 'active' or current_workload >= max_workload
5. **Scoring (0-100 scale):**
   - `expertise_proficiency` (30 pts): expert=30, intermediate=20, junior=10
   - `overall_score` (25 pts): `specialist.overall_score / 5.0 * 25`
   - `workload_availability` (20 pts): `((max_workload - current_workload) / max_workload) * 20`
   - `jurisdiction_match` (15 pts): exact region match=15, country-only match=10, no jurisdiction on case=15 (full points)
   - `years_experience` (10 pts): `min(years_experience / 20 * 10, 10)`
6. **Ranking:** Sort by match_score descending, return top 5
7. Each candidate includes `match_reasons: list[str]` explaining score components (e.g., "Expert-level corporate law proficiency (+30pts)")

```python
def _calculate_match_score(self, specialist, case, expertise) -> tuple[float, list[str]]:
    score = 0.0
    reasons = []

    # Expertise proficiency (30 pts)
    proficiency_scores = {"expert": 30, "intermediate": 20, "junior": 10}
    prof_score = proficiency_scores.get(expertise.proficiency_level, 10)
    score += prof_score
    reasons.append(f"{expertise.proficiency_level.capitalize()}-level {case.legal_domain} proficiency (+{prof_score}pts)")

    # Overall score (25 pts)
    score_pts = (specialist.overall_score / 5.0) * 25
    score += score_pts
    reasons.append(f"Overall rating {specialist.overall_score}/5.0 (+{score_pts:.0f}pts)")

    # Workload availability (20 pts)
    avail = ((specialist.max_workload - specialist.current_workload) / specialist.max_workload) * 20
    score += avail
    reasons.append(f"Workload {specialist.current_workload}/{specialist.max_workload} (+{avail:.0f}pts)")

    # Jurisdiction match (15 pts)
    # ... jurisdiction scoring logic ...

    # Years experience (10 pts)
    exp_pts = min(specialist.years_experience / 20 * 10, 10)
    score += exp_pts
    reasons.append(f"{specialist.years_experience} years experience (+{exp_pts:.0f}pts)")

    return score, reasons
```

**`assign_specialist(case_id, specialist_id, role, proposed_fee, fee_type)`:**
- Creates assignment record
- Updates specialist workload (+1)
- Returns assignment details

**`update_assignment_status(assignment_id, status)`:**
- Updates assignment status
- If status is 'completed' or 'rejected', decrements specialist workload (-1)

**`get_case_specialists(case_id)`:**
- Returns all assignments for a case with specialist details

**Validation:** Scoring weights sum to 100. Top 5 candidates returned sorted by match_score descending. Workload is properly incremented/decremented on assignment changes.
```

---

### LD-010: Pricing Engine

**Title:** `[Legal Desk] Wave 3: Pricing Negotiation Engine`

**Body:**
```markdown
## Context
**Project:** Faroo Legal Desk — Case Management & Specialist Assignment POC
**Overview:** Manages the pricing negotiation lifecycle between Faroo Legal, specialists, and clients. Tracks proposals, counter-offers, acceptance, and rejection with full audit trail. Acceptance locks the `final_quote` and `faroo_margin_pct` on the case. Margin formula: `margin_pct = ((client_price - specialist_cost) / client_price) * 100`.

**Current Wave:** Wave 3 of 6 — Backend Business Logic
**Current Issue:** LD-010 (Issue 10 of 16)
**Parallel Execution:** YES — This issue runs in parallel with LD-008, LD-009, LD-011.

**Dependencies:** LD-004 (DTOs), LD-006 (Case repository)
**What comes next:** Wave 4 API routes will expose pricing endpoints. Wave 6 frontend will render the pricing timeline.

## Request
Implement the pricing negotiation service.

### 1. Pricing Service
Create `apps/Server/src/core/services/ld_pricing_service.py`:

- **`create_proposal(case_id, specialist_cost, client_price, notes, created_by)`:**
  - Calculate margin: `margin_pct = ((client_price - specialist_cost) / client_price) * 100`
  - Store in `ld_pricing_history` with action='proposal'
  - Update case `estimated_cost = specialist_cost`
  - Log: `INFO [LdPricingService]: Proposal for case {case_id}: specialist_cost={specialist_cost}, client_price={client_price}, margin={margin_pct:.1f}%`

- **`submit_counter(case_id, specialist_cost, client_price, notes, created_by)`:**
  - Recalculate margin
  - Store in pricing_history with action='counter'
  - Log counter-offer details

- **`accept_pricing(case_id, created_by)`:**
  - Get latest pricing entry
  - Lock `final_quote = client_price` and `faroo_margin_pct = margin_pct` on the case record
  - Store in pricing_history with action='accept'
  - Log acceptance

- **`reject_pricing(case_id, notes, created_by)`:**
  - Store in pricing_history with action='reject'
  - Log rejection with notes

- **`get_pricing_history(case_id) -> list[PricingHistoryResponseDTO]`:**
  - Return chronological pricing history for the case

**Validation:** Margin calculation correct: `((client_price - specialist_cost) / client_price) * 100`. Acceptance locks final_quote and faroo_margin_pct on case. Full audit trail in ld_pricing_history.
```

---

### LD-011: AI Case Classification + Analytics Service

**Title:** `[Legal Desk] Wave 3: AI Classification & Analytics Service`

**Body:**
```markdown
## Context
**Project:** Faroo Legal Desk — Case Management & Specialist Assignment POC
**Overview:** Two services: (1) AI Classification uses OpenAI GPT-4o-mini to classify cases by legal domain, type, complexity, and confidence. Falls back to keyword-based classification when API is unavailable. (2) Analytics Service provides dashboard aggregation stats.

**Current Wave:** Wave 3 of 6 — Backend Business Logic
**Current Issue:** LD-011 (Issue 11 of 16)
**Parallel Execution:** YES — This issue runs in parallel with LD-008, LD-009, LD-010.

**Dependencies:** LD-004 (DTOs), LD-006 (Case repository), LD-007 (Analytics repository)
**What comes next:** Wave 4 API routes will expose `POST /cases/{id}/classify` and `GET /analytics/dashboard`.

## Request
Implement AI classification and analytics services.

### 1. Classification Service
Create `apps/Server/src/core/services/ld_classification_service.py`:

- **`classify_case(case_id: int) -> ClassificationResultDTO`:**
  1. Fetch case title and description
  2. If `OPENAI_API_KEY` is configured, call GPT-4o-mini with a prompt requesting:
     - `legal_domain` (from LegalDomain enum values)
     - `case_type` (advisory or litigation)
     - `complexity` (low/medium/high/critical)
     - `confidence` (0.0-1.0)
     - `reasoning` (brief explanation)
  3. Parse JSON response into `ClassificationResultDTO`
  4. Store result in case's `ai_classification` JSONB field
  5. On OpenAI error or missing key, fall back to keyword-based classification

- **Keyword Fallback:**
  ```python
  DOMAIN_KEYWORDS = {
      "corporate": ["merger", "acquisition", "shareholder", "board", "incorporation", "corporate"],
      "ip": ["patent", "trademark", "copyright", "intellectual property", "brand"],
      "labor": ["employment", "worker", "termination", "labor", "harassment", "wage"],
      "tax": ["tax", "fiscal", "irs", "deduction", "filing"],
      "litigation": ["lawsuit", "court", "dispute", "damages", "trial"],
      # ... other domains
  }
  ```

### 2. Settings Update
Add `OPENAI_API_KEY` to `apps/Server/src/config/settings.py` if not already present (optional env var).

### 3. Analytics Service
Create `apps/Server/src/core/services/ld_analytics_service.py`:

- **`get_dashboard_stats() -> DashboardStatsDTO`:**
  - `cases_by_status` — dict of status → count
  - `cases_by_domain` — dict of legal_domain → count
  - `revenue_summary` — pipeline value (active cases estimated_cost) and closed revenue (completed cases final_quote)
  - `specialist_performance` — ranked list with names, scores, case counts
  - `recent_cases` — latest 10 cases with basic info

**Validation:** Classification falls back gracefully when OpenAI API is unavailable. OPENAI_API_KEY is optional. Dashboard stats return correct aggregations.
```

---

## Wave 4: Backend API (Run in Parallel)

Expose all Legal Desk functionality through RESTful API endpoints and register the router in the application.

### LD-012: Legal Desk API Routes + Registration

**Title:** `[Legal Desk] Wave 4: API Routes (~33 Endpoints) & App Registration`

**Body:**
```markdown
## Context
**Project:** Faroo Legal Desk — Case Management & Specialist Assignment POC
**Overview:** Create a single route file with ~33 endpoints under `/api/legaldesk` prefix covering all Legal Desk operations. All endpoints require JWT authentication. Register the router in the FastAPI application entry point. After this wave, the entire backend is functional and testable via Swagger UI.

**Current Wave:** Wave 4 of 6 — Backend API
**Current Issue:** LD-012 (Issue 12 of 16)
**Parallel Execution:** NO — Single issue in this wave.

**Dependencies:** LD-008 (Case, Client, Specialist services), LD-009 (Assignment service), LD-010 (Pricing service), LD-011 (Classification, Analytics services)
**What comes next:** Wave 5 frontend service and hooks will call these endpoints.

## Request
Create the API routes file and register it in the application.

### 1. Routes File
Create `apps/Server/src/adapter/rest/legaldesk_routes.py`:

All endpoints use `Depends(get_current_user)` and `Depends(get_db)`.

**Case Endpoints (6):**
```python
router = APIRouter(prefix="/api/legaldesk", tags=["Legal Desk"])

@router.post("/cases")                          # Create case
@router.get("/cases")                           # List cases (with filters)
@router.get("/cases/{case_id}")                 # Get case detail
@router.put("/cases/{case_id}")                 # Update case
@router.patch("/cases/{case_id}/status")        # Update case status
@router.post("/cases/{case_id}/classify")       # AI classify case
```

**Assignment Endpoints (4):**
```python
@router.get("/cases/{case_id}/specialists")           # Get case specialists
@router.post("/cases/{case_id}/specialists")          # Assign specialist
@router.get("/cases/{case_id}/specialists/suggest")   # Suggest specialists (Assignment Engine)
@router.patch("/cases/{case_id}/specialists/{aid}/status")  # Update assignment status
```

**Deliverable Endpoints (4):**
```python
@router.get("/cases/{case_id}/deliverables")              # List deliverables
@router.post("/cases/{case_id}/deliverables")             # Create deliverable
@router.put("/cases/{case_id}/deliverables/{did}")        # Update deliverable
@router.patch("/cases/{case_id}/deliverables/{did}/status")  # Update deliverable status
```

**Message Endpoints (2):**
```python
@router.get("/cases/{case_id}/messages")    # Get messages (with include_internal query param)
@router.post("/cases/{case_id}/messages")   # Create message
```

**Document Endpoints (2):**
```python
@router.get("/cases/{case_id}/documents")   # List documents
@router.post("/cases/{case_id}/documents")  # Add document metadata
```

**Pricing Endpoints (5):**
```python
@router.get("/cases/{case_id}/pricing")           # Get pricing history
@router.post("/cases/{case_id}/pricing/propose")  # Create proposal
@router.post("/cases/{case_id}/pricing/counter")  # Submit counter-offer
@router.post("/cases/{case_id}/pricing/accept")   # Accept pricing
@router.post("/cases/{case_id}/pricing/reject")   # Reject pricing
```

**Specialist Endpoints (7):**
```python
@router.get("/specialists")                         # List all specialists
@router.post("/specialists")                        # Create specialist
@router.get("/specialists/{specialist_id}")          # Get specialist detail
@router.put("/specialists/{specialist_id}")          # Update specialist
@router.post("/specialists/{specialist_id}/expertise")      # Add expertise
@router.post("/specialists/{specialist_id}/jurisdictions")  # Add jurisdiction
@router.post("/specialists/{specialist_id}/scores")         # Submit score
```

**Client Endpoints (4):**
```python
@router.get("/clients")            # List clients
@router.post("/clients")           # Create client
@router.get("/clients/{client_id}")  # Get client
@router.put("/clients/{client_id}")  # Update client
```

**Analytics Endpoint (1):**
```python
@router.get("/analytics/dashboard")  # Get dashboard stats
```

### 2. App Registration
Update `apps/Server/main.py`:
```python
from src.adapter.rest.legaldesk_routes import router as legaldesk_router
app.include_router(legaldesk_router)
```

### 3. Settings Update
Ensure `OPENAI_API_KEY` is available in `apps/Server/src/config/settings.py` as an optional environment variable.

**Validation:** All ~33 endpoints accessible under `/api/legaldesk/`. Every endpoint requires JWT authentication. All endpoints visible in `/docs` Swagger UI. Backend starts without errors.
```

---

## Wave 5: Frontend Data Layer (Run in Parallel)

API service client and React hooks providing the data layer for all UI components.

### LD-013: Frontend API Service + React Hooks

**Title:** `[Legal Desk] Wave 5: API Service & React Hooks`

**Body:**
```markdown
## Context
**Project:** Faroo Legal Desk — Case Management & Specialist Assignment POC
**Overview:** Create the frontend API service client (~35 methods covering all endpoints) and 6 custom React hooks that encapsulate Legal Desk data operations. The service uses the authenticated Axios client with JWT interceptor. The hooks provide loading states, error handling, and data management for all UI pages.

**Current Wave:** Wave 5 of 6 — Frontend Data Layer
**Current Issue:** LD-013 (Issue 13 of 16)
**Parallel Execution:** NO — Single issue in this wave (hooks depend on service).

**Dependencies:** LD-005 (TypeScript types), LD-012 (API endpoints available)
**What comes next:** Wave 6 UI components and pages will consume these hooks.

## Request
Create the API service and all React hooks.

### 1. API Service
Create `apps/Client/src/services/legaldeskService.ts`:

Follow `restaurantService.ts` pattern using the authenticated Axios client.

```typescript
import { apiClient } from '@/api/clients/apiClient';
import type { LdCase, LdCaseDetail, LdSpecialist, LdClient, ... } from '@/types/legaldesk';

const BASE = '/legaldesk';

export const legaldeskService = {
  // Cases
  createCase: (data: CaseCreateData) => apiClient.post<LdCase>(`${BASE}/cases`, data),
  listCases: (filters?: CaseFilters) => apiClient.get<LdCase[]>(`${BASE}/cases`, { params: filters }),
  getCase: (id: number) => apiClient.get<LdCaseDetail>(`${BASE}/cases/${id}`),
  updateCase: (id: number, data: CaseUpdateData) => apiClient.put<LdCase>(`${BASE}/cases/${id}`, data),
  updateCaseStatus: (id: number, status: string) => apiClient.patch(`${BASE}/cases/${id}/status`, { status }),
  classifyCase: (id: number) => apiClient.post(`${BASE}/cases/${id}/classify`),

  // Assignments
  getCaseSpecialists: (caseId: number) => apiClient.get(`${BASE}/cases/${caseId}/specialists`),
  assignSpecialist: (caseId: number, data: AssignmentCreateData) => apiClient.post(`${BASE}/cases/${caseId}/specialists`, data),
  suggestSpecialists: (caseId: number) => apiClient.get(`${BASE}/cases/${caseId}/specialists/suggest`),
  updateAssignmentStatus: (caseId: number, assignmentId: number, status: string) => apiClient.patch(`${BASE}/cases/${caseId}/specialists/${assignmentId}/status`, { status }),

  // Deliverables
  getDeliverables: (caseId: number) => apiClient.get(`${BASE}/cases/${caseId}/deliverables`),
  createDeliverable: (caseId: number, data: DeliverableCreateData) => apiClient.post(`${BASE}/cases/${caseId}/deliverables`, data),
  updateDeliverable: (caseId: number, deliverableId: number, data: DeliverableUpdateData) => apiClient.put(`${BASE}/cases/${caseId}/deliverables/${deliverableId}`, data),
  updateDeliverableStatus: (caseId: number, deliverableId: number, status: string) => apiClient.patch(`${BASE}/cases/${caseId}/deliverables/${deliverableId}/status`, { status }),

  // Messages
  getMessages: (caseId: number, includeInternal?: boolean) => apiClient.get(`${BASE}/cases/${caseId}/messages`, { params: { include_internal: includeInternal } }),
  createMessage: (caseId: number, data: MessageCreateData) => apiClient.post(`${BASE}/cases/${caseId}/messages`, data),

  // Documents
  getDocuments: (caseId: number) => apiClient.get(`${BASE}/cases/${caseId}/documents`),
  addDocument: (caseId: number, data: DocumentCreateData) => apiClient.post(`${BASE}/cases/${caseId}/documents`, data),

  // Pricing
  getPricingHistory: (caseId: number) => apiClient.get(`${BASE}/cases/${caseId}/pricing`),
  createPricingProposal: (caseId: number, data: PricingProposalData) => apiClient.post(`${BASE}/cases/${caseId}/pricing/propose`, data),
  submitCounter: (caseId: number, data: PricingProposalData) => apiClient.post(`${BASE}/cases/${caseId}/pricing/counter`, data),
  acceptPricing: (caseId: number) => apiClient.post(`${BASE}/cases/${caseId}/pricing/accept`),
  rejectPricing: (caseId: number, notes?: string) => apiClient.post(`${BASE}/cases/${caseId}/pricing/reject`, { notes }),

  // Specialists
  listSpecialists: () => apiClient.get<LdSpecialist[]>(`${BASE}/specialists`),
  createSpecialist: (data: SpecialistCreateData) => apiClient.post<LdSpecialist>(`${BASE}/specialists`, data),
  getSpecialist: (id: number) => apiClient.get(`${BASE}/specialists/${id}`),
  updateSpecialist: (id: number, data: SpecialistUpdateData) => apiClient.put(`${BASE}/specialists/${id}`, data),
  addExpertise: (id: number, data: ExpertiseData) => apiClient.post(`${BASE}/specialists/${id}/expertise`, data),
  addJurisdiction: (id: number, data: JurisdictionData) => apiClient.post(`${BASE}/specialists/${id}/jurisdictions`, data),
  submitScore: (id: number, data: ScoreData) => apiClient.post(`${BASE}/specialists/${id}/scores`, data),

  // Clients
  listClients: () => apiClient.get<LdClient[]>(`${BASE}/clients`),
  createClient: (data: ClientCreateData) => apiClient.post<LdClient>(`${BASE}/clients`, data),
  getClient: (id: number) => apiClient.get<LdClient>(`${BASE}/clients/${id}`),
  updateClient: (id: number, data: ClientUpdateData) => apiClient.put<LdClient>(`${BASE}/clients/${id}`, data),

  // Analytics
  getDashboardStats: () => apiClient.get(`${BASE}/analytics/dashboard`),
};
```

### 2. React Hooks
Create the following hooks in `apps/Client/src/hooks/`:

- **`useLegaldeskCases.ts`** — Cases list with filters (status, domain, priority, type) + CRUD operations. Returns `{ cases, loading, error, filters, setFilters, createCase, refreshCases }`.

- **`useLegaldeskCaseDetail.ts`** — Full case detail with all sub-entities. Returns `{ caseDetail, loading, error, updateStatus, assignSpecialist, suggestSpecialists, candidates, addDeliverable, updateDeliverableStatus, addMessage, addDocument, refreshCase }`.

- **`useLegaldeskSpecialists.ts`** — Specialist list + CRUD + scoring. Returns `{ specialists, loading, error, createSpecialist, addExpertise, addJurisdiction, submitScore, refreshSpecialists }`.

- **`useLegaldeskClients.ts`** — Client list + CRUD. Returns `{ clients, loading, error, createClient, updateClient, refreshClients }`.

- **`useLegaldeskDashboard.ts`** — Dashboard stats. Returns `{ stats, loading, error, refreshStats }`.

- **`useLegaldeskPricing.ts`** — Pricing workflow for a case. Returns `{ history, loading, propose, counter, accept, reject, refreshPricing }`.

All hooks follow `useEvents.ts` pattern with loading state, error handling, and data management.

**Validation:** All service methods properly typed. All hooks return loading state, error handling, and data. No `any` types.
```

---

## Wave 6: Frontend UI (Run in Parallel)

All UI components, forms, pages, and routing. These depend on types (Wave 1) and hooks (Wave 5). Grouped into three parallel issues: components + forms, pages, and routing.

### LD-014: UI Components + Forms

**Title:** `[Legal Desk] Wave 6: UI Components & Forms`

**Body:**
```markdown
## Context
**Project:** Faroo Legal Desk — Case Management & Specialist Assignment POC
**Overview:** Build 6 reusable UI components (badges, score display, pricing timeline, deliverable checklist) and 3 react-hook-form based forms (case, specialist, client). These are the building blocks used by all Legal Desk pages.

**Current Wave:** Wave 6 of 6 — Frontend UI
**Current Issue:** LD-014 (Issue 14 of 16)
**Parallel Execution:** YES — This issue runs in parallel with LD-015, LD-016.

**Dependencies:** LD-005 (TypeScript types with label/color maps), LD-013 (React hooks)
**What comes next:** LD-015 pages will compose these components.

## Request
Create 6 UI components and 3 forms.

### 1. UI Components
Create in `apps/Client/src/components/ui/`:

- **`TRCaseStatusBadge.tsx`** — MUI Chip displaying case status with color from `CASE_STATUS_COLORS` map and label from `CASE_STATUS_LABELS`.
  ```typescript
  interface TRCaseStatusBadgeProps { status: CaseStatus; size?: 'small' | 'medium'; }
  ```

- **`TRCasePriorityBadge.tsx`** — MUI Chip for case priority with colors: low=green, medium=blue, high=orange, urgent=red.
  ```typescript
  interface TRCasePriorityBadgeProps { priority: CasePriority; }
  ```

- **`TRLegalDomainBadge.tsx`** — MUI Chip with domain label from `LEGAL_DOMAIN_LABELS`.
  ```typescript
  interface TRLegalDomainBadgeProps { domain: LegalDomain; }
  ```

- **`TRSpecialistScoreDisplay.tsx`** — 5-star rating visual (using MUI Rating component) with numeric score.
  ```typescript
  interface TRSpecialistScoreDisplayProps { score: number; showNumeric?: boolean; }
  ```

- **`TRPricingTimeline.tsx`** — MUI Timeline component showing chronological negotiation history entries. Each entry shows action type, amounts, margin, date, and notes.
  ```typescript
  interface TRPricingTimelineProps { history: PricingHistoryEntry[]; }
  ```

- **`TRDeliverableChecklist.tsx`** — Checklist with status chips and due dates. Each deliverable shows title, assigned specialist, status badge, and due date.
  ```typescript
  interface TRDeliverableChecklistProps {
    deliverables: CaseDeliverable[];
    onStatusChange?: (id: number, status: DeliverableStatus) => void;
  }
  ```

### 2. Forms
Create in `apps/Client/src/components/forms/`:

- **`TRLegalCaseForm.tsx`** — react-hook-form with fields: title (required), description, client_id (Autocomplete from clients list), legal_domain (Select, required), case_type (Select), complexity (Select), origination_channel (Select), client_budget (number), deadline (date picker), jurisdiction (text), priority (Select). Supports create and edit modes.

- **`TRLegalSpecialistForm.tsx`** — react-hook-form with fields: name (required), type (Select: individual/boutique_firm), email, phone, country, city, years_experience, hourly_rate. Sub-sections for adding multiple expertise (domain + proficiency pairs) and jurisdictions (country + region + is_primary).

- **`TRLegalClientForm.tsx`** — react-hook-form with fields: name (required), type (Select: company/individual), contact_email (email validation), contact_phone, country, industry.

All forms use MUI components with error display via helperText.

**UI Language:** English
**Validation:** Required fields enforced. Email format validated on client form. All components use TR prefix. All components properly typed with TypeScript interfaces.
```

---

### LD-015: Frontend Pages

**Title:** `[Legal Desk] Wave 6: All Pages (Dashboard, Cases, Specialists, Clients, Analytics)`

**Body:**
```markdown
## Context
**Project:** Faroo Legal Desk — Case Management & Specialist Assignment POC
**Overview:** Build all 7 Legal Desk pages: Dashboard (stats + charts), Cases List (filterable table), New Case (form), Case Detail (6-tab interface — the most complex page), Specialists (card grid), Clients (table), Analytics (charts + rankings). These pages compose the UI components and forms from LD-014 with data from the hooks in LD-013.

**Current Wave:** Wave 6 of 6 — Frontend UI
**Current Issue:** LD-015 (Issue 15 of 16)
**Parallel Execution:** YES — This issue runs in parallel with LD-014, LD-016.

**Dependencies:** LD-013 (React hooks), LD-014 (UI components and forms)
**What comes next:** LD-016 wires up routing and sidebar navigation.

## Request
Create all 7 Legal Desk page components.

### 1. Dashboard Page
Create `apps/Client/src/pages/legaldesk/LegalDeskDashboardPage.tsx`:
- Route: `/poc/legal-desk/dashboard`
- 4 stat cards: Active Cases, Pipeline Value, Specialists Active, Avg Duration
- Pie chart: Cases by Status (using Recharts)
- Bar chart: Cases by Legal Domain (using Recharts)
- Recent Cases table with status badges
- Top Specialists ranking with score display
- Uses `useLegaldeskDashboard` hook

### 2. Cases List Page
Create `apps/Client/src/pages/legaldesk/LegalDeskCasesPage.tsx`:
- Route: `/poc/legal-desk/cases`
- Filter controls: status (Select), legal_domain (Select), priority (Select), case_type (Select)
- Table columns: case_number, title, client name, domain (TRLegalDomainBadge), status (TRCaseStatusBadge), priority (TRCasePriorityBadge)
- "New Case" button → navigates to `/poc/legal-desk/cases/new`
- Row click → navigates to `/poc/legal-desk/cases/:id`
- Uses `useLegaldeskCases` hook

### 3. New Case Page
Create `apps/Client/src/pages/legaldesk/LegalDeskNewCasePage.tsx`:
- Route: `/poc/legal-desk/cases/new`
- Renders `TRLegalCaseForm`
- On submit: creates case via API, redirects to case detail page
- Loading state during submission, error display on failure

### 4. Case Detail Page (Most Complex)
Create `apps/Client/src/pages/legaldesk/LegalDeskCaseDetailPage.tsx`:
- Route: `/poc/legal-desk/cases/:id`
- 6 MUI Tabs:
  - **Overview**: Case info, client details, status badge, domain badge, priority badge, AI classification results
  - **Specialists**: Assigned specialists table + "Suggest Specialists" button → displays ranked candidates with match_score, match_reasons, and "Assign" action
  - **Deliverables**: TRDeliverableChecklist with add deliverable form
  - **Pricing**: TRPricingTimeline + action buttons (Propose, Counter, Accept, Reject)
  - **Messages**: Threaded message list with internal toggle checkbox, add message form
  - **Documents**: Document metadata list with add document form
- Status action bar: Shows only valid next-status transitions as buttons (using CASE_STATUS_TRANSITIONS logic)
- Uses `useLegaldeskCaseDetail` and `useLegaldeskPricing` hooks

### 5. Specialists Page
Create `apps/Client/src/pages/legaldesk/LegalDeskSpecialistsPage.tsx`:
- Route: `/poc/legal-desk/specialists`
- Card grid or table showing: name, type, domain expertise chips (TRLegalDomainBadge), score (TRSpecialistScoreDisplay), workload indicator (current/max)
- "Add Specialist" button → opens MUI Dialog with TRLegalSpecialistForm
- Uses `useLegaldeskSpecialists` hook

### 6. Clients Page
Create `apps/Client/src/pages/legaldesk/LegalDeskClientsPage.tsx`:
- Route: `/poc/legal-desk/clients`
- Table: name, type, email, country, industry
- "Add Client" button → opens MUI Dialog with TRLegalClientForm
- Uses `useLegaldeskClients` hook

### 7. Analytics Page
Create `apps/Client/src/pages/legaldesk/LegalDeskAnalyticsPage.tsx`:
- Route: `/poc/legal-desk/analytics`
- Revenue summary cards: Pipeline Value, Closed Revenue, Avg Margin
- Recharts: Cases over time (line), Revenue by Domain (bar), Specialist Utilization (bar)
- Specialist performance rankings table
- Uses `useLegaldeskDashboard` hook

**UI Language:** English
**Validation:** All pages handle loading and error states. Case detail tabs switch correctly. Status bar shows only valid transitions.
```

---

### LD-016: Route Registration + Sidebar Navigation

**Title:** `[Legal Desk] Wave 6: Routes & Sidebar Navigation`

**Body:**
```markdown
## Context
**Project:** Faroo Legal Desk — Case Management & Specialist Assignment POC
**Overview:** Register all Legal Desk routes in App.tsx and add Legal Desk navigation items to the sidebar. This is the final wiring step that makes the entire POC accessible through the application's navigation.

**Current Wave:** Wave 6 of 6 — Frontend UI
**Current Issue:** LD-016 (Issue 16 of 16)
**Parallel Execution:** YES — This issue runs in parallel with LD-014, LD-015.

**Dependencies:** LD-015 (page components must exist for import)
**What comes next:** This is the final issue. After completion, the Legal Desk POC is fully functional.

## Request
Wire up routing and sidebar navigation.

### 1. Route Registration
Update `apps/Client/src/App.tsx`:

Add routes under `/poc/legal-desk/*`, all wrapped in `ProtectedRoute`:
```typescript
import { lazy } from 'react';

const LegalDeskDashboardPage = lazy(() => import('@/pages/legaldesk/LegalDeskDashboardPage'));
const LegalDeskCasesPage = lazy(() => import('@/pages/legaldesk/LegalDeskCasesPage'));
const LegalDeskNewCasePage = lazy(() => import('@/pages/legaldesk/LegalDeskNewCasePage'));
const LegalDeskCaseDetailPage = lazy(() => import('@/pages/legaldesk/LegalDeskCaseDetailPage'));
const LegalDeskSpecialistsPage = lazy(() => import('@/pages/legaldesk/LegalDeskSpecialistsPage'));
const LegalDeskClientsPage = lazy(() => import('@/pages/legaldesk/LegalDeskClientsPage'));
const LegalDeskAnalyticsPage = lazy(() => import('@/pages/legaldesk/LegalDeskAnalyticsPage'));

// Inside routes:
<Route path="/poc/legal-desk/dashboard" element={<ProtectedRoute><LegalDeskDashboardPage /></ProtectedRoute>} />
<Route path="/poc/legal-desk/cases" element={<ProtectedRoute><LegalDeskCasesPage /></ProtectedRoute>} />
<Route path="/poc/legal-desk/cases/new" element={<ProtectedRoute><LegalDeskNewCasePage /></ProtectedRoute>} />
<Route path="/poc/legal-desk/cases/:id" element={<ProtectedRoute><LegalDeskCaseDetailPage /></ProtectedRoute>} />
<Route path="/poc/legal-desk/specialists" element={<ProtectedRoute><LegalDeskSpecialistsPage /></ProtectedRoute>} />
<Route path="/poc/legal-desk/clients" element={<ProtectedRoute><LegalDeskClientsPage /></ProtectedRoute>} />
<Route path="/poc/legal-desk/analytics" element={<ProtectedRoute><LegalDeskAnalyticsPage /></ProtectedRoute>} />
```

### 2. Sidebar Navigation
Update `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`:

Add a "Legal Desk" subsection under a POCs section with 5 navigation items:
```typescript
import GavelIcon from '@mui/icons-material/Gavel';
import BusinessCenterIcon from '@mui/icons-material/BusinessCenter';
import PersonSearchIcon from '@mui/icons-material/PersonSearch';
import GroupsIcon from '@mui/icons-material/Groups';
import AnalyticsIcon from '@mui/icons-material/Analytics';

// Legal Desk nav items:
{ text: 'Dashboard', icon: <GavelIcon />, path: '/poc/legal-desk/dashboard' },
{ text: 'Cases', icon: <BusinessCenterIcon />, path: '/poc/legal-desk/cases' },
{ text: 'Specialists', icon: <PersonSearchIcon />, path: '/poc/legal-desk/specialists' },
{ text: 'Clients', icon: <GroupsIcon />, path: '/poc/legal-desk/clients' },
{ text: 'Analytics', icon: <AnalyticsIcon />, path: '/poc/legal-desk/analytics' },
```

Active state should highlight the current page based on `location.pathname`.

**Validation:** All 7 routes registered and navigable. Routes protected by authentication. Lazy loading applied. 5 sidebar items with correct icons and navigation links. Active state highlights current page.
```

---
