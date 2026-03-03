"""Pydantic DTOs for event requests and responses."""

import datetime as _dt
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class EventType(str, Enum):
    """Enumeration of event types."""

    TAREA = "tarea"
    VENCIMIENTO = "vencimiento"
    PAGO = "pago"
    TURNO = "turno"
    CHECKLIST = "checklist"
    ALERTA_STOCK = "alerta_stock"
    ALERTA_RENTABILIDAD = "alerta_rentabilidad"


class EventFrequency(str, Enum):
    """Enumeration of event recurrence frequencies."""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class EventStatus(str, Enum):
    """Enumeration of event statuses."""

    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class EventCreateDTO(BaseModel):
    """DTO for event creation request."""

    restaurant_id: UUID = Field(..., description="Restaurant UUID this event belongs to")
    type: EventType = Field(..., description="Event type")
    date: datetime = Field(..., description="Event date and time")
    description: Optional[str] = Field(None, description="Event description")
    frequency: EventFrequency = Field(EventFrequency.NONE, description="Recurrence frequency")
    responsible_id: Optional[UUID] = Field(None, description="Person UUID responsible for this event")
    notification_channel: str = Field("email", description="Notification channel (email, push, whatsapp)")
    related_document_id: Optional[UUID] = Field(None, description="Related document UUID for audit linking")


class EventUpdateDTO(BaseModel):
    """DTO for event update request (partial update)."""

    type: Optional[EventType] = Field(None, description="Event type")
    description: Optional[str] = Field(None, description="Event description")
    date: Optional[datetime] = Field(None, description="Event date and time")
    frequency: Optional[EventFrequency] = Field(None, description="Recurrence frequency")
    responsible_id: Optional[UUID] = Field(None, description="Person UUID responsible for this event")
    notification_channel: Optional[str] = Field(None, description="Notification channel")
    related_document_id: Optional[UUID] = Field(None, description="Related document UUID")


class EventStatusUpdateDTO(BaseModel):
    """DTO for event status update request."""

    status: EventStatus = Field(..., description="New event status")


class TaskCreateDTO(BaseModel):
    """DTO for task creation request. Tasks are events with type=tarea."""

    restaurant_id: UUID = Field(..., description="Restaurant UUID this task belongs to")
    date: datetime = Field(..., description="Task due date and time")
    description: Optional[str] = Field(None, description="Task description")
    frequency: EventFrequency = Field(EventFrequency.NONE, description="Recurrence frequency")
    responsible_id: UUID = Field(..., description="Person UUID responsible for this task (required)")
    notification_channel: str = Field("email", description="Notification channel")


class EventResponseDTO(BaseModel):
    """DTO for event information in responses."""

    id: UUID = Field(..., description="Event unique identifier")
    restaurant_id: UUID = Field(..., description="Restaurant UUID")
    type: str = Field(..., description="Event type")
    description: Optional[str] = Field(None, description="Event description")
    date: datetime = Field(..., description="Event date and time")
    frequency: str = Field(..., description="Recurrence frequency")
    responsible_id: Optional[UUID] = Field(None, description="Person UUID responsible")
    notification_channel: str = Field(..., description="Notification channel")
    status: str = Field(..., description="Event status")
    related_document_id: Optional[UUID] = Field(None, description="Related document UUID")
    parent_event_id: Optional[UUID] = Field(None, description="Parent event UUID for recurring instances")
    completed_at: Optional[datetime] = Field(None, description="Timestamp when task was completed")
    is_overdue: bool = Field(False, description="Computed: whether event is overdue")
    created_at: datetime = Field(..., description="Event creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Event last update timestamp")

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def compute_is_overdue(cls, data: object) -> object:
        """Compute is_overdue from status and date."""
        now = datetime.utcnow()

        if hasattr(data, "status"):
            # ORM model object
            event_status = data.status
            event_date = data.date
            is_overdue = event_status == "pending" and event_date is not None and event_date < now

            obj_dict = {
                "id": data.id,
                "restaurant_id": data.restaurant_id,
                "type": data.type,
                "description": getattr(data, "description", None),
                "date": data.date,
                "frequency": getattr(data, "frequency", "none"),
                "responsible_id": getattr(data, "responsible_id", None),
                "notification_channel": getattr(data, "notification_channel", "email"),
                "status": event_status,
                "related_document_id": getattr(data, "related_document_id", None),
                "parent_event_id": getattr(data, "parent_event_id", None),
                "completed_at": getattr(data, "completed_at", None),
                "is_overdue": is_overdue,
                "created_at": data.created_at,
                "updated_at": getattr(data, "updated_at", None),
            }
            return obj_dict
        elif isinstance(data, dict):
            event_status = data.get("status", "pending")
            event_date = data.get("date")
            if isinstance(event_date, datetime):
                data["is_overdue"] = event_status == "pending" and event_date < now
            else:
                data["is_overdue"] = False
        return data


class TaskSummaryItemDTO(BaseModel):
    """DTO for a single task in a daily summary."""

    id: UUID = Field(..., description="Task unique identifier")
    description: Optional[str] = Field(None, description="Task description")
    time: Optional[str] = Field(None, description="Task time in HH:MM format")
    status: str = Field(..., description="Task status (pending or overdue)")
    is_overdue: bool = Field(..., description="Whether the task is overdue")


class DailyTaskSummaryDTO(BaseModel):
    """DTO for an employee's daily task summary."""

    person_id: UUID = Field(..., description="Employee person UUID")
    person_name: str = Field(..., description="Employee name")
    date: _dt.date = Field(..., description="Summary date")
    total_tasks: int = Field(..., description="Total number of pending/overdue tasks")
    overdue_count: int = Field(..., description="Number of overdue tasks")
    tasks: list[TaskSummaryItemDTO] = Field(default_factory=list, description="List of task details")
