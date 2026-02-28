#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW PRD to Prompts Iso - AI Developer Workflow for converting PRDs to implementation prompts

Usage:
  uv run adw_prd_to_prompts_iso.py <prd-path> [adw-id] [--example <example-prompts-path>]

Workflow:
1. Validate PRD file exists
2. Load or create ADW state
3. Check/create worktree for isolated execution
4. Allocate unique ports for services
5. Setup worktree environment
6. Execute /prd_to_prompts slash command
7. Save resulting prompts document to ai_docs/
8. Commit, push, and update state

This workflow creates an isolated git worktree under trees/<adw_id>/ for
parallel execution without interference.
"""

import sys
import os
import re
import shutil
import logging
from typing import Optional
from dotenv import load_dotenv

from adw_modules.state import ADWState
from adw_modules.git_ops import commit_changes, finalize_git_operations
from adw_modules.workflow_ops import (
    ensure_adw_id,
    AGENT_PROMPTS_GENERATOR,
)
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


DEFAULT_EXAMPLE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "ai_docs",
    "tendery_v2_implementation_prompts.md",
)


def slugify_prd_name(prd_path: str) -> str:
    """Convert a PRD file path to a slugified name for the output file.

    Extracts filename without extension, converts to lowercase,
    replaces spaces/underscores with hyphens, and removes non-alphanumeric
    characters (except hyphens).
    """
    # Extract filename without extension
    basename = os.path.splitext(os.path.basename(prd_path))[0]
    # Lowercase
    slug = basename.lower()
    # Replace spaces and underscores with hyphens
    slug = slug.replace(" ", "-").replace("_", "-")
    # Remove non-alphanumeric characters (except hyphens)
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    # Collapse multiple hyphens
    slug = re.sub(r"-+", "-", slug)
    # Strip leading/trailing hyphens
    slug = slug.strip("-")
    return slug


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()

    # Parse command line args
    if len(sys.argv) < 2:
        print("Usage: uv run adw_prd_to_prompts_iso.py <prd-path> [adw-id] [--example <example-prompts-path>]")
        sys.exit(1)

    prd_path = sys.argv[1]
    adw_id = None
    example_path = DEFAULT_EXAMPLE_PATH

    # Parse remaining args
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--example" and i + 1 < len(sys.argv):
            example_path = sys.argv[i + 1]
            i += 2
        elif adw_id is None and not sys.argv[i].startswith("--"):
            adw_id = sys.argv[i]
            i += 1
        else:
            i += 1

    # Validate PRD file exists
    if not os.path.exists(prd_path):
        print(f"ERROR: PRD file not found: {prd_path}")
        sys.exit(1)

    # Validate example file exists
    if not os.path.exists(example_path):
        print(f"ERROR: Example prompts file not found: {example_path}")
        sys.exit(1)

    # Ensure ADW ID exists with initialized state
    temp_logger = setup_logger(adw_id, "adw_prd_to_prompts_iso") if adw_id else None
    adw_id = ensure_adw_id("prd2prompts", adw_id, temp_logger)

    # Load the state that was created/found by ensure_adw_id
    state = ADWState.load(adw_id, temp_logger)

    # Ensure state has the adw_id field
    if not state.get("adw_id"):
        state.update(adw_id=adw_id)

    # Track that this ADW workflow has run
    state.append_adw_id("adw_prd_to_prompts_iso")

    # Set up logger with ADW ID
    logger = setup_logger(adw_id, "adw_prd_to_prompts_iso")
    logger.info(f"ADW PRD to Prompts Iso starting - ID: {adw_id}, PRD: {prd_path}")

    # Validate environment
    check_env_vars(logger)

    # Check if worktree already exists
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
        state.save("adw_prd_to_prompts_iso")

        # Generate branch name for the worktree
        branch_name = f"feat-adw-{adw_id}-prd-to-prompts"
        state.update(branch_name=branch_name)
        state.save("adw_prd_to_prompts_iso")
        logger.info(f"Will create branch in worktree: {branch_name}")

        # Create worktree
        logger.info(f"Creating worktree for {adw_id}")
        worktree_path, wt_error = create_worktree(adw_id, branch_name, logger)

        if wt_error:
            logger.error(f"Error creating worktree: {wt_error}")
            sys.exit(1)

        state.update(worktree_path=worktree_path)
        state.save("adw_prd_to_prompts_iso")
        logger.info(f"Created worktree at {worktree_path}")

        # Setup worktree environment (create .ports.env)
        setup_worktree_environment(worktree_path, server_port, client_port, logger)

        # Run install_worktree command to set up the isolated environment
        logger.info("Setting up isolated environment with custom ports")
        install_request = AgentTemplateRequest(
            agent_name="ops",
            slash_command="/install_worktree",
            args=[worktree_path, str(server_port), str(client_port)],
            adw_id=adw_id,
            working_dir=worktree_path,
        )

        install_response = execute_template(install_request)
        if not install_response.success:
            logger.error(f"Error setting up worktree: {install_response.output}")
            sys.exit(1)

        logger.info("Worktree environment setup complete")

    # Copy the PRD file into the worktree if it's not already inside it
    prd_abs = os.path.abspath(prd_path)
    worktree_abs = os.path.abspath(worktree_path)

    if prd_abs.startswith(worktree_abs):
        # PRD is already in the worktree
        prd_path_in_worktree = os.path.relpath(prd_abs, worktree_abs)
    else:
        # Copy PRD into worktree's ai_docs/prds/
        prds_dir = os.path.join(worktree_path, "ai_docs", "prds")
        os.makedirs(prds_dir, exist_ok=True)
        prd_dest = os.path.join(prds_dir, os.path.basename(prd_path))
        shutil.copy2(prd_abs, prd_dest)
        prd_path_in_worktree = os.path.relpath(prd_dest, worktree_abs)
        logger.info(f"Copied PRD to worktree: {prd_path_in_worktree}")

    # Build the ---SPLIT--- argument
    split_args = f"{prd_path_in_worktree} ---SPLIT--- {example_path}"

    # Execute /prd_to_prompts via execute_template
    logger.info("Executing /prd_to_prompts slash command")
    request = AgentTemplateRequest(
        agent_name=AGENT_PROMPTS_GENERATOR,
        slash_command="/prd_to_prompts",
        args=[split_args],
        adw_id=adw_id,
        working_dir=worktree_path,
    )

    response = execute_template(request)

    if not response.success:
        logger.error(f"Error executing /prd_to_prompts: {response.output}")
        sys.exit(1)

    # The response.output IS the prompts markdown
    prompts_content = response.output

    # Save to ai_docs/{slugified-prd-name}-implementation-prompts.md
    slug = slugify_prd_name(prd_path)
    prompts_filename = f"{slug}-implementation-prompts.md"
    prompts_rel_path = os.path.join("ai_docs", prompts_filename)
    prompts_abs_path = os.path.join(worktree_path, prompts_rel_path)

    # Create ai_docs directory if needed
    os.makedirs(os.path.dirname(prompts_abs_path), exist_ok=True)

    with open(prompts_abs_path, "w") as f:
        f.write(prompts_content)

    logger.info(f"Saved prompts document to {prompts_rel_path}")

    # Update state with prompts_file path
    state.update(prompts_file=prompts_rel_path)
    state.save("adw_prd_to_prompts_iso")

    # Commit changes
    logger.info("Committing prompts document")
    commit_msg = f"adw_prd_to_prompts_iso: generate implementation prompts from PRD\n\nGenerated {prompts_filename} from {os.path.basename(prd_path)}"
    success, error = commit_changes(commit_msg, cwd=worktree_path)

    if not success:
        logger.error(f"Error committing prompts: {error}")
        sys.exit(1)

    logger.info(f"Committed: {commit_msg}")

    # Finalize git operations (push and PR)
    finalize_git_operations(state, logger, cwd=worktree_path)

    # Save final state
    state.save("adw_prd_to_prompts_iso")

    print(f"SUCCESS: Prompts document generated at {prompts_rel_path}")
    logger.info("PRD to Prompts workflow completed successfully")


if __name__ == "__main__":
    main()
