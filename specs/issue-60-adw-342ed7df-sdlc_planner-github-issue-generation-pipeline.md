# Feature: GitHub Issue Generation for Pipeline Updates

## Metadata
issue_number: `60`
adw_id: `342ed7df`
issue_json: ``

## Feature Description
Add GitHub issue generation to the meeting transcript processing pipeline (`adw_meeting_pipeline_iso.py`). After processing a meeting transcript and updating the CRM, the pipeline will generate a GitHub issue describing the meeting processing results and CRM updates. These issues follow the existing ADW labeling pattern (`meeting-processed`, `adw-generated`) and contain structured data parseable by downstream workflows like `adw_sdlc_iso`. This is the final capability (REQ-014) in the Meeting Processing CRM Pipeline, completing Wave 3.

The generated issue serves two purposes:
1. **Audit trail**: Provides a visible record of every processed meeting transcript and the resulting CRM actions.
2. **Follow-up trigger**: If CRM updates fail or if additional application changes are needed, the issue can be picked up by `adw_sdlc_iso` for automated implementation.

## User Story
As a CRM pipeline operator
I want the meeting pipeline to generate a GitHub issue summarizing processing results
So that I have a traceable record of every transcript processed and can trigger follow-up workflows when manual intervention or additional changes are needed

## Problem Statement
Currently `adw_meeting_pipeline_iso.py` processes transcripts, saves outputs, and updates the CRM, but produces no externally visible record of what happened. If CRM updates fail silently, there is no notification or follow-up mechanism. There is also no way for downstream ADW workflows to discover that a meeting was processed and may need further attention (e.g., implementing new features discussed in the meeting, or retrying failed CRM operations).

## Solution Statement
Add a `generate_github_issue()` function to `adw_meeting_pipeline_iso.py` that runs after both `save_meeting_outputs()` and `update_crm()`. The function will:

1. Check that `gh` CLI is authenticated (reusing pattern from `adw_prompts_to_issues_iso.py`).
2. Build a structured GitHub issue body containing: prospect info, meeting summary, action items, CRM update results, and a machine-parseable JSON metadata block.
3. Create the issue via `gh issue create` with labels `meeting-processed` and `adw-generated`.
4. Store the created issue number in the ADW state.
5. Handle errors gracefully — issue creation failures should log errors but NOT fail the pipeline.

The implementation reuses existing GitHub operations from `adw_modules/github.py` and follows patterns established in `adw_prompts_to_issues_iso.py`.

## Relevant Files
Use these files to implement the feature:

- `adws/adw_meeting_pipeline_iso.py` — Main pipeline script to extend with GitHub issue generation. Primary file to modify.
- `adws/adw_modules/github.py` — Existing GitHub operations module. Contains `get_github_env()`, `get_repo_url()`, `extract_repo_path()`, and `make_issue_comment()`. Will be extended with a `create_issue()` helper function.
- `adws/adw_prompts_to_issues_iso.py` — Reference for GitHub issue creation patterns. Contains `check_gh_authenticated()` and `parse_issue_numbers()` functions. Read-only reference.
- `adws/adw_modules/data_types.py` — ADW type definitions. No changes needed (workflow type already registered).
- `adws/adw_tests/test_meeting_pipeline.py` — Existing test file to extend with issue generation tests.
- `adws/adw_modules/crm_api_client.py` — CRM API client (read-only reference for understanding CRM update results).
- `ai_docs/prds/prd-970a89f7-meeting-processing-crm-pipeline.md` — PRD containing REQ-014 requirements. Read-only reference.
- `app_docs/feature-e924e4a7-meeting-transcript-summary-processor.md` — Transcript processor documentation. Read-only reference.
- `app_docs/feature-a61cf509-crm-update-from-processed-transcript.md` — CRM update documentation. Read-only reference.
- `.claude/commands/classify_adw.md` — ADW workflow classification. Read to verify no changes needed.
- `adws/README.md` — ADW system documentation. Read-only reference for patterns.

### New Files
None. All changes are additions to existing files.

## Implementation Plan
### Phase 1: Foundation
Add a reusable `create_issue()` helper function to `adws/adw_modules/github.py` that wraps `gh issue create` with retry logic, label management, and structured error handling. This mirrors the existing patterns in that module (e.g., `make_issue_comment()` with retries and `get_github_env()` for token setup).

### Phase 2: Core Implementation
Add a `generate_github_issue()` function to `adw_meeting_pipeline_iso.py` that:
- Accepts meeting data, CRM update results (prospect info, success/failure), and pipeline metadata.
- Builds a well-structured issue body with: human-readable summary sections and a machine-parseable `<!-- ADW_METADATA: {...} -->` JSON block.
- Calls the new `create_issue()` helper to create the GitHub issue with appropriate labels.
- Returns the created issue number (or None on failure).

Modify `update_crm()` to return a result dict capturing what happened (prospect found/created, meeting record created, stage advanced, any failures) so this information can be included in the generated issue.

Integrate `generate_github_issue()` into `main()` after the CRM update step.

### Phase 3: Integration
- Write comprehensive unit tests for the new `create_issue()` helper and `generate_github_issue()` function.
- Update the `update_crm()` function to return a structured result dict.
- Run all validation commands to ensure zero regressions.

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Read existing code and documentation
- Read `adws/adw_meeting_pipeline_iso.py` to understand the current pipeline flow
- Read `adws/adw_modules/github.py` to understand existing GitHub operations
- Read `adws/adw_prompts_to_issues_iso.py` for issue creation patterns (especially `check_gh_authenticated()`)
- Read `adws/adw_tests/test_meeting_pipeline.py` for existing test patterns
- Read `adws/adw_modules/crm_api_client.py` to understand CRM update data available
- Read `app_docs/feature-a61cf509-crm-update-from-processed-transcript.md` for CRM update context

### Step 2: Add `create_issue()` helper to `adws/adw_modules/github.py`
- Add a new function `create_issue(title: str, body: str, labels: List[str], repo_path: Optional[str] = None, max_retries: int = 3) -> Optional[str]`:
  - If `repo_path` is not provided, derive it from `get_repo_url()` and `extract_repo_path()`
  - Build `gh issue create` command with `--title`, `--body`, `--repo`, and `--label` flags for each label
  - Use `get_github_env()` for environment setup
  - Implement retry logic with exponential backoff (matching `make_issue_comment()` pattern)
  - Parse the created issue URL from stdout to extract the issue number
  - Return the issue number string on success, `None` on failure
  - Print/log success and failure messages matching existing module conventions
- Add a new function `check_gh_authenticated() -> bool`:
  - Run `gh auth status` and return True if returncode == 0
  - Return False on `FileNotFoundError` (gh not installed) or non-zero exit code
  - This consolidates the pattern from `adw_prompts_to_issues_iso.py` into the shared module
- Add a new function `ensure_labels_exist(labels: List[str], repo_path: Optional[str] = None) -> None`:
  - For each label, run `gh label create <label> --force` to ensure it exists (no-op if exists)
  - Use `get_github_env()` for environment setup
  - Catch and log failures (non-fatal — `gh issue create` can still auto-create labels)

### Step 3: Modify `update_crm()` to return a structured result
- Change `update_crm()` return type from `None` to `dict`
- The result dict should have keys:
  - `"success"`: bool — overall success/failure
  - `"skipped"`: bool — True if CRM update was skipped (missing env vars, no company name)
  - `"skip_reason"`: Optional[str] — reason for skipping
  - `"prospect_action"`: Optional[str] — `"created"`, `"matched"`, or `None`
  - `"prospect_id"`: Optional[str] — ID of the prospect
  - `"prospect_company"`: Optional[str] — company name
  - `"meeting_record_id"`: Optional[str] — ID of the created meeting record
  - `"stage_advanced"`: bool — whether the prospect stage was advanced
  - `"errors"`: List[str] — list of error messages encountered
- Update each return path to return the appropriate result dict
- The outer try/except in `main()` that wraps `update_crm()` should capture the result

### Step 4: Add `generate_github_issue()` function to `adw_meeting_pipeline_iso.py`
- Add import: `from adw_modules.github import create_issue, check_gh_authenticated, ensure_labels_exist, get_repo_url, extract_repo_path`
- Add function `generate_github_issue(meeting_data: dict, crm_result: dict, adw_id: str, transcript_path: str, logger: logging.Logger) -> Optional[str]`:
  - Check `gh` auth via `check_gh_authenticated()` — if not authenticated, log warning and return None
  - Build issue title: `"[Meeting Processed] {meeting_title} - {company_name or 'Unknown'}"` (truncated to 100 chars)
  - Build issue body with these sections:
    - `## Meeting Summary` — title, date, participants
    - `## Prospect Information` — company name, contact name/email, prospect action taken (created/matched)
    - `## CRM Update Results` — success/failure, prospect ID, meeting record ID, stage advanced
    - `## Action Items` — bulleted list from meeting data
    - `## Decisions` — bulleted list from meeting data
    - `## Next Steps` — bulleted list from meeting data
    - `## Pipeline Metadata` — ADW ID, transcript path, processing timestamp
    - A machine-parseable metadata block: `<!-- ADW_METADATA: {"adw_id": "...", "prospect_id": "...", "meeting_record_id": "...", ...} -->`
  - Define labels: `["meeting-processed", "adw-generated"]`
  - Call `ensure_labels_exist(labels)`
  - Call `create_issue(title, body, labels)` and capture the returned issue number
  - If successful, log the issue number and return it
  - If failed, log warning and return None

### Step 5: Integrate into `main()` flow
- In `main()`, capture the CRM update result:
  - Change the `update_crm()` call to capture its return value: `crm_result = update_crm(...)`
  - In the except block, set `crm_result = {"success": False, "skipped": False, "errors": [str(e)]}`
- After the CRM update (and before markdown summary generation), call:
  ```python
  try:
      issue_number = generate_github_issue(meeting_data, crm_result, adw_id, transcript_path, logger)
      if issue_number:
          state.update(generated_issue_number=issue_number)
          state.save("adw_meeting_pipeline_iso")
  except Exception as e:
      logger.error(f"GitHub issue generation failed (non-fatal): {e}")
  ```
- The pipeline should still continue with markdown summary, commit, and push regardless of issue generation outcome

### Step 6: Write unit tests for `create_issue()` in github module
- Create or extend tests (in `adws/adw_tests/test_meeting_pipeline.py` or a new test file) for:
  - `test_create_issue_success` — mock `subprocess.run` returning success with issue URL in stdout, verify issue number extracted
  - `test_create_issue_failure` — mock `subprocess.run` returning non-zero, verify None returned
  - `test_create_issue_timeout_retry` — mock first call timing out, second succeeding, verify retry logic
  - `test_check_gh_authenticated_success` — mock `subprocess.run` returning 0
  - `test_check_gh_authenticated_failure` — mock `subprocess.run` returning non-zero
  - `test_check_gh_authenticated_not_installed` — mock `FileNotFoundError`
  - `test_ensure_labels_exist` — mock `subprocess.run`, verify called for each label

### Step 7: Write unit tests for `generate_github_issue()`
- In `adws/adw_tests/test_meeting_pipeline.py`, add tests:
  - `test_generate_github_issue_success` — mock `check_gh_authenticated` True, `create_issue` returns "99", verify issue number returned and body contains expected sections
  - `test_generate_github_issue_gh_not_authenticated` — mock `check_gh_authenticated` False, verify returns None with warning logged
  - `test_generate_github_issue_create_fails` — mock `create_issue` returns None, verify returns None with warning logged
  - `test_generate_github_issue_minimal_data` — meeting data with only title (no company, no CRM result), verify issue still created with available data
  - `test_generate_github_issue_includes_metadata_block` — verify body contains `<!-- ADW_METADATA:` with correct JSON

### Step 8: Write unit tests for updated `update_crm()` return value
- In `adws/adw_tests/test_meeting_pipeline.py`, update existing `update_crm` tests to check return values:
  - `test_update_crm_skips_when_env_vars_missing` — verify returns `{"success": False, "skipped": True, ...}`
  - `test_update_crm_creates_new_prospect_and_meeting` — verify returns `{"success": True, "prospect_action": "created", ...}`
  - `test_update_crm_matches_existing_prospect` — verify returns `{"success": True, "prospect_action": "matched", ...}`
  - `test_update_crm_handles_api_failure_gracefully` — verify returns `{"success": False, ...}`

### Step 9: Run validation commands
- Run all validation commands below to validate the feature works correctly with zero regressions.

## Testing Strategy
### Unit Tests
- **`create_issue()` helper**: Test with mocked `subprocess.run` for success, failure, timeout/retry, and missing `gh` CLI scenarios.
- **`check_gh_authenticated()`**: Test with mocked subprocess for authenticated, not authenticated, and gh not installed cases.
- **`ensure_labels_exist()`**: Test with mocked subprocess to verify labels are created.
- **`generate_github_issue()`**: Test full body generation with various meeting data shapes, CRM result states, and error scenarios.
- **Updated `update_crm()`**: Existing tests updated to verify the new return value structure while maintaining existing assertion coverage.
- **Integration**: `main()` function tests remain passing since `gh` will not be authenticated in test environment (graceful skip).

### Edge Cases
- `gh` CLI not installed — issue generation skipped with warning, pipeline continues.
- `gh` CLI not authenticated — issue generation skipped with warning, pipeline continues.
- Meeting data with no company name or contact info — issue still created with available data (reduced metadata).
- CRM update skipped (no env vars) — issue still created, noting CRM was skipped.
- CRM update failed — issue created with error details included.
- Network timeout during `gh issue create` — retried up to 3 times with exponential backoff, then skipped.
- Very long meeting summary — issue body truncated or summarized to stay within GitHub issue size limits.
- Duplicate pipeline run — creates a separate issue for each run (no deduplication, each processing is unique).

## Acceptance Criteria
- `adw_meeting_pipeline_iso.py` generates a GitHub issue after processing a transcript and updating the CRM.
- The generated issue includes: meeting summary, prospect info, CRM update results, action items, and machine-parseable metadata.
- The issue is labeled with `meeting-processed` and `adw-generated` labels.
- The issue body contains a `<!-- ADW_METADATA: {...} -->` block with structured JSON data.
- `update_crm()` returns a structured result dict that captures what happened during the CRM update.
- Issue generation failures (missing `gh`, network errors) do NOT cause the pipeline to exit non-zero.
- The pipeline still commits and pushes the markdown summary regardless of issue generation outcome.
- All existing tests pass without modification.
- New unit tests cover: `create_issue()`, `check_gh_authenticated()`, `ensure_labels_exist()`, `generate_github_issue()`, and updated `update_crm()` return values.
- `create_issue()` is a reusable function in `adw_modules/github.py` usable by other workflows.

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd adws && uv run pytest adw_tests/test_meeting_pipeline.py -v` — Run meeting pipeline tests including new issue generation tests
- `cd adws && uv run pytest adw_tests/ -v` — Run all ADW tests to validate no regressions
- `cd apps/Server && uv run pytest` — Run Server tests to validate no regressions
- `cd apps/Client && npm run tsc --noEmit` — Run Client type check to validate no regressions
- `cd apps/Client && npm run build` — Run Client build to validate no regressions

## Notes
- **No new dependencies**: The `gh` CLI is already used extensively in the ADW system. The `subprocess` module is part of Python's standard library. No new pip/uv dependencies needed.
- **No backend changes**: This feature only modifies ADW pipeline code. All backend API endpoints are unchanged.
- **No frontend changes**: This feature is purely backend pipeline logic.
- **Graceful degradation**: Issue generation is entirely optional. The pipeline's primary deliverables (JSON/HTML/markdown outputs and CRM updates) are unaffected by issue generation failures.
- **Label auto-creation**: GitHub's `gh issue create --label` will auto-create labels that don't exist, but `ensure_labels_exist()` provides explicit control over label colors and descriptions.
- **Metadata block format**: The `<!-- ADW_METADATA: {...} -->` HTML comment block is invisible when rendered but parseable by downstream workflows. This follows the pattern used in other ADW-generated content.
- **Issue title truncation**: GitHub allows up to 256 characters for issue titles, but we truncate to 100 for readability.
- **Consolidating `check_gh_authenticated()`**: This function exists in `adw_prompts_to_issues_iso.py` but should be in the shared `adw_modules/github.py` module. The plan adds it there; optionally `adw_prompts_to_issues_iso.py` can be updated to import from the shared module in a future cleanup.
