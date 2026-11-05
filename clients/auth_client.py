"""Cliente de los endpoints protegidos, basado en APIRequestContext de Playwright."""

from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

LOGIN_PATH = "/api/auth/login"
SECURE_USUARIOS_PATH = "/api/secure/usuarios"
APIKEY_USUARIOS_PATH = "/api/apikey/usuarios"


class AuthClient:
    """Envía solo las credenciales que recibe o que ya tenga configuradas el contexto."""

    def __init__(self, context: APIRequestContext) -> None:
        self._context = context

    def login(self, credenciales: dict[str, Any] | bytes) -> APIResponse:
        """Un dict se envía como JSON; bytes se envían tal cual, para probar cuerpos malformados."""
        return self._context.post(LOGIN_PATH, data=credenciales, headers={"Content-Type": "application/json"})

    def listar_usuarios_seguros(self, authorization: str | None = None) -> APIResponse:
        return self._context.get(SECURE_USUARIOS_PATH, headers=_cabecera("Authorization", authorization))

    def listar_usuarios_con_api_key(self, api_key: str | None = None) -> APIResponse:
        return self._context.get(APIKEY_USUARIOS_PATH, headers=_cabecera("X-API-Key", api_key))


def _cabecera(nombre: str, valor: str | None) -> dict[str, str] | None:
    """None omite la cabecera; una cadena vacía se envía, porque son casos de prueba distintos."""
    return None if valor is None else {nombre: valor}
