"""Coordinador de análisis de reportes basado en OpenAI Agents SDK.

Este módulo no conoce la interfaz ni la persistencia. Los contratos Pydantic y
el clasificador determinista se reciben explícitamente para conservar la
separación entre la IA, los modelos y las reglas de negocio.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from inspect import isawaitable
import logging
from typing import Any, Protocol, TypeVar

from agents import Agent, Runner
from pydantic import BaseModel, ValidationError


AnalysisModel = TypeVar("AnalysisModel", bound=BaseModel)
FallbackClassifier = Callable[
    [str, str], AnalysisModel | Awaitable[AnalysisModel]
]


logger = logging.getLogger(__name__)


COORDINATOR_INSTRUCTIONS = """
Eres el coordinador de análisis de PortoReporta.

Recibes exclusivamente la descripción y la ubicación declaradas por la
persona. Devuelve únicamente el objeto estructurado solicitado por el esquema.
Resume y recomienda una categoría, prioridad y área responsable cuando exista
evidencia en el reporte. Identifica de forma explícita la información que
falte. No inventes barrios, direcciones, fechas, instituciones, personas,
duraciones, riesgos ni datos no proporcionados.

Tu resultado es solo una recomendación para una revisión humana. Nunca
apruebes o rechaces reportes, no declares un caso resuelto y nunca confirmes
que dos reportes son duplicados. Puedes señalar candidatos como posibles
duplicados únicamente si el esquema lo permite.
""".strip()


class AnalysisUnavailableError(RuntimeError):
    """Señala que ni el agente ni el clasificador de respaldo devolvieron una salida válida."""


class _Runner(Protocol):
    async def run(self, starting_agent: Agent, input: str, *, max_turns: int) -> Any:
        """Ejecuta un agente y devuelve un resultado con ``final_output``."""


def create_coordinator_agent(
    output_model: type[AnalysisModel], *, model: str | None = None
) -> Agent:
    """Crea el único agente coordinador con salida estructurada obligatoria.

    ``output_model`` debe ser el modelo Pydantic de análisis definido por la
    capa de modelos. El SDK lo usa como esquema de salida y ``analyze_report``
    lo valida de nuevo antes de entregar el resultado al resto de la aplicación.
    """

    agent_options: dict[str, Any] = {}
    if model is not None:
        agent_options["model"] = model

    return Agent(
        name="Coordinador de PortoReporta",
        instructions=COORDINATOR_INSTRUCTIONS,
        output_type=output_model,
        **agent_options,
    )


async def analyze_report(
    description: str,
    location: str,
    *,
    output_model: type[AnalysisModel],
    fallback_classifier: FallbackClassifier[AnalysisModel] | None = None,
    coordinator: Agent | None = None,
    runner: _Runner = Runner,
) -> AnalysisModel:
    """Analiza un reporte y devuelve exclusivamente un modelo Pydantic válido.

    Si el SDK no puede responder, produce una salida inválida o no está
    disponible, ejecuta el clasificador local inyectado. El llamador debe pasar
    la función de ``src.rules`` correspondiente; este módulo no replica reglas
    de clasificación ni accede a recursos externos distintos de OpenAI.
    """

    normalized_description = _require_text(description, "description")
    normalized_location = _require_text(location, "location")
    active_coordinator = coordinator or create_coordinator_agent(output_model)

    try:
        result = await runner.run(
            active_coordinator,
            _build_agent_input(normalized_description, normalized_location),
            max_turns=1,
        )
        return _validate_output(result.final_output, output_model, origin="IA")
    except Exception as ai_error:
        logger.warning(
            "OpenAI analysis failed; using local rules fallback. reason=%s",
            _safe_failure_reason(ai_error),
        )
        return await _run_fallback(
            fallback_classifier,
            normalized_description,
            normalized_location,
            output_model,
        )


def _require_text(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")

    normalized_value = value.strip()
    if not normalized_value:
        raise ValueError(f"{field_name} must not be empty")
    return normalized_value


def _build_agent_input(description: str, location: str) -> str:
    return f"Descripción declarada: {description}\nUbicación declarada: {location}"


async def _run_fallback(
    fallback_classifier: FallbackClassifier[AnalysisModel] | None,
    description: str,
    location: str,
    output_model: type[AnalysisModel],
) -> AnalysisModel:
    try:
        classifier = fallback_classifier or _load_local_rules_classifier()
        fallback_output = classifier(description, location)
        if isawaitable(fallback_output):
            fallback_output = await fallback_output
        return _validate_output(fallback_output, output_model, origin="REGLAS")
    except Exception as fallback_error:
        logger.error(
            "Local rules fallback failed. reason=%s",
            _safe_failure_reason(fallback_error),
        )
        raise AnalysisUnavailableError(
            "No fue posible obtener un análisis válido mediante IA ni reglas locales."
        ) from fallback_error


def _load_local_rules_classifier() -> FallbackClassifier[AnalysisModel]:
    """Load the local classifier only when the fallback is needed."""

    from .rules import analizar_reporte_local

    return analizar_reporte_local


def _safe_failure_reason(error: Exception) -> str:
    """Return a useful failure reason without logging secret values."""

    return type(error).__name__


def _validate_output(
    output: object, output_model: type[AnalysisModel], *, origin: str
) -> AnalysisModel:
    """Revalida y marca el origen sin permitir texto libre como resultado."""

    if isinstance(output, BaseModel):
        payload: object = output.model_dump(mode="python")
    else:
        payload = output

    if isinstance(payload, dict):
        payload = {**payload, "origen_analisis": origin}

    try:
        return output_model.model_validate(payload)
    except ValidationError as validation_error:
        raise AnalysisUnavailableError("La respuesta no cumple el contrato de análisis.") from validation_error
