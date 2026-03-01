"""Tests for MeetingRecord model and DTOs."""

from datetime import date, datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.interface.meeting_record_dto import (
    MeetingRecordCreateDTO,
    MeetingRecordFilterDTO,
    MeetingRecordListResponseDTO,
    MeetingRecordResponseDTO,
    MeetingRecordUpdateDTO,
)
from src.models.meeting_record import MeetingRecord


# ============================================================================
# MeetingRecordCreateDTO Tests
# ============================================================================


def test_meeting_record_create_dto_valid() -> None:
    """Test valid creation DTO with all fields."""
    entity_id = uuid4()
    prospect_id = uuid4()
    dto = MeetingRecordCreateDTO(
        entity_id=entity_id,
        prospect_id=prospect_id,
        title="Q1 Pipeline Review",
        transcript_ref="s3://bucket/transcripts/meeting-001.txt",
        summary="Discussed Q1 pipeline status and next steps.",
        action_items=["Follow up with client", "Send proposal by Friday"],
        participants=["John Doe (Sales)", "Jane Smith (CTO)"],
        html_output="<h1>Q1 Pipeline Review</h1><p>Summary...</p>",
        meeting_date=date(2026, 2, 15),
    )
    assert dto.entity_id == entity_id
    assert dto.prospect_id == prospect_id
    assert dto.title == "Q1 Pipeline Review"
    assert dto.transcript_ref == "s3://bucket/transcripts/meeting-001.txt"
    assert dto.summary == "Discussed Q1 pipeline status and next steps."
    assert dto.action_items == ["Follow up with client", "Send proposal by Friday"]
    assert dto.participants == ["John Doe (Sales)", "Jane Smith (CTO)"]
    assert dto.html_output == "<h1>Q1 Pipeline Review</h1><p>Summary...</p>"
    assert dto.meeting_date == date(2026, 2, 15)
    print("INFO [TestMeetingRecord]: test_meeting_record_create_dto_valid - PASSED")


def test_meeting_record_create_dto_minimal() -> None:
    """Test valid creation DTO with only required fields."""
    entity_id = uuid4()
    prospect_id = uuid4()
    dto = MeetingRecordCreateDTO(
        entity_id=entity_id,
        prospect_id=prospect_id,
        title="Minimal Meeting",
    )
    assert dto.entity_id == entity_id
    assert dto.prospect_id == prospect_id
    assert dto.title == "Minimal Meeting"
    assert dto.transcript_ref is None
    assert dto.summary is None
    assert dto.action_items is None
    assert dto.participants is None
    assert dto.html_output is None
    assert dto.meeting_date is None
    print("INFO [TestMeetingRecord]: test_meeting_record_create_dto_minimal - PASSED")


def test_meeting_record_create_dto_empty_title_rejected() -> None:
    """Test that empty title string is rejected by min_length=1."""
    with pytest.raises(ValidationError) as exc_info:
        MeetingRecordCreateDTO(
            entity_id=uuid4(),
            prospect_id=uuid4(),
            title="",
        )
    assert "title" in str(exc_info.value)
    print("INFO [TestMeetingRecord]: test_meeting_record_create_dto_empty_title_rejected - PASSED")


def test_meeting_record_create_dto_title_too_long_rejected() -> None:
    """Test that title exceeding 500 characters is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        MeetingRecordCreateDTO(
            entity_id=uuid4(),
            prospect_id=uuid4(),
            title="A" * 501,
        )
    assert "title" in str(exc_info.value)
    print("INFO [TestMeetingRecord]: test_meeting_record_create_dto_title_too_long_rejected - PASSED")


def test_meeting_record_create_dto_transcript_ref_too_long_rejected() -> None:
    """Test that transcript_ref exceeding 1000 characters is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        MeetingRecordCreateDTO(
            entity_id=uuid4(),
            prospect_id=uuid4(),
            title="Valid Title",
            transcript_ref="x" * 1001,
        )
    assert "transcript_ref" in str(exc_info.value)
    print("INFO [TestMeetingRecord]: test_meeting_record_create_dto_transcript_ref_too_long_rejected - PASSED")


def test_meeting_record_create_dto_empty_lists_accepted() -> None:
    """Test that empty action_items and participants lists are accepted."""
    dto = MeetingRecordCreateDTO(
        entity_id=uuid4(),
        prospect_id=uuid4(),
        title="Empty Lists Meeting",
        action_items=[],
        participants=[],
    )
    assert dto.action_items == []
    assert dto.participants == []
    print("INFO [TestMeetingRecord]: test_meeting_record_create_dto_empty_lists_accepted - PASSED")


# ============================================================================
# MeetingRecordUpdateDTO Tests
# ============================================================================


def test_meeting_record_update_dto_partial() -> None:
    """Test partial update with only some fields."""
    dto = MeetingRecordUpdateDTO(
        title="Updated Title",
        summary="Updated summary content.",
    )
    assert dto.title == "Updated Title"
    assert dto.summary == "Updated summary content."
    assert dto.transcript_ref is None
    assert dto.action_items is None
    assert dto.participants is None
    assert dto.html_output is None
    assert dto.meeting_date is None
    assert dto.is_active is None
    print("INFO [TestMeetingRecord]: test_meeting_record_update_dto_partial - PASSED")


def test_meeting_record_update_dto_empty() -> None:
    """Test update DTO with no fields set (all optional)."""
    dto = MeetingRecordUpdateDTO()
    assert dto.title is None
    assert dto.transcript_ref is None
    assert dto.summary is None
    assert dto.action_items is None
    assert dto.participants is None
    assert dto.html_output is None
    assert dto.meeting_date is None
    assert dto.is_active is None
    print("INFO [TestMeetingRecord]: test_meeting_record_update_dto_empty - PASSED")


# ============================================================================
# MeetingRecordResponseDTO Tests
# ============================================================================


def test_meeting_record_response_dto_from_attributes() -> None:
    """Test response DTO from mock model object."""
    mock_record = MagicMock(spec=MeetingRecord)
    mock_record.id = uuid4()
    mock_record.entity_id = uuid4()
    mock_record.prospect_id = uuid4()
    mock_record.title = "Response Meeting"
    mock_record.transcript_ref = "s3://bucket/transcript.txt"
    mock_record.summary = "Meeting summary here."
    mock_record.action_items = '["Action 1", "Action 2"]'
    mock_record.participants = '["Alice (PM)", "Bob (Dev)"]'
    mock_record.html_output = "<p>HTML output</p>"
    mock_record.meeting_date = date(2026, 2, 20)
    mock_record.is_active = True
    mock_record.created_at = datetime(2026, 2, 20, 10, 30, 0)
    mock_record.updated_at = None

    dto = MeetingRecordResponseDTO.model_validate(mock_record, from_attributes=True)
    assert dto.id == mock_record.id
    assert dto.entity_id == mock_record.entity_id
    assert dto.prospect_id == mock_record.prospect_id
    assert dto.title == "Response Meeting"
    assert dto.transcript_ref == "s3://bucket/transcript.txt"
    assert dto.summary == "Meeting summary here."
    assert dto.action_items == '["Action 1", "Action 2"]'
    assert dto.participants == '["Alice (PM)", "Bob (Dev)"]'
    assert dto.html_output == "<p>HTML output</p>"
    assert dto.meeting_date == date(2026, 2, 20)
    assert dto.is_active is True
    assert dto.updated_at is None
    print("INFO [TestMeetingRecord]: test_meeting_record_response_dto_from_attributes - PASSED")


# ============================================================================
# MeetingRecordFilterDTO Tests
# ============================================================================


def test_meeting_record_filter_dto_defaults() -> None:
    """Test filter DTO with all None defaults."""
    dto = MeetingRecordFilterDTO()
    assert dto.prospect_id is None
    assert dto.is_active is None
    assert dto.meeting_date_from is None
    assert dto.meeting_date_to is None
    print("INFO [TestMeetingRecord]: test_meeting_record_filter_dto_defaults - PASSED")


def test_meeting_record_filter_dto_with_values() -> None:
    """Test filter DTO with specific filter values."""
    prospect_id = uuid4()
    dto = MeetingRecordFilterDTO(
        prospect_id=prospect_id,
        is_active=True,
        meeting_date_from=date(2026, 1, 1),
        meeting_date_to=date(2026, 12, 31),
    )
    assert dto.prospect_id == prospect_id
    assert dto.is_active is True
    assert dto.meeting_date_from == date(2026, 1, 1)
    assert dto.meeting_date_to == date(2026, 12, 31)
    print("INFO [TestMeetingRecord]: test_meeting_record_filter_dto_with_values - PASSED")


# ============================================================================
# MeetingRecordListResponseDTO Tests
# ============================================================================


def test_meeting_record_list_response_dto() -> None:
    """Test list response with total count."""
    record_id = uuid4()
    entity_id = uuid4()
    prospect_id = uuid4()
    now = datetime(2026, 2, 1, 12, 0, 0)

    response_dto = MeetingRecordResponseDTO(
        id=record_id,
        entity_id=entity_id,
        prospect_id=prospect_id,
        title="List Meeting",
        transcript_ref=None,
        summary=None,
        action_items=None,
        participants=None,
        html_output=None,
        meeting_date=None,
        is_active=True,
        created_at=now,
        updated_at=None,
    )

    list_dto = MeetingRecordListResponseDTO(
        meeting_records=[response_dto],
        total=1,
    )
    assert len(list_dto.meeting_records) == 1
    assert list_dto.total == 1
    assert list_dto.meeting_records[0].title == "List Meeting"
    print("INFO [TestMeetingRecord]: test_meeting_record_list_response_dto - PASSED")


# ============================================================================
# MeetingRecord Model Tests
# ============================================================================


def test_meeting_record_model_tablename() -> None:
    """Test MeetingRecord model has correct table name."""
    assert MeetingRecord.__tablename__ == "meeting_records"
    print("INFO [TestMeetingRecord]: test_meeting_record_model_tablename - PASSED")


def test_meeting_record_model_repr() -> None:
    """Test MeetingRecord model __repr__ method."""
    record = MeetingRecord()
    record.id = uuid4()
    record.title = "Repr Meeting"
    record.prospect_id = uuid4()

    repr_str = repr(record)
    assert "MeetingRecord" in repr_str
    assert "Repr Meeting" in repr_str
    assert str(record.prospect_id) in repr_str
    print("INFO [TestMeetingRecord]: test_meeting_record_model_repr - PASSED")
