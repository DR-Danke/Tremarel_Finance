"""Pydantic DTOs for notification requests and responses."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class NotificationSendDTO(BaseModel):
    """DTO for sending a notification."""

    channel: str = Field(..., description="Notification channel (e.g., whatsapp, email)")
    recipient: str = Field(..., description="Recipient identifier (phone number or email)")
    message: str = Field(..., description="Message body to send")


class NotificationLogResponseDTO(BaseModel):
    """DTO for notification log entry in responses."""

    id: UUID = Field(..., description="Notification log unique identifier")
    restaurant_id: UUID = Field(..., description="Restaurant UUID")
    channel: str = Field(..., description="Notification channel")
    recipient: str = Field(..., description="Recipient identifier")
    message: Optional[str] = Field(None, description="Message body")
    status: str = Field(..., description="Send status (sent, failed, pending)")
    error_message: Optional[str] = Field(None, description="Error details on failure")
    event_id: Optional[UUID] = Field(None, description="Related event UUID")
    created_at: datetime = Field(..., description="Log entry creation timestamp")

    model_config = {"from_attributes": True}


class NotificationResultDTO(BaseModel):
    """DTO for a single notification send result."""

    person_id: UUID = Field(..., description="Person UUID")
    person_name: str = Field(..., description="Person name")
    recipient: str = Field(..., description="Recipient phone number")
    status: str = Field(..., description="Send status")
    error_message: Optional[str] = Field(None, description="Error details on failure")


class DailySummaryTriggerResponseDTO(BaseModel):
    """DTO for the daily summary trigger endpoint response."""

    total_employees: int = Field(..., description="Total employees processed")
    sent_count: int = Field(..., description="Number of notifications successfully sent")
    skipped_count: int = Field(..., description="Number of employees skipped (no WhatsApp)")
    results: List[NotificationResultDTO] = Field(
        default_factory=list, description="Detailed results per employee"
    )


class EventDispatchResponseDTO(BaseModel):
    """DTO for event dispatch endpoint response."""

    processed: int = Field(..., description="Total events processed")
    sent: int = Field(..., description="Number of notifications successfully sent")
    skipped: int = Field(..., description="Number of events skipped")
    failed: int = Field(..., description="Number of events that failed to send")


class PendingEventsResponseDTO(BaseModel):
    """DTO for pending events query response."""

    pending_count: int = Field(..., description="Number of pending due events")
    events: List[dict] = Field(default_factory=list, description="List of pending event summaries")
