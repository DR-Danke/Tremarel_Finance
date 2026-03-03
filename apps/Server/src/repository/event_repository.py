"""Event repository for database operations."""

from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.event import Event


class EventRepository:
    """Repository for Event database operations."""

    def create(
        self,
        db: Session,
        restaurant_id: UUID,
        event_type: str,
        description: Optional[str],
        event_date: datetime,
        frequency: str = "none",
        responsible_id: Optional[UUID] = None,
        notification_channel: str = "email",
        related_document_id: Optional[UUID] = None,
        parent_event_id: Optional[UUID] = None,
    ) -> Event:
        """
        Create a new event in a restaurant.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            event_type: Event type (e.g., tarea, vencimiento, pago)
            description: Event description
            event_date: Event date and time
            frequency: Recurrence frequency (none, daily, weekly, monthly, yearly)
            responsible_id: Person UUID responsible for this event
            notification_channel: Notification channel preference
            related_document_id: Related document UUID
            parent_event_id: Parent event UUID for recurring instances

        Returns:
            Created Event object
        """
        print(f"INFO [EventRepository]: Creating event type '{event_type}' for restaurant {restaurant_id}")
        event = Event(
            restaurant_id=restaurant_id,
            type=event_type,
            description=description,
            date=event_date,
            frequency=frequency,
            responsible_id=responsible_id,
            notification_channel=notification_channel,
            related_document_id=related_document_id,
            parent_event_id=parent_event_id,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        print(f"INFO [EventRepository]: Event created with id {event.id}")
        return event

    def get_by_id(self, db: Session, event_id: UUID) -> Optional[Event]:
        """
        Find an event by ID.

        Args:
            db: Database session
            event_id: Event UUID

        Returns:
            Event object if found, None otherwise
        """
        print(f"INFO [EventRepository]: Looking up event by id {event_id}")
        event = db.query(Event).filter(Event.id == event_id).first()
        if event:
            print(f"INFO [EventRepository]: Found event type '{event.type}'")
        else:
            print(f"INFO [EventRepository]: No event found with id {event_id}")
        return event

    def get_by_restaurant(
        self,
        db: Session,
        restaurant_id: UUID,
        type_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        responsible_id_filter: Optional[UUID] = None,
    ) -> list[Event]:
        """
        Get all events in a restaurant, with optional filters.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            type_filter: Optional event type to filter by
            status_filter: Optional event status to filter by
            date_from: Optional start date filter
            date_to: Optional end date filter
            responsible_id_filter: Optional responsible person filter

        Returns:
            List of Event objects
        """
        print(f"INFO [EventRepository]: Getting events for restaurant {restaurant_id} (type={type_filter}, status={status_filter})")
        query = db.query(Event).filter(Event.restaurant_id == restaurant_id)
        if type_filter:
            query = query.filter(Event.type == type_filter)
        if status_filter:
            query = query.filter(Event.status == status_filter)
        if date_from:
            query = query.filter(Event.date >= date_from)
        if date_to:
            query = query.filter(Event.date <= date_to)
        if responsible_id_filter:
            query = query.filter(Event.responsible_id == responsible_id_filter)
        events = query.all()
        print(f"INFO [EventRepository]: Found {len(events)} events for restaurant {restaurant_id}")
        return events

    def update(self, db: Session, event: Event) -> Event:
        """
        Update an existing event.

        Args:
            db: Database session
            event: Event object with updated values

        Returns:
            Updated Event object
        """
        print(f"INFO [EventRepository]: Updating event {event.id}")
        db.add(event)
        db.commit()
        db.refresh(event)
        print(f"INFO [EventRepository]: Event {event.id} updated successfully")
        return event

    def delete(self, db: Session, event_id: UUID) -> bool:
        """
        Delete an event from the database.

        Args:
            db: Database session
            event_id: Event UUID

        Returns:
            True if deleted, False if not found
        """
        print(f"INFO [EventRepository]: Deleting event {event_id}")
        event = db.query(Event).filter(Event.id == event_id).first()
        if event:
            db.delete(event)
            db.commit()
            print(f"INFO [EventRepository]: Event {event_id} deleted successfully")
            return True
        print(f"INFO [EventRepository]: Event {event_id} not found for deletion")
        return False

    def get_due_events(
        self,
        db: Session,
        restaurant_id: UUID,
        target_date: date,
    ) -> list[Event]:
        """
        Get events due on a specific date for a restaurant.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            target_date: Target date to check for due events

        Returns:
            List of Event objects due on the target date
        """
        print(f"INFO [EventRepository]: Getting due events for restaurant {restaurant_id} on {target_date}")
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        events = (
            db.query(Event)
            .filter(
                Event.restaurant_id == restaurant_id,
                Event.date >= start_of_day,
                Event.date <= end_of_day,
            )
            .all()
        )
        print(f"INFO [EventRepository]: Found {len(events)} due events")
        return events

    def bulk_create(self, db: Session, events_data: list[dict]) -> list[Event]:
        """
        Bulk insert events for recurring instance generation.

        Args:
            db: Database session
            events_data: List of dictionaries with event field values

        Returns:
            List of created Event objects
        """
        print(f"INFO [EventRepository]: Bulk creating {len(events_data)} events")
        events = []
        for data in events_data:
            event = Event(**data)
            db.add(event)
            events.append(event)
        db.commit()
        for event in events:
            db.refresh(event)
        print(f"INFO [EventRepository]: Bulk created {len(events)} events successfully")
        return events


# Singleton instance
event_repository = EventRepository()
