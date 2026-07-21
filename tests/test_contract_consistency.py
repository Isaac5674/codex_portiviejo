"""Verificaciones de coherencia entre el dominio y el esquema reproducible."""

from pathlib import Path

import pytest

from src.models import EstadoSolicitud, PosibleDuplicado
from src.rules import determinar_estado_inicial


SCHEMA_PATH = Path("supabase/schema.sql")
MIGRATION_PATH = Path("supabase/migrations/20260721201623_allow_duplicate_candidate_initial_state.sql")


@pytest.mark.parametrize(
    ("faltantes", "duplicados", "estado_esperado"),
    [
        ([], [], EstadoSolicitud.PENDIENTE_REVISION),
        (["Ubicación o referencia más precisa"], [], EstadoSolicitud.REQUIERE_INFORMACION),
        (
            [],
            [
                PosibleDuplicado(
                    solicitud_id=1,
                    similitud=0.8,
                    razon="Misma categoría y ubicación aproximada",
                )
            ],
            EstadoSolicitud.POSIBLE_DUPLICADO,
        ),
    ],
)
def test_el_esquema_acepta_todos_los_estados_iniciales_del_dominio(
    faltantes: list[str],
    duplicados: list[PosibleDuplicado],
    estado_esperado: EstadoSolicitud,
) -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    migration = MIGRATION_PATH.read_text(encoding="utf-8")
    estado = determinar_estado_inicial(faltantes, duplicados)

    assert estado is estado_esperado
    assert f"'{estado.value}'" in _bloque_de_estados_iniciales(schema)
    assert f"'{estado.value}'" in _bloque_de_estados_iniciales(migration)


def _bloque_de_estados_iniciales(schema: str) -> str:
    inicio = schema.index("if tg_op = 'INSERT'")
    fin = schema.index("if tg_op = 'UPDATE'", inicio)
    return schema[inicio:fin]
