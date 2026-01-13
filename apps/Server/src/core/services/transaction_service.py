"""Transaction service for business logic."""

from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from src.interface.transaction_dto import (
    TransactionCreateDTO,
    TransactionFilterDTO,
    TransactionUpdateDTO,
)
from src.models.transaction import Transaction
from src.repository.transaction_repository import transaction_repository


class TransactionService:
    """Service for transaction business logic."""

    def create_transaction(
        self,
        db: Session,
        user_id: UUID,
        data: TransactionCreateDTO,
    ) -> Transaction:
        """
        Create a new transaction.

        Args:
            db: Database session
            user_id: ID of the user creating the transaction
            data: Transaction creation data

        Returns:
            Created Transaction object
        """
        print(f"INFO [TransactionService]: Creating transaction for entity {data.entity_id}")
        transaction = transaction_repository.create_transaction(
            db=db,
            entity_id=data.entity_id,
            category_id=data.category_id,
            user_id=user_id,
            amount=data.amount,
            type=data.type,
            description=data.description,
            transaction_date=data.date,
            notes=data.notes,
        )
        print(f"INFO [TransactionService]: Transaction {transaction.id} created successfully")
        return transaction

    def get_transaction(
        self,
        db: Session,
        transaction_id: UUID,
        entity_id: UUID,
    ) -> Optional[Transaction]:
        """
        Get a transaction by ID, validating entity ownership.

        Args:
            db: Database session
            transaction_id: Transaction UUID
            entity_id: Entity UUID for validation

        Returns:
            Transaction object if found and belongs to entity, None otherwise
        """
        print(f"INFO [TransactionService]: Getting transaction {transaction_id}")
        transaction = transaction_repository.get_transaction_by_id(db, transaction_id)
        if transaction and transaction.entity_id != entity_id:
            print(f"ERROR [TransactionService]: Transaction {transaction_id} does not belong to entity {entity_id}")
            return None
        return transaction

    def list_transactions(
        self,
        db: Session,
        entity_id: UUID,
        filters: Optional[TransactionFilterDTO] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Transaction], int]:
        """
        List transactions for an entity with pagination.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            filters: Optional filter criteria
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of transactions, total count)
        """
        print(f"INFO [TransactionService]: Listing transactions for entity {entity_id}")
        transactions = transaction_repository.get_transactions_by_entity(
            db=db,
            entity_id=entity_id,
            filters=filters,
            skip=skip,
            limit=limit,
        )
        total = transaction_repository.count_transactions_by_entity(
            db=db,
            entity_id=entity_id,
            filters=filters,
        )
        print(f"INFO [TransactionService]: Found {len(transactions)} transactions (total: {total})")
        return transactions, total

    def update_transaction(
        self,
        db: Session,
        transaction_id: UUID,
        entity_id: UUID,
        data: TransactionUpdateDTO,
    ) -> Optional[Transaction]:
        """
        Update an existing transaction.

        Args:
            db: Database session
            transaction_id: Transaction UUID
            entity_id: Entity UUID for validation
            data: Update data

        Returns:
            Updated Transaction object if found and updated, None otherwise
        """
        print(f"INFO [TransactionService]: Updating transaction {transaction_id}")
        transaction = transaction_repository.get_transaction_by_id(db, transaction_id)
        if not transaction:
            print(f"ERROR [TransactionService]: Transaction {transaction_id} not found")
            return None
        if transaction.entity_id != entity_id:
            print(f"ERROR [TransactionService]: Transaction {transaction_id} does not belong to entity {entity_id}")
            return None

        # Update fields if provided
        if data.category_id is not None:
            transaction.category_id = data.category_id
        if data.amount is not None:
            transaction.amount = data.amount
        if data.type is not None:
            transaction.type = data.type
        if data.description is not None:
            transaction.description = data.description
        if data.date is not None:
            transaction.date = data.date
        if data.notes is not None:
            transaction.notes = data.notes

        updated = transaction_repository.update_transaction(db, transaction)
        print(f"INFO [TransactionService]: Transaction {transaction_id} updated successfully")
        return updated

    def delete_transaction(
        self,
        db: Session,
        transaction_id: UUID,
        entity_id: UUID,
    ) -> bool:
        """
        Delete a transaction.

        Args:
            db: Database session
            transaction_id: Transaction UUID
            entity_id: Entity UUID for validation

        Returns:
            True if deleted, False if not found or not owned
        """
        print(f"INFO [TransactionService]: Deleting transaction {transaction_id}")
        transaction = transaction_repository.get_transaction_by_id(db, transaction_id)
        if not transaction:
            print(f"ERROR [TransactionService]: Transaction {transaction_id} not found")
            return False
        if transaction.entity_id != entity_id:
            print(f"ERROR [TransactionService]: Transaction {transaction_id} does not belong to entity {entity_id}")
            return False

        transaction_repository.delete_transaction(db, transaction)
        print(f"INFO [TransactionService]: Transaction {transaction_id} deleted successfully")
        return True


# Singleton instance
transaction_service = TransactionService()
