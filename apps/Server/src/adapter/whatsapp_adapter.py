"""WhatsApp notification adapter (stub implementation)."""

import re

from src.core.services.notification_service import NotificationAdapter

# WhatsApp message length limit
WHATSAPP_MAX_MESSAGE_LENGTH = 4096


class WhatsAppAdapter(NotificationAdapter):
    """
    WhatsApp notification adapter.

    Stub implementation that validates inputs and logs sends.
    Ready for provider integration (Twilio, Meta Cloud API).
    """

    def __init__(self, api_key: str = "", phone_number_id: str = "") -> None:
        """
        Initialize WhatsAppAdapter.

        Args:
            api_key: WhatsApp Business API key (empty for stub mode)
            phone_number_id: WhatsApp Business phone number ID (empty for stub mode)
        """
        self.api_key = api_key
        self.phone_number_id = phone_number_id
        print(f"INFO [WhatsAppAdapter]: Initialized (stub_mode={not bool(api_key)})")

    async def send(self, recipient: str, message: str) -> dict:
        """
        Send a WhatsApp message to a recipient.

        Validates recipient format (international, starts with "+") and message
        length (max 4096 chars). Truncates message if it exceeds the limit.

        Args:
            recipient: Phone number in international format (e.g., "+573001234567")
            message: Message body to send

        Returns:
            Dictionary with status and recipient

        Raises:
            ValueError: If recipient format is invalid
        """
        print(f"INFO [WhatsAppAdapter]: Sending message to {recipient}")

        # Validate recipient format: must start with "+" followed by digits
        if not recipient or not re.match(r"^\+\d+$", recipient):
            print(f"ERROR [WhatsAppAdapter]: Invalid recipient format: {recipient}")
            raise ValueError(f"Invalid WhatsApp recipient format: '{recipient}'. Must start with '+' followed by digits.")

        # Truncate message if it exceeds WhatsApp limit
        if len(message) > WHATSAPP_MAX_MESSAGE_LENGTH:
            print(f"INFO [WhatsAppAdapter]: Message truncated from {len(message)} to {WHATSAPP_MAX_MESSAGE_LENGTH} chars")
            message = message[:WHATSAPP_MAX_MESSAGE_LENGTH - 3] + "..."

        # TODO: Replace stub with actual WhatsApp Business API call.
        # Example with Twilio:
        #   from twilio.rest import Client
        #   client = Client(account_sid, auth_token)
        #   message = client.messages.create(
        #       from_=f"whatsapp:{self.phone_number_id}",
        #       body=message,
        #       to=f"whatsapp:{recipient}"
        #   )
        # Example with Meta Cloud API:
        #   import httpx
        #   async with httpx.AsyncClient() as client:
        #       response = await client.post(
        #           f"https://graph.facebook.com/v17.0/{self.phone_number_id}/messages",
        #           headers={"Authorization": f"Bearer {self.api_key}"},
        #           json={"messaging_product": "whatsapp", "to": recipient, "type": "text", "text": {"body": message}}
        #       )

        print(f"INFO [WhatsAppAdapter]: Message sent successfully to {recipient} (stub mode)")
        return {
            "status": "sent",
            "recipient": recipient,
        }


# Singleton instance
whatsapp_adapter = WhatsAppAdapter()
