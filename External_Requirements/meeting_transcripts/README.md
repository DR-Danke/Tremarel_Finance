# Meeting Transcripts

This folder is monitored by the **Meeting Transcript Watcher** (`adws/adw_triggers/trigger_meeting_transcript_watch.py`).

## Purpose

Place meeting transcript files here to automatically trigger the meeting processing pipeline, which converts transcripts into CRM meeting records.

## Supported File Types

- `.md` — Markdown transcripts
- `.pdf` — PDF transcripts

## How It Works

1. Drop a `.md` or `.pdf` file into this folder
2. The watcher detects the new file during its next polling cycle (default: every 30 seconds)
3. The meeting processing pipeline (`adw_meeting_pipeline_iso.py`) is triggered as a non-blocking subprocess
4. The file is marked as processed in `agents/meeting_transcript_watch_processed.json`
5. Pipeline output is logged to `agents/meeting_pipeline_logs/`

## Notes

- Files starting with `.` (dotfiles) are ignored
- `README.md` is ignored
- Modified files (changed modification time) are automatically re-processed
- The watcher can be run in single-check mode with `--once`
