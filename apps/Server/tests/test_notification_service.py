"""Tests for notification service, adapters, email templates, and message formatters."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.adapter.email_adapter import EmailAdapter
from src.adapter.email_templates import (
    format_daily_tasks_html,
    format_expiration_alert_html,
    format_low_stock_alert_html,
)
from src.adapter.whatsapp_adapter import WhatsAppAdapter
from src.core.services.notification_scheduler import (
    format_daily_tasks_message,
    format_document_expiry_message,
    format_low_stock_alert_message,
)
from src.core.services.notification_service import NotificationAdapter, NotificationService


# ============================================================================
# NotificationService Tests
# ============================================================================


@pytest.mark.asyncio
async def test_send_notification_success() -> None:
    """Test successful notification send via adapter."""
    mock_adapter = AsyncMock(spec=NotificationAdapter)
    mock_adapter.send.return_value = {"status": "sent", "recipient": "+573001234567"}

    service = NotificationService(adapters={"whatsapp": mock_adapter})
    result = await service.send_notification("whatsapp", "+573001234567", "Hello")

    assert result["status"] == "sent"
    assert result["recipient"] == "+573001234567"
    mock_adapter.send.assert_called_once_with("+573001234567", "Hello")
    print("INFO [TestNotificationService]: test_send_notification_success - PASSED")


@pytest.mark.asyncio
async def test_send_notification_unknown_channel() -> None:
    """Test notification send with unknown channel returns failed."""
    service = NotificationService(adapters={})
    result = await service.send_notification("sms", "+573001234567", "Hello")

    assert result["status"] == "failed"
    assert "No adapter registered" in result["error_message"]
    print("INFO [TestNotificationService]: test_send_notification_unknown_channel - PASSED")


@pytest.mark.asyncio
async def test_send_notification_retry_on_failure() -> None:
    """Test that notification service retries once on adapter failure."""
    mock_adapter = AsyncMock(spec=NotificationAdapter)
    mock_adapter.send.side_effect = [
        Exception("Network error"),
        {"status": "sent", "recipient": "+573001234567"},
    ]

    service = NotificationService(adapters={"whatsapp": mock_adapter})
    result = await service.send_notification("whatsapp", "+573001234567", "Hello")

    assert result["status"] == "sent"
    assert mock_adapter.send.call_count == 2
    print("INFO [TestNotificationService]: test_send_notification_retry_on_failure - PASSED")


@pytest.mark.asyncio
async def test_send_notification_retry_also_fails() -> None:
    """Test that notification returns failed when retry also fails."""
    mock_adapter = AsyncMock(spec=NotificationAdapter)
    mock_adapter.send.side_effect = Exception("Persistent error")

    service = NotificationService(adapters={"whatsapp": mock_adapter})
    result = await service.send_notification("whatsapp", "+573001234567", "Hello")

    assert result["status"] == "failed"
    assert "Persistent error" in result["error_message"]
    assert mock_adapter.send.call_count == 2
    print("INFO [TestNotificationService]: test_send_notification_retry_also_fails - PASSED")


# ============================================================================
# WhatsAppAdapter Tests
# ============================================================================


@pytest.mark.asyncio
async def test_whatsapp_adapter_valid_recipient() -> None:
    """Test WhatsApp adapter send with valid international number."""
    adapter = WhatsAppAdapter()
    result = await adapter.send("+573001234567", "Hola mundo")

    assert result["status"] == "sent"
    assert result["recipient"] == "+573001234567"
    print("INFO [TestNotificationService]: test_whatsapp_adapter_valid_recipient - PASSED")


@pytest.mark.asyncio
async def test_whatsapp_adapter_invalid_recipient_no_plus() -> None:
    """Test WhatsApp adapter rejects recipient without + prefix."""
    adapter = WhatsAppAdapter()

    with pytest.raises(ValueError, match="Invalid WhatsApp recipient format"):
        await adapter.send("573001234567", "Hello")
    print("INFO [TestNotificationService]: test_whatsapp_adapter_invalid_recipient_no_plus - PASSED")


@pytest.mark.asyncio
async def test_whatsapp_adapter_invalid_recipient_empty() -> None:
    """Test WhatsApp adapter rejects empty recipient."""
    adapter = WhatsAppAdapter()

    with pytest.raises(ValueError, match="Invalid WhatsApp recipient format"):
        await adapter.send("", "Hello")
    print("INFO [TestNotificationService]: test_whatsapp_adapter_invalid_recipient_empty - PASSED")


@pytest.mark.asyncio
async def test_whatsapp_adapter_message_truncation() -> None:
    """Test WhatsApp adapter truncates messages exceeding 4096 chars."""
    adapter = WhatsAppAdapter()
    long_message = "A" * 5000
    result = await adapter.send("+573001234567", long_message)

    assert result["status"] == "sent"
    # Message should have been truncated internally
    print("INFO [TestNotificationService]: test_whatsapp_adapter_message_truncation - PASSED")


# ============================================================================
# Message Formatter Tests
# ============================================================================


def test_format_daily_tasks_message_normal() -> None:
    """Test daily tasks message formatting with normal tasks."""
    summary = {
        "person_name": "Maria Garcia",
        "date": date(2026, 3, 3),
        "total_tasks": 2,
        "overdue_count": 0,
        "tasks": [
            {"description": "Limpiar cocina", "time": "08:00", "status": "pending", "is_overdue": False},
            {"description": "Inventario", "time": "14:00", "status": "pending", "is_overdue": False},
        ],
    }

    message = format_daily_tasks_message(summary)

    assert "Maria Garcia" in message
    assert "2026-03-03" in message
    assert "2 tarea(s)" in message
    assert "Limpiar cocina" in message
    assert "Inventario" in message
    assert "(08:00)" in message
    assert "(14:00)" in message
    assert "VENCIDA" not in message
    print("INFO [TestNotificationService]: test_format_daily_tasks_message_normal - PASSED")


def test_format_daily_tasks_message_empty_tasks() -> None:
    """Test daily tasks message formatting with no tasks."""
    summary = {
        "person_name": "Juan",
        "date": date(2026, 3, 3),
        "total_tasks": 0,
        "overdue_count": 0,
        "tasks": [],
    }

    message = format_daily_tasks_message(summary)

    assert "Juan" in message
    assert "No tienes tareas pendientes" in message
    print("INFO [TestNotificationService]: test_format_daily_tasks_message_empty_tasks - PASSED")


def test_format_daily_tasks_message_overdue() -> None:
    """Test daily tasks message formatting with overdue tasks."""
    summary = {
        "person_name": "Carlos",
        "date": date(2026, 3, 3),
        "total_tasks": 1,
        "overdue_count": 1,
        "tasks": [
            {"description": "Pagar factura", "time": "09:00", "status": "overdue", "is_overdue": True},
        ],
    }

    message = format_daily_tasks_message(summary)

    assert "Carlos" in message
    assert "1 tarea(s) vencida(s)" in message
    assert "VENCIDA" in message
    assert "Pagar factura" in message
    print("INFO [TestNotificationService]: test_format_daily_tasks_message_overdue - PASSED")


def test_format_low_stock_alert_message() -> None:
    """Test low stock alert message formatting."""
    message = format_low_stock_alert_message("Arroz", 2.5, 10.0)

    assert "Alerta de Stock Bajo" in message
    assert "Arroz" in message
    assert "2.5" in message
    assert "10.0" in message
    print("INFO [TestNotificationService]: test_format_low_stock_alert_message - PASSED")


def test_format_document_expiry_message_normal() -> None:
    """Test document expiry message formatting with days remaining > 7."""
    message = format_document_expiry_message("Licencia sanitaria", "2026-04-15", 43)

    assert "Atencion" in message
    assert "Licencia sanitaria" in message
    assert "2026-04-15" in message
    assert "43 dia(s)" in message
    print("INFO [TestNotificationService]: test_format_document_expiry_message_normal - PASSED")


def test_format_document_expiry_message_urgent() -> None:
    """Test document expiry message formatting with days remaining <= 7."""
    message = format_document_expiry_message("Permiso bomberos", "2026-03-10", 5)

    assert "URGENTE" in message
    assert "Permiso bomberos" in message
    assert "5 dia(s)" in message
    print("INFO [TestNotificationService]: test_format_document_expiry_message_urgent - PASSED")


# ============================================================================
# NotificationScheduler Tests
# ============================================================================


@pytest.mark.asyncio
async def test_send_morning_task_summaries_success() -> None:
    """Test send_morning_task_summaries with employees that have WhatsApp numbers."""
    from src.core.services.notification_scheduler import send_morning_task_summaries

    user_id = uuid4()
    restaurant_id = uuid4()
    person_id = uuid4()

    mock_summary = {
        "person_id": person_id,
        "person_name": "Ana Lopez",
        "date": date.today(),
        "total_tasks": 1,
        "overdue_count": 0,
        "tasks": [{"description": "Revisar stock", "time": "10:00", "status": "pending", "is_overdue": False}],
    }

    mock_person = MagicMock()
    mock_person.whatsapp = "+573001234567"
    mock_person.email = None

    mock_db = MagicMock()

    with patch("src.core.services.notification_scheduler.event_service") as mock_event_svc, \
         patch("src.core.services.notification_scheduler.person_service") as mock_person_svc, \
         patch("src.core.services.notification_scheduler.notification_service") as mock_notif_svc, \
         patch("src.core.services.notification_scheduler.notification_log_repository") as mock_log_repo:

        mock_event_svc.get_all_daily_summaries.return_value = [mock_summary]
        mock_person_svc.get_person.return_value = mock_person
        mock_notif_svc.send_notification = AsyncMock(return_value={"status": "sent", "recipient": "+573001234567"})
        mock_log_repo.create.return_value = MagicMock()

        result = await send_morning_task_summaries(mock_db, user_id, restaurant_id)

    assert result["total_employees"] == 1
    assert result["sent_count"] == 1
    assert result["skipped_count"] == 0
    assert len(result["results"]) == 1
    assert result["results"][0]["status"] == "sent"
    mock_log_repo.create.assert_called_once()
    print("INFO [TestNotificationService]: test_send_morning_task_summaries_success - PASSED")


@pytest.mark.asyncio
async def test_send_morning_task_summaries_skip_no_whatsapp() -> None:
    """Test that employees without WhatsApp numbers are skipped."""
    from src.core.services.notification_scheduler import send_morning_task_summaries

    user_id = uuid4()
    restaurant_id = uuid4()
    person_id = uuid4()

    mock_summary = {
        "person_id": person_id,
        "person_name": "Pedro Sin Whatsapp",
        "date": date.today(),
        "total_tasks": 1,
        "overdue_count": 0,
        "tasks": [{"description": "Tarea", "time": "08:00", "status": "pending", "is_overdue": False}],
    }

    mock_person = MagicMock()
    mock_person.whatsapp = None
    mock_person.email = None

    mock_db = MagicMock()

    with patch("src.core.services.notification_scheduler.event_service") as mock_event_svc, \
         patch("src.core.services.notification_scheduler.person_service") as mock_person_svc, \
         patch("src.core.services.notification_scheduler.notification_service") as mock_notif_svc, \
         patch("src.core.services.notification_scheduler.notification_log_repository") as mock_log_repo:

        mock_event_svc.get_all_daily_summaries.return_value = [mock_summary]
        mock_person_svc.get_person.return_value = mock_person

        result = await send_morning_task_summaries(mock_db, user_id, restaurant_id)

    assert result["total_employees"] == 1
    assert result["sent_count"] == 0
    assert result["skipped_count"] == 1
    assert result["results"][0]["status"] == "skipped"
    mock_notif_svc.send_notification.assert_not_called()
    mock_log_repo.create.assert_not_called()
    print("INFO [TestNotificationService]: test_send_morning_task_summaries_skip_no_whatsapp - PASSED")


@pytest.mark.asyncio
async def test_send_morning_task_summaries_empty_restaurant() -> None:
    """Test send_morning_task_summaries with no employee summaries."""
    from src.core.services.notification_scheduler import send_morning_task_summaries

    user_id = uuid4()
    restaurant_id = uuid4()
    mock_db = MagicMock()

    with patch("src.core.services.notification_scheduler.event_service") as mock_event_svc:
        mock_event_svc.get_all_daily_summaries.return_value = []

        result = await send_morning_task_summaries(mock_db, user_id, restaurant_id)

    assert result["total_employees"] == 0
    assert result["sent_count"] == 0
    assert result["skipped_count"] == 0
    assert result["results"] == []
    print("INFO [TestNotificationService]: test_send_morning_task_summaries_empty_restaurant - PASSED")


@pytest.mark.asyncio
async def test_send_morning_task_summaries_skip_empty_whatsapp() -> None:
    """Test that employees with empty string WhatsApp are skipped."""
    from src.core.services.notification_scheduler import send_morning_task_summaries

    user_id = uuid4()
    restaurant_id = uuid4()
    person_id = uuid4()

    mock_summary = {
        "person_id": person_id,
        "person_name": "Empty WA",
        "date": date.today(),
        "total_tasks": 1,
        "overdue_count": 0,
        "tasks": [{"description": "Tarea", "time": "08:00", "status": "pending", "is_overdue": False}],
    }

    mock_person = MagicMock()
    mock_person.whatsapp = ""
    mock_person.email = ""

    mock_db = MagicMock()

    with patch("src.core.services.notification_scheduler.event_service") as mock_event_svc, \
         patch("src.core.services.notification_scheduler.person_service") as mock_person_svc, \
         patch("src.core.services.notification_scheduler.notification_service") as mock_notif_svc, \
         patch("src.core.services.notification_scheduler.notification_log_repository"):

        mock_event_svc.get_all_daily_summaries.return_value = [mock_summary]
        mock_person_svc.get_person.return_value = mock_person

        result = await send_morning_task_summaries(mock_db, user_id, restaurant_id)

    assert result["skipped_count"] == 1
    assert result["sent_count"] == 0
    mock_notif_svc.send_notification.assert_not_called()
    print("INFO [TestNotificationService]: test_send_morning_task_summaries_skip_empty_whatsapp - PASSED")


# ============================================================================
# EmailAdapter Tests
# ============================================================================


@pytest.mark.asyncio
async def test_email_adapter_valid_recipient() -> None:
    """Test EmailAdapter send with valid email address."""
    adapter = EmailAdapter()
    result = await adapter.send("test@example.com", "<p>Hello</p>")

    assert result["status"] == "sent"
    assert result["recipient"] == "test@example.com"
    print("INFO [TestNotificationService]: test_email_adapter_valid_recipient - PASSED")


@pytest.mark.asyncio
async def test_email_adapter_invalid_recipient_no_at() -> None:
    """Test EmailAdapter rejects recipient without @ symbol."""
    adapter = EmailAdapter()

    with pytest.raises(ValueError, match="Invalid email recipient format"):
        await adapter.send("invalid-email", "<p>Hello</p>")
    print("INFO [TestNotificationService]: test_email_adapter_invalid_recipient_no_at - PASSED")


@pytest.mark.asyncio
async def test_email_adapter_invalid_recipient_empty() -> None:
    """Test EmailAdapter rejects empty recipient."""
    adapter = EmailAdapter()

    with pytest.raises(ValueError, match="Invalid email recipient format"):
        await adapter.send("", "<p>Hello</p>")
    print("INFO [TestNotificationService]: test_email_adapter_invalid_recipient_empty - PASSED")


@pytest.mark.asyncio
async def test_email_adapter_stub_mode() -> None:
    """Test EmailAdapter works in stub mode when SMTP credentials are empty."""
    adapter = EmailAdapter(smtp_host="", smtp_port=587, username="", password="")
    assert adapter.stub_mode is True

    result = await adapter.send("user@example.com", "<p>Test</p>")
    assert result["status"] == "sent"
    print("INFO [TestNotificationService]: test_email_adapter_stub_mode - PASSED")


# ============================================================================
# HTML Email Template Tests
# ============================================================================


def test_format_daily_tasks_html_normal() -> None:
    """Test daily tasks HTML formatting with normal tasks."""
    summary = {
        "person_name": "Maria Garcia",
        "date": date(2026, 3, 3),
        "total_tasks": 2,
        "overdue_count": 0,
        "tasks": [
            {"description": "Limpiar cocina", "time": "08:00", "status": "pending", "is_overdue": False},
            {"description": "Inventario", "time": "14:00", "status": "pending", "is_overdue": False},
        ],
    }

    html = format_daily_tasks_html(summary)

    assert "Maria Garcia" in html
    assert "2026-03-03" in html
    assert "2 tarea(s)" in html
    assert "Limpiar cocina" in html
    assert "Inventario" in html
    assert "08:00" in html
    assert "14:00" in html
    assert "<table" in html
    assert "VENCIDA" not in html
    print("INFO [TestNotificationService]: test_format_daily_tasks_html_normal - PASSED")


def test_format_daily_tasks_html_empty_tasks() -> None:
    """Test daily tasks HTML formatting with no tasks."""
    summary = {
        "person_name": "Juan",
        "date": date(2026, 3, 3),
        "total_tasks": 0,
        "overdue_count": 0,
        "tasks": [],
    }

    html = format_daily_tasks_html(summary)

    assert "Juan" in html
    assert "No tienes tareas pendientes" in html
    print("INFO [TestNotificationService]: test_format_daily_tasks_html_empty_tasks - PASSED")


def test_format_daily_tasks_html_overdue() -> None:
    """Test daily tasks HTML formatting with overdue tasks."""
    summary = {
        "person_name": "Carlos",
        "date": date(2026, 3, 3),
        "total_tasks": 1,
        "overdue_count": 1,
        "tasks": [
            {"description": "Pagar factura", "time": "09:00", "status": "overdue", "is_overdue": True},
        ],
    }

    html = format_daily_tasks_html(summary)

    assert "Carlos" in html
    assert "1 tarea(s) vencida(s)" in html
    assert "VENCIDA" in html
    assert "Pagar factura" in html
    assert "ffebee" in html  # red background for overdue
    print("INFO [TestNotificationService]: test_format_daily_tasks_html_overdue - PASSED")


def test_format_expiration_alert_html_normal() -> None:
    """Test document expiration HTML with days > 7 (attention level)."""
    html = format_expiration_alert_html("Licencia sanitaria", "2026-04-15", 43)

    assert "Atencion" in html
    assert "Licencia sanitaria" in html
    assert "2026-04-15" in html
    assert "43 dia(s)" in html
    assert "URGENTE" not in html
    print("INFO [TestNotificationService]: test_format_expiration_alert_html_normal - PASSED")


def test_format_expiration_alert_html_urgent() -> None:
    """Test document expiration HTML with days <= 7 (urgent level)."""
    html = format_expiration_alert_html("Permiso bomberos", "2026-03-10", 5)

    assert "URGENTE" in html
    assert "Permiso bomberos" in html
    assert "5 dia(s)" in html
    assert "c62828" in html  # urgent red color
    print("INFO [TestNotificationService]: test_format_expiration_alert_html_urgent - PASSED")


def test_format_low_stock_alert_html() -> None:
    """Test low stock alert HTML formatting."""
    html = format_low_stock_alert_html("Arroz", 2.5, 10.0)

    assert "Alerta de Stock Bajo" in html
    assert "Arroz" in html
    assert "2.5" in html
    assert "10.0" in html
    assert "<table" in html
    print("INFO [TestNotificationService]: test_format_low_stock_alert_html - PASSED")


# ============================================================================
# Scheduler Channel Routing Tests
# ============================================================================


@pytest.mark.asyncio
async def test_send_morning_task_summaries_email_channel() -> None:
    """Test that person with email but no WhatsApp sends via email."""
    from src.core.services.notification_scheduler import send_morning_task_summaries

    user_id = uuid4()
    restaurant_id = uuid4()
    person_id = uuid4()

    mock_summary = {
        "person_id": person_id,
        "person_name": "Laura Email",
        "date": date.today(),
        "total_tasks": 1,
        "overdue_count": 0,
        "tasks": [{"description": "Revisar menu", "time": "09:00", "status": "pending", "is_overdue": False}],
    }

    mock_person = MagicMock()
    mock_person.email = "laura@example.com"
    mock_person.whatsapp = None

    mock_db = MagicMock()

    with patch("src.core.services.notification_scheduler.event_service") as mock_event_svc, \
         patch("src.core.services.notification_scheduler.person_service") as mock_person_svc, \
         patch("src.core.services.notification_scheduler.notification_service") as mock_notif_svc, \
         patch("src.core.services.notification_scheduler.notification_log_repository") as mock_log_repo:

        mock_event_svc.get_all_daily_summaries.return_value = [mock_summary]
        mock_person_svc.get_person.return_value = mock_person
        mock_notif_svc.send_notification = AsyncMock(return_value={"status": "sent", "recipient": "laura@example.com"})
        mock_log_repo.create.return_value = MagicMock()

        result = await send_morning_task_summaries(mock_db, user_id, restaurant_id)

    assert result["sent_count"] == 1
    assert result["skipped_count"] == 0
    mock_notif_svc.send_notification.assert_called_once()
    call_args = mock_notif_svc.send_notification.call_args
    assert call_args[0][0] == "email"
    assert call_args[0][1] == "laura@example.com"
    assert "<div" in call_args[0][2]  # HTML content
    mock_log_repo.create.assert_called_once()
    assert mock_log_repo.create.call_args[1]["channel"] == "email"
    print("INFO [TestNotificationService]: test_send_morning_task_summaries_email_channel - PASSED")


@pytest.mark.asyncio
async def test_send_morning_task_summaries_both_channels() -> None:
    """Test that person with both email and WhatsApp sends via both."""
    from src.core.services.notification_scheduler import send_morning_task_summaries

    user_id = uuid4()
    restaurant_id = uuid4()
    person_id = uuid4()

    mock_summary = {
        "person_id": person_id,
        "person_name": "Diego Both",
        "date": date.today(),
        "total_tasks": 1,
        "overdue_count": 0,
        "tasks": [{"description": "Abrir local", "time": "07:00", "status": "pending", "is_overdue": False}],
    }

    mock_person = MagicMock()
    mock_person.email = "diego@example.com"
    mock_person.whatsapp = "+573009876543"

    mock_db = MagicMock()

    with patch("src.core.services.notification_scheduler.event_service") as mock_event_svc, \
         patch("src.core.services.notification_scheduler.person_service") as mock_person_svc, \
         patch("src.core.services.notification_scheduler.notification_service") as mock_notif_svc, \
         patch("src.core.services.notification_scheduler.notification_log_repository") as mock_log_repo:

        mock_event_svc.get_all_daily_summaries.return_value = [mock_summary]
        mock_person_svc.get_person.return_value = mock_person
        mock_notif_svc.send_notification = AsyncMock(return_value={"status": "sent", "recipient": "test"})
        mock_log_repo.create.return_value = MagicMock()

        result = await send_morning_task_summaries(mock_db, user_id, restaurant_id)

    assert result["sent_count"] == 1
    assert result["skipped_count"] == 0
    assert mock_notif_svc.send_notification.call_count == 2
    assert mock_log_repo.create.call_count == 2

    # Verify both channels were called
    channels_called = [call[0][0] for call in mock_notif_svc.send_notification.call_args_list]
    assert "email" in channels_called
    assert "whatsapp" in channels_called
    print("INFO [TestNotificationService]: test_send_morning_task_summaries_both_channels - PASSED")


@pytest.mark.asyncio
async def test_send_morning_task_summaries_skip_no_contact() -> None:
    """Test that person with neither email nor WhatsApp is skipped."""
    from src.core.services.notification_scheduler import send_morning_task_summaries

    user_id = uuid4()
    restaurant_id = uuid4()
    person_id = uuid4()

    mock_summary = {
        "person_id": person_id,
        "person_name": "Sin Contacto",
        "date": date.today(),
        "total_tasks": 1,
        "overdue_count": 0,
        "tasks": [{"description": "Tarea", "time": "08:00", "status": "pending", "is_overdue": False}],
    }

    mock_person = MagicMock()
    mock_person.email = None
    mock_person.whatsapp = None

    mock_db = MagicMock()

    with patch("src.core.services.notification_scheduler.event_service") as mock_event_svc, \
         patch("src.core.services.notification_scheduler.person_service") as mock_person_svc, \
         patch("src.core.services.notification_scheduler.notification_service") as mock_notif_svc, \
         patch("src.core.services.notification_scheduler.notification_log_repository") as mock_log_repo:

        mock_event_svc.get_all_daily_summaries.return_value = [mock_summary]
        mock_person_svc.get_person.return_value = mock_person

        result = await send_morning_task_summaries(mock_db, user_id, restaurant_id)

    assert result["skipped_count"] == 1
    assert result["sent_count"] == 0
    assert result["results"][0]["error_message"] == "No email or WhatsApp number"
    mock_notif_svc.send_notification.assert_not_called()
    mock_log_repo.create.assert_not_called()
    print("INFO [TestNotificationService]: test_send_morning_task_summaries_skip_no_contact - PASSED")
