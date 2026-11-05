from typing import Any

import pytest

from clients.usuarios_client import USUARIOS_PATH, UsuariosClient
from data.usuarios import (
    EMAILS_INVALIDOS,
    NOMBRES_VALIDOS,
    PAYLOADS_INVALIDOS,
    PAYLOADS_MALFORMADOS,
    PAYLOADS_SIN_NOMBRE,
    SIGUIENTE_ID,
    USUARIO_NUEVO,
    USUARIOS_EXISTENTES,
)
from utils.validators import validar_datos_invalidos, validar_payload_malformado, validar_usuario

pytestmark = pytest.mark.regression


def ids_de_usuarios(client: UsuariosClient) -> list[int]:
    return [usuario["id"] for usuario in client.listar().json()]


@pytest.mark.smoke
def test_crear_usuario_valido(usuarios_client: UsuariosClient) -> None:
    usuario = validar_usuario(usuarios_client.crear(USUARIO_NUEVO), 201)

    assert usuario == {**USUARIO_NUEVO, "id": SIGUIENTE_ID}


def test_usuario_creado_persiste(usuarios_client: UsuariosClient) -> None:
    creado = validar_usuario(usuarios_client.crear(USUARIO_NUEVO), 201)

    assert validar_usuario(usuarios_client.obtener(creado["id"])) == creado
    assert ids_de_usuarios(usuarios_client) == [*USUARIOS_EXISTENTES, creado["id"]]


@pytest.mark.parametrize("nombre", NOMBRES_VALIDOS)
def test_crear_usuario_con_caracteres_especiales(usuarios_client: UsuariosClient, nombre: str) -> None:
    usuario = validar_usuario(usuarios_client.crear({**USUARIO_NUEVO, "nombre": nombre}), 201)

    assert usuario["nombre"] == nombre


@pytest.mark.negative
@pytest.mark.parametrize("payload", PAYLOADS_SIN_NOMBRE)
def test_crear_usuario_sin_nombre(usuarios_client: UsuariosClient, payload: dict[str, Any]) -> None:
    validar_datos_invalidos(usuarios_client.crear(payload))


@pytest.mark.negative
@pytest.mark.parametrize("email", EMAILS_INVALIDOS)
def test_crear_usuario_con_email_invalido(usuarios_client: UsuariosClient, email: str) -> None:
    validar_datos_invalidos(usuarios_client.crear({**USUARIO_NUEVO, "email": email}))


@pytest.mark.negative
@pytest.mark.parametrize("payload", PAYLOADS_INVALIDOS.values(), ids=PAYLOADS_INVALIDOS.keys())
def test_crear_usuario_con_datos_invalidos(usuarios_client: UsuariosClient, payload: dict[str, Any]) -> None:
    validar_datos_invalidos(usuarios_client.crear(payload))


@pytest.mark.negative
@pytest.mark.parametrize("cuerpo", PAYLOADS_MALFORMADOS)
def test_crear_usuario_con_payload_malformado(usuarios_client: UsuariosClient, cuerpo: bytes) -> None:
    validar_payload_malformado(usuarios_client.enviar_crudo("POST", USUARIOS_PATH, cuerpo))

    assert ids_de_usuarios(usuarios_client) == USUARIOS_EXISTENTES


@pytest.mark.negative
def test_creacion_rechazada_no_persiste(usuarios_client: UsuariosClient) -> None:
    validar_datos_invalidos(usuarios_client.crear({**USUARIO_NUEVO, "email": "invalido"}))

    assert ids_de_usuarios(usuarios_client) == USUARIOS_EXISTENTES
