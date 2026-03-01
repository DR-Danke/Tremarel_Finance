# Feature: Meeting Transcript Watcher

## Metadata
issue_number: `57`
adw_id: `9d184498`
issue_json: `{"number":57,"title":"[CRM Pipeline] Wave 3: Meeting Transcript Watcher","body":"Create a new transcript watcher that monitors a dedicated folder for meeting transcript files. Similar to the existing trigger_transcript_watch.py, it detects new .md and .pdf files, tracks processed files, and triggers the meeting processing pipeline as a non-blocking subprocess."}`

## Feature Description
Create a new ADW trigger script (`trigger_meeting_transcript_watch.py`) that monitors a dedicated folder (`External_Requirements/meeting_transcripts/`) for new meeting transcript files (.md and .pdf). When new or modified files are detected, the watcher triggers a meeting processing pipeline (`adw_meeting_pipeline_iso.py`) as a non-blocking subprocess. This follows the exact same architectural pattern as the existing `trigger_transcript_watch.py` which monitors `External_Requirements/transcripts/` for requirements pipeline processing.

The key difference: the existing watcher feeds transcripts into the **requirements pipeline** (Transcript → PRD → Prompts → Issues), while this new watcher feeds meeting transcripts into the **meeting processing pipeline** (Transcript → Meeting Record in CRM). The meeting processing pipeline script itself will be built in CRM-012; this issue creates only the watcher that triggers it.

## User Story
As a CRM pipeline operator
I want a file watcher that automatically detects new meeting transcripts in a dedicated folder
So that meeting transcripts are automatically processed into CRM meeting records without manual intervention

## Problem Statement
The CRM pipeline needs an automated way to detect when new meeting transcript files are placed in a designated folder and trigger the meeting processing pipeline. Currently, only the requirements pipeline has a transcript watcher (`trigger_transcript_watch.py`). Meeting transcripts destined for CRM processing need their own watcher with a separate watched folder, separate processed-files tracking, and a separate pipeline target.

## Solution Statement
Create a new trigger script `trigger_meeting_transcript_watch.py` that mirrors the existing `trigger_transcript_watch.py` pattern with these differences:
1. **Watched folder**: `External_Requirements/meeting_transcripts/` (separate from the requirements `transcripts/` folder)
2. **Processed log**: `agents/meeting_transcript_watch_processed.json` (separate tracking)
3. **Pipeline target**: `adw_meeting_pipeline_iso.py` (the meeting processing pipeline, to be built in CRM-012)
4. **Environment variables**: `ADW_MEETING_TRANSCRIPT_FOLDER` and `ADW_MEETING_TRANSCRIPT_POLL_INTERVAL`
5. **Log directory**: `agents/meeting_pipeline_logs/` for pipeline output

The watcher gracefully handles the case where the pipeline script does not yet exist (prints an error and skips), allowing this issue to be developed in parallel with CRM-012.

## Relevant Files
Use these files to implement the feature:

- `adws/adw_triggers/trigger_transcript_watch.py` — The existing transcript watcher to use as the reference pattern. This is the primary template for the new watcher.
- `adws/adw_triggers/__init__.py` — Existing init file for the triggers package.
- `adws/adw_modules/utils.py` — Contains `get_safe_subprocess_env()` used by all triggers for safe subprocess execution.
- `adws/README.md` — ADW system documentation. Must be updated to document the new trigger.
- `.claude/commands/classify_adw.md` — ADW workflow classifier. No changes needed since we're adding a trigger, not an `adw_*.py` workflow.

### New Files
- `adws/adw_triggers/trigger_meeting_transcript_watch.py` — The new meeting transcript watcher script.
- `External_Requirements/meeting_transcripts/README.md` — README explaining the purpose of this folder.
- `adws/adw_tests/test_meeting_transcript_watch.py` — Unit tests for the new watcher.

## Implementation Plan
### Phase 1: Foundation
Set up the watched folder with a README and create the new watcher script following the existing `trigger_transcript_watch.py` pattern exactly, adapting configuration values for meeting transcripts.

### Phase 2: Core Implementation
Implement the watcher with all key behaviors:
- Polling loop with configurable interval
- File detection for .md and .pdf extensions
- Processed-file tracking via JSON log with mtime-based change detection
- Non-blocking subprocess launch of the meeting pipeline
- Pipeline log file creation
- Graceful shutdown via signal handlers
- `--once` and `--folder` CLI flags
- Startup banner with configuration summary

### Phase 3: Integration
- Update the ADW README to document the new trigger
- Add unit tests that validate the watcher's file detection, processed-file tracking, and pipeline triggering logic
- Validate the watcher runs successfully in `--once` mode

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create the watched folder
- Create `External_Requirements/meeting_transcripts/` directory
- Add a `README.md` explaining this folder is monitored by the meeting transcript watcher
- Content should explain: purpose, supported file types (.md, .pdf), and how the watcher processes files

### Step 2: Create the meeting transcript watcher script
- Create `adws/adw_triggers/trigger_meeting_transcript_watch.py`
- Follow the exact pattern of `adws/adw_triggers/trigger_transcript_watch.py`
- Use `#!/usr/bin/env uv run` shebang with inline `# /// script` dependencies (`schedule`, `python-dotenv`, `pydantic`)
- Configuration constants:
  - `TRANSCRIPT_FOLDER`: defaults to `External_Requirements/meeting_transcripts/`, overridable via `ADW_MEETING_TRANSCRIPT_FOLDER`
  - `WATCHED_EXTENSIONS`: `{".md", ".pdf"}`
  - `POLL_INTERVAL`: defaults to `30`, overridable via `ADW_MEETING_TRANSCRIPT_POLL_INTERVAL`
  - `PROCESSED_LOG`: `agents/meeting_transcript_watch_processed.json`
- Implement all functions following the existing watcher:
  - `signal_handler()` — graceful shutdown
  - `load_processed_log()` / `save_processed_log()` — JSON persistence
  - `_get_repo_root()` / `_relative_key()` — path utilities
  - `is_processed()` — mtime-based change detection
  - `mark_processed()` — record file as processed with metadata
  - `check_transcript_folder()` — scan for new/modified files
  - `trigger_pipeline()` — launch `adw_meeting_pipeline_iso.py` via `subprocess.Popen` (non-blocking), write output to `agents/meeting_pipeline_logs/{timestamp}_{stem}.log`
  - `main()` — argparse with `--once` and `--folder`, startup banner, schedule loop
- The `trigger_pipeline()` function must gracefully handle the pipeline script not existing (print error, return False) since CRM-012 will create it
- Import `get_safe_subprocess_env` from `adw_modules.utils`

### Step 3: Create unit tests
- Create `adws/adw_tests/test_meeting_transcript_watch.py`
- Test `load_processed_log()` with missing file, valid file, and corrupt file
- Test `save_processed_log()` creates parent directories and writes valid JSON
- Test `is_processed()` returns False for new files, True for already-processed files, and False for modified files (changed mtime)
- Test `mark_processed()` correctly records metadata (processed_at, adw_id, file_size, file_mtime)
- Test `check_transcript_folder()` finds new .md and .pdf files, skips dotfiles and README.md
- Test `trigger_pipeline()` returns False when pipeline script doesn't exist
- Use `tmp_path` pytest fixture for file system isolation

### Step 4: Update ADW README
- Add a new section under "Automation Triggers" in `adws/README.md` for `trigger_meeting_transcript_watch.py`
- Document: usage command, CLI flags, trigger conditions, pipeline target, environment variables
- Follow the same format as the existing `trigger_transcript_watch.py` documentation section
- Add the `uv run` command to the Quick Start section

### Step 5: Run validation commands
- Run all validation commands listed below to confirm zero regressions

## Testing Strategy
### Unit Tests
- File detection: verify .md and .pdf files are found, dotfiles and README.md are skipped
- Processed log persistence: verify JSON read/write cycle, corrupt file handling, missing file handling
- Change detection: verify mtime-based re-processing (modified files are re-processed)
- Pipeline trigger: verify subprocess.Popen is called correctly, verify graceful handling when pipeline script is missing
- Signal handling: verify shutdown_requested flag is set on SIGINT/SIGTERM
- CLI flags: verify `--once` mode runs single check, `--folder` overrides watched folder

### Edge Cases
- Watched folder does not exist (should be created automatically)
- Processed log file is corrupt JSON (should start fresh with warning)
- Processed log file is missing (should start with empty state)
- Pipeline script does not exist yet (should print error and return False without crashing)
- File is modified after initial processing (should be re-processed based on mtime change)
- Shutdown requested during file processing loop (should stop processing remaining files)
- Empty watched folder (should return silently, no errors)
- Files with spaces or special characters in names (should be handled correctly via Path objects)

## Acceptance Criteria
- [ ] `External_Requirements/meeting_transcripts/` folder exists with a README.md
- [ ] `adws/adw_triggers/trigger_meeting_transcript_watch.py` script exists and is executable
- [ ] Watcher correctly detects new .md and .pdf files in the watched folder
- [ ] Watcher skips dotfiles and README.md
- [ ] Watcher tracks processed files in `agents/meeting_transcript_watch_processed.json`
- [ ] Watcher re-processes files whose mtime has changed
- [ ] Watcher triggers `adw_meeting_pipeline_iso.py` as a non-blocking subprocess
- [ ] Watcher gracefully handles missing pipeline script (prints error, continues)
- [ ] Watcher supports `--once` flag for single-check mode
- [ ] Watcher supports `--folder` flag for custom watched folder path
- [ ] Watcher supports environment variables `ADW_MEETING_TRANSCRIPT_FOLDER` and `ADW_MEETING_TRANSCRIPT_POLL_INTERVAL`
- [ ] Watcher handles graceful shutdown via SIGINT/SIGTERM
- [ ] Pipeline logs are written to `agents/meeting_pipeline_logs/`
- [ ] ADW README documents the new trigger
- [ ] All unit tests pass
- [ ] Watcher runs successfully with `--once` flag

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd adws && uv run python -m pytest adw_tests/test_meeting_transcript_watch.py -v` — Run unit tests for the new meeting transcript watcher
- `cd adws && uv run adw_triggers/trigger_meeting_transcript_watch.py --once` — Verify the watcher runs successfully in single-check mode (should complete without errors)
- `cd adws && uv run python -c "from adw_triggers.trigger_meeting_transcript_watch import load_processed_log, save_processed_log, is_processed, mark_processed; print('All imports successful')"` — Verify all functions are importable
- `ls External_Requirements/meeting_transcripts/README.md` — Verify watched folder and README exist

## Notes
- This watcher is designed to run **in parallel** with CRM-012 (the meeting processing pipeline). The watcher gracefully handles the pipeline script not existing yet.
- The pipeline script path is `adws/adw_meeting_pipeline_iso.py` — CRM-012 will create this file. Until then, `trigger_pipeline()` will print an error and return False.
- The existing `trigger_transcript_watch.py` watches `External_Requirements/transcripts/` and feeds into the **requirements pipeline** (`adw_requirements_pipeline_iso.py`). This new watcher is intentionally separate with its own folder, log, and pipeline target.
- No new libraries are needed — the watcher uses the same dependencies as the existing trigger (`schedule`, `python-dotenv`, `pydantic`).
- CRM-013 (CRM Update Logic) and CRM-014 (GitHub Issue Generation) build on top of the pipeline that CRM-012 creates, which this watcher triggers.
