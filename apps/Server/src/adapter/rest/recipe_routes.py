"""Recipe endpoint routes."""

from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.core.services.recipe_service import recipe_service
from src.interface.recipe_dto import (
    RecipeCreateDTO,
    RecipeItemResponseDTO,
    RecipeResponseDTO,
    RecipeUpdateDTO,
)
from src.models.recipe import Recipe, RecipeItem

router = APIRouter(prefix="/api/recipes", tags=["Recipes"])


def _to_response(recipe: Recipe, items: list[RecipeItem]) -> RecipeResponseDTO:
    """Convert a Recipe model and its items to RecipeResponseDTO."""
    item_dtos = [
        RecipeItemResponseDTO.model_validate(item, from_attributes=True)
        for item in items
    ]
    return RecipeResponseDTO(
        id=recipe.id,
        restaurant_id=recipe.restaurant_id,
        name=recipe.name,
        sale_price=recipe.sale_price,
        current_cost=recipe.current_cost,
        margin_percent=recipe.margin_percent,
        is_profitable=recipe.is_profitable,
        is_active=recipe.is_active,
        items=item_dtos,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
    )


@router.post("", response_model=RecipeResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    data: RecipeCreateDTO,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> RecipeResponseDTO:
    """
    Create a new recipe with ingredients in a restaurant.

    Args:
        data: Recipe creation data with items
        db: Database session
        current_user: Current authenticated user

    Returns:
        RecipeResponseDTO: Created recipe information
    """
    print(f"INFO [RecipeRoutes]: Create recipe request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        recipe, items = recipe_service.create_recipe(db, user_id, data)
        print(f"INFO [RecipeRoutes]: Recipe '{recipe.name}' created successfully")
        return _to_response(recipe, items)
    except PermissionError as e:
        print(f"ERROR [RecipeRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get("", response_model=List[RecipeResponseDTO])
async def list_recipes(
    restaurant_id: UUID = Query(..., description="Restaurant UUID to list recipes for"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[RecipeResponseDTO]:
    """
    List all recipes in a restaurant.

    Args:
        restaurant_id: Restaurant UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of RecipeResponseDTO objects
    """
    print(f"INFO [RecipeRoutes]: List recipes request from user {current_user['email']} (restaurant={restaurant_id})")

    user_id = UUID(current_user["id"])
    try:
        recipe_tuples = recipe_service.get_recipes(db, user_id, restaurant_id)
        print(f"INFO [RecipeRoutes]: Returning {len(recipe_tuples)} recipes")
        return [_to_response(recipe, items) for recipe, items in recipe_tuples]
    except PermissionError as e:
        print(f"ERROR [RecipeRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get("/{recipe_id}", response_model=RecipeResponseDTO)
async def get_recipe(
    recipe_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> RecipeResponseDTO:
    """
    Get a specific recipe by ID with its items.

    Args:
        recipe_id: Recipe UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        RecipeResponseDTO: Recipe information with items
    """
    print(f"INFO [RecipeRoutes]: Get recipe {recipe_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        recipe, items = recipe_service.get_recipe(db, user_id, recipe_id)
        print(f"INFO [RecipeRoutes]: Returning recipe '{recipe.name}'")
        return _to_response(recipe, items)
    except PermissionError as e:
        print(f"ERROR [RecipeRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [RecipeRoutes]: Recipe not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/{recipe_id}", response_model=RecipeResponseDTO)
async def update_recipe(
    recipe_id: UUID,
    data: RecipeUpdateDTO,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> RecipeResponseDTO:
    """
    Update a recipe.

    Args:
        recipe_id: Recipe UUID
        data: Recipe update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        RecipeResponseDTO: Updated recipe information
    """
    print(f"INFO [RecipeRoutes]: Update recipe {recipe_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        recipe, items = recipe_service.update_recipe(db, user_id, recipe_id, data)
        print(f"INFO [RecipeRoutes]: Recipe '{recipe.name}' updated successfully")
        return _to_response(recipe, items)
    except PermissionError as e:
        print(f"ERROR [RecipeRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [RecipeRoutes]: Recipe not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> None:
    """
    Delete a recipe.

    Args:
        recipe_id: Recipe UUID
        db: Database session
        current_user: Current authenticated user
    """
    print(f"INFO [RecipeRoutes]: Delete recipe {recipe_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        recipe_service.delete_recipe(db, user_id, recipe_id)
        print(f"INFO [RecipeRoutes]: Recipe {recipe_id} deleted successfully")
    except PermissionError as e:
        print(f"ERROR [RecipeRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [RecipeRoutes]: Recipe not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/{recipe_id}/recalculate", response_model=dict)
async def recalculate_recipe_cost(
    recipe_id: UUID,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> dict:
    """
    Force cost recalculation for a recipe.

    Args:
        recipe_id: Recipe UUID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Dict with current_cost, margin_percent, is_profitable
    """
    print(f"INFO [RecipeRoutes]: Recalculate cost for recipe {recipe_id} request from user {current_user['email']}")

    user_id = UUID(current_user["id"])
    try:
        result = recipe_service.recalculate_cost(db, user_id, recipe_id)
        print(f"INFO [RecipeRoutes]: Recipe {recipe_id} cost recalculated")
        return {
            "current_cost": str(result["current_cost"]),
            "margin_percent": str(result["margin_percent"]),
            "is_profitable": result["is_profitable"],
        }
    except PermissionError as e:
        print(f"ERROR [RecipeRoutes]: Access denied: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ValueError as e:
        print(f"ERROR [RecipeRoutes]: Recipe not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
