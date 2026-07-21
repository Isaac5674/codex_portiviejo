"""Interfaz Streamlit e integración visible de PortoReporta."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
import os
from typing import Any

import streamlit as st
from pydantic import ValidationError

from src.agent import AnalysisUnavailableError, analyze_report
from src.models import (
    AREA_POR_CATEGORIA,
    AnalisisReporte,
    Categoria,
    EntradaReporte,
    EstadoSolicitud,
    OrigenAnalisis,
    PosibleDuplicado,
    Prioridad,
)
from src.repositories import (
    AuditTrailIncompleteError,
    RepositoryError,
    SolicitudesRepository,
)
from src.rules import analizar_reporte_local, determinar_estado_inicial
from src.supabase_client import SupabaseConfigurationError


SESSION_DEFAULTS = {
    "reporte_actual": None,
    "analisis_actual": None,
    "expediente_pendiente": None,
    "solicitud_seleccionada": None,
    "error_actual": None,
    "advertencia_actual": None,
    "solicitudes_cache": None,
    "auditoria_cache": None,
    "auditoria_solicitud_id": None,
    "auditoria_pendiente": None,
}

NAVIGATION_OPTIONS = (
    "Inicio",
    "Crear reporte",
    "Revisión humana",
    "Solicitudes",
    "Historial de auditoría",
)

_PERSISTENCE_ERRORS = (
    RepositoryError,
    SupabaseConfigurationError,
    ValueError,
)


def _initialize_session_state() -> None:
    for key, default_value in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def _repository() -> SolicitudesRepository:
    """Construye el repositorio solo después de una acción explícita."""
    return SolicitudesRepository()


def _clear_messages() -> None:
    st.session_state.error_actual = None
    st.session_state.advertencia_actual = None


def _add_warning(message: str) -> None:
    current = st.session_state.advertencia_actual
    st.session_state.advertencia_actual = f"{current} {message}" if current else message


def _show_messages() -> None:
    if st.session_state.error_actual:
        st.error(st.session_state.error_actual)
    if st.session_state.advertencia_actual:
        st.warning(st.session_state.advertencia_actual)


def _render_home() -> None:
    st.title("PortoReporta")
    st.subheader("Solicitudes ciudadanas organizadas y trazables")
    st.write(
        "PortoReporta recibe un reporte, genera una recomendación estructurada y "
        "la conserva para que una persona pueda revisarla."
    )
    st.warning(
        "PortoReporta es un prototipo académico. No es una plataforma oficial "
        "del Municipio de Portoviejo y no envía reportes a instituciones reales."
    )

    first_column, second_column = st.columns(2)
    with first_column:
        st.markdown("### Recomendación asistida")
        st.write(
            "El sistema propone categoría, prioridad y área responsable. En esta "
            "integración el análisis disponible proviene de reglas locales."
        )
    with second_column:
        st.markdown("### Decisión humana")
        st.write(
            "La IA solo recomienda. Aprobar, modificar, rechazar, solicitar "
            "información o marcar un posible duplicado requiere revisión humana."
        )

    st.info(
        "Con una OPENAI_API_KEY configurada, el agente produce una salida "
        "estructurada. Si OpenAI no está disponible, el sistema continúa con "
        "reglas locales y muestra el origen real del análisis."
    )


def _analyze_report(descripcion: str, ubicacion: str) -> None:
    _clear_messages()
    try:
        entrada = EntradaReporte(descripcion=descripcion, ubicacion=ubicacion)
        analisis = asyncio.run(_execute_analysis(entrada))
    except ValidationError as exc:
        st.session_state.error_actual = _validation_message(exc)
        return
    except (AnalysisUnavailableError, RuntimeError):
        st.session_state.error_actual = (
            "No fue posible obtener un análisis válido mediante IA ni reglas locales."
        )
        return

    st.session_state.reporte_actual = entrada
    st.session_state.analisis_actual = analisis
    st.session_state.expediente_pendiente = None

    if analisis.origen_analisis.value == "REGLAS":
        _add_warning(
            "El análisis se realizó con reglas locales porque OpenAI no está "
            "configurado o no pudo responder."
        )

    try:
        candidates = _repository().buscar_candidatos_duplicados(
            analisis.categoria.value,
            analisis.ubicacion,
            entrada.descripcion,
        )
        st.session_state.analisis_actual = analisis.model_copy(
            update={"posibles_duplicados": candidates}
        )
    except _PERSISTENCE_ERRORS:
        _add_warning(
            "El análisis se completó, pero la búsqueda de posibles "
            "duplicados no estuvo disponible. No se marcó ningún duplicado."
        )


async def _execute_analysis(entrada: EntradaReporte) -> AnalisisReporte:
    """Usa el agente cuando está configurado y reglas cuando falta la clave."""
    if not os.getenv("OPENAI_API_KEY"):
        return analizar_reporte_local(entrada.descripcion, entrada.ubicacion)
    return await analyze_report(
        entrada.descripcion,
        entrada.ubicacion,
        output_model=AnalisisReporte,
        fallback_classifier=analizar_reporte_local,
    )


def _validation_message(exc: ValidationError) -> str:
    first_error = exc.errors()[0] if exc.errors() else {}
    return str(first_error.get("msg", "La entrada no es válida.")).removeprefix(
        "Value error, "
    )


def _analysis_audit_detail(analisis: AnalisisReporte) -> dict[str, Any]:
    return {
        "origen_analisis": analisis.origen_analisis.value,
        "categoria_propuesta": analisis.categoria.value,
        "prioridad_propuesta": analisis.prioridad.value,
        "area_propuesta": analisis.area_responsable.value,
        "senales_riesgo": analisis.senales_riesgo,
        "informacion_faltante": analisis.informacion_faltante,
        "posibles_duplicados": [
            candidate.solicitud_id for candidate in analisis.posibles_duplicados
        ],
    }


def _create_case() -> None:
    _clear_messages()
    entrada = st.session_state.reporte_actual
    analisis = st.session_state.analisis_actual
    if not isinstance(entrada, EntradaReporte) or not isinstance(
        analisis, AnalisisReporte
    ):
        st.session_state.error_actual = "Primero debe completar un análisis válido."
        return

    try:
        audit_detail = _analysis_audit_detail(analisis)
        estado = determinar_estado_inicial(
            analisis.informacion_faltante,
            analisis.posibles_duplicados,
        )
        solicitud = _repository().crear_solicitud_desde_analisis(
            entrada,
            analisis,
            estado,
            actor="CIUDADANO",
            detalle_auditoria=audit_detail,
        )
    except AuditTrailIncompleteError as exc:
        st.session_state.expediente_pendiente = exc.solicitud
        st.session_state.auditoria_pendiente = {
            "solicitud_id": exc.solicitud["id"],
            "estado": exc.solicitud.get("estado"),
            "detalle": audit_detail,
        }
        st.session_state.error_actual = (
            "La solicitud fue creada, pero su auditoría no quedó confirmada. "
            "No repita la creación; solicite revisar la trazabilidad."
        )
        return
    except _PERSISTENCE_ERRORS:
        st.session_state.error_actual = (
            "No se confirmó la creación en Supabase. El análisis permanece "
            "temporalmente disponible para reintentar."
        )
        return

    st.session_state.expediente_pendiente = solicitud
    st.session_state.auditoria_pendiente = None
    st.session_state.solicitudes_cache = None
    st.success(f"Expediente #{solicitud['id']} creado y auditado correctamente.")


def _retry_creation_audit() -> None:
    pending = st.session_state.auditoria_pendiente
    if not isinstance(pending, dict):
        st.session_state.error_actual = "No existe una auditoría pendiente para reintentar."
        return
    detail = {
        "origen": "repositorio",
        "estado": pending.get("estado"),
        **pending["detalle"],
    }
    try:
        _repository().registrar_evento_auditoria(
            pending["solicitud_id"],
            "CIUDADANO",
            "SOLICITUD_CREADA",
            detail,
        )
    except _PERSISTENCE_ERRORS:
        st.session_state.error_actual = (
            "La auditoría continúa sin confirmarse. La solicitud no fue creada otra vez."
        )
        return
    st.session_state.auditoria_pendiente = None
    st.session_state.error_actual = None
    st.success("La auditoría pendiente quedó confirmada sin repetir la solicitud.")


def _render_analysis() -> None:
    analisis = st.session_state.analisis_actual
    if not isinstance(analisis, AnalisisReporte):
        st.info("Complete el formulario para obtener un análisis validado.")
        return

    st.markdown("### Análisis estructurado")
    first_column, second_column, third_column = st.columns(3)
    first_column.metric("Categoría", analisis.categoria.value)
    second_column.metric("Prioridad recomendada", analisis.prioridad.value)
    third_column.metric("Origen", analisis.origen_analisis.value)
    st.write(f"**Resumen:** {analisis.resumen}")
    st.write(f"**Área responsable sugerida:** {analisis.area_responsable.value}")
    st.write(f"**Justificación:** {analisis.justificacion}")
    st.write("**Información faltante:**")
    st.write(analisis.informacion_faltante or "Ninguna detectada")
    st.write("**Señales de riesgo:**")
    st.write(analisis.senales_riesgo or "Ninguna detectada")

    st.write("**Posibles duplicados:**")
    if analisis.posibles_duplicados:
        st.dataframe(
            [candidate.model_dump(mode="json") for candidate in analisis.posibles_duplicados],
            hide_index=True,
            use_container_width=True,
        )
        st.caption("Son candidatos; la coincidencia no confirma un duplicado.")
    else:
        st.write("No se encontraron candidatos o la búsqueda no estuvo disponible.")

    estado = determinar_estado_inicial(
        analisis.informacion_faltante, analisis.posibles_duplicados
    )
    st.write(f"**Estado inicial propuesto por las reglas:** {estado.value}")
    st.button("Confirmar y crear expediente", on_click=_create_case)
    if st.session_state.auditoria_pendiente:
        st.button("Reintentar solo auditoría", on_click=_retry_creation_audit)


def _render_report_creation() -> None:
    st.title("Crear reporte")
    st.write("Describe el problema y proporciona una ubicación o referencia.")
    with st.form("citizen_report_form"):
        descripcion = st.text_area(
            "Descripción del problema",
            placeholder="Describe lo ocurrido sin incluir datos personales innecesarios.",
        )
        ubicacion = st.text_input(
            "Ubicación o referencia",
            placeholder="Ejemplo: barrio y punto de referencia",
        )
        submitted = st.form_submit_button("Analizar reporte", use_container_width=True)
    if submitted:
        _analyze_report(descripcion, ubicacion)
    _show_messages()
    _render_analysis()


def _load_requests() -> list[dict[str, Any]]:
    try:
        requests = _repository().listar_solicitudes()
    except _PERSISTENCE_ERRORS:
        st.session_state.error_actual = (
            "No fue posible consultar las solicitudes en Supabase."
        )
        st.session_state.solicitudes_cache = []
        return []
    st.session_state.solicitudes_cache = requests
    return requests


def _requests() -> list[dict[str, Any]]:
    cached = st.session_state.solicitudes_cache
    return cached if isinstance(cached, list) else _load_requests()


def _review_changes(
    action: str,
    request_id: int,
    reviewer: str,
    reason: str,
    category: str,
    priority: str,
    area: str,
    duplicate_id: int | None,
) -> dict[str, Any]:
    common = {"revisor": reviewer.strip(), "revisado_en": datetime.now(UTC).isoformat()}
    if not common["revisor"]:
        raise ValueError("El nombre del operador es obligatorio.")
    if action == "APROBAR":
        return {**common, "estado": EstadoSolicitud.APROBADA.value}
    if action == "MODIFICAR_Y_APROBAR":
        if not reason.strip():
            raise ValueError("El motivo es obligatorio al modificar la recomendación.")
        return {
            **common,
            "categoria": category,
            "prioridad_final": priority,
            "area_final": area,
            "motivo_revision": reason.strip(),
            "estado": EstadoSolicitud.MODIFICADA_Y_APROBADA.value,
        }
    if action == "RECHAZAR":
        if not reason.strip():
            raise ValueError("El motivo del rechazo es obligatorio.")
        return {
            **common,
            "motivo_revision": reason.strip(),
            "estado": EstadoSolicitud.RECHAZADA.value,
        }
    if action == "SOLICITAR_INFORMACION":
        if not reason.strip():
            raise ValueError("Indique qué información adicional se necesita.")
        return {
            **common,
            "motivo_revision": reason.strip(),
            "estado": EstadoSolicitud.REQUIERE_INFORMACION.value,
        }
    if action == "MARCAR_POSIBLE_DUPLICADO":
        if not duplicate_id:
            raise ValueError("Indique el expediente candidato a duplicado.")
        if duplicate_id == request_id:
            raise ValueError("Un expediente no puede ser posible duplicado de sí mismo.")
        return {
            **common,
            "motivo_revision": reason.strip() or "Candidato marcado por el operador.",
            "posible_duplicado_de": duplicate_id,
            "estado": EstadoSolicitud.POSIBLE_DUPLICADO.value,
        }
    if action == "REENVIAR_A_REVISION":
        return {**common, "estado": EstadoSolicitud.PENDIENTE_REVISION.value}
    raise ValueError("La acción de revisión no está permitida.")


def _apply_review(request: dict[str, Any], changes: dict[str, Any], action: str) -> None:
    _clear_messages()
    try:
        updated = _repository().actualizar_solicitud(
            request["id"], changes, actor="OPERADOR", accion=action
        )
    except AuditTrailIncompleteError:
        st.session_state.error_actual = (
            "La solicitud fue actualizada, pero la auditoría no quedó confirmada."
        )
        return
    except _PERSISTENCE_ERRORS as exc:
        st.session_state.error_actual = str(exc)
        return
    st.session_state.solicitud_seleccionada = updated
    st.session_state.solicitudes_cache = None
    st.session_state.auditoria_cache = None
    st.success(f"La revisión del expediente #{updated['id']} quedó confirmada y auditada.")


def _allowed_actions(state: str) -> tuple[str, ...]:
    if state == EstadoSolicitud.PENDIENTE_REVISION.value:
        return (
            "APROBAR",
            "MODIFICAR_Y_APROBAR",
            "RECHAZAR",
            "SOLICITAR_INFORMACION",
            "MARCAR_POSIBLE_DUPLICADO",
        )
    if state == EstadoSolicitud.REQUIERE_INFORMACION.value:
        return ("REENVIAR_A_REVISION",)
    if state == EstadoSolicitud.POSIBLE_DUPLICADO.value:
        return ("APROBAR", "MODIFICAR_Y_APROBAR", "RECHAZAR")
    return ()


def _render_human_review() -> None:
    st.title("Revisión humana")
    _clear_messages()
    requests = _requests()
    _show_messages()
    if not requests:
        st.info("No hay solicitudes disponibles para revisión.")
        if st.button("Reintentar consulta"):
            st.session_state.solicitudes_cache = None
            st.rerun()
        return

    request_by_id = {request["id"]: request for request in requests}
    selected_id = st.selectbox("Solicitud", tuple(request_by_id), format_func=lambda value: f"#{value}")
    request = request_by_id[selected_id]
    st.session_state.solicitud_seleccionada = request
    st.write(f"**Estado actual:** {request.get('estado', 'No disponible')}")
    st.write(f"**Resumen:** {request.get('resumen') or request.get('descripcion_original')}")
    st.write(f"**Recomendación:** {request.get('categoria')} · {request.get('prioridad_agente')} · {request.get('area_agente')}")
    if request.get("prioridad_final") or request.get("area_final"):
        st.write(
            "**Decisión final registrada:** "
            f"{request.get('categoria')} · "
            f"{request.get('prioridad_final') or request.get('prioridad_agente')} · "
            f"{request.get('area_final') or request.get('area_agente')}"
        )
    if request.get("motivo_revision"):
        st.write(f"**Motivo de revisión:** {request['motivo_revision']}")

    actions = _allowed_actions(str(request.get("estado", "")))
    if not actions:
        st.info("Este expediente ya no admite una transición desde la interfaz del MVP.")
        return

    with st.form("human_review_form"):
        reviewer = st.text_input("Operador")
        categories = tuple(item.value for item in Categoria)
        category_value = str(request.get("categoria", Categoria.OTRO.value))
        category = st.selectbox(
            "Categoría final",
            categories,
            index=categories.index(category_value) if category_value in categories else 0,
        )
        priorities = tuple(item.value for item in Prioridad)
        priority_value = str(
            request.get("prioridad_final") or request.get("prioridad_agente", Prioridad.MEDIA.value)
        )
        priority = st.selectbox(
            "Prioridad final",
            priorities,
            index=priorities.index(priority_value) if priority_value in priorities else 0,
        )
        area = AREA_POR_CATEGORIA[Categoria(category)].value
        st.text_input("Área final", value=area, disabled=True)
        reason = st.text_area("Motivo de la revisión")
        duplicate_id = st.number_input(
            "ID del posible duplicado", min_value=0, step=1, value=0
        )
        action = st.selectbox("Acción humana", actions)
        confirm_rejection = st.checkbox("Confirmo el rechazo")
        submitted = st.form_submit_button("Registrar revisión", use_container_width=True)

    if submitted:
        if action == "RECHAZAR" and not confirm_rejection:
            st.session_state.error_actual = "Debe confirmar expresamente el rechazo."
        else:
            try:
                changes = _review_changes(
                    action,
                    int(request["id"]),
                    reviewer,
                    reason,
                    category,
                    priority,
                    area,
                    int(duplicate_id) or None,
                )
            except ValueError as exc:
                st.session_state.error_actual = str(exc)
            else:
                _apply_review(request, changes, action)
        _show_messages()


def _render_requests() -> None:
    st.title("Solicitudes")
    _clear_messages()
    if st.button("Actualizar listado"):
        st.session_state.solicitudes_cache = None
    requests = _requests()
    _show_messages()
    if requests:
        st.dataframe(requests, hide_index=True, use_container_width=True)
    else:
        st.info("No hay solicitudes disponibles o la consulta no pudo completarse.")


def _render_audit_history() -> None:
    st.title("Historial de auditoría")
    _clear_messages()
    requests = _requests()
    if not requests:
        _show_messages()
        st.info("No hay expedientes disponibles para consultar.")
        return

    request_ids = tuple(request["id"] for request in requests)
    selected_id = st.selectbox(
        "Expediente", request_ids, format_func=lambda value: f"#{value}"
    )
    if st.button("Consultar historial"):
        try:
            st.session_state.auditoria_cache = _repository().obtener_auditoria_por_solicitud(
                selected_id
            )
            st.session_state.auditoria_solicitud_id = selected_id
        except _PERSISTENCE_ERRORS:
            st.session_state.error_actual = (
                "No fue posible consultar el historial de auditoría."
            )
    _show_messages()
    events = st.session_state.auditoria_cache
    if (
        isinstance(events, list)
        and st.session_state.auditoria_solicitud_id == selected_id
    ):
        if events:
            st.dataframe(events, hide_index=True, use_container_width=True)
        else:
            st.info("El expediente no tiene eventos disponibles.")
    else:
        st.info("Seleccione un expediente y consulte su historial.")


def _main() -> None:
    st.set_page_config(
        page_title="PortoReporta",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _initialize_session_state()
    st.sidebar.title("PortoReporta")
    selected_view = st.sidebar.radio("Navegación", NAVIGATION_OPTIONS)
    st.sidebar.divider()
    st.sidebar.caption("Prototipo no oficial. La IA recomienda y una persona decide.")

    renderers = {
        "Inicio": _render_home,
        "Crear reporte": _render_report_creation,
        "Revisión humana": _render_human_review,
        "Solicitudes": _render_requests,
        "Historial de auditoría": _render_audit_history,
    }
    renderers[selected_view]()


_main()
