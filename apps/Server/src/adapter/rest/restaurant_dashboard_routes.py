"""Restaurant dashboard endpoint routes."""

from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.core.services.restaurant_dashboard_service import restaurant_dashboard_service
from src.interface.document_dto import DocumentResponseDTO
from src.interface.event_dto import EventResponseDTO
from src.interface.inventory_movement_dto import InventoryMovementResponseDTO
from src.interface.resource_dto import ResourceResponseDTO

router = APIRouter(prefix="/api/restaurant-dashboard", tags=["RestaurantDashboard"])


def _serialize_event(event: object) -> dict:
    """Convert an Event model to a serializable dict via EventResponseDTO."""
    return EventResponseDTO.model_validate(event, from_attributes=True).model_dump(mode="json")


def _serialize_document(doc: object) -> dict:
    """Convert a Document model to a serializable dict via DocumentResponseDTO."""
    return DocumentResponseDTO.model_validate(doc, from_attributes=True).model_dump(mode="json")


def _serialize_resource(resource: object) -> dict:
    """Convert a Resource model to a serializable dict via ResourceResponseDTO."""
    return ResourceResponseDTO.model_validate(resource, from_attributes=True).model_dump(mode="json")


def _serialize_movement(movement: object) -> dict:
    """Convert an InventoryMovement model to a serializable dict via InventoryMovementResponseDTO."""
    return InventoryMovementResponseDTO.model_validate(movement, from_attributes=True).model_dump(mode="json")


@router.get("/{restaurant_id}/overview")
async def get_dashboard_overview(
    restaurant_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> dict:
    """
    Get aggregated operational dashboard overview for a restaurant.

    Returns stat cards, today's tasks, upcoming expirations, low stock items,
    recent movements, and pending alerts.

    Args:
        restaurant_id: Restaurant UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Dashboard overview dictionary
    """
    print(f"INFO [RestaurantDashboard]: Fetching overview for restaurant {restaurant_id} by user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        overview = restaurant_dashboard_service.get_overview(db, user_id, restaurant_id)

        response = {
            "today_tasks": [_serialize_event(e) for e in overview["today_tasks"]],
            "upcoming_expirations": [_serialize_document(d) for d in overview["upcoming_expirations"]],
            "low_stock_items": [_serialize_resource(r) for r in overview["low_stock_items"]],
            "recent_movements": [_serialize_movement(m) for m in overview["recent_movements"]],
            "pending_alerts": [_serialize_event(a) for a in overview["pending_alerts"]],
            "stats": overview["stats"],
        }

        print(f"INFO [RestaurantDashboard]: Overview returned successfully for restaurant {restaurant_id}")
        return response
    except PermissionError as e:
        print(f"ERROR [RestaurantDashboard]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        print(f"ERROR [RestaurantDashboard]: Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load dashboard overview",
        )
