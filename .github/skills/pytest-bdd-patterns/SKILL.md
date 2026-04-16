---
name: pytest-bdd-patterns
description: >
  Patrones para step definitions con pytest-bdd en proyectos FastAPI.
  Cubre scenarios(), parsers.parse(), fixtures, separación unitario/funcional,
  y convenciones por dominio. Usar cuando se creen o modifiquen step definitions
  en tests/step_defs/ o tests/functional/.
---

# Patrones pytest-bdd

## Cuándo aplicar

- Al crear step definitions en `tests/step_defs/test_<dominio>_steps.py` (unitarios).
- Al crear step definitions en `tests/functional/test_<dominio>_functional.py` (funcionales).
- Al revisar archivos de test que usen pytest-bdd.

## Reglas

### Estructura de archivos

- Un archivo de steps por dominio: `test_<dominio>_steps.py` o `test_<dominio>_functional.py`.
- Cada archivo comienza con `scenarios("../features/<dominio>.feature")`.
- Agrupa steps en orden: `@given` → `@when` → `@then`.

### Registro de escenarios

```python
from pytest_bdd import scenarios

scenarios("../features/<dominio>.feature")
```

No uses `@scenario` individual salvo que necesites un setup específico por escenario.

### Parametrización de steps

- Usa `parsers.parse()` para steps con parámetros:

```python
from pytest_bdd import given, parsers

@given(parsers.parse('un recurso "{nombre}" con categoría "{categoria}"'))
def crear_recurso(client, nombre: str, categoria: str) -> None:
    ...
```

- Para valores numéricos usa `{codigo:d}` (int) o `{monto:f}` (float).
- Evita regex (`parsers.re(...)`) salvo que `parsers.parse()` sea insuficiente.

### Fixtures

#### Tests unitarios (`tests/step_defs/`)

- `client`: `TestClient(app)` — ejecuta la API in-process.
- Definida en `tests/conftest.py` — **no la redeclares**.
- **Cleanup**: El template NO incluye fixture de cleanup automático. DEBES
  crear una fixture `autouse` en tu archivo de steps que llame a `_reset()`
  de services antes y después de cada test.

```python
from collections.abc import Generator

@pytest.fixture(autouse=True)
def _limpia_estado() -> Generator[None, None, None]:
    _reset()
    yield
    _reset()
```

#### Tests funcionales (`tests/functional/`)

- `api_client`: `httpx.Client(base_url=...)` — ejecuta HTTP real contra API desplegada.
- `context`: `dict` limpio por test para compartir estado entre steps.
- Ambas definidas en `tests/functional/conftest.py` — **no las redeclares**.

### Diferencia clave: unitario vs funcional

| Aspecto | Unitario (`step_defs/`) | Funcional (`functional/`) |
|---|---|---|
| Cliente | `TestClient` (in-process) | `httpx.Client` (HTTP real) |
| Servidor | No necesita servidor | Requiere API desplegada |
| Qué valida | Lógica de negocio | Integración completa |
| Cuándo corre | CI en cada PR | Post-deploy en Codespace |
| Fixture principal | `client` | `api_client` + `context` |

Ambos usan los **mismos `.feature`** como fuente de verdad.

### Compartir estado entre steps

- En unitarios: usa variables locales del módulo o fixtures personalizadas.
- En funcionales: usa la fixture `context` (dict) para guardar responses y datos.

```python
@when("se consultan todos los recursos")
def consultar_recursos(api_client, context) -> None:
    response = api_client.get("/api/v1/recursos")
    context["last_response"] = response
```

### Determinismo en tests funcionales

- Cada `@given` funcional debe crear o verificar la precondición vía HTTP
  cuando la API lo permita; no uses steps noop que solo documenten una
  asunción de entorno.
- **Given positivo** ("que existe X"): check-before-create — verificar si ya
  existe en la API antes de crear, para ser idempotente.
- **Given negativo** ("que no existen X"): purge-then-assert — listar todos
  los recursos vía GET, eliminar cada uno individualmente vía DELETE (o usar
  `_reset` si disponible), y verificar que la lista quedó vacía.
  NUNCA solo assertar vacío sin limpiar.
- Si el `.feature` fija una fecha, sala u horario exactos, respétalos en la
  implementación; no cambies el slot dinámicamente para hacer pasar el
  escenario.
- Para datos auxiliares que no forman parte del comportamiento observado, usa
  fechas estables y lejanas como `2099-06-01` o `2000-01-01`.
- Guarda en `context` solo claves que luego serán leídas por otro step o
  helper compartido.
- Si un step usa filtros o parámetros de consulta, valida también el payload
  retornado; no asumas que el backend aplicó el filtro solo porque respondió
  `200`.

## Gotchas

- `scenarios()` debe llamarse a nivel de módulo (top-level), no dentro de una función.
- Si un step del `.feature` no tiene su definición, pytest-bdd da `StepImplementationNotFound` — verifica que TODOS los steps estén implementados.
- `parsers.parse()` es sensible al formato exacto: `"{param}"` con comillas en el `.feature` debe coincidir con `'"{param}"'` en el decorator.
- **Comillas en `Esquema del escenario`**: cuando un step usa `"<placeholder>"`, la tabla `Ejemplos` debe llevar valores **sin comillas** (`10:00`, no `"10:00"`). Si la celda incluye comillas, `parsers.parse` recibe comillas dobles y falla el match.
- **Datatable es `list[list[str]]`**: pytest-bdd entrega las tablas Gherkin como lista de listas de strings. La fila 0 son headers. Acceder con `row["col"]` produce `TypeError`. Usar `datatable[1:]` para iterar filas de datos y `fila[0]`, `fila[1]` para acceder a columnas.
- En funcionales, un `@given` vacío o puramente documental suele introducir
  flakiness porque depende del estado desplegado.
- `strict-markers` en `pytest.ini`/`pyproject.toml` requiere que `@pytest.mark.parametrize` no se mezcle con `scenarios()` — usa `Esquema del escenario` + `Ejemplos` en el `.feature` en su lugar.

## Anti-patrones

| Anti-patrón | Por qué es un problema | Corrección |
|---|---|---|
| Redeclarar fixture `client` en el archivo de steps | Oculta la fixture de conftest | Usar la de `conftest.py` |
| Steps con lógica de negocio | Steps deben ser delegación, no implementación | Delegar a `client.post/get` |
| Copiar steps entre archivos de dominio | Duplicación que diverge | Mover steps comunes a `conftest.py` |
| Usar `@scenario` para cada escenario | Verboso y error-prone | Usar `scenarios()` una vez |
| No verificar todos los steps del `.feature` | Test pasa vacío (sin steps) | Contar steps vs definitions |
| Tipar datatable como `list[dict]` o `list[TypedDict]` | pytest-bdd entrega `list[list[str]]`; acceso `row["col"]` → `TypeError` | Usar `datatable[1:]` + `fila[0]`, `fila[1]` |
| `@given` noop que solo asume estado | Depende del entorno desplegado y genera flakiness | Crear o verificar la precondición vía HTTP |
| Fechas cercanas al presente en datos auxiliares | El test envejece y falla por calendario | Usar fechas estables y lejanas o cálculo relativo |
| `context["clave"]` escrita pero nunca leída | Estado muerto que complica el mantenimiento | Eliminar la clave o usarla explícitamente |
| Confiar en un filtro GET solo por el status code | Un bug de filtrado puede pasar desapercibido | Verificar los campos del payload además del status |
| Comillas en celdas de `Ejemplos` en `Esquema del escenario` | `parsers.parse` recibe `""valor""` y no matchea | Comillas en el step (`"<var>"`), valor limpio en celda |
