from typing import Any

import pytest

from clients.auth_client import AuthClient
from data.auth import (
    CREDENCIALES_INCORRECTAS,
    CREDENCIALES_SIN_PERMISOS,
    CREDENCIALES_VALIDAS,
    TOKEN_SIN_PERMISOS,
    TOKEN_VALIDO,
)
from data.usuarios import PAYLOADS_MALFORMADOS
from utils.validators import validar_content_type_json, validar_error

pytestmark = [pytest.mark.regression, pytest.mark.security]


@pytest.mark.smoke
def test_login_correcto_entrega_el_token(cliente_sin_autenticacion: AuthClient) -> None:
    response = cliente_sin_autenticacion.login(CREDENCIALES_VALIDAS)

    assert response.status == 200
    validar_content_type_json(response)
    assert response.json() == {"access_token": TOKEN_VALIDO, "token_type": "Bearer"}


def test_login_de_usuario_sin_permisos_entrega_otro_token(cliente_sin_autenticacion: AuthClient) -> None:
    response = cliente_sin_autenticacion.login(CREDENCIALES_SIN_PERMISOS)

    assert response.status == 200
    assert response.json()["access_token"] == TOKEN_SIN_PERMISOS


@pytest.mark.negative
@pytest.mark.parametrize("credenciales", CREDENCIALES_INCORRECTAS.values(), ids=CREDENCIALES_INCORRECTAS.keys())
def test_login_incorrecto_responde_401(cliente_sin_autenticacion: AuthClient, credenciales: dict[str, Any]) -> None:
    response = cliente_sin_autenticacion.login(credenciales)

    cuerpo = validar_error(response, 401, "Unauthorized")
    assert cuerpo["mensaje"] == "Credenciales incorrectas."
    assert "access_token" not in cuerpo


@pytest.mark.negative
@pytest.mark.parametrize("cuerpo", PAYLOADS_MALFORMADOS.values(), ids=PAYLOADS_MALFORMADOS.keys())
def test_login_con_cuerpo_malformado_responde_401(cliente_sin_autenticacion: AuthClient, cuerpo: bytes) -> None:
    validar_error(cliente_sin_autenticacion.login(cuerpo), 401, "Unauthorized")


@pytest.mark.negative
def test_login_incorrecto_no_revela_la_password_enviada(cliente_sin_autenticacion: AuthClient) -> None:
    password = "password-que-no-debe-aparecer"

    response = cliente_sin_autenticacion.login({"username": "qa_user", "password": password})

    assert password not in response.text()
