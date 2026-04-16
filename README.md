# Agentic CI Template — Flujo ATDD con Copilot Coding Agent

Template de referencia para ejecutar un flujo agéntico gobernado en GitHub:
el humano define la intención, Copilot propone e implementa cambios acotados,
y GitHub Actions actúa como barrera de control.

## Importante

Este repositorio está pensado como **template**.

- No deberías operar el flujo directamente sobre este repo base.
- Para cada nuevo caso de uso, crea un **repositorio nuevo usando este template**.
- Las ejecuciones reales, Issues, PRs, labels, secrets y workflows deben vivir en ese repo nuevo.

## Dominio de la demo: API de reservas de salas

Este template incluye un dominio de ejemplo concreto para facilitar la
demo del flujo agéntico ATDD: una **API de reservas de salas de reunión**.

El dominio se eligió porque:

- Es universalmente comprensible (cualquier persona en una empresa lo entiende).
- Tiene reglas de negocio naturales y ricas (solapamientos, capacidades,
  validaciones de horario) que se traducen directamente en escenarios Gherkin.
- La complejidad técnica es baja (CRUD en memoria), pero la lógica de
  validación es suficiente para mostrar el valor del agente desarrollador.

> El dominio es solo el vehículo. Lo importante es el **flujo agéntico
> gobernado**: humano define la intención, agentes ejecutan, CI valida,
> humano aprueba.

Los recursos del dominio (modelo, endpoints, reglas de negocio) se
generarán por el flujo agéntico en vivo durante el workshop, a partir
del Issue de demo (ver sección "Demo de referencia: cómo iniciar el flujo").

## Qué hace este template

- Planeación basada en **ATDD**: primero escenarios, luego implementación.
- Separación de responsabilidades por agente:
  - `agent-planner`
  - `agent-developer`
  - `agent-tester`
- Validación automática con CI:
  - alcance de cambios
  - lint y formato
  - seguridad
  - tests BDD
  - tests funcionales post-deploy
- Control humano obligatorio antes del merge.

## Flujo de alto nivel

```text
Issue creado por humano en repo nuevo
  -> label agentic-mission
  -> workflow agentic-plan.yml
  -> Copilot (agent-planner)
  -> PR [ATDD] con archivos .feature
  -> aprobación humana
  -> merge a main
  -> workflows agentic-develop.yml + agentic-test.yml
  -> Issue [IMPL] + Issue [TEST]
  -> Copilot implementa en paralelo
  -> PR [IMPL] y PR [TEST]
  -> CI + review + self-correction
  -> aprobación humana
  -> merge a main
  -> preview.yml + functional-tests.yml
```

## Qué debes hacer primero en un repositorio nuevo

### 1. Crear el repositorio desde el template

1. En GitHub, usa **Use this template** sobre este repositorio.
2. Crea un repo nuevo, por ejemplo: `workshop-devsecops-space-1`.
3. Trabaja siempre sobre ese repo nuevo.

### 2. Confirmar que Copilot Coding Agent esté habilitado

Necesitas que la organización o cuenta tenga habilitado Copilot Coding Agent y
que el repo nuevo pueda asignar a `copilot-swe-agent[bot]`.

### 3. Tener disponibles los perfiles custom de agentes

Este template asume que existe un repositorio `.github-private` con perfiles como:

- `agents/agent-planner.agent.md`
- `agents/agent-developer.agent.md`
- `agents/agent-tester.agent.md`

Sin esos perfiles, la asignación automática puede fallar o usar una configuración
distinta a la esperada.

### 4. Crear los labels del repositorio

Debes crear estos labels en el repo nuevo antes de ejecutar el flujo:

| Label | Uso | Obligatorio |
|---|---|---|
| `agentic-mission` | Dispara la planificación inicial | Sí |
| `agentic-implementation` | Se usa al crear el Issue de implementación | Sí |
| `agentic-testing` | Se usa al crear el Issue de testing funcional | Sí |
| `needs-human-review` | Escalación cuando el loop no converge | Recomendado |

Notas:

- `needs-human-review` puede crearse automáticamente en la primera escalación,
  pero conviene dejarlo creado desde el inicio.
- Si `agentic-implementation` o `agentic-testing` no existen, la creación de los
  Issues derivados puede fallar.

Ejemplo con GitHub CLI:

```bash
gh label create agentic-mission --color 2563eb --description "Dispara la fase de planificación"
gh label create agentic-implementation --color 16a34a --description "Issue o PR de implementación"
gh label create agentic-testing --color f59e0b --description "Issue o PR de testing funcional"
gh label create needs-human-review --color e11d48 --description "Requiere intervención humana"
```

### 5. Configurar secrets

| Secret | Uso | Obligatorio |
|---|---|---|
| `AGENT_PAT` | Asignar Copilot, comentar en PRs, pasar draft a ready | Sí |
| `CODESPACE_PAT` | Crear/eliminar Codespaces para `preview.yml` | Sí, si usarás preview |

Notas sobre `AGENT_PAT`:

- El template lo usa en:
  - `agentic-plan.yml`
  - `agentic-develop.yml`
  - `agentic-test.yml`
  - `agentic-ready-for-review.yml`
  - `agentic-self-correct.yml`
- Si no está configurado, parte del flujo seguirá funcionando, pero la asignación
  automática de Copilot pasará a fallback manual.

### 6. Activar GitHub Actions

Verifica que Actions esté habilitado en el repo nuevo y que los workflows puedan
ejecutarse.

### 7. Configurar branch protection sobre `main`

Recomendado:

- Pull request obligatorio para mergear a `main`
- Al menos 1 aprobación humana
- Checks obligatorios en verde
- Bloquear pushes directos a `main`

Checks que deberías exigir como obligatorios:

- `Scope Check`
- `Lint & Format`
- `Security Scan`
- `Contratos BDD`
- `Merge Gate`

### 8. No eliminar `.devcontainer/`

El workflow `preview.yml` depende del Codespace y de
`.devcontainer/devcontainer.json` para:

- instalar dependencias
- levantar `uvicorn`
- exponer el puerto `8000`

Si lo cambias, el preview puede dejar de funcionar.

## Estructura del repositorio

```text
src/
├── main.py
├── models.py
└── services.py

tests/
├── features/
├── step_defs/
└── functional/

.github/
├── ISSUE_TEMPLATE/
└── workflows/
```

## Roles y restricciones por fase

| Fase | Agente | Entrega esperada | Restricción clave |
|---|---|---|---|
| Planeación | `agent-planner` | PR `[ATDD]` con `.feature` | No escribir Python |
| Implementación | `agent-developer` | PR `[IMPL]` | Solo `src/` y `tests/step_defs/` |
| Testing funcional | `agent-tester` | PR `[TEST]` | Solo `tests/functional/` |
| Validación | CI | Checks en PR | Bloquea merge si falla |
| Decisión final | Humano | Aprobación y merge | No delegable |

## Cómo iniciar una ejecución correctamente

### Paso 1. Crear el Issue usando el template

Usa el template `.github/ISSUE_TEMPLATE/agentic-mission.yml`.

El workflow `agentic-plan.yml` valida que el body del Issue contenga, como mínimo:

- `### Misión`
- `### Alcance`
- `### Fuera de Alcance`
- `### Restricciones Técnicas` o `### Restricciones`

> **Nota:** El template de Issue también incluye los campos **Reglas de Negocio**
> y **Ejemplos del Dominio** como obligatorios (GitHub UI los exige vía
> `required: true`). El workflow solo valida explícitamente los 4 campos
> originales; los 2 adicionales se garantizan por la UI.

### Paso 2. Completar bien cada campo

Guía práctica:

- `Misión`
  - Describe qué se quiere lograr en términos de negocio.
  - No describas archivos o funciones internas.
- `Alcance`
  - Lista lo que sí debe incluir esta entrega.
  - Usa bullets concretos.
- `Fuera de Alcance`
  - Lista explícitamente lo que el agente no debe tocar ni construir.
- `Reglas de Negocio`
  - Cada regla debe ser verificable y traducible 1:1 a un escenario Gherkin.
  - Evita reglas ambiguas: "validar correctamente" no es verificable;
    "la duración mínima es 15 minutos" sí lo es.
  - Una regla faltante = un escenario que no se generará.
- `Ejemplos del Dominio`
  - Incluye datos realistas: nombres, valores, formatos.
  - Incluye tanto ejemplos válidos como inválidos.
  - Reduce la invención del agente: si provees datos, los usará.
- `Restricciones Técnicas`
  - Define stack, librerías permitidas, límites de arquitectura y reglas técnicas.

### Demo de referencia: cómo iniciar el flujo

El siguiente Issue de ejemplo usa el dominio de reservas de salas. Puedes
copiarlo directamente al crear un Issue con el template `Misión Agéntica`:

```md
### Misión
Permitir a los empleados de una empresa reservar salas de reunión disponibles,
respetando la capacidad de cada sala y evitando solapamientos de horarios.

### Alcance (In Scope)
- Crear una reserva de sala con fecha, horario y número de asistentes.
- Listar todas las reservas existentes, con filtro opcional por sala.
- Consultar una reserva por su identificador.
- Cancelar una reserva futura.

### Fuera de Alcance
- NO autenticación ni autorización.
- NO base de datos (almacenamiento en memoria).
- NO notificaciones por correo.
- NO edición parcial de una reserva existente.
- NO gestión del catálogo de salas (las salas son fijas: A, B, C).
- NO recurrencia de reservas (cada reserva es individual).

### Reglas de Negocio
- Las salas existentes son únicamente: Sala A (capacidad 4),
  Sala B (capacidad 8), Sala C (capacidad 20).
- Una sala no puede tener dos reservas que se solapen en el mismo día.
- La hora de fin debe ser posterior a la hora de inicio.
- La duración mínima de una reserva es 15 minutos y la máxima es 4 horas.
- Solo se permiten reservas en horario laboral, entre las 08:00 y las 20:00.
- El número de asistentes no puede exceder la capacidad de la sala reservada.
- El propósito de la reunión es obligatorio y debe tener al menos 10 caracteres.
- Solo se pueden cancelar reservas futuras, no reservas que ya ocurrieron.

### Ejemplos del Dominio
Reserva válida:
  sala: B
  fecha: 2026-04-15
  hora_inicio: "10:00"
  hora_fin: "11:00"
  solicitante: ana.lopez@empresa.com
  asistentes: 5
  proposito: Revisión semanal del equipo de plataforma

Reserva inválida (excede capacidad):
  sala: A
  asistentes: 10
  La Sala A solo admite 4 personas.

Reserva inválida (solapamiento):
  Si ya existe una reserva en la Sala B de 10:00 a 11:00, no se puede crear
  otra reserva en la Sala B de 10:30 a 11:30.

### Restricciones Técnicas
- Python 3.11+
- FastAPI + Pydantic v2
- pytest-bdd
- Storage en memoria (dict)
- Sin dependencias nuevas
- Sin modificar workflows ni configuración
- Zona horaria: hora local del proceso, sin manejo explícito de TZ.
  El campo `fecha` es tipo `date` y `hora_inicio`/`hora_fin` son strings `HH:MM`.
- Cobertura máxima: 8 escenarios totales en el `.feature` generado.
```

### Paso 3. Aplicar o reaplicar el label `agentic-mission`

El workflow inicial escucha el evento `issues:labeled`, por lo que el disparador
real es que el label sea agregado al Issue.

Recomendación operativa:

1. Crea el Issue.
2. Verifica que tenga el label `agentic-mission`.
3. Si el workflow no corre, quita y vuelve a agregar el label manualmente.

## Qué ocurre después

### Fase 1. Planificación

Workflow: `agentic-plan.yml`

Qué hace:

- valida la estructura del Issue
- intenta asignar `copilot-swe-agent[bot]` con `custom_agent: agent-planner`
- comenta el estado del proceso

Resultado esperado:

- PR draft o PR de trabajo con título:
  - `[ATDD] Escenarios para: <titulo>`
- Archivos creados en:
  - `tests/features/`

Qué debes revisar como humano:

- que los escenarios cubran flujo principal
- que incluyan validaciones
- que haya al menos un caso límite
- que exista al menos un escenario de seguridad
- que no se mezclen detalles de implementación

### Fase 2. Implementación y testing funcional en paralelo

Workflows:

- `agentic-develop.yml`
- `agentic-test.yml`

Ambos se disparan cuando se hace merge de un PR cuyo título empieza por `[ATDD]`.

Qué crean:

- un Issue `[IMPL] Implementación: ...`
- un Issue `[TEST] Tests funcionales: ...`

Qué agentes se asignan:

- `agent-developer`
- `agent-tester`

Si la asignación automática falla:

- asigna Copilot manualmente desde el sidebar del Issue
- selecciona el agente correcto

### Fase 3. Revisión y paso de draft a ready

Workflow: `agentic-ready-for-review.yml`

Reglas principales:

- PR `[ATDD]` pasa a ready cuando recibe review `approved`
- PR `[IMPL]` y `[TEST]` pasan a ready cuando Copilot revisa y no deja
  sugerencias de código

### Fase 4. Self-correction

Workflow: `agentic-self-correct.yml`

Aplica sobre PRs `[IMPL]` revisados por Copilot.

Qué hace:

- detecta si la review contiene bloques `suggestion`
- si hay sugerencias, pide a Copilot corregirlas en la misma rama
- intenta hasta 3 iteraciones
- si no converge, agrega `needs-human-review`

### Fase 5. CI obligatoria

Workflow: `ci.yml`

Validaciones incluidas:

- `Scope Check`
  - solo para PRs `[IMPL]`
  - falla si se tocan `.feature`, workflows, `requirements*` o `CODEOWNERS`
- `Lint & Format`
  - `ruff check`
  - `ruff format --check`
- `Security Scan`
  - `bandit`
- `Contratos BDD`
  - ejecuta `pytest`
  - omite `tests/functional`
- `Merge Gate`
  - concentra el estado final requerido para merge

### Fase 6. Preview y tests funcionales

Workflows:

- `preview.yml`
- `functional-tests.yml`

`preview.yml`:

- corre en push a `main` o manualmente
- crea un Codespace efímero
- espera a que la app exponga el puerto `8000`
- publica una URL accesible

`functional-tests.yml`:

- corre contra la URL del preview
- ejecuta `pytest tests/functional/`
- publica resumen de resultados

## Matriz resumida de workflows

| Workflow | Trigger | Propósito |
|---|---|---|
| `agentic-plan.yml` | label `agentic-mission` en Issue | Validar Issue y asignar `agent-planner` |
| `agentic-develop.yml` | merge de PR `[ATDD]` | Crear Issue `[IMPL]` |
| `agentic-test.yml` | merge de PR `[ATDD]` | Crear Issue `[TEST]` |
| `agentic-ready-for-review.yml` | review submit en PR | Pasar draft a ready |
| `agentic-self-correct.yml` | review de Copilot en `[IMPL]` | Aplicar loop de corrección |
| `ci.yml` | PR a `main` | Validar calidad, seguridad y contratos |
| `preview.yml` | push a `main` o manual | Levantar preview efímero |
| `functional-tests.yml` | `workflow_call` o manual | Ejecutar tests funcionales |

## Convenciones que debes respetar

- Los `.feature` aprobados no se modifican en implementación.
- El agente de implementación no debe tocar:
  - `.github/workflows/`
  - `requirements*.txt`
  - `CODEOWNERS`
- El agente tester solo debe crear archivos en `tests/functional/`.
- No se agregan dependencias nuevas.
- El almacenamiento esperado es en memoria.

## Ejemplo de operación end-to-end

1. Crear repo nuevo desde el template.
2. Configurar labels, secrets y branch protection.
3. Crear un Issue `[AGENT] ...` usando el template.
4. Completar `Misión`, `Alcance`, `Fuera de Alcance` y `Restricciones Técnicas`.
5. Aplicar o reaplicar `agentic-mission`.
6. Revisar el PR `[ATDD]` generado por Copilot.
7. Aprobar y mergear `[ATDD]`.
8. Esperar la creación automática de los Issues `[IMPL]` y `[TEST]`.
9. Revisar los PRs derivados y su CI.
10. Aprobar y mergear a `main`.
11. Validar `preview.yml` y luego `functional-tests.yml`.

## Ejecución local

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v --strict-markers
ruff check src/ tests/
ruff format --check src/ tests/
bandit -r src/ -ll
```

Si quieres correr la app localmente:

```bash
python -m uvicorn src.main:app --reload
```

## Troubleshooting

### El workflow de planificación no corrió

- Verifica que el Issue tenga `agentic-mission`.
- Si el label ya estaba puesto al crear el Issue, vuelve a quitarlo y agrégalo.
- Revisa que el body tenga:
  - `### Misión`
  - `### Alcance`
  - `### Fuera de Alcance`
  - `### Restricciones Técnicas`

### Copilot no se asigna automáticamente

- Revisa `AGENT_PAT`.
- Si falla, asigna Copilot manualmente en el Issue y elige:
  - `agent-planner`
  - `agent-developer`
  - `agent-tester`

### No se crean los Issues `[IMPL]` o `[TEST]`

- Confirma que el PR mergeado empiece por `[ATDD]`.
- Confirma que existan los labels:
  - `agentic-implementation`
  - `agentic-testing`
- Verifica `AGENT_PAT`.

### El preview falla

- Verifica `CODESPACE_PAT`.
- Revisa que `.devcontainer/devcontainer.json` siga exponiendo el puerto `8000`.
- Revisa que `postCreateCommand` instale dependencias y arranque `uvicorn`.

### El PR quedó con `needs-human-review`

- El loop automático agotó 3 iteraciones.
- Un humano debe revisar la discusión, decidir qué cambios aplicar y luego retirar
  el label si corresponde.

## Referencias internas

- [.github/ISSUE_TEMPLATE/agentic-mission.yml](.github/ISSUE_TEMPLATE/agentic-mission.yml)
- [.github/copilot-instructions.md](.github/copilot-instructions.md)
- [.github/workflows/agentic-plan.yml](.github/workflows/agentic-plan.yml)
- [.github/workflows/agentic-develop.yml](.github/workflows/agentic-develop.yml)
- [.github/workflows/agentic-test.yml](.github/workflows/agentic-test.yml)
- [.github/workflows/agentic-ready-for-review.yml](.github/workflows/agentic-ready-for-review.yml)
- [.github/workflows/agentic-self-correct.yml](.github/workflows/agentic-self-correct.yml)
- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/preview.yml](.github/workflows/preview.yml)
- [.github/workflows/functional-tests.yml](.github/workflows/functional-tests.yml)
