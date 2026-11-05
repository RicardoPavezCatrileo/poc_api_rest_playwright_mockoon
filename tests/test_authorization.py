import pytest

from clients.auth_client import AuthClient
from clients.usuarios_client import UsuariosClient
from data.auth import (
    AUTORIZACIONES_CON_FORMATO_INVALIDO,
    CREDENCIALES_SIN_PERMISOS,
    TOKEN_SIN_PERMISOS,
    TOKENS_INCORRECTOS,
)
from data.usuarios import USUARIOS_EXISTENTES
from utils.validators import validar_error, validar_lista_usuarios, validar_sin_campos_sensibles

pytestmark = [pytest.mark.regression, pytest.mark.security]


@pytest.mark.smoke
def test_token_valido_accede_al_recurso(cliente_autenticado: AuthClient) -> None:
    usuarios = validar_lista_usuarios(cliente_autenticado.listar_usuarios_seguros())

    assert [usuario["id"] for usuario in usuarios] == USUARIOS_EXISTENTES
    validar_sin_campos_sensibles(usuarios)


def test_recurso_seguro_refleja_los_datos_actuales(
    cliente_autenticado: AuthClient, usuarios_client: UsuariosClient
) -> None:
    usuarios_client.eliminar(1)

    usuarios = validar_lista_usuarios(cliente_autenticado.listar_usuarios_seguros())

    assert [usuario["id"] for usuario in usuarios] == [2, 3]


@pytest.mark.negative
def test_token_ausente_responde_401(cliente_sin_autenticacion: AuthClient) -> None:
    validar_no_autenticado(cliente_sin_autenticacion, None)


@pytest.mark.negative
@pytest.mark.parametrize("authorization", TOKENS_INCORRECTOS.values(), ids=TOKENS_INCORRECTOS.keys())
def test_token_incorrecto_responde_401(cliente_sin_autenticacion: AuthClient, authorization: str) -> None:
    validar_no_autenticado(cliente_sin_autenticacion, authorization)


@pytest.mark.negative
@pytest.mark.parametrize(
    "authorization", AUTORIZACIONES_CON_FORMATO_INVALIDO.values(), ids=AUTORIZACIONES_CON_FORMATO_INVALIDO.keys()
)
def test_token_con_formato_invalido_responde_401(cliente_sin_autenticacion: AuthClient, authorization: str) -> None:
    validar_no_autenticado(cliente_sin_autenticacion, authorization)


@pytest.mark.negative
def test_token_valido_sin_permisos_responde_403(cliente_sin_autenticacion: AuthClient) -> None:
    """401: no se sabe quién llama. 403: se sabe quién llama, pero no puede acceder al recurso."""
    token = cliente_sin_autenticacion.login(CREDENCIALES_SIN_PERMISOS).json()["access_token"]
    assert token == TOKEN_SIN_PERMISOS

    response = cliente_sin_autenticacion.listar_usuarios_seguros(f"Bearer {token}")

    cuerpo = validar_error(response, 403, "Forbidden")
    assert "no tiene permisos" in cuerpo["mensaje"]
    assert "www-authenticate" not in response.headers


def validar_no_autenticado(cliente: AuthClient, authorization: str | None) -> None:
    response = cliente.listar_usuarios_seguros(authorization)

    validar_error(response, 401, "Unauthorized")
    assert response.headers.get("www-authenticate") == "Bearer"
