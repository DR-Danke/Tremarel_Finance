"""Pydantic DTOs for meeting record requests and responses."""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MeetingRecordCreateDTO(BaseModel):
    """DTO for creating a new meeting record."""

    entity_id: UUID = Field(..., description="Entity ID this meeting record belongs to")
    prospect_id: UUID = Field(..., description="Prospect this meeting is linked to")
    title: str = Field(
        ..., min_length=1, max_length=500, description="Human-readable meeting title"
    )
    transcript_ref: Optional[str] = Field(
        None, max_length=1000, description="Reference to original transcript file/URL"
    )
    summary: Optional[str] = Field(None, description="Structured summary of the meeting")
    action_items: Optional[List[str]] = Field(
        None, description="Extracted action items from the meeting"
    )
    participants: Optional[List[str]] = Field(
        None, description="Participant names/roles from the meeting"
    )
    html_output: Optional[str] = Field(
        None, description="Formatted HTML content for download"
    )
    meeting_date: Optional[date] = Field(None, description="Date when the meeting occurred")


class MeetingRecordUpdateDTO(BaseModel):
    """DTO for updating an existing meeting record."""

    title: Optional[str] = Field(
        None, min_length=1, max_length=500, description="Human-readable meeting title"
    )
    transcript_ref: Optional[str] = Field(
        None, max_length=1000, description="Reference to original transcript file/URL"
    )
    summary: Optional[str] = Field(None, description="Structured summary of the meeting")
    action_items: Optional[List[str]] = Field(
        None, description="Extracted action items from the meeting"
    )
    participants: Optional[List[str]] = Field(
        None, description="Participant names/roles from the meeting"
    )
    html_output: Optional[str] = Field(
        None, description="Formatted HTML content for download"
    )
    meeting_date: Optional[date] = Field(None, description="Date when the meeting occurred")
    is_active: Optional[bool] = Field(None, description="Active status (soft delete flag)")


class MeetingRecordResponseDTO(BaseModel):
    """DTO for meeting record response."""

    id: UUID = Field(..., description="Meeting record unique identifier")
    entity_id: UUID = Field(..., description="Entity ID this meeting record belongs to")
    prospect_id: UUID = Field(..., description="Prospect this meeting is linked to")
    title: str = Field(..., description="Human-readable meeting title")
    transcript_ref: Optional[str] = Field(None, description="Reference to original transcript")
    summary: Optional[str] = Field(None, description="Structured summary of the meeting")
    action_items: Optional[str] = Field(None, description="JSON-serialized action items")
    participants: Optional[str] = Field(None, description="JSON-serialized participants")
    html_output: Optional[str] = Field(None, description="Formatted HTML content")
    meeting_date: Optional[date] = Field(None, description="Date when the meeting occurred")
    is_active: bool = Field(..., description="Active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = {"from_attributes": True}


class MeetingRecordListResponseDTO(BaseModel):
    """DTO for meeting record list response."""

    meeting_records: List[MeetingRecordResponseDTO] = Field(
        ..., description="List of meeting records"
    )
    total: int = Field(..., description="Total number of meeting records matching filters")


class MeetingRecordFilterDTO(BaseModel):
    """DTO for filtering meeting records."""

    prospect_id: Optional[UUID] = Field(None, description="Filter by prospect")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    meeting_date_from: Optional[date] = Field(None, description="Filter meetings from this date")
    meeting_date_to: Optional[date] = Field(None, description="Filter meetings up to this date")
