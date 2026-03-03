"""Tests for notification service, WhatsApp adapter, and message formatters."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

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
