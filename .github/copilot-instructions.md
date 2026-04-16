# Instrucciones para Copilot Coding Agent

## Resumen del Proyecto

Repositorio template para flujos ATDD agénticos con 3 fases automatizadas:
1. **Planificador** genera escenarios Gherkin desde Issues.
2. **Desarrollador** implementa código FastAPI que cumple los escenarios.
3. **Tester** genera tests funcionales con httpx contra la API desplegada.

## Convenciones Globales

- **Stack**: Python 3.11+ / FastAPI / Pydantic v2 / pytest-bdd.
- Feature files en español (`# language: es`).
- Type hints obligatorios (parámetros + retorno). No `Any`.
- Pydantic v2 para models (`BaseModel`, `Field`).
- Line length ≤ 100. Imports: stdlib → third-party → local.
- Almacenamiento en memoria (`dict`), no base de datos.

## Layout del Proyecto

```
src/
├── main.py          # FastAPI app + endpoints (prefijo /api/v1/)
├── models.py        # Modelos Pydantic v2 (request y response separados)
└── services.py      # Lógica de negocio + storage en memoria (dict)
tests/
├── conftest.py      # Fixtures: client (TestClient)
├── features/        # .feature aprobados (contratos Gherkin)
├── step_defs/       # Step definitions BDD (pytest-bdd)
└── functional/
    ├── conftest.py  # Fixtures: api_client (httpx), context (dict)
    └── *.py         # Tests funcionales contra API real
```

## Comandos de Validación

Ejecuta siempre en este orden antes de pushear. Todos deben pasar sin errores:

```bash
pip install -r requirements.txt -r requirements-dev.txt  # solo si primer setup
ruff check src/ tests/                                    # lint
ruff format --check src/ tests/                           # formato
bandit -r src/                                            # seguridad
pytest tests/ -v --tb=short --strict-markers              # tests BDD
```

## Restricciones Globales

- No instales dependencias nuevas.
- No modifiques `.github/workflows/` ni `.github/CODEOWNERS`.
- No crees endpoints no solicitados. No modifiques `.feature` aprobados.

## CI Pipeline (`.github/workflows/ci.yml`)

El CI ejecuta estos jobs en PRs `[IMPL]`. Tu código DEBE pasar todos:

1. **scope-check**: Verifica que solo se modificaron archivos permitidos.
2. **lint**: `ruff check` + `ruff format --check` en `src/` y `tests/`.
3. **security**: `bandit -r src/` sin hallazgos.
4. **test-bdd**: `pytest tests/ -v --strict-markers` con 0 fallos.
5. **gate**: Requiere que todos los anteriores pasen para merge.

---

## Determinación de Rol

- Label **`agentic-mission`** → **PLANIFICADOR** (Fase 1).
- Label **`agentic-implementation`** o título `[IMPL]` → **DESARROLLADOR** (Fase 2).
- Label **`agentic-testing`** o título `[TEST]` → **TESTER** (Fase 3).
- Revisión en PR `[IMPL]` → DESARROLLADOR corrigiendo.
- Revisión en PR `[TEST]` → TESTER corrige manualmente según feedback humano/CI.

Las instrucciones detalladas de cada fase están en el agent profile
correspondiente (`agent-planner`, `agent-developer`, `agent-tester`).
A continuación, un resumen compacto como referencia rápida.

---

## Fase 1: PLANIFICADOR (resumen)

Solo `.feature` en `tests/features/`. Sin código Python.
Branch: `atdd/<dominio>-scenarios`. PR: `[ATDD] Escenarios para: <título>`.
Cobertura: ≥1 flujo principal, ≥2 validación, ≥1 caso límite, ≥1 seguridad.

---

## Fase 2: DESARROLLADOR (resumen)

Modifica: `src/main.py`, `src/models.py`, `src/services.py`.
Crea: `tests/step_defs/test_<dominio>_steps.py`.
Branch: `impl/<dominio>-implementation`. PR: `[IMPL] <título>`.
Checks: `ruff check` + `ruff format --check` + `bandit -r src/` + `pytest`.

---

## Fase 3: TESTER (resumen)

Crea: `tests/functional/test_<dominio>_functional.py`.
Branch: `test/<dominio>-functional`. PR: `[TEST] <título>`.
Checks: `ruff check tests/functional/` + `ruff format --check tests/functional/`.
