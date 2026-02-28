#!/usr/bin/env uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "schedule",
#     "python-dotenv",
#     "pydantic",
# ]
# ///

"""
Transcript folder watcher that monitors External_Requirements/transcripts/ for new files.

When a new .md or .pdf transcript file is detected, triggers the ADW requirements pipeline
(adw_requirements_pipeline_iso.py) to process it into PRD → prompts → GitHub issues.

Usage:
  uv run adw_triggers/trigger_transcript_watch.py          # Continuous polling (default 30s)
  uv run adw_triggers/trigger_transcript_watch.py --once   # Single check and exit
  uv run adw_triggers/trigger_transcript_watch.py --folder /path/to/transcripts

Environment variables:
  ADW_TRANSCRIPT_FOLDER         Override watched folder path
  ADW_TRANSCRIPT_POLL_INTERVAL  Override poll interval in seconds (default: 30)
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import schedule
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from adw_modules.utils import get_safe_subprocess_env

# Load environment variables from current or parent directories
load_dotenv()

# Configuration
TRANSCRIPT_FOLDER = os.getenv(
    "ADW_TRANSCRIPT_FOLDER",
    str(Path(__file__).parent.parent.parent / "External_Requirements" / "transcripts"),
)
WATCHED_EXTENSIONS = {".md", ".pdf"}
POLL_INTERVAL = int(os.getenv("ADW_TRANSCRIPT_POLL_INTERVAL", "30"))
PROCESSED_LOG = (
    Path(__file__).parent.parent.parent / "agents" / "transcript_watch_processed.json"
)

# Graceful shutdown flag
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    print(f"\nINFO: Received signal {signum}, initiating graceful shutdown...")
    shutdown_requested = True


def load_processed_log() -> dict:
    """Load the processed files tracking log from disk.

    Returns a dict with a 'processed_files' key mapping relative paths
    to their processing metadata. Returns empty state if file is missing
    or contains invalid JSON.
    """
    try:
        if PROCESSED_LOG.exists():
            with open(PROCESSED_LOG, "r") as f:
                data = json.load(f)
            if isinstance(data, dict) and "processed_files" in data:
                return data
    except (json.JSONDecodeError, OSError) as e:
        print(f"WARNING: Could not read processed log ({e}), starting fresh")
    return {"processed_files": {}}


def save_processed_log(data: dict) -> None:
    """Write the processed files tracking log to disk."""
    PROCESSED_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_LOG, "w") as f:
        json.dump(data, f, indent=2)


def _get_repo_root() -> Path:
    """Return the repository root (three levels up from this script)."""
    return Path(__file__).parent.parent.parent


def _relative_key(filepath: Path) -> str:
    """Return a portable relative path key for the processed log."""
    try:
        return str(filepath.resolve().relative_to(_get_repo_root().resolve()))
    except ValueError:
        return str(filepath)


def is_processed(filepath: Path) -> bool:
    """Check whether a file has already been processed and is unchanged.

    Returns False if the file is not in the log or if its modification
    time has changed (indicating the file was updated).
    """
    data = load_processed_log()
    key = _relative_key(filepath)
    entry = data["processed_files"].get(key)
    if entry is None:
        return False
    # Re-process if the file has been modified since last processing
    current_mtime = datetime.fromtimestamp(
        os.path.getmtime(filepath), tz=timezone.utc
    ).isoformat()
    return entry.get("file_mtime") == current_mtime


def mark_processed(filepath: Path, adw_id: str = "pending") -> None:
    """Record a file as processed in the tracking log."""
    data = load_processed_log()
    key = _relative_key(filepath)
    data["processed_files"][key] = {
        "processed_at": datetime.now(tz=timezone.utc).isoformat(),
        "adw_id": adw_id,
        "file_size": filepath.stat().st_size,
        "file_mtime": datetime.fromtimestamp(
            os.path.getmtime(filepath), tz=timezone.utc
        ).isoformat(),
    }
    save_processed_log(data)


def check_transcript_folder():
    """Scan the watched folder for new or modified transcript files."""
    if shutdown_requested:
        return

    folder = Path(TRANSCRIPT_FOLDER)
    if not folder.exists():
        print(f"WARNING: Watched folder does not exist, creating: {folder}")
        folder.mkdir(parents=True, exist_ok=True)
        return

    new_files: list[Path] = []
    for ext in WATCHED_EXTENSIONS:
        for filepath in folder.glob(f"*{ext}"):
            if filepath.name.startswith("."):
                continue
            if filepath.name == "README.md":
                continue
            if not is_processed(filepath):
                new_files.append(filepath)

    if not new_files:
        return

    print(f"INFO: Found {len(new_files)} new transcript(s):", flush=True)
    for f in new_files:
        print(f"  - {f.name}", flush=True)

    for filepath in new_files:
        if shutdown_requested:
            print("INFO: Shutdown requested, stopping file processing")
            break
        trigger_pipeline(filepath)


def trigger_pipeline(transcript_path: Path) -> bool:
    """Launch the requirements pipeline for a transcript file.

    Uses subprocess.Popen (non-blocking) so the watcher continues
    monitoring while the pipeline runs in the background.
    Stdout and stderr are written to a log file for inspection.
    """
    try:
        print(f"INFO: Triggering pipeline for: {transcript_path.name}")
        pipeline_script = Path(__file__).parent.parent / "adw_requirements_pipeline_iso.py"

        if not pipeline_script.exists():
            print(f"ERROR: Pipeline script not found: {pipeline_script}")
            return False

        # Create a log file for the pipeline output
        log_dir = _get_repo_root() / "agents" / "pipeline_logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
        stem = transcript_path.stem[:60]
        log_file = log_dir / f"{timestamp}_{stem}.log"

        cmd = [sys.executable, str(pipeline_script), str(transcript_path.resolve())]

        log_handle = open(log_file, "w")
        process = subprocess.Popen(
            cmd,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(pipeline_script.parent),
            env=get_safe_subprocess_env(),
        )

        print(f"INFO: Pipeline launched (PID {process.pid}) for {transcript_path.name}", flush=True)
        print(f"INFO: Pipeline log: {log_file}", flush=True)
        print(f"INFO: Monitor with: tail -f {log_file}", flush=True)
        print(f"INFO: ADW ID will appear in the log once the pipeline starts", flush=True)
        mark_processed(transcript_path, adw_id="pending")
        return True

    except Exception as e:
        print(f"ERROR: Failed to trigger pipeline for {transcript_path.name}: {e}")
        return False


def main():
    """Main entry point for the transcript folder watcher."""
    global TRANSCRIPT_FOLDER

    parser = argparse.ArgumentParser(
        description="Watch a folder for new transcript files and trigger the ADW requirements pipeline."
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single check and exit (no continuous polling)",
    )
    parser.add_argument(
        "--folder",
        type=str,
        default=None,
        help="Override the watched folder path",
    )
    args = parser.parse_args()

    if args.folder:
        TRANSCRIPT_FOLDER = args.folder

    # Load existing processed log for stats
    processed_data = load_processed_log()
    processed_count = len(processed_data.get("processed_files", {}))

    # Startup banner
    print("=" * 60)
    print("  ADW TRANSCRIPT FOLDER WATCHER")
    print("=" * 60)
    print(f"  Watched folder:   {TRANSCRIPT_FOLDER}")
    print(f"  File types:       {', '.join(sorted(WATCHED_EXTENSIONS))}")
    print(f"  Poll interval:    {POLL_INTERVAL}s")
    print(f"  Processed log:    {PROCESSED_LOG}")
    print(f"  Previously processed: {processed_count} file(s)")
    print(f"  Mode:             {'single check' if args.once else 'continuous polling'}")
    print("=" * 60)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if args.once:
        check_transcript_folder()
        print("INFO: Single check complete, exiting")
        return

    # Schedule periodic checks
    schedule.every(POLL_INTERVAL).seconds.do(check_transcript_folder)

    # Run initial check immediately
    check_transcript_folder()

    # Main loop
    print("INFO: Entering main polling loop")
    while not shutdown_requested:
        schedule.run_pending()
        time.sleep(1)

    print("INFO: Shutdown complete")


if __name__ == "__main__":
    main()
