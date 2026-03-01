# CRM Update from Processed Transcript

**ADW ID:** a61cf509
**Date:** 2026-03-01
**Specification:** specs/issue-59-adw-a61cf509-sdlc_planner-crm-update-from-processed-transcript.md

## Overview

Extends the meeting transcript processing pipeline (`adw_meeting_pipeline_iso.py`) to automatically update the CRM after processing a transcript. The pipeline now authenticates against the backend API, searches for or creates a prospect by company name, creates a linked meeting record, and optionally advances the prospect's pipeline stage from "lead" to "contacted".

## What Was Built

- **CRM API client module** (`adws/adw_modules/crm_api_client.py`) — reusable HTTP client for all CRM backend API interactions
- **Pipeline CRM integration** — `update_crm()` function in `adw_meeting_pipeline_iso.py` that orchestrates the full CRM update flow
- **Non-fatal error handling** — CRM failures are logged but never block the pipeline from completing its primary deliverable (JSON/HTML/markdown)
- **Comprehensive unit tests** — 16 new tests covering all CRM client methods and `update_crm` code paths

## Technical Implementation

### Files Modified

- `adws/adw_modules/crm_api_client.py`: New module with `CrmApiClient` class (260 lines). Handles JWT authentication, prospect search/create, meeting record creation, and stage advancement via HTTP calls to the backend API.
- `adws/adw_meeting_pipeline_iso.py`: Added `requests` dependency, imported `CrmApiClient`, added `update_crm()` function (100 lines), and integrated it into `main()` after `save_meeting_outputs()` with a try/except wrapper.
- `adws/adw_tests/test_meeting_pipeline.py`: Added 16 new tests (336 lines) for `CrmApiClient` and `update_crm()` covering success paths, error paths, edge cases, and graceful degradation.

### Key Changes

- `CrmApiClient` authenticates using service account credentials (`ADW_SERVICE_EMAIL` / `ADW_SERVICE_PASSWORD`) and caches the JWT token in memory for the pipeline run duration.
- Prospect matching uses case-insensitive company name comparison against the full prospect list for the entity.
- New prospects are created with stage `"contacted"` and source `"meeting-transcript"` since a meeting already occurred.
- Existing prospects at `"lead"` stage are automatically advanced to `"contacted"` when a meeting transcript is processed.
- All HTTP calls use a 30-second timeout and catch `requests.RequestException` for graceful degradation.

## How to Use

1. Set the required environment variables where the pipeline runs:
   - `ADW_SERVICE_EMAIL` — service account email for API authentication
   - `ADW_SERVICE_PASSWORD` — service account password
   - `ADW_ENTITY_ID` — target entity ID for prospect/meeting record creation
   - `ADW_API_BASE_URL` — backend API base URL (defaults to `http://localhost:8000/api`)
2. Run the meeting pipeline as usual (via transcript watcher trigger or manually)
3. After processing the transcript, the pipeline will automatically:
   - Authenticate with the backend API
   - Search for an existing prospect matching the transcript's `company_name`
   - Create a new prospect if no match is found
   - Create a meeting record linked to the matched/created prospect
   - Advance the prospect's stage from "lead" to "contacted" if applicable
4. CRM update results are logged. If any step fails, the pipeline continues normally.

## Configuration

| Environment Variable | Required | Default | Description |
|---|---|---|---|
| `ADW_SERVICE_EMAIL` | Yes | — | Service account email for API auth |
| `ADW_SERVICE_PASSWORD` | Yes | — | Service account password |
| `ADW_ENTITY_ID` | Yes | — | Entity ID for CRM records |
| `ADW_API_BASE_URL` | No | `http://localhost:8000/api` | Backend API base URL |

If any required variable is missing, the CRM update is skipped with a warning log.

## Testing

Run the meeting pipeline tests including CRM update tests:

```bash
cd adws && uv run pytest adw_tests/test_meeting_pipeline.py -v
```

Tests cover:
- `CrmApiClient` — authenticate success/failure, prospect search (found/not found/case-insensitive), prospect creation, meeting record creation, stage advancement, request timeout handling
- `update_crm` — skips when env vars missing, skips when no company_name, creates new prospect and meeting, matches existing prospect, advances lead to contacted, does not advance non-lead, handles API failure gracefully

## Notes

- **No backend changes** — all existing API endpoints are used as-is.
- **No frontend changes** — this is purely pipeline-side logic.
- **New dependency**: `requests` added to the inline script dependencies (resolved by `uv run`, no global dependency changes).
- **Stage advancement**: Only advances from "lead" to "contacted". More sophisticated logic is deferred to future requirements.
- **Prospect matching**: Case-insensitive exact match on company name. Fuzzy matching can be added later if needed.
- **Idempotency**: Duplicate pipeline runs for the same transcript will create additional meeting records (each processing is a unique event).
- **Security**: Service account credentials are read from environment variables, never hardcoded. JWT tokens are held only in memory.
