"""Restaurant endpoint routes."""

from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.adapter.rest.rbac_dependencies import require_roles
from src.core.services.restaurant_service import restaurant_service
from src.interface.restaurant_dto import (
    RestaurantCreateDTO,
    RestaurantResponseDTO,
    RestaurantUpdateDTO,
)

router = APIRouter(prefix="/api/restaurants", tags=["Restaurants"])


@router.post("", response_model=RestaurantResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    data: RestaurantCreateDTO,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> RestaurantResponseDTO:
    """
    Create a new restaurant.

    Creates a new restaurant and adds the current user as owner and admin.

    Args:
        data: Restaurant creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        RestaurantResponseDTO: Created restaurant information
    """
    print(f"INFO [RestaurantRoutes]: Create restaurant request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        restaurant = restaurant_service.create_restaurant(db, user_id, data)
        print(f"INFO [RestaurantRoutes]: Restaurant '{restaurant.name}' created successfully")
        return RestaurantResponseDTO.model_validate(restaurant)
    except PermissionError as e:
        print(f"ERROR [RestaurantRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [RestaurantRoutes]: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("", response_model=List[RestaurantResponseDTO])
async def list_restaurants(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[RestaurantResponseDTO]:
    """
    List all restaurants the current user belongs to.

    Args:
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of RestaurantResponseDTO objects
    """
    print(f"INFO [RestaurantRoutes]: List restaurants request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    restaurants = restaurant_service.get_user_restaurants(db, user_id)

    print(f"INFO [RestaurantRoutes]: Returning {len(restaurants)} restaurants")
    return [RestaurantResponseDTO.model_validate(r) for r in restaurants]


@router.get("/{restaurant_id}", response_model=RestaurantResponseDTO)
async def get_restaurant(
    restaurant_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> RestaurantResponseDTO:
    """
    Get a specific restaurant by ID.

    Args:
        restaurant_id: Restaurant UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        RestaurantResponseDTO: Restaurant information

    Raises:
        HTTPException: 403 if user doesn't have access, 404 if not found
    """
    print(f"INFO [RestaurantRoutes]: Get restaurant {restaurant_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        restaurant = restaurant_service.get_restaurant(db, restaurant_id, user_id)
        print(f"INFO [RestaurantRoutes]: Returning restaurant '{restaurant.name}'")
        return RestaurantResponseDTO.model_validate(restaurant)
    except PermissionError as e:
        print(f"ERROR [RestaurantRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [RestaurantRoutes]: Restaurant not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/{restaurant_id}", response_model=RestaurantResponseDTO)
async def update_restaurant(
    restaurant_id: UUID,
    data: RestaurantUpdateDTO,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> RestaurantResponseDTO:
    """
    Update a restaurant.

    Only owner or admin can update restaurant.

    Args:
        restaurant_id: Restaurant UUID
        data: Restaurant update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        RestaurantResponseDTO: Updated restaurant information

    Raises:
        HTTPException: 403 if insufficient permissions, 404 if not found
    """
    print(f"INFO [RestaurantRoutes]: Update restaurant {restaurant_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        restaurant = restaurant_service.update_restaurant(db, restaurant_id, user_id, data)
        print(f"INFO [RestaurantRoutes]: Restaurant '{restaurant.name}' updated successfully")
        return RestaurantResponseDTO.model_validate(restaurant)
    except PermissionError as e:
        print(f"ERROR [RestaurantRoutes]: Permission denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [RestaurantRoutes]: Restaurant not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_restaurant(
    restaurant_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "manager"])),
) -> None:
    """
    Delete a restaurant.

    Only admin or manager roles can delete.

    Args:
        restaurant_id: Restaurant UUID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: 403 if not owner/admin, 404 if not found
    """
    print(f"INFO [RestaurantRoutes]: Delete restaurant {restaurant_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        restaurant_service.delete_restaurant(db, restaurant_id, user_id)
        print(f"INFO [RestaurantRoutes]: Restaurant {restaurant_id} deleted successfully")
    except PermissionError as e:
        print(f"ERROR [RestaurantRoutes]: Permission denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [RestaurantRoutes]: Restaurant not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
