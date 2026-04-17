"""FastAPI application with endpoints."""

from fastapi import FastAPI, HTTPException

from src.models import ReservaCreate, ReservaResponse
from src.services import (
    ConflictoReserva,
    _reset,
    cancelar_reserva,
    crear_reserva,
    listar_reservas,
    obtener_reserva,
)

app = FastAPI(
    title="DevSecOps Agentic Demo",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/api/v1/reservas", response_model=ReservaResponse, status_code=201)
def crear_reserva_endpoint(data: ReservaCreate) -> ReservaResponse:
    """Crea una nueva reserva de sala."""
    try:
        return crear_reserva(data)
    except ConflictoReserva as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/api/v1/reservas", response_model=list[ReservaResponse])
def listar_reservas_endpoint(sala: str | None = None) -> list[ReservaResponse]:
    """Lista las reservas, con filtro opcional por sala."""
    return listar_reservas(sala)


@app.get("/api/v1/reservas/{reserva_id}", response_model=ReservaResponse)
def obtener_reserva_endpoint(reserva_id: str) -> ReservaResponse:
    """Obtiene una reserva por su identificador."""
    try:
        return obtener_reserva(reserva_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=e.args[0])


@app.delete("/api/v1/reservas/{reserva_id}", status_code=204)
def cancelar_reserva_endpoint(reserva_id: str) -> None:
    """Cancela una reserva futura."""
    try:
        cancelar_reserva(reserva_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=e.args[0])
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.post("/api/v1/_reset", status_code=204)
def reset_estado() -> None:
    """Limpia el estado en memoria. Solo para testing."""
    _reset()
