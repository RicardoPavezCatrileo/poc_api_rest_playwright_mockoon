import re
import time
from typing import Any

import pytest

from clients.usuarios_client import UsuariosClient
from config.settings import settings
from data.usuarios import USUARIO_1
from utils.validators import (
    ESQUEMA_USUARIO,
    validar_datos_invalidos,
    validar_esquema,
    validar_lista_usuarios,
    validar_payload_malformado,
    validar_sin_campos_sensibles,
    validar_usuario,
)

pytestmark = [pytest.mark.regression, pytest.mark.contract]


def test_contrato_lista_de_usuarios(usuarios_client: UsuariosClient) -> None:
    usuarios = validar_lista_usuarios(usuarios_client.listar())

    assert usuarios
    for usuario in usuarios:
        assert re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", usuario["email"])
    assert len({usuario["id"] for usuario in usuarios}) == len(usuarios)


def test_contrato_valores_esperados_del_usuario(usuarios_client: UsuariosClient) -> None:
    assert validar_usuario(usuarios_client.obtener(1)) == USUARIO_1


@pytest.mark.parametrize("obtener", ["listar", "obtener_1"])
def test_respuesta_sin_campos_sensibles(usuarios_client: UsuariosClient, obtener: str) -> None:
    response = usuarios_client.listar() if obtener == "listar" else usuarios_client.obtener(1)

    validar_sin_campos_sensibles(response.json())


def test_tiempo_de_respuesta_dentro_del_umbral(usuarios_client: UsuariosClient) -> None:
    inicio = time.perf_counter()
    usuarios_client.listar()
    transcurrido_ms = (time.perf_counter() - inicio) * 1000

    assert transcurrido_ms < settings.max_response_time_ms


def test_delete_no_declara_content_type(usuarios_client: UsuariosClient) -> None:
    assert "content-type" not in usuarios_client.eliminar(1).headers


# Comprueban que los validadores rechazan datos incorrectos: sin esto, un validador
# defectuoso dejaría pasar todas las pruebas de contrato anteriores.
@pytest.mark.parametrize(
    "datos",
    [
        pytest.param({k: v for k, v in USUARIO_1.items() if k != "email"}, id="campo-faltante"),
        pytest.param({**USUARIO_1, "id": "1"}, id="tipo-incorrecto"),
        pytest.param({**USUARIO_1, "id": True}, id="bool-como-int"),
    ],
)
def test_validar_esquema_rechaza_datos_incorrectos(datos: dict[str, Any]) -> None:
    with pytest.raises(AssertionError):
        validar_esquema(datos, ESQUEMA_USUARIO)


def test_validadores_de_error_rechazan_errores_genericos(usuarios_client: UsuariosClient) -> None:
    with pytest.raises(AssertionError):
        validar_datos_invalidos(usuarios_client.consultar_error(422))
    with pytest.raises(AssertionError):
        validar_payload_malformado(usuarios_client.consultar_error(400))


@pytest.mark.parametrize(
    "datos",
    [
        pytest.param({"password": "x"}, id="directo"),
        pytest.param({"Token": "x"}, id="mayusculas"),
        pytest.param([{"perfil": {"api_key": "x"}}], id="anidado"),
    ],
)
def test_validar_sin_campos_sensibles_los_detecta(datos: Any) -> None:
    with pytest.raises(AssertionError):
        validar_sin_campos_sensibles(datos)
