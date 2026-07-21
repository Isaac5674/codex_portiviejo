---
name: disenar-cambio-modular
description: Diseña cambios modulares para PortoReporta antes de programarlos, protegiendo la arquitectura, el principio abierto-cerrado, la reutilización y las dependencias entre capas.
---

# Diseñar cambios modulares

## Propósito

Usa esta skill antes de implementar una funcionalidad nueva, ampliar una existente o modificar la estructura del proyecto PortoReporta.

Su objetivo es evitar que una petición pequeña termine mezclando interfaz, reglas, agente y Supabase en un mismo archivo. La skill obliga a encontrar el punto correcto de extensión antes de escribir código.

La meta no es crear abstracciones innecesarias. La meta es hacer el cambio más pequeño que:

- cumpla la necesidad;
- conserve el comportamiento anterior;
- respete las responsabilidades existentes;
- permita ampliaciones razonables;
- pueda probarse de manera aislada;
- no duplique reglas ni configuraciones.

## Fuente de verdad

Antes de diseñar cualquier cambio:

1. Lee `docs/contexto-proyecto.md`.
2. Lee `AGENTS.md`.
3. Inspecciona los archivos afectados.
4. Confirma que la petición pertenece al alcance actual.
5. No contradigas el contexto del proyecto sin autorización explícita.

Si la documentación y el código difieren, informa la diferencia antes de continuar. No inventes una nueva arquitectura para ocultar la inconsistencia.

## Cuándo usar esta skill

Úsala cuando se solicite:

- agregar una categoría ciudadana;
- incorporar una nueva regla de prioridad;
- añadir una herramienta al agente;
- crear una pantalla o flujo nuevo;
- ampliar la auditoría;
- agregar filtros o métricas;
- integrar una capacidad futura de Supabase;
- cambiar contratos Pydantic;
- reorganizar módulos;
- reducir duplicación;
- corregir una dependencia incorrecta.

No es necesario usarla para corregir un error tipográfico aislado o cambiar un texto visible sin impacto lógico.

## Entradas necesarias

Obtén o identifica:

- descripción exacta del cambio;
- comportamiento actual;
- comportamiento esperado;
- archivos afectados;
- contratos de datos involucrados;
- pruebas existentes;
- restricciones del MVP;
- riesgo de afectar información persistida.

Cuando falte un dato imprescindible, haz una pregunta concreta. No detengas el trabajo por detalles que puedan verificarse leyendo el repositorio.

## Mapa arquitectónico obligatorio

Respeta estas responsabilidades:

### `app.py`

Responsable de:

- componer la interfaz Streamlit;
- capturar acciones del usuario;
- mostrar resultados;
- llamar servicios o casos de uso.

No debe:

- contener consultas directas a Supabase;
- construir el cliente de Supabase;
- implementar reglas de prioridad;
- contener prompts extensos;
- decidir estados de negocio mediante condicionales dispersos.

### `src/agent.py`

Responsable de:

- configurar el agente;
- ejecutar el análisis;
- coordinar herramientas;
- devolver una salida estructurada.

No debe:

- aprobar solicitudes;
- acceder directamente a variables de entorno fuera del módulo configurado;
- duplicar reglas deterministas;
- escribir SQL;
- mezclar componentes de Streamlit.

### `src/models.py`

Responsable de:

- modelos Pydantic;
- enumeraciones;
- contratos de entrada y salida;
- validaciones estructurales.

No debe:

- consultar Supabase;
- contener reglas operativas complejas;
- importar Streamlit.

### `src/rules.py`

Responsable de:

- categorías centralizadas;
- correspondencia categoría-área;
- señales deterministas de riesgo;
- reglas de prioridad;
- lógica de respaldo sin IA.

No debe:

- contener consultas remotas;
- renderizar interfaz;
- leer secretos.

### `src/tools.py`

Responsable de:

- adaptar capacidades del sistema para que el agente pueda invocarlas;
- validar argumentos antes de delegar;
- devolver resultados acotados y serializables.

No debe:

- duplicar repositorios;
- aprobar decisiones;
- crear clientes globales alternativos;
- esconder errores críticos.

### `src/supabase_client.py`

Responsable únicamente de:

- cargar configuración;
- validar credenciales;
- crear y entregar el cliente Supabase.

No debe contener reglas de negocio ni consultas específicas.

### `src/repositories.py`

Responsable de:

- leer y escribir datos;
- traducir respuestas de Supabase;
- aplicar listas permitidas de campos actualizables;
- encapsular errores de persistencia.

No debe:

- contener componentes de interfaz;
- decidir prioridades;
- ejecutar el agente;
- almacenar claves.

### `tests/`

Responsable de verificar:

- contratos;
- reglas;
- comportamiento previo;
- casos de error;
- integración controlada con repositorios.

## Principios de diseño

### Principio abierto-cerrado

El sistema debe estar abierto a extensión y cerrado a modificaciones innecesarias.

Antes de modificar una función central, pregunta:

1. ¿Puedo añadir una nueva entrada a una configuración central?
2. ¿Puedo agregar una estrategia o función nueva y registrarla?
3. ¿Puedo ampliar un contrato sin cambiar el comportamiento de los consumidores existentes?
4. ¿Puedo inyectar una dependencia en lugar de importar una implementación concreta?
5. ¿Puedo conservar la firma pública actual?

Ejemplo correcto para categorías:

```python
CATEGORY_CONFIG = {
    "AGUA": {"area": "Agua potable", "keywords": (...)},
    "BASURA": {"area": "Gestión ambiental", "keywords": (...)},
}
```

Agregar una categoría debe hacerse extendiendo la configuración y las validaciones relacionadas, no creando condicionales nuevos en cinco archivos.

Ejemplo que debe evitarse:

```python
if categoria == "AGUA":
    ...
elif categoria == "BASURA":
    ...
elif categoria == "ALUMBRADO":
    ...
```

No conviertas automáticamente toda lógica en clases. Una tabla de configuración o una función pequeña puede ser la extensión correcta.

### Responsabilidad única

Cada módulo debe tener una razón principal para cambiar.

Si una función:

- recibe datos de Streamlit;
- clasifica;
- consulta Supabase;
- actualiza el estado;
- registra auditoría;

entonces tiene demasiadas responsabilidades y debe separarse.

### Inversión de dependencias

La lógica de negocio debe depender de contratos simples, no de detalles externos.

Para funciones importantes, acepta dependencias como parámetros cuando facilite pruebas:

```python
def procesar_reporte(reporte, repositorio, analizador):
    ...
```

No introduzcas protocolos o clases abstractas sin una necesidad concreta. Úsalos cuando exista una dependencia externa que deba sustituirse en pruebas o más de una implementación real.

### Reutilización

Extrae una función reutilizable cuando:

- la lógica aparece al menos en dos lugares;
- representa una regla del dominio;
- necesita prueba aislada;
- evita que la interfaz conozca detalles internos.

No extraigas funciones triviales únicamente para aumentar el número de archivos.

### Compatibilidad

Conserva siempre que sea posible:

- nombres públicos;
- formas de respuesta;
- valores de estados;
- campos persistidos;
- comportamiento documentado.

Un cambio incompatible requiere:

- razón explícita;
- lista de consumidores afectados;
- migración;
- pruebas actualizadas;
- aprobación del usuario.

## Procedimiento obligatorio

### 1. Comprender el comportamiento actual

Antes de proponer código:

- localiza el flujo existente;
- identifica entradas, salidas y efectos secundarios;
- enumera las invariantes que no deben romperse;
- identifica pruebas que protegen ese flujo.

### 2. Clasificar el cambio

Clasifícalo como uno o varios de estos tipos:

- extensión de configuración;
- nueva regla de dominio;
- nuevo caso de uso;
- cambio de contrato;
- cambio de persistencia;
- cambio de interfaz;
- integración externa;
- corrección de defecto;
- refactorización.

### 3. Identificar el punto de extensión

Selecciona el lugar más estrecho donde el cambio puede incorporarse.

Ejemplos:

- categoría nueva → configuración central y validaciones;
- regla nueva → `rules.py`;
- consulta nueva → repositorio;
- herramienta nueva → implementación reutilizable y adaptador en `tools.py`;
- campo nuevo → modelo, migración, repositorio, interfaz y pruebas;
- nueva pantalla → función de presentación que consume servicios existentes.

### 4. Hacer análisis de impacto

Incluye:

- archivos que deben cambiar;
- archivos que no deben cambiar;
- contratos afectados;
- datos existentes afectados;
- pruebas que deben ejecutarse;
- riesgos;
- posible retrocompatibilidad.

### 5. Diseñar la modificación mínima

Prefiere:

- añadir antes que reescribir;
- componer antes que heredar;
- configurar antes que duplicar;
- inyectar antes que acoplar;
- validar en límites;
- conservar firmas estables.

### 6. Definir pruebas antes de implementar

Especifica como mínimo:

- un caso feliz;
- un caso inválido;
- un caso de regresión;
- un caso de fallo externo si aplica.

### 7. Entregar el plan

No programes todavía cuando el usuario solo solicitó planificación.

## Formato de salida obligatorio

Entrega:

```markdown
## Objetivo del cambio

## Comportamiento actual que debe conservarse

## Punto de extensión elegido

## Archivos que cambiarán

## Archivos que no deben cambiar

## Contratos o datos afectados

## Plan de implementación

## Pruebas necesarias

## Riesgos y mitigaciones

## Criterio de finalización
```

## Señales de mala arquitectura

Detén y corrige el plan si detectas:

- consultas Supabase desde `app.py`;
- reglas repetidas en interfaz y agente;
- claves o URLs escritas directamente;
- una función con múltiples efectos secundarios no controlados;
- condicionales crecientes dispersos;
- modelos Pydantic duplicados;
- estados escritos como cadenas distintas en varios lugares;
- importaciones circulares;
- una nueva dependencia sin necesidad;
- un refactor total para agregar una función pequeña;
- cambios de esquema sin migración o SQL reproducible.

## Comprobación final

Antes de dar el diseño por terminado, confirma:

- [ ] El cambio respeta `docs/contexto-proyecto.md`.
- [ ] Existe un único punto principal de extensión.
- [ ] No se duplican reglas.
- [ ] La interfaz no conoce detalles de Supabase.
- [ ] La lógica se puede probar sin Streamlit.
- [ ] El cambio no obliga a reescribir módulos no relacionados.
- [ ] Se conserva el comportamiento anterior.
- [ ] No se agregó complejidad sin beneficio.
- [ ] Las pruebas cubren regresión.
- [ ] El alcance sigue siendo razonable para el MVP.
