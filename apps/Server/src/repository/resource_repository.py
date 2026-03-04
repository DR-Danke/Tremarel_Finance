"""Resource repository for database operations."""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.resource import Resource


class ResourceRepository:
    """Repository for Resource database operations."""

    def create(
        self,
        db: Session,
        restaurant_id: UUID,
        resource_type: str,
        name: str,
        unit: str,
        current_stock: Decimal,
        minimum_stock: Decimal,
        last_unit_cost: Decimal,
    ) -> Resource:
        """
        Create a new resource in a restaurant.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            resource_type: Resource type (producto, activo, servicio)
            name: Resource name
            unit: Unit of measurement
            current_stock: Current stock quantity
            minimum_stock: Minimum stock threshold
            last_unit_cost: Last unit cost

        Returns:
            Created Resource object
        """
        print(f"INFO [ResourceRepository]: Creating resource '{name}' for restaurant {restaurant_id}")
        resource = Resource(
            restaurant_id=restaurant_id,
            type=resource_type,
            name=name,
            unit=unit,
            current_stock=current_stock,
            minimum_stock=minimum_stock,
            last_unit_cost=last_unit_cost,
        )
        db.add(resource)
        db.commit()
        db.refresh(resource)
        print(f"INFO [ResourceRepository]: Resource created with id {resource.id}")
        return resource

    def get_by_id(self, db: Session, resource_id: UUID) -> Optional[Resource]:
        """
        Find a resource by ID.

        Args:
            db: Database session
            resource_id: Resource UUID

        Returns:
            Resource object if found, None otherwise
        """
        print(f"INFO [ResourceRepository]: Looking up resource by id {resource_id}")
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if resource:
            print(f"INFO [ResourceRepository]: Found resource '{resource.name}'")
        else:
            print(f"INFO [ResourceRepository]: No resource found with id {resource_id}")
        return resource

    def get_by_restaurant(
        self,
        db: Session,
        restaurant_id: UUID,
        type_filter: Optional[str] = None,
    ) -> list[Resource]:
        """
        Get all resources in a restaurant, with optional type filter.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            type_filter: Optional resource type to filter by

        Returns:
            List of Resource objects
        """
        print(f"INFO [ResourceRepository]: Getting resources for restaurant {restaurant_id} (type_filter={type_filter})")
        query = db.query(Resource).filter(Resource.restaurant_id == restaurant_id)
        if type_filter:
            query = query.filter(Resource.type == type_filter)
        resources = query.all()
        print(f"INFO [ResourceRepository]: Found {len(resources)} resources for restaurant {restaurant_id}")
        return resources

    def update(self, db: Session, resource: Resource) -> Resource:
        """
        Update an existing resource.

        Args:
            db: Database session
            resource: Resource object with updated values

        Returns:
            Updated Resource object
        """
        print(f"INFO [ResourceRepository]: Updating resource {resource.id}")
        db.add(resource)
        db.commit()
        db.refresh(resource)
        print(f"INFO [ResourceRepository]: Resource {resource.id} updated successfully")
        return resource

    def delete(self, db: Session, resource_id: UUID) -> bool:
        """
        Delete a resource from the database.

        Args:
            db: Database session
            resource_id: Resource UUID

        Returns:
            True if deleted, False if not found
        """
        print(f"INFO [ResourceRepository]: Deleting resource {resource_id}")
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if resource:
            db.delete(resource)
            db.commit()
            print(f"INFO [ResourceRepository]: Resource {resource_id} deleted successfully")
            return True
        print(f"INFO [ResourceRepository]: Resource {resource_id} not found for deletion")
        return False

    def find_by_name(self, db: Session, restaurant_id: UUID, name: str) -> Optional[Resource]:
        """
        Find a resource by name within a restaurant (case-insensitive).

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            name: Resource name to search for

        Returns:
            Resource object if found, None otherwise
        """
        print(f"INFO [ResourceRepository]: Looking up resource by name '{name}' in restaurant {restaurant_id}")
        resource = (
            db.query(Resource)
            .filter(
                Resource.restaurant_id == restaurant_id,
                func.lower(Resource.name) == name.lower(),
            )
            .first()
        )
        if resource:
            print(f"INFO [ResourceRepository]: Found resource '{resource.name}' (id={resource.id})")
        else:
            print(f"INFO [ResourceRepository]: No resource found with name '{name}'")
        return resource

    def get_low_stock(self, db: Session, restaurant_id: UUID) -> list[Resource]:
        """
        Get resources where current_stock < minimum_stock for a restaurant.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID

        Returns:
            List of low-stock Resource objects
        """
        print(f"INFO [ResourceRepository]: Getting low-stock resources for restaurant {restaurant_id}")
        resources = (
            db.query(Resource)
            .filter(
                Resource.restaurant_id == restaurant_id,
                Resource.current_stock < Resource.minimum_stock,
            )
            .all()
        )
        print(f"INFO [ResourceRepository]: Found {len(resources)} low-stock resources")
        return resources


    def count(self, db: Session, restaurant_id: UUID) -> int:
        """
        Count all resources for a restaurant.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID

        Returns:
            Count of resources
        """
        print(f"INFO [ResourceRepository]: Counting resources for restaurant {restaurant_id}")
        count = (
            db.query(Resource)
            .filter(Resource.restaurant_id == restaurant_id)
            .count()
        )
        print(f"INFO [ResourceRepository]: Found {count} resources")
        return count


# Singleton instance
resource_repository = ResourceRepository()
