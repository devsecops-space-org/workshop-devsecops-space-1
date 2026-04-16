---
applyTo: "src/**/*.py"
---

# Reglas para código de producción (src/)

## Arquitectura obligatoria

```
Endpoint (src/main.py)       → solo routing + conversión de excepciones
  └→ Service (src/services.py)  → lógica de negocio + storage en memoria
      └→ Model (src/models.py)  → validación declarativa con Pydantic v2
```

## src/models.py
- Usar `BaseModel` + `Field` de Pydantic v2.
- Modelos de request y response SEPARADOS (nunca el mismo para ambos).
- Validaciones declarativas: `Field(min_length=1)`, `Field(ge=0)`, `pattern=`.
- NO usar validadores manuales cuando `Field()` es suficiente.

## src/services.py
- Funciones puras con type hints completos.
- Storage: `dict` a nivel de módulo. NO bases de datos.
- Errores de negocio: `raise ValueError("mensaje descriptivo")`.
- Sin decoradores de framework. Sin imports de FastAPI.
- Toda función debe tener una función `_reset()` o mecanismo de limpieza para tests.

## src/main.py
- Prefijo `/api/v1/` en todas las rutas.
- `response_model` explícito en cada endpoint (omitir en 204).
- Status codes semánticos: 201 crear, 200 ok, 204 eliminar.
- Captura `ValueError` datos inválidos → `HTTPException(status_code=422, detail=str(e))`.
- Captura `ValueError` conflicto de estado → `HTTPException(status_code=409, detail=str(e))`.
- Captura `KeyError` → `HTTPException(status_code=404, detail=e.args[0])` (NO `str(e)`).
- CERO lógica de negocio — todo delegado a services.

## Seguridad
- PROHIBIDO: `eval()`, `exec()`, `pickle`, `subprocess(shell=True)`.
- PROHIBIDO: secretos hardcodeados, `# nosec`, deshabilitar reglas de bandit.
- Toda entrada de usuario validada por Pydantic, nunca manualmente.
