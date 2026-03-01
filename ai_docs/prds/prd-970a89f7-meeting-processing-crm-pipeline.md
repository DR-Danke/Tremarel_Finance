# PRD: Meeting Processing CRM Pipeline

## Meeting Metadata
- **Date**: 28th Feb, 2026
- **Participants**: Speaker 1 (product owner / stakeholder)
- **Duration**: ~5 minutes
- **Context**: Discussion of a new CRM-style prospect tracking system integrated with an automated meeting transcript processing pipeline for the Finance Tracker application.

## Executive Summary
The stakeholder requests two major capabilities: (1) a new CRM/Kanban board section in the application for tracking prospect and customer relationships through pipeline stages, and (2) an automated transcript processing pipeline (similar to the existing transcript watcher) that picks up Fireflies meeting transcripts, processes them into structured content, updates prospect status on the Kanban board, and generates downloadable meeting summaries that can be sent to prospects/customers. The pipeline should integrate with the existing ADW system by generating GitHub issues that trigger SDLC workflows.

## Work Streams

### Stream 1: Prospect/CRM Data Model & Backend API
Build the backend data layer and API endpoints to support prospect tracking, meeting history, and Kanban stage management.

#### Requirements

##### REQ-001: Prospect Data Model
- **Type**: feature
- **Priority**: P0
- **Description**: Create database tables and SQLAlchemy models for prospects/customers. A prospect record should include: company name, contact name, contact email, current pipeline stage, creation date, last activity date, notes, and association with an entity. Prospects must be entity-scoped (multi-entity support) consistent with the existing architecture.
- **Affected Modules**: `apps/Server/src/models/`, `apps/Server/database/`, `apps/Server/src/interface/`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] `prospect` table exists in PostgreSQL with columns: id, entity_id, company_name, contact_name, contact_email, stage, notes, created_at, updated_at
  - [ ] SQLAlchemy model `ProspectModel` is defined in `src/models/prospect_model.py`
  - [ ] Pydantic DTOs for create, update, and response are defined in `src/interface/prospect_dto.py`
  - [ ] Prospects are scoped to entities via `entity_id` foreign key

##### REQ-002: Pipeline Stage Configuration
- **Type**: feature
- **Priority**: P0
- **Description**: Define the Kanban pipeline stages for prospect tracking. Stages should be configurable but start with a sensible default set (e.g., "New Lead", "Initial Contact", "Meeting Scheduled", "Meeting Completed", "Proposal Sent", "Negotiation", "Won", "Lost"). Stage transitions should be tracked with timestamps.
- **Affected Modules**: `apps/Server/src/models/`, `apps/Server/src/interface/`
- **Dependencies**: REQ-001
- **Acceptance Criteria**:
  - [ ] A `pipeline_stage` table or enum exists with at least 5 default stages
  - [ ] Stage transitions are recorded with timestamps (stage history)
  - [ ] Stages have an ordinal position for Kanban column ordering

##### REQ-003: Meeting Record Data Model
- **Type**: feature
- **Priority**: P0
- **Description**: Create a data model for storing processed meeting records linked to prospects. Each meeting record should store: the original transcript reference, processed/structured summary, key action items, meeting date, participants, and a downloadable formatted output (HTML). Multiple meetings can be linked to a single prospect.
- **Affected Modules**: `apps/Server/src/models/`, `apps/Server/src/interface/`
- **Dependencies**: REQ-001
- **Acceptance Criteria**:
  - [ ] `meeting_record` table exists with columns: id, prospect_id, meeting_date, participants, summary, action_items, formatted_output_html, transcript_filename, created_at
  - [ ] Foreign key relationship to `prospect` table
  - [ ] SQLAlchemy model and Pydantic DTOs are defined

##### REQ-004: Prospect CRUD API Endpoints
- **Type**: feature
- **Priority**: P0
- **Description**: Create RESTful API endpoints for prospect management following the existing Clean Architecture pattern: routes in `adapter/rest/`, business logic in `core/services/`, data access in `repository/`. All endpoints must require authentication and filter by entity.
- **Affected Modules**: `apps/Server/src/adapter/rest/prospect_routes.py`, `apps/Server/src/core/services/prospect_service.py`, `apps/Server/src/repository/prospect_repository.py`, `apps/Server/main.py`
- **Dependencies**: REQ-001, REQ-002
- **Acceptance Criteria**:
  - [ ] `GET /api/prospects?entity_id={id}` returns paginated list of prospects filtered by entity
  - [ ] `POST /api/prospects` creates a new prospect
  - [ ] `GET /api/prospects/{id}` returns prospect detail with meeting history
  - [ ] `PUT /api/prospects/{id}` updates prospect information
  - [ ] `PATCH /api/prospects/{id}/stage` updates prospect pipeline stage and records transition
  - [ ] `DELETE /api/prospects/{id}` soft-deletes a prospect
  - [ ] All endpoints require JWT authentication via `get_current_user`
  - [ ] Router is registered in `main.py`

##### REQ-005: Meeting Record API Endpoints
- **Type**: feature
- **Priority**: P1
- **Description**: Create API endpoints for meeting records associated with prospects. Includes listing meetings for a prospect, retrieving meeting detail, and downloading the formatted HTML output.
- **Affected Modules**: `apps/Server/src/adapter/rest/meeting_routes.py`, `apps/Server/src/core/services/meeting_service.py`, `apps/Server/src/repository/meeting_repository.py`, `apps/Server/main.py`
- **Dependencies**: REQ-003, REQ-004
- **Acceptance Criteria**:
  - [ ] `GET /api/prospects/{id}/meetings` returns all meetings for a prospect
  - [ ] `GET /api/meetings/{id}` returns meeting detail with structured summary
  - [ ] `GET /api/meetings/{id}/download` returns the formatted HTML as a downloadable file
  - [ ] `POST /api/meetings` creates a new meeting record (used by the pipeline)
  - [ ] All endpoints require JWT authentication

### Stream 2: CRM Kanban Board Frontend
Build the frontend Kanban board interface for visualizing and managing prospect pipeline stages.

#### Requirements

##### REQ-006: Prospect Kanban Board Page
- **Type**: feature
- **Priority**: P1
- **Description**: Create a new page (`ProspectsPage`) with a Kanban board layout where each column represents a pipeline stage. Prospect cards appear in their respective stage columns. Cards should be draggable between columns to update stage. The page must follow existing patterns: use `TRMainLayout`, `useEntity()` for entity scoping, and be accessible from the sidebar navigation.
- **Affected Modules**: `apps/Client/src/pages/ProspectsPage.tsx`, `apps/Client/src/App.tsx`, `apps/Client/src/components/layout/TRCollapsibleSidebar.tsx`
- **Dependencies**: REQ-004
- **Acceptance Criteria**:
  - [ ] New route `/prospects` is registered in `App.tsx` wrapped with `ProtectedRoute` and `TRMainLayout`
  - [ ] Sidebar navigation includes a "Prospects" link
  - [ ] Kanban board displays columns for each pipeline stage
  - [ ] Prospect cards show company name, contact name, and last activity date
  - [ ] Prospects are filtered by the current entity via `useEntity()`

##### REQ-007: Prospect Card Drag-and-Drop
- **Type**: feature
- **Priority**: P1
- **Description**: Implement drag-and-drop functionality on the Kanban board so prospects can be moved between pipeline stages by dragging their cards. Stage changes must persist to the backend via the `PATCH /api/prospects/{id}/stage` endpoint.
- **Affected Modules**: `apps/Client/src/components/ui/TRKanbanBoard.tsx`, `apps/Client/src/components/ui/TRProspectCard.tsx`
- **Dependencies**: REQ-006
- **Acceptance Criteria**:
  - [ ] Cards can be dragged between Kanban columns
  - [ ] Dropping a card in a new column triggers a stage update API call
  - [ ] UI optimistically updates the card position
  - [ ] Failed API calls revert the card to its previous column with an error notification

##### REQ-008: Prospect Detail View
- **Type**: feature
- **Priority**: P1
- **Description**: When clicking on a prospect card in the Kanban board, display a detail view (drawer or dialog) showing: prospect information, stage history timeline, and a chronological list of all meetings/calls with their structured summaries. Each meeting entry should have a download button for the formatted HTML output.
- **Affected Modules**: `apps/Client/src/components/ui/TRProspectDetail.tsx`, `apps/Client/src/components/ui/TRMeetingHistoryList.tsx`
- **Dependencies**: REQ-005, REQ-006
- **Acceptance Criteria**:
  - [ ] Clicking a prospect card opens a detail view (drawer or modal)
  - [ ] Detail view shows prospect info (company, contact, stage, notes)
  - [ ] Detail view displays stage transition history with timestamps
  - [ ] Detail view shows chronological list of meetings with summaries
  - [ ] Each meeting has a download button that fetches the HTML formatted output
  - [ ] Meeting summaries show key action items

##### REQ-009: Prospect Creation Form
- **Type**: feature
- **Priority**: P1
- **Description**: Create a form component (`TRProspectForm`) for manually adding new prospects. Must use react-hook-form with MUI components following existing form patterns. The form should allow setting: company name, contact name, contact email, initial stage, and notes.
- **Affected Modules**: `apps/Client/src/components/forms/TRProspectForm.tsx`
- **Dependencies**: REQ-006
- **Acceptance Criteria**:
  - [ ] Form uses react-hook-form with MUI TextField components
  - [ ] Required field validation for company name and contact name
  - [ ] Email validation for contact email field
  - [ ] Stage dropdown defaults to "New Lead"
  - [ ] Successful submission creates prospect via API and refreshes Kanban board

##### REQ-010: Prospect Service & Hook
- **Type**: feature
- **Priority**: P1
- **Description**: Create the frontend service layer (`prospectService`) and custom hook (`useProspects`) for managing prospect data. Follow existing patterns with axios API client and entity-scoped queries.
- **Affected Modules**: `apps/Client/src/services/prospectService.ts`, `apps/Client/src/hooks/useProspects.ts`, `apps/Client/src/types/prospect.ts`
- **Dependencies**: REQ-004
- **Acceptance Criteria**:
  - [ ] `prospectService` provides methods: getAll, getById, create, update, updateStage, delete
  - [ ] `useProspects` hook manages loading state, error state, and data fetching
  - [ ] TypeScript interfaces for Prospect, MeetingRecord, and PipelineStage are defined in types
  - [ ] All API calls include JWT authorization header via axios interceptor

### Stream 3: Transcript Processing Pipeline
Build the automated pipeline that processes meeting transcripts into structured content and updates the CRM.

#### Requirements

##### REQ-011: Meeting Transcript Watcher
- **Type**: feature
- **Priority**: P1
- **Description**: Create a new transcript watcher (similar to `trigger_transcript_watch.py`) that monitors a dedicated folder for meeting transcript files. This watcher should detect new `.md` and `.pdf` files, track processed files to avoid reprocessing, and trigger the meeting processing pipeline. It should follow the same polling pattern as the existing transcript watcher (configurable interval, graceful shutdown).
- **Affected Modules**: `adws/adw_triggers/trigger_meeting_transcript_watch.py`
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] Watcher monitors `External_Requirements/meeting_transcripts/` folder (configurable via env var)
  - [ ] Detects new `.md` and `.pdf` files
  - [ ] Maintains a processed log at `agents/meeting_transcript_watch_processed.json`
  - [ ] Re-processes files if modification time changes
  - [ ] Launches processing pipeline as non-blocking subprocess
  - [ ] Graceful shutdown on SIGINT/SIGTERM

##### REQ-012: Transcript to Structured Meeting Summary
- **Type**: feature
- **Priority**: P1
- **Description**: Create an ADW workflow that takes a raw meeting transcript and processes it into a structured meeting summary. The processing should extract: participant names, company/prospect identification, key discussion points, action items, decisions made, next steps, and meeting date. It should also generate a well-formatted HTML document suitable for sending to the prospect/customer.
- **Affected Modules**: `adws/adw_meeting_transcript_processor_iso.py`
- **Dependencies**: REQ-011
- **Acceptance Criteria**:
  - [ ] Accepts a raw transcript file (`.md` or `.pdf`) as input
  - [ ] Extracts and structures: participants, discussion points, action items, decisions, next steps
  - [ ] Identifies the prospect/company from the transcript content
  - [ ] Generates a formatted HTML document with professional styling
  - [ ] Outputs structured JSON with extracted meeting data
  - [ ] Saves outputs to `agents/{adw_id}/meeting_outputs/`

##### REQ-013: CRM Update from Processed Transcript
- **Type**: feature
- **Priority**: P1
- **Description**: After processing a transcript, the pipeline should update the CRM data via the backend API: (1) create or match the prospect if not already in the system, (2) create a new meeting record linked to the prospect, (3) advance the prospect's pipeline stage if appropriate (e.g., from "New Lead" to "Meeting Completed"). This should be done via API calls to the endpoints created in REQ-004 and REQ-005.
- **Affected Modules**: `adws/adw_meeting_transcript_processor_iso.py`, `adws/adw_modules/`
- **Dependencies**: REQ-004, REQ-005, REQ-012
- **Acceptance Criteria**:
  - [ ] Pipeline searches for existing prospect by company name or contact email
  - [ ] Creates new prospect if no match is found (stage: "New Lead" → "Meeting Completed")
  - [ ] Updates existing prospect's stage and last activity date
  - [ ] Creates a meeting record with structured summary and HTML output
  - [ ] API calls use service account or admin JWT token for authentication

##### REQ-014: GitHub Issue Generation for Pipeline Updates
- **Type**: feature
- **Priority**: P2
- **Description**: The pipeline should generate GitHub issues describing the CRM updates that need to be made, following the existing ADW pattern. These issues can then be picked up by the SDLC workflow (`adw_sdlc_iso`) for implementation if direct API updates are not available or if additional application changes are needed.
- **Affected Modules**: `adws/adw_meeting_transcript_processor_iso.py`
- **Dependencies**: REQ-012
- **Acceptance Criteria**:
  - [ ] Pipeline generates a GitHub issue describing the meeting processing results
  - [ ] Issue includes: prospect info, meeting summary, required CRM updates
  - [ ] Issue is labeled for ADW processing (e.g., `meeting-processed` label)
  - [ ] Issue body contains structured data parseable by downstream workflows

## Implementation Waves

### Wave 1: Foundation (Data Model & Backend API)
**REQ IDs**: REQ-001, REQ-002, REQ-003, REQ-004, REQ-005

**Rationale**: The backend data model and API endpoints are foundational — both the frontend Kanban board and the transcript processing pipeline depend on these being available first. No external dependencies; this is pure backend work following established Clean Architecture patterns.

### Wave 2: CRM Frontend (Kanban Board)
**REQ IDs**: REQ-006, REQ-009, REQ-010, REQ-007, REQ-008

**Rationale**: With the backend API in place, the frontend Kanban board can be built. Start with the page structure, service layer, and basic form (REQ-006, REQ-009, REQ-010), then add drag-and-drop (REQ-007) and the detail view (REQ-008). This wave delivers the user-facing CRM functionality.

### Wave 3: Transcript Processing Pipeline
**REQ IDs**: REQ-011, REQ-012, REQ-013, REQ-014

**Rationale**: The pipeline depends on the backend API (Wave 1) for CRM updates. The watcher (REQ-011) and processor (REQ-012) can be built in parallel, then integrated with CRM updates (REQ-013) and GitHub issue generation (REQ-014). This wave delivers the automation that connects Fireflies transcripts to the CRM.

## Cross-Cutting Concerns

- **Database Migration**: New tables (`prospect`, `pipeline_stage`, `meeting_record`, `stage_transition_history`) must be created. A migration script should be provided for both local development and Supabase production.
- **Multi-Entity Scoping**: All prospect and meeting data must be entity-scoped via `entity_id`, consistent with the existing transaction/category/budget architecture.
- **Authentication for Pipeline**: The transcript processing pipeline needs a way to authenticate API calls. Options include a service account JWT, API key, or internal-only endpoints. This decision affects REQ-013.
- **Drag-and-Drop Library**: A DnD library is needed for the Kanban board (REQ-007). Options include `@hello-pangea/dnd` (maintained fork of react-beautiful-dnd), `dnd-kit`, or native HTML5 drag-and-drop.
- **HTML Template for Meeting Summaries**: The formatted HTML output (REQ-012) needs a professional template. Consider whether this is a simple inline-styled HTML document or uses a templating engine.
- **File Storage**: The HTML meeting summaries could be stored as text in the database (simplest) or as files with references. Database storage is recommended for simplicity given the existing architecture.

## Open Questions

- **Q1**: Should pipeline stages be hardcoded or user-configurable per entity? — Context: "moving the prospect from, you know, initial very early stage, to then having had the call" suggests a fixed set, but configurability may be desired.
- **Q2**: How should the pipeline authenticate to the backend API for CRM updates? Options: service account JWT, internal-only endpoints, or direct database access bypassing the API. — Context: "processes all the information and then updates the content that's going to be reviewed on the actual application"
- **Q3**: Should the transcript processing use AI/LLM to extract structured data from transcripts, or rely on a simpler parsing approach? — Context: "processes them from, say, meeting transcript into a more well structured format" implies AI-powered summarization.
- **Q4**: What is the exact folder path for meeting transcripts? Should it reuse `External_Requirements/transcripts/` or have a separate `External_Requirements/meeting_transcripts/` folder? — Context: "the transcript hits this folder" vs the existing transcript watcher also using a transcripts folder.
- **Q5**: Should the Kanban board support manual prospect creation in addition to auto-creation from transcripts? — Context: The transcript focuses on automated processing, but manual entry would be expected for a CRM.
- **Q6**: What information from the Fireflies transcript format can be reliably extracted? Is the format consistent (speaker labels, timestamps)? — Context: "meetings are had through fireflies, attends the meetings" — need to understand the input format.
