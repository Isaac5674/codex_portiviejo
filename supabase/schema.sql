-- Propósito: esquema base reproducible de PortoReporta.
-- Compatibilidad: crea tablas e índices si todavía no existen; no incluye políticas públicas.
-- Reversión: eliminar manualmente las tablas solo en un entorno de desarrollo vacío.

create table if not exists public.solicitudes (
    id bigint generated always as identity primary key,
    descripcion_original text not null,
    resumen text,
    ubicacion text not null,
    categoria text not null check (
        categoria in (
            'AGUA', 'BASURA', 'ALUMBRADO', 'VIALIDAD',
            'ALCANTARILLADO', 'ESPACIO_PUBLICO', 'OTRO'
        )
    ),
    prioridad_agente text not null check (prioridad_agente in ('BAJA', 'MEDIA', 'ALTA')),
    prioridad_final text check (
        prioridad_final is null or prioridad_final in ('BAJA', 'MEDIA', 'ALTA')
    ),
    area_agente text not null,
    area_final text,
    justificacion_agente text not null,
    informacion_faltante jsonb not null default '[]'::jsonb,
    senales_riesgo jsonb not null default '[]'::jsonb,
    posibles_duplicados jsonb not null default '[]'::jsonb,
    origen_analisis text not null default 'REGLAS'
        check (origen_analisis in ('IA', 'REGLAS')),
    estado text not null default 'PENDIENTE_REVISION' check (
        estado in (
            'PENDIENTE_REVISION', 'REQUIERE_INFORMACION', 'APROBADA',
            'MODIFICADA_Y_APROBADA', 'RECHAZADA', 'POSIBLE_DUPLICADO'
        )
    ),
    posible_duplicado_de bigint,
    creado_en timestamptz not null default now(),
    revisado_en timestamptz,
    revisor text,
    motivo_revision text,
    constraint solicitudes_posible_duplicado_fk
        foreign key (posible_duplicado_de)
        references public.solicitudes(id)
        on delete set null
);

create table if not exists public.auditoria (
    id bigint generated always as identity primary key,
    solicitud_id bigint not null,
    actor text not null check (actor in ('CIUDADANO', 'AGENTE', 'OPERADOR', 'SISTEMA')),
    accion text not null,
    detalle jsonb not null default '{}'::jsonb,
    creado_en timestamptz not null default now(),
    constraint auditoria_solicitud_fk
        foreign key (solicitud_id)
        references public.solicitudes(id)
        on delete cascade
);

create index if not exists idx_solicitudes_estado on public.solicitudes (estado);
create index if not exists idx_solicitudes_categoria on public.solicitudes (categoria);
create index if not exists idx_solicitudes_prioridad on public.solicitudes (prioridad_agente);
create index if not exists idx_solicitudes_creado_en on public.solicitudes (creado_en desc);
create index if not exists idx_solicitudes_posible_duplicado_de
    on public.solicitudes (posible_duplicado_de);
create index if not exists idx_auditoria_solicitud_id on public.auditoria (solicitud_id);
create index if not exists idx_auditoria_creado_en on public.auditoria (creado_en);

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

drop trigger if exists validar_transicion_solicitud_trigger on public.solicitudes;
create trigger validar_transicion_solicitud_trigger
before insert or update of estado on public.solicitudes
for each row execute function public.validar_transicion_solicitud();

alter table public.solicitudes enable row level security;
alter table public.auditoria enable row level security;

revoke all on table public.solicitudes from anon, authenticated;
revoke all on table public.auditoria from anon, authenticated;
grant select, insert, update on table public.solicitudes to service_role;
grant select, insert on table public.auditoria to service_role;
grant usage, select on sequence public.solicitudes_id_seq to service_role;
grant usage, select on sequence public.auditoria_id_seq to service_role;
