"""Category repository for database operations."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.category import Category


class CategoryRepository:
    """Repository for Category database operations."""

    def create_category(
        self,
        db: Session,
        entity_id: UUID,
        name: str,
        type: str,
        parent_id: Optional[UUID] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
    ) -> Category:
        """
        Create a new category in the database.

        Args:
            db: Database session
            entity_id: Entity ID the category belongs to
            name: Category name
            type: Category type ('income' or 'expense')
            parent_id: Parent category ID (optional)
            description: Category description (optional)
            color: Category color (optional)
            icon: Category icon (optional)

        Returns:
            Created Category object
        """
        print(f"INFO [CategoryRepository]: Creating category '{name}' for entity {entity_id}")
        category = Category(
            entity_id=entity_id,
            name=name,
            type=type,
            parent_id=parent_id,
            description=description,
            color=color,
            icon=icon,
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        print(f"INFO [CategoryRepository]: Category created with id {category.id}")
        return category

    def get_category_by_id(self, db: Session, category_id: UUID) -> Optional[Category]:
        """
        Find a category by ID.

        Args:
            db: Database session
            category_id: Category UUID

        Returns:
            Category object if found, None otherwise
        """
        print(f"INFO [CategoryRepository]: Looking up category by id {category_id}")
        category = db.query(Category).filter(Category.id == category_id).first()
        if category:
            print(f"INFO [CategoryRepository]: Found category '{category.name}'")
        else:
            print(f"INFO [CategoryRepository]: No category found with id {category_id}")
        return category

    def get_categories_by_entity(
        self, db: Session, entity_id: UUID, include_inactive: bool = False
    ) -> List[Category]:
        """
        Get all categories for an entity.

        Args:
            db: Database session
            entity_id: Entity UUID
            include_inactive: Whether to include inactive categories

        Returns:
            List of Category objects
        """
        print(f"INFO [CategoryRepository]: Getting categories for entity {entity_id}")
        query = db.query(Category).filter(Category.entity_id == entity_id)
        if not include_inactive:
            query = query.filter(Category.is_active.is_(True))
        categories = query.order_by(Category.name).all()
        print(f"INFO [CategoryRepository]: Found {len(categories)} categories")
        return categories

    def get_categories_by_parent(
        self, db: Session, entity_id: UUID, parent_id: Optional[UUID]
    ) -> List[Category]:
        """
        Get categories with a specific parent.

        Args:
            db: Database session
            entity_id: Entity UUID
            parent_id: Parent category UUID (None for root categories)

        Returns:
            List of Category objects
        """
        print(f"INFO [CategoryRepository]: Getting categories with parent {parent_id}")
        query = db.query(Category).filter(
            Category.entity_id == entity_id,
            Category.is_active.is_(True),
        )
        if parent_id is None:
            query = query.filter(Category.parent_id.is_(None))
        else:
            query = query.filter(Category.parent_id == parent_id)
        categories = query.order_by(Category.name).all()
        print(f"INFO [CategoryRepository]: Found {len(categories)} categories")
        return categories

    def get_root_categories(self, db: Session, entity_id: UUID) -> List[Category]:
        """
        Get root categories (no parent) for an entity.

        Args:
            db: Database session
            entity_id: Entity UUID

        Returns:
            List of root Category objects
        """
        print(f"INFO [CategoryRepository]: Getting root categories for entity {entity_id}")
        return self.get_categories_by_parent(db, entity_id, None)

    def update_category(self, db: Session, category: Category) -> Category:
        """
        Update an existing category.

        Args:
            db: Database session
            category: Category object with updated values

        Returns:
            Updated Category object
        """
        print(f"INFO [CategoryRepository]: Updating category {category.id}")
        db.add(category)
        db.commit()
        db.refresh(category)
        print(f"INFO [CategoryRepository]: Category {category.id} updated successfully")
        return category

    def delete_category(self, db: Session, category_id: UUID) -> bool:
        """
        Delete a category from the database.

        Args:
            db: Database session
            category_id: Category UUID to delete

        Returns:
            True if deleted, False if not found
        """
        print(f"INFO [CategoryRepository]: Deleting category {category_id}")
        category = self.get_category_by_id(db, category_id)
        if category is None:
            print(f"ERROR [CategoryRepository]: Category {category_id} not found for deletion")
            return False
        db.delete(category)
        db.commit()
        print(f"INFO [CategoryRepository]: Category {category_id} deleted successfully")
        return True

    def has_children(self, db: Session, category_id: UUID) -> bool:
        """
        Check if a category has child categories.

        Args:
            db: Database session
            category_id: Category UUID to check

        Returns:
            True if category has children, False otherwise
        """
        print(f"INFO [CategoryRepository]: Checking if category {category_id} has children")
        count = db.query(Category).filter(Category.parent_id == category_id).count()
        has_kids = count > 0
        print(f"INFO [CategoryRepository]: Category {category_id} has {count} children")
        return has_kids

    def has_transactions(self, db: Session, category_id: UUID) -> bool:
        """
        Check if a category has any transactions.

        Args:
            db: Database session
            category_id: Category UUID to check

        Returns:
            True if category has transactions, False otherwise
        """
        print(f"INFO [CategoryRepository]: Checking if category {category_id} has transactions")
        # Import here to avoid circular imports
        from sqlalchemy import text

        # Use raw SQL since Transaction model may not exist yet
        result = db.execute(
            text("SELECT COUNT(*) FROM transactions WHERE category_id = :category_id"),
            {"category_id": str(category_id)},
        ).scalar()
        has_txns = result > 0 if result else False
        print(f"INFO [CategoryRepository]: Category {category_id} has {result} transactions")
        return has_txns


# Singleton instance
category_repository = CategoryRepository()
