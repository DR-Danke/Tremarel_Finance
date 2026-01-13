"""Budget API endpoint routes."""

from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.adapter.rest.rbac_dependencies import require_roles
from src.core.services.budget_service import budget_service
from src.interface.budget_dto import (
    BudgetCreateDTO,
    BudgetListResponseDTO,
    BudgetResponseDTO,
    BudgetUpdateDTO,
    BudgetWithSpendingDTO,
)

router = APIRouter(prefix="/api/budgets", tags=["Budgets"])


@router.post("/", response_model=BudgetResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_budget(
    data: BudgetCreateDTO,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BudgetResponseDTO:
    """
    Create a new budget.

    Creates a budget for the specified entity and category. Requires authentication.
    Category must be an expense type.

    Args:
        data: Budget creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        BudgetResponseDTO: Created budget data

    Raises:
        HTTPException: 400 if validation fails
    """
    print(f"INFO [BudgetRoutes]: Create budget request from user {current_user['id']}")

    try:
        budget = budget_service.create_budget(db, data)
        print(f"INFO [BudgetRoutes]: Budget {budget.id} created successfully")
        return BudgetResponseDTO.model_validate(budget)
    except ValueError as e:
        print(f"ERROR [BudgetRoutes]: Budget creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/", response_model=BudgetListResponseDTO)
async def list_budgets(
    entity_id: UUID = Query(..., description="Entity ID to filter budgets"),
    category_id: Optional[UUID] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BudgetListResponseDTO:
    """
    List budgets for an entity with spending information.

    Returns budgets with calculated actual spending and percentage.

    Args:
        entity_id: Entity UUID to filter by
        category_id: Optional category filter
        skip: Pagination offset
        limit: Maximum results to return
        current_user: Current authenticated user
        db: Database session

    Returns:
        BudgetListResponseDTO: List of budgets with spending
    """
    print(f"INFO [BudgetRoutes]: List budgets request for entity {entity_id}")

    budgets, total = budget_service.list_budgets_with_spending(
        db=db,
        entity_id=entity_id,
        category_id=category_id,
        skip=skip,
        limit=limit,
    )

    print(f"INFO [BudgetRoutes]: Returning {len(budgets)} budgets (total: {total})")
    return BudgetListResponseDTO(budgets=budgets, total=total)


@router.get("/{budget_id}", response_model=BudgetWithSpendingDTO)
async def get_budget(
    budget_id: UUID,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BudgetWithSpendingDTO:
    """
    Get a single budget by ID with spending information.

    Args:
        budget_id: Budget UUID
        entity_id: Entity UUID for validation
        current_user: Current authenticated user
        db: Database session

    Returns:
        BudgetWithSpendingDTO: Budget data with spending

    Raises:
        HTTPException: 404 if budget not found or doesn't belong to entity
    """
    print(f"INFO [BudgetRoutes]: Get budget {budget_id}")

    budget = budget_service.get_budget_with_spending(db, budget_id, entity_id)
    if not budget:
        print(f"ERROR [BudgetRoutes]: Budget {budget_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found",
        )

    print(f"INFO [BudgetRoutes]: Returning budget {budget_id}")
    return budget


@router.put("/{budget_id}", response_model=BudgetResponseDTO)
async def update_budget(
    budget_id: UUID,
    data: BudgetUpdateDTO,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BudgetResponseDTO:
    """
    Update an existing budget.

    Args:
        budget_id: Budget UUID
        data: Update data
        entity_id: Entity UUID for validation
        current_user: Current authenticated user
        db: Database session

    Returns:
        BudgetResponseDTO: Updated budget data

    Raises:
        HTTPException: 404 if budget not found or doesn't belong to entity
    """
    print(f"INFO [BudgetRoutes]: Update budget {budget_id}")

    budget = budget_service.update_budget(db, budget_id, entity_id, data)
    if not budget:
        print(f"ERROR [BudgetRoutes]: Budget {budget_id} not found or update failed")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found",
        )

    print(f"INFO [BudgetRoutes]: Budget {budget_id} updated successfully")
    return BudgetResponseDTO.model_validate(budget)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: UUID,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "manager"])),
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a budget.

    Only admin or manager roles can delete budgets.

    Args:
        budget_id: Budget UUID
        entity_id: Entity UUID for validation
        current_user: Current authenticated user (must be admin or manager)
        db: Database session

    Raises:
        HTTPException: 404 if budget not found or doesn't belong to entity
        HTTPException: 403 if user doesn't have required role
    """
    print(f"INFO [BudgetRoutes]: Delete budget {budget_id} by user {current_user['id']}")

    success = budget_service.delete_budget(db, budget_id, entity_id)
    if not success:
        print(f"ERROR [BudgetRoutes]: Budget {budget_id} not found or delete failed")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found",
        )

    print(f"INFO [BudgetRoutes]: Budget {budget_id} deleted successfully")
