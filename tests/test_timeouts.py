"""Distingue tres situaciones que suelen confundirse:

1. Timeout del cliente: no llega respuesta a tiempo y Playwright lanza TimeoutError. No hay código HTTP.
2. HTTP 504: el servidor responde y el cliente recibe un código de estado, sin excepción.
3. HTTP 524 simulado: igual que el 504; el código es propio de Cloudflare y aquí solo se
   simula la respuesta, no su infraestructura.

Ninguna prueba usa time.sleep(): la espera la produce el retardo de la ruta en Mockoon.
"""

import time

import pytest
from playwright.sync_api import Playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from clients.usuarios_client import UsuariosClient
from config.settings import ConfiguracionTimeout, settings
from data.usuarios import ERRORES_HTTP
from utils.validators import validar_content_type_json, validar_error

pytestmark = [pytest.mark.regression, pytest.mark.timeout]

TOLERANCIA = 0.9


@pytest.mark.negative
def test_timeout_del_cliente_corta_la_espera(
    usuarios_client: UsuariosClient, configuracion_timeout: ConfiguracionTimeout
) -> None:
    corto_ms = configuracion_timeout.corto_ms

    inicio = time.perf_counter()
    with pytest.raises(PlaywrightTimeoutError, match=f"Timeout {corto_ms}ms exceeded"):
        usuarios_client.obtener_lento(timeout_ms=corto_ms)
    transcurrido_ms = (time.perf_counter() - inicio) * 1000

    assert corto_ms * TOLERANCIA <= transcurrido_ms < configuracion_timeout.retardo_ms


@pytest.mark.negative
def test_timeout_configurado_en_el_contexto_lanza_excepcion(
    playwright_instance: Playwright, configuracion_timeout: ConfiguracionTimeout
) -> None:
    context = playwright_instance.request.new_context(
        base_url=settings.base_url,
        timeout=configuracion_timeout.corto_ms,
    )
    try:
        with pytest.raises(PlaywrightTimeoutError):
            UsuariosClient(context).obtener_lento()
    finally:
        context.dispose()


def test_endpoint_lento_responde_con_timeout_suficiente(
    usuarios_client: UsuariosClient, configuracion_timeout: ConfiguracionTimeout
) -> None:
    retardo_ms = configuracion_timeout.retardo_ms

    inicio = time.perf_counter()
    response = usuarios_client.obtener_lento(timeout_ms=configuracion_timeout.suficiente_ms)
    transcurrido_ms = (time.perf_counter() - inicio) * 1000

    assert response.status == 200
    validar_content_type_json(response)
    assert response.json()["retardo_ms"] == retardo_ms
    assert retardo_ms * TOLERANCIA <= transcurrido_ms < configuracion_timeout.suficiente_ms


@pytest.mark.negative
@pytest.mark.parametrize("codigo", [504, 524])
def test_timeout_del_servidor_es_una_respuesta_inmediata(usuarios_client: UsuariosClient, codigo: int) -> None:
    """A diferencia del timeout del cliente, hay respuesta: el mock devuelve el código sin esperar."""
    error, mensaje = ERRORES_HTTP[codigo]

    inicio = time.perf_counter()
    response = usuarios_client.consultar_error(codigo)
    transcurrido_ms = (time.perf_counter() - inicio) * 1000

    assert validar_error(response, codigo, error)["mensaje"] == mensaje
    assert transcurrido_ms < settings.max_response_time_ms


@pytest.mark.negative
def test_504_y_524_son_respuestas_distintas(usuarios_client: UsuariosClient) -> None:
    gateway = usuarios_client.consultar_error(504).json()
    simulada = usuarios_client.consultar_error(524).json()

    assert (gateway["codigo"], gateway["error"]) != (simulada["codigo"], simulada["error"])
    assert "simulada" in simulada["mensaje"]
    assert "simulada" not in gateway["mensaje"]
