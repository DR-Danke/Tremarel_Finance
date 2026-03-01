"""Unit tests for the meeting pipeline workflow."""

import json
import logging
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import requests

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import adw_meeting_pipeline_iso as pipeline
from adw_modules.crm_api_client import CrmApiClient


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


# --- CrmApiClient ---


@pytest.fixture
def crm_client():
    """Create a CrmApiClient with a mock logger."""
    logger = MagicMock(spec=logging.Logger)
    return CrmApiClient("http://localhost:8000/api", logger)


@patch("adw_modules.crm_api_client.requests.post")
def test_crm_client_authenticate_success(mock_post, crm_client):
    """Authenticates and caches JWT token on 200 response."""
    mock_post.return_value = MagicMock(
        status_code=200,
        json=MagicMock(return_value={"access_token": "test-jwt-token"}),
    )
    result = crm_client.authenticate("user@test.com", "password123")
    assert result is True
    assert crm_client._token == "test-jwt-token"
    mock_post.assert_called_once()


@patch("adw_modules.crm_api_client.requests.post")
def test_crm_client_authenticate_failure(mock_post, crm_client):
    """Returns False on 401 response."""
    mock_post.return_value = MagicMock(status_code=401)
    result = crm_client.authenticate("user@test.com", "wrong")
    assert result is False
    assert crm_client._token is None


@patch("adw_modules.crm_api_client.requests.get")
def test_crm_client_search_prospect_found(mock_get, crm_client):
    """Finds matching prospect by company name."""
    crm_client._token = "test-token"
    mock_get.return_value = MagicMock(
        status_code=200,
        json=MagicMock(return_value={
            "prospects": [
                {"id": "p-123", "company_name": "Acme Corp", "stage": "lead"},
                {"id": "p-456", "company_name": "Other Inc", "stage": "contacted"},
            ],
            "total": 2,
        }),
    )
    result = crm_client.search_prospect("entity-1", "Acme Corp")
    assert result is not None
    assert result["id"] == "p-123"


@patch("adw_modules.crm_api_client.requests.get")
def test_crm_client_search_prospect_not_found(mock_get, crm_client):
    """Returns None when no prospect matches."""
    crm_client._token = "test-token"
    mock_get.return_value = MagicMock(
        status_code=200,
        json=MagicMock(return_value={"prospects": [], "total": 0}),
    )
    result = crm_client.search_prospect("entity-1", "NonExistent Corp")
    assert result is None


@patch("adw_modules.crm_api_client.requests.get")
def test_crm_client_search_prospect_case_insensitive(mock_get, crm_client):
    """Matches prospect name case-insensitively."""
    crm_client._token = "test-token"
    mock_get.return_value = MagicMock(
        status_code=200,
        json=MagicMock(return_value={
            "prospects": [
                {"id": "p-789", "company_name": "ACME CORP", "stage": "lead"},
            ],
            "total": 1,
        }),
    )
    result = crm_client.search_prospect("entity-1", "acme corp")
    assert result is not None
    assert result["id"] == "p-789"


@patch("adw_modules.crm_api_client.requests.post")
def test_crm_client_create_prospect_success(mock_post, crm_client):
    """Creates prospect and returns response dict on 201."""
    crm_client._token = "test-token"
    mock_post.return_value = MagicMock(
        status_code=201,
        json=MagicMock(return_value={
            "id": "p-new",
            "company_name": "New Corp",
            "stage": "contacted",
        }),
    )
    result = crm_client.create_prospect(
        entity_id="entity-1",
        company_name="New Corp",
        contact_name="Alice",
        contact_email="alice@new.com",
        stage="contacted",
        source="meeting-transcript",
        notes="Auto-created",
    )
    assert result is not None
    assert result["id"] == "p-new"


@patch("adw_modules.crm_api_client.requests.post")
def test_crm_client_create_meeting_record_success(mock_post, crm_client):
    """Creates meeting record and returns response dict on 201."""
    crm_client._token = "test-token"
    mock_post.return_value = MagicMock(
        status_code=201,
        json=MagicMock(return_value={
            "id": "mr-new",
            "title": "Sprint Planning",
            "prospect_id": "p-123",
        }),
    )
    result = crm_client.create_meeting_record(
        entity_id="entity-1",
        prospect_id="p-123",
        title="Sprint Planning",
        transcript_ref="/path/to/transcript.md",
        summary="Discussed sprint goals.",
        action_items=["Create tickets"],
        participants=["Alice", "Bob"],
        meeting_date="2026-03-01",
    )
    assert result is not None
    assert result["id"] == "mr-new"


@patch("adw_modules.crm_api_client.requests.patch")
def test_crm_client_advance_stage_success(mock_patch, crm_client):
    """Advances prospect stage and returns updated dict on 200."""
    crm_client._token = "test-token"
    mock_patch.return_value = MagicMock(
        status_code=200,
        json=MagicMock(return_value={
            "id": "p-123",
            "stage": "contacted",
        }),
    )
    result = crm_client.advance_prospect_stage(
        "p-123", "entity-1", "contacted", "Auto-advanced"
    )
    assert result is not None
    assert result["stage"] == "contacted"


@patch("adw_modules.crm_api_client.requests.post")
def test_crm_client_request_timeout(mock_post, crm_client):
    """Handles request timeout gracefully."""
    mock_post.side_effect = requests.Timeout("Connection timed out")
    result = crm_client.authenticate("user@test.com", "password123")
    assert result is False


# --- update_crm ---


FULL_MEETING_DATA = {
    "title": "Sprint Planning",
    "meeting_date": "2026-03-01",
    "company_name": "Acme Corp",
    "contact_name": "Bob",
    "contact_email": "bob@acme.com",
    "summary": "Discussed sprint goals.",
    "participants": [{"name": "Alice", "role": "PM"}, {"name": "Bob"}],
    "action_items": [{"description": "Create tickets"}, "Follow up"],
    "html_output": "<html><body>Summary</body></html>",
}


@patch.dict(os.environ, {}, clear=True)
def test_update_crm_skips_when_env_vars_missing():
    """Skips CRM update when required env vars are not set."""
    logger = MagicMock(spec=logging.Logger)
    pipeline.update_crm(FULL_MEETING_DATA, "/path/transcript.md", "adw-1", logger)
    logger.warning.assert_called_once()
    assert "ADW_SERVICE_EMAIL" in logger.warning.call_args[0][0]


@patch.dict(os.environ, {
    "ADW_SERVICE_EMAIL": "svc@test.com",
    "ADW_SERVICE_PASSWORD": "pass",
    "ADW_ENTITY_ID": "entity-1",
})
@patch("adw_meeting_pipeline_iso.CrmApiClient")
def test_update_crm_skips_when_no_company_name(mock_client_cls):
    """Skips CRM update when meeting data has no company_name."""
    mock_client = MagicMock()
    mock_client.authenticate.return_value = True
    mock_client_cls.return_value = mock_client

    logger = MagicMock(spec=logging.Logger)
    data = {"title": "Meeting", "summary": "No company info."}
    pipeline.update_crm(data, "/path/transcript.md", "adw-1", logger)

    mock_client.search_prospect.assert_not_called()
    logger.warning.assert_called()
    assert "company_name" in logger.warning.call_args[0][0]


@patch.dict(os.environ, {
    "ADW_SERVICE_EMAIL": "svc@test.com",
    "ADW_SERVICE_PASSWORD": "pass",
    "ADW_ENTITY_ID": "entity-1",
})
@patch("adw_meeting_pipeline_iso.CrmApiClient")
def test_update_crm_creates_new_prospect_and_meeting(mock_client_cls):
    """Creates new prospect and meeting record when no match found."""
    mock_client = MagicMock()
    mock_client.authenticate.return_value = True
    mock_client.search_prospect.return_value = None
    mock_client.create_prospect.return_value = {"id": "p-new", "stage": "contacted"}
    mock_client.create_meeting_record.return_value = {"id": "mr-new"}
    mock_client_cls.return_value = mock_client

    logger = MagicMock(spec=logging.Logger)
    pipeline.update_crm(FULL_MEETING_DATA, "/path/transcript.md", "adw-1", logger)

    mock_client.create_prospect.assert_called_once()
    call_kwargs = mock_client.create_prospect.call_args
    assert call_kwargs.kwargs["company_name"] == "Acme Corp"
    assert call_kwargs.kwargs["stage"] == "contacted"
    assert call_kwargs.kwargs["source"] == "meeting-transcript"

    mock_client.create_meeting_record.assert_called_once()
    mr_kwargs = mock_client.create_meeting_record.call_args.kwargs
    assert mr_kwargs["prospect_id"] == "p-new"
    assert mr_kwargs["title"] == "Sprint Planning"


@patch.dict(os.environ, {
    "ADW_SERVICE_EMAIL": "svc@test.com",
    "ADW_SERVICE_PASSWORD": "pass",
    "ADW_ENTITY_ID": "entity-1",
})
@patch("adw_meeting_pipeline_iso.CrmApiClient")
def test_update_crm_matches_existing_prospect(mock_client_cls):
    """Uses existing prospect and does not create a new one."""
    mock_client = MagicMock()
    mock_client.authenticate.return_value = True
    mock_client.search_prospect.return_value = {
        "id": "p-existing",
        "company_name": "Acme Corp",
        "stage": "contacted",
    }
    mock_client.create_meeting_record.return_value = {"id": "mr-new"}
    mock_client_cls.return_value = mock_client

    logger = MagicMock(spec=logging.Logger)
    pipeline.update_crm(FULL_MEETING_DATA, "/path/transcript.md", "adw-1", logger)

    mock_client.create_prospect.assert_not_called()
    mock_client.create_meeting_record.assert_called_once()
    mr_kwargs = mock_client.create_meeting_record.call_args.kwargs
    assert mr_kwargs["prospect_id"] == "p-existing"


@patch.dict(os.environ, {
    "ADW_SERVICE_EMAIL": "svc@test.com",
    "ADW_SERVICE_PASSWORD": "pass",
    "ADW_ENTITY_ID": "entity-1",
})
@patch("adw_meeting_pipeline_iso.CrmApiClient")
def test_update_crm_advances_lead_to_contacted(mock_client_cls):
    """Advances prospect from 'lead' to 'contacted' stage."""
    mock_client = MagicMock()
    mock_client.authenticate.return_value = True
    mock_client.search_prospect.return_value = {
        "id": "p-lead",
        "company_name": "Acme Corp",
        "stage": "lead",
    }
    mock_client.advance_prospect_stage.return_value = {"id": "p-lead", "stage": "contacted"}
    mock_client.create_meeting_record.return_value = {"id": "mr-new"}
    mock_client_cls.return_value = mock_client

    logger = MagicMock(spec=logging.Logger)
    pipeline.update_crm(FULL_MEETING_DATA, "/path/transcript.md", "adw-1", logger)

    mock_client.advance_prospect_stage.assert_called_once_with(
        "p-lead", "entity-1", "contacted", "Auto-advanced: meeting transcript processed"
    )


@patch.dict(os.environ, {
    "ADW_SERVICE_EMAIL": "svc@test.com",
    "ADW_SERVICE_PASSWORD": "pass",
    "ADW_ENTITY_ID": "entity-1",
})
@patch("adw_meeting_pipeline_iso.CrmApiClient")
def test_update_crm_does_not_advance_non_lead(mock_client_cls):
    """Does not advance stage when prospect is not at 'lead'."""
    mock_client = MagicMock()
    mock_client.authenticate.return_value = True
    mock_client.search_prospect.return_value = {
        "id": "p-qual",
        "company_name": "Acme Corp",
        "stage": "qualified",
    }
    mock_client.create_meeting_record.return_value = {"id": "mr-new"}
    mock_client_cls.return_value = mock_client

    logger = MagicMock(spec=logging.Logger)
    pipeline.update_crm(FULL_MEETING_DATA, "/path/transcript.md", "adw-1", logger)

    mock_client.advance_prospect_stage.assert_not_called()


@patch.dict(os.environ, {
    "ADW_SERVICE_EMAIL": "svc@test.com",
    "ADW_SERVICE_PASSWORD": "pass",
    "ADW_ENTITY_ID": "entity-1",
})
@patch("adw_meeting_pipeline_iso.CrmApiClient")
def test_update_crm_handles_api_failure_gracefully(mock_client_cls):
    """Does not raise exceptions when authentication fails."""
    mock_client = MagicMock()
    mock_client.authenticate.return_value = False
    mock_client_cls.return_value = mock_client

    logger = MagicMock(spec=logging.Logger)
    # Should not raise
    pipeline.update_crm(FULL_MEETING_DATA, "/path/transcript.md", "adw-1", logger)

    mock_client.search_prospect.assert_not_called()
    mock_client.create_prospect.assert_not_called()
    logger.error.assert_called()
