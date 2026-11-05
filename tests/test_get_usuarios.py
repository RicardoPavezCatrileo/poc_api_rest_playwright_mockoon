import pytest

from clients.usuarios_client import UsuariosClient
from data.usuarios import USUARIOS_EXISTENTES, USUARIOS_INEXISTENTES
from utils.validators import validar_error, validar_usuario

pytestmark = pytest.mark.regression


@pytest.mark.smoke
def test_listar_usuarios(usuarios_client: UsuariosClient) -> None:
    response = usuarios_client.listar()

    assert response.status == 200
    assert [usuario["id"] for usuario in response.json()] == USUARIOS_EXISTENTES


@pytest.mark.smoke
@pytest.mark.parametrize("usuario_id", USUARIOS_EXISTENTES)
def test_obtener_usuario_existente(usuarios_client: UsuariosClient, usuario_id: int) -> None:
    usuario = validar_usuario(usuarios_client.obtener(usuario_id))

    assert usuario["id"] == usuario_id


@pytest.mark.negative
@pytest.mark.parametrize("usuario_id", USUARIOS_INEXISTENTES)
def test_obtener_usuario_inexistente(usuarios_client: UsuariosClient, usuario_id: int) -> None:
    cuerpo = validar_error(usuarios_client.obtener(usuario_id), 404, "Not Found")

    assert str(usuario_id) in cuerpo["mensaje"]
