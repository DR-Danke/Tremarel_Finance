"""Inventory movement endpoint routes."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.core.services.inventory_service import inventory_service
from src.interface.inventory_movement_dto import (
    InventoryMovementCreateDTO,
    InventoryMovementResponseDTO,
    MovementReason,
)

router = APIRouter(prefix="/api/inventory-movements", tags=["Inventory Movements"])


def _to_response(movement: object) -> InventoryMovementResponseDTO:
    """Convert an InventoryMovement model to InventoryMovementResponseDTO."""
    return InventoryMovementResponseDTO.model_validate(movement, from_attributes=True)


@router.post("", response_model=InventoryMovementResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_movement(
    data: InventoryMovementCreateDTO,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> InventoryMovementResponseDTO:
    """
    Create an inventory movement and update resource stock.

    Args:
        data: Movement creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        InventoryMovementResponseDTO: Created movement information
    """
    print(f"INFO [InventoryMovementRoutes]: Create movement request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        movement = inventory_service.create_movement(db, user_id, data)
        print(f"INFO [InventoryMovementRoutes]: Movement {movement.id} created successfully")
        return _to_response(movement)
    except PermissionError as e:
        print(f"ERROR [InventoryMovementRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            print(f"ERROR [InventoryMovementRoutes]: Not found: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg,
            )
        print(f"ERROR [InventoryMovementRoutes]: Validation error: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )


@router.get("", response_model=List[InventoryMovementResponseDTO])
async def list_movements(
    resource_id: Optional[UUID] = Query(None, description="Filter movements by resource UUID"),
    restaurant_id: Optional[UUID] = Query(None, description="Filter movements by restaurant UUID"),
    date_from: Optional[datetime] = Query(None, description="Filter movements from this date"),
    date_to: Optional[datetime] = Query(None, description="Filter movements until this date"),
    reason: Optional[MovementReason] = Query(None, description="Filter movements by reason"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[InventoryMovementResponseDTO]:
    """
    List inventory movements filtered by resource or restaurant.

    Args:
        resource_id: Optional resource UUID filter
        restaurant_id: Optional restaurant UUID filter
        date_from: Optional start date filter
        date_to: Optional end date filter
        reason: Optional reason filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of InventoryMovementResponseDTO objects
    """
    print(f"INFO [InventoryMovementRoutes]: List movements request from user {current_user['email']}")

    user_id = UUID(current_user["id"])

    if resource_id is None and restaurant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either resource_id or restaurant_id is required",
        )

    try:
        if resource_id is not None:
            movements = inventory_service.get_movements_by_resource(
                db, user_id, resource_id, date_from, date_to
            )
        else:
            reason_value = reason.value if reason else None
            movements = inventory_service.get_movements_by_restaurant(
                db, user_id, restaurant_id, date_from, date_to, reason_value
            )

        print(f"INFO [InventoryMovementRoutes]: Returning {len(movements)} movements")
        return [_to_response(m) for m in movements]
    except PermissionError as e:
        print(f"ERROR [InventoryMovementRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [InventoryMovementRoutes]: Not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
