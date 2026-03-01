#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic", "PyMuPDF"]
# ///

"""
ADW Meeting Pipeline Iso - Process meeting transcripts into structured summaries

Usage:
  uv run adw_meeting_pipeline_iso.py <transcript-path> [adw-id]

Workflow:
1. Validate transcript file exists and is readable (.md or .pdf)
2. Create isolated worktree for execution
3. Read transcript content
4. Execute /process_meeting_transcript via execute_template()
5. Parse LLM output into structured JSON
6. Save outputs to agents/{adw_id}/meeting_outputs/ (JSON + HTML)
7. Save markdown summary to ai_docs/meeting-summaries/ in worktree
8. Commit and push from worktree

This workflow does NOT require a GitHub issue - it is a file-based workflow.
Implements REQ-012 from prd-970a89f7-meeting-processing-crm-pipeline.md.
"""

import sys
import os
import re
import json
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
    slug = text.lower()
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "ñ": "n", "ü": "u",
    }
    for old, new in replacements.items():
        slug = slug.replace(old, new)
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip("-")
    return slug or "untitled"


def parse_meeting_json(raw_output: str) -> dict:
    """Parse the LLM response to extract meeting summary JSON.

    Handles JSON wrapped in markdown code fences or raw JSON.
    Returns parsed dict or raises ValueError on failure.
    """
    text = raw_output.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove opening fence (with optional language tag) and closing fence
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    # Try to find JSON object in the text
    if not text.startswith("{"):
        # Search for JSON block in the text
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            text = match.group(0)

    return json.loads(text)


def generate_markdown_summary(meeting_data: dict, adw_id: str) -> str:
    """Generate a markdown summary from structured meeting data."""
    title = meeting_data.get("title") or "Untitled Meeting"
    meeting_date = meeting_data.get("meeting_date") or "Not specified"
    summary = meeting_data.get("summary") or "No summary available."

    lines = [
        f"# Meeting Summary: {title}",
        "",
        f"**Date:** {meeting_date}",
        f"**ADW ID:** {adw_id}",
        "",
        "## Summary",
        "",
        summary,
        "",
    ]

    # Participants
    participants = meeting_data.get("participants") or []
    if participants:
        lines.append("## Participants")
        lines.append("")
        for p in participants:
            name = p.get("name", "Unknown") if isinstance(p, dict) else str(p)
            role = p.get("role") if isinstance(p, dict) else None
            if role:
                lines.append(f"- {name} ({role})")
            else:
                lines.append(f"- {name}")
        lines.append("")

    # Company/Prospect
    company = meeting_data.get("company_name")
    contact = meeting_data.get("contact_name")
    if company or contact:
        lines.append("## Prospect")
        lines.append("")
        if company:
            lines.append(f"- **Company:** {company}")
        if contact:
            lines.append(f"- **Contact:** {contact}")
        email = meeting_data.get("contact_email")
        if email:
            lines.append(f"- **Email:** {email}")
        lines.append("")

    # Discussion Points
    discussion_points = meeting_data.get("discussion_points") or []
    if discussion_points:
        lines.append("## Discussion Points")
        lines.append("")
        for dp in discussion_points:
            topic = dp.get("topic", "") if isinstance(dp, dict) else str(dp)
            desc = dp.get("description", "") if isinstance(dp, dict) else ""
            lines.append(f"### {topic}")
            if desc:
                lines.append(f"{desc}")
            lines.append("")

    # Action Items
    action_items = meeting_data.get("action_items") or []
    if action_items:
        lines.append("## Action Items")
        lines.append("")
        for ai in action_items:
            desc = ai.get("description", "") if isinstance(ai, dict) else str(ai)
            owner = ai.get("owner") if isinstance(ai, dict) else None
            deadline = ai.get("deadline") if isinstance(ai, dict) else None
            parts = [f"- [ ] {desc}"]
            if owner:
                parts.append(f" (Owner: {owner})")
            if deadline:
                parts.append(f" [Due: {deadline}]")
            lines.append("".join(parts))
        lines.append("")

    # Decisions
    decisions = meeting_data.get("decisions") or []
    if decisions:
        lines.append("## Decisions")
        lines.append("")
        for d in decisions:
            lines.append(f"- {d}")
        lines.append("")

    # Next Steps
    next_steps = meeting_data.get("next_steps") or []
    if next_steps:
        lines.append("## Next Steps")
        lines.append("")
        for ns in next_steps:
            lines.append(f"- {ns}")
        lines.append("")

    return "\n".join(lines)


def save_meeting_outputs(meeting_data: dict, adw_id: str, logger: logging.Logger) -> str:
    """Save meeting outputs to agents/{adw_id}/meeting_outputs/.

    Returns the output directory path.
    """
    # Project root is parent of adws/
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, "agents", adw_id, "meeting_outputs")
    os.makedirs(output_dir, exist_ok=True)

    # Save structured JSON
    json_path = os.path.join(output_dir, f"meeting-{adw_id}-summary.json")
    logger.info(f"Saving JSON summary to {json_path}")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(meeting_data, f, indent=2, ensure_ascii=False)

    # Save HTML output
    html_content = meeting_data.get("html_output", "")
    if html_content:
        html_path = os.path.join(output_dir, f"meeting-{adw_id}-summary.html")
        logger.info(f"Saving HTML summary to {html_path}")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
    else:
        logger.warning("No HTML output found in meeting data")

    return output_dir


def main():
    """Main entry point."""
    load_dotenv()

    # Parse command line args
    if len(sys.argv) < 2:
        print("Usage: uv run adw_meeting_pipeline_iso.py <transcript-path> [adw-id]")
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
    temp_logger = setup_logger(adw_id, "adw_meeting_pipeline_iso") if adw_id else None
    adw_id = ensure_adw_id("meeting-pipeline", adw_id, temp_logger)

    # Load the state that was created/found by ensure_adw_id
    state = ADWState.load(adw_id, temp_logger)

    if not state.get("adw_id"):
        state.update(adw_id=adw_id)

    # Track that this ADW workflow has run
    state.append_adw_id("adw_meeting_pipeline_iso")

    # Set up logger with ADW ID
    logger = setup_logger(adw_id, "adw_meeting_pipeline_iso")
    logger.info(f"ADW Meeting Pipeline Iso starting - ID: {adw_id}")
    logger.info(f"Transcript file: {transcript_path}")

    # Validate environment
    check_env_vars(logger)

    # Branch name for this workflow
    branch_name = f"meeting-pipeline-{adw_id}"
    state.update(branch_name=branch_name)
    state.save("adw_meeting_pipeline_iso")

    # Check if worktree already exists
    valid, error = validate_worktree(adw_id, state)
    if valid:
        logger.info(f"Using existing worktree for {adw_id}")
        worktree_path = state.get("worktree_path")
    else:
        # Allocate ports for this instance
        server_port, client_port = get_ports_for_adw(adw_id)

        if not (is_port_available(server_port) and is_port_available(client_port)):
            logger.warning(f"Deterministic ports {server_port}/{client_port} are in use, finding alternatives")
            server_port, client_port = find_next_available_ports(adw_id)

        logger.info(f"Allocated ports - Server: {server_port}, Client: {client_port}")
        state.update(server_port=server_port, client_port=client_port)
        state.save("adw_meeting_pipeline_iso")

        # Create worktree
        logger.info(f"Creating worktree for {adw_id}")
        worktree_path, error = create_worktree(adw_id, branch_name, logger)

        if error:
            logger.error(f"Error creating worktree: {error}")
            sys.exit(1)

        state.update(worktree_path=worktree_path)
        state.save("adw_meeting_pipeline_iso")
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

    # Execute /process_meeting_transcript via execute_template()
    logger.info("Executing /process_meeting_transcript slash command")
    request = AgentTemplateRequest(
        agent_name="meeting_processor",
        slash_command="/process_meeting_transcript",
        args=[transcript_content],
        adw_id=adw_id,
        working_dir=worktree_path,
    )

    response = execute_template(request)

    if not response.success:
        logger.error(f"Error executing /process_meeting_transcript: {response.output}")
        sys.exit(1)

    logger.info(f"Meeting transcript processed - {len(response.output)} characters output")

    # Parse the LLM response into structured JSON
    try:
        meeting_data = parse_meeting_json(response.output)
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Error parsing meeting JSON output: {e}")
        logger.error(f"Raw output (first 500 chars): {response.output[:500]}")
        sys.exit(1)

    logger.info("Meeting data parsed successfully")

    # Save outputs to agents/{adw_id}/meeting_outputs/
    output_dir = save_meeting_outputs(meeting_data, adw_id, logger)
    logger.info(f"Meeting outputs saved to {output_dir}")

    # Generate and save markdown summary to worktree
    title = meeting_data.get("title") or "untitled"
    slug = slugify(title)
    logger.info(f"Meeting title: {title}, slug: {slug}")

    md_summary = generate_markdown_summary(meeting_data, adw_id)
    md_relative_path = f"ai_docs/meeting-summaries/meeting-{adw_id}-{slug}.md"
    md_full_path = os.path.join(worktree_path, md_relative_path)

    os.makedirs(os.path.dirname(md_full_path), exist_ok=True)

    logger.info(f"Saving markdown summary to {md_relative_path}")
    with open(md_full_path, "w", encoding="utf-8") as f:
        f.write(md_summary)

    # Update state
    state.update(plan_file=md_relative_path)
    state.save("adw_meeting_pipeline_iso")

    # Commit changes
    logger.info("Committing meeting summary")
    commit_msg = f"adw: add meeting summary from transcript ({adw_id})"
    success, error = commit_changes(commit_msg, cwd=worktree_path)

    if not success:
        logger.error(f"Error committing meeting summary: {error}")
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
    state.save("adw_meeting_pipeline_iso")

    print(f"SUCCESS: Meeting summary generated at {output_dir}")
    logger.info(f"Meeting pipeline workflow completed successfully: {output_dir}")


if __name__ == "__main__":
    main()
