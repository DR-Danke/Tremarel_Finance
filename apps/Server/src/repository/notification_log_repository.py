"""NotificationLog repository for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.notification_log import NotificationLog


class NotificationLogRepository:
    """Repository for NotificationLog database operations."""

    def create(
        self,
        db: Session,
        restaurant_id: UUID,
        channel: str,
        recipient: str,
        message: Optional[str],
        status: str,
        error_message: Optional[str] = None,
        event_id: Optional[UUID] = None,
    ) -> NotificationLog:
        """
        Create a new notification log entry.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            channel: Notification channel (e.g., whatsapp, email)
            recipient: Recipient identifier (phone number or email)
            message: Message body
            status: Send status (sent, failed, pending)
            error_message: Error details on failure
            event_id: Related event UUID for traceability

        Returns:
            Created NotificationLog object
        """
        print(f"INFO [NotificationLogRepository]: Creating notification log entry (channel={channel}, recipient={recipient}, status={status})")
        log_entry = NotificationLog(
            restaurant_id=restaurant_id,
            channel=channel,
            recipient=recipient,
            message=message,
            status=status,
            error_message=error_message,
            event_id=event_id,
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        print(f"INFO [NotificationLogRepository]: Notification log entry created with id {log_entry.id}")
        return log_entry

    def get_by_restaurant(
        self,
        db: Session,
        restaurant_id: UUID,
        channel_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[NotificationLog]:
        """
        Get notification logs for a restaurant with optional filters and pagination.

        Args:
            db: Database session
            restaurant_id: Restaurant UUID
            channel_filter: Optional channel to filter by
            status_filter: Optional status to filter by
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of NotificationLog objects
        """
        print(f"INFO [NotificationLogRepository]: Getting notification logs for restaurant {restaurant_id} (channel={channel_filter}, status={status_filter}, limit={limit}, offset={offset})")
        query = db.query(NotificationLog).filter(NotificationLog.restaurant_id == restaurant_id)
        if channel_filter:
            query = query.filter(NotificationLog.channel == channel_filter)
        if status_filter:
            query = query.filter(NotificationLog.status == status_filter)
        query = query.order_by(NotificationLog.created_at.desc())
        logs = query.offset(offset).limit(limit).all()
        print(f"INFO [NotificationLogRepository]: Found {len(logs)} notification log entries")
        return logs

    def get_by_id(self, db: Session, log_id: UUID) -> Optional[NotificationLog]:
        """
        Find a notification log entry by ID.

        Args:
            db: Database session
            log_id: NotificationLog UUID

        Returns:
            NotificationLog object if found, None otherwise
        """
        print(f"INFO [NotificationLogRepository]: Looking up notification log by id {log_id}")
        log_entry = db.query(NotificationLog).filter(NotificationLog.id == log_id).first()
        if log_entry:
            print(f"INFO [NotificationLogRepository]: Found notification log entry (channel={log_entry.channel})")
        else:
            print(f"INFO [NotificationLogRepository]: No notification log found with id {log_id}")
        return log_entry


# Singleton instance
notification_log_repository = NotificationLogRepository()
