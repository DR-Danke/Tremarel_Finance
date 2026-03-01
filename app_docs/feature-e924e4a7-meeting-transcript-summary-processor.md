# Meeting Transcript Summary Processor

**ADW ID:** e924e4a7
**Date:** 2026-03-01
**Specification:** specs/issue-58-adw-e924e4a7-sdlc_planner-transcript-meeting-summary-processor.md

## Overview

An ADW workflow (`adw_meeting_pipeline_iso.py`) that automatically processes raw meeting transcripts into structured JSON summaries and professionally styled HTML documents. Triggered by the existing folder watcher (`trigger_meeting_transcript_watch.py`), it extracts participants, discussion points, action items, decisions, and next steps using LLM processing. Implements REQ-012 from the meeting processing CRM pipeline PRD.

## What Was Built

- `adw_meeting_pipeline_iso.py` — Entry-point ADW workflow script for meeting transcript processing
- `/process_meeting_transcript` slash command template for LLM-based extraction
- Unit tests covering CLI validation, JSON parsing, slug generation, and markdown summary generation
- Type system registration (SlashCommand, ADWWorkflow, SLASH_COMMAND_MODEL_MAP)
- Documentation updates to `classify_adw.md` and `adws/README.md`

## Technical Implementation

### Files Modified

- `adws/adw_meeting_pipeline_iso.py`: New 405-line workflow script — reads transcripts (.md/.pdf), executes LLM slash command, parses output, saves JSON/HTML/markdown outputs, commits and pushes from worktree
- `.claude/commands/process_meeting_transcript.md`: New slash command template instructing the LLM to extract meeting metadata, participants, discussion points, action items, decisions, next steps, and generate an inline-CSS HTML document
- `adws/adw_tests/test_meeting_pipeline.py`: 214 lines of unit tests covering `slugify()`, `parse_meeting_json()`, `generate_markdown_summary()`, `save_meeting_outputs()`, and CLI argument validation
- `adws/adw_modules/data_types.py`: Added `"adw_meeting_pipeline_iso"` to `ADWWorkflow` Literal and `"/process_meeting_transcript"` to `SlashCommand` Literal
- `adws/adw_modules/agent.py`: Registered `"/process_meeting_transcript"` in `SLASH_COMMAND_MODEL_MAP` with opus model
- `.claude/commands/classify_adw.md`: Added `/adw_meeting_pipeline_iso` to the workflow command list
- `adws/README.md`: Added documentation section for `adw_meeting_pipeline_iso.py` and quick start entry

### Key Changes

- **Transcript reading**: Supports `.md` (plain text read) and `.pdf` (text extraction via PyMuPDF/fitz) input formats
- **LLM processing**: Uses `execute_template()` with an `AgentTemplateRequest` to invoke the `/process_meeting_transcript` slash command, which returns structured JSON with all meeting data fields
- **Output parsing**: `parse_meeting_json()` handles JSON wrapped in markdown code fences, raw JSON, and JSON embedded in surrounding text
- **Triple output**: Saves structured JSON + HTML to `agents/{adw_id}/meeting_outputs/` and a markdown summary to `ai_docs/meeting-summaries/` in the worktree
- **Worktree isolation**: Follows the established entry-point pattern — creates isolated git worktree, commits summary, and pushes the branch

## How to Use

1. Place a meeting transcript file (`.md` or `.pdf`) in a known location
2. Run the pipeline directly:
   ```bash
   cd adws
   uv run adw_meeting_pipeline_iso.py /path/to/transcript.md [optional-adw-id]
   ```
3. Or let the folder watcher trigger it automatically by dropping a transcript into `External_Requirements/meeting_transcripts/`
4. On success, the script prints `SUCCESS: Meeting summary generated at <path>`
5. Find outputs in:
   - `agents/{adw_id}/meeting_outputs/meeting-{adw_id}-summary.json` — structured meeting data
   - `agents/{adw_id}/meeting_outputs/meeting-{adw_id}-summary.html` — styled HTML for sharing
   - `ai_docs/meeting-summaries/meeting-{adw_id}-{slug}.md` — markdown summary committed to the worktree branch

## Configuration

- No additional environment variables required beyond the standard ADW setup (validated by `check_env_vars()`)
- Inline `uv run` dependencies: `python-dotenv`, `pydantic`, `PyMuPDF`
- Uses opus model for LLM processing (configured in `SLASH_COMMAND_MODEL_MAP`)

## Testing

Run the unit tests:
```bash
cd adws && uv run pytest adw_tests/test_meeting_pipeline.py -v
```

Test cases cover:
- `slugify()` — basic text, special characters, Spanish accents, truncation, empty input
- `parse_meeting_json()` — valid JSON, code-fenced JSON, partial fields, invalid JSON, embedded JSON
- `generate_markdown_summary()` — full data and minimal/null data
- `save_meeting_outputs()` — JSON and HTML file creation at correct paths
- CLI validation — missing args, nonexistent file, unsupported extension

## Notes

- This implements REQ-012 (standalone processor) from the meeting processing CRM pipeline PRD. REQ-013 (CRM update) and REQ-014 (GitHub issue generation) are handled in subsequent issues.
- The structured JSON output aligns with `MeetingRecordCreateDTO` fields to facilitate future CRM integration.
- The script name matches the path referenced in `trigger_meeting_transcript_watch.py` at line 185.
- HTML output uses inline CSS (no external dependencies) — fully self-contained for email sharing.
