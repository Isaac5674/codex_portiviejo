from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from src.repositories import (
    AuditTrailIncompleteError,
    InvalidAuditDetailError,
    InvalidUpdateError,
    PersistenceUnavailableError,
    RecordNotFoundError,
    SolicitudesRepository,
)
from src.supabase_client import SupabaseConfigurationError, clear_supabase_client_cache, get_supabase_client


@dataclass
class FakeResponse:
    data: Any


class FakeQuery:
    def __init__(self, client: "FakeClient", table: str) -> None:
        self.client = client
        self.table_name = table
        self.operation = "select"
        self.payload: dict[str, Any] | None = None
        self.filters: list[tuple[str, Any]] = []

    def select(self, _columns: str) -> "FakeQuery":
        return self

    def insert(self, payload: dict[str, Any]) -> "FakeQuery":
        self.operation = "insert"
        self.payload = payload
        return self

    def update(self, payload: dict[str, Any]) -> "FakeQuery":
        self.operation = "update"
        self.payload = payload
        return self

    def eq(self, key: str, value: Any) -> "FakeQuery":
        self.filters.append((key, value))
        return self

    def in_(self, key: str, value: Any) -> "FakeQuery":
        self.filters.append((key, value))
        return self

    def gte(self, key: str, value: Any) -> "FakeQuery":
        self.filters.append((key, value))
        return self

    def order(self, *_args: Any, **_kwargs: Any) -> "FakeQuery":
        return self

    def limit(self, _value: int) -> "FakeQuery":
        return self

    def execute(self) -> FakeResponse:
        self.client.calls.append(self)
        response = self.client.responses.get((self.table_name, self.operation), FakeResponse([]))
        if isinstance(response, Exception):
            raise response
        return response


class FakeClient:
    def __init__(self, responses: dict[tuple[str, str], Any]) -> None:
        self.responses = responses
        self.calls: list[FakeQuery] = []

    def table(self, table: str) -> FakeQuery:
        return FakeQuery(self, table)


def valid_request() -> dict[str, Any]:
    return {
        "descripcion_original": "Hay una alcantarilla sin tapa.",
        "resumen": "Alcantarilla sin tapa",
        "ubicacion": "Barrio San José",
        "categoria": "ALCANTARILLADO",
        "prioridad_agente": "ALTA",
        "area_agente": "Alcantarillado",
        "justificacion_agente": "Existe riesgo de accidente.",
        "senales_riesgo": ["riesgo de accidente"],
        "informacion_faltante": [],
        "origen_analisis": "REGLAS",
    }


def test_crear_solicitud_confirma_respuesta_y_registra_auditoria() -> None:
    client = FakeClient(
        {
            ("solicitudes", "insert"): FakeResponse([{"id": 7, "estado": "PENDIENTE_REVISION"}]),
            ("auditoria", "insert"): FakeResponse([{"id": 13, "solicitud_id": 7}]),
        }
    )

    result = SolicitudesRepository(client).crear_solicitud(valid_request(), actor="AGENTE")

    assert result["id"] == 7
    assert [call.table_name for call in client.calls] == ["solicitudes", "auditoria"]
    assert client.calls[1].payload == {
        "solicitud_id": 7,
        "actor": "AGENTE",
        "accion": "SOLICITUD_CREADA",
        "detalle": {"origen": "repositorio", "estado": "PENDIENTE_REVISION"},
    }


def test_crear_solicitud_informa_auditoria_incompleta_sin_repetir_insercion() -> None:
    client = FakeClient(
        {
            ("solicitudes", "insert"): FakeResponse([{"id": 7, "estado": "PENDIENTE_REVISION"}]),
            ("auditoria", "insert"): RuntimeError("network unavailable"),
        }
    )

    with pytest.raises(AuditTrailIncompleteError) as error:
        SolicitudesRepository(client).crear_solicitud(valid_request())

    assert error.value.solicitud["id"] == 7
    assert len(client.calls) == 2


def test_crear_solicitud_valida_auditoria_antes_de_insertar() -> None:
    client = FakeClient({})

    with pytest.raises(InvalidAuditDetailError):
        SolicitudesRepository(client).crear_solicitud(
            valid_request(), detalle_auditoria={"token": "no permitido"}
        )

    assert client.calls == []


def test_obtener_solicitud_distingue_ausencia_de_error_remoto() -> None:
    missing = FakeClient({("solicitudes", "select"): FakeResponse([])})
    with pytest.raises(RecordNotFoundError):
        SolicitudesRepository(missing).obtener_solicitud_por_id(9)

    unavailable = FakeClient({("solicitudes", "select"): RuntimeError("network unavailable")})
    with pytest.raises(PersistenceUnavailableError):
        SolicitudesRepository(unavailable).obtener_solicitud_por_id(9)


def test_actualizar_solicitud_rechaza_campos_no_permitidos_antes_de_escribir() -> None:
    client = FakeClient({("solicitudes", "select"): FakeResponse([{"id": 7}])})

    with pytest.raises(InvalidUpdateError):
        SolicitudesRepository(client).actualizar_solicitud(7, {"descripcion_original": "cambio"})

    assert client.calls == []


def test_actualizar_recomendacion_exige_motivo_de_revision() -> None:
    client = FakeClient({("solicitudes", "select"): FakeResponse([{"id": 7}])})

    with pytest.raises(InvalidUpdateError, match="motivo de revisión"):
        SolicitudesRepository(client).actualizar_solicitud(7, {"prioridad_final": "ALTA"})


def test_actualizar_solicitud_audita_valores_anteriores_y_nuevos() -> None:
    client = FakeClient(
        {
            ("solicitudes", "select"): FakeResponse([{"id": 7, "estado": "PENDIENTE_REVISION"}]),
            ("solicitudes", "update"): FakeResponse([{"id": 7, "estado": "APROBADA"}]),
            ("auditoria", "insert"): FakeResponse([{"id": 14, "solicitud_id": 7}]),
        }
    )

    result = SolicitudesRepository(client).actualizar_solicitud(7, {"estado": "APROBADA"})

    assert result["estado"] == "APROBADA"
    audit_payload = client.calls[-1].payload
    assert audit_payload["detalle"]["campos_modificados"]["estado"] == {
        "anterior": "PENDIENTE_REVISION",
        "nuevo": "APROBADA",
    }


def test_insert_rechaza_respuesta_sin_identificador_confirmado() -> None:
    client = FakeClient(
        {("solicitudes", "insert"): FakeResponse([{"estado": "PENDIENTE_REVISION"}])}
    )

    with pytest.raises(PersistenceUnavailableError, match="identificador"):
        SolicitudesRepository(client).crear_solicitud(valid_request())


def test_auditoria_rechaza_secretos_y_datos_no_serializables() -> None:
    repository = SolicitudesRepository(FakeClient({}))

    with pytest.raises(InvalidAuditDetailError):
        repository.registrar_evento_auditoria(1, "SISTEMA", "PRUEBA", {"api_key": "x"})
    with pytest.raises(InvalidAuditDetailError):
        repository.registrar_evento_auditoria(1, "SISTEMA", "PRUEBA", {"dato": object()})


def test_buscar_duplicados_devuelve_sugerencias_ordenadas_sin_confirmarlas() -> None:
    client = FakeClient(
        {
            ("solicitudes", "select"): FakeResponse(
                [
                    {
                        "id": 1,
                        "descripcion_original": "Existe una fuga de agua frente al mercado central.",
                        "resumen": "Fuga de agua",
                        "ubicacion": "Frente al mercado central",
                        "categoria": "AGUA",
                        "estado": "PENDIENTE_REVISION",
                    }
                ]
            )
        }
    )

    results = SolicitudesRepository(client).buscar_candidatos_duplicados(
        "AGUA", "Calle del mercado central", "Se está desperdiciando agua en la calle del mercado.",
        umbral_similitud=0.2,
    )

    assert results[0]["id"] == 1
    assert results[0]["es_posible_duplicado"] is True
    assert 0.2 <= results[0]["similitud"] <= 1


def test_cliente_informa_configuracion_faltante_sin_exponer_secretos(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SECRET_KEY", raising=False)
    clear_supabase_client_cache()

    with pytest.raises(SupabaseConfigurationError) as error:
        get_supabase_client()

    assert "SUPABASE_URL" in str(error.value)
