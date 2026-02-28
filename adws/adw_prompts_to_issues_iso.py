#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Prompts to Issues Iso - AI Developer Workflow for creating GitHub issues from prompts

Usage:
  uv run adw_prompts_to_issues_iso.py <prompts-path> [adw-id]

Workflow:
1. Validate prompts file exists
2. Validate gh CLI is authenticated
3. Load or create ADW state
4. Create or reuse worktree for isolated execution
5. Execute /prompts_to_issues slash command via execute_template()
6. Parse output to capture created issue numbers and summary table
7. Post summary to GitHub tracking issue or print to console
8. Update state with created issue numbers
9. Log outputs to agents/{adw_id}/issue_creator/

This is the final stage of the ADW Requirements Pipeline (Wave 2).
Converts implementation prompts into trackable GitHub issues.
"""

import sys
import os
import re
import logging
import json
import subprocess
import shutil
from typing import Optional, List
from dotenv import load_dotenv

from adw_modules.state import ADWState
from adw_modules.github import make_issue_comment, get_repo_url, extract_repo_path
from adw_modules.workflow_ops import ensure_adw_id, format_issue_message
from adw_modules.utils import setup_logger, check_env_vars
from adw_modules.data_types import AgentTemplateRequest
from adw_modules.agent import execute_template
from adw_modules.worktree_ops import (
    create_worktree,
    validate_worktree,
    get_ports_for_adw,
    is_port_available,
    find_next_available_ports,
    setup_worktree_environment,
)


AGENT_NAME = "issue_creator"


def check_gh_authenticated() -> bool:
    """Check if gh CLI is authenticated via 'gh auth status'. Returns True if authenticated."""
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def parse_issue_numbers(output: str) -> List[str]:
    """Extract issue numbers (#NNN) from command output."""
    return re.findall(r"#(\d+)", output)


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()

    # Parse command line args
    if len(sys.argv) < 2:
        print("Usage: uv run adw_prompts_to_issues_iso.py <prompts-path> [adw-id]")
        sys.exit(1)

    prompts_path = sys.argv[1]
    adw_id = sys.argv[2] if len(sys.argv) > 2 else None

    # --- Validation block ---

    # Check prompts file exists
    if not os.path.exists(prompts_path):
        print(f"ERROR: Prompts file not found: {prompts_path}")
        sys.exit(1)

    # Make path absolute for later use
    prompts_path = os.path.abspath(prompts_path)

    # Check gh CLI is authenticated
    if not check_gh_authenticated():
        print("ERROR: gh CLI is not authenticated. Run 'gh auth login' first.")
        sys.exit(1)

    # --- State management ---

    # Use a placeholder issue number for ensure_adw_id since this workflow
    # doesn't necessarily have a GitHub issue to track
    placeholder_issue = "pipeline"
    temp_logger = setup_logger(adw_id, "adw_prompts_to_issues_iso") if adw_id else None
    adw_id = ensure_adw_id(placeholder_issue, adw_id, temp_logger)

    # Load the state that was created/found by ensure_adw_id
    state = ADWState.load(adw_id, temp_logger)

    # Ensure state has the adw_id field
    if not state.get("adw_id"):
        state.update(adw_id=adw_id)

    # Track that this ADW workflow has run
    state.append_adw_id("adw_prompts_to_issues_iso")

    # Set up logger with ADW ID
    logger = setup_logger(adw_id, "adw_prompts_to_issues_iso")
    logger.info(f"ADW Prompts to Issues Iso starting - ID: {adw_id}, Prompts: {prompts_path}")

    # Validate environment
    check_env_vars(logger)

    # --- Worktree handling ---

    valid, error = validate_worktree(adw_id, state)
    if valid:
        logger.info(f"Using existing worktree for {adw_id}")
        worktree_path = state.get("worktree_path")
        server_port = state.get("server_port")
        client_port = state.get("client_port")
    else:
        # Allocate ports for this instance
        server_port, client_port = get_ports_for_adw(adw_id)

        # Check port availability
        if not (is_port_available(server_port) and is_port_available(client_port)):
            logger.warning(f"Deterministic ports {server_port}/{client_port} are in use, finding alternatives")
            server_port, client_port = find_next_available_ports(adw_id)

        logger.info(f"Allocated ports - Server: {server_port}, Client: {client_port}")
        state.update(server_port=server_port, client_port=client_port)
        state.save("adw_prompts_to_issues_iso")

        # Create branch name for the worktree
        branch_name = f"pipeline-prompts-to-issues-{adw_id}"
        state.update(branch_name=branch_name)
        state.save("adw_prompts_to_issues_iso")

        # Create worktree
        logger.info(f"Creating worktree for {adw_id}")
        worktree_path, wt_error = create_worktree(adw_id, branch_name, logger)

        if wt_error:
            logger.error(f"Error creating worktree: {wt_error}")
            sys.exit(1)

        state.update(worktree_path=worktree_path)
        state.save("adw_prompts_to_issues_iso")
        logger.info(f"Created worktree at {worktree_path}")

        # Setup worktree environment
        setup_worktree_environment(worktree_path, server_port, client_port, logger)

    # Copy prompts file into worktree if not already there
    prompts_filename = os.path.basename(prompts_path)
    worktree_prompts_path = os.path.join(worktree_path, prompts_filename)
    if not os.path.exists(worktree_prompts_path):
        shutil.copy2(prompts_path, worktree_prompts_path)
        logger.info(f"Copied prompts file to worktree: {worktree_prompts_path}")

    # --- Slash command execution ---

    logger.info("Executing /prompts_to_issues slash command")
    request = AgentTemplateRequest(
        agent_name=AGENT_NAME,
        slash_command="/prompts_to_issues",
        args=[worktree_prompts_path],
        adw_id=adw_id,
        working_dir=worktree_path,
    )

    response = execute_template(request)

    # --- Output parsing ---

    # Check for "Unknown skill" even on success — Claude returns success=true
    # but with "Unknown skill: prompts_to_issues" when the slash command doesn't exist
    if "unknown skill" in response.output.lower():
        logger.error(f"Slash command not found: {response.output}")
        print(
            "ERROR: /prompts_to_issues slash command not found. "
            "Create .claude/commands/prompts_to_issues.md first."
        )
        state.save("adw_prompts_to_issues_iso")
        sys.exit(1)

    if not response.success:
        logger.error(f"Error executing /prompts_to_issues: {response.output}")

        # Check if this is because the slash command doesn't exist yet
        if "prompts_to_issues" in response.output.lower() and (
            "not found" in response.output.lower()
            or "no such" in response.output.lower()
            or "unknown" in response.output.lower()
        ):
            logger.error(
                "The /prompts_to_issues slash command does not exist yet. "
                "Create .claude/commands/prompts_to_issues.md first."
            )
            print(
                "ERROR: /prompts_to_issues slash command not found. "
                "Create .claude/commands/prompts_to_issues.md first."
            )

        # Report to tracking issue if exists
        tracking_issue = state.get("issue_number")
        if tracking_issue and tracking_issue != "pipeline":
            make_issue_comment(
                tracking_issue,
                format_issue_message(
                    adw_id, AGENT_NAME,
                    f"❌ Error executing /prompts_to_issues: {response.output}"
                ),
            )

        state.save("adw_prompts_to_issues_iso")
        sys.exit(1)

    # Parse created issue numbers from output
    output = response.output
    created_issues = parse_issue_numbers(output)
    logger.info(f"Parsed {len(created_issues)} issue numbers from output")

    # --- Reporting ---

    tracking_issue = state.get("issue_number")

    # Build summary message
    summary = f"## Prompts to Issues Summary\n\n"
    summary += f"**ADW ID:** {adw_id}\n"
    summary += f"**Prompts File:** {prompts_filename}\n"
    summary += f"**Issues Created:** {len(created_issues)}\n\n"

    if created_issues:
        summary += "**Created Issues:**\n"
        for issue_num in created_issues:
            summary += f"- #{issue_num}\n"
        summary += "\n"

    # Include raw output summary (truncated if needed)
    if len(output) <= 2000:
        summary += f"### Agent Output\n```\n{output}\n```\n"
    else:
        summary += f"### Agent Output (truncated)\n```\n{output[:2000]}...\n```\n"

    # Post to tracking issue or print to console
    if tracking_issue and tracking_issue != "pipeline":
        make_issue_comment(
            tracking_issue,
            format_issue_message(adw_id, AGENT_NAME, summary),
        )
        logger.info(f"Posted summary to tracking issue #{tracking_issue}")
    else:
        print(summary)

    # --- State update ---

    # Store created issue numbers in state
    state.data["created_issues"] = created_issues
    state.save("adw_prompts_to_issues_iso")

    # --- Final output ---

    print(f"\nSUCCESS: Created {len(created_issues)} GitHub issues from prompts document")
    if created_issues:
        print(f"Issues: {', '.join(f'#{n}' for n in created_issues)}")

    logger.info(f"ADW Prompts to Issues Iso completed - created {len(created_issues)} issues")


if __name__ == "__main__":
    main()
