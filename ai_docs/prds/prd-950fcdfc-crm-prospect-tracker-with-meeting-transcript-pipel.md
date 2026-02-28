Now I have a comprehensive understanding of the system. Let me produce the PRD.

# PRD: CRM Prospect Tracker with Meeting Transcript Pipeline

## Meeting Metadata
- **Date**: 28th Feb, 2026
- **Participants**: Speaker 1 (product owner)
- **Duration**: ~5 minutes
- **Context**: Product owner describes a new CRM-like section for the Finance Tracker application to track prospect/customer relationships via a Kanban board, powered by an automated meeting transcript processing pipeline.

## Executive Summary
The product owner requests two major capabilities: (1) a new CRM/Kanban board section in the Finance Tracker application for tracking prospect and customer relationships across stages, and (2) an automated pipeline — similar to the existing transcript watcher — that processes meeting transcripts from Fireflies.ai, extracts structured content, updates prospect status on the Kanban board, and generates well-formatted meeting summaries that can be downloaded and sent to prospects/customers. The pipeline should integrate with the existing ADW system, generating GitHub issues that trigger the SDLC workflow to implement Kanban updates.

## Work Streams

### Stream 1: CRM Data Model & Backend API
Establish the database schema, models, repository, service, and REST API endpoints needed to support prospects, pipeline stages, meetings, and meeting artifacts.

#### Requirements

##### REQ-001: Prospect Database Model & Schema
- **Type**: feature
- **Priority**: P0
- **Description**: Create database tables to support the CRM system. A `prospects` table stores prospect/customer information (name, company, contact info, status, current stage, entity association). A `prospect_stages` table defines the Kanban pipeline stages (e.g., "New Lead", "Meeting Scheduled", "Meeting Completed", "Proposal Sent", "Negotiation", "Won", "Lost") with ordering. A `prospect_meetings` table stores processed meeting records linked to a prospect, including the raw transcript reference, processed date, and summary. A `prospect_meeting_artifacts` table stores the well-formatted output content (HTML/Markdown) that can be downloaded and sent to the prospect.
- **Affected Modules**: `apps/Server/database/schema.sql`, `apps/Server/src/models/`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] `prospects` table exists with columns: id (UUID PK), entity_id (FK to entities), name, company, email, phone, current_stage_id (FK), notes, is_active, created_at, updated_at
  - [ ] `prospect_stages` table exists with columns: id (PK), name, display_order, color, description, is_default
  - [ ] `prospect_meetings` table exists with columns: id (UUID PK), prospect_id (FK), transcript_file_path, meeting_date, summary, key_topics (JSON), action_items (JSON), processed_at, created_at
  - [ ] `prospect_meeting_artifacts` table exists with columns: id (UUID PK), meeting_id (FK), content_html, content_markdown, artifact_type, created_at
  - [ ] Default pipeline stages are seeded on migration
  - [ ] All foreign keys and indexes are properly defined

##### REQ-002: Prospect CRUD API Endpoints
- **Type**: feature
- **Priority**: P0
- **Description**: Create FastAPI REST endpoints for full CRUD operations on prospects, scoped by entity_id. Follow existing Clean Architecture patterns: routes in `adapter/rest/`, service in `core/services/`, repository in `repository/`. All endpoints require JWT authentication.
- **Affected Modules**: `apps/Server/src/adapter/rest/prospect_routes.py`, `apps/Server/src/core/services/prospect_service.py`, `apps/Server/src/repository/prospect_repository.py`, `apps/Server/src/interface/`
- **Dependencies**: REQ-001
- **Acceptance Criteria**:
  - [ ] `POST /api/prospects` creates a new prospect for the authenticated user's entity
  - [ ] `GET /api/prospects?entity_id=...` lists all prospects filtered by entity, with optional stage filter
  - [ ] `GET /api/prospects/{id}` returns prospect detail including meetings history
  - [ ] `PUT /api/prospects/{id}` updates prospect info (name, company, contact, notes)
  - [ ] `PATCH /api/prospects/{id}/stage` moves a prospect to a different Kanban stage
  - [ ] `DELETE /api/prospects/{id}` soft-deletes a prospect (admin/manager only)
  - [ ] All endpoints follow existing auth patterns with `get_current_user` dependency

##### REQ-003: Prospect Stages API Endpoints
- **Type**: feature
- **Priority**: P1
- **Description**: Create API endpoints to manage Kanban pipeline stages (list, reorder, create custom stages). Default stages should be pre-seeded but customizable per entity.
- **Affected Modules**: `apps/Server/src/adapter/rest/prospect_stage_routes.py`, `apps/Server/src/core/services/`, `apps/Server/src/repository/`
- **Dependencies**: REQ-001
- **Acceptance Criteria**:
  - [ ] `GET /api/prospect-stages?entity_id=...` returns all stages in display order
  - [ ] `POST /api/prospect-stages` creates a custom stage (admin/manager only)
  - [ ] `PUT /api/prospect-stages/reorder` updates display_order for multiple stages
  - [ ] Default stages are returned even if no custom stages have been created

##### REQ-004: Prospect Meetings & Artifacts API Endpoints
- **Type**: feature
- **Priority**: P0
- **Description**: Create API endpoints to retrieve meeting history for a prospect, view meeting details with structured content, and download formatted artifacts (HTML) for sending to prospects/customers.
- **Affected Modules**: `apps/Server/src/adapter/rest/prospect_meeting_routes.py`, `apps/Server/src/core/services/`, `apps/Server/src/repository/`
- **Dependencies**: REQ-001
- **Acceptance Criteria**:
  - [ ] `GET /api/prospects/{id}/meetings` returns paginated meeting history for a prospect
  - [ ] `GET /api/prospect-meetings/{meeting_id}` returns full meeting detail including summary, key topics, action items
  - [ ] `GET /api/prospect-meetings/{meeting_id}/artifact` returns downloadable HTML content
  - [ ] `POST /api/prospect-meetings` allows creating a meeting record (used by the pipeline)
  - [ ] Meeting artifacts can be downloaded as HTML file via content-disposition header

### Stream 2: CRM Kanban Board Frontend
Build the frontend UI for the CRM section with a Kanban board view for tracking prospects across pipeline stages, and detail views for individual prospects and their meeting history.

#### Requirements

##### REQ-005: Kanban Board Page with Drag-and-Drop
- **Type**: feature
- **Priority**: P0
- **Description**: Create a new `ProspectsPage` accessible from the sidebar navigation. The page displays a Kanban board where each column represents a pipeline stage (e.g., "New Lead", "Meeting Scheduled", "Meeting Completed", etc.) and each card represents a prospect. Cards should show prospect name, company, and last meeting date. Prospects can be dragged between columns to update their stage. Use the TR component prefix convention.
- **Affected Modules**: `apps/Client/src/pages/ProspectsPage.tsx`, `apps/Client/src/components/ui/TRKanbanBoard.tsx`, `apps/Client/src/components/ui/TRKanbanColumn.tsx`, `apps/Client/src/components/ui/TRProspectCard.tsx`, `apps/Client/src/App.tsx`, `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`
- **Dependencies**: REQ-002, REQ-003
- **Acceptance Criteria**:
  - [ ] `/prospects` route exists and is protected behind authentication
  - [ ] Sidebar navigation includes a "Prospects" link (with appropriate icon)
  - [ ] Kanban board renders one column per pipeline stage in correct order
  - [ ] Each prospect card displays: name, company, last meeting date (if any)
  - [ ] Drag-and-drop between columns updates the prospect's stage via API call
  - [ ] Board filters by the currently selected entity (EntityContext)
  - [ ] Loading and empty states are handled gracefully

##### REQ-006: Prospect Detail View
- **Type**: feature
- **Priority**: P0
- **Description**: When clicking a prospect card on the Kanban board, open a detail view (could be a full page or modal/drawer) showing the prospect's information, a timeline of all meetings, and the ability to view/download formatted meeting content. Each meeting entry should show date, summary, key topics, action items, and a download button for the HTML artifact.
- **Affected Modules**: `apps/Client/src/pages/ProspectDetailPage.tsx` or `apps/Client/src/components/ui/TRProspectDetailDrawer.tsx`, `apps/Client/src/components/ui/TRMeetingTimeline.tsx`, `apps/Client/src/components/ui/TRMeetingCard.tsx`
- **Dependencies**: REQ-004, REQ-005
- **Acceptance Criteria**:
  - [ ] Prospect detail displays: name, company, email, phone, current stage, notes
  - [ ] Meeting history is displayed in reverse chronological order
  - [ ] Each meeting shows: date, summary, key topics, action items
  - [ ] Download button triggers HTML artifact download for each meeting
  - [ ] Prospect info can be edited inline or via a form

##### REQ-007: Prospect Create/Edit Form
- **Type**: feature
- **Priority**: P1
- **Description**: Create a form component `TRProspectForm` using react-hook-form + MUI for creating and editing prospect records. Include fields for name, company, email, phone, initial stage selection, and notes.
- **Affected Modules**: `apps/Client/src/components/forms/TRProspectForm.tsx`
- **Dependencies**: REQ-002, REQ-003
- **Acceptance Criteria**:
  - [ ] Form uses react-hook-form with MUI TextField components
  - [ ] Name field is required; email has format validation
  - [ ] Stage dropdown populated from stages API
  - [ ] Form works for both create and edit modes
  - [ ] Error states display via MUI helperText

##### REQ-008: Prospect Frontend Service Layer
- **Type**: feature
- **Priority**: P0
- **Description**: Create `prospectService`, `prospectStageService`, and `prospectMeetingService` in the services directory following the existing service pattern (Axios calls with JWT interceptor). Add corresponding TypeScript types/interfaces.
- **Affected Modules**: `apps/Client/src/services/prospectService.ts`, `apps/Client/src/services/prospectStageService.ts`, `apps/Client/src/services/prospectMeetingService.ts`, `apps/Client/src/types/index.ts` or `apps/Client/src/types/prospect.ts`
- **Dependencies**: REQ-002, REQ-003, REQ-004
- **Acceptance Criteria**:
  - [ ] TypeScript interfaces defined for Prospect, ProspectStage, ProspectMeeting, ProspectMeetingArtifact
  - [ ] `prospectService` exposes: getAll, getById, create, update, updateStage, delete
  - [ ] `prospectStageService` exposes: getAll, create, reorder
  - [ ] `prospectMeetingService` exposes: getByProspect, getById, downloadArtifact
  - [ ] All services use the existing API client with JWT interceptor

### Stream 3: Meeting Transcript Processing Pipeline
Build an automated pipeline that watches for new meeting transcripts, processes them into structured content, matches or creates prospects, updates Kanban status, and generates formatted meeting artifacts — leveraging the existing ADW infrastructure.

#### Requirements

##### REQ-009: CRM Transcript Watcher Trigger
- **Type**: feature
- **Priority**: P1
- **Description**: Create a new transcript watcher (similar to the existing `trigger_transcript_watch.py`) that monitors a dedicated folder for CRM meeting transcripts. When a new transcript file is detected, it triggers the CRM processing pipeline. This watcher should run alongside the existing transcript watcher without conflict. The watched folder could be a subfolder like `External_Requirements/transcripts/crm/` or a separate configurable path.
- **Affected Modules**: `adws/adw_triggers/trigger_crm_transcript_watch.py`, `adws/` configuration
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] New watcher script monitors a configurable CRM transcripts folder
  - [ ] Supports `.md` and `.pdf` transcript files (same as existing watcher)
  - [ ] Maintains its own processed files log (separate from the existing watcher)
  - [ ] Triggers CRM pipeline as a non-blocking background subprocess
  - [ ] Can run in continuous polling mode and single-check (`--once`) mode
  - [ ] Does not interfere with the existing transcript watcher

##### REQ-010: CRM Transcript Processing Pipeline
- **Type**: feature
- **Priority**: P1
- **Description**: Create a pipeline that processes a raw meeting transcript into structured CRM data. The pipeline should: (1) Extract meeting content using AI (Claude) to identify the prospect/customer discussed, key topics, action items, and a structured summary. (2) Match the extracted prospect to an existing prospect record or flag for new prospect creation. (3) Generate a well-formatted HTML/Markdown meeting summary suitable for sending to the prospect. (4) Create a GitHub issue with the extracted information that can trigger the SDLC ADW to update the application data (Kanban board, meeting records).
- **Affected Modules**: `adws/adw_crm_pipeline_iso.py`, `adws/adw_crm_transcript_process_iso.py`, new Claude Code slash commands/prompts
- **Dependencies**: REQ-009, REQ-001
- **Acceptance Criteria**:
  - [ ] Pipeline reads raw transcript (PDF or Markdown)
  - [ ] AI extraction produces: prospect name, company, meeting date, summary, key topics (list), action items (list), recommended stage transition
  - [ ] Pipeline generates formatted HTML meeting summary with professional styling
  - [ ] Pipeline creates a GitHub issue with structured data for SDLC processing
  - [ ] Pipeline output includes both the meeting artifact and Kanban update instructions
  - [ ] Failed processing is logged with error details; does not crash the watcher

##### REQ-011: Prospect Auto-Match and Stage Transition Logic
- **Type**: feature
- **Priority**: P1
- **Description**: When a transcript is processed, the pipeline should attempt to match the discussed prospect/customer against existing records (by name, company, or email). If a match is found, the prospect's stage should be automatically advanced (e.g., from "New Lead" to "Meeting Completed") and a new meeting record added. If no match is found, a new prospect record should be created in an initial stage with the first meeting attached.
- **Affected Modules**: `apps/Server/src/core/services/prospect_service.py`, pipeline scripts
- **Dependencies**: REQ-001, REQ-002, REQ-010
- **Acceptance Criteria**:
  - [ ] Prospect matching works by name (fuzzy) and company name
  - [ ] Matched prospects have their stage updated according to configurable transition rules
  - [ ] Unmatched prospects are created with default "New Lead" stage
  - [ ] A new meeting record is created and linked to the prospect (matched or new)
  - [ ] Meeting artifact (HTML) is stored and accessible for download

## Implementation Waves

### Wave 1: Foundation
**REQ-001** (Database schema), **REQ-009** (CRM transcript watcher trigger)

Rationale: The database schema is the foundation all other features depend on. The transcript watcher can be developed in parallel since it only needs to detect files and trigger a pipeline — it has no dependency on the application database.

### Wave 2: Backend API
**REQ-002** (Prospect CRUD), **REQ-003** (Stages API), **REQ-004** (Meetings & Artifacts API)

Rationale: These require the database schema from Wave 1. All three can be developed in parallel as they operate on different tables/routes. They are prerequisites for both the frontend and the processing pipeline.

### Wave 3: Frontend & Pipeline (Parallel Tracks)
**REQ-008** (Frontend service layer), **REQ-005** (Kanban board page), **REQ-007** (Prospect form), **REQ-010** (CRM transcript processing pipeline)

Rationale: The frontend services and Kanban board depend on the backend API from Wave 2. The processing pipeline depends on the transcript watcher (Wave 1) and the backend API (Wave 2) for writing data. These two tracks (frontend and pipeline) can proceed in parallel.

### Wave 4: Integration & Detail Views
**REQ-006** (Prospect detail view), **REQ-011** (Auto-match and stage transitions)

Rationale: The detail view depends on the Kanban board and meetings API. The auto-match logic depends on both the pipeline and the prospect CRUD API. This wave brings everything together into the complete end-to-end flow.

## Cross-Cutting Concerns

- **Database Migration**: New tables (`prospects`, `prospect_stages`, `prospect_meetings`, `prospect_meeting_artifacts`) must be added to the PostgreSQL schema on Supabase. A migration strategy is needed — either raw SQL scripts or an Alembic-based approach consistent with the existing project.
- **Entity Scoping**: All prospect data must be scoped to entities (like transactions, categories, budgets). The entity_id FK pattern used throughout the app must be replicated.
- **Authentication & RBAC**: All new API endpoints must follow the existing JWT auth pattern. Stage management and prospect deletion should require admin/manager roles.
- **Frontend Routing**: A new `/prospects` route and optionally `/prospects/:id` must be added to `App.tsx` and the sidebar navigation updated.
- **Drag-and-Drop Library**: The Kanban board requires a drag-and-drop library. Options include `@hello-pangea/dnd` (maintained fork of react-beautiful-dnd), `dnd-kit`, or MUI's own drag capabilities. This choice needs to be made during implementation.
- **HTML Generation**: The pipeline needs to produce professional-looking HTML meeting summaries. A templating approach (e.g., a reusable HTML template with CSS styling) should be established.
- **ADW Pipeline Integration**: The new CRM pipeline must follow the same patterns as `adw_requirements_pipeline_iso.py` — using worktrees, state management, and Claude Code execution via `adw_modules/agent.py`.

## Open Questions

- **Q1**: Should the CRM transcript watcher reuse the existing `External_Requirements/transcripts/` folder (with subfolder separation) or use an entirely separate folder? — Context: "These meetings meeting transcripts are gonna hit a folder... The transcript hits this folder, gets to this folder"
- **Q2**: What specific Kanban stages should be pre-seeded? The transcript mentions "initial very early stage" and "having had the call" but doesn't define a complete pipeline. — Context: "updates the status like moving the prospect from, you know, initial very early stage, to then having had the call"
- **Q3**: Should the formatted meeting output be HTML specifically, or is Markdown with HTML export acceptable? — Context: "download it, maybe as HTML or something similar, to then be able to send to the prospect"
- **Q4**: How should the pipeline-generated GitHub issues be structured for the SDLC ADW to process them into application data updates? Should this be a new ADW workflow type or use the existing `adw_sdlc_iso`? — Context: "generates the GitHub say, the GitHub issues that then are gonna be picked up by one of the other adws, maybe like the ADW, SLD software, SDLC"
- **Q5**: Should prospect matching across transcripts be based purely on name/company extraction from the transcript, or should there be a way to tag transcripts with a prospect identifier before they hit the watched folder? — Context: "if it's a new not a customer yet, updates the status"
- **Q6**: Is there a need for manual prospect creation via the UI, or should all prospects be created exclusively through the transcript processing pipeline? — Context: The transcript focuses on automated creation but doesn't explicitly exclude manual creation.