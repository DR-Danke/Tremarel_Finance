"""Event service for business logic operations."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from src.interface.event_dto import EventCreateDTO, EventStatusUpdateDTO, EventUpdateDTO
from src.models.event import Event
from src.repository.event_repository import event_repository
from src.repository.restaurant_repository import restaurant_repository


class EventService:
    """Service for event business logic with restaurant-scoped authorization."""

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
            print(f"ERROR [EventService]: User {user_id} doesn't have access to restaurant {restaurant_id}")
            raise PermissionError("User doesn't have access to this restaurant")

    def create_event(
        self,
        db: Session,
        user_id: UUID,
        data: EventCreateDTO,
    ) -> Event:
        """
        Create a new event in a restaurant.

        If frequency != 'none', auto-generates recurring instances.

        Args:
            db: Database session
            user_id: ID of the user creating the event
            data: Event creation data

        Returns:
            Created Event object

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        print(f"INFO [EventService]: Creating event type '{data.type.value}' in restaurant {data.restaurant_id} by user {user_id}")

        self._check_restaurant_access(db, user_id, data.restaurant_id)

        event = event_repository.create(
            db=db,
            restaurant_id=data.restaurant_id,
            event_type=data.type.value,
            description=data.description,
            event_date=data.date,
            frequency=data.frequency.value,
            responsible_id=data.responsible_id,
            notification_channel=data.notification_channel,
            related_document_id=data.related_document_id,
        )

        if data.frequency.value != "none":
            print(f"INFO [EventService]: Generating recurring instances for event {event.id} (frequency={data.frequency.value})")
            self.generate_recurring_instances(db, event.id)

        print(f"INFO [EventService]: Event type '{event.type}' created with id {event.id}")
        return event

    def get_events(
        self,
        db: Session,
        user_id: UUID,
        restaurant_id: UUID,
        type_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        responsible_id_filter: Optional[UUID] = None,
    ) -> list[Event]:
        """
        Get all events in a restaurant.

        Args:
            db: Database session
            user_id: User UUID
            restaurant_id: Restaurant UUID
            type_filter: Optional event type to filter by
            status_filter: Optional event status to filter by
            date_from: Optional start date filter
            date_to: Optional end date filter
            responsible_id_filter: Optional responsible person filter

        Returns:
            List of Event objects

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        print(f"INFO [EventService]: Getting events for restaurant {restaurant_id} by user {user_id}")

        self._check_restaurant_access(db, user_id, restaurant_id)

        return event_repository.get_by_restaurant(
            db, restaurant_id, type_filter, status_filter, date_from, date_to, responsible_id_filter
        )

    def get_event(
        self,
        db: Session,
        user_id: UUID,
        event_id: UUID,
    ) -> Event:
        """
        Get an event by ID if user has access to the event's restaurant.

        Args:
            db: Database session
            user_id: User UUID
            event_id: Event UUID

        Returns:
            Event object

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If event not found
        """
        print(f"INFO [EventService]: Getting event {event_id} for user {user_id}")

        event = event_repository.get_by_id(db, event_id)
        if event is None:
            print(f"ERROR [EventService]: Event {event_id} not found")
            raise ValueError("Event not found")

        self._check_restaurant_access(db, user_id, event.restaurant_id)

        return event

    def update_event(
        self,
        db: Session,
        user_id: UUID,
        event_id: UUID,
        data: EventUpdateDTO,
    ) -> Event:
        """
        Update an event if user has access to the event's restaurant.

        Args:
            db: Database session
            user_id: User UUID
            event_id: Event UUID
            data: Event update data

        Returns:
            Updated Event object

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If event not found
        """
        print(f"INFO [EventService]: Updating event {event_id} by user {user_id}")

        event = event_repository.get_by_id(db, event_id)
        if event is None:
            print(f"ERROR [EventService]: Event {event_id} not found")
            raise ValueError("Event not found")

        self._check_restaurant_access(db, user_id, event.restaurant_id)

        if data.type is not None:
            event.type = data.type.value
        if data.description is not None:
            event.description = data.description
        if data.date is not None:
            event.date = data.date
        if data.frequency is not None:
            event.frequency = data.frequency.value
        if data.responsible_id is not None:
            event.responsible_id = data.responsible_id
        if data.notification_channel is not None:
            event.notification_channel = data.notification_channel
        if data.related_document_id is not None:
            event.related_document_id = data.related_document_id

        updated_event = event_repository.update(db, event)

        print(f"INFO [EventService]: Event {event_id} updated successfully")
        return updated_event

    def update_event_status(
        self,
        db: Session,
        user_id: UUID,
        event_id: UUID,
        data: EventStatusUpdateDTO,
    ) -> Event:
        """
        Update only the status field of an event.

        Args:
            db: Database session
            user_id: User UUID
            event_id: Event UUID
            data: Event status update data

        Returns:
            Updated Event object

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If event not found
        """
        print(f"INFO [EventService]: Updating status of event {event_id} to '{data.status.value}' by user {user_id}")

        event = event_repository.get_by_id(db, event_id)
        if event is None:
            print(f"ERROR [EventService]: Event {event_id} not found")
            raise ValueError("Event not found")

        self._check_restaurant_access(db, user_id, event.restaurant_id)

        event.status = data.status.value
        updated_event = event_repository.update(db, event)

        print(f"INFO [EventService]: Event {event_id} status updated to '{data.status.value}'")
        return updated_event

    def delete_event(
        self,
        db: Session,
        user_id: UUID,
        event_id: UUID,
    ) -> bool:
        """
        Delete an event if user has access to the event's restaurant.

        Args:
            db: Database session
            user_id: User UUID
            event_id: Event UUID

        Returns:
            True if deleted

        Raises:
            PermissionError: If user doesn't have access to the restaurant
            ValueError: If event not found
        """
        print(f"INFO [EventService]: Deleting event {event_id} by user {user_id}")

        event = event_repository.get_by_id(db, event_id)
        if event is None:
            print(f"ERROR [EventService]: Event {event_id} not found")
            raise ValueError("Event not found")

        self._check_restaurant_access(db, user_id, event.restaurant_id)

        deleted = event_repository.delete(db, event_id)
        if not deleted:
            print(f"ERROR [EventService]: Event {event_id} not found for deletion")
            raise ValueError("Event not found")

        print(f"INFO [EventService]: Event {event_id} deleted successfully")
        return True

    def generate_recurring_instances(
        self,
        db: Session,
        event_id: UUID,
        days_ahead: int = 7,
    ) -> list[Event]:
        """
        Generate recurring event instances for an upcoming period.

        Each instance gets parent_event_id pointing to the recurring event,
        frequency='none', and the computed next date based on parent's frequency.

        Args:
            db: Database session
            event_id: Parent event UUID
            days_ahead: Number of days ahead to generate instances for

        Returns:
            List of created child Event instances
        """
        print(f"INFO [EventService]: Generating recurring instances for event {event_id} (days_ahead={days_ahead})")

        parent = event_repository.get_by_id(db, event_id)
        if parent is None:
            print(f"WARNING [EventService]: Parent event {event_id} not found for recurring generation")
            return []

        frequency = parent.frequency
        if frequency == "none":
            print(f"INFO [EventService]: Event {event_id} has no recurrence, skipping generation")
            return []

        base_date = parent.date
        end_date = datetime.utcnow() + timedelta(days=days_ahead)
        instances_data = []
        current_date = base_date

        while True:
            if frequency == "daily":
                current_date = current_date + timedelta(days=1)
            elif frequency == "weekly":
                current_date = current_date + timedelta(weeks=1)
            elif frequency == "monthly":
                current_date = current_date + relativedelta(months=1)
            elif frequency == "yearly":
                current_date = current_date + relativedelta(years=1)
            else:
                break

            if current_date > end_date:
                break

            instances_data.append({
                "restaurant_id": parent.restaurant_id,
                "type": parent.type,
                "description": parent.description,
                "date": current_date,
                "frequency": "none",
                "responsible_id": parent.responsible_id,
                "notification_channel": parent.notification_channel,
                "status": "pending",
                "related_document_id": parent.related_document_id,
                "parent_event_id": parent.id,
            })

        if instances_data:
            events = event_repository.bulk_create(db, instances_data)
            print(f"INFO [EventService]: Generated {len(events)} recurring instances for event {event_id}")
            return events

        print(f"INFO [EventService]: No recurring instances needed for event {event_id}")
        return []

    def get_due_events(
        self,
        db: Session,
        user_id: UUID,
        restaurant_id: UUID,
        target_date,
    ) -> list[Event]:
        """
        Get events due on a specific date for a restaurant.

        Args:
            db: Database session
            user_id: User UUID
            restaurant_id: Restaurant UUID
            target_date: Target date to check

        Returns:
            List of due Event objects

        Raises:
            PermissionError: If user doesn't have access to the restaurant
        """
        print(f"INFO [EventService]: Getting due events for restaurant {restaurant_id} on {target_date} by user {user_id}")

        self._check_restaurant_access(db, user_id, restaurant_id)

        return event_repository.get_due_events(db, restaurant_id, target_date)


# Singleton instance
event_service = EventService()
