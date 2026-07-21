-- Propósito: conservar los candidatos de duplicado del análisis validado.
-- Dependencias: public.solicitudes creada por initial_portoreporta_schema.
-- Compatibilidad: agrega una columna no nula con valor predeterminado para filas existentes.
-- Reversión: alter table public.solicitudes drop column posibles_duplicados;

alter table public.solicitudes
add column if not exists posibles_duplicados jsonb not null default '[]'::jsonb;
