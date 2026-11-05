import pytest

from clients.auth_client import AuthClient
from data.auth import API_KEY_VALIDA, API_KEYS_RECHAZADAS, TOKEN_VALIDO
from data.usuarios import USUARIOS_EXISTENTES
from utils.validators import validar_error, validar_lista_usuarios, validar_sin_campos_sensibles

pytestmark = [pytest.mark.regression, pytest.mark.security]


@pytest.mark.smoke
def test_api_key_valida_accede_al_recurso(cliente_sin_autenticacion: AuthClient) -> None:
    usuarios = validar_lista_usuarios(cliente_sin_autenticacion.listar_usuarios_con_api_key(API_KEY_VALIDA))

    assert [usuario["id"] for usuario in usuarios] == USUARIOS_EXISTENTES
    validar_sin_campos_sensibles(usuarios)


@pytest.mark.negative
@pytest.mark.parametrize("api_key", API_KEYS_RECHAZADAS.values(), ids=API_KEYS_RECHAZADAS.keys())
def test_api_key_rechazada_responde_401(cliente_sin_autenticacion: AuthClient, api_key: str | None) -> None:
    cuerpo = validar_error(cliente_sin_autenticacion.listar_usuarios_con_api_key(api_key), 401, "Unauthorized")

    assert "API Key" in cuerpo["mensaje"]


@pytest.mark.negative
def test_el_token_bearer_no_sustituye_a_la_api_key(cliente_sin_autenticacion: AuthClient) -> None:
    validar_error(cliente_sin_autenticacion.listar_usuarios_con_api_key(TOKEN_VALIDO), 401, "Unauthorized")
