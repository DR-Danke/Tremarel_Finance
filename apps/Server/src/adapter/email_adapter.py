"""Email notification adapter (stub implementation with SMTP support)."""

import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.config.settings import get_settings
from src.core.services.notification_service import NotificationAdapter

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


class EmailAdapter(NotificationAdapter):
    """
    Email notification adapter.

    Stub implementation that validates inputs and logs sends when SMTP
    credentials are empty. Sends real emails via SMTP when configured.
    """

    def __init__(
        self,
        smtp_host: str = "",
        smtp_port: int = 587,
        username: str = "",
        password: str = "",
        from_email: str = "noreply@restaurant-os.com",
    ) -> None:
        """
        Initialize EmailAdapter.

        Args:
            smtp_host: SMTP server hostname (empty for stub mode)
            smtp_port: SMTP server port
            username: SMTP authentication username
            password: SMTP authentication password
            from_email: Sender email address
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.stub_mode = not bool(smtp_host)
        print(f"INFO [EmailAdapter]: Initialized (stub_mode={self.stub_mode})")

    async def send(self, recipient: str, message: str) -> dict:
        """
        Send an email to a recipient.

        Validates recipient email format. In stub mode, logs the send
        without making an SMTP connection. In SMTP mode, sends via starttls.

        Args:
            recipient: Email address of the recipient
            message: HTML message body to send

        Returns:
            Dictionary with status and recipient

        Raises:
            ValueError: If recipient email format is invalid
        """
        print(f"INFO [EmailAdapter]: Sending email to {recipient}")

        if not recipient or not re.match(EMAIL_REGEX, recipient):
            print(f"ERROR [EmailAdapter]: Invalid email format: {recipient}")
            raise ValueError(
                f"Invalid email recipient format: '{recipient}'. Must be a valid email address."
            )

        if self.stub_mode:
            print(f"INFO [EmailAdapter]: Email sent to {recipient} (stub mode)")
            return {"status": "sent", "recipient": recipient}

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Restaurant OS - Notificacion"
            msg["From"] = self.from_email
            msg["To"] = recipient
            msg.attach(MIMEText(message, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.from_email, recipient, msg.as_string())

            print(f"INFO [EmailAdapter]: Email sent to {recipient} (smtp mode)")
            return {"status": "sent", "recipient": recipient}
        except Exception as e:
            print(f"ERROR [EmailAdapter]: Failed to send email to {recipient}: {e}")
            raise


# Singleton instance using application settings
_settings = get_settings()
email_adapter = EmailAdapter(
    smtp_host=_settings.SMTP_HOST,
    smtp_port=_settings.SMTP_PORT,
    username=_settings.SMTP_USERNAME,
    password=_settings.SMTP_PASSWORD,
    from_email=_settings.SMTP_FROM_EMAIL,
)
