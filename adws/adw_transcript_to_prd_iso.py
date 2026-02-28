#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic", "PyMuPDF"]
# ///

"""
ADW Transcript to PRD Iso - Convert meeting transcripts to PRDs in isolated worktrees

Usage:
  uv run adw_transcript_to_prd_iso.py <transcript-path> [adw-id]

Workflow:
1. Validate transcript file exists and is readable
2. Create isolated worktree for execution
3. Read transcript content
4. Execute /transcript_to_prd via execute_template()
5. Parse PRD output and generate slugified filename
6. Save PRD to ai_docs/prds/prd-{adw_id}-{slug}.md in worktree
7. Commit and push from worktree

This workflow does NOT require a GitHub issue - it is a file-based workflow.
"""

import sys
import os
import re
import logging
from dotenv import load_dotenv

from adw_modules.state import ADWState
from adw_modules.git_ops import commit_changes, push_branch
from adw_modules.workflow_ops import ensure_adw_id
from adw_modules.utils import setup_logger, check_env_vars
from adw_modules.data_types import AgentTemplateRequest
from adw_modules.agent import execute_template
from adw_modules.worktree_ops import (
    create_worktree,
    validate_worktree,
    get_ports_for_adw,
    is_port_available,
    find_next_available_ports,
)


def slugify(text: str, max_length: int = 50) -> str:
    """Convert text to a URL-friendly slug.

    Handles Spanish characters and special chars gracefully.
    """
    # Lowercase
    slug = text.lower()
    # Replace common Spanish accented chars
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "ñ": "n", "ü": "u",
    }
    for old, new in replacements.items():
        slug = slug.replace(old, new)
    # Replace non-alphanumeric with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    # Remove leading/trailing hyphens
    slug = slug.strip("-")
    # Truncate
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip("-")
    return slug or "untitled"


def extract_prd_topic(prd_content: str) -> str:
    """Extract topic from PRD title line (first '# PRD: {topic}' match)."""
    match = re.search(r"^#\s+PRD:\s*(.+)$", prd_content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    # Fallback: try first heading
    match = re.search(r"^#\s+(.+)$", prd_content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "untitled"


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()

    # Parse command line args
    if len(sys.argv) < 2:
        print("Usage: uv run adw_transcript_to_prd_iso.py <transcript-path> [adw-id]")
        sys.exit(1)

    transcript_path = sys.argv[1]
    adw_id = sys.argv[2] if len(sys.argv) > 2 else None

    # Validate transcript file exists
    if not os.path.exists(transcript_path):
        print(f"ERROR: Transcript file not found: {transcript_path}")
        sys.exit(1)

    SUPPORTED_EXTENSIONS = (".md", ".pdf")
    if not transcript_path.endswith(SUPPORTED_EXTENSIONS):
        print(f"ERROR: Transcript file must be one of {SUPPORTED_EXTENSIONS}: {transcript_path}")
        sys.exit(1)

    # Make transcript path absolute for reliable reading
    transcript_path = os.path.abspath(transcript_path)

    # Ensure ADW ID exists with initialized state
    # Use "transcript" as placeholder issue_number since this is file-based
    temp_logger = setup_logger(adw_id, "adw_transcript_to_prd_iso") if adw_id else None
    adw_id = ensure_adw_id("transcript", adw_id, temp_logger)

    # Load the state that was created/found by ensure_adw_id
    state = ADWState.load(adw_id, temp_logger)

    # Ensure state has the adw_id field
    if not state.get("adw_id"):
        state.update(adw_id=adw_id)

    # Track that this ADW workflow has run
    state.append_adw_id("adw_transcript_to_prd_iso")

    # Set up logger with ADW ID
    logger = setup_logger(adw_id, "adw_transcript_to_prd_iso")
    logger.info(f"ADW Transcript to PRD Iso starting - ID: {adw_id}")
    logger.info(f"Transcript file: {transcript_path}")

    # Validate environment
    check_env_vars(logger)

    # Branch name for this workflow
    branch_name = f"transcript-prd-{adw_id}"
    state.update(branch_name=branch_name)
    state.save("adw_transcript_to_prd_iso")

    # Check if worktree already exists
    valid, error = validate_worktree(adw_id, state)
    if valid:
        logger.info(f"Using existing worktree for {adw_id}")
        worktree_path = state.get("worktree_path")
    else:
        # Allocate ports for this instance
        server_port, client_port = get_ports_for_adw(adw_id)

        # Check port availability
        if not (is_port_available(server_port) and is_port_available(client_port)):
            logger.warning(f"Deterministic ports {server_port}/{client_port} are in use, finding alternatives")
            server_port, client_port = find_next_available_ports(adw_id)

        logger.info(f"Allocated ports - Server: {server_port}, Client: {client_port}")
        state.update(server_port=server_port, client_port=client_port)
        state.save("adw_transcript_to_prd_iso")

        # Create worktree
        logger.info(f"Creating worktree for {adw_id}")
        worktree_path, error = create_worktree(adw_id, branch_name, logger)

        if error:
            logger.error(f"Error creating worktree: {error}")
            sys.exit(1)

        state.update(worktree_path=worktree_path)
        state.save("adw_transcript_to_prd_iso")
        logger.info(f"Created worktree at {worktree_path}")

    # Read transcript content
    logger.info("Reading transcript content")
    try:
        if transcript_path.endswith(".pdf"):
            import fitz  # PyMuPDF

            logger.info("Extracting text from PDF file")
            doc = fitz.open(transcript_path)
            page_count = len(doc)
            transcript_content = "\n\n".join(
                page.get_text() for page in doc
            )
            doc.close()
            logger.info(f"Extracted text from {page_count} PDF page(s)")
        else:
            with open(transcript_path, "r", encoding="utf-8") as f:
                transcript_content = f.read()
    except Exception as e:
        logger.error(f"Error reading transcript file: {e}")
        sys.exit(1)

    if not transcript_content.strip():
        logger.warning("Transcript file is empty - proceeding anyway")

    logger.info(f"Transcript content length: {len(transcript_content)} characters")

    # Execute /transcript_to_prd via execute_template()
    logger.info("Executing /transcript_to_prd slash command")
    request = AgentTemplateRequest(
        agent_name="transcript_processor",
        slash_command="/transcript_to_prd",
        args=[transcript_content],
        adw_id=adw_id,
        working_dir=worktree_path,
    )

    response = execute_template(request)

    if not response.success:
        logger.error(f"Error executing /transcript_to_prd: {response.output}")
        sys.exit(1)

    prd_content = response.output
    logger.info(f"PRD generated - {len(prd_content)} characters")

    # Extract topic and generate slug
    topic = extract_prd_topic(prd_content)
    slug = slugify(topic)
    logger.info(f"PRD topic: {topic}, slug: {slug}")

    # Save PRD to ai_docs/prds/ in worktree
    prd_relative_path = f"ai_docs/prds/prd-{adw_id}-{slug}.md"
    prd_full_path = os.path.join(worktree_path, prd_relative_path)

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(prd_full_path), exist_ok=True)

    logger.info(f"Saving PRD to {prd_relative_path}")
    with open(prd_full_path, "w", encoding="utf-8") as f:
        f.write(prd_content)

    # Update state with plan_file (repurposed for PRD path)
    state.update(plan_file=prd_relative_path)
    state.save("adw_transcript_to_prd_iso")

    # Commit changes
    logger.info("Committing PRD")
    commit_msg = f"adw: add PRD from transcript ({adw_id})"
    success, error = commit_changes(commit_msg, cwd=worktree_path)

    if not success:
        logger.error(f"Error committing PRD: {error}")
        sys.exit(1)

    logger.info(f"Committed: {commit_msg}")

    # Push branch
    logger.info("Pushing branch")
    success, error = push_branch(branch_name, cwd=worktree_path)

    if not success:
        logger.error(f"Error pushing branch: {error}")
        sys.exit(1)

    logger.info(f"Pushed branch: {branch_name}")

    # Save final state
    state.save("adw_transcript_to_prd_iso")

    print(f"SUCCESS: PRD generated at {prd_relative_path}")
    logger.info(f"Transcript to PRD workflow completed successfully: {prd_relative_path}")


if __name__ == "__main__":
    main()
