---
name: persistencia-supabase-segura
description: Gestiona cambios de datos y Supabase en PortoReporta de forma centralizada, compatible, auditable y segura, evitando consultas dispersas y migraciones destructivas.
---

# Persistencia segura con Supabase

## Propósito

Usa esta skill siempre que una tarea lea, cree, actualice o elimine información en Supabase, o modifique el esquema PostgreSQL de PortoReporta.

Su objetivo es asegurar que:

- Supabase siga siendo la única base de datos;
- las consultas estén centralizadas;
- los cambios de esquema sean reproducibles;
- las filas existentes continúen siendo válidas;
- las credenciales permanezcan privadas;
- cada decisión importante tenga auditoría;
- la interfaz no dependa directamente del SDK.

## Fuente de verdad

Lee:

1. `docs/contexto-proyecto.md`.
2. `src/supabase_client.py`.
3. `src/repositories.py`.
4. `src/models.py`.
5. `supabase/schema.sql`.
6. migraciones existentes, si el proyecto ya posee `supabase/migrations/`.
7. pruebas de persistencia.

No utilices MySQL ni SQLite como sustituto silencioso.

## Límites de responsabilidad

### `src/supabase_client.py`

Debe:

- leer `SUPABASE_URL`;
- leer `SUPABASE_SECRET_KEY`;
- validar su existencia;
- construir un cliente;
- entregar una única vía de creación del cliente.

No debe:

- consultar tablas;
- contener nombres de categorías;
- implementar reintentos de negocio;
- exponer claves.

### `src/repositories.py`

Debe:

- encapsular consultas;
- transformar respuestas;
- validar que exista información;
- restringir campos actualizables;
- producir errores entendibles para las capas superiores.

No debe:

- importar Streamlit;
- decidir prioridad;
- ejecutar el agente;
- aceptar nombres arbitrarios de tabla;
- aceptar filtros SQL construidos por usuarios.

### `supabase/schema.sql` o migraciones

Debe contener cambios reproducibles e idempotentes cuando sea posible.

Para cambios posteriores al esquema inicial, prefiere una migración nueva en:

```text
supabase/migrations/
```

No modifiques una migración ya aplicada salvo que el proyecto aún no la haya usado en ningún entorno y el equipo lo autorice.

## Principios

### Cambio aditivo primero

Para proteger datos existentes:

1. añade columnas como opcionales o con valor predeterminado;
2. despliega código compatible;
3. rellena datos si es necesario;
4. valida;
5. endurece restricciones después.

Evita agregar directamente una columna `not null` sin valor predeterminado cuando existen filas.

### Compatibilidad de lectura

Durante una transición, el código debe tolerar filas antiguas.

Ejemplo:

```python
prioridad_final = row.get("prioridad_final")
```

No asumas que una migración remota terminó si no fue verificada.

### Fuente única

- categorías y estados: modelos o configuración central;
- datos persistidos: Supabase;
- estado temporal de pantalla: `st.session_state`;
- secretos: variables de entorno.

No dupliques la base en archivos JSON, SQLite o variables globales.

### Operaciones explícitas

Toda función de repositorio debe indicar:

- tabla;
- filtros;
- campos seleccionados;
- orden;
- comportamiento cuando no hay filas;
- error esperado.

Evita `select("*")` cuando la función solo necesita pocos campos, excepto en el MVP cuando simplifique sin exponer datos sensibles.

## Procedimiento para consultas

### Lectura

1. Define la necesidad de datos.
2. Consulta únicamente la tabla correspondiente.
3. Filtra desde Supabase cuando sea razonable.
4. Verifica `response.data`.
5. Devuelve un tipo consistente.
6. No conviertas ausencia de datos en error si el caso es normal.

### Inserción

1. Valida con Pydantic.
2. Construye una lista explícita de campos.
3. Inserta.
4. Verifica que Supabase devolvió la fila.
5. Obtén el identificador.
6. Registra auditoría.
7. Declara éxito solamente después de confirmar.

### Actualización

1. Obtén el caso actual.
2. Verifica que exista.
3. Valida transición y campos permitidos.
4. Crea un diccionario de cambios permitido.
5. Actualiza por identificador.
6. Verifica la respuesta.
7. Registra valores anteriores y nuevos en auditoría.
8. No permita cambiar campos inmutables.

Campos que normalmente no deben editarse después de crear el caso:

- `id`;
- `descripcion_original`, salvo flujo explícito;
- `creado_en`;
- recomendación original del agente, si se desea preservar trazabilidad.

Para decisiones humanas, utiliza campos finales en lugar de sobrescribir la recomendación original.

### Eliminación

La eliminación física queda fuera del MVP.

Si se solicita:

- confirma el requisito;
- evalúa una marca lógica;
- conserva auditoría;
- no borres solicitudes por defecto;
- revisa claves foráneas y retención.

## Auditoría

Toda acción importante debe crear un registro en `auditoria`.

Registrar como mínimo:

- `solicitud_id`;
- `actor`;
- `accion`;
- `detalle`;
- fecha generada por la base.

El detalle debe ser JSON y puede contener:

```json
{
  "valores_anteriores": {},
  "valores_nuevos": {},
  "motivo": "",
  "origen": "interfaz"
}
```

No registrar:

- claves;
- tokens;
- variables de entorno;
- trazas completas con secretos;
- datos personales innecesarios.

## Consistencia

Una actualización de solicitud y su auditoría forman una unidad lógica.

Para el MVP:

1. actualiza;
2. verifica;
3. registra auditoría;
4. si la auditoría falla, no informes operación completamente exitosa.

Para una evolución posterior, utiliza una función PostgreSQL/RPC transaccional.

No ocultes inconsistencias.

## Detección de duplicados

El repositorio debe recuperar candidatos acotados, por ejemplo:

- misma categoría;
- estados activos;
- periodo reciente;
- ubicación semejante.

La comparación textual puede ejecutarse en Python para el MVP.

Nunca marques automáticamente un duplicado definitivo. Devuelve candidatos y puntuaciones.

## Seguridad

### Secretos

- usa `SUPABASE_SECRET_KEY` únicamente en servidor;
- no la incluyas en código;
- no la imprimas;
- no la envíes al navegador;
- no la guardes en auditoría;
- incluye `.env` en `.gitignore`.

### RLS

- mantén RLS activado;
- no abras políticas públicas para facilitar una demo;
- la clave secreta del servidor no sustituye la necesidad de validar en la aplicación;
- no asumas que RLS protege código ejecutado con privilegios elevados.

### Validación

- valida estados;
- valida categorías;
- valida prioridades;
- valida longitud y presencia de texto;
- limita campos actualizables;
- no permita al usuario elegir nombres de tabla o columnas.

## Cambios de esquema

Antes de escribir SQL, entrega:

```markdown
## Motivo del cambio

## Filas existentes afectadas

## Estrategia compatible

## SQL de avance

## Verificación

## Plan de reversión
```

### Reglas SQL

- usa nombres consistentes en `snake_case`;
- usa `timestamptz`;
- crea índices solo para consultas reales;
- evita índices duplicados;
- define claves foráneas;
- elige `on delete` explícitamente;
- usa restricciones `check` cuando protejan invariantes;
- no codifiques secretos en funciones SQL.

### Cambiar una restricción `check`

Para agregar una categoría o estado, no dejes el modelo Python y PostgreSQL desincronizados.

Actualiza:

- enumeración o configuración;
- modelo Pydantic;
- restricción SQL;
- pruebas;
- datos semilla.

### Campos JSONB

Utiliza JSONB para datos variables como:

- señales de riesgo;
- información faltante;
- detalle de auditoría.

No uses JSONB para evitar modelar campos principales que se consultan o validan frecuentemente.

## Pruebas

### Unitarias

Prueba repositorios mediante cliente falso o dependencia inyectada.

Debe cubrir:

- respuesta con datos;
- respuesta vacía;
- error remoto;
- campos no permitidos;
- serialización;
- auditoría.

### Integración

Las pruebas contra Supabase remoto deben:

- estar separadas;
- usar un proyecto o datos de prueba;
- no ejecutarse accidentalmente sin variables;
- limpiar o identificar sus registros;
- no contener secretos.

## Manejo de fallos

Cuando Supabase falla:

- conserva el análisis temporal en `st.session_state`;
- permite reintentar;
- no cambies a otra base;
- no muestres “guardado”;
- registra localmente solo información segura necesaria para diagnóstico;
- explica que la persistencia no fue confirmada.

## Formato de salida obligatorio

```markdown
## Cambio de datos solicitado

## Tablas y funciones afectadas

## Compatibilidad con datos existentes

## SQL o migración

## Cambios de repositorio

## Auditoría

## Seguridad

## Pruebas y verificación

## Riesgos pendientes
```

## Lista de comprobación final

- [ ] Supabase sigue siendo la única base.
- [ ] El cliente está centralizado.
- [ ] No hay consultas en la interfaz.
- [ ] El cambio de esquema es reproducible.
- [ ] Las filas existentes continúan siendo válidas.
- [ ] Modelos y restricciones están sincronizados.
- [ ] Se validan campos actualizables.
- [ ] Se confirma la respuesta antes de declarar éxito.
- [ ] Se registra auditoría.
- [ ] No se exponen secretos.
- [ ] RLS permanece activado.
- [ ] Se probaron respuestas vacías y errores.
