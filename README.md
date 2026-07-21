# PortoReporta

Prototipo para recibir solicitudes ciudadanas, analizarlas de forma estructurada, sugerir categoría y prioridad, detectar posibles duplicados y someter cada expediente a revisión humana. Supabase con PostgreSQL es la única persistencia oficial y Streamlit es la interfaz del MVP.

> PortoReporta es un prototipo académico o de hackatón. No es una plataforma oficial del Municipio de Portoviejo y no envía reportes a instituciones reales.

## Aplicación publicada

La interfaz está disponible en [porto-reporta.vercel.app](https://porto-reporta.vercel.app). Sin credenciales de OpenAI utiliza reglas locales; las funciones de persistencia requieren configurar Supabase en Vercel.

## Principio del proyecto

> La interfaz captura y muestra, el agente interpreta y recomienda, las reglas validan, los repositorios persisten y una persona toma la decisión final.

## División del trabajo para cuatro integrantes

La división sigue los límites definidos en [`docs/arquitectura-y-responsabilidades.md`](docs/arquitectura-y-responsabilidades.md) y las fases de [`docs/plan-de-trabajo-codex.md`](docs/plan-de-trabajo-codex.md).

### Integrante 1 — Dominio, contratos y reglas

Responsabilidad principal: definir el comportamiento válido del sistema sin depender de Streamlit, OpenAI o Supabase.

Se encargará de:

- Mantener los modelos Pydantic y las enumeraciones autorizadas.
- Centralizar categorías, áreas responsables, prioridades y estados.
- Implementar validaciones de descripción y ubicación.
- Implementar clasificación y prioridad mediante reglas deterministas.
- Identificar información faltante.
- Mantener el modo local que se utiliza cuando falla la IA.
- Alinear contratos y reglas con la documentación funcional.
- Crear pruebas unitarias de modelos y reglas.

Archivos principales:

- `src/models.py`
- `src/rules.py`
- `tests/test_models.py`
- `tests/test_rules.py`
- `docs/contratos-de-datos.md`
- `docs/reglas-de-negocio.md`
- `docs/flujos-y-estados.md`

Entregable verificable:

> Una entrada válida o inválida puede procesarse mediante reglas locales y siempre produce —o rechaza— una estructura Pydantic coherente.

### Integrante 2 — Agente de IA, herramientas y fallback

Responsabilidad principal: convertir la entrada ciudadana en una recomendación estructurada, trazable y limitada.

Se encargará de:

- Configurar el agente coordinador con OpenAI Agents SDK.
- Mantener instrucciones y salida estructurada del agente.
- Implementar herramientas pequeñas, tipadas y con una sola responsabilidad.
- Validar las respuestas de IA mediante los modelos del Integrante 1.
- Activar el modo local del Integrante 1 cuando OpenAI falle.
- Mantener la IA sin autoridad para aprobar, rechazar o confirmar duplicados.
- Informar claramente si el análisis provino de IA o de reglas.
- Crear pruebas del agente, herramientas, salidas inválidas y fallback.

Archivos principales:

- `src/agent.py`
- `src/tools.py`
- Pruebas del agente y sus herramientas dentro de `tests/`
- `docs/manejo-de-errores.md`

Entregable verificable:

> El mismo reporte produce un análisis válido tanto con OpenAI disponible como con el modo local, sin inventar información ni tomar decisiones humanas.

### Integrante 3 — Supabase, repositorios, seguridad y auditoría

Responsabilidad principal: garantizar persistencia reproducible, consultas centralizadas y trazabilidad segura.

Se encargará de:

- Crear y mantener el esquema de Supabase.
- Configurar tablas, restricciones, índices y RLS.
- Crear el cliente centralizado de Supabase.
- Implementar repositorios para crear, consultar, listar y actualizar solicitudes.
- Implementar búsqueda de candidatos a posibles duplicados.
- Registrar y consultar eventos de auditoría.
- Validar las respuestas de Supabase antes de informar éxito.
- Proteger credenciales y restringir los campos actualizables.
- Crear pruebas de repositorios, auditoría y fallos de persistencia.

Archivos principales:

- `src/supabase_client.py`
- `src/repositories.py`
- `supabase/schema.sql`
- `supabase/seed.sql`
- Pruebas de persistencia dentro de `tests/`
- `docs/persistencia-supabase.md`
- `docs/seguridad-y-privacidad.md`

Entregable verificable:

> Una solicitud puede crearse, consultarse y actualizarse en Supabase; las acciones quedan auditadas, RLS permanece activo y ningún secreto aparece en el repositorio o los logs.

### Integrante 4 — Streamlit, revisión humana, integración y entrega

Responsabilidad principal: unir las capacidades anteriores en un flujo comprensible, revisable y demostrable.

Se encargará de:

- Crear la interfaz Streamlit y su navegación.
- Implementar formulario de reporte y presentación del análisis.
- Permitir que el ciudadano confirme la creación del expediente.
- Implementar revisión humana: aprobar, modificar, rechazar, solicitar información o marcar posible duplicado.
- Mostrar solicitudes, estados e historial de auditoría.
- Manejar el estado temporal y los errores visibles sin fingir éxito.
- Integrar los módulos de los Integrantes 1, 2 y 3.
- Ejecutar pruebas de humo, los cuatro casos de demostración y la lista final de aceptación.
- Preparar instrucciones de ejecución y guion de demostración.

Archivos principales:

- `app.py`
- Pruebas del flujo integrado dentro de `tests/`
- `docs/pruebas-y-casos-demo.md`
- `docs/criterios-de-aceptacion.md`
- Este `README.md`

Entregable verificable:

> El flujo completo funciona desde el ingreso del reporte hasta la revisión humana y la consulta del historial, mostrando correctamente los fallos de IA o Supabase.

## Límites de responsabilidad

| Tema | Responsable | Colaboración necesaria |
|---|---|---|
| Contratos Pydantic, categorías y estados | Integrante 1 | Integrantes 2, 3 y 4 validan que sus consumidores sigan siendo compatibles. |
| Instrucciones del agente y herramientas | Integrante 2 | Integrante 1 valida reglas; Integrante 3 ofrece repositorios controlados. |
| Esquema, consultas, RLS y auditoría | Integrante 3 | Integrante 1 valida contratos; Integrante 4 valida mensajes y flujo visible. |
| Interfaz y navegación | Integrante 4 | Consume funciones públicas de los Integrantes 1, 2 y 3 sin duplicar su lógica. |
| Pruebas unitarias | Autor del módulo | El Integrante 4 comprueba que estén incluidas en la ejecución final. |
| Pruebas de integración y regresión | Integrantes 3 y 4 | Los Integrantes 1 y 2 corrigen fallos causados por sus módulos. |
| Documentación especializada | Responsable del área | El Integrante 4 revisa coherencia antes de la entrega. |

## Orden de trabajo

### Fase 1 — Contratos y preparación

- Integrante 1 define modelos, enumeraciones y reglas base.
- Integrante 3 prepara esquema, configuración y contrato del repositorio.
- Integrante 2 diseña la salida del agente usando los modelos acordados.
- Integrante 4 prepara la estructura mínima de Streamlit sin duplicar lógica.

### Fase 2 — Desarrollo en paralelo

- Integrante 1 termina reglas locales y pruebas unitarias.
- Integrante 2 implementa agente, herramientas y fallback.
- Integrante 3 implementa persistencia, RLS y auditoría.
- Integrante 4 construye las pantallas usando servicios o dobles temporales.

### Fase 3 — Integración

1. Integrar modelos y reglas con el agente.
2. Integrar repositorios con las herramientas autorizadas.
3. Integrar análisis y persistencia con Streamlit.
4. Integrar revisión humana e historial.
5. Corregir incompatibilidades sin cambiar contratos unilateralmente.

### Fase 4 — Verificación y entrega

- Ejecutar pruebas unitarias y de integración.
- Probar el modo local sin OpenAI.
- Probar el manejo de una falla de Supabase.
- Ejecutar los cuatro casos de demostración.
- Revisar RLS, auditoría, secretos y documentación.
- Detener nuevas funciones cuando se cumplan los criterios de aceptación.

## Reglas de coordinación

1. Cada integrante trabaja principalmente en los archivos asignados.
2. Los cambios de contratos, estados o esquema se acuerdan antes de editar consumidores.
3. Cada cambio incluye evidencia de prueba y una descripción breve.
4. No se duplican reglas entre interfaz, agente y repositorios.
5. Nadie introduce tecnologías o funciones fuera del alcance sin autorización.
6. La IA nunca sustituye la revisión humana.
7. Supabase continúa siendo la única base de datos oficial.
8. Un error externo debe mostrarse; nunca se presenta una operación fallida como exitosa.

## Definición de terminado del equipo

El trabajo conjunto está listo únicamente cuando:

- La aplicación inicia con `streamlit run app.py`.
- Las entradas y salidas se validan con Pydantic.
- El agente y el modo local producen estructuras válidas.
- Supabase persiste solicitudes y auditoría con RLS activo.
- Los duplicados se muestran solo como sugerencias.
- La revisión humana funciona y conserva trazabilidad.
- Los fallos de IA y Supabase se manejan de forma visible.
- Las pruebas principales y los cuatro casos de demostración están verificados.
- No hay secretos ni datos personales innecesarios en el repositorio.

La lista completa se encuentra en [`docs/criterios-de-aceptacion.md`](docs/criterios-de-aceptacion.md).

## Preparación para integración y despliegue

La guía de [integración y despliegue](docs/integracion-y-despliegue.md) contiene dependencias, variables de entorno, pruebas previas y la lista de salida. La [guía de integración del equipo](docs/guia-de-integracion-equipo.md) define el contrato y la entrega mínima de cada integrante. El proyecto no debe desplegarse hasta que los cuatro módulos cumplan los criterios de aceptación.
