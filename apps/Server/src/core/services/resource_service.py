"""Resource service for business logic operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.interface.resource_dto import ResourceCreateDTO, ResourceUpdateDTO
from src.models.resource import Resource
from src.repository.resource_repository import resource_repository
from src.repository.restaurant_repository import restaurant_repository


class ResourceService:
    """Service for resource business logic with restaurant-scoped authorization."""

    def _check_restaurant_access(self, db: Session, user_id: UUID, restaurant_id: UUID) -> None:
        """
        Check that a user has membership in a restaurant.

        Args:
            db: Database session
            user_id: User UUID
            restaurant_id: Restaurant UUID

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        role = restaurant_repository.get_user_restaurant_role(db, user_id, restaurant_id)
        if role is None:
            print(f"ERROR [ResourceService]: User {user_id} doesn't have access to restaurant {restaurant_id}")
            raise PermissionError("User doesn't have access to this restaurant")

    def create_resource(
        self,
        db: Session,
        user_id: UUID,
        data: ResourceCreateDTO,
    ) -> Resource:
        """
        Create a new resource in a restaurant.

        Args:
            db: Database session
            user_id: ID of the user creating the resource
            data: Resource creation data

        Returns:
            Created Resource object

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        print(f"INFO [ResourceService]: Creating resource '{data.name}' in restaurant {data.restaurant_id} by user {user_id}")

        self._check_restaurant_access(db, user_id, data.restaurant_id)

        resource = resource_repository.create(
            db=db,
            restaurant_id=data.restaurant_id,
            resource_type=data.type.value,
            name=data.name,
            unit=data.unit,
            current_stock=data.current_stock,
            minimum_stock=data.minimum_stock,
            last_unit_cost=data.last_unit_cost,
        )

        if resource.current_stock < resource.minimum_stock:
            print(f"WARNING [ResourceService]: Resource '{resource.name}' is below minimum stock ({resource.current_stock} < {resource.minimum_stock})")

        print(f"INFO [ResourceService]: Resource '{resource.name}' created with id {resource.id}")
        return resource

    def get_resources(
        self,
        db: Session,
        user_id: UUID,
        restaurant_id: UUID,
        type_filter: Optional[str] = None,
    ) -> list[Resource]:
        """
        Get all resources in a restaurant.

        Args:
            db: Database session
            user_id: User UUID
            restaurant_id: Restaurant UUID
            type_filter: Optional resource type to filter by

        Returns:
            List of Resource objects

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        print(f"INFO [ResourceService]: Getting resources for restaurant {restaurant_id} by user {user_id}")

        self._check_restaurant_access(db, user_id, restaurant_id)

        return resource_repository.get_by_restaurant(db, restaurant_id, type_filter)

    def get_resource(
        self,
        db: Session,
        user_id: UUID,
        resource_id: UUID,
    ) -> Resource:
        """
        Get a resource by ID if user has access to the resource's restaurant.

        Args:
            db: Database session
            user_id: User UUID
            resource_id: Resource UUID

        Returns:
            Resource object

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If resource not found
        """
        print(f"INFO [ResourceService]: Getting resource {resource_id} for user {user_id}")

        resource = resource_repository.get_by_id(db, resource_id)
        if resource is None:
            print(f"ERROR [ResourceService]: Resource {resource_id} not found")
            raise ValueError("Resource not found")

        self._check_restaurant_access(db, user_id, resource.restaurant_id)

        return resource

    def update_resource(
        self,
        db: Session,
        user_id: UUID,
        resource_id: UUID,
        data: ResourceUpdateDTO,
    ) -> Resource:
        """
        Update a resource if user has access to the resource's restaurant.

        Args:
            db: Database session
            user_id: User UUID
            resource_id: Resource UUID
            data: Resource update data

        Returns:
            Updated Resource object

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If resource not found
        """
        print(f"INFO [ResourceService]: Updating resource {resource_id} by user {user_id}")

        resource = resource_repository.get_by_id(db, resource_id)
        if resource is None:
            print(f"ERROR [ResourceService]: Resource {resource_id} not found")
            raise ValueError("Resource not found")

        self._check_restaurant_access(db, user_id, resource.restaurant_id)

        # Update fields if provided
        if data.type is not None:
            resource.type = data.type.value
        if data.name is not None:
            resource.name = data.name
        if data.unit is not None:
            resource.unit = data.unit
        if data.current_stock is not None:
            resource.current_stock = data.current_stock
        if data.minimum_stock is not None:
            resource.minimum_stock = data.minimum_stock
        if data.last_unit_cost is not None:
            resource.last_unit_cost = data.last_unit_cost

        updated_resource = resource_repository.update(db, resource)

        if updated_resource.current_stock < updated_resource.minimum_stock:
            print(f"WARNING [ResourceService]: Resource '{updated_resource.name}' stock dropped below minimum ({updated_resource.current_stock} < {updated_resource.minimum_stock})")

        print(f"INFO [ResourceService]: Resource {resource_id} updated successfully")
        return updated_resource

    def delete_resource(
        self,
        db: Session,
        user_id: UUID,
        resource_id: UUID,
    ) -> bool:
        """
        Delete a resource if user has access to the resource's restaurant.

        Args:
            db: Database session
            user_id: User UUID
            resource_id: Resource UUID

        Returns:
            True if deleted

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If resource not found
        """
        print(f"INFO [ResourceService]: Deleting resource {resource_id} by user {user_id}")

        resource = resource_repository.get_by_id(db, resource_id)
        if resource is None:
            print(f"ERROR [ResourceService]: Resource {resource_id} not found")
            raise ValueError("Resource not found")

        self._check_restaurant_access(db, user_id, resource.restaurant_id)

        deleted = resource_repository.delete(db, resource_id)
        if not deleted:
            print(f"ERROR [ResourceService]: Resource {resource_id} not found for deletion")
            raise ValueError("Resource not found")

        print(f"INFO [ResourceService]: Resource {resource_id} deleted successfully")
        return True

    def get_low_stock_resources(
        self,
        db: Session,
        user_id: UUID,
        restaurant_id: UUID,
    ) -> list[Resource]:
        """
        Get resources where current_stock < minimum_stock for a restaurant.

        Args:
            db: Database session
            user_id: User UUID
            restaurant_id: Restaurant UUID

        Returns:
            List of low-stock Resource objects

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        print(f"INFO [ResourceService]: Getting low-stock resources for restaurant {restaurant_id} by user {user_id}")

        self._check_restaurant_access(db, user_id, restaurant_id)

        return resource_repository.get_low_stock(db, restaurant_id)


# Singleton instance
resource_service = ResourceService()
