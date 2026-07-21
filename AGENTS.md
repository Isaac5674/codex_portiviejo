# AGENTS.md — PortoReporta

## 1. Propósito de este archivo

Este archivo es el punto de entrada operativo para Codex y cualquier agente de programación que trabaje en PortoReporta.

Su función es:

- indicar qué documentación debe leerse;
- definir cómo seleccionar y aplicar las skills del proyecto;
- resumir las reglas generales de trabajo;
- proteger el alcance, la arquitectura, los contratos, la seguridad y el comportamiento ya existente;
- evitar cambios desordenados, incompatibles o innecesariamente complejos.

Este archivo **no sustituye** a `docs/contexto-proyecto.md`, a los documentos técnicos de `docs/` ni a las skills. Tampoco introduce requisitos nuevos.

Cuando una regla detallada exista en la documentación o en una skill aplicable, se debe seguir esa fuente específica.

---

# 2. Principio central del proyecto

> La interfaz captura y muestra, el agente interpreta y recomienda, las reglas validan, los repositorios persisten en Supabase y la persona decide.

Consecuencias obligatorias:

- La inteligencia artificial no aprueba solicitudes.
- La inteligencia artificial no rechaza solicitudes.
- La inteligencia artificial no confirma duplicados.
- Supabase es la única base de datos oficial.
- La revisión humana es obligatoria.
- Las decisiones relevantes deben quedar auditadas.
- Una operación no se considera exitosa hasta verificar su resultado real.
- El sistema no debe inventar información faltante.

---

# 3. Jerarquía de autoridad

Este archivo respeta la jerarquía definida en `docs/README.md`.

Cuando exista una contradicción, aplica este orden:

1. Instrucción explícita del responsable humano en la conversación actual.
2. `docs/contexto-proyecto.md`.
3. `docs/instrucciones-generales.md`.
4. Documentos técnicos específicos dentro de `docs/`.
5. Código existente y pruebas automatizadas.
6. Suposiciones del agente.

`AGENTS.md` funciona como índice y protocolo operativo. No debe utilizarse para anular una decisión documentada.

Una decisión técnica aceptada en `docs/decisiones-tecnicas.md` no puede cambiarse sin:

- autorización humana;
- una nueva decisión registrada;
- actualización de documentación;
- pruebas correspondientes.

---

# 4. Lectura obligatoria antes de trabajar

## 4.1. Lectura mínima para cualquier tarea

Antes de crear, editar, eliminar o reorganizar código, lee:

1. `AGENTS.md`.
2. `docs/README.md`.
3. `docs/contexto-proyecto.md`.
4. `docs/instrucciones-generales.md`.
5. El documento técnico relacionado con la tarea.
6. Los archivos de código afectados.
7. Las pruebas relacionadas.
8. La skill o combinación de skills aplicable.

## 4.2. Orden completo de la documentación

Cuando la tarea afecte varias partes del sistema o implique una revisión general, sigue este orden:

1. `docs/contexto-proyecto.md`
2. `docs/instrucciones-generales.md`
3. `docs/alcance-mvp.md`
4. `docs/arquitectura-y-responsabilidades.md`
5. `docs/contratos-de-datos.md`
6. `docs/reglas-de-negocio.md`
7. `docs/flujos-y-estados.md`
8. `docs/persistencia-supabase.md`
9. `docs/seguridad-y-privacidad.md`
10. `docs/manejo-de-errores.md`
11. `docs/pruebas-y-casos-demo.md`
12. `docs/criterios-de-aceptacion.md`
13. `docs/plan-de-trabajo-codex.md`
14. `docs/decisiones-tecnicas.md`
15. `docs/glosario.md`

No afirmes haber leído un archivo que no exista o que no hayas abierto.

---

# 5. Skills específicas del proyecto

Las skills están ubicadas en:

```text
.agents/
└── skills/
    ├── disenar-cambio-modular/
    │   └── SKILL.md
    ├── implementar-cambio-seguro/
    │   └── SKILL.md
    ├── persistencia-supabase-segura/
    │   └── SKILL.md
    └── agente-trazable-supervisado/
        └── SKILL.md
```

Las skills pueden combinarse. Elegir una no excluye las demás.

## 5.1. `disenar-cambio-modular`

Usar antes de programar cuando la tarea:

- agrega una funcionalidad;
- modifica arquitectura;
- amplía una regla;
- agrega un campo, categoría o estado;
- crea un nuevo flujo;
- incorpora una integración;
- refactoriza responsabilidades;
- puede afectar varios módulos.

Objetivo:

- encontrar el punto correcto de extensión;
- aplicar el principio abierto-cerrado;
- evitar duplicación;
- mantener responsabilidades separadas;
- definir impacto y pruebas antes de editar.

Cuando el usuario solicite únicamente planificación, utiliza esta skill y no implementes todavía.

## 5.2. `implementar-cambio-seguro`

Usar siempre que se modifique código existente.

Objetivo:

- crear una línea base;
- aplicar el cambio mínimo;
- conservar contratos;
- añadir pruebas;
- comprobar regresiones;
- revisar el diff;
- no dañar funciones anteriores.

Esta skill es obligatoria para correcciones, nuevas funciones y refactorizaciones.

## 5.3. `persistencia-supabase-segura`

Usar cuando la tarea afecte:

- Supabase;
- PostgreSQL;
- tablas;
- restricciones;
- índices;
- RLS;
- variables de entorno de Supabase;
- `src/supabase_client.py`;
- `src/repositories.py`;
- auditoría;
- migraciones;
- búsqueda de duplicados persistidos.

Objetivo:

- conservar Supabase como única base oficial;
- centralizar consultas;
- proteger credenciales;
- mantener compatibilidad con datos existentes;
- aplicar cambios de esquema reproducibles;
- verificar respuestas antes de declarar éxito.

## 5.4. `agente-trazable-supervisado`

Usar cuando la tarea afecte:

- `src/agent.py`;
- instrucciones o configuración del agente;
- herramientas;
- modelos de salida;
- clasificación;
- prioridad;
- información faltante;
- duplicados;
- fallback local;
- supervisión humana;
- auditoría de decisiones.

Objetivo:

- mantener salidas estructuradas;
- evitar invenciones;
- conservar reglas deterministas;
- limitar la autoridad de la IA;
- mantener fallback;
- preservar trazabilidad.

## 5.5. Matriz de selección

| Tipo de tarea | Skills obligatorias |
|---|---|
| Nueva funcionalidad | `disenar-cambio-modular` + `implementar-cambio-seguro` |
| Corrección de error | `implementar-cambio-seguro` |
| Refactorización | `disenar-cambio-modular` + `implementar-cambio-seguro` |
| Cambio en Supabase | `disenar-cambio-modular` + `implementar-cambio-seguro` + `persistencia-supabase-segura` |
| Cambio del agente | `disenar-cambio-modular` + `implementar-cambio-seguro` + `agente-trazable-supervisado` |
| Cambio del agente con persistencia | Las cuatro skills |
| Cambio visual aislado | `implementar-cambio-seguro` |
| Planificación sin código | `disenar-cambio-modular` |

Si una skill contiene un procedimiento más específico para la tarea, sigue ese procedimiento sin repetirlo ni contradecirlo.

---

# 6. Decisiones técnicas ya aceptadas

No reabras estas decisiones sin autorización humana:

1. **Streamlit** es la interfaz.
2. **Supabase con PostgreSQL** es la única base de datos.
3. Se utiliza **un agente coordinador con herramientas internas**.
4. La **supervisión humana es obligatoria**.
5. La salida del análisis se valida con **Pydantic**.
6. Los duplicados son únicamente **sugerencias**.
7. El **modo local basado en reglas es obligatorio** cuando OpenAI falla.

No sustituir estas decisiones por preferencias personales del agente.

---

# 7. Tecnologías autorizadas

## Permitidas

- Python 3.11 o superior.
- Streamlit.
- OpenAI Agents SDK para Python.
- Pydantic.
- Supabase.
- PostgreSQL administrado por Supabase.
- `supabase-py`.
- `python-dotenv`.
- `pytest`.
- Biblioteca estándar de Python.
- `difflib.SequenceMatcher` para posibles duplicados durante el MVP.

## Prohibidas sin autorización humana

- React.
- Vue.
- Angular.
- Next.js.
- FastAPI.
- Flask.
- Django.
- MySQL.
- SQLite.
- MongoDB.
- Firebase.
- Redis.
- Docker como requisito obligatorio.
- Microservicios.
- Colas de mensajes.
- Nuevos frameworks de agentes.
- Modelos propios de aprendizaje automático.
- Servicios externos adicionales.
- Archivos JSON o CSV como base de datos oficial.

No añadas una dependencia cuando la biblioteca estándar o una dependencia ya aceptada resuelva la necesidad.

---

# 8. Alcance obligatorio del MVP

El objetivo es demostrar este flujo:

1. El ciudadano ingresa descripción y ubicación.
2. El sistema valida la entrada.
3. El sistema analiza mediante IA.
4. Si la IA falla, utiliza reglas locales.
5. La salida se valida con Pydantic.
6. Se propone categoría, prioridad y área.
7. Se indica información faltante.
8. Se buscan posibles duplicados.
9. El usuario confirma la creación del expediente.
10. El expediente se guarda en Supabase.
11. Se registra auditoría.
12. Un operador revisa.
13. El operador aprueba, modifica, rechaza, solicita información o marca posible duplicado.
14. La acción se persiste y audita.
15. Se pueden consultar solicitudes e historial.

## Funciones opcionales

Solo después de cumplir todos los criterios de aceptación:

- filtros;
- métricas simples;
- exportación CSV;
- mejoras visuales;
- datos semilla;
- vista detallada mejorada;
- Supabase Storage;
- Supabase Auth básica.

## Fuera del alcance

No implementar durante el MVP:

- aplicación móvil;
- mapas;
- GPS;
- WhatsApp;
- correo;
- integración municipal real;
- reconocimiento de imágenes;
- autenticación compleja;
- roles avanzados;
- dashboard avanzado;
- notificaciones reales;
- cuadrillas;
- resolución física del problema;
- arquitectura multiagente;
- microservicios;
- despliegue complejo.

Cuando se cumplan los criterios de aceptación, deja de agregar funciones y concentra el trabajo en estabilidad, correcciones y demostración.

---

# 9. Arquitectura y responsabilidades

## `app.py`

Debe:

- configurar Streamlit;
- mostrar navegación;
- capturar entradas;
- mostrar resultados;
- invocar servicios o funciones de aplicación;
- conservar estado temporal con `st.session_state`;
- mostrar errores comprensibles.

No debe:

- implementar todas las reglas;
- consultar Supabase de forma dispersa;
- construir SQL;
- guardar secretos;
- duplicar categorías o estados;
- aprobar automáticamente;
- usar `st.session_state` como persistencia oficial.

## `src/agent.py`

Debe:

- configurar el agente coordinador;
- mantener sus instrucciones;
- solicitar salida estructurada;
- ejecutar herramientas autorizadas;
- manejar fallos de IA;
- delegar al modo local.

No debe:

- tomar decisiones finales;
- saltarse Pydantic;
- inventar datos;
- construir SQL;
- contener interfaz;
- acceder arbitrariamente a tablas.

## `src/models.py`

Debe:

- definir modelos Pydantic;
- definir o restringir enumeraciones;
- validar entradas y salidas;
- normalizar únicamente cuando sea seguro.

No debe:

- conectarse a Supabase;
- importar Streamlit;
- ejecutar el agente;
- contener persistencia.

## `src/rules.py`

Debe:

- mantener categorías;
- mantener relación categoría-área;
- definir señales de prioridad;
- implementar clasificación local;
- implementar prioridad local;
- proporcionar reglas deterministas y testeables.

No debe:

- importar Streamlit;
- conectarse a Supabase;
- leer secretos;
- duplicar lógica del repositorio.

## `src/tools.py`

Debe:

- exponer herramientas autorizadas al agente;
- validar argumentos;
- adaptar entradas y salidas;
- delegar a reglas o repositorios;
- devolver datos serializables.

No debe:

- duplicar consultas;
- aprobar o rechazar;
- ocultar fallos;
- aceptar nombres de tabla del usuario.

## `src/supabase_client.py`

Debe:

- leer variables de entorno;
- validar configuración;
- crear un cliente reutilizable;
- emitir errores seguros.

No debe:

- implementar reglas de negocio;
- contener consultas específicas;
- imprimir secretos;
- importar la interfaz.

## `src/repositories.py`

Debe:

- centralizar operaciones con Supabase;
- crear, consultar y actualizar solicitudes;
- registrar y consultar auditoría;
- buscar candidatos a duplicados;
- validar respuestas;
- restringir campos actualizables.

No debe:

- decidir prioridades;
- importar Streamlit;
- ejecutar el agente;
- aceptar actualizaciones arbitrarias;
- aceptar nombres de tabla o columna del usuario.

## `supabase/schema.sql`

Debe:

- crear tablas;
- crear restricciones;
- crear índices;
- activar RLS;
- mantener el esquema reproducible.

Todo cambio posterior de esquema debe seguir la estrategia documentada y, cuando corresponda, añadirse como migración nueva.

## `tests/`

Debe cubrir:

- reglas;
- modelos;
- repositorios;
- fallos;
- fallback;
- revisión humana;
- casos de demostración.

## Dependencia principal

```text
app.py
  ↓
agent.py o servicios de aplicación
  ↓
tools.py
  ↓
rules.py y repositories.py
  ↓
supabase_client.py
  ↓
Supabase
```

No introduzcas dependencias circulares.

Crea un archivo nuevo únicamente si:

- tiene una responsabilidad distinta;
- reduce duplicación real;
- facilita pruebas;
- será reutilizado;
- no agrega una capa innecesaria.

---

# 10. Principios de diseño y mantenimiento

## 10.1. Abierto-cerrado

Prefiere ampliar mediante:

- configuración central;
- funciones especializadas;
- composición;
- estrategias registrables;
- contratos estables;
- dependencias inyectables cuando mejoren las pruebas.

Evita agregar condicionales dispersos en interfaz, agente, reglas y repositorios para representar la misma decisión.

Agregar una categoría no debe exigir reescribir el agente.

## 10.2. Responsabilidad única

Una función no debe simultáneamente:

- capturar interfaz;
- analizar;
- guardar;
- auditar;
- mostrar mensajes.

Separa cálculo, validación, persistencia, auditoría e interfaz.

## 10.3. Reutilización con criterio

Extrae lógica cuando:

- representa una regla del dominio;
- aparece en más de un lugar;
- necesita una prueba aislada;
- evita que una capa conozca detalles de otra.

No crees abstracciones, clases o archivos solo para aparentar arquitectura.

## 10.4. Compatibilidad

Conserva siempre que sea posible:

- firmas públicas;
- nombres;
- contratos;
- estados;
- campos;
- comportamiento probado;
- datos existentes.

Todo cambio incompatible requiere autorización, migración, actualización coordinada y pruebas.

## 10.5. Cambio mínimo

- No reescribas un archivo completo cuando basta un cambio localizado.
- No renombres símbolos no relacionados.
- No mezcles una función nueva con una refactorización general.
- No reemplaces código funcional por una arquitectura más compleja.
- No modifiques archivos no relacionados.
- No elimines código sin buscar consumidores.

---

# 11. Contratos autorizados

## Categorías

- `AGUA`
- `BASURA`
- `ALUMBRADO`
- `VIALIDAD`
- `ALCANTARILLADO`
- `ESPACIO_PUBLICO`
- `OTRO`

## Prioridades

- `BAJA`
- `MEDIA`
- `ALTA`

## Estados

- `PENDIENTE_REVISION`
- `REQUIERE_INFORMACION`
- `APROBADA`
- `MODIFICADA_Y_APROBADA`
- `RECHAZADA`
- `POSIBLE_DUPLICADO`

## Actores de auditoría

- `CIUDADANO`
- `AGENTE`
- `OPERADOR`
- `SISTEMA`

## Origen del análisis

- `IA`
- `REGLAS`

No inventes valores adicionales.

Todo cambio de contrato debe actualizar coordinadamente:

- modelos Pydantic;
- reglas;
- repositorios;
- interfaz;
- pruebas;
- documentación;
- esquema SQL cuando corresponda.

---

# 12. Reglas de negocio no negociables

- El área responsable debe corresponder a la categoría.
- El mapeo categoría-área debe existir en una sola fuente central.
- `OTRO` se utiliza cuando no existe evidencia suficiente.
- La prioridad es una recomendación, no una decisión definitiva.
- Una prioridad alta requiere evidencia de riesgo o afectación grave.
- La ubicación `Sin especificar` debe considerarse insuficiente.
- No inventar barrio, dirección, fecha, duración, afectados, instituciones ni peligro.
- Los duplicados son candidatos.
- La confirmación de duplicado es humana.
- El motivo es obligatorio cuando el operador modifica una recomendación.
- La recomendación original debe conservarse.
- Un expediente no puede crearse directamente como aprobado o rechazado.
- Toda transición relevante debe ser explícita y auditada.

---

# 13. Estados y transiciones

## Estados iniciales permitidos

- `PENDIENTE_REVISION`
- `REQUIERE_INFORMACION`

`POSIBLE_DUPLICADO` puede utilizarse como estado de revisión cuando exista un candidato, pero no confirma identidad.

## Transiciones principales permitidas

- Nuevo análisis → `PENDIENTE_REVISION`
- Nuevo análisis incompleto → `REQUIERE_INFORMACION`
- `PENDIENTE_REVISION` → `APROBADA`
- `PENDIENTE_REVISION` → `MODIFICADA_Y_APROBADA`
- `PENDIENTE_REVISION` → `RECHAZADA`
- `PENDIENTE_REVISION` → `REQUIERE_INFORMACION`
- `PENDIENTE_REVISION` → `POSIBLE_DUPLICADO`
- `REQUIERE_INFORMACION` → `PENDIENTE_REVISION`
- `POSIBLE_DUPLICADO` → `APROBADA`
- `POSIBLE_DUPLICADO` → `MODIFICADA_Y_APROBADA`
- `POSIBLE_DUPLICADO` → `RECHAZADA`

## Prohibiciones

- Crear directamente como `APROBADA`.
- Crear directamente como `RECHAZADA`.
- Cambiar silenciosamente de estado.
- Modificar un caso revisado sin motivo y auditoría.
- Cambiar una decisión humana desde el agente.

---

# 14. Supabase y persistencia

Supabase es la única base oficial.

## Variables esperadas

```text
SUPABASE_URL=
SUPABASE_SECRET_KEY=
OPENAI_API_KEY=
APP_ENV=development
```

## Reglas obligatorias

- Crear el cliente únicamente desde `src/supabase_client.py`.
- Centralizar operaciones en `src/repositories.py`.
- Mantener RLS activado.
- No crear políticas públicas anónimas durante el MVP.
- Utilizar la clave secreta únicamente en el servidor.
- No enviar el cliente privilegiado al navegador.
- No ejecutar SQL generado por IA.
- No declarar éxito sin confirmar `response.data`.
- No usar SQLite, JSON, CSV o sesión como reemplazo silencioso.

## Cambios de esquema

No modificar tablas o restricciones sin:

- autorización cuando afecte el diseño acordado;
- SQL reproducible;
- revisión de compatibilidad;
- actualización de modelos;
- actualización de repositorios;
- actualización de pruebas;
- actualización de documentación.

Prefiere cambios aditivos y compatibles con filas existentes.

## Actualizaciones

- Usa lista blanca de campos.
- No aceptes diccionarios arbitrarios.
- Conserva recomendaciones originales cuando exista un campo final.
- Verifica que la solicitud exista.
- Registra valores anteriores, nuevos y motivo cuando corresponda.

## Auditoría

Después de una operación principal:

1. confirma la respuesta;
2. registra auditoría;
3. confirma la auditoría;
4. solo entonces informa trazabilidad completa.

Si la auditoría falla, informa que la operación principal pudo completarse, pero la trazabilidad quedó incompleta. No repitas automáticamente una operación ya confirmada.

---

# 15. Agente, herramientas y fallback

## El agente puede

- interpretar;
- extraer;
- resumir;
- clasificar;
- proponer prioridad;
- proponer área;
- detectar información faltante;
- sugerir duplicados;
- explicar.

## El agente no puede

- aprobar;
- rechazar;
- confirmar duplicados;
- declarar una emergencia oficial;
- enviar reportes a instituciones;
- declarar el problema resuelto;
- inventar datos;
- cambiar decisiones humanas;
- escribir libremente en Supabase.

## Salida estructurada

Toda salida debe:

- cumplir los modelos Pydantic;
- utilizar valores autorizados;
- contener justificación;
- contener listas válidas;
- indicar `origen_analisis`;
- validarse antes de persistirse.

Si una salida no valida:

1. registra el error de forma segura;
2. normaliza solo valores seguros;
3. si sigue inválida, utiliza reglas locales;
4. no persistas datos inválidos.

## Herramientas

Cada herramienta debe:

- tener una responsabilidad;
- validar parámetros;
- delegar a reglas o repositorios;
- devolver datos serializables;
- limitar su autoridad;
- manejar fallos de forma visible;
- poder probarse sin ejecutar toda la interfaz.

## Modo local

Cuando OpenAI no esté disponible:

1. muestra una advertencia;
2. ejecuta clasificación y prioridad mediante reglas;
3. valida el resultado;
4. marca `origen_analisis` como `REGLAS`;
5. continúa sin aprobación automática;
6. registra el fallback si se crea el expediente.

No simules que el resultado provino de IA.

---

# 16. Manejo de errores

## Principio

Un error debe ser visible, comprensible y recuperable. Nunca fingir éxito.

## Falla de OpenAI

- activar modo local;
- informar al usuario;
- no reintentar indefinidamente;
- no bloquear toda la aplicación.

## Falla de Supabase

- mostrar error claro;
- no mostrar ID inventado;
- no declarar guardado;
- conservar análisis temporal en `st.session_state`;
- permitir reintento;
- no cambiar a otra base;
- identificar claramente un modo de demo sin persistencia.

## Falla de validación

- no persistir;
- intentar correcciones seguras;
- utilizar fallback cuando sea necesario;
- no mostrar trazas sensibles.

## Falla de auditoría

- informar trazabilidad incompleta;
- permitir reintento del evento;
- no repetir la operación principal ya confirmada;
- no declarar finalización completa.

## Falla de duplicados

- continuar el análisis;
- informar que la búsqueda no estuvo disponible;
- no marcar automáticamente;
- registrar el fallo si se guarda el expediente.

No utilices:

```python
except Exception:
    pass
```

Si capturas una excepción, conserva evidencia técnica útil sin exponer secretos y muestra un mensaje seguro al usuario.

---

# 17. Seguridad y privacidad

## Nunca almacenar

- cédulas;
- contraseñas;
- claves API;
- tokens;
- datos médicos;
- datos financieros;
- fotografías de documentos;
- información personal innecesaria;
- teléfonos o correos sin autorización futura;
- direcciones residenciales exactas innecesarias.

## Nunca versionar

- `.env`;
- `.streamlit/secrets.toml`;
- copias de credenciales;
- logs con tokens;
- capturas de claves.

## Interfaz

Debe indicar:

- que PortoReporta es un prototipo;
- que no es una plataforma oficial;
- que no envía reportes a instituciones reales;
- que la prioridad es una recomendación;
- que una persona toma la decisión final.

## Entradas

- validar descripción;
- validar ubicación;
- validar longitud;
- mostrar el contenido como texto;
- no ejecutar contenido ciudadano;
- no construir SQL con entradas;
- no permitir actualizaciones arbitrarias.

## Logs

No incluir:

- secretos;
- encabezados de autorización;
- variables de entorno completas;
- datos personales innecesarios;
- respuestas completas que puedan contener credenciales.

---

# 18. Procedimiento obligatorio para cada tarea

## 18.1. Antes de editar

1. Lee las fuentes obligatorias.
2. Revisa `git status`.
3. Identifica cambios existentes que no pertenecen a la tarea.
4. No sobrescribas trabajo ajeno.
5. Reproduce o comprende el comportamiento actual.
6. Ejecuta las pruebas relacionadas para establecer línea base.
7. Identifica interfaces públicas afectadas.
8. Selecciona las skills.
9. Define los archivos permitidos.
10. Explica brevemente el cambio y sus riesgos.

## 18.2. Durante la edición

1. Aplica el cambio mínimo.
2. Respeta responsabilidades.
3. No introduzcas dependencias no autorizadas.
4. Conserva contratos.
5. Separa efectos secundarios.
6. Valida entradas y salidas.
7. Añade o actualiza pruebas.
8. Actualiza documentación cuando cambie comportamiento documentado.
9. No mezcles trabajos no relacionados.

## 18.3. Después de editar

1. Ejecuta las pruebas relacionadas.
2. Ejecuta una validación manual mínima.
3. Ejecuta verificaciones generales cuando corresponda.
4. Revisa `git diff`.
5. Elimina depuración accidental.
6. Verifica que no existan secretos.
7. Confirma que no cambiaste archivos no relacionados.
8. Informa limitaciones reales.

Comandos habituales:

```bash
pytest
python -m compileall .
streamlit run app.py
```

No afirmes que ejecutaste una comprobación que no se realizó.

---

# 19. Pruebas y protección contra regresiones

Toda modificación lógica debe incluir:

- un caso feliz;
- una entrada inválida;
- una prueba del comportamiento nuevo;
- una prueba de regresión del comportamiento anterior;
- una prueba de fallo externo cuando aplique.

## Partes prioritarias

1. Reglas.
2. Modelos.
3. Persistencia.
4. Auditoría.
5. Fallback.
6. Revisión humana.
7. Duplicados.
8. Casos de demostración.

## Regla de corrección de errores

Para corregir un error:

1. reproduce;
2. identifica causa raíz con evidencia;
3. agrega o ajusta una prueba que falle antes;
4. aplica el cambio mínimo;
5. confirma que la prueba pasa;
6. ejecuta regresiones relacionadas.

Las pruebas unitarias no deben necesitar Supabase remoto. Usa dobles, mocks o dependencias inyectadas.

Las pruebas remotas deben ser explícitas, separadas y seguras.

---

# 20. Casos de demostración obligatorios

## Caso 1: riesgo alto

```text
Hay una alcantarilla sin tapa frente a la escuela del barrio San José. Desde ayer casi ocurre un accidente.
```

Esperado:

- `ALCANTARILLADO`
- `ALTA`
- área `Alcantarillado`
- señales de riesgo
- estado inicial `PENDIENTE_REVISION`

## Caso 2: información insuficiente

```text
Hay un hueco peligroso.
```

Ubicación:

```text
Sin especificar
```

Esperado:

- `VIALIDAD`
- ubicación faltante
- estado `REQUIERE_INFORMACION`

## Caso 3: prioridad media

```text
La luminaria del parque no funciona desde hace cuatro noches.
```

Esperado:

- `ALUMBRADO`
- `MEDIA`
- área `Alumbrado público`

## Caso 4: posible duplicado

Caso existente:

```text
Existe una fuga de agua frente al mercado central.
```

Caso nuevo:

```text
Se está desperdiciando agua en la calle del mercado.
```

Esperado:

- candidato de posible duplicado;
- similitud explicada;
- confirmación humana.

---

# 21. Criterio de terminado y regla de detención

La fuente completa es `docs/criterios-de-aceptacion.md`.

No declares el proyecto terminado hasta comprobar, entre otros:

- aplicación inicia;
- navegación funciona;
- entrada valida;
- análisis estructurado;
- Pydantic valida;
- fallback funciona;
- Supabase persiste;
- RLS está activado;
- no hay políticas anónimas públicas;
- duplicados son sugerencias;
- revisión humana funciona;
- auditoría funciona;
- errores no fingen éxito;
- no hay secretos;
- pruebas pasan;
- cuatro casos de demo fueron probados;
- limitaciones están documentadas.

Cuando todos los criterios estén cumplidos:

1. no agregues funciones;
2. corrige solo defectos;
3. mejora presentación sin cambiar el flujo;
4. prepara la demo;
5. conserva una versión estable;
6. evita cambios de arquitectura.

---

# 22. Formato de trabajo y respuesta

Cada tarea debe definirse, cuando sea posible, con:

```text
Objetivo:
Archivos permitidos:
Restricciones:
Comportamiento esperado:
Pruebas obligatorias:
Criterio de terminado:
```

Después de implementar, responde con:

```markdown
## Resumen de cambios

## Archivos modificados

## Decisiones técnicas

## Comandos ejecutados

## Resultado de pruebas

## Verificación manual

## Riesgos o pendientes

## Cómo verificar
```

No utilices frases como:

- “Todo funciona” sin evidencia.
- “Las pruebas pasan” sin ejecutarlas.
- “Supabase quedó configurado” sin probar la conexión.
- “El expediente fue guardado” sin verificar la respuesta.
- “El caso es definitivamente duplicado”.
- “El municipio recibirá el reporte”.
- “El problema fue resuelto”.

---

# 23. Protocolo cuando falta información

Cuando algo no esté documentado:

1. busca una regla equivalente;
2. elige la alternativa más simple;
3. conserva compatibilidad;
4. evita cambios irreversibles;
5. documenta la suposición;
6. pregunta al responsable humano solo cuando afecte:
   - esquema;
   - arquitectura;
   - seguridad;
   - alcance;
   - dependencias;
   - prioridades;
   - estados;
   - flujo principal de la demo.

No detengas una tarea por un detalle menor que pueda resolverse de manera segura y reversible.

---

# 24. Prohibiciones finales

Codex no debe:

- inventar requisitos;
- ampliar alcance;
- cambiar tecnologías;
- sustituir Supabase;
- exponer secretos;
- aprobar o rechazar con IA;
- confirmar duplicados automáticamente;
- inventar datos;
- ocultar fallback;
- fingir persistencia;
- fingir pruebas;
- modificar archivos no relacionados;
- reescribir arquitectura sin necesidad;
- agregar funciones opcionales antes del MVP;
- crear documentación de funciones inexistentes;
- ejecutar SQL generado por IA;
- eliminar revisión humana;
- afirmar integración municipal;
- ignorar una skill aplicable;
- ignorar fallos conocidos al reportar resultados.

---

# 25. Lista de comprobación rápida

Antes de finalizar una tarea:

- [ ] Leí la documentación aplicable.
- [ ] Seleccioné las skills correctas.
- [ ] Respeté el alcance.
- [ ] Respeté la arquitectura.
- [ ] Apliqué el cambio mínimo.
- [ ] Conservé contratos.
- [ ] No dupliqué reglas.
- [ ] Supabase sigue centralizado.
- [ ] La IA conserva límites.
- [ ] La revisión humana sigue activa.
- [ ] Añadí o actualicé pruebas.
- [ ] Probé regresiones.
- [ ] Revisé el diff.
- [ ] No expuse secretos.
- [ ] Actualicé documentación si correspondía.
- [ ] Informé lo que realmente verifiqué.