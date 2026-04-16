---
name: pr-conventions
description: >
  Convenciones para branches, títulos, labels y body de Pull Requests en el
  flujo ATDD de 3 fases (planner, developer, tester). Usar cuando se abra
  un PR desde cualquier agente o se revise formato de PR.
---

# Convenciones de Pull Requests — Flujo ATDD

## Cuándo aplicar

- Al abrir un PR desde cualquier agente (planner, developer, tester).
- Al verificar que un PR cumple con las convenciones del proyecto.

## Convenciones por fase

### Fase 1: Planner (escenarios Gherkin)

| Campo | Valor |
|---|---|
| Branch | `atdd/<dominio>-scenarios` |
| Título | `[ATDD] Escenarios para: <título del Issue>` |
| Label | `agentic-mission` |
| Body | Resumen de escenarios + tabla de cobertura + `Refs #<número del Issue>` |

### Fase 2: Developer (implementación)

| Campo | Valor |
|---|---|
| Branch | `impl/<dominio>-implementation` |
| Título | `[IMPL] Implementación: <título del Issue>` |
| Label | `agentic-implementation` |
| Body | Resumen por archivo + endpoints creados + `Refs #<número del Issue>` |

### Fase 3: Tester (tests funcionales)

| Campo | Valor |
|---|---|
| Branch | `test/<dominio>-functional` |
| Título | `[TEST] Tests funcionales: <título del Issue>` |
| Label | `agentic-testing` |
| Body | Lista de escenarios cubiertos + mapeo steps→endpoints + `Refs #<número del Issue>` |

## Reglas comunes

- El body SIEMPRE incluye `Refs #<número del Issue>` para trazabilidad.
- Branch desde `main`. Nunca desde otra feature branch.
- Un PR = un dominio funcional. No mezcles dominios en un solo PR.
- Título en español. Usa el prefijo entre corchetes exacto (`[ATDD]`, `[IMPL]`, `[TEST]`).
- Descripción en español con formato Markdown legible.

## Gotchas

- GitHub requiere que el label exista en el repositorio antes de asignarlo. Verifica que `agentic-mission`, `agentic-implementation` y `agentic-testing` están creados.
- `Refs #N` enlaza al Issue pero no lo cierra. Usa `Closes #N` solo si el PR resuelve completamente el Issue (normalmente solo el PR de tester cierra).
- El nombre del branch debe ser kebab-case después del prefijo: `impl/reservas-implementation`, no `impl/ReservasImplementation`.

## Anti-patrones

| Anti-patrón | Corrección |
|---|---|
| Branch sin prefijo de fase (`fix/reservas`) | Usar `atdd/`, `impl/` o `test/` según la fase |
| Título sin prefijo `[ATDD]`/`[IMPL]`/`[TEST]` | Agregar el prefijo exacto |
| Body sin referencia al Issue | Agregar `Refs #<número>` |
| PR que mezcla escenarios + implementación | Un PR por fase |
| Label incorrecto (ej. `agentic-mission` en PR de implementación) | Verificar label vs fase |
