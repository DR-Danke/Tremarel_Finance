# Meeting Processing CRM Pipeline - ADW Implementation Prompts

## Overview

This plan contains GitHub issue prompts for implementing the Meeting Processing CRM Pipeline using `adw_sdlc_iso.py`. Each prompt will trigger the `/feature` command which handles technical planning.

**Source:** Stakeholder discussion 2026-02-28 on CRM prospect tracking and automated meeting transcript processing pipeline.
**Requirements Doc:** `ai_docs/prds/prd-970a89f7-meeting-processing-crm-pipeline.md`

**Project Goal:** Add two major capabilities to the Finance Tracker application: (1) a CRM/Kanban board for tracking prospect and customer relationships through pipeline stages, and (2) an automated transcript processing pipeline that processes Fireflies meeting transcripts into structured content, updates prospect status, generates downloadable meeting summaries, and creates GitHub issues for SDLC workflows.

**Key Concepts:**
1. **Prospect** — A tracked company/customer relationship moving through pipeline stages (entity-scoped)
2. **Pipeline Stage** — Ordered stages a prospect moves through (New Lead → Initial Contact → Meeting Scheduled → Meeting Completed → Proposal Sent → Negotiation → Won → Lost)
3. **Meeting Record** — Processed meeting transcript linked to a prospect, with structured summary and downloadable HTML output
4. **Transcript Watcher** — File system watcher that detects new meeting transcripts and triggers the processing pipeline
5. **Stage Transition** — Tracked movement of a prospect between pipeline stages with timestamps

**Execution**: `uv run adw_sdlc_iso.py <issue-number>`

**Parallelization**: Issues within the same wave can run simultaneously in separate worktrees (up to 15 concurrent).

**Naming Conventions:**
- Component prefix: `TR` (TRProspectForm, TRKanbanBoard, TRProspectCard)
- Database table prefix: none (prospect, pipeline_stage, meeting_record, stage_transition_history)
- Route prefix: `/prospects` (frontend), `/api/prospects` and `/api/meetings` (backend)

**Terminology:**
- **Prospect** = A company/contact being tracked through the sales pipeline
- **Pipeline Stage** = A step in the prospect lifecycle (e.g., "New Lead", "Won")
- **Meeting Record** = Structured output from processing a raw meeting transcript
- **Stage Transition** = A recorded change in prospect stage with timestamp

---

## Wave 1: Foundation — Data Models & Backend API (Run in Parallel)

Build the backend data layer and API endpoints. REQ-001, REQ-002, and REQ-003 create the database models independently. REQ-004 and REQ-005 build the API layers. These five issues can run in parallel since they touch separate files: models, DTOs, routes, services, and repositories each scoped to their own concern.

### CRM-001: Prospect Data Model

**Title:** `[CRM Pipeline] Wave 1: Prospect Data Model`

**Body:**
```markdown
## Context
**Project:** Meeting Processing CRM Pipeline — CRM prospect tracking and automated meeting transcript processing for Finance Tracker
**Overview:** Create the database table, SQLAlchemy model, and Pydantic DTOs for the Prospect entity. Prospects are entity-scoped (multi-entity support) and represent companies/contacts being tracked through a sales pipeline.

**Current Wave:** Wave 1 of 3 — Foundation (Data Models & Backend API)
**Current Issue:** CRM-001 (Issue 1 of 14)
**Parallel Execution:** YES — This issue runs in parallel with CRM-002, CRM-003.

**Dependencies:** None
**What comes next:** CRM-004 builds CRUD API endpoints for prospects, and CRM-005 builds meeting record endpoints. Both depend on these models.

## Request
Create the prospect data model, database table, SQLAlchemy model, and Pydantic DTOs.

### 1. Database Table
Create SQL migration for the `prospect` table in `apps/Server/database/`:
```sql
CREATE TABLE IF NOT EXISTS prospect (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER NOT NULL REFERENCES entities(id),
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    stage VARCHAR(100) NOT NULL DEFAULT 'new_lead',
    notes TEXT,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_prospect_entity_id ON prospect(entity_id);
CREATE INDEX idx_prospect_stage ON prospect(stage);
```

### 2. SQLAlchemy Model
Create `apps/Server/src/models/prospect_model.py`:
```python
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.config.database import Base
from datetime import datetime

class ProspectModel(Base):
    __tablename__ = "prospect"

    id = Column(Integer, primary_key=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False)
    company_name = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=False)
    contact_email = Column(String(255))
    stage = Column(String(100), nullable=False, default="new_lead")
    notes = Column(Text)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    meeting_records = relationship("MeetingRecordModel", back_populates="prospect")
    stage_transitions = relationship("StageTransitionHistoryModel", back_populates="prospect")
```

### 3. Pydantic DTOs
Create `apps/Server/src/interface/prospect_dto.py`:
```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class ProspectCreateDTO(BaseModel):
    entity_id: int
    company_name: str = Field(..., max_length=255)
    contact_name: str = Field(..., max_length=255)
    contact_email: Optional[str] = Field(None, max_length=255)
    stage: str = Field(default="new_lead", max_length=100)
    notes: Optional[str] = None

class ProspectUpdateDTO(BaseModel):
    company_name: Optional[str] = Field(None, max_length=255)
    contact_name: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None

class ProspectResponseDTO(BaseModel):
    id: int
    entity_id: int
    company_name: str
    contact_name: str
    contact_email: Optional[str]
    stage: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProspectStageUpdateDTO(BaseModel):
    stage: str = Field(..., max_length=100)
```

**Validation:** company_name and contact_name are required. contact_email is optional. stage defaults to "new_lead".
```

---

### CRM-002: Pipeline Stage Configuration

**Title:** `[CRM Pipeline] Wave 1: Pipeline Stage Configuration`

**Body:**
```markdown
## Context
**Project:** Meeting Processing CRM Pipeline — CRM prospect tracking and automated meeting transcript processing for Finance Tracker
**Overview:** Define the pipeline stages for prospect tracking and create a stage transition history model. Stages are ordered for Kanban column display. Stage transitions are recorded with timestamps to provide an audit trail.

**Current Wave:** Wave 1 of 3 — Foundation (Data Models & Backend API)
**Current Issue:** CRM-002 (Issue 2 of 14)
**Parallel Execution:** YES — This issue runs in parallel with CRM-001, CRM-003.

**Dependencies:** None
**What comes next:** CRM-004 uses stages for the PATCH endpoint that updates prospect stage and records transitions.

## Request
Create pipeline stage configuration and stage transition history tracking.

### 1. Pipeline Stage Table
Create SQL migration in `apps/Server/database/`:
```sql
CREATE TABLE IF NOT EXISTS pipeline_stage (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    ordinal INTEGER NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO pipeline_stage (name, slug, ordinal, description) VALUES
    ('New Lead', 'new_lead', 1, 'Newly identified prospect'),
    ('Initial Contact', 'initial_contact', 2, 'First outreach made'),
    ('Meeting Scheduled', 'meeting_scheduled', 3, 'Meeting has been set up'),
    ('Meeting Completed', 'meeting_completed', 4, 'Meeting has taken place'),
    ('Proposal Sent', 'proposal_sent', 5, 'Proposal or offer sent to prospect'),
    ('Negotiation', 'negotiation', 6, 'Active negotiation in progress'),
    ('Won', 'won', 7, 'Deal closed successfully'),
    ('Lost', 'lost', 8, 'Prospect declined or went cold');
```

### 2. Stage Transition History Table
```sql
CREATE TABLE IF NOT EXISTS stage_transition_history (
    id SERIAL PRIMARY KEY,
    prospect_id INTEGER NOT NULL REFERENCES prospect(id),
    from_stage VARCHAR(100),
    to_stage VARCHAR(100) NOT NULL,
    transitioned_at TIMESTAMP DEFAULT NOW(),
    transitioned_by INTEGER REFERENCES users(id)
);

CREATE INDEX idx_stage_transition_prospect ON stage_transition_history(prospect_id);
```

### 3. SQLAlchemy Models
Create `apps/Server/src/models/pipeline_stage_model.py`:
```python
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from src.config.database import Base
from datetime import datetime

class PipelineStageModel(Base):
    __tablename__ = "pipeline_stage"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False, unique=True)
    ordinal = Column(Integer, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

Create `apps/Server/src/models/stage_transition_model.py`:
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.config.database import Base
from datetime import datetime

class StageTransitionHistoryModel(Base):
    __tablename__ = "stage_transition_history"

    id = Column(Integer, primary_key=True, index=True)
    prospect_id = Column(Integer, ForeignKey("prospect.id"), nullable=False)
    from_stage = Column(String(100))
    to_stage = Column(String(100), nullable=False)
    transitioned_at = Column(DateTime, default=datetime.utcnow)
    transitioned_by = Column(Integer, ForeignKey("users.id"))

    prospect = relationship("ProspectModel", back_populates="stage_transitions")
```

### 4. Pydantic DTOs
Add to `apps/Server/src/interface/prospect_dto.py` or create `apps/Server/src/interface/pipeline_stage_dto.py`:
```python
class PipelineStageResponseDTO(BaseModel):
    id: int
    name: str
    slug: str
    ordinal: int
    description: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

class StageTransitionResponseDTO(BaseModel):
    id: int
    prospect_id: int
    from_stage: Optional[str]
    to_stage: str
    transitioned_at: datetime
    transitioned_by: Optional[int]

    class Config:
        from_attributes = True
```

### 5. Stage List Endpoint
Create a simple endpoint in `apps/Server/src/adapter/rest/prospect_routes.py`:
```python
@router.get("/api/pipeline-stages")
async def get_pipeline_stages(current_user: dict = Depends(get_current_user)):
    """Return all active pipeline stages ordered by ordinal"""
    stages = await pipeline_stage_repository.get_all_active()
    return stages
```

**Validation:** Stages have unique slugs and sequential ordinal values. Default seed data includes 8 stages.
```

---

### CRM-003: Meeting Record Data Model

**Title:** `[CRM Pipeline] Wave 1: Meeting Record Data Model`

**Body:**
```markdown
## Context
**Project:** Meeting Processing CRM Pipeline — CRM prospect tracking and automated meeting transcript processing for Finance Tracker
**Overview:** Create the data model for storing processed meeting records linked to prospects. Each meeting record stores the original transcript reference, structured summary, action items, participants, and a downloadable formatted HTML output. Multiple meetings can be linked to a single prospect.

**Current Wave:** Wave 1 of 3 — Foundation (Data Models & Backend API)
**Current Issue:** CRM-003 (Issue 3 of 14)
**Parallel Execution:** YES — This issue runs in parallel with CRM-001, CRM-002.

**Dependencies:** None
**What comes next:** CRM-005 builds API endpoints for meeting records. Wave 3 transcript pipeline creates meeting records via the API.

## Request
Create the meeting record data model, database table, SQLAlchemy model, and Pydantic DTOs.

### 1. Database Table
Create SQL migration in `apps/Server/database/`:
```sql
CREATE TABLE IF NOT EXISTS meeting_record (
    id SERIAL PRIMARY KEY,
    prospect_id INTEGER NOT NULL REFERENCES prospect(id),
    meeting_date TIMESTAMP,
    participants TEXT,
    summary TEXT,
    action_items TEXT,
    formatted_output_html TEXT,
    transcript_filename VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_meeting_record_prospect ON meeting_record(prospect_id);
```

### 2. SQLAlchemy Model
Create `apps/Server/src/models/meeting_record_model.py`:
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.config.database import Base
from datetime import datetime

class MeetingRecordModel(Base):
    __tablename__ = "meeting_record"

    id = Column(Integer, primary_key=True, index=True)
    prospect_id = Column(Integer, ForeignKey("prospect.id"), nullable=False)
    meeting_date = Column(DateTime)
    participants = Column(Text)
    summary = Column(Text)
    action_items = Column(Text)
    formatted_output_html = Column(Text)
    transcript_filename = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    prospect = relationship("ProspectModel", back_populates="meeting_records")
```

### 3. Pydantic DTOs
Create `apps/Server/src/interface/meeting_record_dto.py`:
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MeetingRecordCreateDTO(BaseModel):
    prospect_id: int
    meeting_date: Optional[datetime] = None
    participants: Optional[str] = None
    summary: Optional[str] = None
    action_items: Optional[str] = None
    formatted_output_html: Optional[str] = None
    transcript_filename: Optional[str] = None

class MeetingRecordResponseDTO(BaseModel):
    id: int
    prospect_id: int
    meeting_date: Optional[datetime]
    participants: Optional[str]
    summary: Optional[str]
    action_items: Optional[str]
    transcript_filename: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class MeetingRecordDetailDTO(MeetingRecordResponseDTO):
    formatted_output_html: Optional[str]
```

**Validation:** prospect_id is required. All other fields are optional as the pipeline populates them progressively.
```

---

### CRM-004: Prospect CRUD API Endpoints

**Title:** `[CRM Pipeline] Wave 1: Prospect CRUD API Endpoints`

**Body:**
```markdown
## Context
**Project:** Meeting Processing CRM Pipeline — CRM prospect tracking and automated meeting transcript processing for Finance Tracker
**Overview:** Create RESTful API endpoints for prospect management following Clean Architecture: routes in adapter/rest/, business logic in core/services/, data access in repository/. All endpoints require JWT authentication and filter by entity. Includes stage update endpoint with transition tracking.

**Current Wave:** Wave 1 of 3 — Foundation (Data Models & Backend API)
**Current Issue:** CRM-004 (Issue 4 of 14)
**Parallel Execution:** YES — This issue runs in parallel with CRM-001, CRM-002, CRM-003, CRM-005 (all create independent files).

**Dependencies:** CRM-001 (ProspectModel), CRM-002 (StageTransitionHistoryModel)
**What comes next:** Wave 2 frontend consumes these endpoints via prospectService. Wave 3 pipeline uses POST and PATCH endpoints to create/update prospects.

## Request
Create the full prospect API stack: routes, service, repository. Register the router in main.py.

### 1. Prospect Repository
Create `apps/Server/src/repository/prospect_repository.py`:
```python
from src.config.database import SessionLocal
from src.models.prospect_model import ProspectModel
from typing import Optional

class ProspectRepository:
    def get_all_by_entity(self, entity_id: int, skip: int = 0, limit: int = 100) -> list:
        """Return prospects for an entity, excluding soft-deleted"""
        pass

    def get_by_id(self, prospect_id: int) -> Optional[ProspectModel]:
        """Return prospect by ID with meeting records"""
        pass

    def create(self, data: dict) -> ProspectModel:
        """Create a new prospect"""
        pass

    def update(self, prospect_id: int, data: dict) -> Optional[ProspectModel]:
        """Update prospect fields"""
        pass

    def update_stage(self, prospect_id: int, new_stage: str, user_id: int) -> Optional[ProspectModel]:
        """Update prospect stage and record transition in stage_transition_history"""
        pass

    def soft_delete(self, prospect_id: int) -> bool:
        """Soft-delete a prospect"""
        pass

    def search_by_company_or_email(self, entity_id: int, company_name: str = None, contact_email: str = None) -> Optional[ProspectModel]:
        """Search for existing prospect by company name or contact email"""
        pass
```

### 2. Prospect Service
Create `apps/Server/src/core/services/prospect_service.py`:
```python
class ProspectService:
    def __init__(self, prospect_repository: ProspectRepository):
        self.prospect_repository = prospect_repository

    def get_all(self, entity_id: int, skip: int = 0, limit: int = 100) -> list:
        print(f"INFO [ProspectService]: Fetching prospects for entity {entity_id}")
        return self.prospect_repository.get_all_by_entity(entity_id, skip, limit)

    def get_by_id(self, prospect_id: int) -> dict:
        print(f"INFO [ProspectService]: Fetching prospect {prospect_id}")
        prospect = self.prospect_repository.get_by_id(prospect_id)
        if not prospect:
            raise ValueError(f"Prospect {prospect_id} not found")
        return prospect

    def create(self, data: dict) -> dict:
        print(f"INFO [ProspectService]: Creating prospect for entity {data.get('entity_id')}")
        result = self.prospect_repository.create(data)
        print(f"INFO [ProspectService]: Prospect created: {result.id}")
        return result

    def update(self, prospect_id: int, data: dict) -> dict:
        print(f"INFO [ProspectService]: Updating prospect {prospect_id}")
        return self.prospect_repository.update(prospect_id, data)

    def update_stage(self, prospect_id: int, new_stage: str, user_id: int) -> dict:
        print(f"INFO [ProspectService]: Updating stage for prospect {prospect_id} to {new_stage}")
        return self.prospect_repository.update_stage(prospect_id, new_stage, user_id)

    def delete(self, prospect_id: int) -> bool:
        print(f"INFO [ProspectService]: Soft-deleting prospect {prospect_id}")
        return self.prospect_repository.soft_delete(prospect_id)
```

### 3. Prospect Routes
Create `apps/Server/src/adapter/rest/prospect_routes.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from src.adapter.rest.dependencies import get_current_user
from src.interface.prospect_dto import (
    ProspectCreateDTO, ProspectUpdateDTO, ProspectResponseDTO, ProspectStageUpdateDTO
)

router = APIRouter(prefix="/api/prospects", tags=["Prospects"])

@router.get("/")
async def get_prospects(
    entity_id: int = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: dict = Depends(get_current_user)
):
    """GET /api/prospects?entity_id={id} - paginated list"""
    pass

@router.post("/")
async def create_prospect(
    data: ProspectCreateDTO,
    current_user: dict = Depends(get_current_user)
):
    """POST /api/prospects - create new prospect"""
    pass

@router.get("/{prospect_id}")
async def get_prospect(
    prospect_id: int,
    current_user: dict = Depends(get_current_user)
):
    """GET /api/prospects/{id} - detail with meeting history"""
    pass

@router.put("/{prospect_id}")
async def update_prospect(
    prospect_id: int,
    data: ProspectUpdateDTO,
    current_user: dict = Depends(get_current_user)
):
    """PUT /api/prospects/{id} - update prospect info"""
    pass

@router.patch("/{prospect_id}/stage")
async def update_prospect_stage(
    prospect_id: int,
    data: ProspectStageUpdateDTO,
    current_user: dict = Depends(get_current_user)
):
    """PATCH /api/prospects/{id}/stage - update stage and record transition"""
    pass

@router.delete("/{prospect_id}")
async def delete_prospect(
    prospect_id: int,
    current_user: dict = Depends(get_current_user)
):
    """DELETE /api/prospects/{id} - soft delete"""
    pass
```

### 4. Register Router
Add to `apps/Server/main.py`:
```python
from src.adapter.rest.prospect_routes import router as prospect_router
app.include_router(prospect_router)
```

**Validation:** All endpoints require JWT authentication via `get_current_user`. Entity-scoped filtering on GET list. Stage updates record transitions with timestamps.
```

---

### CRM-005: Meeting Record API Endpoints

**Title:** `[CRM Pipeline] Wave 1: Meeting Record API Endpoints`

**Body:**
```markdown
## Context
**Project:** Meeting Processing CRM Pipeline — CRM prospect tracking and automated meeting transcript processing for Finance Tracker
**Overview:** Create API endpoints for meeting records associated with prospects. Includes listing meetings for a prospect, retrieving meeting detail, downloading formatted HTML output, and creating new meeting records (used by the transcript processing pipeline).

**Current Wave:** Wave 1 of 3 — Foundation (Data Models & Backend API)
**Current Issue:** CRM-005 (Issue 5 of 14)
**Parallel Execution:** YES — This issue runs in parallel with CRM-001, CRM-002, CRM-003, CRM-004 (all create independent files).

**Dependencies:** CRM-003 (MeetingRecordModel), CRM-004 (prospect routes registered in main.py)
**What comes next:** Wave 2 frontend displays meeting history in prospect detail view. Wave 3 pipeline creates meeting records via POST endpoint.

## Request
Create the meeting record API stack: routes, service, repository.

### 1. Meeting Record Repository
Create `apps/Server/src/repository/meeting_repository.py`:
```python
from src.config.database import SessionLocal
from src.models.meeting_record_model import MeetingRecordModel

class MeetingRepository:
    def get_by_prospect(self, prospect_id: int) -> list:
        """Return all meeting records for a prospect, ordered by meeting_date DESC"""
        pass

    def get_by_id(self, meeting_id: int) -> MeetingRecordModel:
        """Return meeting record by ID including HTML output"""
        pass

    def create(self, data: dict) -> MeetingRecordModel:
        """Create a new meeting record"""
        pass
```

### 2. Meeting Service
Create `apps/Server/src/core/services/meeting_service.py`:
```python
class MeetingService:
    def __init__(self, meeting_repository: MeetingRepository):
        self.meeting_repository = meeting_repository

    def get_meetings_for_prospect(self, prospect_id: int) -> list:
        print(f"INFO [MeetingService]: Fetching meetings for prospect {prospect_id}")
        return self.meeting_repository.get_by_prospect(prospect_id)

    def get_meeting_detail(self, meeting_id: int) -> dict:
        print(f"INFO [MeetingService]: Fetching meeting detail {meeting_id}")
        return self.meeting_repository.get_by_id(meeting_id)

    def create_meeting(self, data: dict) -> dict:
        print(f"INFO [MeetingService]: Creating meeting record for prospect {data.get('prospect_id')}")
        result = self.meeting_repository.create(data)
        print(f"INFO [MeetingService]: Meeting record created: {result.id}")
        return result
```

### 3. Meeting Routes
Create `apps/Server/src/adapter/rest/meeting_routes.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from src.adapter.rest.dependencies import get_current_user
from src.interface.meeting_record_dto import MeetingRecordCreateDTO, MeetingRecordResponseDTO

router = APIRouter(tags=["Meetings"])

@router.get("/api/prospects/{prospect_id}/meetings")
async def get_prospect_meetings(
    prospect_id: int,
    current_user: dict = Depends(get_current_user)
):
    """GET /api/prospects/{id}/meetings - all meetings for a prospect"""
    pass

@router.get("/api/meetings/{meeting_id}")
async def get_meeting_detail(
    meeting_id: int,
    current_user: dict = Depends(get_current_user)
):
    """GET /api/meetings/{id} - meeting detail with structured summary"""
    pass

@router.get("/api/meetings/{meeting_id}/download")
async def download_meeting_html(
    meeting_id: int,
    current_user: dict = Depends(get_current_user)
):
    """GET /api/meetings/{id}/download - formatted HTML as downloadable file"""
    meeting = meeting_service.get_meeting_detail(meeting_id)
    if not meeting or not meeting.formatted_output_html:
        raise HTTPException(status_code=404, detail="Meeting HTML not available")
    return HTMLResponse(
        content=meeting.formatted_output_html,
        headers={"Content-Disposition": f"attachment; filename=meeting_{meeting_id}.html"}
    )

@router.post("/api/meetings")
async def create_meeting(
    data: MeetingRecordCreateDTO,
    current_user: dict = Depends(get_current_user)
):
    """POST /api/meetings - create meeting record (used by pipeline)"""
    pass
```

### 4. Register Router
Add to `apps/Server/main.py`:
```python
from src.adapter.rest.meeting_routes import router as meeting_router
app.include_router(meeting_router)
```

**Validation:** All endpoints require JWT authentication. Download endpoint returns HTML with Content-Disposition header for browser download.
```

---

## Wave 2: CRM Kanban Board Frontend (Run in Parallel)

Build the frontend Kanban board interface. REQ-010 (service/hook/types), REQ-009 (form), and REQ-006 (page) can run in parallel as they create separate files. REQ-007 (drag-and-drop) and REQ-008 (detail view) depend on the page existing but can also run in parallel with each other.

### CRM-006: Prospect Service, Hook & Types

**Title:** `[CRM Pipeline] Wave 2: Prospect Service, Hook & TypeScript Types`

**Body:**
```markdown
## Context
**Project:** Meeting Processing CRM Pipeline — CRM prospect tracking and automated meeting transcript processing for Finance Tracker
**Overview:** Create the frontend service layer, custom React hook, and TypeScript interfaces for managing prospect and meeting data. Follows existing patterns: axios API client with JWT interceptor, entity-scoped queries via useEntity(), and typed service methods.

**Current Wave:** Wave 2 of 3 — CRM Kanban Board Frontend
**Current Issue:** CRM-006 (Issue 6 of 14)
**Parallel Execution:** YES — This issue runs in parallel with CRM-007, CRM-008.

**Dependencies:** CRM-004, CRM-005 (backend API endpoints must exist)
**What comes next:** CRM-008 (Kanban Board Page), CRM-009 (Drag-and-Drop), and CRM-010 (Detail View) all consume this service and hook.

## Request
Create the prospect frontend data layer: TypeScript types, service, and custom hook.

### 1. TypeScript Interfaces
Create `apps/Client/src/types/prospect.ts`:
```typescript
export interface Prospect {
  id: number;
  entity_id: number;
  company_name: string;
  contact_name: string;
  contact_email?: string;
  stage: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface ProspectCreateData {
  entity_id: number;
  company_name: string;
  contact_name: string;
  contact_email?: string;
  stage?: string;
  notes?: string;
}

export interface ProspectUpdateData {
  company_name?: string;
  contact_name?: string;
  contact_email?: string;
  notes?: string;
}

export interface PipelineStage {
  id: number;
  name: string;
  slug: string;
  ordinal: number;
  description?: string;
  is_active: boolean;
}

export interface MeetingRecord {
  id: number;
  prospect_id: number;
  meeting_date?: string;
  participants?: string;
  summary?: string;
  action_items?: string;
  transcript_filename?: string;
  created_at: string;
}

export interface StageTransition {
  id: number;
  prospect_id: number;
  from_stage?: string;
  to_stage: string;
  transitioned_at: string;
  transitioned_by?: number;
}
```

### 2. Prospect Service
Create `apps/Client/src/services/prospectService.ts`:
```typescript
import apiClient from '@/api/clients/apiClient';
import { Prospect, ProspectCreateData, ProspectUpdateData, PipelineStage, MeetingRecord } from '@/types/prospect';

const prospectService = {
  getAll: async (entityId: number): Promise<Prospect[]> => {
    console.log(`INFO [prospectService]: Fetching prospects for entity ${entityId}`);
    const response = await apiClient.get(`/prospects?entity_id=${entityId}`);
    return response.data;
  },

  getById: async (prospectId: number): Promise<Prospect> => {
    console.log(`INFO [prospectService]: Fetching prospect ${prospectId}`);
    const response = await apiClient.get(`/prospects/${prospectId}`);
    return response.data;
  },

  create: async (data: ProspectCreateData): Promise<Prospect> => {
    console.log(`INFO [prospectService]: Creating prospect for entity ${data.entity_id}`);
    const response = await apiClient.post('/prospects', data);
    return response.data;
  },

  update: async (prospectId: number, data: ProspectUpdateData): Promise<Prospect> => {
    console.log(`INFO [prospectService]: Updating prospect ${prospectId}`);
    const response = await apiClient.put(`/prospects/${prospectId}`, data);
    return response.data;
  },

  updateStage: async (prospectId: number, stage: string): Promise<Prospect> => {
    console.log(`INFO [prospectService]: Updating stage for prospect ${prospectId} to ${stage}`);
    const response = await apiClient.patch(`/prospects/${prospectId}/stage`, { stage });
    return response.data;
  },

  delete: async (prospectId: number): Promise<void> => {
    console.log(`INFO [prospectService]: Deleting prospect ${prospectId}`);
    await apiClient.delete(`/prospects/${prospectId}`);
  },

  getStages: async (): Promise<PipelineStage[]> => {
    console.log(`INFO [prospectService]: Fetching pipeline stages`);
    const response = await apiClient.get('/pipeline-stages');
    return response.data;
  },

  getMeetings: async (prospectId: number): Promise<MeetingRecord[]> => {
    console.log(`INFO [prospectService]: Fetching meetings for prospect ${prospectId}`);
    const response = await apiClient.get(`/prospects/${prospectId}/meetings`);
    return response.data;
  },

  downloadMeetingHtml: async (meetingId: number): Promise<void> => {
    console.log(`INFO [prospectService]: Downloading meeting HTML ${meetingId}`);
    const response = await apiClient.get(`/meetings/${meetingId}/download`, { responseType: 'blob' });
    // Trigger browser download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `meeting_${meetingId}.html`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },
};

export default prospectService;
```

### 3. Custom Hook
Create `apps/Client/src/hooks/useProspects.ts`:
```typescript
import { useState, useEffect, useCallback } from 'react';
import { useEntity } from '@/contexts/EntityContext';
import prospectService from '@/services/prospectService';
import { Prospect, PipelineStage } from '@/types/prospect';

export const useProspects = () => {
  const { currentEntity } = useEntity();
  const [prospects, setProspects] = useState<Prospect[]>([]);
  const [stages, setStages] = useState<PipelineStage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProspects = useCallback(async () => {
    if (!currentEntity?.id) return;
    setLoading(true);
    setError(null);
    try {
      const [prospectsData, stagesData] = await Promise.all([
        prospectService.getAll(currentEntity.id),
        prospectService.getStages(),
      ]);
      setProspects(prospectsData);
      setStages(stagesData);
    } catch (err) {
      console.error('ERROR [useProspects]: Failed to fetch prospects:', err);
      setError('Failed to load prospects');
    } finally {
      setLoading(false);
    }
  }, [currentEntity?.id]);

  useEffect(() => {
    fetchProspects();
  }, [fetchProspects]);

  return { prospects, stages, loading, error, refetch: fetchProspects };
};
```

**Validation:** All API calls use the JWT-authenticated axios client. Entity scoping via useEntity(). Loading and error states managed in hook.
```

---

### CRM-007: Prospect Creation Form

**Title:** `[CRM Pipeline] Wave 2: Prospect Creation Form`

**Body:**
```markdown
## Context
**Project:** Meeting Processing CRM Pipeline — CRM prospect tracking and automated meeting transcript processing for Finance Tracker
**Overview:** Create the TRProspectForm component for manually adding new prospects. Uses react-hook-form with MUI components following existing form patterns. Allows setting company name, contact name, contact email, initial stage, and notes.

**Current Wave:** Wave 2 of 3 — CRM Kanban Board Frontend
**Current Issue:** CRM-007 (Issue 7 of 14)
**Parallel Execution:** YES — This issue runs in parallel with CRM-006, CRM-008.

**Dependencies:** CRM-006 (TypeScript types for Prospect and PipelineStage)
**What comes next:** CRM-008 (Kanban Board Page) integrates this form in a dialog for creating new prospects.

## Request
Create the TRProspectForm component with react-hook-form and MUI.

### 1. Form Component
Create `apps/Client/src/components/forms/TRProspectForm.tsx`:
```typescript
import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import {
  TextField, Button, MenuItem, Select, FormControl,
  InputLabel, FormHelperText, Box, Stack
} from '@mui/material';
import { ProspectCreateData, PipelineStage } from '@/types/prospect';

interface TRProspectFormProps {
  stages: PipelineStage[];
  onSubmit: (data: ProspectCreateData) => Promise<void>;
  onCancel: () => void;
  loading?: boolean;
}

export const TRProspectForm: React.FC<TRProspectFormProps> = ({
  stages,
  onSubmit,
  onCancel,
  loading = false,
}) => {
  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<ProspectCreateData>({
    defaultValues: {
      stage: 'new_lead',
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Stack spacing={2}>
        <TextField
          {...register('company_name', { required: 'Company name is required' })}
          label="Company Name"
          fullWidth
          error={!!errors.company_name}
          helperText={errors.company_name?.message}
        />
        <TextField
          {...register('contact_name', { required: 'Contact name is required' })}
          label="Contact Name"
          fullWidth
          error={!!errors.contact_name}
          helperText={errors.contact_name?.message}
        />
        <TextField
          {...register('contact_email', {
            pattern: {
              value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
              message: 'Invalid email address',
            },
          })}
          label="Contact Email"
          type="email"
          fullWidth
          error={!!errors.contact_email}
          helperText={errors.contact_email?.message}
        />
        <Controller
          name="stage"
          control={control}
          render={({ field }) => (
            <FormControl fullWidth>
              <InputLabel>Initial Stage</InputLabel>
              <Select {...field} label="Initial Stage">
                {stages.map((stage) => (
                  <MenuItem key={stage.slug} value={stage.slug}>
                    {stage.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          )}
        />
        <TextField
          {...register('notes')}
          label="Notes"
          multiline
          rows={3}
          fullWidth
        />
        <Box display="flex" gap={2} justifyContent="flex-end">
          <Button onClick={onCancel} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? 'Creating...' : 'Create Prospect'}
          </Button>
        </Box>
      </Stack>
    </form>
  );
};
```

**UI Language:** English
**Validation:** company_name and contact_name are required. contact_email validates email format. Stage defaults to "new_lead".
```

---

### CRM-008: Prospect Kanban Board Page

**Title:** `[CRM Pipeline] Wave 2: Prospect Kanban Board Page`

**Body:**
```markdown
## Context
**Project:** Meeting Processing CRM Pipeline — CRM prospect tracking and automated meeting transcript processing for Finance Tracker
**Overview:** Create the ProspectsPage with a Kanban board layout. Each column represents a pipeline stage. Prospect cards appear in their respective stage columns. The page uses TRMainLayout, useEntity() for entity scoping, and is accessible from the sidebar navigation. Includes a button to open the TRProspectForm in a dialog.

**Current Wave:** Wave 2 of 3 — CRM Kanban Board Frontend
**Current Issue:** CRM-008 (Issue 8 of 14)
**Parallel Execution:** YES — This issue runs in parallel with CRM-006, CRM-007.

**Dependencies:** CRM-006 (useProspects hook, prospectService, types), CRM-007 (TRProspectForm)
**What comes next:** CRM-009 adds drag-and-drop to the Kanban board. CRM-010 adds prospect detail drawer.

## Request
Create the Kanban board page, Kanban board component, prospect card component, and add route + sidebar navigation.

### 1. Prospect Card Component
Create `apps/Client/src/components/ui/TRProspectCard.tsx`:
```typescript
import React from 'react';
import { Card, CardContent, Typography, Chip, Box } from '@mui/material';
import { Prospect } from '@/types/prospect';

interface TRProspectCardProps {
  prospect: Prospect;
  onClick: (prospect: Prospect) => void;
}

export const TRProspectCard: React.FC<TRProspectCardProps> = ({ prospect, onClick }) => {
  return (
    <Card
      sx={{ mb: 1, cursor: 'pointer', '&:hover': { boxShadow: 3 } }}
      onClick={() => onClick(prospect)}
    >
      <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
        <Typography variant="subtitle2" noWrap>{prospect.company_name}</Typography>
        <Typography variant="body2" color="text.secondary" noWrap>
          {prospect.contact_name}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {new Date(prospect.updated_at).toLocaleDateString()}
        </Typography>
      </CardContent>
    </Card>
  );
};
```

### 2. Kanban Board Component
Create `apps/Client/src/components/ui/TRKanbanBoard.tsx`:
```typescript
import React from 'react';
import { Box, Paper, Typography, Stack } from '@mui/material';
import { Prospect, PipelineStage } from '@/types/prospect';
import { TRProspectCard } from './TRProspectCard';

interface TRKanbanBoardProps {
  stages: PipelineStage[];
  prospects: Prospect[];
  onCardClick: (prospect: Prospect) => void;
}

export const TRKanbanBoard: React.FC<TRKanbanBoardProps> = ({
  stages,
  prospects,
  onCardClick,
}) => {
  const getProspectsForStage = (stageSlug: string) =>
    prospects.filter((p) => p.stage === stageSlug);

  return (
    <Box sx={{ display: 'flex', gap: 2, overflowX: 'auto', pb: 2, minHeight: '60vh' }}>
      {stages
        .sort((a, b) => a.ordinal - b.ordinal)
        .map((stage) => (
          <Paper
            key={stage.slug}
            sx={{ minWidth: 280, maxWidth: 320, p: 2, bgcolor: 'grey.50', flexShrink: 0 }}
          >
            <Typography variant="subtitle1" fontWeight="bold" mb={1}>
              {stage.name} ({getProspectsForStage(stage.slug).length})
            </Typography>
            <Stack spacing={1}>
              {getProspectsForStage(stage.slug).map((prospect) => (
                <TRProspectCard
                  key={prospect.id}
                  prospect={prospect}
                  onClick={onCardClick}
                />
              ))}
            </Stack>
          </Paper>
        ))}
    </Box>
  );
};
```

### 3. Prospects Page
Create `apps/Client/src/pages/ProspectsPage.tsx`:
- Import `useProspects` hook, `TRKanbanBoard`, `TRProspectForm`
- Display page title "Prospects Pipeline"
- Add "New Prospect" button that opens TRProspectForm in a MUI Dialog
- Render TRKanbanBoard with prospects and stages from hook
- Handle card click (placeholder for detail view from CRM-010)
- Show loading spinner while data loads
- Show error alert if fetch fails

### 4. Route Registration
Add to `apps/Client/src/App.tsx`:
```typescript
import ProspectsPage from '@/pages/ProspectsPage';

// Inside Routes:
<Route path="/prospects" element={
  <ProtectedRoute>
    <TRMainLayout>
      <ProspectsPage />
    </TRMainLayout>
  </ProtectedRoute>
} />
```

### 5. Sidebar Navigation
Update `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`:
- Add a "Prospects" navigation item with an appropriate MUI icon (e.g., `PeopleOutline` or `BusinessOutlined`)
- Link to `/prospects` route
- Place it logically in the sidebar (after Dashboard or Transactions)

**UI Language:** English
**Validation:** Page requires authentication (ProtectedRoute). Prospects filtered by current entity.
```

---

### CRM-009: Prospect Card Drag-and-Drop

**Title:** `[CRM Pipeline] Wave 2: Prospect Card Drag-and-Drop`

**Body:**
```markdown
## Context
**Project:** Meeting Processing CRM Pipeline — CRM prospect tracking and automated meeting transcript processing for Finance Tracker
**Overview:** Implement drag-and-drop on the Kanban board so prospects can be moved between pipeline stages by dragging cards. Stage changes persist to the backend via PATCH /api/prospects/{id}/stage. Uses optimistic updates with rollback on failure.

**Current Wave:** Wave 2 of 3 — CRM Kanban Board Frontend
**Current Issue:** CRM-009 (Issue 9 of 14)
**Parallel Execution:** NO — Depends on CRM-008 (Kanban board must exist to add DnD).

**Dependencies:** CRM-008 (TRKanbanBoard component)
**What comes next:** Wave 3 transcript pipeline. This completes the interactive Kanban experience.

## Request
Add drag-and-drop to the TRKanbanBoard component using @hello-pangea/dnd.

### 1. Install Dependency
Add `@hello-pangea/dnd` to `apps/Client/package.json`:
```bash
cd apps/Client && npm install @hello-pangea/dnd
```

### 2. Update TRKanbanBoard
Modify `apps/Client/src/components/ui/TRKanbanBoard.tsx`:
- Wrap the board in `<DragDropContext onDragEnd={handleDragEnd}>`
- Wrap each stage column in `<Droppable droppableId={stage.slug}>`
- Wrap each prospect card in `<Draggable draggableId={String(prospect.id)}>`
- `handleDragEnd` callback:
  1. Check if destination exists and is different from source
  2. Optimistically update local prospect state (move card to new column)
  3. Call `prospectService.updateStage(prospectId, newStageSlug)`
  4. On failure: revert card to original column, show error snackbar
  5. On success: refetch prospects to sync with server

### 3. Update TRProspectCard
Modify `apps/Client/src/components/ui/TRProspectCard.tsx`:
- Accept `provided` and `snapshot` props from Draggable render function
- Apply `provided.draggableProps`, `provided.dragHandleProps`, and `ref` to the Card
- Add visual feedback when dragging (e.g., elevated shadow, slight opacity change)

### 4. Error Handling
- Display a Snackbar/Alert on failed stage update
- Log errors: `console.error('ERROR [TRKanbanBoard]: Stage update failed:', error)`

**Validation:** Optimistic update with rollback. Error notification on API failure. Cards visually indicate drag state.
```

---

### CRM-010: Prospect Detail View

**Title:** `[CRM Pipeline] Wave 2: Prospect Detail View with Meeting History`

**Body:**
```markdown
## Context
**Project:** Meeting Processing CRM Pipeline — CRM prospect tracking and automated meeting transcript processing for Finance Tracker
**Overview:** When clicking a prospect card, display a detail drawer showing: prospect information, stage transition history timeline, and chronological list of meetings with structured summaries. Each meeting entry has a download button for the formatted HTML output.

**Current Wave:** Wave 2 of 3 — CRM Kanban Board Frontend
**Current Issue:** CRM-010 (Issue 10 of 14)
**Parallel Execution:** NO — Depends on CRM-008 (card click handler exists in Kanban board).

**Dependencies:** CRM-005 (meeting record API), CRM-006 (prospectService.getMeetings), CRM-008 (TRKanbanBoard card click)
**What comes next:** Wave 3 transcript pipeline creates meeting records that appear in this detail view.

## Request
Create the prospect detail drawer and meeting history list components.

### 1. Meeting History List Component
Create `apps/Client/src/components/ui/TRMeetingHistoryList.tsx`:
```typescript
import React from 'react';
import { List, ListItem, ListItemText, IconButton, Typography, Divider, Box } from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import { MeetingRecord } from '@/types/prospect';
import prospectService from '@/services/prospectService';

interface TRMeetingHistoryListProps {
  meetings: MeetingRecord[];
}

export const TRMeetingHistoryList: React.FC<TRMeetingHistoryListProps> = ({ meetings }) => {
  const handleDownload = async (meetingId: number) => {
    console.log(`INFO [TRMeetingHistoryList]: Downloading meeting ${meetingId}`);
    await prospectService.downloadMeetingHtml(meetingId);
  };

  if (meetings.length === 0) {
    return <Typography color="text.secondary">No meetings recorded yet.</Typography>;
  }

  return (
    <List>
      {meetings.map((meeting) => (
        <React.Fragment key={meeting.id}>
          <ListItem
            secondaryAction={
              <IconButton edge="end" onClick={() => handleDownload(meeting.id)}>
                <DownloadIcon />
              </IconButton>
            }
          >
            <ListItemText
              primary={meeting.meeting_date
                ? new Date(meeting.meeting_date).toLocaleDateString()
                : 'Date unknown'}
              secondary={
                <Box>
                  {meeting.participants && (
                    <Typography variant="caption" display="block">
                      Participants: {meeting.participants}
                    </Typography>
                  )}
                  {meeting.summary && (
                    <Typography variant="body2" sx={{ mt: 0.5 }}>
                      {meeting.summary}
                    </Typography>
                  )}
                  {meeting.action_items && (
                    <Typography variant="body2" color="primary" sx={{ mt: 0.5 }}>
                      Action Items: {meeting.action_items}
                    </Typography>
                  )}
                </Box>
              }
            />
          </ListItem>
          <Divider />
        </React.Fragment>
      ))}
    </List>
  );
};
```

### 2. Prospect Detail Drawer
Create `apps/Client/src/components/ui/TRProspectDetail.tsx`:
- Use MUI `Drawer` (anchor="right", width ~450px)
- Props: `prospect: Prospect | null`, `open: boolean`, `onClose: () => void`
- When opened with a prospect:
  1. Fetch meetings via `prospectService.getMeetings(prospect.id)`
  2. Display prospect info: company name, contact name, contact email, stage (as Chip), notes
  3. Display stage transition history section (fetch from prospect detail endpoint which includes transitions)
  4. Display meeting history section using `TRMeetingHistoryList`
- Show loading skeleton while fetching meeting data

### 3. Integrate with ProspectsPage
Update `apps/Client/src/pages/ProspectsPage.tsx`:
- Add state for `selectedProspect` and `drawerOpen`
- Pass `onCardClick` handler to TRKanbanBoard that sets selectedProspect and opens drawer
- Render `TRProspectDetail` drawer

**UI Language:** English
**Validation:** Drawer closes on backdrop click or close button. Meeting download triggers browser file save.
```

---

## Wave 3: Transcript Processing Pipeline (Run in Parallel)

Build the automated pipeline that processes meeting transcripts into structured content and updates the CRM. REQ-011 (watcher) and REQ-012 (processor) can start in parallel. REQ-013 (CRM update) depends on REQ-012. REQ-014 (GitHub issue generation) depends on REQ-012.

### CRM-011: Meeting Transcript Watcher

**Title:** `[CRM Pipeline] Wave 3: Meeting Transcript Watcher`

**Body:**
```markdown
## Context
**Project:** Meeting Processing CRM Pipeline — CRM prospect tracking and automated meeting transcript processing for Finance Tracker
**Overview:** Create a new transcript watcher that monitors a dedicated folder for meeting transcript files. Similar to the existing `trigger_transcript_watch.py`, it detects new .md and .pdf files, tracks processed files, and triggers the meeting processing pipeline as a non-blocking subprocess.

**Current Wave:** Wave 3 of 3 — Transcript Processing Pipeline
**Current Issue:** CRM-011 (Issue 11 of 14)
**Parallel Execution:** YES — This issue runs in parallel with CRM-012.

**Dependencies:** None
**What comes next:** CRM-012 builds the processor that this watcher triggers. CRM-013 adds CRM update logic. CRM-014 adds GitHub issue generation.

## Request
Create the meeting transcript file watcher following existing ADW trigger patterns.

### 1. Watcher Script
Create `adws/adw_triggers/trigger_meeting_transcript_watch.py`:

Follow the same pattern as `adws/adw_triggers/trigger_transcript_watch.py`:
- Monitor folder: `External_Requirements/meeting_transcripts/` (configurable via `MEETING_TRANSCRIPT_FOLDER` env var)
- Detect new `.md` and `.pdf` files
- Maintain processed log at `agents/meeting_transcript_watch_processed.json`
- Track file modification time to re-process changed files
- On new/changed file detection:
  1. Log: `print(f"INFO [MeetingTranscriptWatcher]: New transcript detected: {filename}")`
  2. Launch processor as subprocess: `subprocess.Popen(["uv", "run", "adw_meeting_transcript_processor_iso.py", filepath])`
  3. Record file in processed log with mtime
- Configurable poll interval (default: 30 seconds, via `MEETING_WATCH_INTERVAL` env var)
- Graceful shutdown on SIGINT/SIGTERM

### 2. Processed Log Format
```json
{
  "processed_files": {
    "meeting_2026-02-28_acme-corp.md": {
      "processed_at": "2026-02-28T10:30:00",
      "mtime": 1709123400.0,
      "status": "launched"
    }
  }
}
```

### 3. Folder Setup
Create the watched folder if it doesn't exist:
```bash
mkdir -p External_Requirements/meeting_transcripts/
```
Add a `.gitkeep` file to preserve the empty directory.

### 4. Logging
```python
print(f"INFO [MeetingTranscriptWatcher]: Starting watcher on {watch_folder}")
print(f"INFO [MeetingTranscriptWatcher]: Poll interval: {interval}s")
print(f"INFO [MeetingTranscriptWatcher]: New transcript detected: {filename}")
print(f"INFO [MeetingTranscriptWatcher]: Launching processor for: {filename}")
print(f"INFO [MeetingTranscriptWatcher]: Graceful shutdown received")
```

**Validation:** Watcher must not reprocess files unless mtime changes. Subprocess launch must be non-blocking. Graceful shutdown required.
```

---

### CRM-012: Transcript to Structured Meeting Summary

**Title:** `[CRM Pipeline] Wave 3: Transcript to Structured Meeting Summary Processor`

**Body:**
```markdown
## Context
**Project:** Meeting Processing CRM Pipeline — CRM prospect tracking and automated meeting transcript processing for Finance Tracker
**Overview:** Create an ADW workflow that takes a raw meeting transcript and processes it into a structured meeting summary. Uses AI/LLM to extract participants, company/prospect identification, discussion points, action items, decisions, and next steps. Also generates a professionally styled HTML document suitable for sharing with the prospect.

**Current Wave:** Wave 3 of 3 — Transcript Processing Pipeline
**Current Issue:** CRM-012 (Issue 12 of 14)
**Parallel Execution:** YES — This issue runs in parallel with CRM-011.

**Dependencies:** None (standalone processor script)
**What comes next:** CRM-013 adds CRM update logic that uses this processor's structured output. CRM-014 adds GitHub issue generation.

## Request
Create the meeting transcript processor ADW workflow.

### 1. Processor Script
Create `adws/adw_meeting_transcript_processor_iso.py`:

Follow the existing ADW workflow pattern (worktree isolation):
- Accept transcript file path as CLI argument
- Generate a unique ADW ID (e.g., `meeting-proc-{timestamp}`)
- Read the transcript file content (.md or .pdf)
- Process via Claude API (or configured LLM) with a structured prompt

### 2. AI Processing Prompt
The processor should extract:
```python
EXTRACTION_PROMPT = """
Analyze this meeting transcript and extract the following in JSON format:

{
  "company_name": "The company/prospect discussed",
  "contact_name": "Primary contact person name",
  "contact_email": "Contact email if mentioned",
  "meeting_date": "Date of the meeting (ISO format)",
  "participants": ["List of all participants"],
  "summary": "3-5 sentence executive summary of the meeting",
  "discussion_points": ["Key topics discussed"],
  "action_items": ["Specific action items with owners if mentioned"],
  "decisions_made": ["Decisions reached during the meeting"],
  "next_steps": ["Agreed next steps"],
  "suggested_stage": "Suggested pipeline stage (new_lead, initial_contact, meeting_scheduled, meeting_completed, proposal_sent, negotiation, won, lost)"
}
"""
```

### 3. HTML Output Generation
Generate a professionally styled HTML document:
```python
def generate_meeting_html(meeting_data: dict) -> str:
    """Generate a clean, professional HTML meeting summary"""
    # Inline CSS for email/download compatibility
    # Sections: Header (company + date), Participants, Summary,
    # Discussion Points, Action Items, Decisions, Next Steps
    # Professional styling: clean fonts, subtle colors, clear hierarchy
    pass
```

### 4. Output Files
Save outputs to `agents/{adw_id}/meeting_outputs/`:
- `meeting_data.json` — structured extracted data
- `meeting_summary.html` — formatted HTML document
- `processing_log.txt` — processing log with timestamps

### 5. Logging
```python
print(f"INFO [MeetingProcessor]: Processing transcript: {filepath}")
print(f"INFO [MeetingProcessor]: Extracted company: {company_name}")
print(f"INFO [MeetingProcessor]: Generated HTML summary ({len(html)} bytes)")
print(f"INFO [MeetingProcessor]: Outputs saved to agents/{adw_id}/meeting_outputs/")
```

**Validation:** Must handle both .md and .pdf input formats. JSON output must be valid and parseable. HTML must use inline styles for portability.
```

---

### CRM-013: CRM Update from Processed Transcript

**Title:** `[CRM Pipeline] Wave 3: CRM Update from Processed Transcript`

**Body:**
```markdown
## Context
**Project:** Meeting Processing CRM Pipeline — CRM prospect tracking and automated meeting transcript processing for Finance Tracker
**Overview:** After processing a transcript (CRM-012), the pipeline updates the CRM via backend API calls: (1) create or match the prospect, (2) create a meeting record linked to the prospect, (3) advance the prospect's pipeline stage if appropriate. Uses API calls to endpoints from CRM-004 and CRM-005.

**Current Wave:** Wave 3 of 3 — Transcript Processing Pipeline
**Current Issue:** CRM-013 (Issue 13 of 14)
**Parallel Execution:** NO — Depends on CRM-012 (needs structured meeting data output).

**Dependencies:** CRM-004 (prospect API), CRM-005 (meeting API), CRM-012 (processor output)
**What comes next:** CRM-014 generates GitHub issues for additional processing. This completes the automated CRM update flow.

## Request
Add CRM update logic to the meeting transcript processor.

### 1. CRM Update Module
Create `adws/adw_modules/crm_update.py`:
```python
import httpx
import os

class CRMUpdater:
    def __init__(self):
        self.api_base = os.getenv("API_BASE_URL", "http://localhost:8000/api")
        self.auth_token = os.getenv("CRM_SERVICE_TOKEN")  # Service account JWT

    async def find_or_create_prospect(self, entity_id: int, meeting_data: dict) -> dict:
        """Search for existing prospect by company name/email, create if not found"""
        print(f"INFO [CRMUpdater]: Searching for prospect: {meeting_data['company_name']}")

        # Search existing prospects
        response = await self._get(f"/prospects?entity_id={entity_id}")
        prospects = response.json()

        # Match by company name or contact email
        match = None
        for p in prospects:
            if (p['company_name'].lower() == meeting_data['company_name'].lower() or
                (meeting_data.get('contact_email') and
                 p.get('contact_email', '').lower() == meeting_data['contact_email'].lower())):
                match = p
                break

        if match:
            print(f"INFO [CRMUpdater]: Found existing prospect: {match['id']}")
            return match

        # Create new prospect
        print(f"INFO [CRMUpdater]: Creating new prospect: {meeting_data['company_name']}")
        new_prospect = await self._post("/prospects", {
            "entity_id": entity_id,
            "company_name": meeting_data["company_name"],
            "contact_name": meeting_data.get("contact_name", "Unknown"),
            "contact_email": meeting_data.get("contact_email"),
            "stage": "new_lead",
            "notes": f"Auto-created from meeting transcript on {meeting_data.get('meeting_date', 'unknown date')}",
        })
        return new_prospect.json()

    async def create_meeting_record(self, prospect_id: int, meeting_data: dict, html_output: str) -> dict:
        """Create a meeting record linked to the prospect"""
        print(f"INFO [CRMUpdater]: Creating meeting record for prospect {prospect_id}")
        response = await self._post("/meetings", {
            "prospect_id": prospect_id,
            "meeting_date": meeting_data.get("meeting_date"),
            "participants": ", ".join(meeting_data.get("participants", [])),
            "summary": meeting_data.get("summary"),
            "action_items": "\n".join(meeting_data.get("action_items", [])),
            "formatted_output_html": html_output,
            "transcript_filename": meeting_data.get("transcript_filename"),
        })
        return response.json()

    async def advance_stage(self, prospect_id: int, suggested_stage: str) -> dict:
        """Advance prospect stage if appropriate"""
        print(f"INFO [CRMUpdater]: Advancing prospect {prospect_id} to stage: {suggested_stage}")
        response = await self._patch(f"/prospects/{prospect_id}/stage", {
            "stage": suggested_stage,
        })
        return response.json()

    async def _get(self, path: str):
        async with httpx.AsyncClient() as client:
            return await client.get(
                f"{self.api_base}{path}",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )

    async def _post(self, path: str, data: dict):
        async with httpx.AsyncClient() as client:
            return await client.post(
                f"{self.api_base}{path}",
                json=data,
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )

    async def _patch(self, path: str, data: dict):
        async with httpx.AsyncClient() as client:
            return await client.patch(
                f"{self.api_base}{path}",
                json=data,
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
```

### 2. Integrate into Processor
Update `adws/adw_meeting_transcript_processor_iso.py`:
- After extracting meeting data (CRM-012), call `CRMUpdater`
- Sequence: find_or_create_prospect → create_meeting_record → advance_stage
- Handle API failures gracefully (log error, continue processing)

### 3. Environment Configuration
Add to `.env` or ADW config:
```bash
API_BASE_URL=http://localhost:8000/api
CRM_SERVICE_TOKEN=<service-account-jwt-token>
CRM_DEFAULT_ENTITY_ID=1
```

### 4. Logging
```python
print(f"INFO [CRMUpdater]: CRM update complete for prospect {prospect_id}")
print(f"INFO [CRMUpdater]: Meeting record {meeting_id} created")
print(f"ERROR [CRMUpdater]: API call failed: {response.status_code} {response.text}")
```

**Validation:** Must handle case where prospect already exists (match by company/email). API failures must not crash the pipeline. Service account JWT must be configured.
```

---

### CRM-014: GitHub Issue Generation for Pipeline Updates

**Title:** `[CRM Pipeline] Wave 3: GitHub Issue Generation for Pipeline Updates`

**Body:**
```markdown
## Context
**Project:** Meeting Processing CRM Pipeline — CRM prospect tracking and automated meeting transcript processing for Finance Tracker
**Overview:** The pipeline generates GitHub issues describing CRM updates and meeting processing results. These issues follow the existing ADW pattern and can be picked up by adw_sdlc_iso for implementation if direct API updates fail or if additional application changes are needed.

**Current Wave:** Wave 3 of 3 — Transcript Processing Pipeline
**Current Issue:** CRM-014 (Issue 14 of 14)
**Parallel Execution:** NO — Depends on CRM-012 (needs structured meeting data).

**Dependencies:** CRM-012 (processor output data)
**What comes next:** This is the final issue. Generated GitHub issues can trigger adw_sdlc_iso workflows for follow-up work.

## Request
Add GitHub issue generation to the meeting transcript processor.

### 1. Issue Generation Module
Create or extend `adws/adw_modules/github_issue_generator.py` (or add to the processor):
```python
import subprocess
import json

def generate_meeting_issue(meeting_data: dict, prospect_data: dict, adw_id: str) -> str:
    """Generate a GitHub issue for the processed meeting"""

    title = f"[Meeting Processed] {meeting_data['company_name']} - {meeting_data.get('meeting_date', 'Unknown Date')}"

    body = f"""## Meeting Processing Results

**ADW ID:** {adw_id}
**Prospect:** {meeting_data['company_name']}
**Contact:** {meeting_data.get('contact_name', 'Unknown')} ({meeting_data.get('contact_email', 'N/A')})
**Meeting Date:** {meeting_data.get('meeting_date', 'Unknown')}
**Suggested Stage:** {meeting_data.get('suggested_stage', 'meeting_completed')}

### Summary
{meeting_data.get('summary', 'No summary available')}

### Action Items
{chr(10).join(f'- [ ] {item}' for item in meeting_data.get('action_items', []))}

### Decisions Made
{chr(10).join(f'- {d}' for d in meeting_data.get('decisions_made', []))}

### Next Steps
{chr(10).join(f'- {s}' for s in meeting_data.get('next_steps', []))}

### CRM Update Status
- Prospect ID: {prospect_data.get('id', 'N/A')}
- Prospect Created: {'Yes' if prospect_data.get('created', False) else 'Existing'}
- Meeting Record ID: {prospect_data.get('meeting_record_id', 'N/A')}
- Stage Updated: {prospect_data.get('stage_updated', False)}

---
*Generated by Meeting Transcript Processor ({adw_id})*
"""

    # Create GitHub issue using gh CLI
    result = subprocess.run(
        ["gh", "issue", "create",
         "--title", title,
         "--body", body,
         "--label", "meeting-processed"],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        issue_url = result.stdout.strip()
        print(f"INFO [GitHubIssueGenerator]: Issue created: {issue_url}")
        return issue_url
    else:
        print(f"ERROR [GitHubIssueGenerator]: Failed to create issue: {result.stderr}")
        return ""
```

### 2. Integrate into Processor
Update `adws/adw_meeting_transcript_processor_iso.py`:
- After CRM update (CRM-013), call `generate_meeting_issue()`
- Pass meeting_data and prospect update results
- Log the created issue URL

### 3. Label Setup
Ensure the `meeting-processed` label exists in the GitHub repository:
```bash
gh label create meeting-processed --description "Auto-generated from meeting transcript processing" --color "0e8a16"
```

### 4. Logging
```python
print(f"INFO [MeetingProcessor]: Generating GitHub issue for meeting: {company_name}")
print(f"INFO [MeetingProcessor]: GitHub issue created: {issue_url}")
print(f"INFO [MeetingProcessor]: Pipeline complete for transcript: {filename}")
```

**Validation:** Issue must include structured data (prospect info, action items, CRM status). Label must be applied for downstream workflow detection. Failed issue creation must not crash the pipeline.
```
