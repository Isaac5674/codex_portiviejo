import ast
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.models import (
    AnalisisReporte,
    AreaResponsable,
    Categoria,
    EstadoSolicitud,
    OrigenAnalisis,
    PosibleDuplicado,
    Prioridad,
)
from src.rules import (
    analizar_reporte_local,
    clasificar_reporte,
    determinar_estado_inicial,
    evaluar_prioridad,
    identificar_informacion_faltante,
    obtener_area_responsable,
)


@pytest.mark.parametrize(
    ("descripcion", "ubicacion", "esperada"),
    [
        ("Existe una fuga de agua.", "Frente al mercado", Categoria.AGUA),
        ("Hay basura acumulada.", "Cerca del mercado", Categoria.BASURA),
        ("La luminaria no funciona.", "Parque central", Categoria.ALUMBRADO),
        ("Hay un hueco en la calle.", "Avenida principal", Categoria.VIALIDAD),
        ("La alcantarilla está sin tapa.", "Frente a la escuela", Categoria.ALCANTARILLADO),
        ("Los juegos infantiles están dañados.", "Parque del barrio", Categoria.ESPACIO_PUBLICO),
        ("Necesito ayuda con una situación.", "Barrio central", Categoria.OTRO),
    ],
)
def test_clasificacion_documentada(
    descripcion: str,
    ubicacion: str,
    esperada: Categoria,
) -> None:
    assert clasificar_reporte(descripcion, ubicacion) is esperada


def test_clasificacion_es_determinista_y_tolera_mayusculas_y_acentos() -> None:
    resultados = {
        clasificar_reporte("LÁMPARA dañada", "PARQUE Los Tamarindos")
        for _ in range(10)
    }
    assert resultados == {Categoria.ALUMBRADO}


def test_area_responsable_proviene_del_mapeo_central() -> None:
    assert obtener_area_responsable(Categoria.AGUA) is AreaResponsable.AGUA_POTABLE
    assert obtener_area_responsable("VIALIDAD") is AreaResponsable.OBRAS_PUBLICAS
    with pytest.raises(ValueError):
        obtener_area_responsable("INVENTADA")


def test_prioridad_alta_por_riesgo_y_lugar_sensible() -> None:
    evaluacion = evaluar_prioridad(
        "Hay una alcantarilla sin tapa y casi ocurre un accidente.",
        "Frente a la escuela",
        Categoria.ALCANTARILLADO,
    )
    assert evaluacion.prioridad is Prioridad.ALTA
    assert "alcantarilla abierta" in evaluacion.senales_riesgo
    assert "riesgo de accidente" in evaluacion.senales_riesgo
    assert "cercanía a escuela" in evaluacion.senales_riesgo


def test_escuela_sin_peligro_no_es_suficiente_para_prioridad_alta() -> None:
    evaluacion = evaluar_prioridad(
        "Se solicita mantenimiento general.",
        "Escuela del barrio",
        Categoria.OTRO,
    )
    assert evaluacion.prioridad is Prioridad.BAJA
    assert evaluacion.senales_riesgo == []


def test_prioridad_media_por_afectacion_relevante() -> None:
    evaluacion = evaluar_prioridad(
        "La luminaria del parque no funciona desde hace cuatro noches.",
        "Parque del barrio Los Tamarindos",
        Categoria.ALUMBRADO,
    )
    assert evaluacion.prioridad is Prioridad.MEDIA
    assert evaluacion.senales_riesgo == []


def test_prioridad_baja_por_mantenimiento() -> None:
    evaluacion = evaluar_prioridad(
        "Se necesita mantenimiento por césped alto.",
        "Parque del barrio",
        Categoria.ESPACIO_PUBLICO,
    )
    assert evaluacion.prioridad is Prioridad.BAJA


def test_informacion_faltante_detecta_ubicacion_insuficiente() -> None:
    faltantes = identificar_informacion_faltante(
        "Hay un hueco peligroso.",
        "Sin especificar",
        Categoria.VIALIDAD,
    )
    assert faltantes == ["Ubicación o referencia más precisa"]


def test_informacion_faltante_pide_tipo_cuando_no_hay_evidencia_de_categoria() -> None:
    faltantes = identificar_informacion_faltante(
        "Necesito ayuda con una situación.",
        "Barrio central",
        Categoria.OTRO,
    )
    assert faltantes == ["Tipo de incidente o descripción más específica"]


def test_estado_inicial_depende_de_faltantes_o_candidatos_sin_aprobar() -> None:
    candidato = PosibleDuplicado(solicitud_id=12, similitud=0.84, razon="Misma zona y categoría")
    assert determinar_estado_inicial([]) is EstadoSolicitud.PENDIENTE_REVISION
    assert determinar_estado_inicial(["Ubicación más precisa"]) is EstadoSolicitud.REQUIERE_INFORMACION
    assert determinar_estado_inicial([], [candidato]) is EstadoSolicitud.POSIBLE_DUPLICADO


def test_fallback_local_produce_el_mismo_contrato_estructurado() -> None:
    resultado = analizar_reporte_local(
        "Hay una alcantarilla sin tapa frente a la escuela. Casi ocurre un accidente.",
        "Barrio San José, frente a la escuela",
    )
    assert isinstance(resultado, AnalisisReporte)
    assert resultado.categoria is Categoria.ALCANTARILLADO
    assert resultado.prioridad is Prioridad.ALTA
    assert resultado.area_responsable is AreaResponsable.ALCANTARILLADO
    assert resultado.origen_analisis is OrigenAnalisis.REGLAS
    assert resultado.posibles_duplicados == []


def test_fallback_local_no_inventa_ubicacion() -> None:
    resultado = analizar_reporte_local("Hay un hueco peligroso.", "Sin especificar")
    assert resultado.ubicacion == "Sin especificar"
    assert resultado.informacion_faltante == ["Ubicación o referencia más precisa"]
    assert determinar_estado_inicial(resultado.informacion_faltante) is EstadoSolicitud.REQUIERE_INFORMACION


def test_fallback_rechaza_entrada_vacia_con_error_claro() -> None:
    with pytest.raises(ValidationError, match="descripcion no puede estar vacío"):
        analizar_reporte_local("  ", "Mercado central")


def test_modulos_de_dominio_no_importan_responsabilidades_ajenas() -> None:
    prohibidos = {"streamlit", "openai", "supabase"}
    for ruta in (Path("src/models.py"), Path("src/rules.py")):
        arbol = ast.parse(ruta.read_text(encoding="utf-8"))
        importados = set()
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Import):
                importados.update(alias.name.split(".")[0] for alias in nodo.names)
            elif isinstance(nodo, ast.ImportFrom) and nodo.module:
                importados.add(nodo.module.split(".")[0])
        assert importados.isdisjoint(prohibidos)
