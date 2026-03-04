"""Event repository for database operations."""

from datetime import date, datetime
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
        related_resource_id: Optional[UUID] = None,
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
            related_resource_id: Related resource UUID for stock alerts

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
            related_resource_id=related_resource_id,
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

    def update_overdue(self, db: Session, restaurant_id: UUID, cutoff_time: datetime) -> int:
        """
        Bulk update pending events with date before cutoff to overdue status.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            cutoff_time: Events with date before this time are considered overdue

        Returns:
            Count of updated rows
        """
        print(f"INFO [EventRepository]: Flagging overdue events for restaurant {restaurant_id} (cutoff={cutoff_time})")
        count = (
            db.query(Event)
            .filter(
                Event.restaurant_id == restaurant_id,
                Event.status == "pending",
                Event.date < cutoff_time,
            )
            .update({"status": "overdue"}, synchronize_session="fetch")
        )
        db.commit()
        print(f"INFO [EventRepository]: Flagged {count} events as overdue")
        return count

    def delete_by_related_document(self, db: Session, document_id: UUID) -> int:
        """
        Delete all vencimiento events linked to a specific document.

        Args:
            db: Database session
            document_id: Document UUID

        Returns:
            Count of deleted events
        """
        print(f"INFO [EventRepository]: Deleting vencimiento events for document {document_id}")
        count = (
            db.query(Event)
            .filter(
                Event.related_document_id == document_id,
                Event.type == "vencimiento",
            )
            .delete(synchronize_session="fetch")
        )
        db.commit()
        print(f"INFO [EventRepository]: Deleted {count} vencimiento events for document {document_id}")
        return count

    def get_pending_alerts_by_resource(
        self, db: Session, restaurant_id: UUID, resource_id: UUID
    ) -> list[Event]:
        """
        Get pending alerta_stock events for a specific resource.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            resource_id: Resource UUID

        Returns:
            List of pending alerta_stock Event objects
        """
        print(f"INFO [EventRepository]: Getting pending stock alerts for resource {resource_id}")
        events = (
            db.query(Event)
            .filter(
                Event.restaurant_id == restaurant_id,
                Event.type == "alerta_stock",
                Event.status == "pending",
                Event.related_resource_id == resource_id,
            )
            .all()
        )
        print(f"INFO [EventRepository]: Found {len(events)} pending stock alerts for resource {resource_id}")
        return events

    def resolve_alerts_by_resource(
        self, db: Session, restaurant_id: UUID, resource_id: UUID
    ) -> int:
        """
        Resolve all pending alerta_stock events for a resource.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            resource_id: Resource UUID

        Returns:
            Count of resolved events
        """
        print(f"INFO [EventRepository]: Resolving stock alerts for resource {resource_id}")
        count = (
            db.query(Event)
            .filter(
                Event.restaurant_id == restaurant_id,
                Event.type == "alerta_stock",
                Event.status == "pending",
                Event.related_resource_id == resource_id,
            )
            .update(
                {"status": "completed", "completed_at": datetime.utcnow()},
                synchronize_session="fetch",
            )
        )
        db.commit()
        print(f"INFO [EventRepository]: Resolved {count} stock alerts for resource {resource_id}")
        return count

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


    def get_tasks_by_date(self, db: Session, restaurant_id: UUID, target_date: date) -> list[Event]:
        """
        Get task events for a specific date.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            target_date: Target date

        Returns:
            List of task Event objects
        """
        print(f"INFO [EventRepository]: Getting tasks for restaurant {restaurant_id} on {target_date}")
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        events = (
            db.query(Event)
            .filter(
                Event.restaurant_id == restaurant_id,
                Event.type == "tarea",
                Event.date >= start_of_day,
                Event.date <= end_of_day,
            )
            .all()
        )
        print(f"INFO [EventRepository]: Found {len(events)} tasks for {target_date}")
        return events

    def get_pending_alerts(self, db: Session, restaurant_id: UUID) -> list[Event]:
        """
        Get pending alert events (vencimiento, alerta_stock, alerta_rentabilidad).

        Args:
            db: Database session
            restaurant_id: Restaurant UUID

        Returns:
            List of pending alert Event objects
        """
        print(f"INFO [EventRepository]: Getting pending alerts for restaurant {restaurant_id}")
        events = (
            db.query(Event)
            .filter(
                Event.restaurant_id == restaurant_id,
                Event.type.in_(["vencimiento", "alerta_stock", "alerta_rentabilidad"]),
                Event.status == "pending",
            )
            .all()
        )
        print(f"INFO [EventRepository]: Found {len(events)} pending alerts")
        return events

    def count_completed_tasks(self, db: Session, restaurant_id: UUID, target_date: date) -> int:
        """
        Count tasks completed on a specific date.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            target_date: Target date

        Returns:
            Count of completed tasks
        """
        print(f"INFO [EventRepository]: Counting completed tasks for restaurant {restaurant_id} on {target_date}")
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        count = (
            db.query(Event)
            .filter(
                Event.restaurant_id == restaurant_id,
                Event.type == "tarea",
                Event.status == "completed",
                Event.completed_at >= start_of_day,
                Event.completed_at <= end_of_day,
            )
            .count()
        )
        print(f"INFO [EventRepository]: Found {count} completed tasks")
        return count


# Singleton instance
event_repository = EventRepository()
