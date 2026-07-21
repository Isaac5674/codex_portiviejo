---
name: integrar-supabase-seguro
description: Implementa o modifica persistencia, tablas, índices, RLS, consultas, repositorios o migraciones de Supabase en PortoReporta sin acoplar la base de datos al resto del código. Úsala para cualquier cambio que lea o escriba datos. No la uses para lógica puramente visual o de dominio que no toca persistencia.
---

# Integrar Supabase de forma segura

## Propósito

Mantener Supabase encapsulado, proteger credenciales, conservar compatibilidad de datos y evitar que un cambio de persistencia rompa la interfaz, el agente o las reglas.

Supabase es la única base de datos oficial del proyecto.

No introducir MySQL ni SQLite como persistencia alternativa.

## Principios

1. Toda consulta pasa por repositorios.
2. La interfaz no conoce detalles de Supabase.
3. Las credenciales solo se leen desde variables de entorno.
4. La clave secreta nunca se expone al navegador, Git, logs ni mensajes.
5. Los modelos Pydantic validan datos antes de persistirlos.
6. Los cambios de esquema se registran mediante SQL reproducible.
7. Los cambios deben ser compatibles o incluir una migración clara.
8. RLS debe permanecer activado.
9. Las operaciones deben informar fallos; no deben fingir éxito.
10. Auditoría y solicitud deben mantenerse consistentes.

## Archivos responsables

```text
src/supabase_client.py
    Configuración y creación del cliente.

src/repositories.py
    Operaciones del dominio sobre Supabase.

src/models.py
    Validación de datos.

supabase/schema.sql
    Esquema base reproducible.

supabase/migrations/
    Cambios incrementales posteriores.

supabase/seed.sql
    Datos de demostración no sensibles.
```

Crear `supabase/migrations/` cuando aparezca el primer cambio posterior al esquema inicial.

## Cliente centralizado

El cliente debe crearse en un único módulo.

Ejemplo conceptual:

```python
import os
from functools import lru_cache

from supabase import Client, create_client


class SupabaseConfigurationError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    url = os.getenv("SUPABASE_URL")
    secret_key = os.getenv("SUPABASE_SECRET_KEY")

    if not url or not secret_key:
        raise SupabaseConfigurationError(
            "Faltan SUPABASE_URL o SUPABASE_SECRET_KEY."
        )

    return create_client(url, secret_key)
```

No crear un cliente nuevo en cada función.

No escribir valores reales como respaldo dentro del código.

## Repositorios

Los nombres de métodos deben representar operaciones del dominio.

Preferido:

```text
crear_solicitud
listar_solicitudes
obtener_solicitud
actualizar_revision
buscar_candidatos_duplicados
registrar_evento_auditoria
listar_auditoria
```

Evitar métodos genéricos expuestos al resto del sistema como:

```text
insertar_en_tabla
actualizar_cualquier_columna
ejecutar_consulta
```

Los repositorios deben controlar:

- Tabla permitida.
- Columnas modificables.
- Conversión de datos.
- Manejo de respuesta vacía.
- Excepciones.
- Ordenamiento.
- Límites de consulta.

## Validación antes de persistir

Flujo obligatorio:

```text
Entrada
  ↓
Modelo Pydantic
  ↓
Conversión a diccionario permitido
  ↓
Repositorio
  ↓
Supabase
```

Nunca enviar directamente a Supabase:

- Diccionarios arbitrarios del usuario.
- Respuestas crudas del modelo.
- Campos no definidos.
- Nombres de tablas.
- Nombres de columnas.
- Valores de estado no validados.

## Campos permitidos para revisión

Una actualización de revisión solo puede modificar, según el caso:

```text
categoria
prioridad_final
area_final
estado
revisado_en
revisor
motivo_revision
posible_duplicado_de
```

No aceptar un diccionario libre desde Streamlit.

Construir el payload explícitamente.

## Cambios de esquema

Antes de modificar el esquema:

1. Revisar `supabase/schema.sql`.
2. Buscar modelos y consultas que usan la tabla.
3. Identificar datos existentes afectados.
4. Elegir una migración compatible.
5. Añadir o actualizar pruebas.
6. Verificar RLS, índices y claves foráneas.
7. Documentar cómo aplicar y revertir el cambio.

## Regla de migraciones

No editar silenciosamente el esquema inicial después de que el proyecto tenga datos compartidos.

Crear archivos ordenados:

```text
supabase/migrations/
├── 001_add_report_source.sql
├── 002_add_request_indexes.sql
└── 003_add_operator_notes.sql
```

Cada migración debe contener:

```sql
-- Propósito:
-- Dependencias:
-- Compatibilidad:
-- Reversión:
```

## Cambios compatibles

Preferir:

- Agregar columnas opcionales.
- Agregar columnas con valor predeterminado.
- Crear tablas nuevas.
- Agregar índices.
- Añadir restricciones después de limpiar datos.
- Mantener temporalmente campos antiguos durante una migración.

Evitar sin planificación:

- Eliminar columnas.
- Renombrar columnas.
- Cambiar tipos incompatibles.
- Hacer obligatorio un campo que tiene valores nulos.
- Eliminar categorías existentes.
- Cambiar significado de estados almacenados.

## Ejemplo: agregar un campo seguro

```sql
alter table public.solicitudes
add column if not exists fuente text
default 'WEB'
check (fuente in ('WEB', 'OPERADOR', 'API'));
```

Después:

1. Actualizar modelo Pydantic.
2. Actualizar repositorio.
3. Añadir prueba.
4. Confirmar que registros anteriores reciben un valor válido.

## Row Level Security

RLS debe estar activado:

```sql
alter table public.solicitudes enable row level security;
alter table public.auditoria enable row level security;
```

Para el MVP:

- No crear políticas anónimas abiertas.
- Usar la clave secreta únicamente en Streamlit del lado servidor.
- No colocar la clave secreta en código frontend.
- No imprimir la clave.
- No incluirla en capturas.

Cuando se agregue autenticación en el futuro:

1. Diseñar roles.
2. Definir políticas mínimas.
3. Probar cada rol.
4. Evitar políticas `using (true)` para escritura sin justificación.

## Auditoría

Toda operación importante debe producir auditoría:

- Creación.
- Análisis del agente.
- Uso del modo de respaldo.
- Modificación humana.
- Aprobación.
- Rechazo.
- Marcado de duplicado.
- Error técnico relevante.

El detalle debe ser JSON estructurado y no contener secretos.

Ejemplo:

```json
{
  "campos_modificados": {
    "prioridad": {
      "anterior": "ALTA",
      "nueva": "MEDIA"
    }
  },
  "motivo": "La zona fue aislada preventivamente."
}
```

## Consistencia

Versión mínima:

1. Ejecutar la operación de solicitud.
2. Confirmar que devolvió datos.
3. Registrar auditoría inmediatamente.
4. Informar si la auditoría falla.
5. No afirmar que el flujo completo terminó si una parte falló.

Versión futura:

- Crear una función PostgreSQL y llamarla mediante RPC para ejecutar ambas acciones dentro de una transacción.

No introducir RPC durante el MVP salvo que la consistencia ya sea un problema real y el flujo principal esté completo.

## Detección de duplicados

Separar:

1. Consulta de candidatos en Supabase.
2. Cálculo de similitud en Python.
3. Presentación como sugerencia.

La consulta puede filtrar por:

- Categoría.
- Fecha reciente.
- Fragmentos de ubicación.
- Estado no rechazado.

No descargar toda la tabla si crece.

No marcar automáticamente un duplicado definitivo.

## Manejo de errores

Crear errores controlados:

```text
SupabaseConfigurationError
RepositoryError
RecordNotFoundError
PersistenceUnavailableError
```

El repositorio debe conservar la excepción original mediante encadenamiento:

```python
raise RepositoryError("No se pudo crear la solicitud.") from exc
```

La interfaz muestra un mensaje útil sin exponer detalles internos.

## Pruebas

Las pruebas unitarias no deben depender siempre de Supabase real.

Usar:

- Cliente simulado.
- Repositorio falso.
- Respuestas controladas.

Mantener una prueba de integración opcional para Supabase real, separada y ejecutada únicamente cuando existan credenciales de prueba.

Nunca usar datos de producción para pruebas.

## Lista de revisión

- [ ] Supabase sigue siendo la única base de datos.
- [ ] El cliente está centralizado.
- [ ] No hay credenciales en el código.
- [ ] `.env` está ignorado.
- [ ] La interfaz no consulta tablas.
- [ ] Los payloads están validados.
- [ ] Las actualizaciones usan campos permitidos.
- [ ] RLS permanece activado.
- [ ] El SQL es reproducible.
- [ ] Hay migración cuando corresponde.
- [ ] Los datos anteriores siguen siendo válidos.
- [ ] La auditoría no contiene secretos.
- [ ] Los errores no fingen éxito.
- [ ] Las pruebas no modifican producción.
