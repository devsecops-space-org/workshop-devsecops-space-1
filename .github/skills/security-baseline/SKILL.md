---
name: security-baseline
description: >
  Línea base de seguridad para código Python en proyectos FastAPI.
  Cubre funciones prohibidas, secretos, validación de inputs y bandit.
  Usar cuando se genere o revise código en src/ o se evalúe seguridad.
---

# Línea Base de Seguridad — Python / FastAPI

## Cuándo aplicar

- Al crear o modificar cualquier archivo en `src/`.
- Al revisar código generado por otro agente.
- Antes de abrir un PR (paso de verificación).

## Reglas

### Funciones prohibidas

No uses NINGUNA de las siguientes — sin excepciones:

- `eval()` — ejecución arbitraria de código.
- `exec()` — ejecución arbitraria de código.
- `pickle.loads()` / `pickle.load()` — deserialización insegura.
- `subprocess` con `shell=True` — inyección de comandos.
- `os.system()` — inyección de comandos.
- `compile()` con input del usuario — ejecución de código.

### Secretos

- No hardcodees secretos, passwords, tokens ni API keys en el código fuente.
- Usa variables de entorno (`os.environ["KEY"]`) o configuración externa.
- No incluyas secretos en logs, mensajes de error ni responses.

### Validación de inputs

- Valida TODOS los inputs del usuario con Pydantic (BaseModel + Field).
- No valides manualmente con `if/else` — Pydantic lo hace mejor y más consistente.
- No confíes en datos del cliente: valida tipos, rangos, longitudes y formatos.

### Bandit

- `bandit -r src/` debe ejecutarse antes de cada PR.
- Severidad HIGH = fallo de pipeline. No se fusiona con findings HIGH.
- Revisa findings MEDIUM — corrige los legítimos, suprime los falsos positivos con `# nosec` justificado.

## Auto-verificación

Después de escribir código, aplica esta checklist mental:

1. ¿Alguna función de la lista prohibida aparece en el código?
2. ¿Hay strings que parezcan secretos, tokens o passwords?
3. ¿Todos los inputs del usuario pasan por un modelo Pydantic?
4. ¿Los mensajes de error exponen detalles internos del sistema?

Si la respuesta a cualquiera es "sí", corrige ANTES de continuar.

## Gotchas

- `subprocess.run(["cmd", arg])` sin `shell=True` es aceptable — el riesgo es `shell=True`.
- `json.loads()` es seguro (no como `pickle.loads()`), pero valida la estructura resultante con Pydantic.
- FastAPI ya escapa HTML en responses JSON, pero si generas HTML manualmente, escapa con `markupsafe`.
- `bandit` reporta `S101` (assert) en tests — es un falso positivo en contexto de testing.

## Anti-patrones

| Anti-patrón | Riesgo | Corrección |
|---|---|---|
| `eval(user_input)` | RCE (ejecución remota) | Eliminar — usar parser dedicado |
| `password = "s3cret"` en código | Exposición de credenciales | Variable de entorno |
| `if len(titulo) > 100: raise` | Validación manual frágil | `Field(max_length=100)` |
| `subprocess.run(cmd, shell=True)` | Inyección de comandos OS | `shell=False` + lista de args |
| `except Exception: pass` | Oculta errores de seguridad | Manejar excepciones específicas |
| `# nosec` sin comentario | Supresión sin justificación | Agregar razón: `# nosec B101 — test assertion` |
