"""Herramientas reutilizables para el coordinador de PortoReporta.

Las reglas deterministas y los contratos Pydantic pertenecen a sus módulos de
dominio. Estas funciones solamente validan entradas y delegan cada operación a
esa fuente central, por lo que se pueden sustituir por dobles en pruebas.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from .models import AreaResponsable, Categoria, EvaluacionPrioridad
from .rules import (
    evaluar_prioridad as _evaluar_prioridad_por_reglas,
    identificar_informacion_faltante as _identificar_informacion_faltante,
    obtener_area_responsable as _obtener_area_por_reglas,
)


AreaResolver = Callable[[Categoria | str], AreaResponsable]
PriorityEvaluator = Callable[[str, str, Categoria | str], EvaluacionPrioridad]
MissingInformationDetector = Callable[[str, str, Categoria | str | None], Sequence[str]]


def obtener_area_responsable(
    categoria: Categoria | str,
    *,
    resolver_area: AreaResolver = _obtener_area_por_reglas,
) -> AreaResponsable:
    """Obtiene el área responsable desde la fuente central de reglas."""

    return resolver_area(_require_text(categoria, "categoria"))


def evaluar_prioridad(
    descripcion: str,
    ubicacion: str,
    categoria: Categoria | str,
    *,
    evaluador: PriorityEvaluator = _evaluar_prioridad_por_reglas,
) -> EvaluacionPrioridad:
    """Devuelve la evaluación Pydantic de prioridad calculada por las reglas."""

    return evaluador(
        _require_text(descripcion, "descripcion"),
        _require_text(ubicacion, "ubicacion"),
        _require_text(categoria, "categoria"),
    )


def detectar_informacion_faltante(
    descripcion: str,
    ubicacion: str,
    categoria: Categoria | str | None = None,
    *,
    detector: MissingInformationDetector = _identificar_informacion_faltante,
) -> list[str]:
    """Devuelve la información faltante detectada por las reglas locales."""

    normalized_category = (
        None if categoria is None else _require_text(categoria, "categoria")
    )
    missing_items = detector(
        _require_text(descripcion, "descripcion"),
        _require_text(ubicacion, "ubicacion"),
        normalized_category,
    )
    return _normalize_text_list(missing_items, "informacion_faltante")


def construir_resumen(descripcion: str, *, max_length: int = 180) -> str:
    """Resume exclusivamente el texto declarado, sin inferir datos adicionales."""

    normalized_description = _normalize_spaces(_require_text(descripcion, "descripcion"))
    if not isinstance(max_length, int) or isinstance(max_length, bool) or max_length < 1:
        raise ValueError("max_length must be a positive integer")
    if len(normalized_description) <= max_length:
        return normalized_description
    if max_length == 1:
        return "…"

    truncated = normalized_description[: max_length - 1]
    last_space = truncated.rfind(" ")
    if last_space > 0:
        truncated = truncated[:last_space]
    return f"{truncated.rstrip(' ,;:.')}…"


def _normalize_text_list(values: Sequence[str], field_name: str) -> list[str]:
    if isinstance(values, (str, bytes)):
        raise TypeError(f"{field_name} must be a sequence of strings")

    normalized_values: list[str] = []
    for value in values:
        normalized_value = _require_text(value, field_name)
        if normalized_value not in normalized_values:
            normalized_values.append(normalized_value)
    return normalized_values


def _require_text(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")

    normalized_value = value.strip()
    if not normalized_value:
        raise ValueError(f"{field_name} must not be empty")
    return normalized_value


def _normalize_spaces(value: str) -> str:
    return " ".join(value.split())
