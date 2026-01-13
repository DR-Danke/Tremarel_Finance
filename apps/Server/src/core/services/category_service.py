"""Category service for business logic operations."""

from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.interface.category_dto import CategoryCreateDTO, CategoryTreeDTO, CategoryUpdateDTO
from src.models.category import Category
from src.repository.category_repository import category_repository


class CategoryService:
    """Service for Category business logic."""

    def create_category(self, db: Session, data: CategoryCreateDTO) -> Category:
        """
        Create a new category.

        Args:
            db: Database session
            data: Category creation data

        Returns:
            Created Category object

        Raises:
            ValueError: If validation fails
        """
        print(f"INFO [CategoryService]: Creating category '{data.name}' for entity {data.entity_id}")

        # Validate parent_id if provided
        if data.parent_id is not None:
            parent = category_repository.get_category_by_id(db, data.parent_id)
            if parent is None:
                print(f"ERROR [CategoryService]: Parent category {data.parent_id} not found")
                raise ValueError("Parent category not found")

            # Validate parent belongs to same entity
            if parent.entity_id != data.entity_id:
                print(
                    f"ERROR [CategoryService]: Parent category {data.parent_id} "
                    f"belongs to different entity"
                )
                raise ValueError("Parent category belongs to a different entity")

            # Validate parent has same type
            if parent.type != data.type:
                print(
                    f"ERROR [CategoryService]: Parent category type '{parent.type}' "
                    f"does not match '{data.type}'"
                )
                raise ValueError(
                    f"Parent category type '{parent.type}' does not match "
                    f"child type '{data.type}'"
                )

        category = category_repository.create_category(
            db=db,
            entity_id=data.entity_id,
            name=data.name,
            type=data.type,
            parent_id=data.parent_id,
            description=data.description,
            color=data.color,
            icon=data.icon,
        )

        print(f"INFO [CategoryService]: Category '{data.name}' created with id {category.id}")
        return category

    def get_category(
        self, db: Session, category_id: UUID, entity_id: UUID
    ) -> Optional[Category]:
        """
        Get a category by ID, validating it belongs to the entity.

        Args:
            db: Database session
            category_id: Category UUID
            entity_id: Entity UUID for validation

        Returns:
            Category object if found and belongs to entity, None otherwise
        """
        print(f"INFO [CategoryService]: Getting category {category_id} for entity {entity_id}")
        category = category_repository.get_category_by_id(db, category_id)

        if category is None:
            print(f"INFO [CategoryService]: Category {category_id} not found")
            return None

        if category.entity_id != entity_id:
            print(
                f"ERROR [CategoryService]: Category {category_id} does not belong "
                f"to entity {entity_id}"
            )
            return None

        return category

    def get_categories_for_entity(
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
        print(f"INFO [CategoryService]: Getting categories for entity {entity_id}")
        return category_repository.get_categories_by_entity(db, entity_id, include_inactive)

    def get_category_tree(self, db: Session, entity_id: UUID) -> List[CategoryTreeDTO]:
        """
        Get hierarchical category tree for an entity.

        Args:
            db: Database session
            entity_id: Entity UUID

        Returns:
            List of root CategoryTreeDTO objects with nested children
        """
        print(f"INFO [CategoryService]: Building category tree for entity {entity_id}")

        # Get all active categories for the entity
        categories = category_repository.get_categories_by_entity(db, entity_id)

        # Build a mapping of category id to CategoryTreeDTO
        category_map: Dict[UUID, CategoryTreeDTO] = {}
        for cat in categories:
            category_map[cat.id] = CategoryTreeDTO(
                id=cat.id,
                entity_id=cat.entity_id,
                name=cat.name,
                type=cat.type,
                parent_id=cat.parent_id,
                description=cat.description,
                color=cat.color,
                icon=cat.icon,
                is_active=cat.is_active,
                created_at=cat.created_at,
                updated_at=cat.updated_at,
                children=[],
            )

        # Build tree structure
        root_categories: List[CategoryTreeDTO] = []
        for cat_id, cat_dto in category_map.items():
            if cat_dto.parent_id is None:
                root_categories.append(cat_dto)
            else:
                parent_dto = category_map.get(cat_dto.parent_id)
                if parent_dto is not None:
                    parent_dto.children.append(cat_dto)

        # Sort root categories and children by name
        root_categories.sort(key=lambda c: c.name)
        for cat_dto in category_map.values():
            cat_dto.children.sort(key=lambda c: c.name)

        print(f"INFO [CategoryService]: Built tree with {len(root_categories)} root categories")
        return root_categories

    def update_category(
        self,
        db: Session,
        category_id: UUID,
        entity_id: UUID,
        data: CategoryUpdateDTO,
    ) -> Optional[Category]:
        """
        Update an existing category.

        Args:
            db: Database session
            category_id: Category UUID to update
            entity_id: Entity UUID for validation
            data: Category update data

        Returns:
            Updated Category object if found, None otherwise

        Raises:
            ValueError: If validation fails (e.g., circular reference)
        """
        print(f"INFO [CategoryService]: Updating category {category_id}")

        category = self.get_category(db, category_id, entity_id)
        if category is None:
            return None

        # Update parent_id if provided
        if data.parent_id is not None:
            # Prevent setting self as parent
            if data.parent_id == category_id:
                print(f"ERROR [CategoryService]: Cannot set category as its own parent")
                raise ValueError("Category cannot be its own parent")

            # Check parent exists and belongs to same entity
            parent = category_repository.get_category_by_id(db, data.parent_id)
            if parent is None:
                print(f"ERROR [CategoryService]: Parent category {data.parent_id} not found")
                raise ValueError("Parent category not found")

            if parent.entity_id != entity_id:
                print(f"ERROR [CategoryService]: Parent belongs to different entity")
                raise ValueError("Parent category belongs to a different entity")

            # Check parent has same type
            if parent.type != category.type:
                print(f"ERROR [CategoryService]: Parent type mismatch")
                raise ValueError(
                    f"Parent category type '{parent.type}' does not match "
                    f"category type '{category.type}'"
                )

            # Check for circular reference
            if self._would_create_cycle(db, category_id, data.parent_id):
                print(f"ERROR [CategoryService]: Circular reference detected")
                raise ValueError("This change would create a circular reference")

            category.parent_id = data.parent_id

        # Update other fields if provided
        if data.name is not None:
            category.name = data.name
        if data.description is not None:
            category.description = data.description
        if data.color is not None:
            category.color = data.color
        if data.icon is not None:
            category.icon = data.icon
        if data.is_active is not None:
            category.is_active = data.is_active

        updated = category_repository.update_category(db, category)
        print(f"INFO [CategoryService]: Category {category_id} updated successfully")
        return updated

    def delete_category(
        self, db: Session, category_id: UUID, entity_id: UUID
    ) -> bool:
        """
        Delete a category.

        Args:
            db: Database session
            category_id: Category UUID to delete
            entity_id: Entity UUID for validation

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If category has children or transactions
        """
        print(f"INFO [CategoryService]: Deleting category {category_id}")

        category = self.get_category(db, category_id, entity_id)
        if category is None:
            print(f"ERROR [CategoryService]: Category {category_id} not found")
            raise ValueError("Category not found")

        # Check for children
        if category_repository.has_children(db, category_id):
            print(f"ERROR [CategoryService]: Category {category_id} has children")
            raise ValueError("Cannot delete category with subcategories")

        # Check for transactions
        if category_repository.has_transactions(db, category_id):
            print(f"ERROR [CategoryService]: Category {category_id} has transactions")
            raise ValueError("Cannot delete category with transactions")

        result = category_repository.delete_category(db, category_id)
        print(f"INFO [CategoryService]: Category {category_id} deleted: {result}")
        return result

    def _would_create_cycle(
        self, db: Session, category_id: UUID, new_parent_id: UUID
    ) -> bool:
        """
        Check if setting new_parent_id as parent would create a cycle.

        Args:
            db: Database session
            category_id: Category being updated
            new_parent_id: Proposed new parent ID

        Returns:
            True if a cycle would be created
        """
        # Walk up the tree from new_parent_id
        current_id = new_parent_id
        visited = {category_id}  # Include the category being updated

        while current_id is not None:
            if current_id in visited:
                return True
            visited.add(current_id)

            parent = category_repository.get_category_by_id(db, current_id)
            if parent is None:
                break
            current_id = parent.parent_id

        return False


# Singleton instance
category_service = CategoryService()
