from collections.abc import Iterator
from typing import Any

import pytest
from playwright.sync_api import APIRequestContext, Error, Playwright, sync_playwright

from clients.auth_client import AuthClient
from clients.usuarios_client import UsuariosClient
from config.settings import ConfiguracionTimeout, settings
from data.auth import CREDENCIALES_VALIDAS


def pytest_html_report_title(report: Any) -> None:
    report.title = "POC API REST: Playwright, Pytest y Mockoon"


def _crear_contexto(playwright: Playwright, cabeceras: dict[str, str] | None = None) -> APIRequestContext:
    return playwright.request.new_context(
        base_url=settings.base_url,
        timeout=settings.timeout_ms,
        extra_http_headers={"Accept": "application/json", **(cabeceras or {})},
    )


@pytest.fixture(scope="session")
def playwright_instance() -> Iterator[Playwright]:
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def api_context(playwright_instance: Playwright) -> Iterator[APIRequestContext]:
    context = _crear_contexto(playwright_instance)
    yield context
    context.dispose()


@pytest.fixture(scope="session", autouse=True)
def api_disponible(api_context: APIRequestContext) -> None:
    """Detiene la ejecución si no se puede usar el mock, en lugar de omitir o fallar cada prueba."""
    client = UsuariosClient(api_context)
    try:
        health = client.health()
        restablecido = client.restablecer_datos()
    except Error as error:
        pytest.exit(
            f"La API no está disponible en {settings.base_url}. Inicie Mockoon antes de ejecutar las pruebas.\n{error}",
            returncode=3,
        )
    if not (health.ok and restablecido.ok):
        pytest.exit(
            f"El servidor en {settings.base_url} no parece ser este mock: /api/health respondió "
            f"HTTP {health.status} y /api/test/reset HTTP {restablecido.status}. "
            "Reinícielo con la versión actual de mocks/usuarios-api.json.",
            returncode=3,
        )


@pytest.fixture
def configuracion_timeout() -> ConfiguracionTimeout:
    """Falla si un cambio en .env dejara las pruebas de timeout sin sentido."""
    configuracion = ConfiguracionTimeout(
        corto_ms=settings.short_timeout_ms,
        suficiente_ms=settings.timeout_ms,
        retardo_ms=settings.slow_endpoint_delay_ms,
    )
    assert configuracion.corto_ms < configuracion.retardo_ms < configuracion.suficiente_ms, configuracion
    return configuracion


@pytest.fixture
def usuarios_client(api_context: APIRequestContext) -> UsuariosClient:
    return UsuariosClient(api_context)


@pytest.fixture
def cliente_sin_autenticacion(api_context: APIRequestContext) -> AuthClient:
    return AuthClient(api_context)


@pytest.fixture
def bearer_token(cliente_sin_autenticacion: AuthClient) -> str:
    response = cliente_sin_autenticacion.login(CREDENCIALES_VALIDAS)
    assert response.status == 200, f"No se pudo iniciar sesión: HTTP {response.status}"
    return response.json()["access_token"]


@pytest.fixture
def cliente_autenticado(playwright_instance: Playwright, bearer_token: str) -> Iterator[AuthClient]:
    """Usa un contexto propio para que el token no alcance a las demás pruebas."""
    context = _crear_contexto(playwright_instance, {"Authorization": f"Bearer {bearer_token}"})
    yield AuthClient(context)
    context.dispose()


@pytest.fixture(autouse=True)
def datos_iniciales(usuarios_client: UsuariosClient) -> None:
    """Cada prueba empieza con los datos iniciales: el mock conserva los cambios entre solicitudes."""
    response = usuarios_client.restablecer_datos()
    assert response.ok, f"No se pudieron restablecer los datos: HTTP {response.status}"
