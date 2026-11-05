"""Cliente REST de la API de usuarios, basado en APIRequestContext de Playwright."""

from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

USUARIOS_PATH = "/api/usuarios"
ERRORES_PATH = "/api/errores"
HEALTH_PATH = "/api/health"
RESTABLECER_PATH = "/api/test/reset"


class UsuariosClient:
    def __init__(self, context: APIRequestContext) -> None:
        self._context = context

    def listar(self) -> APIResponse:
        return self._context.get(USUARIOS_PATH)

    def obtener(self, usuario_id: int) -> APIResponse:
        return self._context.get(f"{USUARIOS_PATH}/{usuario_id}")

    def crear(self, payload: dict[str, Any]) -> APIResponse:
        return self._context.post(USUARIOS_PATH, data=payload)

    def actualizar(self, usuario_id: int, payload: dict[str, Any]) -> APIResponse:
        return self._context.put(f"{USUARIOS_PATH}/{usuario_id}", data=payload)

    def actualizar_parcial(self, usuario_id: int, payload: dict[str, Any]) -> APIResponse:
        return self._context.patch(f"{USUARIOS_PATH}/{usuario_id}", data=payload)

    def eliminar(self, usuario_id: int) -> APIResponse:
        return self._context.delete(f"{USUARIOS_PATH}/{usuario_id}")

    def obtener_lento(self, timeout_ms: float | None = None) -> APIResponse:
        return self._context.get(f"{USUARIOS_PATH}/lento", timeout=timeout_ms)

    def consultar_error(self, codigo: int) -> APIResponse:
        return self._context.get(f"{ERRORES_PATH}/{codigo}")

    def enviar_crudo(self, metodo: str, ruta: str, cuerpo: bytes) -> APIResponse:
        """Envía el cuerpo tal cual, para probar payloads malformados.

        Debe ser bytes: si recibe un str inválido con Content-Type JSON, Playwright
        lo serializa como cadena JSON y el servidor recibiría un JSON válido.
        """
        return self._context.fetch(
            ruta,
            method=metodo,
            data=cuerpo,
            headers={"Content-Type": "application/json"},
        )

    def health(self) -> APIResponse:
        return self._context.get(HEALTH_PATH)

    def restablecer_datos(self) -> APIResponse:
        """Devuelve los usuarios del mock a su estado inicial."""
        return self._context.post(RESTABLECER_PATH)
