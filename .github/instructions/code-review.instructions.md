---
applyTo: "**"
---

# Code Review para Copilot

Responde en **español**.

## Prioridades de Revisión

### 🔴 CRÍTICO (Bloquea merge)
- **Seguridad**: Vulnerabilidades, secretos expuestos, `eval/exec/pickle/subprocess(shell=True)`.
- **Correctitud**: Errores lógicos, corrupción de datos, race conditions.
- **Contrato roto**: Código que incumple escenarios `.feature` aprobados.
- **Ruptura de API**: Cambios en contratos de endpoints sin versionar.
- **Contrato temporal roto**: Tests que alteran fecha/horario del `.feature` para hacerlo pasar.

### 🟡 IMPORTANTE (Requiere discusión)
- **Cobertura de tests**: Steps faltantes para escenarios aprobados.
- **Validación**: Inputs validados manualmente en lugar de Pydantic declarativo.
- **Arquitectura**: Lógica de negocio en endpoints (va en `services.py`).
- **Performance**: Operaciones O(n²) evitables, iteraciones innecesarias.
- **Determinismo funcional**: `Given` noop, fechas auxiliares cercanas al presente, validaciones que asumen filtros del backend.

### 🟢 SUGERENCIA (No bloquea)
- **Legibilidad**: Nombres poco descriptivos, lógica compleja sin simplificar.
- **Convenciones**: Desviaciones menores de estilo (line length, imports).
- **Documentación**: Docstrings faltantes en funciones públicas.
- **Estado muerto en tests**: claves en `context` escritas pero nunca leídas.

## Checklist por Área

### Código Python (src/)
- Type hints en parámetros y retorno. No `Any`.
- Imports ordenados: stdlib → third-party → local.
- Line length ≤ 100.
- Pydantic v2: `BaseModel` + `Field`, request/response separados.
- Pydantic `Field(pattern=...)` semánticamente estricto: `HH:MM` debe usar `^(?:[01]\d|2[0-3]):[0-5]\d$`, no `^\d{2}:\d{2}$`.
- Dict de storage tipado internamente: `dict[str, MiTypedDict]`, no `dict[str, dict]`.
- Services: funciones puras, `ValueError` para errores de negocio.
- Endpoints: prefijo `/api/v1/`, `response_model` explícito, `ValueError` → `HTTPException`.
- Sin lógica de negocio en endpoints.
- Sin `eval`, `exec`, `pickle`, `subprocess(shell=True)`, ni secretos hardcodeados.
- `KeyError` en endpoints usa `e.args[0]` como `detail`, no `str(e)`.
- Mensajes de error usan constantes, no valores hardcodeados.
- Endpoint `_reset` (POST /api/v1/_reset) expuesto cuando storage es en memoria.

### Tests BDD (tests/step_defs/)
- Usa `scenarios()` para importar escenarios.
- Usa `parsers.parse` para parametrización.
- Cada step tiene su step definition.
- Steps con datatable DEBEN aceptar parámetro `datatable` y validar sus valores contra constantes esperadas.
- Datatable tipado como `list[list[str]]` (NO `list[dict]`). Acceso: `datatable[1:]` + `fila[0]`, `fila[1]`.
- Aserciones de rechazo usan rango 4xx: `400 <= status_code < 500`, no `status_code >= 400`.
- Usa fixture `client` (TestClient), no instanciar app.
- No modifica `.feature` aprobados.

### Tests Funcionales (tests/functional/)
- Usa fixtures `api_client` y `context` del `conftest.py`.
- No hardcodear URLs; usa `api_client`.
- Cada escenario tiene todos sus steps funcionales.
- `Given` crean/verifican precondiciones vía HTTP; no noops.
- `Given` negativos ("no existen X") limpian estado (GET + DELETE cada uno + assert vacío); no solo verifican.
- Si usa `_reset`: tras POST, verificar con GET que la lista quedó vacía.
- En fallback GET+DELETE: assertar status code (200/204) de cada DELETE individual.
- Check-before-create filtra por TODOS los campos relevantes del Given.
- Datatable: validar header, detectar duplicados, verificar completitud del set.
- Datatable tipado como `list[list[str]]`. Si usa `row["col"]` en vez de `fila[0]`, es bug (`TypeError` en runtime).
- Respuestas de creación/consulta verifican TODOS los campos del payload enviado, no solo `id` o status code.
- Status codes en aserciones alineados con los que devuelve `src/main.py` (ej: conflicto = 409, no solo 400/422).
- Datos auxiliares sin fechas cercanas al presente salvo contrato.
- `context` no guarda claves sin uso posterior.
- Filtros se validan sobre el payload, no solo status code.
- No modifica `tests/step_defs/`, `tests/conftest.py`, ni `src/`.

### Archivos .feature
- Header `# language: es` presente.
- Sin HTTP/JSON/status codes — solo comportamiento de negocio.
- Steps con `<variables>`, `Esquema del escenario` + `Ejemplos`.
- Comillas en step (`"<var>"`), sin comillas en celdas de `Ejemplos`.
- Categorías/nombres de escenarios en español: `Flujo principal`, `Validación`, `Caso límite`, `Seguridad`.
- Máximo 7 pasos por escenario.
- Cobertura: ≥1 flujo principal, ≥2 validación, ≥1 caso límite, ≥1 seguridad.
- Fechas usan centinelas estables si el día no es contractual.
- Ejemplos del Issue como referencia, no literales frágiles.
- Mismo paso de negocio = mismo texto exacto en todos los escenarios.
- Misma familia de step = misma firma de parámetros en todos los escenarios.

## Scope de PRs

- **`[ATDD]`**: Solo `.feature` en `tests/features/`.
- **`[IMPL]`**: Solo `src/main.py`, `src/models.py`, `src/services.py`, y `tests/step_defs/`.
- **`[TEST]`**: Solo archivos en `tests/functional/`.
- Ningún PR modifica `.github/workflows/`, `.github/CODEOWNERS`, `requirements*.txt`.

## Formato: `**[🔴|🟡|🟢] Categoría: Título** — Descripción. **Por qué importa:** impacto. **Corrección sugerida:** código.`
