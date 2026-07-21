---
name: implementar-cambio-seguro
description: Implementa cambios pequeños y verificables en PortoReporta sin romper funciones anteriores, aplicando análisis de impacto, pruebas de regresión y compatibilidad.
---

# Implementar un cambio seguro

## Propósito

Usa esta skill al modificar código existente en PortoReporta.

Su objetivo es impedir que Codex sustituya archivos completos, cambie contratos silenciosamente o arregle una función rompiendo otra. Cada modificación debe ser pequeña, trazable, comprobable y compatible con el comportamiento anterior.

## Fuente de verdad

Lee antes de editar:

1. `AGENTS.md`.
2. `docs/contexto-proyecto.md`.
3. La skill `disenar-cambio-modular` cuando el cambio afecta arquitectura.
4. Los archivos y pruebas relacionados.

No asumas que una función está sin uso. Busca referencias antes de cambiarla o eliminarla.

## Cuándo usar esta skill

Úsala para:

- implementar una funcionalidad;
- corregir un error;
- refactorizar;
- cambiar un contrato;
- modificar reglas;
- tocar persistencia;
- modificar el agente;
- cambiar un flujo de Streamlit;
- actualizar dependencias.

## Regla central

> Ningún cambio se considera correcto solamente porque la función nueva opera. También debe comprobarse que los comportamientos anteriores siguen funcionando.

## Entradas necesarias

Identifica:

- petición;
- criterios de aceptación;
- comportamiento actual;
- archivos afectados;
- pruebas existentes;
- comandos de ejecución;
- riesgos conocidos;
- dependencias externas.

## Procedimiento obligatorio

### 1. Crear una línea base

Antes de editar:

- revisa `git status`;
- identifica cambios existentes que no pertenecen a la tarea;
- no sobrescribas trabajo ajeno;
- ejecuta las pruebas relacionadas;
- registra si alguna prueba ya fallaba;
- ejecuta una comprobación mínima del flujo afectado.

No atribuyas al cambio un fallo que ya existía.

### 2. Explicar el impacto

Resume internamente:

- qué comportamiento se agrega o corrige;
- qué no debe variar;
- qué módulos dependen del código;
- qué datos persistidos podrían verse afectados.

### 3. Modificar la menor superficie posible

Reglas:

- no reescribas archivos completos si basta editar una sección;
- no renombres símbolos no relacionados;
- no cambies formato masivamente;
- no mezcles refactorización general con una función urgente;
- no agregues dependencias para resolver algo disponible en la biblioteca estándar;
- no conviertas el proyecto en otra arquitectura.

### 4. Mantener contratos estables

Antes de cambiar una firma pública, un modelo o una respuesta:

- busca todos sus consumidores;
- conserva valores predeterminados cuando sea seguro;
- añade campos opcionales antes que eliminar campos;
- actualiza productores y consumidores de forma coordinada;
- valida en los límites;
- documenta cualquier incompatibilidad.

### 5. Separar efectos secundarios

Mantén separados:

- cálculo;
- validación;
- persistencia;
- auditoría;
- interfaz;
- llamadas al agente.

Una función pura debe devolver datos sin escribir en Supabase ni modificar Streamlit.

### 6. Implementar validaciones

Valida:

- entradas del usuario;
- salida del agente;
- categorías;
- prioridades;
- estados;
- campos actualizables;
- respuestas vacías de Supabase;
- credenciales necesarias.

No captures excepciones con `except Exception: pass`.

Cuando captures una excepción:

- conserva una causa útil para registro interno;
- muestra un mensaje seguro al usuario;
- no expongas secretos;
- no declares éxito si una operación falló.

### 7. Añadir o actualizar pruebas

Toda modificación lógica requiere pruebas.

Incluye:

- caso nuevo;
- comportamiento anterior;
- entrada inválida;
- error externo cuando aplique.

Las pruebas unitarias no deben depender de una conexión real a Supabase. Usa dobles, funciones inyectadas o repositorios falsos.

Las pruebas de integración remota deben ser explícitas y separadas.

### 8. Ejecutar verificaciones

Ejecuta, según el cambio:

```bash
pytest
python -m compileall .
streamlit run app.py
```

No afirmes que la interfaz funciona si no fue ejecutada o revisada.

Si no puedes ejecutar algo, indica exactamente qué no verificaste.

### 9. Revisar el diff

Antes de finalizar:

- revisa `git diff`;
- elimina código muerto;
- elimina impresiones de depuración;
- confirma que no aparecen claves;
- verifica que no cambió un archivo no relacionado;
- revisa que las cadenas de estado sean válidas;
- revisa imports y ciclos.

### 10. Informar el resultado

Explica:

- qué cambió;
- por qué se cambió así;
- qué pruebas se ejecutaron;
- qué riesgo queda;
- qué no se modificó.

## Reglas para cambios frecuentes

### Agregar una categoría

Debe revisar como mínimo:

- configuración central;
- enumeración o modelo;
- restricción PostgreSQL;
- reglas de respaldo;
- casos de prueba;
- presentación si existe un selector.

No repitas la nueva categoría manualmente en múltiples componentes sin una fuente central.

### Agregar un campo

Debe revisar:

- modelo Pydantic;
- SQL o migración;
- lectura y escritura del repositorio;
- valores predeterminados;
- compatibilidad con filas existentes;
- interfaz;
- auditoría;
- pruebas.

### Agregar un estado

Debe revisar:

- enumeración;
- restricción SQL;
- transiciones permitidas;
- interfaz;
- consultas;
- pruebas.

No permitas transiciones arbitrarias por el solo hecho de que el valor sea válido.

### Cambiar una regla de prioridad

Debe:

- conservar una función determinista;
- agregar casos de prueba;
- comprobar casos anteriores;
- actualizar la explicación visible;
- no depender solamente del prompt del agente.

### Agregar una herramienta del agente

Debe:

- definir argumentos validados;
- delegar a una función reutilizable;
- limitar efectos secundarios;
- devolver un resultado serializable;
- manejar fallos;
- registrar acciones relevantes.

### Cambiar una pantalla Streamlit

Debe:

- conservar lógica fuera de la vista;
- evitar consultas repetidas por cada rerun;
- usar `st.session_state` solo para estado de interfaz temporal;
- no usarlo como base de datos;
- mostrar éxito únicamente después de confirmar persistencia.

## Política de refactorización

Refactoriza solo cuando:

- reduce un riesgo real de la tarea;
- elimina duplicación que impide el cambio;
- hace posible probar la lógica;
- corrige una dependencia incorrecta.

No refactorices todo el proyecto durante una tarea local.

Si el refactor es mayor:

1. conserva comportamiento;
2. agrega pruebas de caracterización;
3. mueve en pasos pequeños;
4. ejecuta pruebas entre pasos;
5. no añadas funcionalidad al mismo tiempo.

## Política de eliminación

Antes de eliminar código:

- busca referencias;
- confirma que no forma parte del fallback;
- confirma que no es usado por pruebas o scripts;
- sustituye consumidores;
- elimina pruebas obsoletas únicamente cuando el comportamiento dejó de existir de forma autorizada.

## Formato de salida obligatorio

```markdown
## Cambio implementado

## Archivos modificados

## Comportamiento conservado

## Decisiones técnicas

## Pruebas ejecutadas

## Resultados

## Riesgos o verificaciones pendientes
```

## Lista de comprobación final

- [ ] Leí el contexto y las instrucciones.
- [ ] Revisé el estado inicial del repositorio.
- [ ] No sobrescribí cambios ajenos.
- [ ] El diff es pequeño y relacionado.
- [ ] Conservé contratos o documenté el cambio.
- [ ] No dupliqué reglas.
- [ ] No mezclé UI, dominio y persistencia.
- [ ] Añadí una prueba del cambio.
- [ ] Añadí o conservé pruebas de regresión.
- [ ] Ejecuté las verificaciones disponibles.
- [ ] Revisé el diff.
- [ ] No expuse secretos.
- [ ] No afirmé éxito sin confirmación.
- [ ] El cambio cumple el criterio de aceptación.
