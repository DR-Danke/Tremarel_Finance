The PRD has been generated and saved to `ai_docs/prds/prd-970a89f7-meeting-processing-crm-pipeline.md`.

Here's a summary of what was extracted:

**3 Work Streams, 14 Requirements, 3 Implementation Waves:**

| Wave | Stream | Requirements | Focus |
|------|--------|-------------|-------|
| **Wave 1** | Backend Data Model & API | REQ-001 to REQ-005 | Prospect, stage, and meeting record models + CRUD endpoints |
| **Wave 2** | CRM Kanban Frontend | REQ-006 to REQ-010 | Kanban board page, drag-and-drop, prospect detail/form, service layer |
| **Wave 3** | Transcript Pipeline | REQ-011 to REQ-014 | Meeting transcript watcher, AI processing, CRM updates, GitHub issue generation |

**6 Open Questions** flagged for clarification, including: stage configurability, pipeline authentication strategy, AI vs simple parsing for transcripts, folder path for meeting transcripts, manual vs auto prospect creation, and Fireflies format reliability.

The PRD follows the existing ADW patterns (transcript watcher, worktree isolation, GitHub issue generation) and the application's Clean Architecture conventions (TR-prefixed components, entity-scoped data, react-hook-form, FastAPI layered backend).