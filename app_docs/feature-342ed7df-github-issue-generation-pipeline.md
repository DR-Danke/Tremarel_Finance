# GitHub Issue Generation Pipeline

**ADW ID:** 342ed7df
**Date:** 2026-03-01
**Specification:** specs/issue-60-adw-342ed7df-sdlc_planner-github-issue-generation-pipeline.md

## Overview

Adds automatic GitHub issue generation to the meeting transcript processing pipeline (`adw_meeting_pipeline_iso.py`). After processing a transcript and updating the CRM, the pipeline now creates a GitHub issue summarizing the results — providing an audit trail and enabling follow-up workflows like `adw_sdlc_iso` to pick up unresolved items.

## What Was Built

- Reusable `create_issue()` helper in the shared GitHub module with retry logic and exponential backoff
- `check_gh_authenticated()` consolidated into `adw_modules/github.py` for use across all ADW workflows
- `ensure_labels_exist()` to explicitly manage GitHub labels before issue creation
- `generate_github_issue()` function that builds structured issue bodies with human-readable sections and machine-parseable metadata
- `update_crm()` now returns a structured result dict capturing all CRM operations performed
- Integration into `main()` flow with non-fatal error handling — issue generation failures never break the pipeline

## Technical Implementation

### Files Modified

- `adws/adw_modules/github.py`: Added `check_gh_authenticated()`, `ensure_labels_exist()`, and `create_issue()` functions (+133 lines)
- `adws/adw_meeting_pipeline_iso.py`: Added `generate_github_issue()` function, modified `update_crm()` to return result dict, integrated issue generation into `main()` flow (+199 lines)
- `adws/adw_tests/test_meeting_pipeline.py`: Added 12 new test cases covering all new functions and updated existing CRM tests for return value assertions (+240 lines)

### Key Changes

- **`create_issue()`** wraps `gh issue create` with retry logic (up to 3 attempts with exponential backoff), parses the issue number from the returned URL, and uses `get_github_env()` for token setup
- **`update_crm()` result dict** captures: `success`, `skipped`, `skip_reason`, `prospect_action` (created/matched), `prospect_id`, `prospect_company`, `meeting_record_id`, `stage_advanced`, and `errors` — every return path now populates these fields
- **Issue body structure** includes sections for Meeting Summary, Prospect Information, CRM Update Results, Action Items, Decisions, Next Steps, Pipeline Metadata, and a `<!-- ADW_METADATA: {...} -->` HTML comment block with JSON for downstream parsing
- **Issue title** follows pattern `[Meeting Processed] {title} - {company}` truncated to 100 characters
- **Labels** `meeting-processed` and `adw-generated` are applied to every generated issue

## How to Use

1. Process a meeting transcript through the pipeline as usual (via folder watcher trigger or `/process_meeting_transcript` command)
2. If `gh` CLI is authenticated, the pipeline automatically creates a GitHub issue after the CRM update step
3. The issue number is stored in `adw_state.json` under `generated_issue_number`
4. View generated issues on GitHub filtered by label: `meeting-processed`

No manual intervention required — issue generation is fully automatic when `gh` is available.

## Configuration

- **`gh` CLI**: Must be installed and authenticated (`gh auth login`). If not available, issue generation is silently skipped.
- **No new environment variables**: Uses existing `gh` authentication and git remote configuration.
- **No new dependencies**: All functionality uses Python standard library (`subprocess`, `json`) and the existing `gh` CLI.

## Testing

Run the meeting pipeline tests:

```bash
cd adws && uv run pytest adw_tests/test_meeting_pipeline.py -v
```

Test coverage includes:
- `check_gh_authenticated()`: success, failure, gh-not-installed scenarios
- `ensure_labels_exist()`: verifies `--force` flag usage for each label
- `create_issue()`: success (URL parsing), failure, timeout with retry
- `generate_github_issue()`: success, gh-not-authenticated skip, create failure, minimal data, metadata block JSON validation
- `update_crm()` return values: all existing tests updated to assert structured result dict fields

## Notes

- Issue generation is entirely optional and non-fatal — the pipeline's primary deliverables (JSON/HTML/markdown outputs and CRM updates) are unaffected by failures
- The `<!-- ADW_METADATA: {...} -->` block is invisible in rendered GitHub issues but parseable by downstream ADW workflows
- `check_gh_authenticated()` was consolidated from `adw_prompts_to_issues_iso.py` into the shared module; the original can be updated to import from `adw_modules/github.py` in a future cleanup
- This completes REQ-014 (Wave 3) of the Meeting Processing CRM Pipeline PRD
