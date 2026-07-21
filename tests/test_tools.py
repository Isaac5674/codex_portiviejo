"""Pruebas unitarias de herramientas, sin red ni persistencia."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from src.models import AreaResponsable, EvaluacionPrioridad, Prioridad
from src.tools import (
    construir_resumen,
    detectar_informacion_faltante,
    evaluar_prioridad,
    obtener_area_responsable,
)


def _evaluacion_media() -> EvaluacionPrioridad:
    return EvaluacionPrioridad(
        prioridad=Prioridad.MEDIA,
        senales_riesgo=["luminaria dañada"],
        justificacion="El problema persiste.",
    )


def test_obtener_area_responsable_delegates_to_the_injected_rule() -> None:
    area = obtener_area_responsable(
        "ALUMBRADO",
        resolver_area=lambda _categoria: AreaResponsable.ALUMBRADO_PUBLICO,
    )

    assert area is AreaResponsable.ALUMBRADO_PUBLICO


def test_evaluar_prioridad_returns_the_pydantic_rule_result() -> None:
    result = evaluar_prioridad(
        "Hay una alcantarilla sin tapa.",
        "Frente a la escuela",
        "ALCANTARILLADO",
        evaluador=lambda _descripcion, _ubicacion, _categoria: _evaluacion_media(),
    )

    assert isinstance(result, EvaluacionPrioridad)
    assert result.prioridad is Prioridad.MEDIA
    assert result.senales_riesgo == ["luminaria dañada"]


def test_detectar_informacion_faltante_normalizes_the_rule_result() -> None:
    missing_information = detectar_informacion_faltante(
        "Hay un hueco peligroso.",
        "Sin especificar",
        "VIALIDAD",
        detector=lambda _descripcion, _ubicacion, _categoria: [
            " Ubicación más precisa ",
            "Ubicación más precisa",
            "Referencia del lugar",
        ],
    )

    assert missing_information == ["Ubicación más precisa", "Referencia del lugar"]


def test_tool_execution_delegates_each_domain_decision_once() -> None:
    area_resolver = Mock(return_value=AreaResponsable.ALUMBRADO_PUBLICO)
    priority_evaluator = Mock(return_value=_evaluacion_media())
    missing_information_detector = Mock(return_value=["Referencia del lugar"])

    assert obtener_area_responsable("ALUMBRADO", resolver_area=area_resolver) is AreaResponsable.ALUMBRADO_PUBLICO
    assert evaluar_prioridad(
        "La luminaria no funciona.",
        "Parque central",
        "ALUMBRADO",
        evaluador=priority_evaluator,
    ).prioridad is Prioridad.MEDIA
    assert detectar_informacion_faltante(
        "La luminaria no funciona.",
        "Parque central",
        "ALUMBRADO",
        detector=missing_information_detector,
    ) == ["Referencia del lugar"]
    assert construir_resumen("La luminaria no funciona.") == "La luminaria no funciona."

    area_resolver.assert_called_once_with("ALUMBRADO")
    priority_evaluator.assert_called_once_with(
        "La luminaria no funciona.", "Parque central", "ALUMBRADO"
    )
    missing_information_detector.assert_called_once_with(
        "La luminaria no funciona.", "Parque central", "ALUMBRADO"
    )


def test_tools_reject_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="descripcion"):
        construir_resumen("   ")

    with pytest.raises(ValueError):
        obtener_area_responsable("CATEGORIA_INVENTADA")
