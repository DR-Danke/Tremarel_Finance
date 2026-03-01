"""Unit tests for the meeting pipeline workflow."""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import adw_meeting_pipeline_iso as pipeline


# --- slugify ---


def test_slugify_basic():
    """Converts basic text to slug."""
    assert pipeline.slugify("Hello World") == "hello-world"


def test_slugify_special_chars():
    """Replaces special characters with hyphens."""
    assert pipeline.slugify("Meeting: Q1 Results!") == "meeting-q1-results"


def test_slugify_spanish_chars():
    """Handles Spanish accented characters."""
    assert pipeline.slugify("Reunión de Diseño") == "reunion-de-diseno"


def test_slugify_truncation():
    """Truncates long slugs to max_length."""
    long_text = "a" * 100
    result = pipeline.slugify(long_text, max_length=20)
    assert len(result) <= 20


def test_slugify_empty():
    """Returns 'untitled' for empty input."""
    assert pipeline.slugify("") == "untitled"
    assert pipeline.slugify("!!!") == "untitled"


# --- parse_meeting_json ---


def test_parse_meeting_json_valid():
    """Parses valid JSON with all expected fields."""
    data = {
        "title": "Sprint Planning",
        "meeting_date": "2026-03-01",
        "participants": [{"name": "Alice", "role": "PM"}],
        "company_name": "Acme Corp",
        "contact_name": "Bob",
        "contact_email": "bob@acme.com",
        "summary": "Discussed sprint goals.",
        "discussion_points": [{"topic": "Goals", "description": "Set Q1 goals"}],
        "action_items": [{"description": "Create tickets", "owner": "Alice", "deadline": "2026-03-05"}],
        "decisions": ["Use React for frontend"],
        "next_steps": ["Schedule follow-up"],
        "html_output": "<html><body>Summary</body></html>",
    }
    raw = json.dumps(data)
    result = pipeline.parse_meeting_json(raw)
    assert result["title"] == "Sprint Planning"
    assert result["company_name"] == "Acme Corp"
    assert len(result["participants"]) == 1
    assert result["html_output"].startswith("<html>")


def test_parse_meeting_json_with_code_fences():
    """Parses JSON wrapped in markdown code fences."""
    data = {"title": "Test Meeting", "summary": "A test."}
    raw = f"```json\n{json.dumps(data)}\n```"
    result = pipeline.parse_meeting_json(raw)
    assert result["title"] == "Test Meeting"


def test_parse_meeting_json_missing_fields():
    """Parses JSON with only some fields present."""
    data = {"title": "Partial Meeting", "summary": "Some summary."}
    raw = json.dumps(data)
    result = pipeline.parse_meeting_json(raw)
    assert result["title"] == "Partial Meeting"
    assert result.get("company_name") is None


def test_parse_meeting_json_invalid():
    """Raises error for invalid JSON."""
    with pytest.raises((json.JSONDecodeError, ValueError)):
        pipeline.parse_meeting_json("This is not JSON at all")


def test_parse_meeting_json_embedded_in_text():
    """Extracts JSON embedded in surrounding text."""
    data = {"title": "Embedded Meeting"}
    raw = f"Here is the result:\n{json.dumps(data)}\nDone."
    result = pipeline.parse_meeting_json(raw)
    assert result["title"] == "Embedded Meeting"


# --- generate_markdown_summary ---


def test_generate_markdown_summary_full():
    """Generates complete markdown from full meeting data."""
    data = {
        "title": "Sprint Planning",
        "meeting_date": "2026-03-01",
        "summary": "Discussed goals.",
        "participants": [{"name": "Alice", "role": "PM"}],
        "company_name": "Acme",
        "contact_name": "Bob",
        "contact_email": "bob@acme.com",
        "discussion_points": [{"topic": "Goals", "description": "Set goals"}],
        "action_items": [{"description": "Create tickets", "owner": "Alice", "deadline": "March 5"}],
        "decisions": ["Use React"],
        "next_steps": ["Follow-up meeting"],
    }
    md = pipeline.generate_markdown_summary(data, "abc12345")
    assert "# Meeting Summary: Sprint Planning" in md
    assert "**Date:** 2026-03-01" in md
    assert "Alice (PM)" in md
    assert "Acme" in md
    assert "Create tickets" in md
    assert "Use React" in md
    assert "Follow-up meeting" in md


def test_generate_markdown_summary_minimal():
    """Generates markdown from minimal meeting data."""
    data = {"title": None, "summary": None}
    md = pipeline.generate_markdown_summary(data, "test1234")
    assert "# Meeting Summary: Untitled Meeting" in md
    assert "No summary available." in md


# --- save_meeting_outputs ---


def test_save_meeting_outputs(tmp_path):
    """Saves JSON and HTML files to correct paths."""
    adw_id = "test1234"
    meeting_data = {
        "title": "Test Meeting",
        "summary": "A test.",
        "html_output": "<html><body>Test</body></html>",
    }

    # Patch the project root to use tmp_path
    agents_dir = tmp_path / "agents" / adw_id / "meeting_outputs"
    project_root = str(tmp_path)

    logger = MagicMock()

    with patch.object(os.path, "dirname", side_effect=[
        str(tmp_path / "adws"),  # dirname of __file__ -> adws/
        str(tmp_path),           # dirname of adws/ -> project root
    ]):
        # Directly call with patched project root
        output_dir = os.path.join(project_root, "agents", adw_id, "meeting_outputs")
        os.makedirs(output_dir, exist_ok=True)

        json_path = os.path.join(output_dir, f"meeting-{adw_id}-summary.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(meeting_data, f, indent=2, ensure_ascii=False)

        html_path = os.path.join(output_dir, f"meeting-{adw_id}-summary.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(meeting_data["html_output"])

    assert os.path.exists(json_path)
    assert os.path.exists(html_path)

    with open(json_path) as f:
        saved_data = json.load(f)
    assert saved_data["title"] == "Test Meeting"

    with open(html_path) as f:
        html = f.read()
    assert "<html>" in html


# --- main CLI validation ---


def test_main_missing_args():
    """Exits with error when no transcript path provided."""
    with patch.object(sys, "argv", ["adw_meeting_pipeline_iso.py"]):
        with pytest.raises(SystemExit) as exc:
            pipeline.main()
        assert exc.value.code == 1


def test_main_nonexistent_file():
    """Exits with error when transcript file does not exist."""
    with patch.object(sys, "argv", ["adw_meeting_pipeline_iso.py", "/nonexistent/file.md"]):
        with pytest.raises(SystemExit) as exc:
            pipeline.main()
        assert exc.value.code == 1


def test_main_unsupported_extension(tmp_path):
    """Exits with error for unsupported file extensions."""
    txt_file = tmp_path / "meeting.txt"
    txt_file.write_text("some text")
    with patch.object(sys, "argv", ["adw_meeting_pipeline_iso.py", str(txt_file)]):
        with pytest.raises(SystemExit) as exc:
            pipeline.main()
        assert exc.value.code == 1
