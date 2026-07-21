-- Alinea el trigger ya aplicado con determinar_estado_inicial del dominio.
-- Es seguro para solicitudes existentes: solo amplía los estados permitidos al insertar.

create or replace function public.validar_transicion_solicitud()
returns trigger
language plpgsql
set search_path = pg_catalog
as $$
begin
    if tg_op = 'INSERT' and new.estado not in (
        'PENDIENTE_REVISION', 'REQUIERE_INFORMACION', 'POSIBLE_DUPLICADO'
    ) then
        raise exception 'Una solicitud nueva debe iniciar pendiente de revisión, requerir información o marcar un posible duplicado.';
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
        raise exception 'Transición de estado no permitida: % a %.', old.estado, new.estado;
    end if;

    return new;
end;
$$;
