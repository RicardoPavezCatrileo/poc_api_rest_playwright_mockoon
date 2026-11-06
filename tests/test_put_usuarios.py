from typing import Any

import pytest

from clients.usuarios_client import USUARIOS_PATH, UsuariosClient
from data.usuarios import (
    PAYLOADS_INVALIDOS,
    PAYLOADS_MALFORMADOS,
    PAYLOADS_SIN_NOMBRE,
    USUARIO_1,
    USUARIO_ACTUALIZADO,
    USUARIOS_EXISTENTES,
    USUARIOS_INEXISTENTES,
)
from utils.validators import validar_datos_invalidos, validar_error, validar_payload_malformado, validar_usuario

pytestmark = pytest.mark.regression


@pytest.mark.smoke
def test_actualizar_usuario_completo(usuarios_client: UsuariosClient) -> None:
    usuario = validar_usuario(usuarios_client.actualizar(1, USUARIO_ACTUALIZADO))

    assert usuario == {**USUARIO_ACTUALIZADO, "id": 1}


def test_actualizacion_completa_persiste(usuarios_client: UsuariosClient) -> None:
    usuarios_client.actualizar(1, USUARIO_ACTUALIZADO)

    assert validar_usuario(usuarios_client.obtener(1)) == {**USUARIO_ACTUALIZADO, "id": 1}


def test_actualizar_solo_afecta_al_usuario_indicado(usuarios_client: UsuariosClient) -> None:
    otros_antes = usuarios_client.listar().json()[1:]

    usuarios_client.actualizar(1, USUARIO_ACTUALIZADO)

    assert usuarios_client.listar().json()[1:] == otros_antes


@pytest.mark.negative
@pytest.mark.parametrize("usuario_id", USUARIOS_INEXISTENTES)
def test_actualizar_usuario_inexistente(usuarios_client: UsuariosClient, usuario_id: int) -> None:
    cuerpo = validar_error(usuarios_client.actualizar(usuario_id, USUARIO_ACTUALIZADO), 404, "Not Found")

    assert str(usuario_id) in cuerpo["mensaje"]
    assert [usuario["id"] for usuario in usuarios_client.listar().json()] == USUARIOS_EXISTENTES


@pytest.mark.negative
@pytest.mark.parametrize("payload", PAYLOADS_SIN_NOMBRE)
def test_actualizar_usuario_sin_nombre(usuarios_client: UsuariosClient, payload: dict[str, Any]) -> None:
    validar_datos_invalidos(usuarios_client.actualizar(1, payload))


@pytest.mark.negative
def test_actualizar_usuario_con_email_invalido(usuarios_client: UsuariosClient) -> None:
    validar_datos_invalidos(usuarios_client.actualizar(1, {**USUARIO_ACTUALIZADO, "email": "invalido"}))


@pytest.mark.negative
@pytest.mark.parametrize("payload", PAYLOADS_INVALIDOS.values(), ids=PAYLOADS_INVALIDOS.keys())
def test_actualizar_usuario_con_datos_invalidos(usuarios_client: UsuariosClient, payload: dict[str, Any]) -> None:
    validar_datos_invalidos(usuarios_client.actualizar(1, payload))


@pytest.mark.negative
@pytest.mark.parametrize("cuerpo", PAYLOADS_MALFORMADOS.values(), ids=PAYLOADS_MALFORMADOS.keys())
def test_actualizar_usuario_con_payload_malformado(usuarios_client: UsuariosClient, cuerpo: bytes) -> None:
    validar_payload_malformado(usuarios_client.enviar_crudo("PUT", f"{USUARIOS_PATH}/1", cuerpo))

    assert validar_usuario(usuarios_client.obtener(1)) == USUARIO_1


@pytest.mark.negative
def test_actualizacion_rechazada_no_persiste(usuarios_client: UsuariosClient) -> None:
    validar_datos_invalidos(usuarios_client.actualizar(1, {**USUARIO_ACTUALIZADO, "email": "invalido"}))

    assert validar_usuario(usuarios_client.obtener(1)) == USUARIO_1
