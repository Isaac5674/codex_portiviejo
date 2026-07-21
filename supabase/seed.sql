-- Datos de demostración no sensibles. Se pueden ejecutar más de una vez.

with solicitud_semilla as (
    insert into public.solicitudes (
        descripcion_original, resumen, ubicacion, categoria, prioridad_agente,
        area_agente, justificacion_agente, senales_riesgo, origen_analisis
    )
    select
        'Existe una fuga de agua frente al mercado central.',
        'Fuga de agua frente al mercado central',
        'Frente al mercado central',
        'AGUA',
        'MEDIA',
        'Agua potable',
        'Se recomienda atención por desperdicio continuo de agua.',
        '["fuga de agua"]'::jsonb,
        'REGLAS'
    where not exists (
        select 1 from public.solicitudes
        where descripcion_original = 'Existe una fuga de agua frente al mercado central.'
    )
    returning id
)
insert into public.auditoria (solicitud_id, actor, accion, detalle)
select id, 'SISTEMA', 'DATOS_SEMILLA_CREADOS', '{"origen":"seed.sql"}'::jsonb
from solicitud_semilla;
