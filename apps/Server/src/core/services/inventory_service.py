"""Inventory service for business logic operations on inventory movements."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.interface.inventory_movement_dto import InventoryMovementCreateDTO, MovementType
from src.models.inventory_movement import InventoryMovement
from src.repository.inventory_movement_repository import inventory_movement_repository
from src.repository.resource_repository import resource_repository
from src.repository.restaurant_repository import restaurant_repository


class InventoryService:
    """Service for inventory movement business logic with restaurant-scoped authorization."""

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
            print(f"ERROR [InventoryService]: User {user_id} doesn't have access to restaurant {restaurant_id}")
            raise PermissionError("User doesn't have access to this restaurant")

    def create_movement(
        self,
        db: Session,
        user_id: UUID,
        data: InventoryMovementCreateDTO,
    ) -> InventoryMovement:
        """
        Create an inventory movement and atomically update resource stock.

        Args:
            db: Database session
            user_id: ID of the user creating the movement
            data: Movement creation data

        Returns:
            Created InventoryMovement object

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If resource not found, restaurant mismatch, or insufficient stock
        """
        print(f"INFO [InventoryService]: Creating {data.type.value} movement for resource {data.resource_id} by user {user_id}")

        self._check_restaurant_access(db, user_id, data.restaurant_id)

        resource = resource_repository.get_by_id(db, data.resource_id)
        if resource is None:
            print(f"ERROR [InventoryService]: Resource {data.resource_id} not found")
            raise ValueError("Resource not found")

        if resource.restaurant_id != data.restaurant_id:
            print(f"ERROR [InventoryService]: Resource {data.resource_id} does not belong to restaurant {data.restaurant_id}")
            raise ValueError("Resource does not belong to this restaurant")

        if data.type == MovementType.EXIT:
            if resource.current_stock < data.quantity:
                print(f"ERROR [InventoryService]: Insufficient stock for resource {data.resource_id}: current_stock is {resource.current_stock} but requested {data.quantity}")
                raise ValueError(f"Insufficient stock: current_stock is {resource.current_stock} but requested {data.quantity}")

        movement = inventory_movement_repository.create(
            db=db,
            resource_id=data.resource_id,
            movement_type=data.type.value,
            quantity=data.quantity,
            reason=data.reason.value,
            date=data.date,
            person_id=data.person_id,
            restaurant_id=data.restaurant_id,
            notes=data.notes,
        )

        if data.type == MovementType.ENTRY:
            resource.current_stock = resource.current_stock + data.quantity
        else:
            resource.current_stock = resource.current_stock - data.quantity

        resource_repository.update(db, resource)

        if resource.current_stock < resource.minimum_stock:
            print(f"WARNING [InventoryService]: Resource '{resource.name}' is below minimum stock (current: {resource.current_stock}, minimum: {resource.minimum_stock})")

        print(f"INFO [InventoryService]: Movement created with id {movement.id}, resource stock updated to {resource.current_stock}")
        return movement

    def get_movements_by_resource(
        self,
        db: Session,
        user_id: UUID,
        resource_id: UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list[InventoryMovement]:
        """
        Get movement history for a resource.

        Args:
            db: Database session
            user_id: User UUID
            resource_id: Resource UUID
            date_from: Optional start date filter
            date_to: Optional end date filter

        Returns:
            List of InventoryMovement objects

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If resource not found
        """
        print(f"INFO [InventoryService]: Getting movements for resource {resource_id} by user {user_id}")

        resource = resource_repository.get_by_id(db, resource_id)
        if resource is None:
            print(f"ERROR [InventoryService]: Resource {resource_id} not found")
            raise ValueError("Resource not found")

        self._check_restaurant_access(db, user_id, resource.restaurant_id)

        return inventory_movement_repository.get_by_resource(db, resource_id, date_from, date_to)

    def get_movements_by_restaurant(
        self,
        db: Session,
        user_id: UUID,
        restaurant_id: UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        reason: Optional[str] = None,
    ) -> list[InventoryMovement]:
        """
        Get all movements for a restaurant with optional filters.

        Args:
            db: Database session
            user_id: User UUID
            restaurant_id: Restaurant UUID
            date_from: Optional start date filter
            date_to: Optional end date filter
            reason: Optional reason filter

        Returns:
            List of InventoryMovement objects

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        print(f"INFO [InventoryService]: Getting movements for restaurant {restaurant_id} by user {user_id}")

        self._check_restaurant_access(db, user_id, restaurant_id)

        return inventory_movement_repository.get_by_restaurant(db, restaurant_id, date_from, date_to, reason)


# Singleton instance
inventory_service = InventoryService()
