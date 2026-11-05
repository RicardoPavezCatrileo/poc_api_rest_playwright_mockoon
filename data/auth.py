"""Credenciales ficticias, exclusivamente de laboratorio. Los tokens son cadenas fijas, no JWT."""

from typing import Any

CREDENCIALES_VALIDAS = {"username": "qa_user", "password": "demo123"}
CREDENCIALES_SIN_PERMISOS = {"username": "qa_sin_permisos", "password": "demo123"}

TOKEN_VALIDO = "token-demo-12345"
TOKEN_SIN_PERMISOS = "token-sin-permisos-67890"

API_KEY_VALIDA = "demo-api-key-123"

CREDENCIALES_INCORRECTAS: dict[str, dict[str, Any]] = {
    "password-incorrecta": {"username": "qa_user", "password": "otra"},
    "usuario-desconocido": {"username": "desconocido", "password": "demo123"},
    "usuario-con-otras-mayusculas": {"username": "QA_USER", "password": "demo123"},
    "sin-password": {"username": "qa_user"},
    "sin-username": {"password": "demo123"},
    "password-vacia": {"username": "qa_user", "password": ""},
    "cuerpo-vacio": {},
}

TOKENS_INCORRECTOS = {
    "desconocido": "Bearer token-falso",
    "otras-mayusculas": f"Bearer {TOKEN_VALIDO.upper()}",
    "truncado": f"Bearer {TOKEN_VALIDO[:-1]}",
}

AUTORIZACIONES_CON_FORMATO_INVALIDO = {
    "sin-esquema": TOKEN_VALIDO,
    "otro-esquema": f"Basic {TOKEN_VALIDO}",
    "esquema-sin-token": "Bearer",
    "contenido-adicional": f"Bearer {TOKEN_VALIDO} adicional",
    "cabecera-vacia": "",
}

API_KEYS_RECHAZADAS: dict[str, str | None] = {
    "incorrecta": "api-key-falsa",
    "otras-mayusculas": API_KEY_VALIDA.upper(),
    "ausente": None,
    "vacia": "",
}
