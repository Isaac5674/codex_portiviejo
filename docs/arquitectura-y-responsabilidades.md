# Arquitectura y responsabilidades

## Principio de diseño

> La interfaz captura y muestra, el agente interpreta, las reglas validan, los repositorios persisten y el operador decide.

## Componentes

### `app.py`

Responsabilidades:

- Configurar la aplicación Streamlit.
- Mostrar navegación.
- Capturar entradas.
- Mostrar resultados.
- Invocar servicios o funciones de aplicación.
- Mantener estado temporal con `st.session_state`.
- Mostrar errores comprensibles.

No debe:

- Contener todas las reglas de negocio.
- Crear el cliente Supabase en varios lugares.
- Construir SQL.
- Guardar secretos.
- Duplicar categorías o estados.
- Aprobar automáticamente.

### `src/agent.py`

Responsabilidades:

- Configurar el agente coordinador.
- Definir instrucciones del agente.
- Solicitar salida estructurada.
- Ejecutar herramientas autorizadas.
- Convertir fallos de IA en un resultado manejable.
- Delegar al modo local cuando sea necesario.

No debe:

- Escribir directamente en tablas desde múltiples funciones.
- Saltarse Pydantic.
- Tomar decisiones finales.
- Inventar datos faltantes.

### `src/models.py`

Responsabilidades:

- Definir modelos Pydantic.
- Restringir categorías, prioridades y estados.
- Validar listas y campos.
- Normalizar datos cuando sea seguro.
- Rechazar estructuras inválidas.

### `src/rules.py`

Responsabilidades:

- Definir categorías.
- Definir relación categoría-área.
- Definir señales de prioridad.
- Implementar clasificación local.
- Implementar prioridad local.
- Mantener reglas deterministas y testeables.

### `src/tools.py`

Responsabilidades:

- Exponer herramientas al agente.
- Adaptar entradas y salidas.
- Llamar reglas o repositorios.
- Validar parámetros.
- Evitar lógica duplicada.

### `src/supabase_client.py`

Responsabilidades:

- Leer variables de entorno.
- Crear un único cliente reutilizable.
- Validar configuración mínima.
- Producir errores claros sin revelar secretos.

### `src/repositories.py`

Responsabilidades:

- Centralizar operaciones con Supabase.
- Crear solicitudes.
- Consultar solicitudes.
- Actualizar campos permitidos.
- Crear eventos de auditoría.
- Buscar candidatos a duplicados.
- Validar respuestas de Supabase.

### `supabase/schema.sql`

Responsabilidades:

- Crear tablas.
- Crear restricciones.
- Crear índices.
- Activar RLS.
- Mantener el esquema reproducible.

### `supabase/seed.sql`

Responsabilidades:

- Insertar datos de demostración no sensibles.
- Permitir repetir la demo.
- No incluir credenciales.
- No depender de datos reales.

### `tests/`

Responsabilidades:

- Probar reglas.
- Probar modelos.
- Probar repositorios con dobles o mocks cuando sea necesario.
- Probar fallos.
- Probar los casos de demostración.

## Dependencias permitidas entre capas

```text
app.py
  ↓
agent.py / servicios de aplicación
  ↓
tools.py
  ↓
rules.py y repositories.py
  ↓
supabase_client.py
  ↓
Supabase
```

## Dependencias prohibidas

- `rules.py` no debe importar Streamlit.
- `models.py` no debe conectarse a Supabase.
- `supabase_client.py` no debe importar la interfaz.
- `repositories.py` no debe decidir prioridades.
- `app.py` no debe contener consultas repetidas a Supabase.
- El agente no debe construir nombres de tabla a partir de texto del usuario.

## Criterio para crear archivos nuevos

Crear un archivo nuevo solamente cuando:

- Existe una responsabilidad claramente distinta.
- Reduce duplicación real.
- Será usado por más de un flujo.
- Facilita pruebas.
- No añade una capa innecesaria.

Durante el MVP se debe preferir pocos archivos bien definidos.
