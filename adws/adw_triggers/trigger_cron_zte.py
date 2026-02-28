#!/usr/bin/env uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "python-dotenv",
#     "pydantic",
# ]
# ///

"""
Sequential ZTE trigger — processes GitHub issues with 'adw_run' one at a time.

This script scans all open issues for the 'adw_run' keyword (in body or comments),
then processes them sequentially using adw_sdlc_zte_iso.py (Zero Touch Execution).

Behavior:
- Scans once, builds a queue of qualifying issues sorted by issue number (lowest first)
- Processes each issue one at a time (blocking) via adw_sdlc_zte_iso.py
- If any issue fails, the queue halts immediately — no further issues are processed
- After the queue is exhausted (or halted), enters a polling loop checking every
  60 seconds for new 'adw_run' issues to process

Usage:
  uv run adw_triggers/trigger_cron_zte.py
  uv run adw_triggers/trigger_cron_zte.py --once   # Single pass, no polling
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from adw_modules.github import (
    fetch_open_issues,
    fetch_issue_comments,
    get_repo_url,
    extract_repo_path,
    ADW_BOT_IDENTIFIER,
)
from adw_modules.utils import get_safe_subprocess_env

# Load environment variables
load_dotenv()

# Get repository URL from git remote
try:
    GITHUB_REPO_URL = get_repo_url()
    REPO_PATH = extract_repo_path(GITHUB_REPO_URL)
except ValueError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# Polling interval in seconds (only used after initial queue is drained)
POLL_INTERVAL = 60

# Track issues already completed or attempted in this session
completed_issues: Set[int] = set()

# Graceful shutdown flag
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    print(f"\nINFO: Received signal {signum}, initiating graceful shutdown...")
    shutdown_requested = True


def has_adw_run(issue_number: int, issue_body: str) -> bool:
    """Check if 'adw_run' appears in the issue body or any non-bot comment."""
    # Check issue body
    body_lower = (issue_body or "").lower()
    if "adw_run" in body_lower or "adw run" in body_lower:
        return True

    # Check comments
    comments = fetch_issue_comments(REPO_PATH, issue_number)
    for comment in comments:
        comment_body = comment.get("body", "")
        # Skip bot comments
        if ADW_BOT_IDENTIFIER in comment_body:
            continue
        comment_lower = comment_body.lower()
        if "adw_run" in comment_lower or "adw run" in comment_lower:
            return True

    return False


def find_qualifying_issues() -> List[int]:
    """Find all open issues with 'adw_run' that haven't been processed yet.

    Returns issue numbers sorted ascending (lowest first).
    """
    issues = fetch_open_issues(REPO_PATH)
    if not issues:
        return []

    qualifying = []
    for issue in issues:
        if not issue.number:
            continue
        if issue.number in completed_issues:
            continue
        if has_adw_run(issue.number, issue.body):
            qualifying.append(issue.number)

    # Process lowest issue numbers first
    qualifying.sort()
    return qualifying


def run_zte_workflow(issue_number: int) -> bool:
    """Run adw_sdlc_zte_iso.py for a single issue (blocking).

    Returns True if the workflow succeeded, False otherwise.
    """
    script_path = Path(__file__).parent.parent / "adw_sdlc_zte_iso.py"

    print(f"\n{'='*60}")
    print(f"  STARTING ZTE WORKFLOW — Issue #{issue_number}")
    print(f"{'='*60}")

    cmd = [sys.executable, str(script_path), str(issue_number)]

    try:
        result = subprocess.run(
            cmd,
            cwd=script_path.parent,
            env=get_safe_subprocess_env(),
        )

        if result.returncode == 0:
            print(f"\nINFO: Issue #{issue_number} — ZTE completed successfully")
            return True
        else:
            print(f"\nERROR: Issue #{issue_number} — ZTE failed (exit code {result.returncode})")
            return False

    except Exception as e:
        print(f"\nERROR: Issue #{issue_number} — Exception during ZTE: {e}")
        return False


def process_queue(queue: List[int]) -> Tuple[int, Optional[int]]:
    """Process a queue of issues sequentially. Halts on first failure.

    Returns (completed_count, failed_issue_number or None).
    """
    completed_count = 0

    for issue_number in queue:
        if shutdown_requested:
            print(f"INFO: Shutdown requested, halting queue")
            return completed_count, None

        success = run_zte_workflow(issue_number)
        completed_issues.add(issue_number)

        if success:
            completed_count += 1
        else:
            print(f"\nERROR: Halting queue — issue #{issue_number} failed")
            return completed_count, issue_number

    return completed_count, None


def main():
    """Main entry point."""
    once_mode = "--once" in sys.argv

    print(f"INFO: Sequential ZTE Trigger starting")
    print(f"INFO: Repository: {REPO_PATH}")
    print(f"INFO: Workflow: adw_sdlc_zte_iso.py (Zero Touch Execution)")
    print(f"INFO: Mode: {'single pass' if once_mode else f'continuous (poll every {POLL_INTERVAL}s)'}")

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while not shutdown_requested:
        # Scan for qualifying issues
        print(f"\nINFO: Scanning for issues with 'adw_run'...")
        queue = find_qualifying_issues()

        if not queue:
            print(f"INFO: No qualifying issues found")
        else:
            print(f"INFO: Found {len(queue)} issue(s) to process: {queue}")
            completed, failed = process_queue(queue)
            print(f"\nINFO: Queue result — {completed} completed, failed: {failed or 'none'}")

            if failed is not None:
                print(f"ERROR: Stopping — fix issue #{failed} and restart")
                sys.exit(1)

        # Exit if single-pass mode
        if once_mode:
            print(f"INFO: Single-pass mode, exiting")
            break

        # Poll for new issues
        print(f"INFO: Waiting {POLL_INTERVAL}s before next scan...")
        for _ in range(POLL_INTERVAL):
            if shutdown_requested:
                break
            time.sleep(1)

    print(f"INFO: Shutdown complete — processed {len(completed_issues)} issue(s) total")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print(__doc__)
        print("\nUsage: uv run adw_triggers/trigger_cron_zte.py [--once]")
        print("\nFlags:")
        print("  --once    Single pass: process current queue and exit")
        print("\nWithout --once, polls every 60 seconds for new 'adw_run' issues.")
        print("Halts immediately if any issue's ZTE workflow fails.")
        sys.exit(0)

    main()
