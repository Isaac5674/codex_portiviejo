"""Creación centralizada y segura del cliente de Supabase."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any


class SupabaseConfigurationError(RuntimeError):
    """Se lanza cuando faltan las variables necesarias para Supabase."""


@lru_cache(maxsize=1)
def get_supabase_client() -> Any:
    """Devuelve un único cliente configurado desde las variables de entorno.

    La importación diferida permite ejecutar pruebas unitarias sin una instalación
    local de ``supabase-py`` y mantiene esta dependencia fuera de los módulos de
    dominio.
    """

    url = os.getenv("SUPABASE_URL")
    secret_key = os.getenv("SUPABASE_SECRET_KEY")
    if not url or not secret_key:
        raise SupabaseConfigurationError(
            "Faltan SUPABASE_URL o SUPABASE_SECRET_KEY para conectar con Supabase."
        )

    try:
        from supabase import create_client
    except ImportError as exc:
        raise SupabaseConfigurationError(
            "La dependencia supabase-py no está disponible en este entorno."
        ) from exc

    try:
        return create_client(url, secret_key)
    except Exception as exc:
        raise SupabaseConfigurationError(
            "No fue posible configurar el cliente de Supabase."
        ) from exc


def clear_supabase_client_cache() -> None:
    """Limpia la caché del cliente; se usa al cambiar configuración en pruebas."""

    get_supabase_client.cache_clear()
