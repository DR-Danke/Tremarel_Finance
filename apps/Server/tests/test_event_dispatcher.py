"""Tests for the EventNotificationDispatcher and new message formatters."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.adapter.email_templates import (
    format_general_event_html,
    format_profitability_alert_html,
)
from src.core.services.notification_scheduler import (
    format_general_event_message,
    format_profitability_alert_message,
)


# ============================================================================
# Profitability Alert Formatter Tests
# ============================================================================


def test_format_profitability_alert_message() -> None:
    """Test profitability alert WhatsApp message formatting."""
    message = format_profitability_alert_message("Margen bajo en platos principales")

    assert "Alerta de Rentabilidad" in message
    assert "Margen bajo en platos principales" in message
    assert "indicadores financieros" in message
    print("INFO [TestEventDispatcher]: test_format_profitability_alert_message - PASSED")


def test_format_profitability_alert_html() -> None:
    """Test profitability alert HTML email template."""
    html = format_profitability_alert_html("Margen bajo en platos principales")

    assert "Alerta de Rentabilidad" in html
    assert "Margen bajo en platos principales" in html
    assert "indicadores financieros" in html
    assert "<div" in html
    print("INFO [TestEventDispatcher]: test_format_profitability_alert_html - PASSED")


# ============================================================================
# General Event Formatter Tests
# ============================================================================


def test_format_general_event_message() -> None:
    """Test generic event WhatsApp message formatting."""
    message = format_general_event_message("checklist", "Revision de higiene semanal")

    assert "Notificacion de Evento" in message
    assert "checklist" in message
    assert "Revision de higiene semanal" in message
    print("INFO [TestEventDispatcher]: test_format_general_event_message - PASSED")


def test_format_general_event_html() -> None:
    """Test generic event HTML email template."""
    html = format_general_event_html("checklist", "Revision de higiene semanal")

    assert "Notificacion de Evento" in html
    assert "checklist" in html
    assert "Revision de higiene semanal" in html
    assert "<div" in html
    print("INFO [TestEventDispatcher]: test_format_general_event_html - PASSED")


# ============================================================================
# EventNotificationDispatcher Tests
# ============================================================================


def _make_mock_event(
    event_type: str = "alerta_stock",
    status: str = "pending",
    notification_channel: str = "whatsapp",
    responsible_id=None,
    related_document_id=None,
    related_resource_id=None,
    description: str = "Test event",
):
    """Helper to create a mock event."""
    event = MagicMock()
    event.id = uuid4()
    event.type = event_type
    event.status = status
    event.notification_channel = notification_channel
    event.responsible_id = responsible_id or uuid4()
    event.restaurant_id = uuid4()
    event.related_document_id = related_document_id
    event.related_resource_id = related_resource_id
    event.description = description
    event.date = MagicMock()
    return event


def _make_mock_person(name="Ana Lopez", whatsapp="+573001234567", email=None):
    """Helper to create a mock person."""
    person = MagicMock()
    person.id = uuid4()
    person.name = name
    person.whatsapp = whatsapp
    person.email = email
    person.type = "employee"
    return person


@pytest.mark.asyncio
async def test_process_due_events_sends_notifications() -> None:
    """Test that process_due_events sends notifications for pending events."""
    from src.core.services.event_dispatcher import EventNotificationDispatcher

    dispatcher = EventNotificationDispatcher()
    user_id = uuid4()
    restaurant_id = uuid4()

    mock_event = _make_mock_event(
        event_type="alerta_stock",
        related_resource_id=uuid4(),
    )
    mock_event.restaurant_id = restaurant_id

    mock_person = _make_mock_person()
    mock_resource = MagicMock()
    mock_resource.name = "Arroz"
    mock_resource.current_stock = 2.5
    mock_resource.minimum_stock = 10.0

    with patch("src.core.services.event_dispatcher.event_service") as mock_event_svc, \
         patch("src.core.services.event_dispatcher.person_repository") as mock_person_repo, \
         patch("src.core.services.event_dispatcher.resource_repository") as mock_resource_repo, \
         patch("src.core.services.event_dispatcher._send_via_channel", new_callable=AsyncMock) as mock_send, \
         patch("src.core.services.event_dispatcher._determine_channel") as mock_determine:

        mock_event_svc.get_due_events.return_value = [mock_event]
        mock_person_repo.get_by_id.return_value = mock_person
        mock_resource_repo.get_by_id.return_value = mock_resource
        mock_determine.return_value = "whatsapp"
        mock_send.return_value = True
        mock_event_svc.update_event_status.return_value = MagicMock()

        result = await dispatcher.process_due_events(MagicMock(), user_id, restaurant_id)

    assert result["processed"] == 1
    assert result["sent"] == 1
    assert result["skipped"] == 0
    assert result["failed"] == 0
    mock_send.assert_called_once()
    mock_event_svc.update_event_status.assert_called_once()
    print("INFO [TestEventDispatcher]: test_process_due_events_sends_notifications - PASSED")


@pytest.mark.asyncio
async def test_process_due_events_skips_tarea() -> None:
    """Test that tarea events are skipped by the general dispatcher."""
    from src.core.services.event_dispatcher import EventNotificationDispatcher

    dispatcher = EventNotificationDispatcher()
    user_id = uuid4()
    restaurant_id = uuid4()

    mock_event = _make_mock_event(event_type="tarea")

    with patch("src.core.services.event_dispatcher.event_service") as mock_event_svc, \
         patch("src.core.services.event_dispatcher._send_via_channel", new_callable=AsyncMock) as mock_send:

        mock_event_svc.get_due_events.return_value = [mock_event]

        result = await dispatcher.process_due_events(MagicMock(), user_id, restaurant_id)

    assert result["processed"] == 0
    assert result["sent"] == 0
    mock_send.assert_not_called()
    print("INFO [TestEventDispatcher]: test_process_due_events_skips_tarea - PASSED")


@pytest.mark.asyncio
async def test_process_due_events_skips_no_channel() -> None:
    """Test that events without notification_channel are skipped."""
    from src.core.services.event_dispatcher import EventNotificationDispatcher

    dispatcher = EventNotificationDispatcher()
    user_id = uuid4()
    restaurant_id = uuid4()

    mock_event = _make_mock_event(notification_channel="")

    with patch("src.core.services.event_dispatcher.event_service") as mock_event_svc, \
         patch("src.core.services.event_dispatcher._send_via_channel", new_callable=AsyncMock) as mock_send:

        mock_event_svc.get_due_events.return_value = [mock_event]

        result = await dispatcher.process_due_events(MagicMock(), user_id, restaurant_id)

    assert result["skipped"] == 1
    mock_send.assert_not_called()
    print("INFO [TestEventDispatcher]: test_process_due_events_skips_no_channel - PASSED")


@pytest.mark.asyncio
async def test_process_due_events_no_recipient_fallback_to_owner() -> None:
    """Test that events without responsible_id fall back to restaurant owner."""
    from src.core.services.event_dispatcher import EventNotificationDispatcher

    dispatcher = EventNotificationDispatcher()
    user_id = uuid4()
    restaurant_id = uuid4()

    mock_event = _make_mock_event(event_type="alerta_rentabilidad")
    mock_event.responsible_id = None
    mock_event.restaurant_id = restaurant_id

    mock_owner = _make_mock_person(name="Owner", whatsapp="+573009999999")

    mock_db = MagicMock()

    with patch("src.core.services.event_dispatcher.event_service") as mock_event_svc, \
         patch("src.core.services.event_dispatcher.person_repository") as mock_person_repo, \
         patch("src.core.services.event_dispatcher._send_via_channel", new_callable=AsyncMock) as mock_send, \
         patch("src.core.services.event_dispatcher._determine_channel") as mock_determine:

        mock_event_svc.get_due_events.return_value = [mock_event]
        mock_person_repo.get_by_id.return_value = None
        mock_person_repo.find_owner.return_value = mock_owner
        mock_determine.return_value = "whatsapp"
        mock_send.return_value = True
        mock_event_svc.update_event_status.return_value = MagicMock()

        result = await dispatcher.process_due_events(mock_db, user_id, restaurant_id)

    assert result["sent"] == 1
    mock_person_repo.find_owner.assert_called_once_with(mock_db, restaurant_id)
    print("INFO [TestEventDispatcher]: test_process_due_events_no_recipient_fallback_to_owner - PASSED")


@pytest.mark.asyncio
async def test_process_due_events_no_recipient_no_owner() -> None:
    """Test that events with no responsible and no owner are skipped."""
    from src.core.services.event_dispatcher import EventNotificationDispatcher

    dispatcher = EventNotificationDispatcher()
    user_id = uuid4()
    restaurant_id = uuid4()

    mock_event = _make_mock_event()
    mock_event.responsible_id = None
    mock_event.restaurant_id = restaurant_id

    with patch("src.core.services.event_dispatcher.event_service") as mock_event_svc, \
         patch("src.core.services.event_dispatcher.person_repository") as mock_person_repo, \
         patch("src.core.services.event_dispatcher._send_via_channel", new_callable=AsyncMock) as mock_send:

        mock_event_svc.get_due_events.return_value = [mock_event]
        mock_person_repo.get_by_id.return_value = None
        mock_person_repo.find_owner.return_value = None

        result = await dispatcher.process_due_events(MagicMock(), user_id, restaurant_id)

    assert result["skipped"] == 1
    assert result["sent"] == 0
    mock_send.assert_not_called()
    print("INFO [TestEventDispatcher]: test_process_due_events_no_recipient_no_owner - PASSED")


@pytest.mark.asyncio
async def test_process_due_events_failed_notification() -> None:
    """Test that failed notifications are logged but don't block remaining events."""
    from src.core.services.event_dispatcher import EventNotificationDispatcher

    dispatcher = EventNotificationDispatcher()
    user_id = uuid4()
    restaurant_id = uuid4()

    mock_event1 = _make_mock_event(event_type="alerta_rentabilidad", description="Alert 1")
    mock_event1.restaurant_id = restaurant_id
    mock_event2 = _make_mock_event(event_type="alerta_rentabilidad", description="Alert 2")
    mock_event2.restaurant_id = restaurant_id

    mock_person = _make_mock_person()

    with patch("src.core.services.event_dispatcher.event_service") as mock_event_svc, \
         patch("src.core.services.event_dispatcher.person_repository") as mock_person_repo, \
         patch("src.core.services.event_dispatcher._send_via_channel", new_callable=AsyncMock) as mock_send, \
         patch("src.core.services.event_dispatcher._determine_channel") as mock_determine:

        mock_event_svc.get_due_events.return_value = [mock_event1, mock_event2]
        mock_person_repo.get_by_id.return_value = mock_person
        mock_determine.return_value = "whatsapp"
        # First event fails, second succeeds
        mock_send.side_effect = [False, True]
        mock_event_svc.update_event_status.return_value = MagicMock()

        result = await dispatcher.process_due_events(MagicMock(), user_id, restaurant_id)

    assert result["processed"] == 2
    assert result["sent"] == 1
    assert result["failed"] == 1
    assert mock_send.call_count == 2
    print("INFO [TestEventDispatcher]: test_process_due_events_failed_notification - PASSED")


@pytest.mark.asyncio
async def test_process_due_events_empty() -> None:
    """Test that no due events returns zeros."""
    from src.core.services.event_dispatcher import EventNotificationDispatcher

    dispatcher = EventNotificationDispatcher()
    user_id = uuid4()
    restaurant_id = uuid4()

    with patch("src.core.services.event_dispatcher.event_service") as mock_event_svc:
        mock_event_svc.get_due_events.return_value = []

        result = await dispatcher.process_due_events(MagicMock(), user_id, restaurant_id)

    assert result["processed"] == 0
    assert result["sent"] == 0
    assert result["skipped"] == 0
    assert result["failed"] == 0
    print("INFO [TestEventDispatcher]: test_process_due_events_empty - PASSED")


# ============================================================================
# Message Builder Tests
# ============================================================================


def test_build_message_vencimiento() -> None:
    """Test document expiry message built correctly with document enrichment."""
    from src.core.services.event_dispatcher import EventNotificationDispatcher

    dispatcher = EventNotificationDispatcher()
    mock_db = MagicMock()

    mock_event = _make_mock_event(
        event_type="vencimiento",
        related_document_id=uuid4(),
    )

    mock_doc = MagicMock()
    mock_doc.type = "Licencia sanitaria"
    mock_doc.expiration_date = date(2026, 4, 15)

    with patch("src.core.services.event_dispatcher.document_repository") as mock_doc_repo:
        mock_doc_repo.get_by_id.return_value = mock_doc

        message = dispatcher._build_whatsapp_message(mock_event, mock_db)

    assert "Licencia sanitaria" in message
    assert "2026-04-15" in message
    print("INFO [TestEventDispatcher]: test_build_message_vencimiento - PASSED")


def test_build_message_alerta_stock() -> None:
    """Test stock alert message built correctly with resource enrichment."""
    from src.core.services.event_dispatcher import EventNotificationDispatcher

    dispatcher = EventNotificationDispatcher()
    mock_db = MagicMock()

    mock_event = _make_mock_event(
        event_type="alerta_stock",
        related_resource_id=uuid4(),
    )

    mock_resource = MagicMock()
    mock_resource.name = "Arroz"
    mock_resource.current_stock = 2.5
    mock_resource.minimum_stock = 10.0

    with patch("src.core.services.event_dispatcher.resource_repository") as mock_res_repo:
        mock_res_repo.get_by_id.return_value = mock_resource

        message = dispatcher._build_whatsapp_message(mock_event, mock_db)

    assert "Arroz" in message
    assert "2.5" in message
    assert "10.0" in message
    print("INFO [TestEventDispatcher]: test_build_message_alerta_stock - PASSED")


def test_build_message_alerta_rentabilidad() -> None:
    """Test profitability alert message."""
    from src.core.services.event_dispatcher import EventNotificationDispatcher

    dispatcher = EventNotificationDispatcher()
    mock_db = MagicMock()

    mock_event = _make_mock_event(
        event_type="alerta_rentabilidad",
        description="Margen bajo en platos principales",
    )

    message = dispatcher._build_whatsapp_message(mock_event, mock_db)

    assert "Alerta de Rentabilidad" in message
    assert "Margen bajo en platos principales" in message
    print("INFO [TestEventDispatcher]: test_build_message_alerta_rentabilidad - PASSED")


def test_build_message_unknown_type() -> None:
    """Test generic fallback message for unknown event types."""
    from src.core.services.event_dispatcher import EventNotificationDispatcher

    dispatcher = EventNotificationDispatcher()
    mock_db = MagicMock()

    mock_event = _make_mock_event(
        event_type="custom_event",
        description="Some custom event happened",
    )

    message = dispatcher._build_whatsapp_message(mock_event, mock_db)

    assert "Notificacion de Evento" in message
    assert "custom_event" in message
    assert "Some custom event happened" in message
    print("INFO [TestEventDispatcher]: test_build_message_unknown_type - PASSED")


def test_build_email_vencimiento() -> None:
    """Test document expiry HTML message built correctly."""
    from src.core.services.event_dispatcher import EventNotificationDispatcher

    dispatcher = EventNotificationDispatcher()
    mock_db = MagicMock()

    mock_event = _make_mock_event(
        event_type="vencimiento",
        related_document_id=uuid4(),
    )

    mock_doc = MagicMock()
    mock_doc.type = "Permiso bomberos"
    mock_doc.expiration_date = date(2026, 3, 10)

    with patch("src.core.services.event_dispatcher.document_repository") as mock_doc_repo:
        mock_doc_repo.get_by_id.return_value = mock_doc

        html = dispatcher._build_email_message(mock_event, mock_db)

    assert "Permiso bomberos" in html
    assert "<div" in html
    print("INFO [TestEventDispatcher]: test_build_email_vencimiento - PASSED")


def test_build_message_vencimiento_no_document_fallback() -> None:
    """Test that vencimiento with no document falls back to generic message."""
    from src.core.services.event_dispatcher import EventNotificationDispatcher

    dispatcher = EventNotificationDispatcher()
    mock_db = MagicMock()

    mock_event = _make_mock_event(
        event_type="vencimiento",
        related_document_id=uuid4(),
        description="Documento por vencer",
    )

    with patch("src.core.services.event_dispatcher.document_repository") as mock_doc_repo:
        mock_doc_repo.get_by_id.return_value = None

        message = dispatcher._build_whatsapp_message(mock_event, mock_db)

    assert "Notificacion de Evento" in message
    assert "Documento por vencer" in message
    print("INFO [TestEventDispatcher]: test_build_message_vencimiento_no_document_fallback - PASSED")


def test_build_message_alerta_stock_no_resource_fallback() -> None:
    """Test that alerta_stock with deleted resource falls back to generic message."""
    from src.core.services.event_dispatcher import EventNotificationDispatcher

    dispatcher = EventNotificationDispatcher()
    mock_db = MagicMock()

    mock_event = _make_mock_event(
        event_type="alerta_stock",
        related_resource_id=uuid4(),
        description="Stock bajo de ingrediente",
    )

    with patch("src.core.services.event_dispatcher.resource_repository") as mock_res_repo:
        mock_res_repo.get_by_id.return_value = None

        message = dispatcher._build_whatsapp_message(mock_event, mock_db)

    assert "Notificacion de Evento" in message
    assert "Stock bajo de ingrediente" in message
    print("INFO [TestEventDispatcher]: test_build_message_alerta_stock_no_resource_fallback - PASSED")
