"""Herramientas reutilizables para el coordinador de PortoReporta.

Las decisiones de dominio se inyectan desde ``src.rules``. De esta manera las
herramientas validan y adaptan datos sin duplicar la clasificación, las áreas o
las reglas de prioridad.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypedDict


class RecomendacionPrioridad(TypedDict):
    """Estructura serializable de una recomendación determinista de prioridad."""

    prioridad: str
    senales: list[str]
    justificacion: str


AreaResolver = Callable[[str], str]
PriorityEvaluator = Callable[[str, str, str], RecomendacionPrioridad]
MissingInformationDetector = Callable[[str, str, str], Sequence[str]]


def obtener_area_responsable(categoria: str, *, resolver_area: AreaResolver) -> str:
    """Obtiene el área responsable para una categoría mediante una regla inyectada.

    No contiene un mapa propio de categorías; ``resolver_area`` debe provenir
    de la fuente central definida en ``src.rules``.
    """

    normalized_category = _require_text(categoria, "categoria")
    area = resolver_area(normalized_category)
    return _require_text(area, "area_responsable")


def evaluar_prioridad(
    descripcion: str,
    ubicacion: str,
    categoria: str,
    *,
    evaluador: PriorityEvaluator,
) -> RecomendacionPrioridad:
    """Evalúa prioridad y señales delegando la decisión a reglas deterministas.

    La herramienta valida que el resultado sea serializable y completo, pero
    no decide una prioridad ni modifica las señales calculadas por las reglas.
    """

    recommendation = evaluador(
        _require_text(descripcion, "descripcion"),
        _require_text(ubicacion, "ubicacion"),
        _require_text(categoria, "categoria"),
    )
    return _validate_priority_recommendation(recommendation)


def detectar_informacion_faltante(
    descripcion: str,
    ubicacion: str,
    categoria: str,
    *,
    detector: MissingInformationDetector,
) -> list[str]:
    """Devuelve los datos faltantes que detecte una regla determinista inyectada.

    La lista resultante se normaliza y desduplica conservando el orden, sin
    completar información que no fue declarada por la persona.
    """

    missing_items = detector(
        _require_text(descripcion, "descripcion"),
        _require_text(ubicacion, "ubicacion"),
        _require_text(categoria, "categoria"),
    )
    return _normalize_text_list(missing_items, "informacion_faltante")


def construir_resumen(descripcion: str, *, max_length: int = 180) -> str:
    """Construye un resumen acotado a partir del texto declarado, sin inventar datos.

    Si debe acortarlo, corta en un límite de palabra y usa una elipsis. No
    infiere categoría, ubicación, prioridad ni gravedad.
    """

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


def _validate_priority_recommendation(
    recommendation: RecomendacionPrioridad,
) -> RecomendacionPrioridad:
    if not isinstance(recommendation, dict):
        raise TypeError("priority evaluator must return a dictionary")

    priority = _require_text(recommendation.get("prioridad"), "prioridad")
    justification = _require_text(recommendation.get("justificacion"), "justificacion")
    signals = _normalize_text_list(recommendation.get("senales"), "senales")
    return {
        "prioridad": priority,
        "senales": signals,
        "justificacion": justification,
    }


def _normalize_text_list(values: Sequence[str] | object, field_name: str) -> list[str]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
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
