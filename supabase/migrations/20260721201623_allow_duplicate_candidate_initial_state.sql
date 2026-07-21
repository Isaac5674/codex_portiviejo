-- Propósito: permitir que un candidato de duplicado inicie la revisión humana.
-- Dependencias: public.validar_transicion_solicitud creada por initial_portoreporta_schema.
-- Compatibilidad: amplía un estado inicial ya autorizado por el contrato de dominio.
-- Reversión: restaurar la función sin POSIBLE_DUPLICADO en la condición de INSERT.

create or replace function public.validar_transicion_solicitud()
returns trigger
language plpgsql
set search_path = pg_catalog
as $$
begin
    if tg_op = 'INSERT' and new.estado not in (
        'PENDIENTE_REVISION', 'REQUIERE_INFORMACION', 'POSIBLE_DUPLICADO'
    ) then
        raise exception 'A new request must start pending review, require information, or be a possible duplicate.';
    end if;

    if tg_op = 'UPDATE' and new.estado is distinct from old.estado and not (
        (old.estado = 'PENDIENTE_REVISION' and new.estado in (
            'APROBADA', 'MODIFICADA_Y_APROBADA', 'RECHAZADA',
            'REQUIERE_INFORMACION', 'POSIBLE_DUPLICADO'
        ))
        or (old.estado = 'REQUIERE_INFORMACION' and new.estado = 'PENDIENTE_REVISION')
        or (old.estado = 'POSIBLE_DUPLICADO' and new.estado in (
            'APROBADA', 'MODIFICADA_Y_APROBADA', 'RECHAZADA'
        ))
    ) then
        raise exception 'Invalid status transition: % to %.', old.estado, new.estado;
    end if;

    return new;
end;
$$;
