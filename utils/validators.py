"""Validaciones de contrato reutilizables."""

from typing import Any

from playwright.sync_api import APIResponse

ESQUEMA_USUARIO: dict[str, type] = {
    "id": int,
    "nombre": str,
    "email": str,
    "rol": str,
    "activo": bool,
}

ESQUEMA_ERROR: dict[str, type] = {"codigo": int, "error": str, "mensaje": str}

CAMPOS_SENSIBLES = frozenset({"password", "contrasena", "clave", "hash", "salt", "token", "secret", "api_key"})


def validar_content_type_json(response: APIResponse) -> None:
    content_type = response.headers.get("content-type", "")
    assert content_type.startswith("application/json"), f"Content-Type inesperado: {content_type!r}"


def validar_esquema(datos: dict[str, Any], esquema: dict[str, type]) -> None:
    """Comprueba campos obligatorios y tipos exactos (un bool no se acepta como int)."""
    faltantes = esquema.keys() - datos.keys()
    assert not faltantes, f"Faltan campos obligatorios: {sorted(faltantes)}"
    for campo, tipo in esquema.items():
        assert type(datos[campo]) is tipo, (
            f"El campo {campo!r} debe ser {tipo.__name__}, se recibió {type(datos[campo]).__name__}"
        )


def validar_sin_campos_sensibles(datos: Any) -> None:
    """Busca campos sensibles de forma recursiva en objetos y listas."""
    if isinstance(datos, dict):
        expuestos = {clave for clave in datos if clave.lower() in CAMPOS_SENSIBLES}
        assert not expuestos, f"La respuesta expone campos sensibles: {sorted(expuestos)}"
        for valor in datos.values():
            validar_sin_campos_sensibles(valor)
    elif isinstance(datos, list):
        for elemento in datos:
            validar_sin_campos_sensibles(elemento)


def validar_usuario(response: APIResponse, status: int = 200) -> dict[str, Any]:
    assert response.status == status, f"HTTP {response.status}: {response.text()}"
    validar_content_type_json(response)
    usuario = response.json()
    validar_esquema(usuario, ESQUEMA_USUARIO)
    return usuario


def validar_lista_usuarios(response: APIResponse) -> list[dict[str, Any]]:
    assert response.status == 200, f"HTTP {response.status}: {response.text()}"
    validar_content_type_json(response)
    usuarios = response.json()
    assert isinstance(usuarios, list), f"Se esperaba una lista: {usuarios!r}"
    for usuario in usuarios:
        validar_esquema(usuario, ESQUEMA_USUARIO)
    return usuarios


def validar_error(response: APIResponse, codigo: int, error: str | None = None) -> dict[str, Any]:
    assert response.status == codigo, f"HTTP {response.status}: {response.text()}"
    validar_content_type_json(response)
    cuerpo = response.json()
    validar_esquema(cuerpo, ESQUEMA_ERROR)
    assert cuerpo["codigo"] == codigo
    if error is not None:
        assert cuerpo["error"] == error
    return cuerpo


def validar_datos_invalidos(response: APIResponse) -> None:
    """HTTP 422 propio de la validación de usuarios, no un 422 genérico."""
    cuerpo = validar_error(response, 422, "Unprocessable Entity")
    assert cuerpo["mensaje"].startswith("Datos inválidos"), f"Mensaje inesperado: {cuerpo['mensaje']!r}"


def validar_payload_malformado(response: APIResponse) -> None:
    """HTTP 400 propio de un cuerpo que no es un objeto JSON, no un 400 genérico."""
    cuerpo = validar_error(response, 400, "Bad Request")
    assert "objeto JSON" in cuerpo["mensaje"], f"Mensaje inesperado: {cuerpo['mensaje']!r}"
