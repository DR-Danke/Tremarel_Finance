# CRM Pipeline — User Guide

This guide covers all new CRM Pipeline features added to Tremarel Finance (Issues 47–59). These features enable sales prospect management, visual pipeline tracking, meeting documentation, and automated transcript processing.

---

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Prospect Kanban Board](#prospect-kanban-board)
4. [Managing Prospects](#managing-prospects)
5. [Drag-and-Drop Stage Changes](#drag-and-drop-stage-changes)
6. [Prospect Detail Drawer](#prospect-detail-drawer)
7. [Meeting Records](#meeting-records)
8. [Pipeline Stage Configuration](#pipeline-stage-configuration)
9. [Automated Transcript Processing](#automated-transcript-processing)
10. [Environment Setup for Automation](#environment-setup-for-automation)

---

## Overview

The CRM Pipeline adds a complete sales prospect management system to Tremarel Finance. It is designed for startup entities that need to track potential clients through a sales funnel — from initial lead to won or lost deal.

**What you can do:**

- Track prospects through a visual Kanban board with customizable pipeline stages
- Create and edit prospect records with company, contact, and deal information
- Move prospects between stages by dragging cards across columns
- View full prospect detail including stage change history and meeting notes
- Attach meeting records with summaries, action items, and downloadable HTML reports
- Automate meeting transcript processing — drop a file and the system extracts structured data, creates HTML summaries, and updates the CRM automatically

---

## Getting Started

### Prerequisites

- You must be logged in with a valid account
- You must have an active entity selected (family or startup)
- CRM features are accessible from the sidebar navigation

### Accessing the CRM

1. Log in to Tremarel Finance
2. Select your entity from the entity selector in the top navbar
3. Click **"Prospects"** in the left sidebar (look for the business icon)

If this is your first time accessing the Prospects page for an entity, the system will automatically create the default pipeline stages for you.

---

## Prospect Kanban Board

The Kanban board is the central view for managing your sales pipeline. It displays prospects as cards organized into columns, one per pipeline stage.

### Board Layout

The board shows columns left to right in pipeline order:

| Stage | Color | Purpose |
|---|---|---|
| Lead | Blue (#90CAF9) | New uncontacted prospects |
| Contacted | Default | Initial outreach made |
| Qualified | Default | Prospect confirmed as a good fit |
| Proposal | Default | Proposal or quote sent |
| Negotiation | Default | Terms being discussed |
| Won | Green (#66BB6A) | Deal closed successfully |
| Lost | Red (#EF5350) | Deal did not close |

Each column header shows the stage name and a count of prospects in that stage. The columns scroll horizontally if they overflow the screen, and cards within each column scroll vertically.

### Loading State

While data is being fetched, the board displays skeleton placeholder animations so you know content is on its way.

---

## Managing Prospects

### Creating a Prospect

1. Click the **"Add Prospect"** button at the top of the Kanban board
2. A dialog opens with the prospect form
3. Fill in the required and optional fields:

| Field | Required | Notes |
|---|---|---|
| Company Name | Yes | Up to 255 characters |
| Contact Name | No | Up to 255 characters |
| Contact Email | No | Must be a valid email format |
| Contact Phone | No | Up to 100 characters |
| Pipeline Stage | Yes | Defaults to "Lead" |
| Estimated Value | No | Dollar amount, minimum $0 |
| Source | No | How you found this prospect (e.g., "referral", "website") |
| Notes | No | Free-text notes about the prospect |

4. Click **"Create"** to save — the card appears immediately in the corresponding stage column
5. Click **"Cancel"** to discard

### Editing a Prospect

There are two ways to edit:

1. **From the detail drawer:** Click a prospect card to open the detail drawer, then click the edit (pencil) icon in the drawer header
2. **Direct edit:** Use the three-dot menu or edit icon on the prospect card

The same form opens pre-filled with the prospect's current data. Make your changes and click **"Save"**.

### Deleting a Prospect

Deletion requires **admin** or **manager** role. Prospects are soft-deleted (marked inactive) rather than permanently removed.

---

## Drag-and-Drop Stage Changes

The fastest way to move a prospect through your pipeline is drag-and-drop.

### How to Use

1. **Click and hold** any prospect card
2. **Drag** the card to a different stage column
3. **Release** to drop the card in its new stage

### What Happens

- The card moves to the new column **immediately** (optimistic update — no waiting for the server)
- A stage transition record is created in the background for audit tracking
- If the server update fails, the card **automatically rolls back** to its original column and an error message appears

### Notes

- Dropping a card back into the same column does nothing
- Dropping outside a valid column does nothing
- The order of cards within a column is not persisted — cards appear in their default sort order after refresh

---

## Prospect Detail Drawer

Clicking a prospect card opens a detail drawer that slides in from the right side of the screen (520px wide).

### Prospect Information (Top Section)

Displays all prospect details at a glance:

- **Company name** (prominent header)
- **Contact info:** name, email (clickable mailto link), phone
- **Current stage** shown as a colored chip
- **Estimated value** formatted in USD
- **Source** and **Notes**

### Stage History Timeline (Middle Section)

Shows a chronological list of every stage change for this prospect:

- Each entry shows **"From Stage → To Stage"** with the date
- The first entry shows **"Initial assignment"** since there is no previous stage
- If a stage was deleted from the pipeline, it appears as **"Unknown"**
- This history is immutable — it cannot be edited or deleted

### Meeting History (Bottom Section)

Lists all meeting records linked to this prospect:

- Each meeting shows its **title**, **date**, **summary** (truncated to 3 lines), and **participants**
- A **Download** button on each meeting lets you save the formatted HTML meeting summary to your computer

### Navigation

- Click **X** or click outside the drawer to close it
- Click the **edit (pencil) icon** in the drawer header to switch to the edit dialog

---

## Meeting Records

Meeting records capture the results of meetings with prospects — summaries, action items, participants, and formatted reports.

### What a Meeting Record Contains

| Field | Description |
|---|---|
| Title | Meeting title (e.g., "Q1 Review with Acme Corp") |
| Meeting Date | When the meeting took place |
| Summary | Executive summary of the meeting |
| Action Items | List of follow-up tasks with owners and deadlines |
| Participants | List of attendees |
| HTML Output | Professionally formatted meeting report |
| Transcript Reference | Path or URL to the original transcript |

### Viewing Meeting Records

Meeting records appear in the **Meeting History** section of the prospect detail drawer. Each record shows a summary and allows you to download the full HTML report.

### Downloading HTML Reports

1. Open the prospect detail drawer by clicking a prospect card
2. Scroll to the Meeting History section
3. Click the **Download** button next to a meeting record
4. The formatted HTML report downloads to your browser's default download location
5. Open the `.html` file in any browser to view the professionally styled meeting summary

### Creating Meeting Records via API

Meeting records can be created through the REST API at `POST /api/meeting-records/`. This is primarily used by the automated transcript processing pipeline (see below), but can also be called directly if needed.

---

## Pipeline Stage Configuration

Pipeline stages are **customizable per entity**. Admins and managers can modify the sales pipeline to match their workflow.

### Default Stages

When you first access the Kanban board for an entity, seven default stages are automatically created:

1. Lead (Blue)
2. Contacted
3. Qualified
4. Proposal
5. Negotiation
6. Won (Green)
7. Lost (Red)

### API-Level Configuration

Stage management is currently available through the REST API:

- `GET /api/pipeline-stages/?entity_id=...` — List all stages for your entity
- `POST /api/pipeline-stages/` — Create a new stage (admin/manager)
- `PUT /api/pipeline-stages/{id}` — Update a stage (name, color, order)
- `DELETE /api/pipeline-stages/{id}` — Remove a stage (admin/manager)
- `POST /api/pipeline-stages/seed?entity_id=...` — Re-seed default stages (admin/manager)

### Stage Properties

Each stage has:
- **Name:** Internal identifier (e.g., "lead")
- **Display Name:** What appears on the Kanban board (e.g., "Lead")
- **Order Index:** Controls left-to-right column order
- **Color:** Hex color for the column header border (e.g., "#90CAF9")
- **Is Default:** Whether this is a system-created default stage
- **Is Active:** Active/inactive status

---

## Automated Transcript Processing

The transcript processing pipeline automatically converts raw meeting transcripts into structured CRM data. This is an operator-level feature that runs outside the web UI.

### How It Works

The pipeline has three components that work together:

```
Drop transcript file → Watcher detects it → Processor extracts data → CRM is updated
```

### Step 1: Drop a Transcript File

Place a `.md` (Markdown) or `.pdf` meeting transcript into:

```
External_Requirements/meeting_transcripts/
```

The transcript should be a raw meeting transcript — for example, exported from Fireflies, Otter.ai, or similar meeting recording tools.

### Step 2: Automatic Detection (Watcher)

The transcript watcher (`adw_meeting_transcript_watch.py`) polls the folder every 30 seconds. When it detects a new or modified file:

- It launches the processing pipeline as a background process
- Logs are written to `agents/meeting_pipeline_logs/`
- Processed files are tracked so they are not re-processed unless modified

**Running the watcher:**

```bash
cd adws/
uv run adw_meeting_transcript_watch.py           # Continuous monitoring
uv run adw_meeting_transcript_watch.py --once     # Single check, then exit
```

### Step 3: Transcript Processing

The processor (`adw_meeting_pipeline_iso.py`) uses an LLM to extract structured data from the transcript:

**Extracted data:**
- Meeting title and date
- Participants list
- Company/prospect identification
- Discussion points and key decisions
- Action items with owners and deadlines
- Executive summary (2-4 sentences)

**Outputs generated:**
1. **JSON summary** — Structured data in `agents/{id}/meeting_outputs/`
2. **HTML report** — Professionally styled document with inline CSS, suitable for sharing or printing
3. **Markdown summary** — Committed to a git branch in `ai_docs/meeting-summaries/`

### Step 4: Automatic CRM Update

After processing, the pipeline automatically updates the CRM:

1. **Prospect matching:** Searches existing prospects by company name (case-insensitive)
2. **If no match:** Creates a new prospect at the "Contacted" stage with source "meeting-transcript"
3. **If match at "Lead" stage:** Advances the prospect to "Contacted" (since a meeting already occurred)
4. **If match at any other stage:** No stage change (never regresses a prospect)
5. **Meeting record creation:** Links the processed meeting data to the matched/created prospect

All CRM updates are automatic and require no manual intervention.

**Important:** CRM update failures are non-fatal. If the CRM is unavailable or credentials are missing, the pipeline still completes its primary job (generating the HTML report and summaries).

---

## Environment Setup for Automation

The automated transcript processing pipeline requires the following environment variables:

| Variable | Required | Default | Description |
|---|---|---|---|
| `ADW_SERVICE_EMAIL` | Yes* | — | Service account email for CRM authentication |
| `ADW_SERVICE_PASSWORD` | Yes* | — | Service account password |
| `ADW_ENTITY_ID` | Yes* | — | Target entity ID for prospect/meeting creation |
| `ADW_API_BASE_URL` | No | `http://localhost:8000/api` | Backend API URL |
| `ADW_MEETING_TRANSCRIPT_FOLDER` | No | `External_Requirements/meeting_transcripts/` | Override watched folder path |
| `ADW_MEETING_TRANSCRIPT_POLL_INTERVAL` | No | `30` (seconds) | Override polling interval |

*Required only for CRM auto-update. If missing, the pipeline still processes transcripts and generates outputs — it just skips the CRM update silently.

### Setting Up a Service Account

1. Create a user account in Tremarel Finance for the automation pipeline
2. Assign it to the target entity with at least **user** role
3. Set `ADW_SERVICE_EMAIL` and `ADW_SERVICE_PASSWORD` to this account's credentials
4. Set `ADW_ENTITY_ID` to the entity where prospects and meeting records should be created

---

## Quick Reference

### Keyboard / Mouse Actions

| Action | Result |
|---|---|
| Click prospect card | Opens detail drawer |
| Click + hold + drag card | Moves prospect to new stage |
| Click edit icon (card or drawer) | Opens edit form dialog |
| Click "Add Prospect" button | Opens create form dialog |
| Click Download on meeting | Downloads HTML report |
| Click email in detail drawer | Opens email client (mailto) |

### API Endpoints Summary

| Endpoint | Method | Description |
|---|---|---|
| `/api/prospects/` | POST | Create prospect |
| `/api/prospects/` | GET | List prospects (with filters) |
| `/api/prospects/{id}` | GET | Get prospect detail |
| `/api/prospects/{id}` | PUT | Update prospect |
| `/api/prospects/{id}/stage` | PATCH | Change pipeline stage |
| `/api/prospects/{id}` | DELETE | Soft-delete prospect |
| `/api/meeting-records/` | POST | Create meeting record |
| `/api/meeting-records/` | GET | List meeting records |
| `/api/meeting-records/{id}` | GET | Get meeting record |
| `/api/meeting-records/{id}/html` | GET | Download HTML report |
| `/api/meeting-records/{id}` | PUT | Update meeting record |
| `/api/meeting-records/{id}` | DELETE | Soft-delete meeting record |
| `/api/pipeline-stages/` | GET | List pipeline stages |
| `/api/pipeline-stages/` | POST | Create stage |
| `/api/pipeline-stages/{id}` | PUT | Update stage |
| `/api/pipeline-stages/{id}` | DELETE | Delete stage |
| `/api/pipeline-stages/seed` | POST | Seed default stages |
| `/api/pipeline-stages/transitions/{prospect_id}` | GET | Get stage change history |

### Role Requirements

| Action | Minimum Role |
|---|---|
| View prospects, meetings, stages | Any authenticated user |
| Create/edit prospects and meetings | user |
| Delete prospects or meetings | admin or manager |
| Create/delete/seed pipeline stages | admin or manager |
