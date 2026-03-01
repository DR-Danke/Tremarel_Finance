"""Unit tests for the meeting transcript folder watcher."""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import adw_triggers.trigger_meeting_transcript_watch as watcher


@pytest.fixture(autouse=True)
def reset_shutdown_flag():
    """Reset the shutdown flag before each test."""
    watcher.shutdown_requested = False
    yield
    watcher.shutdown_requested = False


@pytest.fixture
def processed_log_path(tmp_path):
    """Provide a temporary processed log path and patch it into the module."""
    log_path = tmp_path / "meeting_transcript_watch_processed.json"
    with patch.object(watcher, "PROCESSED_LOG", log_path):
        yield log_path


# --- load_processed_log ---


def test_load_processed_log_missing_file(tmp_path):
    """Returns empty state when the log file does not exist."""
    missing = tmp_path / "does_not_exist.json"
    with patch.object(watcher, "PROCESSED_LOG", missing):
        result = watcher.load_processed_log()
    assert result == {"processed_files": {}}


def test_load_processed_log_valid_file(processed_log_path):
    """Returns parsed data when the log file contains valid JSON."""
    data = {"processed_files": {"some/file.md": {"processed_at": "2025-01-01"}}}
    processed_log_path.write_text(json.dumps(data))
    result = watcher.load_processed_log()
    assert result == data


def test_load_processed_log_corrupt_file(processed_log_path):
    """Returns empty state and warns when the log file contains invalid JSON."""
    processed_log_path.write_text("NOT VALID JSON {{{{")
    result = watcher.load_processed_log()
    assert result == {"processed_files": {}}


# --- save_processed_log ---


def test_save_processed_log_creates_parents(tmp_path):
    """Creates parent directories and writes valid JSON."""
    log_path = tmp_path / "nested" / "dir" / "processed.json"
    with patch.object(watcher, "PROCESSED_LOG", log_path):
        data = {"processed_files": {"test.md": {"processed_at": "2025-01-01"}}}
        watcher.save_processed_log(data)
    assert log_path.exists()
    loaded = json.loads(log_path.read_text())
    assert loaded == data


# --- is_processed ---


def test_is_processed_new_file(tmp_path, processed_log_path):
    """Returns False for a file not in the log."""
    test_file = tmp_path / "new_transcript.md"
    test_file.write_text("meeting notes")
    with patch.object(watcher, "_get_repo_root", return_value=tmp_path):
        result = watcher.is_processed(test_file)
    assert result is False


def test_is_processed_already_processed(tmp_path, processed_log_path):
    """Returns True for a file already processed with matching mtime."""
    test_file = tmp_path / "processed_transcript.md"
    test_file.write_text("meeting notes")
    mtime = datetime.fromtimestamp(
        os.path.getmtime(test_file), tz=timezone.utc
    ).isoformat()
    key = str(test_file.resolve().relative_to(tmp_path.resolve()))
    data = {"processed_files": {key: {"file_mtime": mtime}}}
    processed_log_path.write_text(json.dumps(data))
    with patch.object(watcher, "_get_repo_root", return_value=tmp_path):
        result = watcher.is_processed(test_file)
    assert result is True


def test_is_processed_modified_file(tmp_path, processed_log_path):
    """Returns False for a file whose mtime has changed since processing."""
    test_file = tmp_path / "modified_transcript.md"
    test_file.write_text("original notes")
    key = str(test_file.resolve().relative_to(tmp_path.resolve()))
    data = {"processed_files": {key: {"file_mtime": "2020-01-01T00:00:00+00:00"}}}
    processed_log_path.write_text(json.dumps(data))
    with patch.object(watcher, "_get_repo_root", return_value=tmp_path):
        result = watcher.is_processed(test_file)
    assert result is False


# --- mark_processed ---


def test_mark_processed_records_metadata(tmp_path, processed_log_path):
    """Records correct metadata including processed_at, adw_id, file_size, file_mtime."""
    test_file = tmp_path / "transcript.md"
    test_file.write_text("meeting content")
    with patch.object(watcher, "_get_repo_root", return_value=tmp_path):
        watcher.mark_processed(test_file, adw_id="abc12345")
    data = json.loads(processed_log_path.read_text())
    key = str(test_file.resolve().relative_to(tmp_path.resolve()))
    entry = data["processed_files"][key]
    assert "processed_at" in entry
    assert entry["adw_id"] == "abc12345"
    assert entry["file_size"] == len("meeting content")
    assert "file_mtime" in entry


# --- check_transcript_folder ---


def test_check_transcript_folder_finds_files(tmp_path, processed_log_path):
    """Finds new .md and .pdf files, skips dotfiles and README.md."""
    folder = tmp_path / "meeting_transcripts"
    folder.mkdir()
    (folder / "meeting1.md").write_text("notes")
    (folder / "meeting2.pdf").write_text("pdf content")
    (folder / ".hidden.md").write_text("hidden")
    (folder / "README.md").write_text("readme")
    (folder / "notes.txt").write_text("txt file")

    triggered_files = []

    def mock_trigger(filepath):
        triggered_files.append(filepath.name)
        return True

    with patch.object(watcher, "TRANSCRIPT_FOLDER", str(folder)), \
         patch.object(watcher, "_get_repo_root", return_value=tmp_path), \
         patch.object(watcher, "trigger_pipeline", side_effect=mock_trigger):
        watcher.check_transcript_folder()

    assert "meeting1.md" in triggered_files
    assert "meeting2.pdf" in triggered_files
    assert ".hidden.md" not in triggered_files
    assert "README.md" not in triggered_files
    assert "notes.txt" not in triggered_files


def test_check_transcript_folder_creates_missing_folder(tmp_path, processed_log_path):
    """Creates the watched folder if it does not exist."""
    folder = tmp_path / "nonexistent_folder"
    with patch.object(watcher, "TRANSCRIPT_FOLDER", str(folder)):
        watcher.check_transcript_folder()
    assert folder.exists()


def test_check_transcript_folder_empty(tmp_path, processed_log_path):
    """Returns silently for an empty folder."""
    folder = tmp_path / "empty_folder"
    folder.mkdir()
    with patch.object(watcher, "TRANSCRIPT_FOLDER", str(folder)), \
         patch.object(watcher, "trigger_pipeline") as mock_trigger:
        watcher.check_transcript_folder()
    mock_trigger.assert_not_called()


def test_check_transcript_folder_respects_shutdown(tmp_path, processed_log_path):
    """Stops processing when shutdown is requested."""
    watcher.shutdown_requested = True
    folder = tmp_path / "transcripts"
    folder.mkdir()
    (folder / "meeting.md").write_text("notes")
    with patch.object(watcher, "TRANSCRIPT_FOLDER", str(folder)), \
         patch.object(watcher, "trigger_pipeline") as mock_trigger:
        watcher.check_transcript_folder()
    mock_trigger.assert_not_called()


# --- trigger_pipeline ---


def test_trigger_pipeline_missing_script(tmp_path):
    """Returns False when the pipeline script does not exist."""
    transcript = tmp_path / "meeting.md"
    transcript.write_text("notes")
    # The pipeline script path is derived from __file__, so it won't exist in tests
    result = watcher.trigger_pipeline(transcript)
    assert result is False


# --- signal_handler ---


def test_signal_handler_sets_shutdown():
    """Sets shutdown_requested flag on signal."""
    watcher.shutdown_requested = False
    watcher.signal_handler(2, None)  # SIGINT = 2
    assert watcher.shutdown_requested is True
