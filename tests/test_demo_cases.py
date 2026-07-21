import pytest

from src.models import Categoria, EstadoSolicitud, Prioridad
from src.rules import analizar_reporte_local, determinar_estado_inicial


@pytest.mark.parametrize(
    ("descripcion", "ubicacion", "categoria", "prioridad", "estado"),
    [
        (
            "Hay una alcantarilla sin tapa frente a la escuela del barrio San José. Desde ayer casi ocurre un accidente.",
            "Barrio San José, frente a la escuela",
            Categoria.ALCANTARILLADO,
            Prioridad.ALTA,
            EstadoSolicitud.PENDIENTE_REVISION,
        ),
        (
            "Hay un hueco peligroso.",
            "Sin especificar",
            Categoria.VIALIDAD,
            Prioridad.ALTA,
            EstadoSolicitud.REQUIERE_INFORMACION,
        ),
        (
            "La luminaria del parque no funciona desde hace cuatro noches.",
            "Parque del barrio Los Tamarindos",
            Categoria.ALUMBRADO,
            Prioridad.MEDIA,
            EstadoSolicitud.PENDIENTE_REVISION,
        ),
    ],
)
def test_casos_de_demostracion_del_dominio(
    descripcion: str,
    ubicacion: str,
    categoria: Categoria,
    prioridad: Prioridad,
    estado: EstadoSolicitud,
) -> None:
    analisis = analizar_reporte_local(descripcion, ubicacion)

    assert analisis.categoria is categoria
    assert analisis.prioridad is prioridad
    assert determinar_estado_inicial(
        analisis.informacion_faltante,
        analisis.posibles_duplicados,
    ) is estado


def test_resultado_local_es_consumible_por_las_capas_de_integracion() -> None:
    analisis = analizar_reporte_local(
        "Existe una fuga de agua frente al mercado central.",
        "Mercado central",
    )

    datos = analisis.model_dump(mode="json")
    assert set(datos) == {
        "resumen",
        "categoria",
        "prioridad",
        "area_responsable",
        "ubicacion",
        "informacion_faltante",
        "senales_riesgo",
        "justificacion",
        "posibles_duplicados",
        "origen_analisis",
    }
    assert datos["categoria"] == "AGUA"
    assert datos["origen_analisis"] == "REGLAS"
