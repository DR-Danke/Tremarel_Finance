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
Continuous Improvement Scanner trigger — runs the CI scanner on a schedule.

Launches the adw_continuous_improvement_iso pipeline at configured times, alternating
between technical and ux-business categories.

Usage:
  uv run adw_triggers/trigger_continuous_improvement.py           # Continuous schedule (08:00, 14:00)
  uv run adw_triggers/trigger_continuous_improvement.py --once    # Single scan and exit
  uv run adw_triggers/trigger_continuous_improvement.py --once --category technical
  uv run adw_triggers/trigger_continuous_improvement.py --dry-run # Pass --dry-run to pipeline

Environment variables:
  ADW_CI_SCAN_TIMES       Comma-separated scan times (default: "08:00,14:00")
  ADW_CI_SCAN_CATEGORIES  Comma-separated category rotation (default: "technical,ux-business")
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

# Load environment variables
load_dotenv()

# Configuration
SCAN_TIMES = os.getenv("ADW_CI_SCAN_TIMES", "08:00,14:00").split(",")
SCAN_CATEGORIES = os.getenv("ADW_CI_SCAN_CATEGORIES", "technical,ux-business").split(",")
PIPELINE_SCRIPT = Path(__file__).parent.parent / "adw_continuous_improvement_iso.py"
LOG_DIR = Path(__file__).parent.parent.parent / "agents" / "continuous_improvement_logs"
LOCK_FILE = LOG_DIR / ".scanner.lock"

# Graceful shutdown flag
shutdown_requested = False

# Track which category index to use next (alternates between runs)
category_index = 0


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    print(f"\nINFO: Received signal {signum}, initiating graceful shutdown...")
    shutdown_requested = True


def is_pipeline_running() -> bool:
    """Check if a CI scanner pipeline is already running via lock file."""
    if not LOCK_FILE.exists():
        return False
    try:
        with open(LOCK_FILE, "r") as f:
            data = json.load(f)
        pid = data.get("pid")
        if pid:
            # Check if process is still running
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                # Process not running, stale lock
                LOCK_FILE.unlink(missing_ok=True)
                return False
    except (json.JSONDecodeError, OSError):
        LOCK_FILE.unlink(missing_ok=True)
    return False


def create_lock(pid: int) -> None:
    """Create a lock file with the pipeline PID."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOCK_FILE, "w") as f:
        json.dump({
            "pid": pid,
            "started_at": datetime.now(tz=timezone.utc).isoformat(),
        }, f)


def launch_pipeline(
    category: str | None = None,
    dry_run: bool = False,
    zone: str | None = None,
) -> bool:
    """Launch the CI scanner pipeline as a background subprocess."""
    if shutdown_requested:
        return False

    if is_pipeline_running():
        print("INFO: Pipeline already running, skipping this scheduled run")
        return False

    if not PIPELINE_SCRIPT.exists():
        print(f"ERROR: Pipeline script not found: {PIPELINE_SCRIPT}")
        return False

    # Build command
    cmd = ["uv", "run", str(PIPELINE_SCRIPT)]
    if category:
        cmd.extend(["--category", category])
    if dry_run:
        cmd.append("--dry-run")
    if zone:
        cmd.extend(["--zone", zone])

    # Create log file
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    cat_label = category or "all"
    log_file = LOG_DIR / f"{timestamp}_{cat_label}.log"

    try:
        log_handle = open(log_file, "w")
        process = subprocess.Popen(
            cmd,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(PIPELINE_SCRIPT.parent),
            env=get_safe_subprocess_env(),
        )

        create_lock(process.pid)

        print(f"INFO: CI scanner launched (PID {process.pid})", flush=True)
        print(f"INFO: Category: {category or 'auto'}", flush=True)
        print(f"INFO: Log: {log_file}", flush=True)
        print(f"INFO: Monitor with: tail -f {log_file}", flush=True)
        return True

    except Exception as e:
        print(f"ERROR: Failed to launch pipeline: {e}")
        return False


def scheduled_scan(dry_run: bool = False) -> None:
    """Run a scheduled scan, rotating category each time."""
    global category_index

    if shutdown_requested:
        return

    category = SCAN_CATEGORIES[category_index % len(SCAN_CATEGORIES)]
    category_index += 1

    print(f"INFO: Scheduled scan triggered — category: {category}", flush=True)
    launch_pipeline(category=category, dry_run=dry_run)


def main():
    """Main entry point for the CI scanner trigger."""
    global category_index

    parser = argparse.ArgumentParser(
        description="Continuous Improvement Scanner trigger — schedule-based codebase scanning"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single scan and exit (no continuous scheduling)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Pass --dry-run to the pipeline (skip GitHub issue creation)",
    )
    parser.add_argument(
        "--category",
        type=str,
        choices=["technical", "ux-business"],
        default=None,
        help="Override category for single scan (used with --once)",
    )
    parser.add_argument(
        "--zone",
        type=str,
        default=None,
        help="Override zone selection (used with --once)",
    )
    args = parser.parse_args()

    # Startup banner
    print("=" * 60)
    print("  ADW CONTINUOUS IMPROVEMENT TRIGGER")
    print("=" * 60)
    print(f"  Scan times:    {', '.join(SCAN_TIMES)}")
    print(f"  Categories:    {', '.join(SCAN_CATEGORIES)}")
    print(f"  Pipeline:      {PIPELINE_SCRIPT}")
    print(f"  Log dir:       {LOG_DIR}")
    print(f"  Dry run:       {args.dry_run}")
    print(f"  Mode:          {'single scan' if args.once else 'continuous schedule'}")
    print("=" * 60)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if args.once:
        launch_pipeline(
            category=args.category,
            dry_run=args.dry_run,
            zone=args.zone,
        )
        print("INFO: Single scan launched, exiting trigger")
        return

    # Schedule scans at configured times
    for i, scan_time in enumerate(SCAN_TIMES):
        scan_time = scan_time.strip()
        # Pre-set category_index so each time slot gets a different category
        def make_job(cat_idx: int):
            def job():
                global category_index
                category_index = cat_idx
                scheduled_scan(dry_run=args.dry_run)
            return job

        schedule.every().day.at(scan_time).do(make_job(i))
        expected_cat = SCAN_CATEGORIES[i % len(SCAN_CATEGORIES)]
        print(f"INFO: Scheduled scan at {scan_time} (category rotation starts at: {expected_cat})")

    # Main loop
    print("INFO: Entering main scheduling loop")
    while not shutdown_requested:
        schedule.run_pending()
        time.sleep(30)

    # Cleanup
    LOCK_FILE.unlink(missing_ok=True)
    print("INFO: Shutdown complete")


if __name__ == "__main__":
    main()
