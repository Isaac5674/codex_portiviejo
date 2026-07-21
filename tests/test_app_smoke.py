"""Pruebas de humo para la estructura visual inicial de PortoReporta."""

import importlib
import asyncio

from streamlit.testing.v1 import AppTest


EXPECTED_SESSION_KEYS = {
    "reporte_actual",
    "analisis_actual",
    "expediente_pendiente",
    "solicitud_seleccionada",
    "error_actual",
}

EXPECTED_NAVIGATION = (
    "Inicio",
    "Crear reporte",
    "Revisión humana",
    "Solicitudes",
    "Historial de auditoría",
)


def test_app_imports_and_exposes_required_structure() -> None:
    app = importlib.import_module("app")

    assert EXPECTED_SESSION_KEYS <= set(app.SESSION_DEFAULTS)
    assert app.NAVIGATION_OPTIONS == EXPECTED_NAVIGATION


def test_initial_session_values_are_empty() -> None:
    app = importlib.import_module("app")

    assert all(value is None for value in app.SESSION_DEFAULTS.values())


def test_payload_uses_domain_state_and_preserves_original_recommendation() -> None:
    app = importlib.import_module("app")
    entry = app.EntradaReporte(
        descripcion="Hay un hueco peligroso.", ubicacion="Sin especificar"
    )
    analysis = app.analizar_reporte_local(entry.descripcion, entry.ubicacion)

    payload = app._analysis_payload(entry, analysis)

    assert payload["estado"] == "REQUIERE_INFORMACION"
    assert payload["categoria"] == "VIALIDAD"
    assert payload["origen_analisis"] == "REGLAS"

    audit_detail = app._analysis_audit_detail(analysis)
    assert audit_detail["categoria_propuesta"] == "VIALIDAD"
    assert audit_detail["prioridad_propuesta"] == "ALTA"
    assert audit_detail["origen_analisis"] == "REGLAS"


def test_human_modification_requires_a_reason() -> None:
    app = importlib.import_module("app")

    try:
        app._review_changes(
            "MODIFICAR_Y_APROBAR",
            7,
            "Operador demo",
            "",
            "VIALIDAD",
            "ALTA",
            "Obras públicas",
            None,
        )
    except ValueError as exc:
        assert "motivo" in str(exc).lower()
    else:
        raise AssertionError("La modificación sin motivo fue aceptada")


def test_case_cannot_be_marked_as_duplicate_of_itself() -> None:
    app = importlib.import_module("app")

    try:
        app._review_changes(
            "MARCAR_POSIBLE_DUPLICADO",
            7,
            "Operador demo",
            "",
            "AGUA",
            "MEDIA",
            "Agua potable",
            7,
        )
    except ValueError as exc:
        assert "sí mismo" in str(exc)
    else:
        raise AssertionError("El expediente fue aceptado como duplicado de sí mismo")


def test_all_navigation_views_render_without_exceptions() -> None:
    app_test = AppTest.from_file("app.py", default_timeout=15).run()

    for view in EXPECTED_NAVIGATION:
        app_test.radio[0].set_value(view)
        app_test.run()
        assert len(app_test.exception) == 0


def test_incomplete_report_uses_visible_local_fallback() -> None:
    app_test = AppTest.from_file("app.py", default_timeout=15).run()
    app_test.radio[0].set_value("Crear reporte")
    app_test.run()
    app_test.text_area[0].set_value("Hay un hueco peligroso.")
    app_test.text_input[0].set_value("Sin especificar")
    app_test.button[0].click()

    app_test.run()

    metrics = {metric.label: metric.value for metric in app_test.metric}
    assert len(app_test.exception) == 0
    assert metrics["Categoría"] == "VIALIDAD"
    assert metrics["Origen"] == "REGLAS"
    assert any("duplicados" in warning.value for warning in app_test.warning)


def test_analysis_uses_agent_contract_when_key_is_configured(monkeypatch) -> None:
    app = importlib.import_module("app")
    entry = app.EntradaReporte(
        descripcion="La luminaria no funciona.", ubicacion="Parque central"
    )
    expected = app.analizar_reporte_local(entry.descripcion, entry.ubicacion).model_copy(
        update={"origen_analisis": app.OrigenAnalisis.IA}
    )
    calls = []

    async def fake_agent(description, location, **kwargs):
        calls.append((description, location, kwargs))
        return expected

    monkeypatch.setenv("OPENAI_API_KEY", "clave-de-prueba-no-real")
    monkeypatch.setattr(app, "analyze_report", fake_agent)

    result = asyncio.run(app._execute_analysis(entry))

    assert result is expected
    assert calls[0][0:2] == (entry.descripcion, entry.ubicacion)
    assert calls[0][2]["output_model"] is app.AnalisisReporte


def test_analysis_skips_openai_when_key_is_missing(monkeypatch) -> None:
    app = importlib.import_module("app")
    entry = app.EntradaReporte(
        descripcion="Hay basura acumulada.", ubicacion="Mercado central"
    )
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = asyncio.run(app._execute_analysis(entry))

    assert result.origen_analisis.value == "REGLAS"
