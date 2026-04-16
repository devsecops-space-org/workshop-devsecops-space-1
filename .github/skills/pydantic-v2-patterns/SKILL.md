---
name: pydantic-v2-patterns
description: >
  Patrones y convenciones para modelos Pydantic v2 en proyectos FastAPI.
  Cubre BaseModel, Field, validaciones declarativas, separación request/response.
  Usar cuando se cree o modifique src/models.py o cualquier modelo Pydantic.
---

# Patrones Pydantic v2

## Cuándo aplicar

- Al crear o modificar modelos en `src/models.py`.
- Al definir request/response bodies para endpoints FastAPI.

## Reglas

### Modelos base

- Usa `BaseModel` + `Field` con validaciones declarativas.
- Docstring breve (una línea) por modelo público.
- Nombres de modelos en PascalCase, descriptivos del dominio.

### Separación request / response

- Crea modelos separados para request y response. Nunca expongas el modelo interno como response.
- Convención de nombres: `<Entidad>Create` (request), `<Entidad>Response` (response).
- El modelo de response incluye campos generados (id, timestamps) que el request no tiene.

### Validaciones

- Usa `Field(...)` con `min_length`, `max_length`, `ge`, `le`, `pattern` según aplique.
- Usa `field_validator` para lógica que no se expresa con Field constraints.
- Para enums, usa `Literal["valor1", "valor2"]` o `Enum` de Python.

### Ejemplo mínimo

```python
from pydantic import BaseModel, Field


class RecursoCreate(BaseModel):
    """Datos para crear un recurso."""

    nombre: str = Field(..., min_length=1, max_length=100)
    categoria: str = Field(default="general")


class RecursoResponse(BaseModel):
    """Recurso con ID asignado."""

    id: str
    nombre: str
    categoria: str
```

## Gotchas

- Pydantic v2 usa `model_validate()`, no `parse_obj()` (v1). No mezcles API v1/v2.
- `Field(default=...)` y `Field(...)` (required) son distintos — no los confundas.
- FastAPI usa `response_model` para serializar — define el response model explícitamente en el endpoint.
- No uses `from __future__ import annotations` si necesitas validadores en runtime.

## Anti-patrones

| Anti-patrón | Por qué es un problema | Corrección |
|---|---|---|
| Un solo modelo para request y response | Expone campos internos (id) en el request | Separar en `Create` y `Response` |
| `dict` como tipo de campo sin estructura | Pierde validación y documentación | Crear un sub-modelo tipado |
| Validación manual en el endpoint | Duplica lógica, error-prone | Mover a Field/field_validator |
| `model.dict()` (API v1) | Deprecado en Pydantic v2 | Usar `model.model_dump()` |
