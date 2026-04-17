"""Step definitions para el dominio de reservas de salas."""

from collections.abc import Generator

import pytest
from pytest_bdd import given, parsers, scenarios, then, when
from starlette.testclient import TestClient

from src.services import HORA_FIN_LABORAL, HORA_INICIO_LABORAL, SALAS, _reset

scenarios("../features/reserva.feature")


@pytest.fixture
def context() -> dict:
    """Contexto compartido entre steps del mismo escenario."""
    return {}


@pytest.fixture(autouse=True)
def _limpia_estado() -> Generator[None, None, None]:
    """Limpia el estado en memoria antes y después de cada test."""
    _reset()
    yield
    _reset()


@given("que el sistema gestiona las siguientes salas con sus capacidades máximas:")
def gestionar_salas(datatable: list[list[str]]) -> None:
    """Verifica que el sistema gestiona las salas declaradas en el feature."""
    assert datatable[0] == ["sala", "capacidad"]
    salas_feature = [fila[0] for fila in datatable[1:]]
    assert len(salas_feature) == len(set(salas_feature)), "El datatable contiene salas duplicadas"
    assert set(SALAS.keys()) == set(salas_feature), (
        "Las salas del sistema no coinciden con el feature"
    )
    for fila in datatable[1:]:
        assert int(fila[1]) == SALAS[fila[0]]


@given(parsers.parse('que el horario laboral permitido para reservas es de "{inicio}" a "{fin}"'))
def horario_laboral(inicio: str, fin: str) -> None:
    """Verifica el horario laboral configurado en el sistema."""
    assert inicio == HORA_INICIO_LABORAL
    assert fin == HORA_FIN_LABORAL


@given("que no existen reservas en el sistema")
def no_existen_reservas(client: TestClient) -> None:
    """Verifica que no hay reservas en el sistema."""
    response = client.get("/api/v1/reservas")
    assert response.status_code == 200
    assert response.json() == []


@given(
    parsers.parse(
        'que existe una reserva en la sala "{sala}" el día "{fecha}" '
        'de "{hora_inicio}" a "{hora_fin}" con {asistentes:d} asistentes '
        'y propósito "{proposito}"'
    )
)
def existe_reserva(
    client: TestClient,
    context: dict,
    sala: str,
    fecha: str,
    hora_inicio: str,
    hora_fin: str,
    asistentes: int,
    proposito: str,
) -> None:
    """Crea una reserva preexistente para el escenario."""
    payload = {
        "sala": sala,
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "asistentes": asistentes,
        "proposito": proposito,
    }
    response = client.post("/api/v1/reservas", json=payload)
    assert response.status_code == 201
    data = response.json()
    for campo in ("sala", "fecha", "hora_inicio", "hora_fin", "asistentes", "proposito"):
        assert data[campo] == payload[campo]
    context["reserva_id"] = data["id"]
    context["reserva_data"] = payload


@when(
    parsers.parse(
        'se crea una reserva para la sala "{sala}" el día "{fecha}" '
        'de "{hora_inicio}" a "{hora_fin}" con {asistentes:d} asistentes '
        'y propósito "{proposito}"'
    )
)
def crear_reserva_step(
    client: TestClient,
    context: dict,
    sala: str,
    fecha: str,
    hora_inicio: str,
    hora_fin: str,
    asistentes: int,
    proposito: str,
) -> None:
    """Envía una solicitud de creación de reserva."""
    payload = {
        "sala": sala,
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "asistentes": asistentes,
        "proposito": proposito,
    }
    context["response"] = client.post("/api/v1/reservas", json=payload)
    context["reserva_data"] = payload


@when(
    parsers.parse(
        'se intenta crear una reserva para la sala "{sala}" el día "{fecha}" '
        'de "{hora_inicio}" a "{hora_fin}" con {asistentes:d} asistentes '
        'y propósito "{proposito}"'
    )
)
def intentar_crear_reserva_step(
    client: TestClient,
    context: dict,
    sala: str,
    fecha: str,
    hora_inicio: str,
    hora_fin: str,
    asistentes: int,
    proposito: str,
) -> None:
    """Envía una solicitud de creación de reserva que se espera sea rechazada."""
    payload = {
        "sala": sala,
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "asistentes": asistentes,
        "proposito": proposito,
    }
    context["response"] = client.post("/api/v1/reservas", json=payload)


@when("se cancela la reserva previamente registrada")
def cancelar_reserva_step(client: TestClient, context: dict) -> None:
    """Cancela la reserva previamente creada en el contexto."""
    reserva_id = context["reserva_id"]
    context["response"] = client.delete(f"/api/v1/reservas/{reserva_id}")


@when(parsers.parse('se listan las reservas filtrando por la sala "{sala}"'))
def listar_reservas_sala_step(client: TestClient, context: dict, sala: str) -> None:
    """Lista las reservas filtrando por sala."""
    context["response"] = client.get("/api/v1/reservas", params={"sala": sala})


@then("el sistema confirma la creación de la reserva")
def confirma_creacion(context: dict) -> None:
    """Verifica que la creación de la reserva fue exitosa."""
    assert context["response"].status_code == 201
    data = context["response"].json()
    context["reserva_id"] = data["id"]
    for campo in ("sala", "fecha", "hora_inicio", "hora_fin", "asistentes", "proposito"):
        assert data[campo] == context["reserva_data"][campo]


@then("es posible consultar la reserva por su identificador con los datos registrados")
def consultar_por_id(client: TestClient, context: dict) -> None:
    """Verifica que la reserva puede consultarse por su ID."""
    reserva_id = context["reserva_id"]
    response = client.get(f"/api/v1/reservas/{reserva_id}")
    assert response.status_code == 200
    data = response.json()
    for campo in ("sala", "fecha", "hora_inicio", "hora_fin", "asistentes", "proposito"):
        assert data[campo] == context["reserva_data"][campo]


@then(parsers.parse('la reserva aparece al listar las reservas de la sala "{sala}"'))
def reserva_aparece_en_listado(client: TestClient, context: dict, sala: str) -> None:
    """Verifica que la reserva aparece en el listado de la sala."""
    response = client.get("/api/v1/reservas", params={"sala": sala})
    assert response.status_code == 200
    ids = [r["id"] for r in response.json()]
    assert context["reserva_id"] in ids


@then("el sistema confirma la cancelación")
def confirma_cancelacion(context: dict) -> None:
    """Verifica que la cancelación fue exitosa."""
    assert context["response"].status_code == 204


@then(parsers.parse('la reserva ya no aparece al listar las reservas de la sala "{sala}"'))
def reserva_no_aparece(client: TestClient, context: dict, sala: str) -> None:
    """Verifica que la reserva ya no aparece en el listado de la sala."""
    response = client.get("/api/v1/reservas", params={"sala": sala})
    assert response.status_code == 200
    ids = [r["id"] for r in response.json()]
    assert context["reserva_id"] not in ids


@then("el sistema rechaza la operación por superar la capacidad de la sala")
def rechaza_capacidad(context: dict) -> None:
    """Verifica que la operación fue rechazada por superar la capacidad."""
    assert 400 <= context["response"].status_code < 500


@then("el sistema rechaza la operación por solapamiento de horario")
def rechaza_solapamiento(context: dict) -> None:
    """Verifica que la operación fue rechazada por solapamiento de horario."""
    assert 400 <= context["response"].status_code < 500


@then("el sistema rechaza la operación por no poder cancelar reservas pasadas")
def rechaza_cancelar_pasada(context: dict) -> None:
    """Verifica que no se pueden cancelar reservas pasadas."""
    assert 400 <= context["response"].status_code < 500


@then("el sistema rechaza la operación por datos inválidos")
def rechaza_datos_invalidos(context: dict) -> None:
    """Verifica que la operación fue rechazada por datos inválidos."""
    assert 400 <= context["response"].status_code < 500


@then("el sistema retorna una lista vacía de reservas")
def retorna_lista_vacia(context: dict) -> None:
    """Verifica que el sistema retorna una lista vacía."""
    assert context["response"].status_code == 200
    assert context["response"].json() == []
