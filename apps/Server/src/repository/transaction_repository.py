"""Transaction repository for database operations."""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.interface.transaction_dto import TransactionFilterDTO
from src.models.transaction import Transaction


class TransactionRepository:
    """Repository for Transaction database operations."""

    def create_transaction(
        self,
        db: Session,
        entity_id: UUID,
        category_id: UUID,
        user_id: Optional[UUID],
        amount: Decimal,
        type: str,
        description: Optional[str],
        transaction_date: date,
        notes: Optional[str],
    ) -> Transaction:
        """
        Create a new transaction in the database.

        Args:
            db: Database session
            entity_id: Entity UUID the transaction belongs to
            category_id: Category UUID for the transaction
            user_id: User UUID who created the transaction (optional)
            amount: Transaction amount
            type: Transaction type (income or expense)
            description: Transaction description (optional)
            transaction_date: Date of the transaction
            notes: Additional notes (optional)

        Returns:
            Created Transaction object
        """
        print(f"INFO [TransactionRepository]: Creating transaction for entity {entity_id}")
        transaction = Transaction(
            entity_id=entity_id,
            category_id=category_id,
            user_id=user_id,
            amount=amount,
            type=type,
            description=description,
            date=transaction_date,
            notes=notes,
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        print(f"INFO [TransactionRepository]: Transaction created with id {transaction.id}")
        return transaction

    def get_transaction_by_id(
        self, db: Session, transaction_id: UUID
    ) -> Optional[Transaction]:
        """
        Find a transaction by ID.

        Args:
            db: Database session
            transaction_id: Transaction UUID

        Returns:
            Transaction object if found, None otherwise
        """
        print(f"INFO [TransactionRepository]: Looking up transaction by id {transaction_id}")
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if transaction:
            print(f"INFO [TransactionRepository]: Found transaction {transaction.id}")
        else:
            print(f"INFO [TransactionRepository]: No transaction found with id {transaction_id}")
        return transaction

    def get_transactions_by_entity(
        self,
        db: Session,
        entity_id: UUID,
        filters: Optional[TransactionFilterDTO] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Transaction]:
        """
        Get transactions for an entity with optional filtering.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            filters: Optional filter criteria
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return

        Returns:
            List of Transaction objects
        """
        print(f"INFO [TransactionRepository]: Fetching transactions for entity {entity_id}")
        query = db.query(Transaction).filter(Transaction.entity_id == entity_id)

        if filters:
            if filters.start_date:
                print(f"INFO [TransactionRepository]: Filtering by start_date >= {filters.start_date}")
                query = query.filter(Transaction.date >= filters.start_date)
            if filters.end_date:
                print(f"INFO [TransactionRepository]: Filtering by end_date <= {filters.end_date}")
                query = query.filter(Transaction.date <= filters.end_date)
            if filters.category_id:
                print(f"INFO [TransactionRepository]: Filtering by category_id = {filters.category_id}")
                query = query.filter(Transaction.category_id == filters.category_id)
            if filters.type:
                print(f"INFO [TransactionRepository]: Filtering by type = {filters.type}")
                query = query.filter(Transaction.type == filters.type)

        query = query.order_by(Transaction.date.desc())
        transactions = query.offset(skip).limit(limit).all()
        print(f"INFO [TransactionRepository]: Found {len(transactions)} transactions")
        return transactions

    def count_transactions_by_entity(
        self,
        db: Session,
        entity_id: UUID,
        filters: Optional[TransactionFilterDTO] = None,
    ) -> int:
        """
        Count transactions for an entity with optional filtering.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            filters: Optional filter criteria

        Returns:
            Count of transactions matching criteria
        """
        print(f"INFO [TransactionRepository]: Counting transactions for entity {entity_id}")
        query = db.query(Transaction).filter(Transaction.entity_id == entity_id)

        if filters:
            if filters.start_date:
                query = query.filter(Transaction.date >= filters.start_date)
            if filters.end_date:
                query = query.filter(Transaction.date <= filters.end_date)
            if filters.category_id:
                query = query.filter(Transaction.category_id == filters.category_id)
            if filters.type:
                query = query.filter(Transaction.type == filters.type)

        count = query.count()
        print(f"INFO [TransactionRepository]: Count result: {count}")
        return count

    def update_transaction(self, db: Session, transaction: Transaction) -> Transaction:
        """
        Update an existing transaction.

        Args:
            db: Database session
            transaction: Transaction object with updated values

        Returns:
            Updated Transaction object
        """
        print(f"INFO [TransactionRepository]: Updating transaction {transaction.id}")
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        print(f"INFO [TransactionRepository]: Transaction {transaction.id} updated successfully")
        return transaction

    def delete_transaction(self, db: Session, transaction: Transaction) -> None:
        """
        Delete a transaction.

        Args:
            db: Database session
            transaction: Transaction object to delete
        """
        print(f"INFO [TransactionRepository]: Deleting transaction {transaction.id}")
        db.delete(transaction)
        db.commit()
        print(f"INFO [TransactionRepository]: Transaction {transaction.id} deleted successfully")


# Singleton instance
transaction_repository = TransactionRepository()
