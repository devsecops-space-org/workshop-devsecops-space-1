---
name: self-review
description: >
  Auto-revisión pre-PR para agentes ATDD. Contiene las mismas checklists
  que code-review.instructions.md organizadas por fase (planner, developer,
  tester). El agente verifica su propio output antes de abrir el PR.
  Patrón inspirado en quality-playbook Phase 3: Verify.
---

# Self-Review — Auto-revisión Pre-PR

Antes de abrir el PR, el agente relee su propio output y verifica la
checklist de su fase. Si algún item falla, corrige y re-verifica hasta
que pase limpia. Solo entonces procede al PR.

> **Origen**: Estas checklists son idénticas a las de
> `instructions/code-review.instructions.md`. Si las reglas de review
> cambian, actualizar ESTE archivo para que los agentes hereden el cambio.
>
> **Patrón**: Inspirado en
> [quality-playbook Phase 3: Verify](https://github.com/github/awesome-copilot/tree/main/skills/quality-playbook)
> del repo `github/awesome-copilot`.

---

## Fase 1 — Planner (archivos .feature)

Aplica después de generar los `.feature` y antes de abrir el PR `[ATDD]`.

- [ ] Header `# language: es` presente en cada archivo.
- [ ] Sin HTTP, JSON, status codes ni detalles técnicos — solo comportamiento
      de negocio.
- [ ] Steps parametrizados con `<variables>` y `Esquema del escenario` +
      `Ejemplos`.
- [ ] Comillas en el step (`"<var>"`), valores limpios en tabla `Ejemplos`
      (sin comillas en celdas).
- [ ] Nombres/categorías de escenarios en español: `Flujo principal`,
      `Validación`, `Caso límite`, `Seguridad`.
- [ ] Máximo 7 pasos por escenario.
- [ ] Cobertura mínima: ≥1 flujo principal, ≥2 validación, ≥1 caso límite,
      ≥1 seguridad.
- [ ] Fechas y datos temporales usan placeholders o centinelas estables
      (`2099-06-01`, `2000-01-01`) cuando el día exacto no es contractual.
- [ ] Los ejemplos del Issue se usaron como referencia de dominio, no como
      literales obligatorios cuando vuelven frágil el contrato.
- [ ] Mismo paso de negocio = mismo texto exacto en todos los escenarios.
- [ ] La misma familia de step mantiene la misma firma de parámetros en todos
      los escenarios; no aparecen variantes opcionales aisladas.

### Scope permitido

Solo archivos `.feature` en `tests/features/`.

---

## Fase 2 — Developer (src/ + tests/step_defs/)

Aplica después de pasar `ruff check`, `ruff format --check`, `bandit` y
`pytest`, y antes de abrir el PR `[IMPL]`.

> **OBLIGATORIO**: Ejecuta los 4 comandos y confirma exit code 0 ANTES de
> revisar esta checklist. La revisión mental NO sustituye la ejecución real
> de las herramientas (ej: una línea de 101 chars no se detecta a ojo).

### Código Python (src/)

- [ ] Type hints en parámetros Y retorno de cada función. No `Any`.
- [ ] Imports ordenados: stdlib → third-party → local.
- [ ] Line length ≤ 100 caracteres.
- [ ] Modelos Pydantic v2: `BaseModel` + `Field`, request y response separados.
- [ ] Pydantic `Field(pattern=...)` semánticamente estricto: `HH:MM` usa
      `^(?:[01]\d|2[0-3]):[0-5]\d$`, no `^\d{2}:\d{2}$`.
- [ ] Dict de storage tipado internamente: `dict[str, MiTypedDict]`, no
      `dict[str, dict]`.
- [ ] Services: funciones puras, `ValueError` para errores de negocio.
- [ ] Endpoints: prefijo `/api/v1/`, `response_model` explícito,
      `ValueError` → `HTTPException`.
- [ ] Sin lógica de negocio en endpoints — delega a services.
- [ ] Sin `eval`, `exec`, `pickle`, `subprocess(shell=True)`, ni secretos
      hardcodeados.
- [ ] `KeyError` en endpoints usa `e.args[0]` como `detail`, no `str(e)`
      (evita comillas extra en el mensaje de error).
- [ ] Mensajes de error usan constantes (`HORA_INICIO_LABORAL`, etc.),
      no valores hardcodeados que se desactualicen si la constante cambia.
- [ ] Si el storage es en memoria: endpoint `POST /api/v1/_reset` expuesto
      para que tests funcionales puedan limpiar estado.

### Tests BDD (tests/step_defs/)

- [ ] Usa `scenarios()` para importar todos los escenarios del `.feature`.
- [ ] Usa `parsers.parse` para parametrización de steps.
- [ ] Cada step del `.feature` tiene su step definition correspondiente.
- [ ] Steps con datatable aceptan parámetro `datatable` y validan sus
      valores contra constantes esperadas (no solo reciben y pasan).
- [ ] Datatable tipado como `list[list[str]]` (NO `list[dict]` ni
      `list[TypedDict]`). Acceso con `datatable[1:]` + `fila[0]`, `fila[1]`.
- [ ] Aserciones de rechazo usan rango 4xx: `400 <= status_code < 500`,
      no `status_code >= 400`.
- [ ] Usa fixture `client` (TestClient) — no instancia la app directamente.
- [ ] No modifica archivos `.feature` aprobados.

### Scope permitido

Solo `src/main.py`, `src/models.py`, `src/services.py` y
`tests/step_defs/test_<dominio>_steps.py`.

---

## Fase 3 — Tester (tests/functional/)

Aplica después de pasar `ruff check` y `ruff format --check`, y antes de
abrir el PR `[TEST]`.

- [ ] Usa fixture `api_client` (httpx) y `context` (dict) del `conftest.py`.
- [ ] No hardcodea URLs — usa la fixture `api_client`.
- [ ] Cada escenario del `.feature` tiene todos sus steps funcionales.
- [ ] Los `Given` funcionales crean o verifican precondiciones reales vía
      HTTP; no son noops.
- [ ] Los `Given` negativos ("que no existen X") limpian estado: listar
      recursos (GET), eliminar cada uno (DELETE), verificar vacío (GET + assert).
      NUNCA solo assertar vacío sin limpiar.
- [ ] Si usa `_reset` para limpiar: tras POST _reset, verificar con GET
      que la lista quedó vacía antes de retornar al happy path.
- [ ] En fallback GET+DELETE: assertar status code (200/204) de cada DELETE
      individual, no solo del GET final.
- [ ] Check-before-create filtra por TODOS los campos relevantes del Given
      (fecha + hora_inicio + hora_fin + propósito), no un subconjunto.
- [ ] Datatable: validar header row, detectar duplicados, verificar
      completitud del set esperado (no solo que cada fila sea correcta).
- [ ] Datatable tipado como `list[list[str]]`. Si usa `row["col"]` en vez
      de `fila[0]`, corregir — pytest-bdd nunca entrega diccionarios.
- [ ] Los datos auxiliares no usan fechas cercanas al presente salvo que el
      contrato exija ese día exacto.
- [ ] `context` no guarda claves sin uso posterior.
- [ ] Los filtros/parámetros de consulta se validan sobre el payload, no solo
      con status code.
- [ ] Respuestas de creación/consulta verifican TODOS los campos del payload
      enviado, no solo `id` o status code.
- [ ] Status codes en aserciones alineados con los que devuelve `src/main.py`
      (ej: conflicto → 409, no solo 400/422).
- [ ] No modifica `tests/step_defs/`, `tests/conftest.py`, ni `src/`.

### Scope permitido

Solo archivos en `tests/functional/`.

---

## Protocolo de corrección

Si algún item de la checklist falla:

1. Corrige el problema en el archivo correspondiente.
2. Re-ejecuta los checks técnicos de tu fase (lint/format/bandit/pytest).
3. Vuelve a verificar la checklist completa desde el inicio.
4. Solo procede al PR cuando **todos** los items pasen.
