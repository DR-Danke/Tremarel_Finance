"""Permit type presets with pre-configured alert schedules for common restaurant permits."""

PERMIT_PRESETS: dict[str, dict] = {
    "manipulacion_alimentos": {
        "name": "Certificado de Manipulación de Alimentos",
        "alert_windows": [30, 7, 0],
        "notification_channel": "whatsapp",
    },
    "bomberos": {
        "name": "Permiso de Bomberos",
        "alert_windows": [0],
        "notification_channel": "whatsapp",
    },
    "camara_comercio": {
        "name": "Registro de Cámara de Comercio",
        "alert_windows": [30, 14],
        "notification_channel": "email",
    },
    "extintor": {
        "name": "Servicio de Extintores",
        "alert_windows": [30, 7],
        "notification_channel": "whatsapp",
    },
    "sanidad": {
        "name": "Certificado de Inspección Sanitaria",
        "alert_windows": [30, 14, 7],
        "notification_channel": "whatsapp",
    },
}
