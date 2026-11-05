import pytest

from clients.usuarios_client import UsuariosClient
from data.usuarios import ERRORES_HTTP
from utils.validators import validar_error

pytestmark = [pytest.mark.regression, pytest.mark.negative]


@pytest.mark.parametrize(
    ("codigo", "error", "mensaje"),
    [(codigo, error, mensaje) for codigo, (error, mensaje) in ERRORES_HTTP.items()],
    ids=[str(codigo) for codigo in ERRORES_HTTP],
)
def test_error_http(usuarios_client: UsuariosClient, codigo: int, error: str, mensaje: str) -> None:
    cuerpo = validar_error(usuarios_client.consultar_error(codigo), codigo, error)

    assert cuerpo["mensaje"] == mensaje


@pytest.mark.parametrize(
    ("codigo", "encabezado", "valor"),
    [(401, "www-authenticate", "Bearer"), (429, "retry-after", "60"), (503, "retry-after", "30")],
)
def test_encabezados_de_error(usuarios_client: UsuariosClient, codigo: int, encabezado: str, valor: str) -> None:
    assert usuarios_client.consultar_error(codigo).headers[encabezado] == valor
