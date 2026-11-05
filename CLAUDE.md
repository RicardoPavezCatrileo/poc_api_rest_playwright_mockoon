# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos

Requieren Mockoon en marcha, Desktop o CLI, nunca ambos en el mismo puerto; si no, Pytest se detiene con código de salida 3.

```powershell
npx @mockoon/cli@9.10.0 start --data .\mocks\usuarios-api.json --disable-log-to-file   # Terminal aparte
python -m pip install -r requirements.txt
python -m pytest -v
python -m pytest -m smoke -v      # También: regression, negative, security, contract, timeout
python -m pytest tests/test_timeouts.py::test_timeout_del_cliente_corta_la_espera -v
python -m pytest -v --html=reports/report.html --self-contained-html
```

Mockoon carga el archivo al iniciar: reinícialo después de editar el mock. No hace falta `playwright install`, porque `APIRequestContext` no usa navegadores. No hay linter configurado.

## Arquitectura

Las pruebas (`tests/`) reciben sus clientes desde `conftest.py`. `usuarios_client` y `cliente_sin_autenticacion` comparten un único `APIRequestContext` por sesión, sin credenciales; `cliente_autenticado` usa un contexto propio con el token, para que no alcance a otras pruebas. Las aserciones de contrato están en `utils/validators.py`, los datos en `data/` y la configuración, leída de variables de entorno o `.env`, en `config/settings.py`.

El mock guarda los usuarios en memoria, en el data bucket `usuarios`. El fixture autouse `datos_iniciales` los restablece antes de cada prueba con `POST /api/test/reset`, así que las pruebas pueden modificar datos sin afectarse entre sí, pero no pueden ejecutarse en paralelo.

## Restricciones

- Todas las solicitudes HTTP pasan por Playwright. No uses Requests ni Selenium.
- Toda prueba lleva `regression`, además de sus marcadores específicos. `--strict-markers` rechaza los no declarados en `pytest.ini`.
- No inventes resultados en el README: solo salidas de ejecuciones reales.

## Detalles que no son evidentes

**Playwright**
- Los payloads malformados deben enviarse como `bytes` (`enviar_crudo`, `AuthClient.login`). Un `str` inválido con `Content-Type` JSON se serializa como cadena JSON válida, y la prueba dejaría de enviar un JSON roto.

**`mocks/usuarios-api.json`**
- Las rutas se evalúan en orden: `lento`, `999` y DELETE van antes de la ruta CRUD `api/usuarios`.
- DELETE tiene ruta propia porque el modo CRUD responde 200 y el contrato exige 204. Borra con `setData 'del'` en la plantilla.
- Las reglas de una ruta CRUD se evalúan en todos sus métodos: las de validación deben incluir una regla `method`, o un GET sin cuerpo devolvería 400.
- La respuesta `default` de la ruta CRUD ejecuta la operación; las respuestas con reglas son cuerpos inline y no tocan los datos.
- El modo CRUD guarda el cuerpo tal cual: los esquemas `esquema-usuario-*` del data bucket impiden guardar usuarios incompletos o con campos de más.
- El helper `eq` compara también el tipo: usa `parseInt (urlParam 'id')` para comparar con un id numérico.
- `POST /api/test/reset` existe porque Desktop genera un token de administración nuevo en cada inicio, así que `/mockoon-admin/data-buckets/purge` no sirve a la suite. Copia el bucket `usuarios-iniciales`, que no debe modificarse, con `jsonParse (data ...)` para no compartir la referencia.
- El retardo de `api/usuarios/lento` está en `latency` y `retardo_ms`, y debe coincidir con `SLOW_ENDPOINT_DELAY_MS`.

## Git

Si `git rev-parse --show-toplevel` devuelve `C:/Users/ricar`, esta carpeta aún no tiene repositorio propio: el detectado abarca todo el home, incluidos `.ssh/` y `.claude.json`. En ese caso no ejecutes `git add -A`, `git commit -a` ni `git clean`; primero hay que ejecutar `git init` en esta carpeta.
