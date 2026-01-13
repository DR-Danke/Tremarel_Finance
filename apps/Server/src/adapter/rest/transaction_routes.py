"""Transaction API endpoint routes."""

from datetime import date
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.adapter.rest.dependencies import get_current_user, get_db
from src.adapter.rest.rbac_dependencies import require_roles
from src.core.services.transaction_service import transaction_service
from src.interface.transaction_dto import (
    TransactionCreateDTO,
    TransactionFilterDTO,
    TransactionListResponseDTO,
    TransactionResponseDTO,
    TransactionUpdateDTO,
)

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.post("/", response_model=TransactionResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    data: TransactionCreateDTO,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionResponseDTO:
    """
    Create a new transaction.

    Creates a transaction for the specified entity. Requires authentication.

    Args:
        data: Transaction creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        TransactionResponseDTO: Created transaction data
    """
    print(f"INFO [TransactionRoutes]: Create transaction request from user {current_user['id']}")

    user_id = UUID(current_user["id"])
    transaction = transaction_service.create_transaction(db, user_id, data)

    print(f"INFO [TransactionRoutes]: Transaction {transaction.id} created successfully")
    return TransactionResponseDTO.model_validate(transaction)


@router.get("/", response_model=TransactionListResponseDTO)
async def list_transactions(
    entity_id: UUID = Query(..., description="Entity ID to filter transactions"),
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter until date"),
    category_id: Optional[UUID] = Query(None, description="Filter by category"),
    type: Optional[str] = Query(None, description="Filter by type (income/expense)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionListResponseDTO:
    """
    List transactions for an entity with optional filtering.

    Supports pagination and filtering by date range, category, and type.

    Args:
        entity_id: Entity UUID to filter by
        start_date: Optional start date filter
        end_date: Optional end date filter
        category_id: Optional category filter
        type: Optional type filter (income/expense)
        skip: Pagination offset
        limit: Maximum results to return
        current_user: Current authenticated user
        db: Database session

    Returns:
        TransactionListResponseDTO: Paginated list of transactions
    """
    print(f"INFO [TransactionRoutes]: List transactions request for entity {entity_id}")

    filters = TransactionFilterDTO(
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        type=type,
    )

    transactions, total = transaction_service.list_transactions(
        db=db,
        entity_id=entity_id,
        filters=filters,
        skip=skip,
        limit=limit,
    )

    print(f"INFO [TransactionRoutes]: Returning {len(transactions)} transactions (total: {total})")
    return TransactionListResponseDTO(
        transactions=[TransactionResponseDTO.model_validate(t) for t in transactions],
        total=total,
    )


@router.get("/{transaction_id}", response_model=TransactionResponseDTO)
async def get_transaction(
    transaction_id: UUID,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionResponseDTO:
    """
    Get a single transaction by ID.

    Args:
        transaction_id: Transaction UUID
        entity_id: Entity UUID for validation
        current_user: Current authenticated user
        db: Database session

    Returns:
        TransactionResponseDTO: Transaction data

    Raises:
        HTTPException: 404 if transaction not found or doesn't belong to entity
    """
    print(f"INFO [TransactionRoutes]: Get transaction {transaction_id}")

    transaction = transaction_service.get_transaction(db, transaction_id, entity_id)
    if not transaction:
        print(f"ERROR [TransactionRoutes]: Transaction {transaction_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    print(f"INFO [TransactionRoutes]: Returning transaction {transaction_id}")
    return TransactionResponseDTO.model_validate(transaction)


@router.put("/{transaction_id}", response_model=TransactionResponseDTO)
async def update_transaction(
    transaction_id: UUID,
    data: TransactionUpdateDTO,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TransactionResponseDTO:
    """
    Update an existing transaction.

    Args:
        transaction_id: Transaction UUID
        data: Update data
        entity_id: Entity UUID for validation
        current_user: Current authenticated user
        db: Database session

    Returns:
        TransactionResponseDTO: Updated transaction data

    Raises:
        HTTPException: 404 if transaction not found or doesn't belong to entity
    """
    print(f"INFO [TransactionRoutes]: Update transaction {transaction_id}")

    transaction = transaction_service.update_transaction(db, transaction_id, entity_id, data)
    if not transaction:
        print(f"ERROR [TransactionRoutes]: Transaction {transaction_id} not found or update failed")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    print(f"INFO [TransactionRoutes]: Transaction {transaction_id} updated successfully")
    return TransactionResponseDTO.model_validate(transaction)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: UUID,
    entity_id: UUID = Query(..., description="Entity ID for validation"),
    current_user: Dict[str, Any] = Depends(require_roles(["admin", "manager"])),
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a transaction.

    Only admin or manager roles can delete transactions.

    Args:
        transaction_id: Transaction UUID
        entity_id: Entity UUID for validation
        current_user: Current authenticated user (must be admin or manager)
        db: Database session

    Raises:
        HTTPException: 404 if transaction not found or doesn't belong to entity
        HTTPException: 403 if user doesn't have required role
    """
    print(f"INFO [TransactionRoutes]: Delete transaction {transaction_id} by user {current_user['id']}")

    success = transaction_service.delete_transaction(db, transaction_id, entity_id)
    if not success:
        print(f"ERROR [TransactionRoutes]: Transaction {transaction_id} not found or delete failed")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    print(f"INFO [TransactionRoutes]: Transaction {transaction_id} deleted successfully")
