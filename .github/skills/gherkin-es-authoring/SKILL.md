---
name: gherkin-es-authoring
description: >
  Autoría de escenarios Gherkin en español para flujos ATDD. Cubre formato
  de .feature, cobertura obligatoria, reglas de calidad, parametrización y
  naming. Usar cuando se generen o revisen archivos .feature en tests/features/.
---

# Autoría de Escenarios Gherkin en Español

## Cuándo aplicar

- Al crear archivos `.feature` en `tests/features/`.
- Al revisar escenarios Gherkin generados.

## Formato obligatorio de cada `.feature`

```gherkin
# language: es

Característica: <nombre descriptivo del dominio>

  Como <actor>
  Quiero <acción>
  Para <beneficio de negocio>

  Escenario: <categoría> - <descripción breve>
    Dado <precondición>
    Cuando <acción del actor>
    Entonces <resultado observable>
```

- Header `# language: es` es **obligatorio** en la primera línea.
- Nombre del archivo: `<dominio>.feature` en snake_case singular.
- Un archivo por dominio funcional.

## Cobertura obligatoria por feature

| Categoría | Qué cubrir | Mínimo |
|---|---|---|
| Flujo principal | Flujos exitosos principales | 1 |
| Validación | Datos inválidos, campos faltantes, tipos incorrectos | 2 |
| Caso límite | Valores límite, estados vacíos, duplicados | 1 |
| Seguridad | Inyección, datos maliciosos | 1 |

Total mínimo: **5 escenarios** por feature.

## Reglas de calidad

### Comportamiento, no implementación

- Describe **comportamiento de negocio**. El usuario hace X, el sistema responde Y.
- NUNCA menciones: HTTP, JSON, status codes, endpoints, headers, bases de datos, REST.
- Piensa como el product owner, no como el desarrollador.

### Estructura de escenarios

- Un escenario = un solo comportamiento. No mezcles validaciones distintas.
- Máximo **7 pasos** por escenario (Dado/Cuando/Entonces combinados).
- Usa `Esquema del escenario` + `Ejemplos` para variantes del mismo comportamiento.

### Steps

- Redacta en infinitivo o tercera persona del singular.
- Steps reutilizables y parametrizados con `<variables>` o comillas `"valor"`.
- Mismo paso de negocio = mismo texto de step. Consistencia entre escenarios.
- Mismo paso de negocio = misma firma de parámetros. No agregues fragmentos
  opcionales en un solo escenario de la misma familia de steps.

### Naming

- Nombre del escenario: `<Categoría> - <descripción concisa>` en español.
- Categorías válidas: `Flujo principal`, `Validación`, `Caso límite`, `Seguridad`.

### Fechas y datos de ejemplo

- Usa los datos del campo `Ejemplos del Dominio` como referencia de vocabulario,
  valores y casos típicos; no los copies literalmente si el valor exacto no
  cambia el comportamiento.
- Evita fechas cercanas al presente en `.feature` cuando el escenario solo
  necesita distinguir pasado/futuro.
- Si el día exacto no es contractual, prefiere placeholders semánticos
  (`<fecha_futura>`, `<fecha_pasada>`) o fechas centinela estables y lejanas
  como `2099-06-01` y `2000-01-01`.
- Si el comportamiento depende de una fecha u horario exactos, deja explícito
  en el step por qué ese dato concreto importa.

### Ejemplo completo

```gherkin
# language: es

Característica: Gestión de recursos

  Como usuario del sistema
  Quiero administrar mis recursos
  Para organizar mi trabajo diario

  Escenario: Flujo principal - Crear un recurso con datos válidos
    Dado que no existen recursos en el sistema
    Cuando se crea un recurso con nombre "Ejemplo" y categoría "alta"
    Entonces el sistema confirma la creación del recurso
    Y el recurso "Ejemplo" aparece con categoría "alta"

  Esquema del escenario: Validación - Rechazar recurso con datos inválidos
    Cuando se intenta crear un recurso con nombre "<nombre>" y categoría "<categoria>"
    Entonces el sistema rechaza la operación por datos inválidos

    Ejemplos:
      | nombre | categoria |
      |        | alta      |
      | Test   | invalida  |
```

## Auto-verificación

Antes de entregar, revisa cada escenario con esta checklist:

1. ¿Describe comportamiento de negocio sin detalles técnicos?
2. ¿Tiene 7 pasos o menos?
3. ¿Prueba UN solo comportamiento?
4. ¿Los steps son reutilizables y parametrizados?
5. ¿El nombre sigue el formato `<Categoría> - <descripción>` con categoría en español?
6. ¿El mismo comportamiento reutiliza exactamente el mismo texto de step?
7. ¿Los steps equivalentes mantienen la misma firma de parámetros?
8. ¿Está cubierta la tabla de cobertura mínima?

## Gotchas

- `Esquema del escenario` (español) ≠ `Scenario Outline` (inglés). Con `# language: es` usa las keywords en español.
- Los nombres de columnas en `Ejemplos` deben coincidir exactamente con los `<placeholders>` de los steps.
- Gherkin en español usa `Y` (conjunción), no `And`. Las keywords completas: `Dado`, `Cuando`, `Entonces`, `Y`, `Pero`.
- `pytest-bdd` requiere que cada step text coincida exactamente con el parser — un espacio extra rompe el match.
- **Sinónimos aparentes crean steps distintos**: `al listar todas las reservas de la sala` y `al listar las reservas de la sala` son textos distintos para `pytest-bdd`. Si expresan el mismo comportamiento, usa uno solo en todos los escenarios.
- **Firma de parámetros consistente por familia de steps**: Si el paso `se crea una reserva...` aparece en varios escenarios, todos deben llevar los mismos parámetros. No metas `solicitada por "<email>"` solo en uno, salvo que decidas que el solicitante es parte del contrato y lo agregues en todos.
- **Consistencia comillas/placeholders en `Esquema del escenario`**: Las comillas van en el **step**, NO en la tabla `Ejemplos`. El step lleva `"<variable>"` y la celda lleva el valor sin comillas. Gherkin sustituye `<variable>` literalmente; si la celda dice `"valor"`, el texto resultante tendrá comillas dobles (`""valor""`), rompiendo el match con `parsers.parse()`.
  - Correcto: step `"<hora>"` → celda `10:00` → resultado `"10:00"`
  - Incorrecto: step `<hora>` → celda `"10:00"` → resultado `"10:00"` (comillas viajan como dato, inconsistente con otros escenarios)
- **Ejemplos del Dominio no son contrato literal**: Si el Issue trae una fecha
  cercana al presente, úsala como referencia de negocio y no como valor
  obligatorio del `.feature` salvo que ese día exacto sea parte de la regla.

## Anti-patrones

| Anti-patrón | Por qué es un problema | Corrección |
|---|---|---|
| `Entonces la API retorna 201` | Implementación técnica, no negocio | `Entonces el sistema confirma la creación` |
| `Dado que POST /api/v1/recursos` | Acoplado a la ruta HTTP | `Dado que se crea un recurso "X"` |
| 10 pasos en un escenario | Difícil de leer y mantener | Dividir en escenarios atómicos |
| Categoría en inglés dentro de un `.feature` en español | Mezcla idiomas y ensucia el contrato | `Flujo principal - Crear recurso` |
| Steps hardcodeados sin parámetros | No reutilizables | Parametrizar con `"valor"` o `<variable>` |
| Mezclar 2 validaciones en 1 escenario | Falla ambigua | Un comportamiento por escenario |
| Mismo comportamiento con texto distinto | Fuerza steps duplicados o parsers complejos | Reutilizar el mismo texto exacto |
| Firma distinta para la misma familia de step | Complica step definitions sin valor funcional | Mantener exactamente los mismos parámetros |
| Copiar fechas cercanas al presente desde el Issue | El contrato envejece y los tests funcionales se vuelven frágiles | Usar `<fecha_futura>`/`<fecha_pasada>` o fechas centinela estables |
| Comillas en celdas de `Ejemplos` | `parsers.parse` recibe comillas dobles, rompe match | Comillas en el step (`"<var>"`), valor limpio en la tabla |
