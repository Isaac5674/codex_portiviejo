"""Contratos y enumeraciones del dominio de PortoReporta.

Este módulo no realiza efectos secundarios ni depende de la interfaz, OpenAI o
Supabase. Las etiquetas de áreas responsables y su correspondencia con las
categorías viven aquí como una única fuente de verdad contractual.
"""

from __future__ import annotations

from enum import Enum
from types import MappingProxyType
from typing import Mapping

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator, model_validator


class Categoria(str, Enum):
    """Categorías autorizadas para un reporte ciudadano."""

    AGUA = "AGUA"
    BASURA = "BASURA"
    ALUMBRADO = "ALUMBRADO"
    VIALIDAD = "VIALIDAD"
    ALCANTARILLADO = "ALCANTARILLADO"
    ESPACIO_PUBLICO = "ESPACIO_PUBLICO"
    OTRO = "OTRO"


class AreaResponsable(str, Enum):
    """Áreas responsables autorizadas por los contratos del MVP."""

    AGUA_POTABLE = "Agua potable"
    GESTION_AMBIENTAL = "Gestión ambiental"
    ALUMBRADO_PUBLICO = "Alumbrado público"
    OBRAS_PUBLICAS = "Obras públicas"
    ALCANTARILLADO = "Alcantarillado"
    ESPACIOS_PUBLICOS = "Espacios públicos"
    ATENCION_CIUDADANA = "Atención ciudadana"


AREA_POR_CATEGORIA: Mapping[Categoria, AreaResponsable] = MappingProxyType(
    {
        Categoria.AGUA: AreaResponsable.AGUA_POTABLE,
        Categoria.BASURA: AreaResponsable.GESTION_AMBIENTAL,
        Categoria.ALUMBRADO: AreaResponsable.ALUMBRADO_PUBLICO,
        Categoria.VIALIDAD: AreaResponsable.OBRAS_PUBLICAS,
        Categoria.ALCANTARILLADO: AreaResponsable.ALCANTARILLADO,
        Categoria.ESPACIO_PUBLICO: AreaResponsable.ESPACIOS_PUBLICOS,
        Categoria.OTRO: AreaResponsable.ATENCION_CIUDADANA,
    }
)


class Prioridad(str, Enum):
    """Prioridades que el sistema puede recomendar."""

    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


class EstadoSolicitud(str, Enum):
    """Estados autorizados para el ciclo de vida de una solicitud."""

    PENDIENTE_REVISION = "PENDIENTE_REVISION"
    REQUIERE_INFORMACION = "REQUIERE_INFORMACION"
    APROBADA = "APROBADA"
    MODIFICADA_Y_APROBADA = "MODIFICADA_Y_APROBADA"
    RECHAZADA = "RECHAZADA"
    POSIBLE_DUPLICADO = "POSIBLE_DUPLICADO"


class ActorAuditoria(str, Enum):
    """Actores que pueden aparecer posteriormente en la auditoría."""

    CIUDADANO = "CIUDADANO"
    AGENTE = "AGENTE"
    OPERADOR = "OPERADOR"
    SISTEMA = "SISTEMA"


class OrigenAnalisis(str, Enum):
    """Origen verificable de un análisis."""

    IA = "IA"
    REGLAS = "REGLAS"


class ModeloDominio(BaseModel):
    """Configuración común para rechazar campos que no pertenecen al contrato."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class EntradaReporte(ModeloDominio):
    """Entrada mínima proporcionada por el ciudadano."""

    descripcion: str
    ubicacion: str

    @field_validator("descripcion", "ubicacion")
    @classmethod
    def validar_texto_requerido(cls, valor: str, info: object) -> str:
        texto = " ".join(valor.split())
        if not texto:
            nombre = getattr(info, "field_name", "campo")
            raise ValueError(f"{nombre} no puede estar vacío")
        return texto


class PosibleDuplicado(ModeloDominio):
    """Candidato de similitud que todavía requiere decisión humana."""

    solicitud_id: PositiveInt
    similitud: float = Field(ge=0.0, le=1.0)
    razon: str

    @field_validator("razon")
    @classmethod
    def validar_razon(cls, valor: str) -> str:
        texto = " ".join(valor.split())
        if not texto:
            raise ValueError("razon no puede estar vacía")
        return texto


class EvaluacionPrioridad(ModeloDominio):
    """Resultado determinista de evaluar la urgencia recomendada."""

    prioridad: Prioridad
    senales_riesgo: list[str] = Field(default_factory=list)
    justificacion: str

    @field_validator("senales_riesgo")
    @classmethod
    def validar_senales(cls, valores: list[str]) -> list[str]:
        return _validar_lista_de_textos(valores, "senales_riesgo")

    @field_validator("justificacion")
    @classmethod
    def validar_justificacion(cls, valor: str) -> str:
        texto = " ".join(valor.split())
        if not texto:
            raise ValueError("justificacion no puede estar vacía")
        return texto


class AnalisisReporte(ModeloDominio):
    """Salida compartida por el análisis con IA y el fallback por reglas."""

    resumen: str
    categoria: Categoria
    prioridad: Prioridad
    area_responsable: AreaResponsable
    ubicacion: str
    informacion_faltante: list[str] = Field(default_factory=list)
    senales_riesgo: list[str] = Field(default_factory=list)
    justificacion: str
    posibles_duplicados: list[PosibleDuplicado] = Field(default_factory=list)
    origen_analisis: OrigenAnalisis

    @field_validator("resumen", "ubicacion", "justificacion")
    @classmethod
    def validar_textos_de_salida(cls, valor: str, info: object) -> str:
        texto = " ".join(valor.split())
        if not texto:
            nombre = getattr(info, "field_name", "campo")
            raise ValueError(f"{nombre} no puede estar vacío")
        return texto

    @field_validator("informacion_faltante", "senales_riesgo")
    @classmethod
    def validar_listas_de_texto(cls, valores: list[str], info: object) -> list[str]:
        nombre = getattr(info, "field_name", "lista")
        return _validar_lista_de_textos(valores, nombre)

    @model_validator(mode="after")
    def validar_correspondencia_de_area(self) -> "AnalisisReporte":
        area_esperada = AREA_POR_CATEGORIA[self.categoria]
        if self.area_responsable != area_esperada:
            raise ValueError(
                "area_responsable no corresponde a la categoría: "
                f"se esperaba {area_esperada.value}"
            )
        return self


def _validar_lista_de_textos(valores: list[str], nombre: str) -> list[str]:
    """Normaliza espacios sin aceptar elementos vacíos o no informativos."""

    resultado: list[str] = []
    for valor in valores:
        texto = " ".join(valor.split())
        if not texto:
            raise ValueError(f"{nombre} no puede contener textos vacíos")
        resultado.append(texto)
    return resultado
