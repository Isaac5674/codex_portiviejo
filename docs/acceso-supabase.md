# Acceso de trabajo a Supabase

Proyecto de PortoReporta:

- [Abrir el panel de Supabase](https://supabase.com/dashboard/project/xdxrurthvkcswooqqzdg)

Para trabajar en la base de datos, cada integrante debe iniciar sesión con su propia cuenta de Supabase y solicitar acceso al responsable del proyecto. El enlace no concede permisos por sí solo.

## Reglas de colaboración

- No compartir ni versionar `SUPABASE_SECRET_KEY`, tokens ni archivos `.env`.
- Revisar [`supabase/schema.sql`](../supabase/schema.sql) antes de modificar tablas, índices, RLS o restricciones.
- Registrar todo cambio posterior como una migración reproducible y actualizar el repositorio, las pruebas y la documentación relacionada.
- Mantener RLS activo y no crear políticas públicas anónimas para la demostración.
- Usar los repositorios de `src/repositories.py`; la interfaz y el agente no deben consultar tablas directamente.

## Estado actual

Las tablas `solicitudes` y `auditoria`, sus índices, el trigger de transiciones y RLS ya están aplicados. Los datos de demostración repetibles están en [`supabase/seed.sql`](../supabase/seed.sql).
