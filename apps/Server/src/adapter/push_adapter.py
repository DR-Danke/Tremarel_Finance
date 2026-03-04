"""Push notification adapter (stub implementation with FCM support)."""

import httpx

from src.config.settings import get_settings
from src.core.services.notification_service import NotificationAdapter

# FCM notification body max length
PUSH_MAX_BODY_LENGTH = 200


class PushNotificationAdapter(NotificationAdapter):
    """
    Push notification adapter using Firebase Cloud Messaging.

    Stub implementation that validates inputs and logs sends when FCM_SERVER_KEY
    is empty. Sends real push notifications via FCM legacy HTTP API when configured.
    """

    def __init__(self, fcm_server_key: str = "") -> None:
        """
        Initialize PushNotificationAdapter.

        Args:
            fcm_server_key: Firebase Cloud Messaging server key (empty for stub mode)
        """
        self.fcm_server_key = fcm_server_key
        self.stub_mode = not bool(fcm_server_key)
        self.fcm_url = "https://fcm.googleapis.com/fcm/send"
        print(f"INFO [PushAdapter]: Initialized (stub_mode={self.stub_mode})")

    async def send(self, recipient: str, message: str) -> dict:
        """
        Send a push notification to a device token.

        Validates recipient is non-empty. In stub mode, logs the send without
        calling FCM. In live mode, sends via FCM legacy HTTP API.

        Args:
            recipient: FCM device token
            message: Notification body text

        Returns:
            Dictionary with status and recipient

        Raises:
            ValueError: If recipient is empty or None
        """
        print(f"INFO [PushAdapter]: Sending push notification to {recipient[:20] if recipient else 'None'}...")

        if not recipient or not recipient.strip():
            print(f"ERROR [PushAdapter]: Invalid recipient: empty or None")
            raise ValueError("Invalid push notification recipient: token is empty or None.")

        # Truncate message for notification body
        notification_body = message[:PUSH_MAX_BODY_LENGTH] if len(message) > PUSH_MAX_BODY_LENGTH else message

        if self.stub_mode:
            print(f"INFO [PushAdapter]: Push notification sent successfully to {recipient[:20]}... (stub mode)")
            return {"status": "sent", "recipient": recipient[:20]}

        try:
            payload = {
                "to": recipient,
                "notification": {
                    "title": "Restaurant OS",
                    "body": notification_body,
                },
                "data": {
                    "full_message": message,
                },
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.fcm_url,
                    headers={
                        "Authorization": f"key={self.fcm_server_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=10.0,
                )

            if response.status_code == 200:
                result = response.json()
                if result.get("success", 0) > 0:
                    print(f"INFO [PushAdapter]: Push notification sent successfully to {recipient[:20]}... (fcm mode)")
                    return {"status": "sent", "recipient": recipient[:20]}
                else:
                    error_msg = str(result.get("results", [{}])[0].get("error", "Unknown FCM error"))
                    print(f"ERROR [PushAdapter]: FCM reported failure: {error_msg}")
                    raise Exception(f"FCM send failed: {error_msg}")
            else:
                print(f"ERROR [PushAdapter]: FCM HTTP error: {response.status_code}")
                raise Exception(f"FCM HTTP error: {response.status_code}")

        except httpx.HTTPError as e:
            print(f"ERROR [PushAdapter]: HTTP request failed: {str(e)}")
            raise


# Singleton instance using application settings
_settings = get_settings()
push_adapter = PushNotificationAdapter(fcm_server_key=_settings.FCM_SERVER_KEY)
