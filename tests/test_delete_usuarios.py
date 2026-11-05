import pytest

from clients.usuarios_client import UsuariosClient
from data.usuarios import (
    SIGUIENTE_ID,
    USUARIO_1,
    USUARIO_ACTUALIZADO,
    USUARIO_NUEVO,
    USUARIOS_EXISTENTES,
    USUARIOS_INEXISTENTES,
)
from utils.validators import validar_error, validar_usuario

pytestmark = pytest.mark.regression


@pytest.mark.smoke
def test_eliminar_usuario_responde_204_sin_cuerpo(usuarios_client: UsuariosClient) -> None:
    response = usuarios_client.eliminar(1)

    assert response.status == 204
    assert response.body() == b""


def test_usuario_eliminado_deja_de_existir(usuarios_client: UsuariosClient) -> None:
    usuarios_client.eliminar(1)

    validar_error(usuarios_client.obtener(1), 404, "Not Found")
    assert 1 not in [usuario["id"] for usuario in usuarios_client.listar().json()]


def test_eliminar_solo_afecta_al_usuario_indicado(usuarios_client: UsuariosClient) -> None:
    usuarios_client.eliminar(2)

    assert [usuario["id"] for usuario in usuarios_client.listar().json()] == [1, 3]


@pytest.mark.negative
@pytest.mark.parametrize("usuario_id", USUARIOS_INEXISTENTES)
def test_eliminar_usuario_inexistente(usuarios_client: UsuariosClient, usuario_id: int) -> None:
    cuerpo = validar_error(usuarios_client.eliminar(usuario_id), 404, "Not Found")

    assert str(usuario_id) in cuerpo["mensaje"]
    assert [usuario["id"] for usuario in usuarios_client.listar().json()] == USUARIOS_EXISTENTES


@pytest.mark.negative
def test_eliminar_dos_veces_responde_404(usuarios_client: UsuariosClient) -> None:
    assert usuarios_client.eliminar(1).status == 204

    validar_error(usuarios_client.eliminar(1), 404, "Not Found")


@pytest.mark.smoke
def test_ciclo_de_vida_completo_de_un_usuario(usuarios_client: UsuariosClient) -> None:
    creado = validar_usuario(usuarios_client.crear(USUARIO_NUEVO), 201)
    usuario_id = creado["id"]
    assert usuario_id == SIGUIENTE_ID
    assert validar_usuario(usuarios_client.obtener(usuario_id)) == creado

    esperado = {**USUARIO_ACTUALIZADO, "id": usuario_id}
    assert validar_usuario(usuarios_client.actualizar(usuario_id, USUARIO_ACTUALIZADO)) == esperado

    esperado = {**esperado, "activo": True}
    assert validar_usuario(usuarios_client.actualizar_parcial(usuario_id, {"activo": True})) == esperado
    assert validar_usuario(usuarios_client.obtener(usuario_id)) == esperado

    assert usuarios_client.eliminar(usuario_id).status == 204
    validar_error(usuarios_client.obtener(usuario_id), 404, "Not Found")
    assert [usuario["id"] for usuario in usuarios_client.listar().json()] == USUARIOS_EXISTENTES


def test_restablecer_recupera_los_datos_iniciales(usuarios_client: UsuariosClient) -> None:
    usuarios_client.eliminar(1)

    assert usuarios_client.restablecer_datos().ok

    assert validar_usuario(usuarios_client.obtener(1)) == USUARIO_1


def test_restablecer_no_altera_la_copia_inicial(usuarios_client: UsuariosClient) -> None:
    usuarios_client.restablecer_datos()
    usuarios_client.eliminar(1)

    usuarios_client.restablecer_datos()

    assert validar_usuario(usuarios_client.obtener(1)) == USUARIO_1
