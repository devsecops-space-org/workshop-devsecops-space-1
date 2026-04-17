"""Business logic and in-memory storage."""

import uuid
from datetime import date
from typing import TypedDict

from src.models import ReservaCreate, ReservaResponse

SALAS: dict[str, int] = {"A": 4, "B": 8, "C": 20}
HORA_INICIO_LABORAL = "08:00"
HORA_FIN_LABORAL = "20:00"
DURACION_MINIMA_MINUTOS = 15
DURACION_MAXIMA_MINUTOS = 240  # 4 horas


class ConflictoReserva(ValueError):
    """Excepción por conflicto de estado en el sistema de reservas."""


class _ReservaDato(TypedDict):
    id: str
    sala: str
    fecha: date
    hora_inicio: str
    hora_fin: str
    asistentes: int
    proposito: str


_storage: dict[str, _ReservaDato] = {}


def _tiempo_a_minutos(hora: str) -> int:
    """Convierte una hora en formato HH:MM a minutos desde medianoche."""
    h, m = hora.split(":")
    return int(h) * 60 + int(m)


def crear_reserva(data: ReservaCreate) -> ReservaResponse:
    """Crea una nueva reserva validando todas las reglas de negocio."""
    if data.sala not in SALAS:
        raise ValueError(f"La sala '{data.sala}' no está registrada en el sistema")

    if data.asistentes > SALAS[data.sala]:
        raise ValueError(
            f"El número de asistentes supera la capacidad máxima de la sala '{data.sala}'"
        )

    inicio_min = _tiempo_a_minutos(data.hora_inicio)
    fin_min = _tiempo_a_minutos(data.hora_fin)

    if fin_min <= inicio_min:
        raise ValueError("La hora de fin debe ser posterior a la hora de inicio")

    duracion = fin_min - inicio_min
    if duracion < DURACION_MINIMA_MINUTOS:
        raise ValueError(f"La duración mínima de una reserva es {DURACION_MINIMA_MINUTOS} minutos")

    if duracion > DURACION_MAXIMA_MINUTOS:
        raise ValueError(
            f"La duración máxima de una reserva es {DURACION_MAXIMA_MINUTOS // 60} horas"
        )

    laboral_inicio = _tiempo_a_minutos(HORA_INICIO_LABORAL)
    laboral_fin = _tiempo_a_minutos(HORA_FIN_LABORAL)
    if inicio_min < laboral_inicio or fin_min > laboral_fin:
        raise ValueError(
            f"La reserva está fuera del horario laboral ({HORA_INICIO_LABORAL}-{HORA_FIN_LABORAL})"
        )

    for r in _storage.values():
        if r["sala"] == data.sala and r["fecha"] == data.fecha:
            r_inicio = _tiempo_a_minutos(r["hora_inicio"])
            r_fin = _tiempo_a_minutos(r["hora_fin"])
            if inicio_min < r_fin and fin_min > r_inicio:
                raise ConflictoReserva(
                    "Ya existe una reserva que se solapa con el horario solicitado"
                )

    reserva_id = str(uuid.uuid4())
    reserva: _ReservaDato = {
        "id": reserva_id,
        "sala": data.sala,
        "fecha": data.fecha,
        "hora_inicio": data.hora_inicio,
        "hora_fin": data.hora_fin,
        "asistentes": data.asistentes,
        "proposito": data.proposito,
    }
    _storage[reserva_id] = reserva
    return ReservaResponse(**reserva)


def obtener_reserva(reserva_id: str) -> ReservaResponse:
    """Obtiene una reserva por su identificador."""
    if reserva_id not in _storage:
        raise KeyError(f"Reserva con id '{reserva_id}' no encontrada")
    return ReservaResponse(**_storage[reserva_id])


def listar_reservas(sala: str | None = None) -> list[ReservaResponse]:
    """Lista todas las reservas, con filtro opcional por sala."""
    reservas = list(_storage.values())
    if sala is not None:
        reservas = [r for r in reservas if r["sala"] == sala]
    return [ReservaResponse(**r) for r in reservas]


def cancelar_reserva(reserva_id: str) -> None:
    """Cancela una reserva futura por su identificador."""
    if reserva_id not in _storage:
        raise KeyError(f"Reserva con id '{reserva_id}' no encontrada")
    reserva = _storage[reserva_id]
    if reserva["fecha"] < date.today():
        raise ValueError("No se puede cancelar una reserva que ya ocurrió")
    del _storage[reserva_id]


def _reset() -> None:
    """Limpia el almacenamiento en memoria (para tests)."""
    _storage.clear()
