"""Pruebas unitarias del coordinador, sin llamadas a OpenAI ni Supabase."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import logging
import sys
import types

import pytest

pytest.importorskip("agents")

from pydantic import BaseModel

from src.agent import AnalysisUnavailableError, analyze_report


class AnalysisForTest(BaseModel):
    resumen: str
    origen_analisis: str


@dataclass
class FakeRunResult:
    final_output: object


class FakeRunner:
    def __init__(self, final_output: object | Exception) -> None:
        self.final_output = final_output
        self.calls = 0

    async def run(self, *_args: object, **_kwargs: object) -> FakeRunResult:
        self.calls += 1
        if isinstance(self.final_output, Exception):
            raise self.final_output
        return FakeRunResult(final_output=self.final_output)


def test_returns_a_revalidated_ai_structured_output() -> None:
    runner = FakeRunner({"resumen": "Luminaria sin funcionar", "origen_analisis": "REGLAS"})

    result = asyncio.run(
        analyze_report(
            "La luminaria no funciona.",
            "Parque central",
            output_model=AnalysisForTest,
            fallback_classifier=lambda _description, _location: AnalysisForTest(
                resumen="No debería usarse", origen_analisis="REGLAS"
            ),
            runner=runner,
        )
    )

    assert isinstance(result, AnalysisForTest)
    assert result.origen_analisis == "IA"
    assert runner.calls == 1


def test_uses_rules_when_the_sdk_returns_an_invalid_output() -> None:
    runner = FakeRunner({"origen_analisis": "IA"})

    result = asyncio.run(
        analyze_report(
            "Hay un hueco peligroso.",
            "Sin especificar",
            output_model=AnalysisForTest,
            fallback_classifier=lambda _description, _location: AnalysisForTest(
                resumen="Hueco reportado", origen_analisis="IA"
            ),
            runner=runner,
        )
    )

    assert result.resumen == "Hueco reportado"
    assert result.origen_analisis == "REGLAS"


def test_uses_fallback_when_the_sdk_returns_invalid_json() -> None:
    runner = FakeRunner("this is not valid JSON for the analysis schema")

    result = asyncio.run(
        analyze_report(
            "Hay una fuga de agua.",
            "Mercado central",
            output_model=AnalysisForTest,
            fallback_classifier=lambda _description, _location: AnalysisForTest(
                resumen="Fuga de agua reportada", origen_analisis="IA"
            ),
            runner=runner,
        )
    )

    assert result.resumen == "Fuga de agua reportada"
    assert result.origen_analisis == "REGLAS"


def test_uses_the_local_rules_module_when_openai_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runner = FakeRunner(RuntimeError("OpenAI unavailable"))
    monkeypatch.setitem(
        sys.modules,
        "src.rules",
        types.SimpleNamespace(
            analizar_reporte_local=lambda description, location: AnalysisForTest(
                resumen=f"{description} en {location}", origen_analisis="IA"
            )
        ),
    )

    result = asyncio.run(
        analyze_report(
            "Hay basura acumulada.",
            "Mercado central",
            output_model=AnalysisForTest,
            runner=runner,
        )
    )

    assert result.resumen == "Hay basura acumulada. en Mercado central"
    assert result.origen_analisis == "REGLAS"


def test_logs_the_openai_failure_reason_before_using_fallback(caplog: pytest.LogCaptureFixture) -> None:
    runner = FakeRunner(RuntimeError("OpenAI unavailable"))

    with caplog.at_level(logging.WARNING, logger="src.agent"):
        result = asyncio.run(
            analyze_report(
                "Hay basura acumulada.",
                "Mercado central",
                output_model=AnalysisForTest,
                fallback_classifier=lambda _description, _location: AnalysisForTest(
                    resumen="Basura reportada", origen_analisis="IA"
                ),
                runner=runner,
            )
        )

    assert result.origen_analisis == "REGLAS"
    assert "reason=RuntimeError" in caplog.text


def test_rejects_empty_input_without_calling_the_agent() -> None:
    runner = FakeRunner({"resumen": "No debe ejecutarse", "origen_analisis": "IA"})

    with pytest.raises(ValueError, match="description"):
        asyncio.run(
            analyze_report(
                "   ",
                "Parque central",
                output_model=AnalysisForTest,
                fallback_classifier=lambda _description, _location: AnalysisForTest(
                    resumen="No debería usarse", origen_analisis="REGLAS"
                ),
                runner=runner,
            )
        )

    assert runner.calls == 0


def test_rejects_missing_location_without_calling_the_agent() -> None:
    runner = FakeRunner({"resumen": "No debe ejecutarse", "origen_analisis": "IA"})

    with pytest.raises(ValueError, match="location"):
        asyncio.run(
            analyze_report(
                "Hay una luminaria apagada.",
                "   ",
                output_model=AnalysisForTest,
                fallback_classifier=lambda _description, _location: AnalysisForTest(
                    resumen="No debería usarse", origen_analisis="REGLAS"
                ),
                runner=runner,
            )
        )

    assert runner.calls == 0


def test_raises_a_controlled_error_when_the_fallback_is_invalid() -> None:
    runner = FakeRunner(RuntimeError("OpenAI unavailable"))

    with pytest.raises(AnalysisUnavailableError):
        asyncio.run(
            analyze_report(
                "Hay basura acumulada.",
                "Mercado central",
                output_model=AnalysisForTest,
                fallback_classifier=lambda _description, _location: {"origen_analisis": "REGLAS"},  # type: ignore[return-value]
                runner=runner,
            )
        )
