Generated the implementation prompts document at `ai_docs/prds/prd-970a89f7-meeting-processing-crm-pipeline-prompts.md`.

**Summary: 14 prompts across 3 waves:**

| Wave | Issues | Focus | Parallel? |
|------|--------|-------|-----------|
| **Wave 1** | CRM-001 to CRM-005 | Backend data models (Prospect, Pipeline Stage, Meeting Record) + CRUD API endpoints | YES (5 parallel) |
| **Wave 2** | CRM-006 to CRM-010 | Frontend service/types, form, Kanban board page, drag-and-drop, detail drawer | Partially (006-008 parallel, then 009-010) |
| **Wave 3** | CRM-011 to CRM-014 | Transcript watcher, AI processor, CRM auto-update, GitHub issue generation | Partially (011-012 parallel, then 013-014) |

Each prompt is self-contained with Context/Request sections, explicit file paths, code snippets, dependency references, and parallel execution flags — ready for `adw_sdlc_iso.py` execution.