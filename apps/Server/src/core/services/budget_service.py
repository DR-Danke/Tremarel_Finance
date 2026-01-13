"""Budget service for business logic."""

from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from src.interface.budget_dto import (
    BudgetCreateDTO,
    BudgetUpdateDTO,
    BudgetWithSpendingDTO,
)
from src.models.budget import Budget
from src.repository.budget_repository import budget_repository
from src.repository.category_repository import category_repository


class BudgetService:
    """Service for budget business logic."""

    def create_budget(
        self,
        db: Session,
        data: BudgetCreateDTO,
    ) -> Budget:
        """
        Create a new budget.

        Args:
            db: Database session
            data: Budget creation data

        Returns:
            Created Budget object

        Raises:
            ValueError: If category is not expense type or duplicate budget exists
        """
        print(f"INFO [BudgetService]: Creating budget for entity {data.entity_id}")

        # Validate category exists and is expense type
        category = category_repository.get_category_by_id(db, data.category_id)
        if not category:
            print(f"ERROR [BudgetService]: Category {data.category_id} not found")
            raise ValueError(f"Category {data.category_id} not found")

        if category.type != "expense":
            print(f"ERROR [BudgetService]: Category {data.category_id} is not expense type")
            raise ValueError("Budgets can only be created for expense categories")

        if category.entity_id != data.entity_id:
            print(f"ERROR [BudgetService]: Category {data.category_id} does not belong to entity {data.entity_id}")
            raise ValueError("Category does not belong to the specified entity")

        # Check for duplicate budget
        if budget_repository.check_duplicate_budget(
            db=db,
            entity_id=data.entity_id,
            category_id=data.category_id,
            period_type=data.period_type,
            start_date=data.start_date,
        ):
            print(f"ERROR [BudgetService]: Duplicate budget exists for category {data.category_id}")
            raise ValueError("A budget with the same category, period type, and start date already exists")

        budget = budget_repository.create_budget(
            db=db,
            entity_id=data.entity_id,
            category_id=data.category_id,
            amount=data.amount,
            period_type=data.period_type,
            start_date=data.start_date,
        )
        print(f"INFO [BudgetService]: Budget {budget.id} created successfully")
        return budget

    def get_budget(
        self,
        db: Session,
        budget_id: UUID,
        entity_id: UUID,
    ) -> Optional[Budget]:
        """
        Get a budget by ID, validating entity ownership.

        Args:
            db: Database session
            budget_id: Budget UUID
            entity_id: Entity UUID for validation

        Returns:
            Budget object if found and belongs to entity, None otherwise
        """
        print(f"INFO [BudgetService]: Getting budget {budget_id}")
        budget = budget_repository.get_budget_by_id(db, budget_id)
        if budget and budget.entity_id != entity_id:
            print(f"ERROR [BudgetService]: Budget {budget_id} does not belong to entity {entity_id}")
            return None
        return budget

    def get_budget_with_spending(
        self,
        db: Session,
        budget_id: UUID,
        entity_id: UUID,
    ) -> Optional[BudgetWithSpendingDTO]:
        """
        Get a budget with spending information.

        Args:
            db: Database session
            budget_id: Budget UUID
            entity_id: Entity UUID for validation

        Returns:
            BudgetWithSpendingDTO if found, None otherwise
        """
        print(f"INFO [BudgetService]: Getting budget {budget_id} with spending")
        budget = self.get_budget(db, budget_id, entity_id)
        if not budget:
            return None

        return self._budget_to_dto_with_spending(db, budget)

    def list_budgets(
        self,
        db: Session,
        entity_id: UUID,
        category_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Budget], int]:
        """
        List budgets for an entity with pagination.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            category_id: Optional category filter
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of budgets, total count)
        """
        print(f"INFO [BudgetService]: Listing budgets for entity {entity_id}")
        budgets = budget_repository.get_budgets_by_entity(
            db=db,
            entity_id=entity_id,
            category_id=category_id,
            skip=skip,
            limit=limit,
        )
        total = budget_repository.count_budgets_by_entity(
            db=db,
            entity_id=entity_id,
            category_id=category_id,
        )
        print(f"INFO [BudgetService]: Found {len(budgets)} budgets (total: {total})")
        return budgets, total

    def list_budgets_with_spending(
        self,
        db: Session,
        entity_id: UUID,
        category_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[BudgetWithSpendingDTO], int]:
        """
        List budgets with spending information for an entity.

        Args:
            db: Database session
            entity_id: Entity UUID to filter by
            category_id: Optional category filter
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (list of budgets with spending, total count)
        """
        print(f"INFO [BudgetService]: Listing budgets with spending for entity {entity_id}")
        budgets, total = self.list_budgets(
            db=db,
            entity_id=entity_id,
            category_id=category_id,
            skip=skip,
            limit=limit,
        )

        budgets_with_spending = [
            self._budget_to_dto_with_spending(db, budget) for budget in budgets
        ]
        print(f"INFO [BudgetService]: Returning {len(budgets_with_spending)} budgets with spending")
        return budgets_with_spending, total

    def update_budget(
        self,
        db: Session,
        budget_id: UUID,
        entity_id: UUID,
        data: BudgetUpdateDTO,
    ) -> Optional[Budget]:
        """
        Update an existing budget.

        Args:
            db: Database session
            budget_id: Budget UUID
            entity_id: Entity UUID for validation
            data: Update data

        Returns:
            Updated Budget object if found and updated, None otherwise
        """
        print(f"INFO [BudgetService]: Updating budget {budget_id}")
        budget = budget_repository.get_budget_by_id(db, budget_id)
        if not budget:
            print(f"ERROR [BudgetService]: Budget {budget_id} not found")
            return None
        if budget.entity_id != entity_id:
            print(f"ERROR [BudgetService]: Budget {budget_id} does not belong to entity {entity_id}")
            return None

        # Update fields if provided
        if data.amount is not None:
            budget.amount = data.amount
        if data.period_type is not None:
            budget.period_type = data.period_type
            # Recalculate end date when period type changes
            budget.end_date = budget_repository._calculate_end_date(
                budget.start_date, data.period_type
            )
        if data.start_date is not None:
            budget.start_date = data.start_date
            # Recalculate end date when start date changes
            budget.end_date = budget_repository._calculate_end_date(
                data.start_date, budget.period_type
            )
        if data.is_active is not None:
            budget.is_active = data.is_active

        updated = budget_repository.update_budget(db, budget)
        print(f"INFO [BudgetService]: Budget {budget_id} updated successfully")
        return updated

    def delete_budget(
        self,
        db: Session,
        budget_id: UUID,
        entity_id: UUID,
    ) -> bool:
        """
        Delete a budget.

        Args:
            db: Database session
            budget_id: Budget UUID
            entity_id: Entity UUID for validation

        Returns:
            True if deleted, False if not found or not owned
        """
        print(f"INFO [BudgetService]: Deleting budget {budget_id}")
        budget = budget_repository.get_budget_by_id(db, budget_id)
        if not budget:
            print(f"ERROR [BudgetService]: Budget {budget_id} not found")
            return False
        if budget.entity_id != entity_id:
            print(f"ERROR [BudgetService]: Budget {budget_id} does not belong to entity {entity_id}")
            return False

        budget_repository.delete_budget(db, budget)
        print(f"INFO [BudgetService]: Budget {budget_id} deleted successfully")
        return True

    def _budget_to_dto_with_spending(
        self, db: Session, budget: Budget
    ) -> BudgetWithSpendingDTO:
        """
        Convert a Budget model to BudgetWithSpendingDTO.

        Args:
            db: Database session
            budget: Budget model

        Returns:
            BudgetWithSpendingDTO with calculated spending
        """
        # Calculate spending for the budget period
        spent_amount = budget_repository.calculate_spending(
            db=db,
            entity_id=budget.entity_id,
            category_id=budget.category_id,
            start_date=budget.start_date,
            end_date=budget.end_date,
        )

        # Calculate percentage
        if budget.amount > 0:
            spent_percentage = (spent_amount / budget.amount) * 100
        else:
            spent_percentage = Decimal("0.00")

        # Get category name
        category = category_repository.get_category_by_id(db, budget.category_id)
        category_name = category.name if category else None

        return BudgetWithSpendingDTO(
            id=budget.id,
            entity_id=budget.entity_id,
            category_id=budget.category_id,
            category_name=category_name,
            amount=budget.amount,
            period_type=budget.period_type,
            start_date=budget.start_date,
            end_date=budget.end_date,
            is_active=budget.is_active,
            spent_amount=spent_amount,
            spent_percentage=round(spent_percentage, 2),
            created_at=budget.created_at,
            updated_at=budget.updated_at,
        )


# Singleton instance
budget_service = BudgetService()
