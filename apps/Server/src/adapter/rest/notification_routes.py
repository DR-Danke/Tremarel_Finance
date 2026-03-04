"""Notification endpoint routes."""

from datetime import date
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.core.services.event_dispatcher import event_dispatcher
from src.core.services.event_service import event_service
from src.core.services.notification_scheduler import (
    process_document_expiration_alerts,
    send_morning_task_summaries,
)
from src.interface.notification_dto import (
    DailySummaryTriggerResponseDTO,
    EventDispatchResponseDTO,
    NotificationLogResponseDTO,
    PendingEventsResponseDTO,
)
from src.repository.notification_log_repository import notification_log_repository
from src.repository.restaurant_repository import restaurant_repository

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.post("/send-daily-summaries", response_model=DailySummaryTriggerResponseDTO)
async def trigger_daily_summaries(
    restaurant_id: UUID = Query(..., description="Restaurant UUID to send summaries for"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> DailySummaryTriggerResponseDTO:
    """
    Trigger sending daily task summary WhatsApp messages to all employees.

    Designed to be called manually or by an external cron job every morning.

    Args:
        restaurant_id: Restaurant UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        DailySummaryTriggerResponseDTO with send counts and results
    """
    print(f"INFO [NotificationRoutes]: Send daily summaries request from user {current_user['email']} (restaurant={restaurant_id})")

    user_id = UUID(current_user["id"])
    try:
        result = await send_morning_task_summaries(db, user_id, restaurant_id)
        print(f"INFO [NotificationRoutes]: Daily summaries sent: {result['sent_count']} sent, {result['skipped_count']} skipped")
        return result
    except PermissionError as e:
        print(f"ERROR [NotificationRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [NotificationRoutes]: Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        print(f"ERROR [NotificationRoutes]: Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send daily summaries",
        )


@router.get("/log", response_model=List[NotificationLogResponseDTO])
async def list_notification_logs(
    restaurant_id: UUID = Query(..., description="Restaurant UUID to query logs for"),
    channel: Optional[str] = Query(None, description="Filter by notification channel"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by send status"),
    limit: int = Query(50, description="Maximum number of results", ge=1, le=500),
    offset: int = Query(0, description="Number of results to skip", ge=0),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[NotificationLogResponseDTO]:
    """
    Query notification log entries for a restaurant.

    Args:
        restaurant_id: Restaurant UUID
        channel: Optional channel filter
        status_filter: Optional status filter
        limit: Maximum number of results
        offset: Number of results to skip
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of NotificationLogResponseDTO objects
    """
    print(f"INFO [NotificationRoutes]: List notification logs request from user {current_user['email']} (restaurant={restaurant_id})")

    try:
        logs = notification_log_repository.get_by_restaurant(
            db, restaurant_id, channel_filter=channel, status_filter=status_filter,
            limit=limit, offset=offset,
        )
        print(f"INFO [NotificationRoutes]: Returning {len(logs)} notification log entries")
        return [NotificationLogResponseDTO.model_validate(log, from_attributes=True) for log in logs]
    except Exception as e:
        print(f"ERROR [NotificationRoutes]: Failed to query logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to query notification logs",
        )


@router.post("/process-expiration-alerts")
async def trigger_expiration_alerts(
    restaurant_id: UUID = Query(..., description="Restaurant UUID to process alerts for"),
    target_date: Optional[date] = Query(None, description="Target date for alerts (defaults to today)"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> dict:
    """
    Process due document expiration alert events and send notifications.

    Designed to be called manually or by an external cron job.

    Args:
        restaurant_id: Restaurant UUID
        target_date: Optional target date (defaults to today)
        db: Database session
        current_user: Current authenticated user

    Returns:
        Summary dict with processed, sent, skipped, failed counts
    """
    print(f"INFO [NotificationRoutes]: Processing expiration alerts for restaurant {restaurant_id}")

    user_id = UUID(current_user["id"])
    try:
        result = await process_document_expiration_alerts(db, user_id, restaurant_id, target_date)
        print(f"INFO [NotificationRoutes]: Expiration alerts processed: {result['processed']} processed, {result['sent']} sent")
        return result
    except PermissionError as e:
        print(f"ERROR [NotificationRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [NotificationRoutes]: Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        print(f"ERROR [NotificationRoutes]: Unexpected error processing alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process expiration alerts",
        )


@router.post("/dispatch", response_model=EventDispatchResponseDTO)
async def dispatch_due_events(
    restaurant_id: UUID = Query(..., description="Restaurant UUID to dispatch events for"),
    target_date: Optional[date] = Query(None, description="Target date for dispatch (defaults to today)"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> EventDispatchResponseDTO:
    """
    Manually trigger event notification dispatch for a restaurant.

    Processes all pending due events and sends notifications via appropriate channels.

    Args:
        restaurant_id: Restaurant UUID
        target_date: Optional target date (defaults to today)
        db: Database session
        current_user: Current authenticated user

    Returns:
        EventDispatchResponseDTO with dispatch results
    """
    print(f"INFO [NotificationRoutes]: Dispatch request from user {current_user['email']} (restaurant={restaurant_id})")

    user_id = UUID(current_user["id"])
    try:
        result = await event_dispatcher.process_due_events(db, user_id, restaurant_id, target_date)
        print(f"INFO [NotificationRoutes]: Dispatch complete: {result['sent']} sent, {result['skipped']} skipped, {result['failed']} failed")
        return result
    except PermissionError as e:
        print(f"ERROR [NotificationRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [NotificationRoutes]: Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        print(f"ERROR [NotificationRoutes]: Unexpected error dispatching events: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to dispatch event notifications",
        )


@router.get("/pending", response_model=PendingEventsResponseDTO)
async def get_pending_events(
    restaurant_id: UUID = Query(..., description="Restaurant UUID to query pending events for"),
    target_date: Optional[date] = Query(None, description="Target date (defaults to today)"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> PendingEventsResponseDTO:
    """
    Get count and list of pending due events for a restaurant.

    Args:
        restaurant_id: Restaurant UUID
        target_date: Optional target date (defaults to today)
        db: Database session
        current_user: Current authenticated user

    Returns:
        PendingEventsResponseDTO with count and event summaries
    """
    print(f"INFO [NotificationRoutes]: Pending events request from user {current_user['email']} (restaurant={restaurant_id})")

    if target_date is None:
        target_date = date.today()

    user_id = UUID(current_user["id"])
    try:
        due_events = event_service.get_due_events(db, user_id, restaurant_id, target_date)
        pending_events = [e for e in due_events if e.status == "pending"]

        event_summaries = [
            {
                "id": str(e.id),
                "type": e.type,
                "description": getattr(e, "description", None),
                "date": str(e.date),
                "notification_channel": getattr(e, "notification_channel", None),
            }
            for e in pending_events
        ]

        print(f"INFO [NotificationRoutes]: Found {len(pending_events)} pending due events")
        return PendingEventsResponseDTO(
            pending_count=len(pending_events),
            events=event_summaries,
        )
    except PermissionError as e:
        print(f"ERROR [NotificationRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        print(f"ERROR [NotificationRoutes]: Unexpected error querying pending events: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to query pending events",
        )


@router.post("/dispatch-all", response_model=List[EventDispatchResponseDTO])
async def dispatch_all_restaurants(
    target_date: Optional[date] = Query(None, description="Target date for dispatch (defaults to today)"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[EventDispatchResponseDTO]:
    """
    Cron-friendly endpoint that dispatches event notifications for all restaurants.

    Iterates over all restaurants the user has access to and dispatches due events.

    Args:
        target_date: Optional target date (defaults to today)
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of EventDispatchResponseDTO, one per restaurant
    """
    print(f"INFO [NotificationRoutes]: Dispatch-all request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    restaurants = restaurant_repository.get_restaurants_by_user(db, user_id)
    print(f"INFO [NotificationRoutes]: Found {len(restaurants)} restaurants for user")

    results = []
    for restaurant in restaurants:
        try:
            result = await event_dispatcher.process_due_events(db, user_id, restaurant.id, target_date)
            results.append(result)
        except Exception as e:
            print(f"ERROR [NotificationRoutes]: Failed to dispatch for restaurant {restaurant.id}: {str(e)}")
            results.append({"processed": 0, "sent": 0, "skipped": 0, "failed": 0})

    print(f"INFO [NotificationRoutes]: Dispatch-all complete for {len(restaurants)} restaurants")
    return results
