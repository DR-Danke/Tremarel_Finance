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
Cron-based ADW trigger system that monitors GitHub issues and automatically processes them.

This script polls GitHub every 20 seconds to detect issues where 'adw_run' appears
in the issue body or as a comment. Only explicit 'adw_run' triggers processing.

When a qualifying issue is found, it triggers the ADW SDLC workflow.
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Set, Optional

import schedule
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from adw_modules.utils import get_safe_subprocess_env

from adw_modules.github import fetch_open_issues, fetch_issue_comments, get_repo_url, extract_repo_path

# Load environment variables from current or parent directories
load_dotenv()

# Optional environment variables
GITHUB_PAT = os.getenv("GITHUB_PAT")

# Get repository URL from git remote
try:
    GITHUB_REPO_URL = get_repo_url()
    REPO_PATH = extract_repo_path(GITHUB_REPO_URL)
except ValueError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# Track processed issues
processed_issues: Set[int] = set()
# Track issues with their last processed comment ID
issue_last_comment: Dict[int, Optional[int]] = {}
# Track running workflow processes (issue_number -> Popen)
running_workflows: Dict[int, subprocess.Popen] = {}

# Graceful shutdown flag
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global shutdown_requested
    print(f"\nINFO: Received signal {signum}, initiating graceful shutdown...")
    shutdown_requested = True


def should_process_issue(issue_number: int, issue_body: str) -> Optional[str]:
    """Determine if an issue should be processed based on 'adw_run' in body or comments.

    Returns the workflow name to trigger, or None if the issue should not be processed.
    Only triggers when 'adw_run' (or 'adw run') appears in the issue body or as a comment.
    """
    # Check if 'adw_run' appears in the issue body
    body_lower = (issue_body or "").lower().strip()
    if "adw_run" in body_lower or "adw run" in body_lower:
        # Only trigger once per issue — skip if already processed
        if issue_number in processed_issues:
            return None
        print(f"INFO: Issue #{issue_number} - 'adw_run' found in issue body - marking for adw_sdlc_iso")
        return "adw_sdlc_iso"

    # Check comments for 'adw_run'
    comments = fetch_issue_comments(REPO_PATH, issue_number)

    if not comments:
        return None

    # Get the latest comment
    latest_comment = comments[-1]
    comment_body = latest_comment.get("body", "").lower().strip()
    comment_id = latest_comment.get("id")

    # Check if we've already processed this comment
    last_processed_comment = issue_last_comment.get(issue_number)
    if last_processed_comment == comment_id:
        return None

    # Check if latest comment contains 'adw_run' or 'adw run'
    if "adw_run" in comment_body or "adw run" in comment_body:
        print(f"INFO: Issue #{issue_number} - 'adw_run' found in latest comment - marking for adw_sdlc_iso")
        issue_last_comment[issue_number] = comment_id
        return "adw_sdlc_iso"

    return None


def trigger_adw_workflow(issue_number: int, workflow: str = "adw_plan_build_iso") -> bool:
    """Trigger an ADW workflow for a specific issue (non-blocking).

    Launches the workflow as a background process so the cron trigger
    can continue polling and pick up other issues concurrently.
    """
    try:
        script_path = Path(__file__).parent.parent / f"{workflow}.py"

        print(f"INFO: Triggering ADW workflow '{workflow}' for issue #{issue_number}")

        cmd = [sys.executable, str(script_path), str(issue_number)]

        # Get project root for log directory
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / "agents" / f"cron_issue_{issue_number}"
        log_dir.mkdir(parents=True, exist_ok=True)

        stdout_log = open(log_dir / "stdout.log", "w")
        stderr_log = open(log_dir / "stderr.log", "w")

        # Launch as non-blocking background process so the cron loop keeps polling
        process = subprocess.Popen(
            cmd,
            stdout=stdout_log,
            stderr=stderr_log,
            cwd=script_path.parent,
            env=get_safe_subprocess_env(),
        )

        # Track the running process
        running_workflows[issue_number] = process
        print(f"INFO: Launched workflow for issue #{issue_number} (PID: {process.pid})")
        return True

    except Exception as e:
        print(f"ERROR: Exception while triggering workflow for issue #{issue_number}: {e}")
        return False


def check_running_workflows():
    """Check on background workflow processes and log completions."""
    completed = []
    for issue_number, process in running_workflows.items():
        retcode = process.poll()
        if retcode is not None:
            if retcode == 0:
                print(f"INFO: Workflow for issue #{issue_number} completed successfully (PID: {process.pid})")
            else:
                print(f"WARNING: Workflow for issue #{issue_number} exited with code {retcode} (PID: {process.pid})")
            completed.append(issue_number)

    for issue_number in completed:
        del running_workflows[issue_number]


def check_and_process_issues():
    """Main function that checks for issues and processes qualifying ones."""
    if shutdown_requested:
        print(f"INFO: Shutdown requested, skipping check cycle")
        return

    # Check on any running background workflows
    check_running_workflows()

    start_time = time.time()
    print(f"INFO: Starting issue check cycle (active workflows: {len(running_workflows)})")
    
    try:
        # Fetch all open issues
        issues = fetch_open_issues(REPO_PATH)
        
        if not issues:
            print(f"INFO: No open issues found")
            return
        
        # Track newly qualified issues as (issue_number, workflow) tuples
        new_qualifying_issues = []

        # Check each issue
        for issue in issues:
            issue_number = issue.number
            if not issue_number:
                continue

            # Skip if already processed in this session
            if issue_number in processed_issues:
                continue

            # Check if issue should be processed (pass body for adw_run detection)
            workflow = should_process_issue(issue_number, issue.body)
            if workflow:
                new_qualifying_issues.append((issue_number, workflow))

        # Process qualifying issues
        if new_qualifying_issues:
            print(f"INFO: Found {len(new_qualifying_issues)} new qualifying issues: {[i for i, _ in new_qualifying_issues]}")

            for issue_number, workflow in new_qualifying_issues:
                if shutdown_requested:
                    print(f"INFO: Shutdown requested, stopping issue processing")
                    break

                # Trigger the workflow
                if trigger_adw_workflow(issue_number, workflow):
                    processed_issues.add(issue_number)
                else:
                    print(f"WARNING: Failed to process issue #{issue_number}, will retry in next cycle")
        else:
            print(f"INFO: No new qualifying issues found")
        
        # Log performance metrics
        cycle_time = time.time() - start_time
        print(f"INFO: Check cycle completed in {cycle_time:.2f} seconds")
        print(f"INFO: Total processed issues in session: {len(processed_issues)}")
        
    except Exception as e:
        print(f"ERROR: Error during check cycle: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point for the cron trigger."""
    print(f"INFO: Starting ADW cron trigger")
    print(f"INFO: Repository: {REPO_PATH}")
    print(f"INFO: Polling interval: 20 seconds")
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Schedule the check function
    schedule.every(20).seconds.do(check_and_process_issues)
    
    # Run initial check immediately
    check_and_process_issues()
    
    # Main loop
    print(f"INFO: Entering main scheduling loop")
    while not shutdown_requested:
        schedule.run_pending()
        time.sleep(1)
    
    print(f"INFO: Shutdown complete")


if __name__ == "__main__":
    # Support --help flag
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print(__doc__)
        print("\nUsage: ./trigger_cron.py")
        print("\nEnvironment variables:")
        print("  GITHUB_PAT - (Optional) GitHub Personal Access Token")
        print("\nThe script will poll GitHub issues every 20 seconds and trigger")
        print("the ADW workflow for qualifying issues.")
        print("\nNote: Repository URL is automatically detected from git remote.")
        sys.exit(0)
    
    main()