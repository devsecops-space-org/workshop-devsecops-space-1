---
name: python-fastapi-standards
description: >
  Estándares de código Python 3.11+ para proyectos FastAPI. Aplica reglas de
  type hints, imports, line length, ruff y convenciones de estilo.
  Usar cuando se genere o modifique código Python en src/ o tests/.
---

# Estándares de Código Python 3.11+ / FastAPI

## Cuándo aplicar

- Al crear o modificar cualquier archivo `.py` en `src/` o `tests/`.
- Al revisar código Python generado por otro agente.

## Reglas

### Type hints

- Type hints en TODAS las funciones: parámetros + retorno. Sin excepciones.
- No uses `Any`. Si no conoces el tipo, estréchalo (`str | int`, `dict[str, str]`, etc.).
- Usa tipos nativos de Python 3.11+: `dict[str, T]`, `list[T]`, `str | None`.
- No uses `Optional[T]` ni `Union[X, Y]` — usa la sintaxis `X | None` y `X | Y`.

### Imports

- Orden estricto: stdlib → third-party → local. Separados por una línea en blanco.
- Usa imports absolutos desde `src.` (ejemplo: `from src.models import RecursoResponse`).
- No dejes imports sin usar — ruff regla F los detecta.

### Estilo

- Line length máximo: **100 caracteres**.
- Docstrings en funciones públicas: una línea descriptiva.
- No dejes código comentado. Si no se usa, se elimina.

### Linting

- **ruff** con reglas `E, F, I, S` es obligatorio.
- Ejecuta `ruff check <ruta>` y `ruff format --check <ruta>` antes de cualquier PR.
- Corrige TODOS los errores. No uses `# noqa` salvo justificación documentada.

## Gotchas

- `ruff` no detecta type hints faltantes — revísalos manualmente.
- Un `from __future__ import annotations` cambia la semántica de tipos en runtime; no lo uses a menos que sea necesario para Pydantic.
- `list` vs `List`: en Python 3.11+ siempre usa `list` en minúscula. Ruff regla UP006 lo detecta.

## Anti-patrones

| Anti-patrón | Por qué es un problema | Corrección |
|---|---|---|
| `def foo(x):` sin type hints | Rompe verificabilidad y legibilidad | `def foo(x: str) -> str:` |
| `from typing import Any` | Elude el sistema de tipos | Reemplaza con tipo concreto |
| `import os; import sys` en una línea | Viola estilo de imports | Un import por línea |
| Código comentado `# resp = ...` | Ruido sin valor | Eliminar |
| `# noqa` sin justificación | Esconde problemas reales | Eliminar o justificar |
