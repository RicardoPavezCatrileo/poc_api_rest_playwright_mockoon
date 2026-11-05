from typing import Any

import pytest

from clients.usuarios_client import USUARIOS_PATH, UsuariosClient
from data.usuarios import PAYLOADS_MALFORMADOS, USUARIO_1, USUARIOS_INEXISTENTES
from utils.validators import validar_datos_invalidos, validar_error, validar_payload_malformado, validar_usuario

pytestmark = pytest.mark.regression


@pytest.mark.smoke
def test_actualizar_parcialmente_conserva_los_demas_campos(usuarios_client: UsuariosClient) -> None:
    usuario = validar_usuario(usuarios_client.actualizar_parcial(1, {"nombre": "Ana T."}))

    assert usuario == {**USUARIO_1, "nombre": "Ana T."}


@pytest.mark.parametrize(
    "cambios",
    [{"email": "nuevo@example.com"}, {"rol": "supervisor"}, {"activo": False}],
    ids=["email", "rol", "activo"],
)
def test_actualizacion_parcial_persiste(usuarios_client: UsuariosClient, cambios: dict[str, Any]) -> None:
    usuarios_client.actualizar_parcial(1, cambios)

    assert validar_usuario(usuarios_client.obtener(1)) == {**USUARIO_1, **cambios}


@pytest.mark.negative
@pytest.mark.parametrize("usuario_id", USUARIOS_INEXISTENTES)
def test_actualizar_parcialmente_usuario_inexistente(usuarios_client: UsuariosClient, usuario_id: int) -> None:
    cuerpo = validar_error(usuarios_client.actualizar_parcial(usuario_id, {"nombre": "Nadie"}), 404, "Not Found")

    assert str(usuario_id) in cuerpo["mensaje"]


@pytest.mark.negative
@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"nombre": ""},
        {"nombre": "  "},
        {"email": ""},
        {"email": "invalido"},
        {"rol": "root"},
        {"activo": "si"},
        {"id": 50},
        {"password": "secreta"},
    ],
)
def test_actualizar_parcialmente_con_datos_invalidos(usuarios_client: UsuariosClient, payload: dict[str, Any]) -> None:
    validar_datos_invalidos(usuarios_client.actualizar_parcial(1, payload))

    assert validar_usuario(usuarios_client.obtener(1)) == USUARIO_1


@pytest.mark.negative
@pytest.mark.parametrize("cuerpo", PAYLOADS_MALFORMADOS)
def test_actualizar_parcialmente_con_payload_malformado(usuarios_client: UsuariosClient, cuerpo: bytes) -> None:
    validar_payload_malformado(usuarios_client.enviar_crudo("PATCH", f"{USUARIOS_PATH}/1", cuerpo))

    assert validar_usuario(usuarios_client.obtener(1)) == USUARIO_1
