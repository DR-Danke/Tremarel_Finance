"""Notification endpoint routes."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.core.services.notification_scheduler import send_morning_task_summaries
from src.interface.notification_dto import (
    DailySummaryTriggerResponseDTO,
    NotificationLogResponseDTO,
)
from src.repository.notification_log_repository import notification_log_repository

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
