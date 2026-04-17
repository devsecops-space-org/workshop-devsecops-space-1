"""Tests funcionales: Gestión de reservas de salas de reunión."""

import httpx
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../features/reserva.feature")


# ─────────────────────────────────────────────
# Antecedentes (Background)
# ─────────────────────────────────────────────


@given(parsers.parse("que el sistema gestiona las siguientes salas con sus capacidades máximas:"))
def gestiona_salas(datatable: list[list[str]], api_client: httpx.Client) -> None:
    salas_esperadas = {"A": 4, "B": 8, "C": 20}
    assert datatable[0] == ["sala", "capacidad"], f"Header inesperado: {datatable[0]}"
    salas_vistas: set[str] = set()
    for fila in datatable[1:]:
        sala, capacidad = fila[0], int(fila[1])
        assert sala in salas_esperadas, f"Sala inesperada: {sala}"
        assert capacidad == salas_esperadas[sala], f"Capacidad incorrecta para sala {sala}"
        assert sala not in salas_vistas, f"Sala duplicada: {sala}"
        salas_vistas.add(sala)
    faltantes = set(salas_esperadas) - salas_vistas
    assert not faltantes, f"Salas faltantes en el datatable: {faltantes}"
    response = api_client.get("/api/v1/reservas")
    assert response.status_code == 200


@given(
    parsers.parse(
        'que el horario laboral permitido para reservas es de "{hora_inicio}" a "{hora_fin}"'
    )
)
def horario_laboral(hora_inicio: str, hora_fin: str, api_client: httpx.Client) -> None:
    payload = {
        "sala": "B",
        "fecha": "2099-06-01",
        "hora_inicio": "07:00",
        "hora_fin": "08:30",
        "asistentes": 2,
        "proposito": "Verificación de límite de horario laboral",
    }
    response = api_client.post("/api/v1/reservas", json=payload)
    assert response.status_code == 422, (
        f"Se esperaba rechazo (422) para reserva fuera de horario "
        f"{hora_inicio}-{hora_fin}, pero se obtuvo {response.status_code}"
    )


# ─────────────────────────────────────────────
# Given steps
# ─────────────────────────────────────────────


@given("que no existen reservas en el sistema")
def no_existen_reservas(api_client: httpx.Client) -> None:
    reset_resp = api_client.post("/api/v1/_reset")
    assert reset_resp.status_code in (200, 204), (
        f"Error al resetear estado: {reset_resp.status_code} - {reset_resp.text}"
    )
    response = api_client.get("/api/v1/reservas")
    assert response.status_code == 200
    assert response.json() == [], f"_reset no limpió el estado: {response.json()}"


@given(
    parsers.parse(
        'que existe una reserva en la sala "{sala}" el día "{fecha}" '
        'de "{hora_inicio}" a "{hora_fin}" con {asistentes:d} asistentes '
        'y propósito "{proposito}"'
    )
)
def existe_reserva(
    sala: str,
    fecha: str,
    hora_inicio: str,
    hora_fin: str,
    asistentes: int,
    proposito: str,
    api_client: httpx.Client,
    context: dict,
) -> None:
    listado = api_client.get("/api/v1/reservas", params={"sala": sala})
    assert listado.status_code == 200
    existentes = [
        r
        for r in listado.json()
        if r["sala"] == sala
        and r["fecha"] == fecha
        and r["hora_inicio"] == hora_inicio
        and r["hora_fin"] == hora_fin
        and r["asistentes"] == asistentes
        and r["proposito"] == proposito
    ]
    if existentes:
        context["reserva_id"] = existentes[0]["id"]
        return
    payload = {
        "sala": sala,
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "asistentes": asistentes,
        "proposito": proposito,
    }
    response = api_client.post("/api/v1/reservas", json=payload)
    assert response.status_code == 201, (
        f"Error al crear reserva de precondición: {response.status_code} - {response.text}"
    )
    context["reserva_id"] = response.json()["id"]


# ─────────────────────────────────────────────
# When steps
# ─────────────────────────────────────────────


@when(
    parsers.parse(
        'se crea una reserva para la sala "{sala}" el día "{fecha}" '
        'de "{hora_inicio}" a "{hora_fin}" con {asistentes:d} asistentes '
        'y propósito "{proposito}"'
    )
)
def crea_reserva(
    sala: str,
    fecha: str,
    hora_inicio: str,
    hora_fin: str,
    asistentes: int,
    proposito: str,
    api_client: httpx.Client,
    context: dict,
) -> None:
    payload = {
        "sala": sala,
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "asistentes": asistentes,
        "proposito": proposito,
    }
    context["payload"] = payload
    context["last_response"] = api_client.post("/api/v1/reservas", json=payload)


@when(
    parsers.parse(
        'se intenta crear una reserva para la sala "{sala}" el día "{fecha}" '
        'de "{hora_inicio}" a "{hora_fin}" con {asistentes:d} asistentes '
        'y propósito "{proposito}"'
    )
)
def intenta_crear_reserva(
    sala: str,
    fecha: str,
    hora_inicio: str,
    hora_fin: str,
    asistentes: int,
    proposito: str,
    api_client: httpx.Client,
    context: dict,
) -> None:
    payload = {
        "sala": sala,
        "fecha": fecha,
        "hora_inicio": hora_inicio,
        "hora_fin": hora_fin,
        "asistentes": asistentes,
        "proposito": proposito,
    }
    context["last_response"] = api_client.post("/api/v1/reservas", json=payload)


@when("se cancela la reserva previamente registrada")
def cancela_reserva(api_client: httpx.Client, context: dict) -> None:
    context["last_response"] = api_client.delete(f"/api/v1/reservas/{context['reserva_id']}")


@when(parsers.parse('se listan las reservas filtrando por la sala "{sala}"'))
def lista_reservas_sala(sala: str, api_client: httpx.Client, context: dict) -> None:
    context["last_response"] = api_client.get("/api/v1/reservas", params={"sala": sala})


# ─────────────────────────────────────────────
# Then steps
# ─────────────────────────────────────────────


@then("el sistema confirma la creación de la reserva")
def confirma_creacion(context: dict) -> None:
    response = context["last_response"]
    assert response.status_code == 201, (
        f"Se esperaba 201, pero se obtuvo {response.status_code}: {response.text}"
    )
    data = response.json()
    assert "id" in data
    payload = context["payload"]
    assert data["sala"] == payload["sala"]
    assert data["fecha"] == payload["fecha"]
    assert data["hora_inicio"] == payload["hora_inicio"]
    assert data["hora_fin"] == payload["hora_fin"]
    assert data["asistentes"] == payload["asistentes"]
    assert data["proposito"] == payload["proposito"]
    context["reserva_id"] = data["id"]


@then("es posible consultar la reserva por su identificador con los datos registrados")
def consulta_por_id(api_client: httpx.Client, context: dict) -> None:
    reserva_id = context["reserva_id"]
    response = api_client.get(f"/api/v1/reservas/{reserva_id}")
    assert response.status_code == 200
    data = response.json()
    payload = context["payload"]
    assert data["id"] == reserva_id
    assert data["sala"] == payload["sala"]
    assert data["fecha"] == payload["fecha"]
    assert data["hora_inicio"] == payload["hora_inicio"]
    assert data["hora_fin"] == payload["hora_fin"]
    assert data["asistentes"] == payload["asistentes"]
    assert data["proposito"] == payload["proposito"]


@then(parsers.parse('la reserva aparece al listar las reservas de la sala "{sala}"'))
def reserva_aparece_en_lista(sala: str, api_client: httpx.Client, context: dict) -> None:
    response = api_client.get("/api/v1/reservas", params={"sala": sala})
    assert response.status_code == 200
    reservas = response.json()
    reserva_id = context["reserva_id"]
    ids = [r["id"] for r in reservas]
    assert reserva_id in ids, f"La reserva {reserva_id} no aparece en el listado de sala {sala}"
    for reserva in reservas:
        assert reserva["sala"] == sala, (
            f"Reserva con sala incorrecta en el filtro por '{sala}': {reserva}"
        )


@then("el sistema confirma la cancelación")
def confirma_cancelacion(context: dict) -> None:
    response = context["last_response"]
    assert response.status_code in (200, 204), (
        f"Se esperaba 200 o 204, pero se obtuvo {response.status_code}: {response.text}"
    )


@then(parsers.parse('la reserva ya no aparece al listar las reservas de la sala "{sala}"'))
def reserva_no_aparece(sala: str, api_client: httpx.Client, context: dict) -> None:
    response = api_client.get("/api/v1/reservas", params={"sala": sala})
    assert response.status_code == 200
    ids = [r["id"] for r in response.json()]
    assert context["reserva_id"] not in ids, (
        f"La reserva {context['reserva_id']} todavía aparece en el listado de sala {sala}"
    )


@then("el sistema rechaza la operación por superar la capacidad de la sala")
def rechaza_por_capacidad(context: dict) -> None:
    response = context["last_response"]
    assert response.status_code == 422, (
        f"Se esperaba 422 por exceso de capacidad, pero se obtuvo {response.status_code}"
    )


@then("el sistema rechaza la operación por solapamiento de horario")
def rechaza_por_solapamiento(context: dict) -> None:
    response = context["last_response"]
    assert response.status_code == 409, (
        f"Se esperaba 409 por solapamiento de horario, pero se obtuvo {response.status_code}"
    )


@then("el sistema rechaza la operación por no poder cancelar reservas pasadas")
def rechaza_cancelar_pasadas(context: dict) -> None:
    response = context["last_response"]
    assert response.status_code == 422, (
        f"Se esperaba 422 por cancelar reserva pasada, pero se obtuvo {response.status_code}"
    )


@then("el sistema rechaza la operación por datos inválidos")
def rechaza_por_datos_invalidos(context: dict) -> None:
    response = context["last_response"]
    assert response.status_code == 422, (
        f"Se esperaba 422 por datos inválidos, pero se obtuvo {response.status_code}"
    )


@then("el sistema retorna una lista vacía de reservas")
def lista_vacia(context: dict) -> None:
    response = context["last_response"]
    assert response.status_code == 200
    data = response.json()
    assert data == [], f"Se esperaba lista vacía, pero se obtuvo: {data}"
