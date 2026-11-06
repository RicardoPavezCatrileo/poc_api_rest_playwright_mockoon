## Qué cambia y por qué

<!-- Describa el cambio y el motivo. -->

## Tipo de cambio

- [ ] Pruebas nuevas o modificadas
- [ ] Mock (`mocks/usuarios-api.json`)
- [ ] Framework (clientes, fixtures, validadores o configuración)
- [ ] Workflow de CI
- [ ] Documentación

## Cómo se probó

<!-- Pegue solo resultados reales. Indique con qué servidor se ejecutó: Mockoon Desktop o CLI. -->

```text
python -m pytest -v
```

## Lista de comprobación

- [ ] La suite pasa en local y el workflow `API Tests` está en verde.
- [ ] Las solicitudes usan Playwright, sin Requests, Selenium ni `time.sleep()`.
- [ ] Toda prueba nueva lleva `regression` y sus marcadores específicos.
- [ ] Si cambió el mock, `mockoon-cli validate` no da errores y el orden de las rutas sigue siendo correcto.
- [ ] No se incluyen `.env`, reportes generados ni credenciales reales.
- [ ] El README y `docs/` reflejan el cambio.

## Notas para la revisión

<!-- Decisiones, riesgos o partes que conviene revisar con más atención. -->
