# Meeting Transcript Folder Watcher

**ADW ID:** 9d184498
**Date:** 2026-03-01
**Specification:** specs/issue-57-adw-9d184498-sdlc_planner-meeting-transcript-watcher.md

## Overview

A new ADW trigger script that monitors `External_Requirements/meeting_transcripts/` for new `.md` and `.pdf` meeting transcript files. When new or modified files are detected, it triggers the meeting processing pipeline (`adw_meeting_pipeline_iso.py`) as a non-blocking subprocess, converting transcripts into CRM meeting records automatically.

## What Was Built

- **Meeting transcript watcher script** (`trigger_meeting_transcript_watch.py`) — polls a folder for new/modified transcript files and launches the meeting pipeline
- **Watched folder with README** (`External_Requirements/meeting_transcripts/`) — dedicated drop folder for meeting transcripts
- **Unit test suite** (13 tests) — validates file detection, processed-log persistence, change detection, pipeline triggering, and signal handling
- **ADW README documentation** — new section documenting the trigger's usage, CLI flags, and environment variables

## Technical Implementation

### Files Modified

- `adws/adw_triggers/trigger_meeting_transcript_watch.py`: New watcher script (286 lines) following the existing `trigger_transcript_watch.py` pattern
- `External_Requirements/meeting_transcripts/README.md`: New README explaining the watched folder purpose and workflow
- `adws/adw_tests/test_meeting_transcript_watch.py`: New unit test file (211 lines) with 13 test cases
- `adws/README.md`: Added Quick Start command and Automation Triggers documentation section

### Key Changes

- **Polling-based file detection**: Uses `schedule` library to poll every 30 seconds (configurable via `ADW_MEETING_TRANSCRIPT_POLL_INTERVAL`), scanning for `.md` and `.pdf` files while skipping dotfiles and `README.md`
- **Mtime-based change detection**: Tracks processed files in `agents/meeting_transcript_watch_processed.json` with file modification timestamps; automatically re-processes files when their mtime changes
- **Non-blocking pipeline launch**: Uses `subprocess.Popen` to trigger `adw_meeting_pipeline_iso.py` in the background, writing output to timestamped log files in `agents/meeting_pipeline_logs/`
- **Graceful degradation**: Handles missing pipeline script (returns False with error message), missing/corrupt processed log (starts fresh), and missing watched folder (auto-creates it)
- **Signal handling**: Registers SIGINT/SIGTERM handlers for graceful shutdown, checking the `shutdown_requested` flag between file processing iterations

## How to Use

1. Place a `.md` or `.pdf` meeting transcript file in `External_Requirements/meeting_transcripts/`
2. Start the watcher in continuous mode:
   ```bash
   cd adws && uv run adw_triggers/trigger_meeting_transcript_watch.py
   ```
3. The watcher detects the file on its next polling cycle and launches the meeting pipeline
4. Monitor pipeline progress via log files in `agents/meeting_pipeline_logs/`
5. To run a single check without continuous polling:
   ```bash
   cd adws && uv run adw_triggers/trigger_meeting_transcript_watch.py --once
   ```
6. To override the watched folder:
   ```bash
   cd adws && uv run adw_triggers/trigger_meeting_transcript_watch.py --folder /path/to/transcripts
   ```

## Configuration

| Setting | Environment Variable | Default |
|---------|---------------------|---------|
| Watched folder | `ADW_MEETING_TRANSCRIPT_FOLDER` | `External_Requirements/meeting_transcripts/` |
| Poll interval | `ADW_MEETING_TRANSCRIPT_POLL_INTERVAL` | `30` seconds |

Other paths (not configurable):
- Processed log: `agents/meeting_transcript_watch_processed.json`
- Pipeline logs: `agents/meeting_pipeline_logs/`
- Pipeline script: `adws/adw_meeting_pipeline_iso.py` (created by CRM-012)

## Testing

Run unit tests:
```bash
cd adws && uv run python -m pytest adw_tests/test_meeting_transcript_watch.py -v
```

Test coverage includes:
- `load_processed_log` — missing file, valid file, corrupt JSON
- `save_processed_log` — parent directory creation, valid JSON output
- `is_processed` — new files, already-processed files, modified files (mtime change)
- `mark_processed` — metadata recording (processed_at, adw_id, file_size, file_mtime)
- `check_transcript_folder` — file detection (.md/.pdf), dotfile/README skipping, missing folder creation, empty folder, shutdown respect
- `trigger_pipeline` — missing pipeline script handling
- `signal_handler` — shutdown flag setting

## Notes

- The meeting pipeline script (`adw_meeting_pipeline_iso.py`) does not exist yet — it will be created by CRM-012. The watcher gracefully handles this by printing an error and skipping.
- This watcher is intentionally separate from the existing `trigger_transcript_watch.py`, which monitors `External_Requirements/transcripts/` for the requirements pipeline. Each watcher has its own folder, processed log, and pipeline target.
- The watcher uses the same dependencies as the existing trigger (`schedule`, `python-dotenv`, `pydantic`) — no new libraries required.
