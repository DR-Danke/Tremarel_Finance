"""Notification service with abstract adapter interface and dispatch orchestration."""

from abc import ABC, abstractmethod
from typing import Dict


class NotificationAdapter(ABC):
    """Abstract base class for notification channel adapters."""

    @abstractmethod
    async def send(self, recipient: str, message: str) -> dict:
        """
        Send a notification to a recipient.

        Args:
            recipient: Recipient identifier (phone number, email, etc.)
            message: Message body to send

        Returns:
            Dictionary with send result (status, recipient, error_message if failed)
        """
        pass


class NotificationService:
    """
    Service for dispatching notifications through channel adapters.

    Orchestrates sending by looking up the appropriate adapter for the
    requested channel and dispatching the message with a single retry on failure.
    """

    def __init__(self, adapters: Dict[str, NotificationAdapter]) -> None:
        """
        Initialize NotificationService with channel adapters.

        Args:
            adapters: Dictionary mapping channel names to adapter instances
        """
        self.adapters = adapters
        print(f"INFO [NotificationService]: Initialized with channels: {list(adapters.keys())}")

    async def send_notification(self, channel: str, recipient: str, message: str) -> dict:
        """
        Send a notification through the specified channel.

        Looks up the adapter for the channel, attempts to send, and retries
        once on failure.

        Args:
            channel: Notification channel name (e.g., "whatsapp", "email")
            recipient: Recipient identifier
            message: Message body

        Returns:
            Dictionary with status, recipient, and optional error_message
        """
        print(f"INFO [NotificationService]: Sending notification via '{channel}' to {recipient}")

        adapter = self.adapters.get(channel)
        if adapter is None:
            print(f"ERROR [NotificationService]: No adapter registered for channel '{channel}'")
            return {
                "status": "failed",
                "recipient": recipient,
                "error_message": f"No adapter registered for channel '{channel}'",
            }

        # First attempt
        try:
            result = await adapter.send(recipient, message)
            print(f"INFO [NotificationService]: Notification sent successfully to {recipient} via '{channel}'")
            return result
        except Exception as e:
            print(f"ERROR [NotificationService]: First attempt failed for {recipient} via '{channel}': {str(e)}")

        # Retry once
        try:
            print(f"INFO [NotificationService]: Retrying notification to {recipient} via '{channel}'")
            result = await adapter.send(recipient, message)
            print(f"INFO [NotificationService]: Retry successful for {recipient} via '{channel}'")
            return result
        except Exception as e:
            print(f"ERROR [NotificationService]: Retry failed for {recipient} via '{channel}': {str(e)}")
            return {
                "status": "failed",
                "recipient": recipient,
                "error_message": str(e),
            }
