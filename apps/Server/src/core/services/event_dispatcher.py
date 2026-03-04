"""General event notification dispatcher service.

Processes ALL due events and dispatches notifications through the appropriate
channel (WhatsApp, Email, Push). Handles all event types with type-specific message
templates and a generic fallback for unknown types.
"""

from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.adapter.email_templates import (
    format_expiration_alert_html,
    format_general_event_html,
    format_low_stock_alert_html,
    format_profitability_alert_html,
)
from src.core.services.event_service import event_service
from src.core.services.notification_scheduler import (
    _determine_channel,
    _send_via_channel,
    format_document_expiry_message,
    format_general_event_message,
    format_low_stock_alert_message,
    format_profitability_alert_message,
)
from src.interface.event_dto import EventStatusUpdateDTO
from src.repository.document_repository import document_repository
from src.repository.person_repository import person_repository
from src.repository.resource_repository import resource_repository


class EventNotificationDispatcher:
    """General-purpose dispatcher that processes due events and sends notifications."""

    def _build_whatsapp_message(self, event: object, db: Session) -> str:
        """
        Build a plain-text WhatsApp message based on the event type.

        Args:
            event: Event object
            db: Database session for enrichment lookups

        Returns:
            Formatted plain-text message string
        """
        event_type = event.type
        description = getattr(event, "description", "") or ""

        if event_type == "vencimiento":
            doc = None
            if event.related_document_id:
                doc = document_repository.get_by_id(db, event.related_document_id)
            if doc and doc.expiration_date:
                days_remaining = (doc.expiration_date - date.today()).days
                return format_document_expiry_message(
                    doc.type, str(doc.expiration_date), days_remaining
                )
            return format_general_event_message(event_type, description)

        if event_type == "alerta_stock":
            resource = None
            if event.related_resource_id:
                resource = resource_repository.get_by_id(db, event.related_resource_id)
            if resource:
                return format_low_stock_alert_message(
                    resource.name,
                    float(resource.current_stock),
                    float(resource.minimum_stock),
                )
            return format_general_event_message(event_type, description)

        if event_type == "alerta_rentabilidad":
            return format_profitability_alert_message(description)

        return format_general_event_message(event_type, description)

    def _build_email_message(self, event: object, db: Session) -> str:
        """
        Build an HTML email message based on the event type.

        Args:
            event: Event object
            db: Database session for enrichment lookups

        Returns:
            Formatted HTML message string
        """
        event_type = event.type
        description = getattr(event, "description", "") or ""

        if event_type == "vencimiento":
            doc = None
            if event.related_document_id:
                doc = document_repository.get_by_id(db, event.related_document_id)
            if doc and doc.expiration_date:
                days_remaining = (doc.expiration_date - date.today()).days
                return format_expiration_alert_html(
                    doc.type, str(doc.expiration_date), days_remaining
                )
            return format_general_event_html(event_type, description)

        if event_type == "alerta_stock":
            resource = None
            if event.related_resource_id:
                resource = resource_repository.get_by_id(db, event.related_resource_id)
            if resource:
                return format_low_stock_alert_html(
                    resource.name,
                    float(resource.current_stock),
                    float(resource.minimum_stock),
                )
            return format_general_event_html(event_type, description)

        if event_type == "alerta_rentabilidad":
            return format_profitability_alert_html(description)

        return format_general_event_html(event_type, description)

    def _resolve_recipient(
        self, event: object, db: Session, user_id: UUID
    ) -> tuple:
        """
        Resolve the notification recipient for an event.

        Falls back to the restaurant owner if no responsible_id is set.

        Args:
            event: Event object
            db: Database session
            user_id: User UUID for authorization

        Returns:
            Tuple of (person_object_or_None, reason_string)
        """
        if event.responsible_id:
            person = person_repository.get_by_id(db, event.responsible_id)
            if person:
                return (person, "responsible")
            print(f"WARNING [EventDispatcher]: Responsible person {event.responsible_id} not found for event {event.id}")

        owner = person_repository.find_owner(db, event.restaurant_id)
        if owner:
            print(f"INFO [EventDispatcher]: Falling back to restaurant owner for event {event.id}")
            return (owner, "owner_fallback")

        return (None, "no_recipient")

    async def process_due_events(
        self,
        db: Session,
        user_id: UUID,
        restaurant_id: UUID,
        target_date: Optional[date] = None,
    ) -> dict:
        """
        Process all due events for a restaurant and dispatch notifications.

        Queries pending events with date <= target_date, builds appropriate
        messages, resolves recipients, and dispatches via the correct channel.

        Args:
            db: Database session
            user_id: User UUID for authorization
            restaurant_id: Restaurant UUID
            target_date: Date to check for due events (defaults to today)

        Returns:
            Dictionary with processed, sent, skipped, failed counts
        """
        if target_date is None:
            target_date = date.today()

        print(f"INFO [EventDispatcher]: Processing due events for restaurant {restaurant_id} on {target_date}")

        due_events = event_service.get_due_events(db, user_id, restaurant_id, target_date)

        pending_events = [
            e for e in due_events
            if e.status == "pending" and e.type != "tarea"
        ]

        print(f"INFO [EventDispatcher]: Found {len(pending_events)} pending non-tarea events (from {len(due_events)} total due)")

        results = []
        sent_count = 0
        skipped_count = 0
        failed_count = 0

        for event in pending_events:
            notification_channel = getattr(event, "notification_channel", None)
            if not notification_channel:
                print(f"INFO [EventDispatcher]: Skipping event {event.id} - no notification channel")
                skipped_count += 1
                continue

            person, reason = self._resolve_recipient(event, db, user_id)
            if person is None:
                print(f"WARNING [EventDispatcher]: Skipping event {event.id} - {reason}")
                skipped_count += 1
                continue

            channel = _determine_channel(person)
            has_push_token = bool(getattr(person, "push_token", None) and getattr(person, "push_token", "").strip())

            # Skip if person has no contact info and no push token
            if channel == "none" and not has_push_token:
                print(f"INFO [EventDispatcher]: Skipping event {event.id} - person has no contact info")
                skipped_count += 1
                continue

            # If notification_channel is "push" but person has no push_token, skip
            if notification_channel == "push" and not has_push_token:
                print(f"INFO [EventDispatcher]: Skipping event {event.id} - person has no push_token")
                skipped_count += 1
                continue

            person_id = person.id
            person_name = getattr(person, "name", "")
            event_sent = False

            try:
                if notification_channel == "push":
                    # Push-only channel: send via push
                    push_token = getattr(person, "push_token", "")
                    push_message = self._build_whatsapp_message(event, db)
                    sent = await _send_via_channel(
                        "push", push_token, push_message, db, restaurant_id,
                        person_id, person_name, results, event_id=event.id,
                    )
                    if sent:
                        event_sent = True
                else:
                    # Email/WhatsApp channels
                    if channel in ("whatsapp", "both"):
                        whatsapp_number = getattr(person, "whatsapp", "")
                        wa_message = self._build_whatsapp_message(event, db)
                        sent = await _send_via_channel(
                            "whatsapp", whatsapp_number, wa_message, db, restaurant_id,
                            person_id, person_name, results, event_id=event.id,
                        )
                        if sent:
                            event_sent = True

                    if channel in ("email", "both"):
                        email_address = getattr(person, "email", "")
                        html_message = self._build_email_message(event, db)
                        sent = await _send_via_channel(
                            "email", email_address, html_message, db, restaurant_id,
                            person_id, person_name, results, event_id=event.id,
                        )
                        if sent:
                            event_sent = True

                if event_sent:
                    sent_count += 1
                    try:
                        event_service.update_event_status(
                            db, user_id, event.id,
                            EventStatusUpdateDTO(status="completed"),
                        )
                        print(f"INFO [EventDispatcher]: Event {event.id} marked as completed")
                    except ValueError as e:
                        print(f"WARNING [EventDispatcher]: Could not update event {event.id} status: {str(e)}")
                else:
                    failed_count += 1
            except Exception as e:
                print(f"ERROR [EventDispatcher]: Failed to process event {event.id}: {str(e)}")
                failed_count += 1

        processed = len(pending_events)
        print(f"INFO [EventDispatcher]: Dispatch complete for restaurant {restaurant_id}: processed={processed}, sent={sent_count}, skipped={skipped_count}, failed={failed_count}")

        return {
            "processed": processed,
            "sent": sent_count,
            "skipped": skipped_count,
            "failed": failed_count,
        }


# Singleton instance
event_dispatcher = EventNotificationDispatcher()
