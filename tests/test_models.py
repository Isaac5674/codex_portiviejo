import pytest
from pydantic import ValidationError

from src.models import (
    AREA_POR_CATEGORIA,
    AnalisisReporte,
    AreaResponsable,
    Categoria,
    EntradaReporte,
    EstadoSolicitud,
    OrigenAnalisis,
    PosibleDuplicado,
    Prioridad,
)


def analisis_valido(**cambios: object) -> dict[str, object]:
    datos: dict[str, object] = {
        "resumen": "Alcantarilla sin tapa frente a una escuela",
        "categoria": "ALCANTARILLADO",
        "prioridad": "ALTA",
        "area_responsable": "Alcantarillado",
        "ubicacion": "Barrio San José, frente a la escuela",
        "informacion_faltante": [],
        "senales_riesgo": ["riesgo de accidente"],
        "justificacion": "Se propone prioridad alta por riesgo para peatones.",
        "posibles_duplicados": [],
        "origen_analisis": "IA",
    }
    datos.update(cambios)
    return datos


def test_enumeraciones_coinciden_con_el_contrato_documentado() -> None:
    assert {valor.value for valor in Categoria} == {
        "AGUA",
        "BASURA",
        "ALUMBRADO",
        "VIALIDAD",
        "ALCANTARILLADO",
        "ESPACIO_PUBLICO",
        "OTRO",
    }
    assert {valor.value for valor in Prioridad} == {"BAJA", "MEDIA", "ALTA"}
    assert {valor.value for valor in EstadoSolicitud} == {
        "PENDIENTE_REVISION",
        "REQUIERE_INFORMACION",
        "APROBADA",
        "MODIFICADA_Y_APROBADA",
        "RECHAZADA",
        "POSIBLE_DUPLICADO",
    }


def test_mapeo_cubre_todas_las_categorias() -> None:
    assert set(AREA_POR_CATEGORIA) == set(Categoria)
    assert AREA_POR_CATEGORIA[Categoria.VIALIDAD] is AreaResponsable.OBRAS_PUBLICAS


def test_entrada_limpia_espacios_sin_inventar_contenido() -> None:
    entrada = EntradaReporte(
        descripcion="  Hay   una fuga de agua. ",
        ubicacion=" Mercado   central ",
    )
    assert entrada.descripcion == "Hay una fuga de agua."
    assert entrada.ubicacion == "Mercado central"


@pytest.mark.parametrize("campo", ["descripcion", "ubicacion"])
def test_entrada_rechaza_campos_vacios(campo: str) -> None:
    datos = {"descripcion": "Hay una fuga", "ubicacion": "Mercado central"}
    datos[campo] = "   "
    with pytest.raises(ValidationError, match="no puede estar vacío"):
        EntradaReporte(**datos)


def test_sin_especificar_es_entrada_valida_pero_no_se_normaliza_como_ubicacion_real() -> None:
    entrada = EntradaReporte(descripcion="Hay un hueco peligroso.", ubicacion="Sin especificar")
    assert entrada.ubicacion == "Sin especificar"


def test_analisis_acepta_el_contrato_completo() -> None:
    analisis = AnalisisReporte(**analisis_valido())
    assert analisis.categoria is Categoria.ALCANTARILLADO
    assert analisis.prioridad is Prioridad.ALTA
    assert analisis.origen_analisis is OrigenAnalisis.IA
    assert analisis.model_dump(mode="json")["categoria"] == "ALCANTARILLADO"


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("categoria", "INVENTADA"),
        ("prioridad", "URGENTE"),
        ("origen_analisis", "DESCONOCIDO"),
    ],
)
def test_analisis_rechaza_enumeraciones_inventadas(campo: str, valor: str) -> None:
    with pytest.raises(ValidationError):
        AnalisisReporte(**analisis_valido(**{campo: valor}))


def test_analisis_rechaza_area_que_no_corresponde_a_categoria() -> None:
    with pytest.raises(ValidationError, match="no corresponde a la categoría"):
        AnalisisReporte(**analisis_valido(area_responsable="Obras públicas"))


def test_analisis_exige_justificacion_no_vacia() -> None:
    with pytest.raises(ValidationError, match="justificacion no puede estar vacío"):
        AnalisisReporte(**analisis_valido(justificacion="  "))


def test_analisis_rechaza_listas_con_textos_vacios() -> None:
    with pytest.raises(ValidationError, match="no puede contener textos vacíos"):
        AnalisisReporte(**analisis_valido(informacion_faltante=["  "]))


def test_listas_predeterminadas_no_se_comparten_entre_instancias() -> None:
    primero = AnalisisReporte(**analisis_valido())
    segundo = AnalisisReporte(**analisis_valido())
    primero.informacion_faltante.append("Ubicación más precisa")
    assert segundo.informacion_faltante == []


def test_posible_duplicado_es_solo_un_candidato_validado() -> None:
    candidato = PosibleDuplicado(
        solicitud_id=7,
        similitud=0.82,
        razon="Misma categoría y referencia de ubicación",
    )
    assert candidato.solicitud_id == 7
    with pytest.raises(ValidationError):
        PosibleDuplicado(solicitud_id=7, similitud=1.2, razon="Coincidencia")


def test_analisis_rechaza_campos_ajenos_al_contrato() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        AnalisisReporte(**analisis_valido(aprobada_automaticamente=True))
