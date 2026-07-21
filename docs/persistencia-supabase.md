# Persistencia en Supabase

## Base de datos oficial

Supabase es la única base de datos autorizada para PortoReporta.

No utilizar:

- MySQL.
- SQLite.
- Archivos JSON como persistencia oficial.
- CSV como persistencia oficial.
- Variables de sesión como sustituto permanente.
- Otra plataforma de base de datos.

## Variables de entorno

```text
SUPABASE_URL=
SUPABASE_SECRET_KEY=
OPENAI_API_KEY=
APP_ENV=development
```

## Cliente centralizado

El cliente debe crearse únicamente en:

```text
src/supabase_client.py
```

Requisitos:

- Leer variables desde el entorno.
- Fallar con un mensaje claro cuando falte configuración.
- No incluir el valor del secreto en errores.
- No recrear el cliente en cada pantalla.
- No enviar la clave secreta al navegador.

## Repositorio

Todas las operaciones deben pasar por `src/repositories.py`.

Funciones mínimas:

```text
crear_solicitud(datos)
obtener_solicitudes()
obtener_solicitud_por_id(id)
actualizar_solicitud(id, cambios)
registrar_auditoria(datos)
obtener_auditoria_por_solicitud(id)
buscar_candidatos_duplicados(categoria, ubicacion)
```

## Validación de respuestas

Después de una inserción o actualización:

1. Comprobar que no ocurrió una excepción.
2. Comprobar que Supabase devolvió datos.
3. Comprobar que existe el identificador esperado.
4. Registrar auditoría.
5. Informar al usuario únicamente cuando la operación esté confirmada.

## Actualizaciones seguras

- Usar una lista blanca de campos.
- Convertir el ID a un tipo válido.
- No aceptar nombres de tabla del usuario.
- No aceptar nombres de columna del usuario.
- No registrar objetos que contengan secretos.
- No ejecutar SQL generado por IA.

## RLS

Las tablas deben tener Row Level Security activado.

Para el MVP:

- No crear políticas públicas anónimas.
- Usar la clave secreta solo en el servidor Streamlit.
- No exponer el cliente privilegiado al navegador.

## Consistencia con auditoría

Flujo mínimo:

1. Crear o actualizar solicitud.
2. Confirmar respuesta.
3. Crear evento de auditoría.
4. Confirmar auditoría.
5. Mostrar resultado.

Si la auditoría falla:

- Informar que la operación principal pudo completarse, pero el historial quedó incompleto.
- No afirmar trazabilidad completa.
- Permitir reintento.
- Registrar el error en consola sin secretos.

## Cambios de esquema

No modificar tablas o restricciones sin:

- Actualizar `supabase/schema.sql`.
- Actualizar modelos Pydantic.
- Actualizar repositorios.
- Actualizar pruebas.
- Actualizar documentación.
- Verificar compatibilidad con datos existentes.
