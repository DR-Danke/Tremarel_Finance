# Feature: CRM Update from Processed Transcript

## Metadata
issue_number: `59`
adw_id: `a61cf509`
issue_json: ``

## Feature Description
After the meeting transcript processor (`adw_meeting_pipeline_iso.py`, REQ-012) extracts structured JSON from a raw transcript, the pipeline must automatically update the CRM by: (1) searching for an existing prospect by company name or contact email, (2) creating a new prospect if no match is found, (3) creating a meeting record linked to the prospect, and (4) advancing the prospect's pipeline stage if appropriate. This implements REQ-013 from the meeting processing CRM pipeline PRD (`prd-970a89f7`).

The CRM update happens entirely within the ADW pipeline script — it authenticates against the backend API using service account credentials, then calls the existing prospect and meeting record REST endpoints.

## User Story
As a CRM pipeline operator
I want the meeting transcript processor to automatically create or update prospects and meeting records in the CRM
So that every processed transcript is linked to a prospect with a full meeting history without manual data entry

## Problem Statement
Currently `adw_meeting_pipeline_iso.py` processes transcripts into structured JSON and HTML but does not push that data into the CRM. The structured output contains `company_name`, `contact_name`, `contact_email`, and meeting details that map directly to the Prospect and MeetingRecord models, but no code exists to create those records via the backend API. Users must manually create prospects and meeting records, defeating the purpose of automated transcript processing.

## Solution Statement
Extend `adw_meeting_pipeline_iso.py` with a new `update_crm()` function that runs after `save_meeting_outputs()`. This function will:

1. Authenticate with the backend API using service account credentials (`ADW_SERVICE_EMAIL` / `ADW_SERVICE_PASSWORD` env vars) to obtain a JWT token.
2. Search existing prospects by company name (case-insensitive) using `GET /api/prospects/?entity_id=...`.
3. If no match found, create a new prospect via `POST /api/prospects/` with stage `"contacted"` (since a meeting already occurred).
4. Create a meeting record via `POST /api/meeting-records/` linked to the prospect, populating all available fields from the parsed transcript JSON.
5. Advance the prospect's pipeline stage from `"lead"` to `"contacted"` if the prospect was already at `"lead"` stage, using `PATCH /api/prospects/{id}/stage`.
6. Handle errors gracefully — CRM update failures should log errors but NOT fail the overall pipeline (the transcript processing itself already succeeded).

The `requests` library will be added as a dependency to the script's inline metadata for HTTP calls.

## Relevant Files
Use these files to implement the feature:

- `adws/adw_meeting_pipeline_iso.py` — Main pipeline script to extend with CRM update logic. This is the primary file to modify.
- `adws/adw_tests/test_meeting_pipeline.py` — Existing test file to extend with CRM update tests.
- `apps/Server/src/adapter/rest/prospect_routes.py` — Prospect API endpoints (POST create, GET list, PATCH stage). Read-only reference for API contract.
- `apps/Server/src/adapter/rest/meeting_record_routes.py` — Meeting record API endpoints (POST create). Read-only reference for API contract.
- `apps/Server/src/interface/prospect_dto.py` — Prospect DTOs defining request/response shapes. Read-only reference.
- `apps/Server/src/interface/meeting_record_dto.py` — Meeting record DTOs defining request/response shapes. Read-only reference.
- `apps/Server/src/adapter/rest/auth_routes.py` — Auth login endpoint (`POST /api/auth/login`). Read-only reference for obtaining JWT token.
- `apps/Server/src/config/settings.py` — Backend settings, shows env var patterns. Read-only reference.
- `.claude/commands/process_meeting_transcript.md` — Slash command template that defines the structured JSON output schema. Read-only reference.
- `app_docs/feature-e924e4a7-meeting-transcript-summary-processor.md` — Documentation for the transcript processor (REQ-012). Read-only reference.
- `app_docs/feature-70362135-prospect-crud-api-endpoints.md` — Documentation for prospect CRUD endpoints. Read-only reference.
- `app_docs/feature-d1b26544-meeting-record-api-endpoints.md` — Documentation for meeting record API endpoints. Read-only reference.

### New Files
- `adws/adw_modules/crm_api_client.py` — New module encapsulating all CRM API calls (auth, prospect CRUD, meeting record creation). Keeps the pipeline script clean and the API logic reusable.

## Implementation Plan
### Phase 1: Foundation
Create the `CrmApiClient` module (`adws/adw_modules/crm_api_client.py`) that handles:
- Authentication: `POST /api/auth/login` with service account credentials, caching the JWT token.
- Prospect search: `GET /api/prospects/?entity_id=...` with company name matching.
- Prospect creation: `POST /api/prospects/` with transcript-extracted data.
- Meeting record creation: `POST /api/meeting-records/` with all structured fields.
- Stage advancement: `PATCH /api/prospects/{id}/stage` to advance from lead to contacted.
- Error handling: All API calls wrapped with proper logging, timeouts, and graceful degradation.

### Phase 2: Core Implementation
Integrate the CRM API client into `adw_meeting_pipeline_iso.py`:
- Add `requests` to the inline script dependencies.
- Add new env vars: `ADW_SERVICE_EMAIL`, `ADW_SERVICE_PASSWORD`, `ADW_API_BASE_URL`, `ADW_ENTITY_ID`.
- Add a new `update_crm()` function that orchestrates the CRM update flow.
- Call `update_crm()` after `save_meeting_outputs()` in the `main()` function.
- CRM failures should log but not exit — the pipeline's primary deliverable (JSON/HTML/markdown) is already saved.

### Phase 3: Integration
- Write comprehensive unit tests for the CRM API client and the pipeline's `update_crm()` integration.
- Validate the full pipeline by running tests end-to-end.
- Ensure backward compatibility — the pipeline must still work when CRM env vars are not set (skip CRM update with a warning).

## Step by Step Tasks

### Step 1: Read relevant documentation and existing code
- Read `app_docs/feature-e924e4a7-meeting-transcript-summary-processor.md` for processor context
- Read `app_docs/feature-70362135-prospect-crud-api-endpoints.md` for prospect API contract
- Read `app_docs/feature-d1b26544-meeting-record-api-endpoints.md` for meeting record API contract
- Read `adws/adw_meeting_pipeline_iso.py` to understand the current pipeline flow
- Read `apps/Server/src/interface/prospect_dto.py` and `apps/Server/src/interface/meeting_record_dto.py` for DTO shapes
- Read `apps/Server/src/adapter/rest/prospect_routes.py` and `apps/Server/src/adapter/rest/meeting_record_routes.py` for endpoint signatures
- Read `apps/Server/src/adapter/rest/auth_routes.py` for login endpoint

### Step 2: Create CRM API client module
- Create `adws/adw_modules/crm_api_client.py` with class `CrmApiClient`
- Constructor takes `base_url: str` and `logger: logging.Logger`
- Implement `authenticate(email: str, password: str) -> bool` method:
  - `POST {base_url}/auth/login` with `{"email": email, "password": password}`
  - Cache the JWT token from `response.json()["access_token"]`
  - Return `True` on success, `False` on failure
  - Log outcome
- Implement `_headers() -> dict` helper that returns `{"Authorization": f"Bearer {self._token}", "Content-Type": "application/json"}`
- Implement `search_prospect(entity_id: str, company_name: str) -> dict | None` method:
  - `GET {base_url}/prospects/?entity_id={entity_id}&limit=100`
  - Iterate through `response.json()["prospects"]` and find a case-insensitive match on `company_name`
  - Return the first match or `None`
  - Log outcome
- Implement `create_prospect(entity_id: str, company_name: str, contact_name: str | None, contact_email: str | None, stage: str, source: str, notes: str | None) -> dict | None` method:
  - `POST {base_url}/prospects/` with `ProspectCreateDTO`-shaped JSON body
  - Return the created prospect dict or `None` on failure
  - Log outcome
- Implement `create_meeting_record(entity_id: str, prospect_id: str, title: str, transcript_ref: str | None, summary: str | None, action_items: list[str] | None, participants: list[str] | None, html_output: str | None, meeting_date: str | None) -> dict | None` method:
  - `POST {base_url}/meeting-records/` with `MeetingRecordCreateDTO`-shaped JSON body
  - Return the created meeting record dict or `None` on failure
  - Log outcome
- Implement `advance_prospect_stage(prospect_id: str, entity_id: str, new_stage: str, notes: str | None) -> dict | None` method:
  - `PATCH {base_url}/prospects/{prospect_id}/stage?entity_id={entity_id}` with `{"new_stage": new_stage, "notes": notes}`
  - Return the updated prospect dict or `None` on failure
  - Log outcome
- All HTTP calls should use a 30-second timeout and catch `requests.RequestException`

### Step 3: Add CRM update function to pipeline script
- Add `requests` to the inline `# dependencies` list in `adw_meeting_pipeline_iso.py`
- Add import: `from adw_modules.crm_api_client import CrmApiClient`
- Add function `update_crm(meeting_data: dict, transcript_path: str, adw_id: str, logger: logging.Logger) -> None`:
  - Read env vars: `ADW_API_BASE_URL` (default `http://localhost:8000/api`), `ADW_SERVICE_EMAIL`, `ADW_SERVICE_PASSWORD`, `ADW_ENTITY_ID`
  - If any of `ADW_SERVICE_EMAIL`, `ADW_SERVICE_PASSWORD`, `ADW_ENTITY_ID` are missing, log a warning and return (graceful skip)
  - Create `CrmApiClient(base_url, logger)`
  - Call `client.authenticate(email, password)` — on failure, log error and return
  - Extract `company_name` from `meeting_data.get("company_name")` — if missing, log warning and return (cannot match/create prospect without company name)
  - Call `client.search_prospect(entity_id, company_name)`
  - If prospect found:
    - Log that an existing prospect was matched
    - If prospect `stage == "lead"`, call `client.advance_prospect_stage(prospect_id, entity_id, "contacted", "Auto-advanced: meeting transcript processed")`
  - If no prospect found:
    - Call `client.create_prospect(entity_id, company_name, contact_name, contact_email, stage="contacted", source="meeting-transcript", notes=f"Auto-created from transcript processing (ADW: {adw_id})")`
    - If creation fails, log error and return
  - Extract participant names as `[p.get("name", "Unknown") if isinstance(p, dict) else str(p) for p in meeting_data.get("participants", [])]`
  - Extract action items as `[a.get("description", str(a)) if isinstance(a, dict) else str(a) for a in meeting_data.get("action_items", [])]`
  - Call `client.create_meeting_record(entity_id, prospect_id, title, transcript_ref=transcript_path, summary, action_items, participants, html_output, meeting_date)`
  - Log success or failure

### Step 4: Integrate CRM update into main() flow
- In `adw_meeting_pipeline_iso.py` `main()`, after `save_meeting_outputs()` and before `generate_markdown_summary()`:
  - Call `update_crm(meeting_data, transcript_path, adw_id, logger)`
  - Wrap in try/except to ensure CRM failures don't block the rest of the pipeline
- The pipeline should still commit and push the markdown summary regardless of CRM update outcome

### Step 5: Write unit tests for CRM API client
- In `adws/adw_tests/test_meeting_pipeline.py`, add tests for `CrmApiClient`:
  - `test_crm_client_authenticate_success` — mock `requests.post` to return 200 with token, verify `_token` is set
  - `test_crm_client_authenticate_failure` — mock `requests.post` to return 401, verify returns `False`
  - `test_crm_client_search_prospect_found` — mock `requests.get` to return prospect list with matching company, verify match returned
  - `test_crm_client_search_prospect_not_found` — mock `requests.get` to return empty list, verify `None` returned
  - `test_crm_client_search_prospect_case_insensitive` — mock with different casing, verify match still works
  - `test_crm_client_create_prospect_success` — mock `requests.post` to return 201, verify dict returned
  - `test_crm_client_create_meeting_record_success` — mock `requests.post` to return 201, verify dict returned
  - `test_crm_client_advance_stage_success` — mock `requests.patch` to return 200, verify dict returned
  - `test_crm_client_request_timeout` — mock `requests.post` to raise `requests.Timeout`, verify graceful handling

### Step 6: Write unit tests for update_crm function
- In `adws/adw_tests/test_meeting_pipeline.py`, add tests for `update_crm`:
  - `test_update_crm_skips_when_env_vars_missing` — no env vars set, verify function returns without API calls
  - `test_update_crm_skips_when_no_company_name` — meeting data without `company_name`, verify function returns after auth
  - `test_update_crm_creates_new_prospect_and_meeting` — mock full flow: auth → search (no match) → create prospect → create meeting record
  - `test_update_crm_matches_existing_prospect` — mock full flow: auth → search (match found) → create meeting record (no new prospect)
  - `test_update_crm_advances_lead_to_contacted` — mock prospect with stage "lead", verify `advance_prospect_stage` called
  - `test_update_crm_does_not_advance_non_lead` — mock prospect with stage "qualified", verify `advance_prospect_stage` NOT called
  - `test_update_crm_handles_api_failure_gracefully` — mock `authenticate` to fail, verify no exception raised

### Step 7: Run validation commands
- Run all validation commands below to ensure zero regressions.

## Testing Strategy
### Unit Tests
- **CrmApiClient methods**: Each public method tested with mocked `requests` responses for success, failure, and timeout scenarios.
- **update_crm function**: Tested with mocked CrmApiClient for all code paths: missing env vars, missing company name, new prospect, existing prospect, stage advancement, API failures.
- **Pipeline integration**: Existing tests remain passing; `main()` tests still work since CRM env vars won't be set in test environment (graceful skip).

### Edge Cases
- Missing `company_name` in transcript JSON — CRM update skipped with warning, pipeline continues.
- Missing `contact_email` / `contact_name` — prospect created with only `company_name`, meeting record created with available fields.
- Backend API unreachable — CRM update logs error and returns, pipeline continues with commit/push.
- JWT token expired mid-flow — requests fail with 401, logged as error, no retry (single-run pipeline).
- Service account env vars not configured — CRM update skipped entirely with informative warning.
- Prospect search returns multiple matches — first match used (ordered by `created_at.desc()`).
- Meeting date is `null` in transcript JSON — meeting record created without date.
- Duplicate pipeline run for same transcript — creates a second meeting record (idempotency not required; each processing is a unique event).

## Acceptance Criteria
- `adw_meeting_pipeline_iso.py` calls the backend API to create/match a prospect and create a meeting record after processing a transcript.
- When `company_name` is present in the transcript JSON and service account env vars are set, a prospect is found or created.
- A meeting record is created for every successfully processed transcript, linked to the matched/created prospect.
- Prospects at "lead" stage are automatically advanced to "contacted" when a meeting is processed.
- CRM update failures (missing env vars, API errors, network issues) do NOT cause the pipeline to exit non-zero — the pipeline still commits and pushes the markdown summary.
- All existing tests pass without modification.
- New unit tests cover all CRM API client methods and update_crm code paths.
- `CrmApiClient` is in its own module (`adws/adw_modules/crm_api_client.py`) following Clean Architecture separation.

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd adws && uv run pytest adw_tests/test_meeting_pipeline.py -v` — Run meeting pipeline tests including new CRM update tests
- `cd apps/Server && uv run pytest` — Run Server tests to validate no regressions
- `cd apps/Client && npm run tsc --noEmit` — Run Client type check to validate no regressions
- `cd apps/Client && npm run build` — Run Client build to validate no regressions

## Notes
- **New dependency**: `requests` added to the inline script dependencies in `adw_meeting_pipeline_iso.py`. No global project dependency changes needed since `uv run` resolves inline deps.
- **Environment variables**: Four new env vars needed for CRM integration: `ADW_API_BASE_URL`, `ADW_SERVICE_EMAIL`, `ADW_SERVICE_PASSWORD`, `ADW_ENTITY_ID`. These should be added to the `.env` file or set in the environment where the pipeline runs.
- **No backend changes**: This feature only modifies ADW pipeline code. All backend API endpoints already exist and are unchanged.
- **No frontend changes**: This feature is purely backend pipeline logic.
- **Stage advancement logic**: Only advances from "lead" to "contacted". More sophisticated stage logic (e.g., tracking multiple meetings, advancing further) is deferred to future requirements.
- **Prospect matching**: Uses case-insensitive company name comparison. A more robust fuzzy matching strategy could be added later if needed.
- **Security**: Service account credentials are read from environment variables, never hardcoded. The JWT token is held only in memory for the duration of the pipeline run.
