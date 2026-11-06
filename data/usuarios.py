"""Datos de prueba, separados de los casos de prueba."""

from typing import Any

USUARIOS_EXISTENTES = [1, 2, 3]
USUARIOS_INEXISTENTES = [999, 12345]
SIGUIENTE_ID = 4

USUARIO_1: dict[str, Any] = {
    "id": 1,
    "nombre": "Ana Torres",
    "email": "ana.torres@example.com",
    "rol": "admin",
    "activo": True,
}

USUARIO_NUEVO: dict[str, Any] = {
    "nombre": "Diego Rojas",
    "email": "diego.rojas@example.com",
    "rol": "usuario",
    "activo": True,
}

USUARIO_ACTUALIZADO: dict[str, Any] = {
    "nombre": "Ana María Torres",
    "email": "ana.maria@example.com",
    "rol": "supervisor",
    "activo": False,
}

NOMBRES_VALIDOS = ["José Ñúñez", "Liam O'Brien", 'Ana "Anita" Pérez']

EMAILS_INVALIDOS = ["sin-arroba.example.com", "ana@", "@example.com", "ana@example", "ana torres@example.com", ""]

PAYLOADS_SIN_NOMBRE: list[dict[str, Any]] = [
    {k: v for k, v in USUARIO_NUEVO.items() if k != "nombre"},
    {**USUARIO_NUEVO, "nombre": ""},
    {**USUARIO_NUEVO, "nombre": "   "},
    {**USUARIO_NUEVO, "nombre": None},
]

# Cada payload incumple una sola regla del contrato de POST y PUT.
PAYLOADS_INVALIDOS: dict[str, dict[str, Any]] = {
    "sin-rol": {k: v for k, v in USUARIO_NUEVO.items() if k != "rol"},
    "sin-activo": {k: v for k, v in USUARIO_NUEVO.items() if k != "activo"},
    "rol-desconocido": {**USUARIO_NUEVO, "rol": "root"},
    "activo-no-booleano": {**USUARIO_NUEVO, "activo": "si"},
    "campo-sensible": {**USUARIO_NUEVO, "password": "secreta"},
    "id-en-el-cuerpo": {**USUARIO_NUEVO, "id": 50},
}

PAYLOADS_MALFORMADOS: dict[str, bytes] = {
    "json-truncado": b'{"nombre": "Ana", "email": ',
    "coma-final": b'{"nombre": "Ana",}',
    "texto-plano": b"esto no es json",
    "cuerpo-vacio": b"",
}

# Código de /api/errores/<código>: (error, mensaje).
ERRORES_HTTP: dict[int, tuple[str, str]] = {
    400: ("Bad Request", "La solicitud es incorrecta."),
    401: ("Unauthorized", "Se requiere autenticación."),
    403: ("Forbidden", "No tiene permisos para acceder a este recurso."),
    404: ("Not Found", "El recurso solicitado no existe."),
    409: ("Conflict", "El recurso entra en conflicto con el estado actual."),
    422: ("Unprocessable Entity", "Los datos enviados no son procesables."),
    429: ("Too Many Requests", "Se superó el límite de solicitudes."),
    500: ("Internal Server Error", "Error interno del servidor."),
    502: ("Bad Gateway", "Respuesta inválida del servidor de origen."),
    503: ("Service Unavailable", "Servicio temporalmente no disponible."),
    504: ("Gateway Timeout", "El gateway no recibió respuesta a tiempo."),
    # 524 es propio de Cloudflare, no un código HTTP estándar. Mockoon solo simula la respuesta.
    524: ("A Timeout Occurred", "Respuesta 524 simulada; no reproduce la infraestructura real de Cloudflare."),
}
