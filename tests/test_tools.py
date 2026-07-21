"""Pruebas unitarias de herramientas puras, sin red ni persistencia."""

from __future__ import annotations

import pytest
from unittest.mock import Mock

from src.tools import (
    construir_resumen,
    detectar_informacion_faltante,
    evaluar_prioridad,
    obtener_area_responsable,
)


def test_obtener_area_responsable_delegates_to_the_injected_rule() -> None:
    area = obtener_area_responsable(
        "ALUMBRADO",
        resolver_area=lambda categoria: {"ALUMBRADO": "Alumbrado público"}[categoria],
    )

    assert area == "Alumbrado público"


def test_evaluar_prioridad_returns_a_serializable_rule_result() -> None:
    result = evaluar_prioridad(
        "Hay una alcantarilla sin tapa.",
        "Frente a la escuela",
        "ALCANTARILLADO",
        evaluador=lambda _descripcion, _ubicacion, _categoria: {
            "prioridad": "ALTA",
            "senales": ["alcantarilla abierta", "escuela", "escuela"],
            "justificacion": "Existe riesgo de accidente.",
        },
    )

    assert result == {
        "prioridad": "ALTA",
        "senales": ["alcantarilla abierta", "escuela"],
        "justificacion": "Existe riesgo de accidente.",
    }


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
    area_resolver = Mock(return_value="Alumbrado público")
    priority_evaluator = Mock(
        return_value={
            "prioridad": "MEDIA",
            "senales": ["luminaria dañada"],
            "justificacion": "El problema persiste.",
        }
    )
    missing_information_detector = Mock(return_value=["Referencia del lugar"])

    assert obtener_area_responsable("ALUMBRADO", resolver_area=area_resolver) == "Alumbrado público"
    assert evaluar_prioridad(
        "La luminaria no funciona.",
        "Parque central",
        "ALUMBRADO",
        evaluador=priority_evaluator,
    )["prioridad"] == "MEDIA"
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


def test_construir_resumen_keeps_only_declared_text() -> None:
    summary = construir_resumen("  La   luminaria del parque no funciona desde anoche.  ")

    assert summary == "La luminaria del parque no funciona desde anoche."


def test_construir_resumen_limits_long_text_at_a_word_boundary() -> None:
    summary = construir_resumen("La luminaria del parque no funciona desde hace cuatro noches.", max_length=28)

    assert summary == "La luminaria del parque no…"


def test_tools_reject_invalid_inputs_and_outputs() -> None:
    with pytest.raises(ValueError, match="descripcion"):
        construir_resumen("   ")

    with pytest.raises(TypeError, match="senales"):
        evaluar_prioridad(
            "Hay basura acumulada.",
            "Mercado central",
            "BASURA",
            evaluador=lambda _descripcion, _ubicacion, _categoria: {
                "prioridad": "MEDIA",
                "senales": "basura acumulada",  # type: ignore[typeddict-item]
                "justificacion": "Requiere atención.",
            },
        )
