"""Reglas deterministas y fallback local de PortoReporta."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable, Sequence
from types import MappingProxyType
from typing import Mapping

from .models import (
    AREA_POR_CATEGORIA,
    AnalisisReporte,
    AreaResponsable,
    Categoria,
    EntradaReporte,
    EstadoSolicitud,
    EvaluacionPrioridad,
    OrigenAnalisis,
    PosibleDuplicado,
    Prioridad,
)


SENALES_POR_CATEGORIA: Mapping[Categoria, tuple[str, ...]] = MappingProxyType(
    {
        Categoria.AGUA: (
            "fuga de agua",
            "fuga",
            "tuberia",
            "sin agua",
            "desperdicio de agua",
            "agua potable",
        ),
        Categoria.BASURA: (
            "basura",
            "desechos",
            "recoleccion",
            "botadero",
        ),
        Categoria.ALUMBRADO: (
            "lampara",
            "luminaria",
            "poste sin luz",
            "sin alumbrado",
            "oscuridad",
        ),
        Categoria.VIALIDAD: (
            "hueco",
            "bache",
            "calle danada",
            "via danada",
            "senalizacion",
        ),
        Categoria.ALCANTARILLADO: (
            "alcantarilla",
            "drenaje",
            "sumidero",
            "aguas servidas",
        ),
        Categoria.ESPACIO_PUBLICO: (
            "parque",
            "cancha",
            "juegos infantiles",
            "area comunitaria",
            "espacio publico",
        ),
        Categoria.OTRO: (),
    }
)

_ORDEN_DESEMPATE = (
    Categoria.ALCANTARILLADO,
    Categoria.AGUA,
    Categoria.BASURA,
    Categoria.ALUMBRADO,
    Categoria.VIALIDAD,
    Categoria.ESPACIO_PUBLICO,
)

_UBICACIONES_INSUFICIENTES = frozenset(
    {
        "sin especificar",
        "sin ubicacion",
        "ubicacion desconocida",
        "desconocida",
        "desconocido",
        "no especificada",
        "no especificado",
        "no se",
        "aqui",
    }
)

_SENALES_ALTAS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("riesgo inmediato",), "riesgo inmediato"),
    (("riesgo de accidente", "casi ocurre un accidente", "posible accidente"), "riesgo de accidente"),
    (("alcantarilla sin tapa", "alcantarilla abierta", "sumidero abierto"), "alcantarilla abierta"),
    (("cable expuesto", "cables expuestos"), "cables expuestos"),
    (("poste caido",), "poste caído"),
    (("inundacion", "inundado", "inundada"), "inundación"),
    (("via bloqueada", "calle bloqueada", "completamente bloqueada"), "vía bloqueada"),
    (("fuga grande", "fuga abundante"), "fuga grande"),
    (("falta total de agua", "todo el sector sin agua", "sin agua en todo el sector"), "falta total de agua"),
    (("peligro", "peligroso", "peligrosa"), "peligro mencionado"),
)

_SENALES_MEDIAS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("basura acumulada",), "basura acumulada"),
    (("luminaria danada", "luminaria no funciona", "lampara no funciona"), "luminaria dañada"),
    (("dificulta el transito",), "dificultad de tránsito"),
    (("fuga pequena",), "fuga pequeña"),
    (("hueco", "bache"), "afectación vial"),
    (("deteriorado", "deteriorada"), "deterioro relevante"),
    (("desde hace",), "problema persistente"),
)

_SENALES_BAJAS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("mantenimiento",), "mantenimiento general"),
    (("cesped alto",), "césped alto"),
    (("pintura deteriorada",), "pintura deteriorada"),
    (("dano estetico",), "daño estético"),
)


def normalizar_para_busqueda(texto: str) -> str:
    """Normaliza texto solamente para comparar señales, sin alterar el original."""

    sin_acentos = "".join(
        caracter
        for caracter in unicodedata.normalize("NFKD", texto)
        if not unicodedata.combining(caracter)
    )
    palabras = re.sub(r"[^a-z0-9]+", " ", sin_acentos.casefold())
    return " ".join(palabras.split())


def obtener_area_responsable(categoria: Categoria | str) -> AreaResponsable:
    """Devuelve el área contractual de una categoría o rechaza valores inventados."""

    categoria_valida = categoria if isinstance(categoria, Categoria) else Categoria(categoria)
    return AREA_POR_CATEGORIA[categoria_valida]


def clasificar_reporte(descripcion: str, ubicacion: str) -> Categoria:
    """Clasifica por evidencia explícita en descripción y ubicación."""

    entrada = EntradaReporte(descripcion=descripcion, ubicacion=ubicacion)
    texto = normalizar_para_busqueda(f"{entrada.descripcion} {entrada.ubicacion}")
    puntuaciones = {
        categoria: sum(_contiene(texto, senal) for senal in senales)
        for categoria, senales in SENALES_POR_CATEGORIA.items()
        if categoria is not Categoria.OTRO
    }
    mayor_puntuacion = max(puntuaciones.values(), default=0)
    if mayor_puntuacion == 0:
        return Categoria.OTRO
    return next(
        categoria
        for categoria in _ORDEN_DESEMPATE
        if puntuaciones[categoria] == mayor_puntuacion
    )


def evaluar_prioridad(
    descripcion: str,
    ubicacion: str,
    categoria: Categoria | str,
) -> EvaluacionPrioridad:
    """Sugiere prioridad usando señales documentadas y sin tomar una decisión final."""

    entrada = EntradaReporte(descripcion=descripcion, ubicacion=ubicacion)
    categoria_valida = categoria if isinstance(categoria, Categoria) else Categoria(categoria)
    texto = normalizar_para_busqueda(f"{entrada.descripcion} {entrada.ubicacion}")

    senales_altas = _detectar_senales(texto, _SENALES_ALTAS)
    lugar_sensible = _primera_coincidencia(texto, ("escuela", "hospital"))
    if senales_altas and lugar_sensible:
        senales_altas.append(f"cercanía a {lugar_sensible}")

    if senales_altas:
        return EvaluacionPrioridad(
            prioridad=Prioridad.ALTA,
            senales_riesgo=senales_altas,
            justificacion=(
                "Se propone prioridad alta porque se detectó evidencia de "
                f"{_unir_etiquetas(senales_altas)}."
            ),
        )

    senales_bajas = _detectar_senales(texto, _SENALES_BAJAS)
    if senales_bajas:
        return EvaluacionPrioridad(
            prioridad=Prioridad.BAJA,
            senales_riesgo=[],
            justificacion=(
                "Se propone prioridad baja porque el reporte describe "
                f"{_unir_etiquetas(senales_bajas)} sin evidencia de riesgo inmediato."
            ),
        )

    senales_medias = _detectar_senales(texto, _SENALES_MEDIAS)
    if senales_medias or categoria_valida is not Categoria.OTRO:
        motivos = senales_medias or ["una afectación de servicio que requiere atención"]
        return EvaluacionPrioridad(
            prioridad=Prioridad.MEDIA,
            senales_riesgo=[],
            justificacion=(
                "Se propone prioridad media porque se identificó "
                f"{_unir_etiquetas(motivos)} sin evidencia de peligro inmediato."
            ),
        )

    return EvaluacionPrioridad(
        prioridad=Prioridad.BAJA,
        senales_riesgo=[],
        justificacion=(
            "Se propone prioridad baja porque no se proporcionó evidencia de una "
            "afectación urgente o de riesgo inmediato."
        ),
    )


def identificar_informacion_faltante(
    descripcion: str,
    ubicacion: str,
    categoria: Categoria | str | None = None,
) -> list[str]:
    """Informa ausencias críticas comprobables sin inferir datos no proporcionados."""

    entrada = EntradaReporte(descripcion=descripcion, ubicacion=ubicacion)
    categoria_valida = (
        clasificar_reporte(entrada.descripcion, entrada.ubicacion)
        if categoria is None
        else categoria if isinstance(categoria, Categoria) else Categoria(categoria)
    )
    faltantes: list[str] = []
    if normalizar_para_busqueda(entrada.ubicacion) in _UBICACIONES_INSUFICIENTES:
        faltantes.append("Ubicación o referencia más precisa")
    if categoria_valida is Categoria.OTRO:
        faltantes.append("Tipo de incidente o descripción más específica")
    return faltantes


def determinar_estado_inicial(
    informacion_faltante: Sequence[str],
    posibles_duplicados: Sequence[PosibleDuplicado] = (),
) -> EstadoSolicitud:
    """Determina solamente uno de los estados iniciales autorizados."""

    if informacion_faltante:
        return EstadoSolicitud.REQUIERE_INFORMACION
    if posibles_duplicados:
        return EstadoSolicitud.POSIBLE_DUPLICADO
    return EstadoSolicitud.PENDIENTE_REVISION


def analizar_reporte_local(descripcion: str, ubicacion: str) -> AnalisisReporte:
    """Produce el contrato de análisis mediante reglas, sin servicios externos."""

    entrada = EntradaReporte(descripcion=descripcion, ubicacion=ubicacion)
    categoria = clasificar_reporte(entrada.descripcion, entrada.ubicacion)
    evaluacion = evaluar_prioridad(entrada.descripcion, entrada.ubicacion, categoria)
    informacion_faltante = identificar_informacion_faltante(
        entrada.descripcion,
        entrada.ubicacion,
        categoria,
    )
    return AnalisisReporte(
        resumen=_crear_resumen_extractivo(entrada.descripcion),
        categoria=categoria,
        prioridad=evaluacion.prioridad,
        area_responsable=obtener_area_responsable(categoria),
        ubicacion=entrada.ubicacion,
        informacion_faltante=informacion_faltante,
        senales_riesgo=evaluacion.senales_riesgo,
        justificacion=evaluacion.justificacion,
        posibles_duplicados=[],
        origen_analisis=OrigenAnalisis.REGLAS,
    )


def _contiene(texto: str, senal: str) -> bool:
    patron = rf"(?:^|\s){re.escape(senal)}(?:$|\s)"
    return re.search(patron, texto) is not None


def _detectar_senales(
    texto: str,
    grupos: Iterable[tuple[tuple[str, ...], str]],
) -> list[str]:
    return [
        etiqueta
        for variantes, etiqueta in grupos
        if any(_contiene(texto, variante) for variante in variantes)
    ]


def _primera_coincidencia(texto: str, opciones: Iterable[str]) -> str | None:
    return next((opcion for opcion in opciones if _contiene(texto, opcion)), None)


def _unir_etiquetas(etiquetas: Sequence[str]) -> str:
    if len(etiquetas) == 1:
        return etiquetas[0]
    return ", ".join(etiquetas[:-1]) + f" y {etiquetas[-1]}"


def _crear_resumen_extractivo(descripcion: str, limite: int = 160) -> str:
    """Resume sin inventar: conserva la primera oración o un prefijo literal."""

    texto = " ".join(descripcion.split())
    primera_oracion = re.split(r"(?<=[.!?])\s+", texto, maxsplit=1)[0]
    if len(primera_oracion) <= limite:
        return primera_oracion
    return primera_oracion[: limite - 1].rstrip() + "…"
