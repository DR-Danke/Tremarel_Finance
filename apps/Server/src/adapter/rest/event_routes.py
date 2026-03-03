"""Event endpoint routes."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.core.services.event_service import event_service
from src.interface.event_dto import (
    EventCreateDTO,
    EventResponseDTO,
    EventStatusUpdateDTO,
    EventUpdateDTO,
    TaskCreateDTO,
)

router = APIRouter(prefix="/api/events", tags=["Events"])


def _to_response(event: object) -> EventResponseDTO:
    """Convert an Event model to EventResponseDTO with computed is_overdue."""
    return EventResponseDTO.model_validate(event, from_attributes=True)


@router.post("", response_model=EventResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_event(
    data: EventCreateDTO,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> EventResponseDTO:
    """
    Create a new event.

    Args:
        data: Event creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        EventResponseDTO: Created event information
    """
    print(f"INFO [EventRoutes]: Create event request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        event = event_service.create_event(db, user_id, data)
        print(f"INFO [EventRoutes]: Event type '{event.type}' created successfully")
        return _to_response(event)
    except PermissionError as e:
        print(f"ERROR [EventRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get("/due", response_model=List[EventResponseDTO])
async def get_due_events(
    restaurant_id: UUID = Query(..., description="Restaurant UUID"),
    target_date: date = Query(..., description="Target date to check for due events"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[EventResponseDTO]:
    """
    Get events due on a specific date for a restaurant.

    Args:
        restaurant_id: Restaurant UUID
        target_date: Target date
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of due EventResponseDTO objects
    """
    print(f"INFO [EventRoutes]: Due events request from user {current_user['email']} (restaurant={restaurant_id}, date={target_date})")

    user_id = UUID(current_user["id"])
    try:
        events = event_service.get_due_events(db, user_id, restaurant_id, target_date)
        print(f"INFO [EventRoutes]: Returning {len(events)} due events")
        return [_to_response(e) for e in events]
    except PermissionError as e:
        print(f"ERROR [EventRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get("", response_model=List[EventResponseDTO])
async def list_events(
    restaurant_id: UUID = Query(..., description="Restaurant UUID to list events for"),
    type: Optional[str] = Query(None, description="Filter by event type"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by event status"),
    date_from: Optional[datetime] = Query(None, description="Filter events from this date"),
    date_to: Optional[datetime] = Query(None, description="Filter events until this date"),
    responsible_id: Optional[UUID] = Query(None, description="Filter by responsible person"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[EventResponseDTO]:
    """
    List all events in a restaurant, with optional filters.

    Args:
        restaurant_id: Restaurant UUID
        type: Optional event type filter
        status_filter: Optional event status filter
        date_from: Optional start date filter
        date_to: Optional end date filter
        responsible_id: Optional responsible person filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of EventResponseDTO objects
    """
    print(f"INFO [EventRoutes]: List events request from user {current_user['email']} (restaurant={restaurant_id})")

    user_id = UUID(current_user["id"])
    try:
        events = event_service.get_events(
            db, user_id, restaurant_id, type, status_filter, date_from, date_to, responsible_id
        )
        print(f"INFO [EventRoutes]: Returning {len(events)} events")
        return [_to_response(e) for e in events]
    except PermissionError as e:
        print(f"ERROR [EventRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post("/tasks", response_model=EventResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreateDTO,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> EventResponseDTO:
    """
    Create a new task (event with type=tarea).

    Args:
        data: Task creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        EventResponseDTO: Created task information
    """
    print(f"INFO [EventRoutes]: Create task request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        event = event_service.create_task(db, user_id, data)
        print(f"INFO [EventRoutes]: Task created successfully with id {event.id}")
        return _to_response(event)
    except PermissionError as e:
        print(f"ERROR [EventRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [EventRoutes]: Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/tasks", response_model=List[EventResponseDTO])
async def get_tasks(
    restaurant_id: UUID = Query(..., description="Restaurant UUID"),
    responsible_id: Optional[UUID] = Query(None, description="Filter by responsible person"),
    date_from: Optional[datetime] = Query(None, description="Filter tasks from this date"),
    date_to: Optional[datetime] = Query(None, description="Filter tasks until this date"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by task status"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[EventResponseDTO]:
    """
    List tasks (events with type=tarea) with optional filtering.

    Args:
        restaurant_id: Restaurant UUID
        responsible_id: Optional responsible person filter
        date_from: Optional start date filter
        date_to: Optional end date filter
        status_filter: Optional status filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of EventResponseDTO objects
    """
    print(f"INFO [EventRoutes]: Get tasks request from user {current_user['email']} (restaurant={restaurant_id})")

    user_id = UUID(current_user["id"])
    try:
        events = event_service.get_tasks(
            db, user_id, restaurant_id, responsible_id, date_from, date_to, status_filter
        )
        print(f"INFO [EventRoutes]: Returning {len(events)} tasks")
        return [_to_response(e) for e in events]
    except PermissionError as e:
        print(f"ERROR [EventRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post("/tasks/flag-overdue")
async def flag_overdue_events(
    restaurant_id: UUID = Query(..., description="Restaurant UUID"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, int]:
    """
    Flag overdue events by bulk-updating pending events past their due date.

    Args:
        restaurant_id: Restaurant UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Dictionary with flagged_count
    """
    print(f"INFO [EventRoutes]: Flag overdue request from user {current_user['email']} (restaurant={restaurant_id})")

    user_id = UUID(current_user["id"])
    try:
        count = event_service.flag_overdue_events(db, user_id, restaurant_id)
        print(f"INFO [EventRoutes]: Flagged {count} events as overdue")
        return {"flagged_count": count}
    except PermissionError as e:
        print(f"ERROR [EventRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get("/{event_id}", response_model=EventResponseDTO)
async def get_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> EventResponseDTO:
    """
    Get a specific event by ID.

    Args:
        event_id: Event UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        EventResponseDTO: Event information
    """
    print(f"INFO [EventRoutes]: Get event {event_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        event = event_service.get_event(db, user_id, event_id)
        print(f"INFO [EventRoutes]: Returning event type '{event.type}'")
        return _to_response(event)
    except PermissionError as e:
        print(f"ERROR [EventRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [EventRoutes]: Event not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/{event_id}", response_model=EventResponseDTO)
async def update_event(
    event_id: UUID,
    data: EventUpdateDTO,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> EventResponseDTO:
    """
    Update an event.

    Args:
        event_id: Event UUID
        data: Event update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        EventResponseDTO: Updated event information
    """
    print(f"INFO [EventRoutes]: Update event {event_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        event = event_service.update_event(db, user_id, event_id, data)
        print(f"INFO [EventRoutes]: Event type '{event.type}' updated successfully")
        return _to_response(event)
    except PermissionError as e:
        print(f"ERROR [EventRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [EventRoutes]: Event not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.patch("/{event_id}/status", response_model=EventResponseDTO)
async def update_event_status(
    event_id: UUID,
    data: EventStatusUpdateDTO,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> EventResponseDTO:
    """
    Update only the status of an event.

    Args:
        event_id: Event UUID
        data: Event status update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        EventResponseDTO: Updated event information
    """
    print(f"INFO [EventRoutes]: Update event status {event_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        event = event_service.update_event_status(db, user_id, event_id, data)
        print(f"INFO [EventRoutes]: Event {event_id} status updated to '{event.status}'")
        return _to_response(event)
    except PermissionError as e:
        print(f"ERROR [EventRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            print(f"ERROR [EventRoutes]: Event not found: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg,
            )
        print(f"ERROR [EventRoutes]: Status transition error: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> None:
    """
    Delete an event.

    Args:
        event_id: Event UUID
        db: Database session
        current_user: Current authenticated user
    """
    print(f"INFO [EventRoutes]: Delete event {event_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        event_service.delete_event(db, user_id, event_id)
        print(f"INFO [EventRoutes]: Event {event_id} deleted successfully")
    except PermissionError as e:
        print(f"ERROR [EventRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [EventRoutes]: Event not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
