"""Budget repository for database operations."""

from calendar import monthrange
from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.budget import Budget
from src.models.transaction import Transaction


class BudgetRepository:
    """Repository for Budget database operations."""

    def create_budget(
        self,
        db: Session,
        entity_id: UUID,
        category_id: UUID,
        amount: Decimal,
        period_type: str,
        start_date: date,
        end_date: Optional[date] = None,
    ) -> Budget:
        """
        Create a new budget in the database.

        Args:
            db: Database session
            entity_id: Entity UUID the budget belongs to
            category_id: Category UUID for the budget
            amount: Budget amount
            period_type: Budget period type (monthly, quarterly, yearly)
            start_date: Budget start date
            end_date: Budget end date (optional, will be calculated if not provided)

        Returns:
            Created Budget object
        """
        print(f"INFO [BudgetRepository]: Creating budget for entity {entity_id}, category {category_id}")

        if end_date is None:
            end_date = self._calculate_end_date(start_date, period_type)

        budget = Budget(
            entity_id=entity_id,
            category_id=category_id,
            amount=amount,
            period_type=period_type,
            start_date=start_date,
            end_date=end_date,
            is_active=True,
        )
        db.add(budget)
        db.commit()
        db.refresh(budget)
        print(f"INFO [BudgetRepository]: Budget created with id {budget.id}")
        return budget

    def get_budget_by_id(self, db: Session, budget_id: UUID) -> Optional[Budget]:
        """
        Find a budget by ID.

        Args:
            db: Database session
            budget_id: Budget UUID

        Returns:
            Budget object if found, None otherwise
        """
        print(f"INFO [BudgetRepository]: Looking up budget by id {budget_id}")
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if budget:
            print(f"INFO [BudgetRepository]: Found budget {budget.id}")
        else:
            print(f"INFO [BudgetRepository]: No budget found with id {budget_id}")
        return budget

    def get_budgets_by_entity(
        self,
        db: Session,
        entity_id: UUID,
        category_id: Optional[UUID] = None,
        is_active: Optional[bool] = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Budget]:
        """
        Get budgets for an entity with optional filtering.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            category_id: Optional category filter
            is_active: Optional active status filter (default True)
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return

        Returns:
            List of Budget objects
        """
        print(f"INFO [BudgetRepository]: Fetching budgets for entity {entity_id}")
        query = db.query(Budget).filter(Budget.entity_id == entity_id)

        if category_id is not None:
            print(f"INFO [BudgetRepository]: Filtering by category_id = {category_id}")
            query = query.filter(Budget.category_id == category_id)

        if is_active is not None:
            print(f"INFO [BudgetRepository]: Filtering by is_active = {is_active}")
            query = query.filter(Budget.is_active == is_active)

        query = query.order_by(Budget.created_at.desc())
        budgets = query.offset(skip).limit(limit).all()
        print(f"INFO [BudgetRepository]: Found {len(budgets)} budgets")
        return budgets

    def count_budgets_by_entity(
        self,
        db: Session,
        entity_id: UUID,
        category_id: Optional[UUID] = None,
        is_active: Optional[bool] = True,
    ) -> int:
        """
        Count budgets for an entity with optional filtering.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            category_id: Optional category filter
            is_active: Optional active status filter

        Returns:
            Count of budgets matching criteria
        """
        print(f"INFO [BudgetRepository]: Counting budgets for entity {entity_id}")
        query = db.query(Budget).filter(Budget.entity_id == entity_id)

        if category_id is not None:
            query = query.filter(Budget.category_id == category_id)

        if is_active is not None:
            query = query.filter(Budget.is_active == is_active)

        count = query.count()
        print(f"INFO [BudgetRepository]: Count result: {count}")
        return count

    def update_budget(self, db: Session, budget: Budget) -> Budget:
        """
        Update an existing budget.

        Args:
            db: Database session
            budget: Budget object with updated values

        Returns:
            Updated Budget object
        """
        print(f"INFO [BudgetRepository]: Updating budget {budget.id}")
        db.add(budget)
        db.commit()
        db.refresh(budget)
        print(f"INFO [BudgetRepository]: Budget {budget.id} updated successfully")
        return budget

    def delete_budget(self, db: Session, budget: Budget) -> None:
        """
        Delete a budget.

        Args:
            db: Database session
            budget: Budget object to delete
        """
        print(f"INFO [BudgetRepository]: Deleting budget {budget.id}")
        db.delete(budget)
        db.commit()
        print(f"INFO [BudgetRepository]: Budget {budget.id} deleted successfully")

    def calculate_spending(
        self,
        db: Session,
        entity_id: UUID,
        category_id: UUID,
        start_date: date,
        end_date: date,
    ) -> Decimal:
        """
        Calculate total spending for a category within a date range.

        Args:
            db: Database session
            entity_id: Entity UUID
            category_id: Category UUID
            start_date: Start of period
            end_date: End of period

        Returns:
            Total spending amount
        """
        print(f"INFO [BudgetRepository]: Calculating spending for category {category_id} from {start_date} to {end_date}")

        result = (
            db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                Transaction.entity_id == entity_id,
                Transaction.category_id == category_id,
                Transaction.type == "expense",
                Transaction.date >= start_date,
                Transaction.date <= end_date,
            )
            .scalar()
        )

        spending = Decimal(str(result)) if result else Decimal("0.00")
        print(f"INFO [BudgetRepository]: Spending calculated: {spending}")
        return spending

    def check_duplicate_budget(
        self,
        db: Session,
        entity_id: UUID,
        category_id: UUID,
        period_type: str,
        start_date: date,
        exclude_budget_id: Optional[UUID] = None,
    ) -> bool:
        """
        Check if a duplicate budget already exists.

        Args:
            db: Database session
            entity_id: Entity UUID
            category_id: Category UUID
            period_type: Budget period type
            start_date: Budget start date
            exclude_budget_id: Budget ID to exclude from check (for updates)

        Returns:
            True if duplicate exists, False otherwise
        """
        print(f"INFO [BudgetRepository]: Checking for duplicate budget")
        query = db.query(Budget).filter(
            Budget.entity_id == entity_id,
            Budget.category_id == category_id,
            Budget.period_type == period_type,
            Budget.start_date == start_date,
            Budget.is_active == True,
        )

        if exclude_budget_id:
            query = query.filter(Budget.id != exclude_budget_id)

        exists = query.first() is not None
        print(f"INFO [BudgetRepository]: Duplicate exists: {exists}")
        return exists

    def _calculate_end_date(self, start_date: date, period_type: str) -> date:
        """
        Calculate end date based on period type.

        Args:
            start_date: Budget start date
            period_type: Budget period type

        Returns:
            Calculated end date
        """
        if period_type == "monthly":
            # End of the month
            _, last_day = monthrange(start_date.year, start_date.month)
            return date(start_date.year, start_date.month, last_day)
        elif period_type == "quarterly":
            # End of 3-month period
            month = start_date.month + 2
            year = start_date.year
            if month > 12:
                month -= 12
                year += 1
            _, last_day = monthrange(year, month)
            return date(year, month, last_day)
        elif period_type == "yearly":
            # End of 12-month period
            year = start_date.year
            if start_date.month == 1 and start_date.day == 1:
                # Full calendar year
                return date(year, 12, 31)
            else:
                # Rolling 12 months
                month = start_date.month - 1
                if month == 0:
                    month = 12
                    year += 1
                else:
                    year += 1
                _, last_day = monthrange(year, month)
                return date(year, month, last_day)
        else:
            # Default to monthly
            _, last_day = monthrange(start_date.year, start_date.month)
            return date(start_date.year, start_date.month, last_day)


# Singleton instance
budget_repository = BudgetRepository()
