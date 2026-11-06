# Estrategia de ramas

Esta guía simula la colaboración entre tres QA Automation Engineers. Los roles son didácticos: cada commit debe llevar la identidad real de quien lo hace, sin usar nombres ni correos ajenos.

## Ramas

| Rama | Responsable | Alcance |
|---|---|---|
| `main` | Todo el equipo | Código revisado, con el workflow en verde |
| `feature/api-crud` | QA 1 | GET, POST, PUT, PATCH y DELETE |
| `feature/api-auth` | QA 2 | Login, Bearer Token, API Key, 401 y 403 |
| `feature/api-errors` | QA 3 | Errores HTTP y timeouts |

```text
main ───●──────────────●──────────●──────────●───
         \            /          /          /
          ├─ feature/api-crud ──┘          /
          ├─ feature/api-auth ────────────┘
          └─ feature/api-errors ──────────┘
```

## Crear una rama

Parta siempre de un `main` actualizado:

```powershell
git switch main
git pull
git switch -c feature/api-crud
```

## Commits

Use commits pequeños con un solo propósito y el formato `tipo: descripción`:

| Tipo | Uso | Ejemplo |
|---|---|---|
| `feat` | Funcionalidad o pruebas nuevas | `feat: add API key tests` |
| `fix` | Corrección | `fix: use exact token comparison in mock` |
| `test` | Cambios en pruebas existentes | `test: validate 422 error messages` |
| `docs` | Documentación | `docs: describe timeout scenarios` |
| `ci` | Workflow | `ci: validate mock before starting it` |
| `chore` | Mantenimiento | `chore: update pinned dependencies` |

Antes de cada commit:

```powershell
git status
git diff
python -m pytest -v
```

No versione `.env`, reportes generados ni credenciales reales.

## Pull requests

1. Publique la rama: `git push -u origin feature/api-crud`.
2. Abra el pull request hacia `main`. La plantilla está en `.github/pull_request_template.md`.
3. Espere a que el workflow `API Tests` termine en verde.
4. Pida la revisión de otro integrante.

Mantenga cada pull request acotado a su rama. Un cambio ajeno a su alcance va en otro pull request.

## Code review

Quien revisa comprueba que:

- Las pruebas validan el comportamiento, y fallarían si este se rompe.
- Los casos negativos comprueban el código y el mensaje de error.
- Los datos están en `data/` y las aserciones comunes en `utils/validators.py`.
- Las solicitudes usan Playwright, sin Requests, Selenium ni `time.sleep()`.
- Toda prueba lleva `regression` y los marcadores que le correspondan.
- El README coincide con el cambio y solo muestra resultados reales.

Quien hace la revisión comenta con un motivo concreto. Quien abrió el pull request responde a cada comentario y no aprueba su propio trabajo.

## Conflictos

Los conflictos más probables están en los archivos compartidos: `tests/conftest.py`, `data/usuarios.py` y `mocks/usuarios-api.json`.

Actualice su rama con `main` y resuélvalos en local:

```powershell
git switch feature/api-auth
git fetch origin
git merge origin/main
# Edite los archivos en conflicto y conserve los cambios de ambas ramas que correspondan
git add tests/conftest.py
git commit
```

Después valide el resultado:

```powershell
npx @mockoon/cli@9.10.0 validate --data .\mocks\usuarios-api.json
python -m pytest -v
git push
```

En `mocks/usuarios-api.json`, compruebe además que `lento`, `999` y DELETE sigan antes de la ruta CRUD, y que `rootChildren` contenga cada ruta. Si el conflicto es grande, puede ser más seguro aplicar los cambios de nuevo desde Mockoon Desktop.

No use `git push --force` sobre una rama compartida.

## Merge

Se hace cuando el workflow está en verde, hay una aprobación y no quedan conversaciones abiertas.

Se recomienda **Squash and merge**, para dejar en `main` un commit por pull request con un mensaje en el formato anterior. Después, borre la rama y actualice su copia:

```powershell
git switch main
git pull
git branch -d feature/api-crud
```

## Protección de main

Esto se configura en GitHub, en **Settings > Branches > Add branch protection rule**, para el patrón `main`:

- **Require a pull request before merging**, con al menos una aprobación.
- **Dismiss stale pull request approvals when new commits are pushed**.
- **Require status checks to pass before merging**, con el check `api-tests`.
- **Require branches to be up to date before merging**.
- **Require conversation resolution before merging**.
- **Do not allow bypassing the above settings**.
- Mantener desactivados los force push y el borrado de la rama.

Con una sola persona en el repositorio, exigir una aprobación impide hacer el merge, porque GitHub no permite aprobar un pull request propio. En ese caso, exija solo el pull request y el check.

Según el plan de GitHub y la visibilidad del repositorio, algunas opciones pueden no estar disponibles.

## Estado de este repositorio

Los primeros commits de la POC se hicieron directamente en `main`, antes de que existieran estas ramas. La regla se aplica desde entonces. La protección de `main` queda documentada, pero no está activada.
