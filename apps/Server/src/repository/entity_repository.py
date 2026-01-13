"""Entity repository for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.entity import Entity
from src.models.user import User
from src.models.user_entity import UserEntity


class EntityRepository:
    """Repository for Entity and UserEntity database operations."""

    def create_entity(
        self,
        db: Session,
        name: str,
        entity_type: str,
        description: Optional[str] = None,
    ) -> Entity:
        """
        Create a new entity in the database.

        Args:
            db: Database session
            name: Entity name
            entity_type: Entity type (family or startup)
            description: Entity description (optional)

        Returns:
            Created Entity object
        """
        print(f"INFO [EntityRepository]: Creating entity with name '{name}' and type '{entity_type}'")
        entity = Entity(
            name=name,
            type=entity_type,
            description=description,
        )
        db.add(entity)
        db.commit()
        db.refresh(entity)
        print(f"INFO [EntityRepository]: Entity created with id {entity.id}")
        return entity

    def get_entity_by_id(self, db: Session, entity_id: UUID) -> Optional[Entity]:
        """
        Find an entity by ID.

        Args:
            db: Database session
            entity_id: Entity UUID

        Returns:
            Entity object if found, None otherwise
        """
        print(f"INFO [EntityRepository]: Looking up entity by id {entity_id}")
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if entity:
            print(f"INFO [EntityRepository]: Found entity '{entity.name}'")
        else:
            print(f"INFO [EntityRepository]: No entity found with id {entity_id}")
        return entity

    def get_entities_by_user_id(self, db: Session, user_id: UUID) -> list[Entity]:
        """
        Get all entities that a user belongs to.

        Args:
            db: Database session
            user_id: User UUID

        Returns:
            List of Entity objects
        """
        print(f"INFO [EntityRepository]: Getting entities for user {user_id}")
        entities = (
            db.query(Entity)
            .join(UserEntity, Entity.id == UserEntity.entity_id)
            .filter(UserEntity.user_id == user_id)
            .all()
        )
        print(f"INFO [EntityRepository]: Found {len(entities)} entities for user {user_id}")
        return entities

    def update_entity(self, db: Session, entity: Entity) -> Entity:
        """
        Update an existing entity.

        Args:
            db: Database session
            entity: Entity object with updated values

        Returns:
            Updated Entity object
        """
        print(f"INFO [EntityRepository]: Updating entity {entity.id}")
        db.add(entity)
        db.commit()
        db.refresh(entity)
        print(f"INFO [EntityRepository]: Entity {entity.id} updated successfully")
        return entity

    def delete_entity(self, db: Session, entity_id: UUID) -> bool:
        """
        Delete an entity from the database.

        Args:
            db: Database session
            entity_id: Entity UUID

        Returns:
            True if deleted, False if not found
        """
        print(f"INFO [EntityRepository]: Deleting entity {entity_id}")
        entity = db.query(Entity).filter(Entity.id == entity_id).first()
        if entity:
            db.delete(entity)
            db.commit()
            print(f"INFO [EntityRepository]: Entity {entity_id} deleted successfully")
            return True
        print(f"INFO [EntityRepository]: Entity {entity_id} not found for deletion")
        return False

    def add_user_to_entity(
        self,
        db: Session,
        user_id: UUID,
        entity_id: UUID,
        role: str = "user",
    ) -> UserEntity:
        """
        Add a user to an entity with a specific role.

        Args:
            db: Database session
            user_id: User UUID
            entity_id: Entity UUID
            role: User role in the entity (default: "user")

        Returns:
            Created UserEntity object
        """
        print(f"INFO [EntityRepository]: Adding user {user_id} to entity {entity_id} with role '{role}'")
        user_entity = UserEntity(
            user_id=user_id,
            entity_id=entity_id,
            role=role,
        )
        db.add(user_entity)
        db.commit()
        db.refresh(user_entity)
        print(f"INFO [EntityRepository]: User {user_id} added to entity {entity_id}")
        return user_entity

    def remove_user_from_entity(
        self,
        db: Session,
        user_id: UUID,
        entity_id: UUID,
    ) -> bool:
        """
        Remove a user from an entity.

        Args:
            db: Database session
            user_id: User UUID
            entity_id: Entity UUID

        Returns:
            True if removed, False if not found
        """
        print(f"INFO [EntityRepository]: Removing user {user_id} from entity {entity_id}")
        user_entity = (
            db.query(UserEntity)
            .filter(UserEntity.user_id == user_id, UserEntity.entity_id == entity_id)
            .first()
        )
        if user_entity:
            db.delete(user_entity)
            db.commit()
            print(f"INFO [EntityRepository]: User {user_id} removed from entity {entity_id}")
            return True
        print(f"INFO [EntityRepository]: User {user_id} not found in entity {entity_id}")
        return False

    def get_user_entity_role(
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
        print(f"INFO [EntityRepository]: Getting role for user {user_id} in entity {entity_id}")
        user_entity = (
            db.query(UserEntity)
            .filter(UserEntity.user_id == user_id, UserEntity.entity_id == entity_id)
            .first()
        )
        if user_entity:
            print(f"INFO [EntityRepository]: User {user_id} has role '{user_entity.role}' in entity {entity_id}")
            return user_entity.role
        print(f"INFO [EntityRepository]: User {user_id} not found in entity {entity_id}")
        return None

    def get_entity_members(self, db: Session, entity_id: UUID) -> list[dict]:
        """
        Get all members of an entity with user details.

        Args:
            db: Database session
            entity_id: Entity UUID

        Returns:
            List of dicts with user-entity membership info and user details
        """
        print(f"INFO [EntityRepository]: Getting members for entity {entity_id}")
        results = (
            db.query(UserEntity, User)
            .join(User, UserEntity.user_id == User.id)
            .filter(UserEntity.entity_id == entity_id)
            .all()
        )
        members = []
        for user_entity, user in results:
            members.append({
                "id": user_entity.id,
                "user_id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user_entity.role,
                "created_at": user_entity.created_at,
            })
        print(f"INFO [EntityRepository]: Found {len(members)} members for entity {entity_id}")
        return members

    def get_user_entity(
        self,
        db: Session,
        user_id: UUID,
        entity_id: UUID,
    ) -> Optional[UserEntity]:
        """
        Get a specific user-entity membership.

        Args:
            db: Database session
            user_id: User UUID
            entity_id: Entity UUID

        Returns:
            UserEntity object if found, None otherwise
        """
        print(f"INFO [EntityRepository]: Looking up user-entity for user {user_id} in entity {entity_id}")
        user_entity = (
            db.query(UserEntity)
            .filter(UserEntity.user_id == user_id, UserEntity.entity_id == entity_id)
            .first()
        )
        return user_entity

    def count_entity_admins(self, db: Session, entity_id: UUID) -> int:
        """
        Count the number of admins in an entity.

        Args:
            db: Database session
            entity_id: Entity UUID

        Returns:
            Number of admins in the entity
        """
        print(f"INFO [EntityRepository]: Counting admins in entity {entity_id}")
        count = (
            db.query(UserEntity)
            .filter(UserEntity.entity_id == entity_id, UserEntity.role == "admin")
            .count()
        )
        print(f"INFO [EntityRepository]: Entity {entity_id} has {count} admin(s)")
        return count


# Singleton instance
entity_repository = EntityRepository()
