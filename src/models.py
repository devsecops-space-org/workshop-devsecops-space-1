"""Pydantic models for the application."""

from pydantic import BaseModel, Field


class ReservaCreate(BaseModel):
    """Datos necesarios para crear una reserva de sala."""

    sala: str = Field(..., min_length=1, max_length=50)
    fecha: str = Field(..., pattern=r"^(?:19|20)\d{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$")
    hora_inicio: str = Field(..., pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    hora_fin: str = Field(..., pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")
    asistentes: int = Field(..., ge=1)
    proposito: str = Field(..., min_length=10, max_length=200, pattern=r"^[^<>]*$")


class ReservaResponse(BaseModel):
    """Reserva con identificador asignado."""

    id: str
    sala: str
    fecha: str
    hora_inicio: str
    hora_fin: str
    asistentes: int
    proposito: str
