"""Entity service for business logic operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.interface.entity_dto import EntityCreateDTO, EntityUpdateDTO
from src.models.entity import Entity
from src.models.user_entity import UserEntity
from src.repository.entity_repository import entity_repository


class EntityService:
    """Service for entity business logic."""

    def create_entity(
        self,
        db: Session,
        user_id: UUID,
        entity_data: EntityCreateDTO,
    ) -> Entity:
        """
        Create a new entity and add the creator as admin.

        Args:
            db: Database session
            user_id: ID of the user creating the entity
            entity_data: Entity creation data

        Returns:
            Created Entity object
        """
        print(f"INFO [EntityService]: Creating entity '{entity_data.name}' for user {user_id}")

        # Create the entity
        entity = entity_repository.create_entity(
            db=db,
            name=entity_data.name,
            entity_type=entity_data.type,
            description=entity_data.description,
        )

        # Add creator as admin of the entity
        entity_repository.add_user_to_entity(
            db=db,
            user_id=user_id,
            entity_id=entity.id,
            role="admin",
        )

        print(f"INFO [EntityService]: Entity '{entity.name}' created with user {user_id} as admin")
        return entity

    def get_user_entities(self, db: Session, user_id: UUID) -> list[Entity]:
        """
        Get all entities that a user belongs to.

        Args:
            db: Database session
            user_id: User UUID

        Returns:
            List of Entity objects
        """
        print(f"INFO [EntityService]: Getting entities for user {user_id}")
        return entity_repository.get_entities_by_user_id(db, user_id)

    def get_entity(
        self,
        db: Session,
        entity_id: UUID,
        user_id: UUID,
    ) -> Optional[Entity]:
        """
        Get an entity by ID if user has access.

        Args:
            db: Database session
            entity_id: Entity UUID
            user_id: User UUID requesting access

        Returns:
            Entity object if user has access, None otherwise

        Raises:
            PermissionError: If user doesn't have access to the entity
        """
        print(f"INFO [EntityService]: Getting entity {entity_id} for user {user_id}")

        # Check if user has access to the entity
        role = entity_repository.get_user_entity_role(db, user_id, entity_id)
        if role is None:
            print(f"ERROR [EntityService]: User {user_id} doesn't have access to entity {entity_id}")
            raise PermissionError("User doesn't have access to this entity")

        entity = entity_repository.get_entity_by_id(db, entity_id)
        return entity

    def update_entity(
        self,
        db: Session,
        entity_id: UUID,
        user_id: UUID,
        entity_data: EntityUpdateDTO,
    ) -> Entity:
        """
        Update an entity if user has admin or manager role.

        Args:
            db: Database session
            entity_id: Entity UUID
            user_id: User UUID
            entity_data: Entity update data

        Returns:
            Updated Entity object

        Raises:
            PermissionError: If user doesn't have admin/manager role
            ValueError: If entity not found
        """
        print(f"INFO [EntityService]: Updating entity {entity_id} by user {user_id}")

        # Check user role
        role = entity_repository.get_user_entity_role(db, user_id, entity_id)
        if role not in ("admin", "manager"):
            print(f"ERROR [EntityService]: User {user_id} doesn't have permission to update entity {entity_id}")
            raise PermissionError("Only admin or manager can update entity")

        # Get entity
        entity = entity_repository.get_entity_by_id(db, entity_id)
        if entity is None:
            print(f"ERROR [EntityService]: Entity {entity_id} not found")
            raise ValueError("Entity not found")

        # Update fields if provided
        if entity_data.name is not None:
            entity.name = entity_data.name
        if entity_data.description is not None:
            entity.description = entity_data.description

        updated_entity = entity_repository.update_entity(db, entity)
        print(f"INFO [EntityService]: Entity {entity_id} updated successfully")
        return updated_entity

    def delete_entity(
        self,
        db: Session,
        entity_id: UUID,
        user_id: UUID,
    ) -> bool:
        """
        Delete an entity if user has admin role.

        Args:
            db: Database session
            entity_id: Entity UUID
            user_id: User UUID

        Returns:
            True if deleted

        Raises:
            PermissionError: If user doesn't have admin role
            ValueError: If entity not found
        """
        print(f"INFO [EntityService]: Deleting entity {entity_id} by user {user_id}")

        # Check user role
        role = entity_repository.get_user_entity_role(db, user_id, entity_id)
        if role != "admin":
            print(f"ERROR [EntityService]: User {user_id} doesn't have admin permission to delete entity {entity_id}")
            raise PermissionError("Only admin can delete entity")

        # Delete entity
        deleted = entity_repository.delete_entity(db, entity_id)
        if not deleted:
            print(f"ERROR [EntityService]: Entity {entity_id} not found for deletion")
            raise ValueError("Entity not found")

        print(f"INFO [EntityService]: Entity {entity_id} deleted successfully")
        return True

    def add_member(
        self,
        db: Session,
        entity_id: UUID,
        user_id: UUID,
        target_user_id: UUID,
        role: str = "user",
    ) -> UserEntity:
        """
        Add a member to an entity.

        Args:
            db: Database session
            entity_id: Entity UUID
            user_id: User UUID performing the action
            target_user_id: User UUID to add to entity
            role: Role for the new member

        Returns:
            Created UserEntity object

        Raises:
            PermissionError: If user doesn't have admin/manager role
            ValueError: If target user is already a member
        """
        print(f"INFO [EntityService]: Adding user {target_user_id} to entity {entity_id} by user {user_id}")

        # Check user role
        current_role = entity_repository.get_user_entity_role(db, user_id, entity_id)
        if current_role not in ("admin", "manager"):
            print(f"ERROR [EntityService]: User {user_id} doesn't have permission to add members to entity {entity_id}")
            raise PermissionError("Only admin or manager can add members")

        # Check if target user is already a member
        existing_role = entity_repository.get_user_entity_role(db, target_user_id, entity_id)
        if existing_role is not None:
            print(f"ERROR [EntityService]: User {target_user_id} is already a member of entity {entity_id}")
            raise ValueError("User is already a member of this entity")

        # Add member
        user_entity = entity_repository.add_user_to_entity(db, target_user_id, entity_id, role)
        print(f"INFO [EntityService]: User {target_user_id} added to entity {entity_id} with role '{role}'")
        return user_entity

    def remove_member(
        self,
        db: Session,
        entity_id: UUID,
        user_id: UUID,
        target_user_id: UUID,
    ) -> bool:
        """
        Remove a member from an entity.

        Args:
            db: Database session
            entity_id: Entity UUID
            user_id: User UUID performing the action
            target_user_id: User UUID to remove from entity

        Returns:
            True if removed

        Raises:
            PermissionError: If user doesn't have admin role
            ValueError: If target user is not a member or is the last admin
        """
        print(f"INFO [EntityService]: Removing user {target_user_id} from entity {entity_id} by user {user_id}")

        # Check user role
        current_role = entity_repository.get_user_entity_role(db, user_id, entity_id)
        if current_role != "admin":
            print(f"ERROR [EntityService]: User {user_id} doesn't have admin permission to remove members")
            raise PermissionError("Only admin can remove members")

        # Check if target user is a member
        target_role = entity_repository.get_user_entity_role(db, target_user_id, entity_id)
        if target_role is None:
            print(f"ERROR [EntityService]: User {target_user_id} is not a member of entity {entity_id}")
            raise ValueError("User is not a member of this entity")

        # Check if removing the last admin
        if target_role == "admin":
            admin_count = entity_repository.count_entity_admins(db, entity_id)
            if admin_count <= 1:
                print(f"ERROR [EntityService]: Cannot remove the last admin from entity {entity_id}")
                raise ValueError("Cannot remove the last admin from entity")

        # Remove member
        entity_repository.remove_user_from_entity(db, target_user_id, entity_id)
        print(f"INFO [EntityService]: User {target_user_id} removed from entity {entity_id}")
        return True

    def get_user_role_in_entity(
        self,
        db: Session,
        user_id: UUID,
        entity_id: UUID,
    ) -> Optional[str]:
        """
        Get a user's role in a specific entity.

        Args:
            db: Database session
            user_id: User UUID
            entity_id: Entity UUID

        Returns:
            Role string if found, None otherwise
        """
        print(f"INFO [EntityService]: Getting role for user {user_id} in entity {entity_id}")
        return entity_repository.get_user_entity_role(db, user_id, entity_id)

    def get_entity_members(self, db: Session, entity_id: UUID, user_id: UUID) -> list[dict]:
        """
        Get all members of an entity.

        Args:
            db: Database session
            entity_id: Entity UUID
            user_id: User UUID requesting the list

        Returns:
            List of member dicts with user details

        Raises:
            PermissionError: If user doesn't have access to the entity
        """
        print(f"INFO [EntityService]: Getting members for entity {entity_id} by user {user_id}")

        # Check if user has access to the entity
        role = entity_repository.get_user_entity_role(db, user_id, entity_id)
        if role is None:
            print(f"ERROR [EntityService]: User {user_id} doesn't have access to entity {entity_id}")
            raise PermissionError("User doesn't have access to this entity")

        return entity_repository.get_entity_members(db, entity_id)


# Singleton instance
entity_service = EntityService()
