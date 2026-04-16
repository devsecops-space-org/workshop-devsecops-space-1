---
applyTo: "tests/**/*.py"
---

# Reglas para tests (tests/)

## Tests BDD — tests/step_defs/
- Usar `scenarios()` para importar escenarios desde el `.feature`.
- Usar `parsers.parse` para parametrización: `@given(parsers.parse('...'))`.
- Fixture `client` (TestClient) del `conftest.py` — no instanciar app directamente.
- El template NO incluye fixture de cleanup. Crear una `autouse` que llame
  `_reset()` antes y después de cada test (ver pytest-bdd-patterns skill).
- Datatable tipado como `list[list[str]]` (NO `list[dict]`). Acceso:
  `datatable[1:]` + `fila[0]`, `fila[1]`.
- Un archivo por dominio: `test_<dominio>_steps.py`.
- NUNCA modificar archivos `.feature` aprobados.

## Tests Funcionales — tests/functional/
- Fixtures disponibles en `tests/functional/conftest.py`:
  - `api_client`: `httpx.Client` con `base_url` configurado.
  - `context`: `dict` limpio por test para compartir estado entre steps.
  - `base_url`: URL de la API desplegada (vía `--base-url`).
- Cada `Dado` funcional debe crear o verificar la precondición vía HTTP cuando
  la API lo permita; no usar steps noop que solo documenten una asunción de
  entorno.
- `Dado` negativos ("que no existen X") deben limpiar estado: listar recursos
  (GET), eliminar cada uno (DELETE), verificar vacío. No solo assertar vacío.
- `Dado` positivos ("que existe X") deben ser idempotentes: verificar si ya
  existe antes de crear (check-before-create).
- Si el `.feature` fija una fecha, sala u horario exactos, respétalos; no los
  cambies dinámicamente para hacer pasar el escenario.
- Para datos auxiliares no observables por el usuario, usar fechas estables y
  lejanas (por ejemplo `2099-06-01` para futuro).
- Guardar en `context` solo claves que se leerán en steps o helpers
  posteriores.
- Al probar filtros o parámetros de consulta, validar también el payload
  retornado; no asumir que el backend aplicó el filtro solo por responder 200.
- NUNCA hardcodear URLs.
- NUNCA modificar `tests/step_defs/`, `tests/conftest.py`, ni `src/`.
- NO ejecutar los tests localmente (requieren API desplegada).

## Convenciones generales
- Type hints en parámetros y retorno.
- Imports: stdlib → third-party → local.
- Line length ≤ 100.
- Sin imports no utilizados. Sin código comentado.
