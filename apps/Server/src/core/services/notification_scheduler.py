"""Notification scheduler for automated task summary and alert sending."""

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from src.adapter.email_adapter import email_adapter
from src.adapter.email_templates import format_daily_tasks_html
from src.adapter.whatsapp_adapter import whatsapp_adapter
from src.core.services.event_service import event_service
from src.core.services.notification_service import NotificationService
from src.core.services.person_service import person_service
from src.repository.notification_log_repository import notification_log_repository

# Create the notification service singleton here to avoid circular imports
# (notification_service.py defines the ABC, adapters implement it)
notification_service = NotificationService(
    adapters={
        "whatsapp": whatsapp_adapter,
        "email": email_adapter,
    }
)


def format_daily_tasks_message(summary: dict) -> str:
    """
    Format a daily task summary into a Spanish WhatsApp message.

    Args:
        summary: Dictionary with person_name, date, total_tasks, overdue_count, tasks list

    Returns:
        Formatted message string in Spanish (Colombian)
    """
    person_name = summary.get("person_name", "Empleado")
    summary_date = summary.get("date", date.today())
    total_tasks = summary.get("total_tasks", 0)
    overdue_count = summary.get("overdue_count", 0)
    tasks = summary.get("tasks", [])

    lines = []
    lines.append(f"Buenos dias, {person_name}! 🌅")
    lines.append(f"📋 *Resumen de tareas para {summary_date}*")
    lines.append("")

    if total_tasks == 0:
        lines.append("✅ No tienes tareas pendientes para hoy. Buen trabajo!")
    else:
        lines.append(f"Tienes *{total_tasks} tarea(s)* pendiente(s)")
        if overdue_count > 0:
            lines.append(f"⚠️ *{overdue_count} tarea(s) vencida(s)*")
        lines.append("")

        for i, task in enumerate(tasks, 1):
            description = task.get("description", "Sin descripcion")
            task_time = task.get("time", "")
            is_overdue = task.get("is_overdue", False)

            overdue_indicator = " ⚠️ *VENCIDA*" if is_overdue else ""
            time_str = f" ({task_time})" if task_time else ""
            lines.append(f"{i}. {description}{time_str}{overdue_indicator}")

    lines.append("")
    lines.append("Que tengas un excelente dia! 💪")

    return "\n".join(lines)


def format_low_stock_alert_message(resource_name: str, current_stock: float, min_stock: float) -> str:
    """
    Format a low-stock alert message in Spanish.

    Args:
        resource_name: Name of the resource/ingredient
        current_stock: Current stock level
        min_stock: Minimum stock threshold

    Returns:
        Formatted alert message string in Spanish
    """
    return (
        f"⚠️ *Alerta de Stock Bajo*\n"
        f"\n"
        f"El recurso *{resource_name}* esta por debajo del minimo:\n"
        f"📦 Stock actual: *{current_stock}*\n"
        f"📉 Stock minimo: *{min_stock}*\n"
        f"\n"
        f"Por favor, realiza el pedido correspondiente."
    )


def format_document_expiry_message(document_name: str, expiry_date: str, days_remaining: int) -> str:
    """
    Format a document expiration alert message in Spanish.

    Args:
        document_name: Name of the document
        expiry_date: Expiration date string
        days_remaining: Number of days until expiration

    Returns:
        Formatted alert message string in Spanish
    """
    urgency = "🔴 *URGENTE*" if days_remaining <= 7 else "🟡 *Atencion*"
    return (
        f"{urgency} - Documento por vencer\n"
        f"\n"
        f"El documento *{document_name}* vence el *{expiry_date}*.\n"
        f"⏰ Quedan *{days_remaining} dia(s)*.\n"
        f"\n"
        f"Por favor, gestiona la renovacion a tiempo."
    )


def _determine_channel(person: object) -> str:
    """
    Determine notification channel based on person's available contact info.

    Args:
        person: Person object with optional email and whatsapp fields

    Returns:
        "both", "email", "whatsapp", or "none"
    """
    has_email = bool(getattr(person, "email", None) and getattr(person, "email", "").strip())
    has_whatsapp = bool(getattr(person, "whatsapp", None) and getattr(person, "whatsapp", "").strip())

    if has_email and has_whatsapp:
        return "both"
    if has_email:
        return "email"
    if has_whatsapp:
        return "whatsapp"
    return "none"


async def _send_via_channel(
    channel: str,
    recipient: str,
    message: str,
    db: Session,
    restaurant_id: UUID,
    person_id: UUID,
    person_name: str,
    results: list,
) -> bool:
    """
    Send a notification via a specific channel and log the result.

    Args:
        channel: "email" or "whatsapp"
        recipient: Recipient address (email or phone)
        message: Formatted message body
        db: Database session
        restaurant_id: Restaurant UUID
        person_id: Person UUID
        person_name: Person display name
        results: Results list to append to

    Returns:
        True if sent successfully, False otherwise
    """
    print(f"INFO [NotificationScheduler]: Sending daily summary to {person_name} via {channel} ({recipient})")

    send_result = await notification_service.send_notification(channel, recipient, message)
    status = send_result.get("status", "failed")
    error_message = send_result.get("error_message")

    notification_log_repository.create(
        db=db,
        restaurant_id=restaurant_id,
        channel=channel,
        recipient=recipient,
        message=message,
        status=status,
        error_message=error_message,
    )

    results.append({
        "person_id": person_id,
        "person_name": person_name,
        "channel": channel,
        "recipient": recipient,
        "status": status,
        "error_message": error_message,
    })

    return status == "sent"


async def send_morning_task_summaries(
    db: Session,
    user_id: UUID,
    restaurant_id: UUID,
) -> dict:
    """
    Send daily task summary notifications to all employees in a restaurant.

    Routes notifications via email, WhatsApp, or both based on each person's
    available contact information.

    Orchestrates the full flow:
    1. Fetches all daily summaries from EventService.
    2. For each summary, fetches the person to get contact info.
    3. Determines channel(s) based on available email/whatsapp fields.
    4. Formats and sends via appropriate channel(s).
    5. Logs each attempt to the notification_log table.

    Args:
        db: Database session
        user_id: User UUID for authorization
        restaurant_id: Restaurant UUID

    Returns:
        Dictionary with total_employees, sent_count, skipped_count, results list
    """
    print(f"INFO [NotificationScheduler]: Sending morning task summaries for restaurant {restaurant_id}")

    summaries = event_service.get_all_daily_summaries(db, user_id, restaurant_id, date.today())
    print(f"INFO [NotificationScheduler]: Found {len(summaries)} employee summaries with tasks")

    results = []
    sent_count = 0
    skipped_count = 0

    for summary in summaries:
        person_id = summary["person_id"]
        person_name = summary["person_name"]

        try:
            person = person_service.get_person(db, user_id, person_id)
        except (ValueError, PermissionError) as e:
            print(f"ERROR [NotificationScheduler]: Could not fetch person {person_id}: {str(e)}")
            skipped_count += 1
            results.append({
                "person_id": person_id,
                "person_name": person_name,
                "recipient": "",
                "status": "skipped",
                "error_message": str(e),
            })
            continue

        channel = _determine_channel(person)

        if channel == "none":
            print(f"INFO [NotificationScheduler]: Skipping person {person_id} ({person_name}) - no contact info")
            skipped_count += 1
            results.append({
                "person_id": person_id,
                "person_name": person_name,
                "recipient": "",
                "status": "skipped",
                "error_message": "No email or WhatsApp number",
            })
            continue

        person_sent = False

        if channel in ("email", "both"):
            email_address = getattr(person, "email", "")
            html_message = format_daily_tasks_html(summary)
            sent = await _send_via_channel(
                "email", email_address, html_message, db, restaurant_id, person_id, person_name, results
            )
            if sent:
                person_sent = True

        if channel in ("whatsapp", "both"):
            whatsapp_number = getattr(person, "whatsapp", "")
            wa_message = format_daily_tasks_message(summary)
            sent = await _send_via_channel(
                "whatsapp", whatsapp_number, wa_message, db, restaurant_id, person_id, person_name, results
            )
            if sent:
                person_sent = True

        if person_sent:
            sent_count += 1

    total_employees = len(summaries)
    print(f"INFO [NotificationScheduler]: Morning summaries complete: total={total_employees}, sent={sent_count}, skipped={skipped_count}")

    return {
        "total_employees": total_employees,
        "sent_count": sent_count,
        "skipped_count": skipped_count,
        "results": results,
    }
