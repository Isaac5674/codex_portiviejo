"""Repositorios de solicitudes y auditoría sobre Supabase.

Este módulo es la única capa autorizada para construir consultas de Supabase.
Las entradas deben llegar ya validadas por los modelos Pydantic del dominio; el
repositorio aplica además listas blancas y verifica las respuestas remotas.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from difflib import SequenceMatcher
import json
import re
from typing import Any

from .models import AnalisisReporte, Categoria, EntradaReporte, EstadoSolicitud, PosibleDuplicado
from .supabase_client import get_supabase_client


class RepositoryError(RuntimeError):
    """Error controlado al ejecutar una operación de persistencia."""


class RecordNotFoundError(RepositoryError):
    """La solicitud solicitada no existe."""


class PersistenceUnavailableError(RepositoryError):
    """Supabase no estuvo disponible o devolvió una respuesta inválida."""


class InvalidUpdateError(RepositoryError):
    """La actualización contiene campos no permitidos o no contiene cambios."""


class InvalidAuditDetailError(RepositoryError):
    """El detalle de auditoría no es serializable o podría contener secretos."""


class AuditTrailIncompleteError(RepositoryError):
    """La operación principal fue confirmada, pero no su evento de auditoría."""

    def __init__(self, message: str, solicitud: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.solicitud = dict(solicitud)


SOLICITUD_CREATION_FIELDS = frozenset(
    {
        "descripcion_original",
        "resumen",
        "ubicacion",
        "categoria",
        "prioridad_agente",
        "area_agente",
        "justificacion_agente",
        "informacion_faltante",
        "senales_riesgo",
        "posibles_duplicados",
        "origen_analisis",
        "estado",
        "posible_duplicado_de",
    }
)

SOLICITUD_UPDATE_FIELDS = frozenset(
    {
        "categoria",
        "prioridad_final",
        "area_final",
        "estado",
        "revisado_en",
        "revisor",
        "motivo_revision",
        "posible_duplicado_de",
    }
)

AUDIT_FIELDS = frozenset({"solicitud_id", "actor", "accion", "detalle"})
ACTIVE_DUPLICATE_STATES = (
    "PENDIENTE_REVISION",
    "REQUIERE_INFORMACION",
    "APROBADA",
    "MODIFICADA_Y_APROBADA",
    "POSIBLE_DUPLICADO",
)
_SENSITIVE_KEY = re.compile(
    r"(?:api[_-]?key|secret|token|password|authorization|credential)", re.IGNORECASE
)


def _as_mapping(value: Any) -> dict[str, Any]:
    """Acepta dicts o modelos Pydantic sin acoplar el repositorio a su versión."""

    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "model_dump"):
        return dict(value.model_dump(mode="json"))
    if hasattr(value, "dict"):
        return dict(value.dict())
    raise TypeError("Se esperaba un diccionario o un modelo validado.")


def _positive_id(solicitud_id: int | str) -> int:
    if isinstance(solicitud_id, bool):
        raise ValueError("El identificador de solicitud debe ser un entero positivo.")
    try:
        normalized = int(solicitud_id)
    except (TypeError, ValueError) as exc:
        raise ValueError("El identificador de solicitud debe ser un entero positivo.") from exc
    if normalized <= 0:
        raise ValueError("El identificador de solicitud debe ser un entero positivo.")
    return normalized


def _response_rows(response: Any, operation: str) -> list[dict[str, Any]]:
    data = getattr(response, "data", None)
    if not isinstance(data, list) or not data:
        raise PersistenceUnavailableError(
            f"Supabase no confirmó datos al {operation}."
        )
    if not all(isinstance(row, Mapping) for row in data):
        raise PersistenceUnavailableError(
            f"Supabase devolvió una respuesta inválida al {operation}."
        )
    return [dict(row) for row in data]


def _confirmed_row(
    response: Any, operation: str, *, expected_id: int | None = None
) -> dict[str, Any]:
    row = _response_rows(response, operation)[0]
    row_id = row.get("id")
    if not isinstance(row_id, int):
        raise PersistenceUnavailableError(
            f"Supabase no devolvió un identificador válido al {operation}."
        )
    if expected_id is not None and row_id != expected_id:
        raise PersistenceUnavailableError(
            f"Supabase devolvió una solicitud distinta al {operation}."
        )
    return row


def _contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(
            _SENSITIVE_KEY.search(str(key)) or _contains_sensitive_key(item)
            for key, item in value.items()
        )
    if isinstance(value, (list, tuple)):
        return any(_contains_sensitive_key(item) for item in value)
    return False


def _validated_audit_detail(detail: Any) -> dict[str, Any]:
    if detail is None:
        return {}
    if not isinstance(detail, Mapping):
        raise InvalidAuditDetailError("El detalle de auditoría debe ser un objeto JSON.")
    normalized = dict(detail)
    if _contains_sensitive_key(normalized):
        raise InvalidAuditDetailError("El detalle de auditoría no puede contener secretos.")
    try:
        json.dumps(normalized)
    except (TypeError, ValueError) as exc:
        raise InvalidAuditDetailError(
            "El detalle de auditoría debe contener datos serializables."
        ) from exc
    return normalized


def _validate_audit_identity(actor: Any, accion: Any) -> tuple[str, str]:
    if not isinstance(actor, str) or not actor.strip():
        raise ValueError("El actor de auditoría es obligatorio.")
    if not isinstance(accion, str) or not accion.strip():
        raise ValueError("La acción de auditoría es obligatoria.")
    return actor, accion


def _normalized_text(value: Any) -> str:
    return " ".join(str(value or "").casefold().split())


def _similarity(left: Any, right: Any) -> float:
    left_text = _normalized_text(left)
    right_text = _normalized_text(right)
    if not left_text or not right_text:
        return 0.0
    return SequenceMatcher(None, left_text, right_text).ratio()


class SolicitudesRepository:
    """Operaciones explícitas sobre solicitudes y sus eventos de auditoría."""

    def __init__(self, client: Any | None = None) -> None:
        self._client = client if client is not None else get_supabase_client()

    def crear_solicitud(
        self,
        datos: Mapping[str, Any] | Any,
        *,
        actor: str = "SISTEMA",
        accion: str = "SOLICITUD_CREADA",
        detalle_auditoria: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = self._creation_payload(datos)
        actor, accion = _validate_audit_identity(actor, accion)
        audit_detail = _validated_audit_detail(detalle_auditoria)
        try:
            response = self._client.table("solicitudes").insert(payload).execute()
            solicitud = _confirmed_row(response, "crear la solicitud")
        except PersistenceUnavailableError:
            raise
        except Exception as exc:
            raise PersistenceUnavailableError(
                "No fue posible crear la solicitud en Supabase."
            ) from exc

        detail = {
            "origen": "repositorio",
            "estado": solicitud.get("estado"),
            **audit_detail,
        }
        try:
            self.registrar_evento_auditoria(solicitud["id"], actor, accion, detail)
        except (KeyError, RepositoryError) as exc:
            raise AuditTrailIncompleteError(
                "La solicitud fue creada, pero no se confirmó su auditoría.", solicitud
            ) from exc
        return solicitud

    def crear_solicitud_desde_analisis(
        self,
        entrada: EntradaReporte,
        analisis: AnalisisReporte,
        estado: EstadoSolicitud,
        *,
        actor: str = "CIUDADANO",
        accion: str = "SOLICITUD_CREADA",
    ) -> dict[str, Any]:
        """Persiste únicamente contratos de dominio ya validados.

        El estado inicial se recibe explícitamente desde las reglas para que el
        repositorio no decida flujos de negocio ni sustituya la revisión humana.
        """

        if not isinstance(entrada, EntradaReporte):
            raise TypeError("La entrada debe ser un EntradaReporte validado.")
        if not isinstance(analisis, AnalisisReporte):
            raise TypeError("El análisis debe ser un AnalisisReporte validado.")
        if not isinstance(estado, EstadoSolicitud):
            raise TypeError("El estado debe ser un EstadoSolicitud válido.")

        payload = {
            "descripcion_original": entrada.descripcion,
            "resumen": analisis.resumen,
            "ubicacion": entrada.ubicacion,
            "categoria": analisis.categoria.value,
            "prioridad_agente": analisis.prioridad.value,
            "area_agente": analisis.area_responsable.value,
            "justificacion_agente": analisis.justificacion,
            "informacion_faltante": analisis.informacion_faltante,
            "senales_riesgo": analisis.senales_riesgo,
            "posibles_duplicados": [
                candidato.model_dump(mode="json")
                for candidato in analisis.posibles_duplicados
            ],
            "origen_analisis": analisis.origen_analisis.value,
            "estado": estado.value,
        }
        return self.crear_solicitud(payload, actor=actor, accion=accion)

    def listar_solicitudes(self, *, limite: int = 100) -> list[dict[str, Any]]:
        limite = self._bounded_limit(limite)
        try:
            response = (
                self._client.table("solicitudes")
                .select("*")
                .order("creado_en", desc=True)
                .limit(limite)
                .execute()
            )
            data = getattr(response, "data", None)
            if data is None:
                raise PersistenceUnavailableError(
                    "Supabase no confirmó la consulta de solicitudes."
                )
            if not isinstance(data, list) or not all(isinstance(row, Mapping) for row in data):
                raise PersistenceUnavailableError(
                    "Supabase devolvió una respuesta inválida al listar solicitudes."
                )
            return [dict(row) for row in data]
        except PersistenceUnavailableError:
            raise
        except Exception as exc:
            raise PersistenceUnavailableError(
                "No fue posible consultar las solicitudes en Supabase."
            ) from exc

    def obtener_solicitud_por_id(self, solicitud_id: int | str) -> dict[str, Any]:
        normalized_id = _positive_id(solicitud_id)
        try:
            response = (
                self._client.table("solicitudes")
                .select("*")
                .eq("id", normalized_id)
                .limit(1)
                .execute()
            )
            data = getattr(response, "data", None)
            if data == []:
                raise RecordNotFoundError("La solicitud indicada no existe.")
            return _response_rows(response, "obtener la solicitud")[0]
        except (RecordNotFoundError, PersistenceUnavailableError):
            raise
        except Exception as exc:
            raise PersistenceUnavailableError(
                "No fue posible consultar la solicitud en Supabase."
            ) from exc

    def actualizar_solicitud(
        self,
        solicitud_id: int | str,
        cambios: Mapping[str, Any] | Any,
        *,
        actor: str = "OPERADOR",
        accion: str = "SOLICITUD_ACTUALIZADA",
    ) -> dict[str, Any]:
        normalized_id = _positive_id(solicitud_id)
        actor, accion = _validate_audit_identity(actor, accion)
        payload = self._update_payload(cambios)
        previous = self.obtener_solicitud_por_id(normalized_id)
        try:
            response = (
                self._client.table("solicitudes")
                .update(payload)
                .eq("id", normalized_id)
                .execute()
            )
            solicitud = _confirmed_row(
                response, "actualizar la solicitud", expected_id=normalized_id
            )
        except PersistenceUnavailableError:
            raise
        except Exception as exc:
            raise PersistenceUnavailableError(
                "No fue posible actualizar la solicitud en Supabase."
            ) from exc

        changed_values = {
            field: {"anterior": previous.get(field), "nuevo": solicitud.get(field)}
            for field in payload
        }
        detail = {
            "origen": "repositorio",
            "valores_anteriores": {field: previous.get(field) for field in payload},
            "valores_nuevos": {field: solicitud.get(field) for field in payload},
            "campos_modificados": changed_values,
            "motivo": solicitud.get("motivo_revision"),
        }
        try:
            self.registrar_evento_auditoria(normalized_id, actor, accion, detail)
        except RepositoryError as exc:
            raise AuditTrailIncompleteError(
                "La solicitud fue actualizada, pero no se confirmó su auditoría.", solicitud
            ) from exc
        return solicitud

    def buscar_candidatos_duplicados(
        self,
        categoria: Categoria | str,
        ubicacion: str,
        descripcion: str = "",
        *,
        limite: int = 20,
        dias_recientes: int = 90,
        umbral_similitud: float = 0.45,
    ) -> list[PosibleDuplicado]:
        """Devuelve sugerencias ordenadas; nunca confirma un duplicado."""

        try:
            categoria_valida = (
                categoria if isinstance(categoria, Categoria) else Categoria(categoria)
            )
        except (TypeError, ValueError) as exc:
            raise ValueError("La categoría es obligatoria para buscar duplicados.") from exc
        if not isinstance(ubicacion, str) or not ubicacion.strip():
            raise ValueError("La ubicación es obligatoria para buscar duplicados.")
        if not 0.0 <= umbral_similitud <= 1.0:
            raise ValueError("El umbral de similitud debe estar entre 0 y 1.")
        if dias_recientes < 1:
            raise ValueError("El periodo de búsqueda debe ser positivo.")

        since = (datetime.now(UTC) - timedelta(days=dias_recientes)).isoformat()
        try:
            response = (
                self._client.table("solicitudes")
                .select("id,resumen,descripcion_original,ubicacion,categoria,estado,creado_en")
                .eq("categoria", categoria_valida.value)
                .in_("estado", list(ACTIVE_DUPLICATE_STATES))
                .gte("creado_en", since)
                .limit(self._bounded_limit(limite, maximum=50))
                .execute()
            )
            data = getattr(response, "data", None)
            if data is None or not isinstance(data, list):
                raise PersistenceUnavailableError(
                    "Supabase no confirmó la búsqueda de posibles duplicados."
                )
        except PersistenceUnavailableError:
            raise
        except Exception as exc:
            raise PersistenceUnavailableError(
                "No fue posible buscar posibles duplicados en Supabase."
            ) from exc

        candidates: list[PosibleDuplicado] = []
        for row in data:
            if not isinstance(row, Mapping):
                continue
            description_score = _similarity(
                descripcion, row.get("descripcion_original") or row.get("resumen")
            )
            location_score = _similarity(ubicacion, row.get("ubicacion"))
            score = round((description_score * 0.7) + (location_score * 0.3), 3)
            if score >= umbral_similitud:
                candidates.append(
                    PosibleDuplicado(
                        solicitud_id=_positive_id(row.get("id")),
                        similitud=score,
                        razon="Coincidencia aproximada de descripción y ubicación.",
                    )
                )
        return sorted(candidates, key=lambda item: item.similitud, reverse=True)

    def registrar_evento_auditoria(
        self,
        solicitud_id: int | str,
        actor: str,
        accion: str,
        detalle: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        actor, accion = _validate_audit_identity(actor, accion)
        payload = {
            "solicitud_id": _positive_id(solicitud_id),
            "actor": actor,
            "accion": accion,
            "detalle": _validated_audit_detail(detalle),
        }
        try:
            response = self._client.table("auditoria").insert(payload).execute()
            return _confirmed_row(response, "registrar la auditoría")
        except PersistenceUnavailableError:
            raise
        except Exception as exc:
            raise PersistenceUnavailableError(
                "No fue posible registrar la auditoría en Supabase."
            ) from exc

    def registrar_auditoria(self, datos: Mapping[str, Any] | Any) -> dict[str, Any]:
        raw = _as_mapping(datos)
        unexpected = set(raw) - AUDIT_FIELDS
        if unexpected:
            raise InvalidAuditDetailError(
                f"Campos de auditoría no permitidos: {', '.join(sorted(unexpected))}."
            )
        required = {"solicitud_id", "actor", "accion"}
        missing = required - set(raw)
        if missing:
            raise InvalidAuditDetailError(
                f"Faltan campos de auditoría: {', '.join(sorted(missing))}."
            )
        return self.registrar_evento_auditoria(
            raw["solicitud_id"], raw["actor"], raw["accion"], raw.get("detalle")
        )

    def obtener_auditoria_por_solicitud(
        self, solicitud_id: int | str, *, limite: int = 100
    ) -> list[dict[str, Any]]:
        normalized_id = _positive_id(solicitud_id)
        try:
            response = (
                self._client.table("auditoria")
                .select("*")
                .eq("solicitud_id", normalized_id)
                .order("creado_en", desc=False)
                .limit(self._bounded_limit(limite))
                .execute()
            )
            data = getattr(response, "data", None)
            if data is None or not isinstance(data, list) or not all(
                isinstance(row, Mapping) for row in data
            ):
                raise PersistenceUnavailableError(
                    "Supabase no confirmó el historial de auditoría."
                )
            return [dict(row) for row in data]
        except PersistenceUnavailableError:
            raise
        except Exception as exc:
            raise PersistenceUnavailableError(
                "No fue posible consultar la auditoría en Supabase."
            ) from exc

    @staticmethod
    def _bounded_limit(value: int, *, maximum: int = 100) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
            raise ValueError(f"El límite debe estar entre 1 y {maximum}.")
        return value

    @staticmethod
    def _creation_payload(datos: Mapping[str, Any] | Any) -> dict[str, Any]:
        raw = _as_mapping(datos)
        unexpected = set(raw) - SOLICITUD_CREATION_FIELDS
        if unexpected:
            raise InvalidUpdateError(
                f"Campos no permitidos al crear: {', '.join(sorted(unexpected))}."
            )
        required = {
            "descripcion_original",
            "ubicacion",
            "categoria",
            "prioridad_agente",
            "area_agente",
            "justificacion_agente",
        }
        missing = required - set(raw)
        if missing:
            raise InvalidUpdateError(
                f"Faltan campos obligatorios al crear: {', '.join(sorted(missing))}."
            )
        return raw

    @staticmethod
    def _update_payload(cambios: Mapping[str, Any] | Any) -> dict[str, Any]:
        raw = _as_mapping(cambios)
        if not raw:
            raise InvalidUpdateError("Debe indicar al menos un campo para actualizar.")
        unexpected = set(raw) - SOLICITUD_UPDATE_FIELDS
        if unexpected:
            raise InvalidUpdateError(
                f"Campos no permitidos al actualizar: {', '.join(sorted(unexpected))}."
            )
        recommendation_changes = {"categoria", "prioridad_final", "area_final"}
        if recommendation_changes & set(raw) and not str(raw.get("motivo_revision", "")).strip():
            raise InvalidUpdateError(
                "El motivo de revisión es obligatorio al modificar una recomendación."
            )
        return raw


def _default_repository() -> SolicitudesRepository:
    return SolicitudesRepository()


# Adaptadores de compatibilidad para los consumidores que usan el contrato funcional.
def crear_solicitud(datos: Mapping[str, Any] | Any, **kwargs: Any) -> dict[str, Any]:
    return _default_repository().crear_solicitud(datos, **kwargs)


def crear_solicitud_desde_analisis(
    entrada: EntradaReporte,
    analisis: AnalisisReporte,
    estado: EstadoSolicitud,
    **kwargs: Any,
) -> dict[str, Any]:
    return _default_repository().crear_solicitud_desde_analisis(
        entrada, analisis, estado, **kwargs
    )


def obtener_solicitudes(*, limite: int = 100) -> list[dict[str, Any]]:
    return _default_repository().listar_solicitudes(limite=limite)


def obtener_solicitud_por_id(solicitud_id: int | str) -> dict[str, Any]:
    return _default_repository().obtener_solicitud_por_id(solicitud_id)


def actualizar_solicitud(
    solicitud_id: int | str, cambios: Mapping[str, Any] | Any, **kwargs: Any
) -> dict[str, Any]:
    return _default_repository().actualizar_solicitud(solicitud_id, cambios, **kwargs)


def registrar_auditoria(datos: Mapping[str, Any] | Any) -> dict[str, Any]:
    return _default_repository().registrar_auditoria(datos)


def obtener_auditoria_por_solicitud(
    solicitud_id: int | str, *, limite: int = 100
) -> list[dict[str, Any]]:
    return _default_repository().obtener_auditoria_por_solicitud(solicitud_id, limite=limite)


def buscar_candidatos_duplicados(
    categoria: Categoria | str, ubicacion: str, descripcion: str = "", **kwargs: Any
) -> list[PosibleDuplicado]:
    return _default_repository().buscar_candidatos_duplicados(
        categoria, ubicacion, descripcion, **kwargs
    )
