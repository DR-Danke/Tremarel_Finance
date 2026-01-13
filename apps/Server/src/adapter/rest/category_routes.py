"""Category endpoint routes."""

from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.core.services.category_service import category_service
from src.interface.category_dto import (
    CategoryCreateDTO,
    CategoryResponseDTO,
    CategoryTreeDTO,
    CategoryUpdateDTO,
)

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreateDTO,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> CategoryResponseDTO:
    """
    Create a new category.

    Creates a category for the specified entity. Categories can have optional
    parent categories for hierarchical organization.

    Args:
        data: Category creation data
        db: Database session
        current_user: Authenticated user

    Returns:
        CategoryResponseDTO: Created category

    Raises:
        HTTPException: 400 if validation fails, 403 if user lacks access
    """
    print(f"INFO [CategoryRoutes]: Create category request from user {current_user['email']}")

    try:
        category = category_service.create_category(db, data)
    except ValueError as e:
        print(f"ERROR [CategoryRoutes]: Category creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    print(f"INFO [CategoryRoutes]: Category {category.id} created successfully")
    return CategoryResponseDTO.model_validate(category)


@router.get("/entity/{entity_id}", response_model=List[CategoryResponseDTO])
async def get_categories_by_entity(
    entity_id: UUID,
    include_inactive: bool = Query(False, description="Include inactive categories"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[CategoryResponseDTO]:
    """
    Get all categories for an entity.

    Returns a flat list of all categories belonging to the specified entity.

    Args:
        entity_id: Entity UUID
        include_inactive: Whether to include inactive categories
        db: Database session
        current_user: Authenticated user

    Returns:
        List[CategoryResponseDTO]: List of categories
    """
    print(f"INFO [CategoryRoutes]: Get categories for entity {entity_id}")

    categories = category_service.get_categories_for_entity(db, entity_id, include_inactive)

    print(f"INFO [CategoryRoutes]: Returning {len(categories)} categories")
    return [CategoryResponseDTO.model_validate(c) for c in categories]


@router.get("/entity/{entity_id}/tree", response_model=List[CategoryTreeDTO])
async def get_category_tree(
    entity_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[CategoryTreeDTO]:
    """
    Get hierarchical category tree for an entity.

    Returns categories organized in a tree structure with root categories
    containing their children recursively.

    Args:
        entity_id: Entity UUID
        db: Database session
        current_user: Authenticated user

    Returns:
        List[CategoryTreeDTO]: Root categories with nested children
    """
    print(f"INFO [CategoryRoutes]: Get category tree for entity {entity_id}")

    tree = category_service.get_category_tree(db, entity_id)

    print(f"INFO [CategoryRoutes]: Returning tree with {len(tree)} root categories")
    return tree


@router.get("/{category_id}", response_model=CategoryResponseDTO)
async def get_category(
    category_id: UUID,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> CategoryResponseDTO:
    """
    Get a single category by ID.

    Args:
        category_id: Category UUID
        entity_id: Entity UUID for access validation
        db: Database session
        current_user: Authenticated user

    Returns:
        CategoryResponseDTO: Category data

    Raises:
        HTTPException: 404 if category not found or doesn't belong to entity
    """
    print(f"INFO [CategoryRoutes]: Get category {category_id}")

    category = category_service.get_category(db, category_id, entity_id)
    if category is None:
        print(f"ERROR [CategoryRoutes]: Category {category_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return CategoryResponseDTO.model_validate(category)


@router.put("/{category_id}", response_model=CategoryResponseDTO)
async def update_category(
    category_id: UUID,
    data: CategoryUpdateDTO,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> CategoryResponseDTO:
    """
    Update an existing category.

    Args:
        category_id: Category UUID to update
        data: Category update data
        entity_id: Entity UUID for access validation
        db: Database session
        current_user: Authenticated user

    Returns:
        CategoryResponseDTO: Updated category

    Raises:
        HTTPException: 404 if not found, 400 if validation fails
    """
    print(f"INFO [CategoryRoutes]: Update category {category_id}")

    try:
        category = category_service.update_category(db, category_id, entity_id, data)
    except ValueError as e:
        print(f"ERROR [CategoryRoutes]: Category update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    if category is None:
        print(f"ERROR [CategoryRoutes]: Category {category_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    print(f"INFO [CategoryRoutes]: Category {category_id} updated successfully")
    return CategoryResponseDTO.model_validate(category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> None:
    """
    Delete a category.

    Categories with children or transactions cannot be deleted.

    Args:
        category_id: Category UUID to delete
        entity_id: Entity UUID for access validation
        db: Database session
        current_user: Authenticated user

    Raises:
        HTTPException: 404 if not found, 400 if has children/transactions
    """
    print(f"INFO [CategoryRoutes]: Delete category {category_id}")

    try:
        category_service.delete_category(db, category_id, entity_id)
    except ValueError as e:
        error_msg = str(e)
        print(f"ERROR [CategoryRoutes]: Category deletion failed: {error_msg}")

        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )

    print(f"INFO [CategoryRoutes]: Category {category_id} deleted successfully")
