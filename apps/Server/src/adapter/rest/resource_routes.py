"""Resource endpoint routes."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.adapter.rest.rbac_dependencies import require_roles
from src.core.services.resource_service import resource_service
from src.interface.resource_dto import (
    ResourceCreateDTO,
    ResourceResponseDTO,
    ResourceType,
    ResourceUpdateDTO,
)

router = APIRouter(prefix="/api/resources", tags=["Resources"])


def _to_response(resource: object) -> ResourceResponseDTO:
    """Convert a Resource model to ResourceResponseDTO with computed is_low_stock."""
    return ResourceResponseDTO.model_validate(resource, from_attributes=True)


@router.post("", response_model=ResourceResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_resource(
    data: ResourceCreateDTO,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> ResourceResponseDTO:
    """
    Create a new resource in a restaurant.

    Args:
        data: Resource creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        ResourceResponseDTO: Created resource information
    """
    print(f"INFO [ResourceRoutes]: Create resource request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        resource = resource_service.create_resource(db, user_id, data)
        print(f"INFO [ResourceRoutes]: Resource '{resource.name}' created successfully")
        return _to_response(resource)
    except PermissionError as e:
        print(f"ERROR [ResourceRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get("/low-stock", response_model=List[ResourceResponseDTO])
async def get_low_stock_resources(
    restaurant_id: UUID = Query(..., description="Restaurant UUID to check low stock"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[ResourceResponseDTO]:
    """
    Get resources where current stock is below minimum stock.

    Args:
        restaurant_id: Restaurant UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of low-stock ResourceResponseDTO objects
    """
    print(f"INFO [ResourceRoutes]: Low-stock resources request from user {current_user['email']} (restaurant={restaurant_id})")

    user_id = UUID(current_user["id"])
    try:
        resources = resource_service.get_low_stock_resources(db, user_id, restaurant_id)
        print(f"INFO [ResourceRoutes]: Returning {len(resources)} low-stock resources")
        return [_to_response(r) for r in resources]
    except PermissionError as e:
        print(f"ERROR [ResourceRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get("", response_model=List[ResourceResponseDTO])
async def list_resources(
    restaurant_id: UUID = Query(..., description="Restaurant UUID to list resources for"),
    type: Optional[ResourceType] = Query(None, description="Filter by resource type"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[ResourceResponseDTO]:
    """
    List all resources in a restaurant, with optional type filter.

    Args:
        restaurant_id: Restaurant UUID
        type: Optional resource type filter
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of ResourceResponseDTO objects
    """
    print(f"INFO [ResourceRoutes]: List resources request from user {current_user['email']} (restaurant={restaurant_id})")

    user_id = UUID(current_user["id"])
    type_filter = type.value if type else None
    try:
        resources = resource_service.get_resources(db, user_id, restaurant_id, type_filter)
        print(f"INFO [ResourceRoutes]: Returning {len(resources)} resources")
        return [_to_response(r) for r in resources]
    except PermissionError as e:
        print(f"ERROR [ResourceRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get("/{resource_id}", response_model=ResourceResponseDTO)
async def get_resource(
    resource_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> ResourceResponseDTO:
    """
    Get a specific resource by ID.

    Args:
        resource_id: Resource UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        ResourceResponseDTO: Resource information
    """
    print(f"INFO [ResourceRoutes]: Get resource {resource_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        resource = resource_service.get_resource(db, user_id, resource_id)
        print(f"INFO [ResourceRoutes]: Returning resource '{resource.name}'")
        return _to_response(resource)
    except PermissionError as e:
        print(f"ERROR [ResourceRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [ResourceRoutes]: Resource not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/{resource_id}", response_model=ResourceResponseDTO)
async def update_resource(
    resource_id: UUID,
    data: ResourceUpdateDTO,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> ResourceResponseDTO:
    """
    Update a resource.

    Args:
        resource_id: Resource UUID
        data: Resource update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        ResourceResponseDTO: Updated resource information
    """
    print(f"INFO [ResourceRoutes]: Update resource {resource_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        resource = resource_service.update_resource(db, user_id, resource_id, data)
        print(f"INFO [ResourceRoutes]: Resource '{resource.name}' updated successfully")
        return _to_response(resource)
    except PermissionError as e:
        print(f"ERROR [ResourceRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [ResourceRoutes]: Resource not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "manager"])),
) -> None:
    """
    Delete a resource.

    Only admin or manager roles can delete.

    Args:
        resource_id: Resource UUID
        db: Database session
        current_user: Current authenticated user (admin or manager)
    """
    print(f"INFO [ResourceRoutes]: Delete resource {resource_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        resource_service.delete_resource(db, user_id, resource_id)
        print(f"INFO [ResourceRoutes]: Resource {resource_id} deleted successfully")
    except PermissionError as e:
        print(f"ERROR [ResourceRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [ResourceRoutes]: Resource not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
