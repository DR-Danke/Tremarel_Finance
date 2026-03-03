#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic", "PyMuPDF", "requests"]
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
from datetime import datetime, timezone
from dotenv import load_dotenv

from adw_modules.crm_api_client import CrmApiClient
from adw_modules.github import (
    check_gh_authenticated,
    create_issue,
    ensure_labels_exist,
)
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

    Handles JSON wrapped in markdown code fences, raw JSON, or JSON
    embedded within markdown commentary. Uses multiple strategies:
    1. Direct JSON parse
    2. Strip markdown code fences and parse
    3. Extract JSON block from within markdown text
    Returns parsed dict or raises ValueError on failure.
    """
    text = raw_output.strip()

    # Strategy 1: Direct parse (response is pure JSON)
    if text.startswith("{"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    # Strategy 2: Strip markdown code fences
    # Find all fenced code blocks and try to parse each as JSON
    fence_pattern = re.compile(r"```(?:json)?\s*\n([\s\S]*?)\n```")
    for match in fence_pattern.finditer(text):
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            continue

    # Strategy 3: Find the largest JSON object in the text
    # Use a balanced-brace approach to find complete JSON objects
    candidates = []
    for match in re.finditer(r"\{", text):
        start = match.start()
        depth = 0
        in_string = False
        escape_next = False
        for i in range(start, len(text)):
            ch = text[i]
            if escape_next:
                escape_next = False
                continue
            if ch == "\\":
                escape_next = True
                continue
            if ch == '"' and not escape_next:
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidates.append(text[start : i + 1])
                    break

    # Try candidates from largest to smallest (the meeting JSON is typically the biggest)
    candidates.sort(key=len, reverse=True)
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
            # Validate it looks like meeting data (has at least a title or summary)
            if isinstance(parsed, dict) and ("title" in parsed or "summary" in parsed):
                return parsed
        except json.JSONDecodeError:
            continue

    raise ValueError("No valid meeting JSON found in LLM output")


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


def update_crm(
    meeting_data: dict, transcript_path: str, adw_id: str, logger: logging.Logger
) -> dict:
    """Update CRM with prospect and meeting record from processed transcript.

    Authenticates with the backend API using service account credentials,
    searches for or creates a prospect, creates a meeting record, and
    optionally advances the prospect's pipeline stage.

    CRM failures are logged but do NOT raise exceptions — the pipeline's
    primary deliverable (JSON/HTML/markdown) is already saved.

    Returns a result dict with keys:
        success, skipped, skip_reason, prospect_action, prospect_id,
        prospect_company, meeting_record_id, stage_advanced, errors
    """
    result = {
        "success": False,
        "skipped": False,
        "skip_reason": None,
        "prospect_action": None,
        "prospect_id": None,
        "prospect_company": None,
        "meeting_record_id": None,
        "stage_advanced": False,
        "errors": [],
    }

    base_url = os.environ.get("ADW_API_BASE_URL", "http://localhost:8000/api")
    service_email = os.environ.get("ADW_SERVICE_EMAIL")
    service_password = os.environ.get("ADW_SERVICE_PASSWORD")
    entity_id = os.environ.get("ADW_ENTITY_ID")

    if not all([service_email, service_password, entity_id]):
        logger.warning(
            "CRM update skipped: ADW_SERVICE_EMAIL, ADW_SERVICE_PASSWORD, "
            "and ADW_ENTITY_ID must all be set"
        )
        result["skipped"] = True
        result["skip_reason"] = "Missing required env vars (ADW_SERVICE_EMAIL, ADW_SERVICE_PASSWORD, ADW_ENTITY_ID)"
        return result

    client = CrmApiClient(base_url, logger)

    if not client.authenticate(service_email, service_password):
        logger.error("CRM update aborted: authentication failed")
        result["errors"].append("Authentication failed")
        return result

    company_name = meeting_data.get("company_name")
    if not company_name:
        company_name = meeting_data.get("title", f"Meeting Transcript {adw_id}")
        logger.info(f"No company_name in meeting data, using title as fallback: {company_name}")

    result["prospect_company"] = company_name

    # Search for existing prospect
    prospect = client.search_prospect(entity_id, company_name)

    if prospect:
        logger.info(f"CRM: Matched existing prospect {prospect['id']} for '{company_name}'")
        result["prospect_action"] = "matched"
        # Advance from lead to contacted if applicable
        if prospect.get("stage") == "lead":
            advance_result = client.advance_prospect_stage(
                prospect["id"],
                entity_id,
                "contacted",
                "Auto-advanced: meeting transcript processed",
            )
            if advance_result:
                result["stage_advanced"] = True
    else:
        # Create new prospect
        contact_name = meeting_data.get("contact_name")
        contact_email = meeting_data.get("contact_email")
        prospect = client.create_prospect(
            entity_id=entity_id,
            company_name=company_name,
            contact_name=contact_name,
            contact_email=contact_email,
            stage="contacted",
            source="meeting-transcript",
            notes=f"Auto-created from transcript processing (ADW: {adw_id})",
        )
        if not prospect:
            logger.error("CRM update aborted: failed to create prospect")
            result["errors"].append("Failed to create prospect")
            return result
        result["prospect_action"] = "created"

    prospect_id = prospect["id"]
    result["prospect_id"] = prospect_id

    # Extract participants and action items
    participants = [
        p.get("name", "Unknown") if isinstance(p, dict) else str(p)
        for p in meeting_data.get("participants", [])
    ]
    action_items = [
        a.get("description", str(a)) if isinstance(a, dict) else str(a)
        for a in meeting_data.get("action_items", [])
    ]

    title = meeting_data.get("title") or "Untitled Meeting"
    summary = meeting_data.get("summary")
    html_output = meeting_data.get("html_output")
    meeting_date = meeting_data.get("meeting_date")

    record = client.create_meeting_record(
        entity_id=entity_id,
        prospect_id=prospect_id,
        title=title,
        transcript_ref=transcript_path,
        summary=summary,
        action_items=action_items if action_items else None,
        participants=participants if participants else None,
        html_output=html_output,
        meeting_date=meeting_date,
    )

    if record:
        result["meeting_record_id"] = record["id"]
        result["success"] = True
        logger.info(f"CRM update complete: meeting record {record['id']} linked to prospect {prospect_id}")
    else:
        result["errors"].append("Failed to create meeting record")
        logger.error("CRM update: failed to create meeting record")

    return result


def generate_github_issue(
    meeting_data: dict,
    crm_result: dict,
    adw_id: str,
    transcript_path: str,
    logger: logging.Logger,
) -> str | None:
    """Generate a GitHub issue summarizing meeting processing results.

    Creates an issue with structured sections and machine-parseable metadata.
    Failures are logged but do NOT raise exceptions.

    Returns the created issue number string, or None on failure.
    """
    if not check_gh_authenticated():
        logger.warning("GitHub issue generation skipped: gh CLI not authenticated")
        return None

    # Build issue title
    title = meeting_data.get("title") or "Untitled Meeting"
    company_name = meeting_data.get("company_name") or "Unknown"
    issue_title = f"[Meeting Processed] {title} - {company_name}"
    if len(issue_title) > 100:
        issue_title = issue_title[:97] + "..."

    # Build issue body sections
    sections = []

    # Meeting Summary
    meeting_date = meeting_data.get("meeting_date") or "Not specified"
    summary_text = meeting_data.get("summary") or "No summary available."
    participants = meeting_data.get("participants") or []
    participant_list = ", ".join(
        p.get("name", "Unknown") if isinstance(p, dict) else str(p)
        for p in participants
    ) or "Not specified"

    sections.append(
        f"## Meeting Summary\n\n"
        f"- **Title:** {title}\n"
        f"- **Date:** {meeting_date}\n"
        f"- **Participants:** {participant_list}\n\n"
        f"{summary_text}"
    )

    # Prospect Information
    contact_name = meeting_data.get("contact_name")
    contact_email = meeting_data.get("contact_email")
    prospect_action = crm_result.get("prospect_action") or "N/A"
    prospect_lines = [f"- **Company:** {company_name}"]
    if contact_name:
        prospect_lines.append(f"- **Contact:** {contact_name}")
    if contact_email:
        prospect_lines.append(f"- **Email:** {contact_email}")
    prospect_lines.append(f"- **Prospect Action:** {prospect_action}")
    sections.append(f"## Prospect Information\n\n" + "\n".join(prospect_lines))

    # CRM Update Results
    crm_success = crm_result.get("success", False)
    crm_skipped = crm_result.get("skipped", False)
    crm_lines = []
    if crm_skipped:
        skip_reason = crm_result.get("skip_reason") or "Unknown"
        crm_lines.append(f"- **Status:** Skipped ({skip_reason})")
    elif crm_success:
        crm_lines.append("- **Status:** Success")
    else:
        crm_lines.append("- **Status:** Failed")
    if crm_result.get("prospect_id"):
        crm_lines.append(f"- **Prospect ID:** {crm_result['prospect_id']}")
    if crm_result.get("meeting_record_id"):
        crm_lines.append(f"- **Meeting Record ID:** {crm_result['meeting_record_id']}")
    crm_lines.append(f"- **Stage Advanced:** {'Yes' if crm_result.get('stage_advanced') else 'No'}")
    crm_errors = crm_result.get("errors") or []
    if crm_errors:
        crm_lines.append(f"- **Errors:** {'; '.join(crm_errors)}")
    sections.append(f"## CRM Update Results\n\n" + "\n".join(crm_lines))

    # Action Items
    action_items = meeting_data.get("action_items") or []
    if action_items:
        items = []
        for ai in action_items:
            desc = ai.get("description", str(ai)) if isinstance(ai, dict) else str(ai)
            items.append(f"- {desc}")
        sections.append(f"## Action Items\n\n" + "\n".join(items))

    # Decisions
    decisions = meeting_data.get("decisions") or []
    if decisions:
        sections.append(f"## Decisions\n\n" + "\n".join(f"- {d}" for d in decisions))

    # Next Steps
    next_steps = meeting_data.get("next_steps") or []
    if next_steps:
        sections.append(f"## Next Steps\n\n" + "\n".join(f"- {ns}" for ns in next_steps))

    # Pipeline Metadata
    timestamp = datetime.now(timezone.utc).isoformat()
    sections.append(
        f"## Pipeline Metadata\n\n"
        f"- **ADW ID:** {adw_id}\n"
        f"- **Transcript:** `{transcript_path}`\n"
        f"- **Processed At:** {timestamp}"
    )

    # Machine-parseable metadata block
    metadata = {
        "adw_id": adw_id,
        "prospect_id": crm_result.get("prospect_id"),
        "meeting_record_id": crm_result.get("meeting_record_id"),
        "prospect_company": crm_result.get("prospect_company"),
        "crm_success": crm_result.get("success", False),
        "crm_skipped": crm_result.get("skipped", False),
        "timestamp": timestamp,
    }
    sections.append(f"<!-- ADW_METADATA: {json.dumps(metadata)} -->")

    body = "\n\n".join(sections)

    # Create issue with labels
    labels = ["meeting-processed", "adw-generated"]
    ensure_labels_exist(labels)
    issue_number = create_issue(issue_title, body, labels)

    if issue_number:
        logger.info(f"GitHub issue created: #{issue_number}")
        return issue_number
    else:
        logger.warning("GitHub issue creation failed")
        return None


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

    # Obtain structured meeting data using multiple strategies:
    # 1. Parse raw_output.jsonl for JSON text blocks and Write tool calls
    # 2. Search for summary JSON files in worktree and agents output
    # 3. Parse the final LLM response text
    meeting_data = None
    meeting_json_dir = None  # Track where the JSON was found for sibling HTML lookup
    import glob as glob_mod

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    agents_output_dir = os.path.join(project_root, "agents", adw_id)

    # Strategy 1: Parse raw_output.jsonl for JSON in assistant messages and Write tool calls
    raw_jsonl_path = os.path.join(agents_output_dir, "meeting_processor", "raw_output.jsonl")
    if os.path.exists(raw_jsonl_path):
        logger.info(f"Parsing raw output JSONL: {raw_jsonl_path}")
        try:
            with open(raw_jsonl_path, "r", encoding="utf-8") as rjf:
                for line in rjf:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    if entry.get("type") != "assistant":
                        continue
                    msg = entry.get("message", {})
                    for block in msg.get("content", []):
                        # Check text blocks for JSON content
                        if block.get("type") == "text" and meeting_data is None:
                            text = block.get("text", "").strip()
                            try:
                                meeting_data = parse_meeting_json(text)
                                logger.info("Meeting data extracted from JSONL text block")
                            except (json.JSONDecodeError, ValueError):
                                pass
                        # Check Write tool calls for HTML content
                        if block.get("type") == "tool_use" and block.get("name") == "Write":
                            inp = block.get("input", {})
                            fp = inp.get("file_path", "")
                            if fp.endswith(".html") and inp.get("content", "").strip().startswith("<"):
                                html_from_jsonl = inp["content"]
                                if meeting_data and (not meeting_data.get("html_output") or not meeting_data["html_output"].strip().startswith("<")):
                                    meeting_data["html_output"] = html_from_jsonl
                                    logger.info(f"HTML output loaded from JSONL Write call: {fp}")
        except Exception as e:
            logger.warning(f"Error parsing raw JSONL: {e}")

    # Strategy 2: Search for summary JSON files in worktree and agents output
    if meeting_data is None:
        search_patterns = [
            os.path.join(worktree_path, "meetings", "**", "summary.json"),
            os.path.join(worktree_path, "meetings", "**", "*.json"),
            os.path.join(worktree_path, "agents", "**", "*summary*.json"),
            os.path.join(worktree_path, "agents", "**", "summary.json"),
            os.path.join(agents_output_dir, "**", "*summary*.json"),
            os.path.join(agents_output_dir, "**", "summary.json"),
        ]
        json_candidates = []
        for pattern in search_patterns:
            json_candidates.extend(glob_mod.glob(pattern, recursive=True))
        json_candidates = sorted(set(json_candidates), key=os.path.getmtime, reverse=True)
        for json_path in json_candidates:
            try:
                with open(json_path, "r", encoding="utf-8") as jf:
                    meeting_data = json.load(jf)
                if isinstance(meeting_data, dict) and ("title" in meeting_data or "summary" in meeting_data):
                    meeting_json_dir = os.path.dirname(json_path)
                    logger.info(f"Loaded meeting data from file: {json_path}")
                    break
                meeting_data = None
            except (json.JSONDecodeError, OSError) as fe:
                logger.warning(f"Could not read {json_path}: {fe}")
                meeting_data = None

    # Strategy 3: Parse JSON from the final LLM response text
    if meeting_data is None:
        logger.info("Attempting to parse LLM response text as fallback")
        try:
            meeting_data = parse_meeting_json(response.output)
            logger.info("Meeting data parsed from LLM response text")
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Could not parse JSON from LLM response: {e}")

    if meeting_data is None:
        logger.error("Failed to obtain meeting data from worktree files or LLM response")
        logger.error(f"Raw output (first 500 chars): {response.output[:500]}")
        sys.exit(1)

    # If html_output is missing or is a reference (not actual HTML), load from sibling HTML file
    html_content = meeting_data.get("html_output", "")
    if not html_content or not html_content.strip().startswith("<"):
        logger.info("html_output is missing or is a file reference, searching for HTML file")
        html_candidates = []
        if meeting_json_dir:
            html_candidates.extend(glob_mod.glob(os.path.join(meeting_json_dir, "*.html")))
        html_candidates.extend(glob_mod.glob(os.path.join(worktree_path, "meetings", "**", "*.html"), recursive=True))
        html_candidates.extend(glob_mod.glob(os.path.join(worktree_path, "agents", "**", "*summary*.html"), recursive=True))
        html_candidates.extend(glob_mod.glob(os.path.join(agents_output_dir, "**", "*.html"), recursive=True))
        html_candidates = sorted(set(html_candidates), key=os.path.getmtime, reverse=True)
        for html_path in html_candidates:
            try:
                with open(html_path, "r", encoding="utf-8") as hf:
                    loaded_html = hf.read()
                if loaded_html.strip().startswith("<"):
                    meeting_data["html_output"] = loaded_html
                    logger.info(f"Loaded HTML output from: {html_path}")
                    break
            except OSError as he:
                logger.warning(f"Could not read {html_path}: {he}")

    logger.info("Meeting data parsed successfully")

    # Generate technical diagrams in a separate focused call if none were produced
    if not meeting_data.get("diagrams"):
        logger.info("No diagrams in meeting data, running dedicated diagram generation step")
        summary_text = meeting_data.get("summary", "")
        discussion_text = json.dumps(meeting_data.get("discussion_points", []), indent=2)
        diagram_prompt = (
            "Based on the following meeting summary and discussion points, generate Mermaid diagrams "
            "that visualize the technical systems, architectures, and workflows discussed.\n\n"
            f"## Summary\n{summary_text}\n\n"
            f"## Discussion Points\n{discussion_text}\n\n"
            "## Instructions\n"
            "Generate 2-4 Mermaid diagrams. For each diagram, respond with ONLY a JSON array. "
            "No preamble, no commentary, just the JSON array.\n\n"
            "Use these diagram types as appropriate:\n"
            "- flowchart TD for processes and decision flows\n"
            "- flowchart LR for system architecture and component connections\n"
            "- sequenceDiagram for multi-party interactions\n\n"
            "```json\n"
            '[{"title": "Diagram Title", "mermaid_code": "flowchart TD\\n  A[Start] --> B[End]"}]\n'
            "```\n\n"
            "Respond ONLY with the JSON array in a code block. No other text."
        )
        # Use direct prompt (not slash command) for focused diagram generation
        from adw_modules.agent import AgentPromptRequest, prompt_claude_code_with_retry
        diagram_output_file = os.path.join(agents_output_dir, "diagram_generator", "raw_output.jsonl")
        diagram_prompt_request = AgentPromptRequest(
            prompt=diagram_prompt,
            adw_id=adw_id,
            agent_name="diagram_generator",
            model="sonnet",
            dangerously_skip_permissions=True,
            output_file=diagram_output_file,
            working_dir=worktree_path,
        )
        os.makedirs(os.path.dirname(diagram_prompt_request.output_file), exist_ok=True)
        try:
            diagram_response = prompt_claude_code_with_retry(diagram_prompt_request)
            if diagram_response.success:
                # Try to parse diagrams from response text
                diagram_text = diagram_response.output.strip()
                try:
                    diagrams = parse_meeting_json(diagram_text) if diagram_text.startswith("{") else None
                except (json.JSONDecodeError, ValueError):
                    diagrams = None

                if diagrams is None:
                    # Try parsing as array
                    fence_pattern = re.compile(r"```(?:json)?\s*\n([\s\S]*?)\n```")
                    for m in fence_pattern.finditer(diagram_text):
                        try:
                            diagrams = json.loads(m.group(1).strip())
                            break
                        except json.JSONDecodeError:
                            continue
                    if diagrams is None:
                        # Try direct array parse
                        arr_match = re.search(r"\[[\s\S]*\]", diagram_text)
                        if arr_match:
                            try:
                                diagrams = json.loads(arr_match.group(0))
                            except json.JSONDecodeError:
                                pass

                # Also check JSONL for diagrams
                if not diagrams:
                    jsonl_path = diagram_prompt_request.output_file
                    if os.path.exists(jsonl_path):
                        with open(jsonl_path, "r") as djf:
                            for dline in djf:
                                dentry = json.loads(dline.strip())
                                if dentry.get("type") != "assistant":
                                    continue
                                for dblock in dentry.get("message", {}).get("content", []):
                                    if dblock.get("type") == "text":
                                        dtxt = dblock.get("text", "").strip()
                                        for dm in fence_pattern.finditer(dtxt):
                                            try:
                                                diagrams = json.loads(dm.group(1).strip())
                                                if isinstance(diagrams, list):
                                                    break
                                            except json.JSONDecodeError:
                                                continue
                                        if not diagrams:
                                            arr_m = re.search(r"\[[\s\S]*\]", dtxt)
                                            if arr_m:
                                                try:
                                                    diagrams = json.loads(arr_m.group(0))
                                                except json.JSONDecodeError:
                                                    pass
                                    if diagrams:
                                        break
                                if diagrams:
                                    break

                if isinstance(diagrams, list) and len(diagrams) > 0:
                    meeting_data["diagrams"] = diagrams
                    logger.info(f"Generated {len(diagrams)} technical diagram(s)")
                    for d in diagrams:
                        logger.info(f"  - {d.get('title', 'untitled')}")
                    # Inject diagrams into HTML if present
                    html = meeting_data.get("html_output", "")
                    if html and diagrams:
                        mermaid_section = '\n<div style="margin-top:32px;"><h2 style="color:#1565C0;border-bottom:2px solid #1565C0;padding-bottom:8px;">Technical Architecture</h2>\n'
                        for d in diagrams:
                            title = d.get("title", "")
                            code = d.get("mermaid_code", "")
                            mermaid_section += f'<h3 style="color:#333;margin-top:24px;">{title}</h3>\n<pre class="mermaid">\n{code}\n</pre>\n'
                        mermaid_section += '</div>\n'
                        mermaid_script = '<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>\n<script>mermaid.initialize({startOnLoad:true});</script>\n'
                        # Insert before </body>
                        if "</body>" in html:
                            html = html.replace("</body>", mermaid_section + mermaid_script + "</body>")
                        else:
                            html += mermaid_section + mermaid_script
                        meeting_data["html_output"] = html
                        logger.info("Injected Mermaid diagrams into HTML output")
                else:
                    logger.warning("Diagram generation returned no valid diagrams")
        except Exception as e:
            logger.warning(f"Diagram generation failed (non-fatal): {e}")

    # Save outputs to agents/{adw_id}/meeting_outputs/
    output_dir = save_meeting_outputs(meeting_data, adw_id, logger)
    logger.info(f"Meeting outputs saved to {output_dir}")

    # Update CRM with prospect and meeting record
    try:
        crm_result = update_crm(meeting_data, transcript_path, adw_id, logger)
    except Exception as e:
        logger.error(f"CRM update failed (non-fatal): {e}")
        crm_result = {"success": False, "skipped": False, "errors": [str(e)]}

    # Generate GitHub issue summarizing processing results
    try:
        issue_number = generate_github_issue(
            meeting_data, crm_result, adw_id, transcript_path, logger
        )
        if issue_number:
            state.update(generated_issue_number=issue_number)
            state.save("adw_meeting_pipeline_iso")
    except Exception as e:
        logger.error(f"GitHub issue generation failed (non-fatal): {e}")

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
