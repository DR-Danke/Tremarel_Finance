# Feature: Transcript to Structured Meeting Summary Processor

## Metadata
issue_number: `58`
adw_id: `e924e4a7`
issue_json: ``

## Feature Description
Create an ADW workflow script (`adw_meeting_pipeline_iso.py`) that takes a raw meeting transcript file and processes it into a structured meeting summary using AI/LLM. The processor extracts participants, company/prospect identification, discussion points, action items, decisions, and next steps. It also generates a professionally styled HTML document suitable for sharing with prospects/customers. This workflow is triggered by the existing `trigger_meeting_transcript_watch.py` folder watcher (built in issue #57) and outputs structured JSON meeting data plus an HTML summary to `agents/{adw_id}/meeting_outputs/`.

## User Story
As a sales/account manager using the Finance Tracker CRM
I want meeting transcripts to be automatically processed into structured summaries
So that I can quickly review key discussion points, action items, and decisions from client meetings without manually parsing raw transcripts

## Problem Statement
Raw meeting transcripts from tools like Fireflies are unstructured, verbose, and difficult to extract actionable information from. The existing meeting transcript watcher (`trigger_meeting_transcript_watch.py`) detects new transcript files but has no pipeline script to process them — `adw_meeting_pipeline_iso.py` does not yet exist. Without this processor, transcripts sit in the drop folder with no automated processing.

## Solution Statement
Build `adw_meeting_pipeline_iso.py` following the established ADW entry-point workflow pattern (modeled after `adw_transcript_to_prd_iso.py`). The workflow will:
1. Accept a transcript file path as input
2. Create an isolated git worktree
3. Read the transcript content (supporting `.md` and `.pdf`)
4. Execute a new `/process_meeting_transcript` slash command via `execute_template()` to extract structured data using LLM
5. Parse the LLM output into structured JSON (participants, discussion points, action items, decisions, next steps, HTML output)
6. Save outputs to `agents/{adw_id}/meeting_outputs/` (structured JSON + HTML file)
7. Commit and push from the worktree

This is a standalone processor (REQ-012 from the PRD). CRM update logic (REQ-013) and GitHub issue generation (REQ-014) will be added in subsequent issues.

## Relevant Files
Use these files to implement the feature:

- `adws/adw_transcript_to_prd_iso.py` — Primary reference pattern for file-based ADW entry-point workflows. This is the closest analog to what we're building.
- `adws/adw_modules/agent.py` — Contains `execute_template()`, `SLASH_COMMAND_MODEL_MAP`. Must be updated to register the new `/process_meeting_transcript` slash command.
- `adws/adw_modules/data_types.py` — Contains `SlashCommand` Literal type and `ADWWorkflow` Literal type. Must be updated to add the new command and workflow.
- `adws/adw_modules/state.py` — `ADWState` class for loading/saving persistent state.
- `adws/adw_modules/worktree_ops.py` — `create_worktree()`, `validate_worktree()`, `get_ports_for_adw()`, `is_port_available()`, `find_next_available_ports()`.
- `adws/adw_modules/workflow_ops.py` — `ensure_adw_id()` for initializing ADW state.
- `adws/adw_modules/git_ops.py` — `commit_changes()`, `push_branch()` for git operations.
- `adws/adw_modules/utils.py` — `setup_logger()`, `check_env_vars()`, `make_adw_id()`.
- `adws/adw_triggers/trigger_meeting_transcript_watch.py` — The existing watcher that calls `adw_meeting_pipeline_iso.py`. Read to understand the expected interface (script path, CLI args pattern).
- `adws/adw_tests/test_meeting_transcript_watch.py` — Reference for test patterns used in ADW tests.
- `.claude/commands/transcript_to_prd.md` — Reference for how existing slash commands are structured (prompt template pattern).
- `.claude/commands/classify_adw.md` — Must be updated to include the new workflow command.
- `adws/README.md` — Must be updated to document the new workflow.
- `ai_docs/prds/prd-970a89f7-meeting-processing-crm-pipeline.md` — The PRD defining REQ-012 requirements.
- `app_docs/feature-9d184498-meeting-transcript-watcher.md` — Documentation for the watcher feature (for context on expected pipeline interface).
- `app_docs/feature-17ff3ddf-meeting-record-data-model.md` — Documentation for meeting record data model (for context on output structure alignment).

### New Files
- `adws/adw_meeting_pipeline_iso.py` — The main meeting transcript processor workflow script (entry-point, creates worktree).
- `.claude/commands/process_meeting_transcript.md` — New slash command template for LLM-based meeting transcript processing.
- `adws/adw_tests/test_meeting_pipeline.py` — Unit tests for the new pipeline script.

## Implementation Plan
### Phase 1: Foundation
Register the new slash command and workflow in the ADW type system and agent module so the infrastructure recognizes it. Create the slash command template that defines how the LLM should process meeting transcripts.

### Phase 2: Core Implementation
Build the `adw_meeting_pipeline_iso.py` workflow script following the established entry-point pattern. Implement transcript reading (`.md` and `.pdf`), LLM execution via `execute_template()`, output parsing, and file saving to `agents/{adw_id}/meeting_outputs/`.

### Phase 3: Integration
Update documentation (`adws/README.md`, `classify_adw.md`), write unit tests, and validate the full flow from watcher trigger through to structured output generation. Ensure the existing `trigger_meeting_transcript_watch.py` can successfully invoke the new pipeline script.

## Step by Step Tasks

### Step 1: Create the `/process_meeting_transcript` slash command template
- Create `.claude/commands/process_meeting_transcript.md` with a detailed prompt template that instructs the LLM to:
  - Parse the raw meeting transcript provided via `$ARGUMENTS`
  - Extract: meeting title, meeting date, participants (names and roles), company/prospect identification, key discussion points, action items (with owners and deadlines if mentioned), decisions made, next steps, and a 2-4 sentence executive summary
  - Generate a professionally styled inline-CSS HTML document suitable for sending to the prospect
  - Return the output as a structured JSON object wrapped in a code block, with fields: `title`, `meeting_date`, `participants`, `company_name`, `contact_name`, `contact_email`, `summary`, `discussion_points`, `action_items`, `decisions`, `next_steps`, `html_output`
- Follow the same pattern as `.claude/commands/transcript_to_prd.md` — clear instructions, quality rules, explicit output format

### Step 2: Register the new slash command and workflow in ADW types
- In `adws/adw_modules/data_types.py`:
  - Add `"/process_meeting_transcript"` to the `SlashCommand` Literal type
  - Add `"adw_meeting_pipeline_iso"` to the `ADWWorkflow` Literal type
- In `adws/adw_modules/agent.py`:
  - Add `"/process_meeting_transcript": {"base": "opus", "heavy": "opus"}` to `SLASH_COMMAND_MODEL_MAP`

### Step 3: Build `adw_meeting_pipeline_iso.py`
- Create `adws/adw_meeting_pipeline_iso.py` as a `#!/usr/bin/env -S uv run` script with inline dependencies: `python-dotenv`, `pydantic`, `PyMuPDF`
- Follow the exact pattern from `adw_transcript_to_prd_iso.py`:
  1. Parse CLI args: `<transcript-path> [adw-id]`
  2. Validate transcript file exists and has `.md` or `.pdf` extension
  3. Make transcript path absolute
  4. Call `ensure_adw_id("meeting-pipeline", adw_id)` to initialize state
  5. Load `ADWState`, append `"adw_meeting_pipeline_iso"` to workflow history
  6. Set up logger with `setup_logger(adw_id, "adw_meeting_pipeline_iso")`
  7. Call `check_env_vars(logger)` to validate environment
  8. Set branch name to `meeting-pipeline-{adw_id}`
  9. Check/create worktree using `validate_worktree()` / `create_worktree()`
  10. Allocate ports with `get_ports_for_adw()` / `find_next_available_ports()`
  11. Read transcript content: handle `.pdf` via `fitz` (PyMuPDF), `.md` as text
  12. Execute `/process_meeting_transcript` via `execute_template()` with `AgentTemplateRequest`
  13. Parse the LLM response output — expect JSON with meeting data fields
  14. Save structured JSON to `agents/{adw_id}/meeting_outputs/meeting-{adw_id}-summary.json`
  15. Save HTML output to `agents/{adw_id}/meeting_outputs/meeting-{adw_id}-summary.html`
  16. Also save a markdown summary to the worktree at `ai_docs/meeting-summaries/meeting-{adw_id}-{slug}.md`
  17. Commit changes with message: `adw: add meeting summary from transcript ({adw_id})`
  18. Push branch
  19. Save final state
  20. Print `SUCCESS: Meeting summary generated at {output_path}`

### Step 4: Write unit tests for the pipeline
- Create `adws/adw_tests/test_meeting_pipeline.py` following the pattern in `adws/adw_tests/test_meeting_transcript_watch.py`
- Test cases:
  - `test_main_missing_args` — exits with error when no transcript path provided
  - `test_main_nonexistent_file` — exits with error when transcript file does not exist
  - `test_main_unsupported_extension` — exits with error for `.txt` or `.doc` files
  - `test_slugify` — verifies slug generation from meeting titles (reuse the slugify function or import from the script)
  - `test_parse_meeting_json_valid` — verifies JSON output parsing with all expected fields
  - `test_parse_meeting_json_missing_fields` — verifies graceful handling of partial JSON
  - `test_save_meeting_outputs` — verifies files are written to the correct paths in `agents/{adw_id}/meeting_outputs/`
- Use `unittest.mock.patch` for external calls (`execute_template`, `ensure_adw_id`, `create_worktree`, `commit_changes`, `push_branch`)

### Step 5: Update `classify_adw.md` with the new workflow
- Add `/adw_meeting_pipeline_iso` to the list of valid ADW commands in `.claude/commands/classify_adw.md`
- Add a description: "Meeting Pipeline: Process meeting transcript into structured summary and HTML output"

### Step 6: Update `adws/README.md` with documentation
- Add a new section under "Entry Point Workflows" for `adw_meeting_pipeline_iso.py`:
  - Usage: `uv run adw_meeting_pipeline_iso.py <transcript-path> [adw-id]`
  - Description of what it does (accept transcript, process via LLM, generate structured JSON + HTML, commit to worktree)
  - Note that this is a file-based workflow (no GitHub issue required)
  - Note that it is invoked by `trigger_meeting_transcript_watch.py`
- Add `uv run adw_meeting_pipeline_iso.py transcript.md` to the Quick Start section

### Step 7: Run validation commands
- Run all validation commands listed below to ensure zero regressions

## Testing Strategy
### Unit Tests
- Test CLI argument validation (missing args, nonexistent file, unsupported extension)
- Test transcript content reading (mock file reads for `.md` and `.pdf`)
- Test LLM response JSON parsing (valid JSON, malformed JSON, missing fields)
- Test output file creation (correct paths, correct content)
- Test slugify function for meeting title conversion
- All external dependencies (`execute_template`, `ensure_adw_id`, `create_worktree`, `commit_changes`, `push_branch`) must be mocked

### Edge Cases
- Empty transcript file — should proceed with a warning (matching existing pattern)
- PDF with no extractable text — should produce empty content with warning
- LLM returns malformed JSON — should log error and exit with non-zero status
- LLM returns JSON with missing optional fields (e.g., no `contact_email`) — should handle gracefully with None/empty defaults
- Very long transcript content — no truncation, pass full content to LLM
- Transcript in non-English language — LLM should still extract and output in English (matching existing `/transcript_to_prd` behavior)
- Worktree already exists from previous run — should reuse existing worktree
- Port conflict — should find alternative ports using `find_next_available_ports()`

## Acceptance Criteria
- `adw_meeting_pipeline_iso.py` exists and is executable via `uv run`
- The script accepts a raw transcript file (`.md` or `.pdf`) as input via CLI argument
- The script creates an isolated git worktree and processes the transcript via `/process_meeting_transcript` slash command
- The `/process_meeting_transcript` slash command extracts: participants, discussion points, action items, decisions, next steps, company/prospect identification
- Structured JSON output is saved to `agents/{adw_id}/meeting_outputs/meeting-{adw_id}-summary.json`
- Professionally styled HTML document is saved to `agents/{adw_id}/meeting_outputs/meeting-{adw_id}-summary.html`
- A markdown summary is committed to `ai_docs/meeting-summaries/` in the worktree
- Changes are committed and pushed from the worktree
- The script prints `SUCCESS: Meeting summary generated at <path>` on completion (parseable by the watcher/orchestrators)
- `trigger_meeting_transcript_watch.py` can successfully invoke the pipeline script
- `/process_meeting_transcript` is registered in `SlashCommand` Literal, `SLASH_COMMAND_MODEL_MAP`, and `ADWWorkflow` Literal
- `classify_adw.md` includes the new workflow
- `adws/README.md` documents the new workflow
- All unit tests pass
- No regressions in existing tests

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd adws && uv run pytest adw_tests/test_meeting_pipeline.py -v` — Run new unit tests for the meeting pipeline
- `cd adws && uv run pytest adw_tests/ -v` — Run all ADW tests to ensure zero regressions
- `cd adws && python -c "from adw_modules.data_types import SlashCommand, ADWWorkflow; print('SlashCommand and ADWWorkflow types OK')"` — Verify type definitions are valid
- `cd adws && python -c "from adw_modules.agent import SLASH_COMMAND_MODEL_MAP; assert '/process_meeting_transcript' in SLASH_COMMAND_MODEL_MAP; print('Model map OK')"` — Verify slash command is registered in model map
- `test -f adws/adw_meeting_pipeline_iso.py && echo 'Pipeline script exists' || echo 'MISSING'` — Verify pipeline script exists
- `test -f .claude/commands/process_meeting_transcript.md && echo 'Slash command exists' || echo 'MISSING'` — Verify slash command template exists
- `grep -q "adw_meeting_pipeline_iso" .claude/commands/classify_adw.md && echo 'classify_adw updated' || echo 'MISSING'` — Verify classify_adw includes new workflow
- `grep -q "adw_meeting_pipeline_iso" adws/README.md && echo 'README updated' || echo 'MISSING'` — Verify README documents new workflow

## Notes
- This implementation covers REQ-012 from the PRD (`prd-970a89f7-meeting-processing-crm-pipeline.md`). REQ-013 (CRM update logic) and REQ-014 (GitHub issue generation) are handled in subsequent issues.
- The pipeline outputs structured JSON that aligns with the `MeetingRecordCreateDTO` fields (title, summary, action_items, participants, html_output, meeting_date) to facilitate future CRM integration in REQ-013.
- The script name `adw_meeting_pipeline_iso.py` matches the path referenced in `trigger_meeting_transcript_watch.py` at line 185: `pipeline_script = Path(__file__).parent.parent / "adw_meeting_pipeline_iso.py"`.
- No new Python packages are needed beyond what's already in the inline `uv run` dependencies (`python-dotenv`, `pydantic`, `PyMuPDF`).
- The HTML output uses inline CSS styling (no external templates or libraries) — the LLM generates the full HTML document as part of its response.
