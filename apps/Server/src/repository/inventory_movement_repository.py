"""Inventory movement repository for database operations."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.inventory_movement import InventoryMovement


class InventoryMovementRepository:
    """Repository for InventoryMovement database operations."""

    def create(
        self,
        db: Session,
        resource_id: UUID,
        movement_type: str,
        quantity: Decimal,
        reason: str,
        date: Optional[datetime],
        person_id: Optional[UUID],
        restaurant_id: UUID,
        notes: Optional[str],
    ) -> InventoryMovement:
        """
        Create a new inventory movement record.

        Args:
            db: Database session
            resource_id: Resource UUID
            movement_type: Movement type (entry/exit)
            quantity: Quantity moved
            reason: Reason for the movement
            date: Movement date (defaults to now)
            person_id: Person UUID who performed the movement
            restaurant_id: Restaurant UUID
            notes: Additional notes

        Returns:
            Created InventoryMovement object
        """
        print(f"INFO [InventoryMovementRepository]: Creating {movement_type} movement for resource {resource_id}")
        movement = InventoryMovement(
            resource_id=resource_id,
            type=movement_type,
            quantity=quantity,
            reason=reason,
            date=date,
            person_id=person_id,
            restaurant_id=restaurant_id,
            notes=notes,
        )
        db.add(movement)
        db.commit()
        db.refresh(movement)
        print(f"INFO [InventoryMovementRepository]: Movement created with id {movement.id}")
        return movement

    def get_by_resource(
        self,
        db: Session,
        resource_id: UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list[InventoryMovement]:
        """
        Get all movements for a resource with optional date range filter.

        Args:
            db: Database session
            resource_id: Resource UUID
            date_from: Optional start date filter
            date_to: Optional end date filter

        Returns:
            List of InventoryMovement objects ordered by date descending
        """
        print(f"INFO [InventoryMovementRepository]: Getting movements for resource {resource_id} (date_from={date_from}, date_to={date_to})")
        query = db.query(InventoryMovement).filter(InventoryMovement.resource_id == resource_id)
        if date_from:
            query = query.filter(InventoryMovement.date >= date_from)
        if date_to:
            query = query.filter(InventoryMovement.date <= date_to)
        movements = query.order_by(InventoryMovement.date.desc()).all()
        print(f"INFO [InventoryMovementRepository]: Found {len(movements)} movements for resource {resource_id}")
        return movements

    def get_by_restaurant(
        self,
        db: Session,
        restaurant_id: UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        reason: Optional[str] = None,
    ) -> list[InventoryMovement]:
        """
        Get all movements for a restaurant with optional filters.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            date_from: Optional start date filter
            date_to: Optional end date filter
            reason: Optional reason filter

        Returns:
            List of InventoryMovement objects ordered by date descending
        """
        print(f"INFO [InventoryMovementRepository]: Getting movements for restaurant {restaurant_id} (date_from={date_from}, date_to={date_to}, reason={reason})")
        query = db.query(InventoryMovement).filter(InventoryMovement.restaurant_id == restaurant_id)
        if date_from:
            query = query.filter(InventoryMovement.date >= date_from)
        if date_to:
            query = query.filter(InventoryMovement.date <= date_to)
        if reason:
            query = query.filter(InventoryMovement.reason == reason)
        movements = query.order_by(InventoryMovement.date.desc()).all()
        print(f"INFO [InventoryMovementRepository]: Found {len(movements)} movements for restaurant {restaurant_id}")
        return movements


    def get_recent(self, db: Session, restaurant_id: UUID, limit: int = 10) -> list[InventoryMovement]:
        """
        Get the most recent movements for a restaurant.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            limit: Maximum number of movements to return

        Returns:
            List of InventoryMovement objects ordered by date descending
        """
        print(f"INFO [InventoryMovementRepository]: Getting recent {limit} movements for restaurant {restaurant_id}")
        movements = (
            db.query(InventoryMovement)
            .filter(InventoryMovement.restaurant_id == restaurant_id)
            .order_by(InventoryMovement.date.desc())
            .limit(limit)
            .all()
        )
        print(f"INFO [InventoryMovementRepository]: Found {len(movements)} recent movements")
        return movements


# Singleton instance
inventory_movement_repository = InventoryMovementRepository()
