"""HTML email templates for notification types (Spanish - Colombian)."""

from datetime import date

BASE_STYLE = (
    "font-family: Arial, Helvetica, sans-serif; "
    "max-width: 600px; margin: 0 auto; padding: 20px; "
    "color: #333333; line-height: 1.6;"
)

HEADER_STYLE = (
    "background-color: #2196F3; color: #ffffff; "
    "padding: 20px; border-radius: 8px 8px 0 0; text-align: center;"
)

BODY_STYLE = (
    "background-color: #ffffff; padding: 20px; "
    "border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 8px 8px;"
)

FOOTER_STYLE = (
    "text-align: center; padding: 15px; "
    "color: #888888; font-size: 12px;"
)

TABLE_STYLE = (
    "width: 100%; border-collapse: collapse; margin: 15px 0;"
)

TH_STYLE = (
    "background-color: #f5f5f5; padding: 10px; "
    "text-align: left; border-bottom: 2px solid #2196F3; font-size: 14px;"
)

TD_STYLE = "padding: 10px; border-bottom: 1px solid #eeeeee; font-size: 14px;"

TD_OVERDUE_STYLE = (
    "padding: 10px; border-bottom: 1px solid #eeeeee; "
    "font-size: 14px; background-color: #ffebee; color: #c62828;"
)

URGENT_HEADER_STYLE = (
    "background-color: #d32f2f; color: #ffffff; "
    "padding: 20px; border-radius: 8px 8px 0 0; text-align: center;"
)

WARNING_HEADER_STYLE = (
    "background-color: #f9a825; color: #ffffff; "
    "padding: 20px; border-radius: 8px 8px 0 0; text-align: center;"
)


def format_daily_tasks_html(summary: dict) -> str:
    """
    Format a daily task summary as mobile-friendly HTML email.

    Args:
        summary: Dictionary with person_name, date, total_tasks, overdue_count, tasks list

    Returns:
        HTML string for the email body
    """
    person_name = summary.get("person_name", "Empleado")
    summary_date = summary.get("date", date.today())
    total_tasks = summary.get("total_tasks", 0)
    overdue_count = summary.get("overdue_count", 0)
    tasks = summary.get("tasks", [])

    if total_tasks == 0:
        task_section = (
            '<p style="text-align: center; color: #4caf50; font-size: 16px;">'
            "No tienes tareas pendientes para hoy. Buen trabajo!</p>"
        )
    else:
        rows = ""
        for task in tasks:
            description = task.get("description", "Sin descripcion")
            task_time = task.get("time", "")
            is_overdue = task.get("is_overdue", False)
            status = "VENCIDA" if is_overdue else "Pendiente"
            style = TD_OVERDUE_STYLE if is_overdue else TD_STYLE

            rows += (
                f"<tr>"
                f'<td style="{style}">{description}</td>'
                f'<td style="{style}">{task_time}</td>'
                f'<td style="{style}">{status}</td>'
                f"</tr>"
            )

        overdue_msg = ""
        if overdue_count > 0:
            overdue_msg = (
                f'<p style="color: #c62828; font-weight: bold;">'
                f"{overdue_count} tarea(s) vencida(s)</p>"
            )

        task_section = (
            f"<p>Tienes <strong>{total_tasks} tarea(s)</strong> pendiente(s)</p>"
            f"{overdue_msg}"
            f'<table style="{TABLE_STYLE}">'
            f"<thead><tr>"
            f'<th style="{TH_STYLE}">Descripcion</th>'
            f'<th style="{TH_STYLE}">Hora</th>'
            f'<th style="{TH_STYLE}">Estado</th>'
            f"</tr></thead>"
            f"<tbody>{rows}</tbody>"
            f"</table>"
        )

    return (
        f'<div style="{BASE_STYLE}">'
        f'<div style="{HEADER_STYLE}">'
        f"<h2>Resumen de Tareas</h2>"
        f"</div>"
        f'<div style="{BODY_STYLE}">'
        f"<p>Buenos dias, <strong>{person_name}</strong>!</p>"
        f"<p>Resumen de tareas para <strong>{summary_date}</strong></p>"
        f"{task_section}"
        f"</div>"
        f'<div style="{FOOTER_STYLE}">'
        f"<p>Que tengas un excelente dia!</p>"
        f"<p>Restaurant OS - Notificaciones</p>"
        f"</div>"
        f"</div>"
    )


def format_expiration_alert_html(document_name: str, expiry_date: str, days_until: int) -> str:
    """
    Format a document expiration alert as HTML email.

    Args:
        document_name: Name of the expiring document
        expiry_date: Expiration date string
        days_until: Number of days until expiration

    Returns:
        HTML string for the email body
    """
    is_urgent = days_until <= 7
    header_style = URGENT_HEADER_STYLE if is_urgent else WARNING_HEADER_STYLE
    urgency_label = "URGENTE" if is_urgent else "Atencion"
    urgency_color = "#c62828" if is_urgent else "#f57f17"

    return (
        f'<div style="{BASE_STYLE}">'
        f'<div style="{header_style}">'
        f"<h2>{urgency_label} - Documento por Vencer</h2>"
        f"</div>"
        f'<div style="{BODY_STYLE}">'
        f'<p style="font-size: 16px;">El documento <strong>{document_name}</strong> '
        f"vence el <strong>{expiry_date}</strong>.</p>"
        f'<p style="font-size: 24px; text-align: center; color: {urgency_color}; font-weight: bold;">'
        f"Quedan {days_until} dia(s)</p>"
        f"<p>Por favor, gestiona la renovacion a tiempo.</p>"
        f"</div>"
        f'<div style="{FOOTER_STYLE}">'
        f"<p>Restaurant OS - Notificaciones</p>"
        f"</div>"
        f"</div>"
    )


def format_low_stock_alert_html(resource_name: str, current_stock: float, min_stock: float) -> str:
    """
    Format a low stock alert as HTML email.

    Args:
        resource_name: Name of the resource/ingredient
        current_stock: Current stock level
        min_stock: Minimum stock threshold

    Returns:
        HTML string for the email body
    """
    return (
        f'<div style="{BASE_STYLE}">'
        f'<div style="{WARNING_HEADER_STYLE}">'
        f"<h2>Alerta de Stock Bajo</h2>"
        f"</div>"
        f'<div style="{BODY_STYLE}">'
        f"<p>El recurso <strong>{resource_name}</strong> esta por debajo del minimo:</p>"
        f'<table style="{TABLE_STYLE}">'
        f"<tr>"
        f'<td style="{TD_STYLE}"><strong>Stock actual</strong></td>'
        f'<td style="{TD_STYLE}">{current_stock}</td>'
        f"</tr>"
        f"<tr>"
        f'<td style="{TD_STYLE}"><strong>Stock minimo</strong></td>'
        f'<td style="{TD_STYLE}">{min_stock}</td>'
        f"</tr>"
        f"</table>"
        f"<p>Por favor, realiza el pedido correspondiente.</p>"
        f"</div>"
        f'<div style="{FOOTER_STYLE}">'
        f"<p>Restaurant OS - Notificaciones</p>"
        f"</div>"
        f"</div>"
    )
