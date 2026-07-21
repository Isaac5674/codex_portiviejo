---
name: validar-regresiones
description: Verifica después de cualquier cambio de código que la función nueva opere y que el comportamiento anterior de PortoReporta no se haya roto. Úsala al finalizar funciones, correcciones, refactorizaciones, cambios de Supabase o integraciones. No la uses para cambios puramente documentales que no alteren comandos, configuración ni comportamiento.
---

# Validar cambios y prevenir regresiones

## Propósito

Un cambio no está completo solo porque la función nueva parece funcionar.

También debe demostrarse que:

- Los comportamientos anteriores siguen funcionando.
- Los contratos no cambiaron accidentalmente.
- El modo de respaldo continúa disponible.
- La persistencia y la auditoría mantienen consistencia.
- No se introdujeron errores silenciosos.
- No se dañaron rutas no relacionadas.

Una regresión es un comportamiento que antes funcionaba y deja de hacerlo después de un cambio.

## Regla principal

Todo cambio técnico debe responder dos preguntas:

1. ¿Funciona lo nuevo?
2. ¿Sigue funcionando lo anterior?

No finalizar mientras solo se haya comprobado la primera.

## Flujo obligatorio

### 1. Comprender el cambio

Registrar:

```text
Comportamiento nuevo:
...

Comportamientos anteriores relacionados:
...

Contratos afectados:
...

Riesgos:
...
```

### 2. Revisar el estado inicial

Antes de atribuir fallos al cambio:

- Revisar `git status`.
- Ejecutar pruebas relevantes existentes.
- Registrar fallos preexistentes.
- No ocultar ni corregir problemas ajenos sin indicarlo.

### 3. Definir matriz de pruebas

Incluir como mínimo:

| Tipo | Pregunta |
|---|---|
| Caso normal nuevo | ¿La función solicitada trabaja correctamente? |
| Caso límite | ¿Qué ocurre con datos vacíos, largos o inesperados? |
| Caso inválido | ¿El sistema rechaza o informa el error? |
| Regresión directa | ¿El comportamiento que se modificó sigue siendo compatible? |
| Regresión vecina | ¿Los consumidores cercanos siguen funcionando? |
| Falla externa | ¿Qué ocurre si OpenAI o Supabase falla? |
| Persistencia | ¿Los datos se guardan y leen con el formato esperado? |
| Auditoría | ¿La decisión queda registrada? |

### 4. Añadir pruebas al nivel correcto

#### Pruebas unitarias

Para:

- Reglas de prioridad.
- Resolución de áreas.
- Validaciones Pydantic.
- Similitud.
- Transformaciones.
- Servicios con dependencias simuladas.

#### Pruebas de integración

Para:

- Repositorios con Supabase de prueba.
- Coordinación agente-herramientas.
- Creación de solicitud y auditoría.
- Actualización por revisión humana.

#### Prueba manual de humo

Para:

- Inicio de Streamlit.
- Navegación.
- Formulario.
- Resultado.
- Revisión.
- Historial.

No intentar automatizar toda la interfaz durante el MVP si consume el tiempo crítico.

## Casos base de PortoReporta

Estos casos deben mantenerse como regresión:

### Caso de prioridad alta

```text
Descripción:
Hay una alcantarilla sin tapa frente a la escuela del barrio San José. Desde ayer casi ocurre un accidente.

Ubicación:
Barrio San José, frente a la escuela
```

Esperado:

- `ALCANTARILLADO`.
- `ALTA`.
- Área de alcantarillado.
- Señales de escuela, riesgo y alcantarilla abierta.
- Sin aprobación automática.

### Caso incompleto

```text
Descripción:
Hay un hueco peligroso.

Ubicación:
Sin especificar
```

Esperado:

- `VIALIDAD`.
- Información faltante.
- Estado sugerido `REQUIERE_INFORMACION`.

### Caso de prioridad media

```text
Descripción:
La luminaria del parque no funciona desde hace cuatro noches.

Ubicación:
Parque del barrio Los Tamarindos
```

Esperado:

- `ALUMBRADO`.
- `MEDIA`.
- Área de alumbrado público.

### Posible duplicado

Dos reportes semejantes de fuga cerca del mercado.

Esperado:

- Sugerencia de posible duplicado.
- Nunca confirmación automática.

### Falla de OpenAI

Esperado:

- Se activa el modo local.
- El usuario recibe una advertencia.
- El flujo continúa.
- Se registra auditoría.

### Falla de Supabase

Esperado:

- No se afirma que el caso fue guardado.
- El análisis permanece temporalmente en sesión.
- Se permite reintentar.
- Se muestra un error controlado.

## Pruebas de contratos

Comprobar que:

- Las categorías continúan dentro del conjunto permitido.
- Las prioridades continúan siendo `BAJA`, `MEDIA` o `ALTA`.
- Los estados continúan válidos.
- La salida del agente cumple el modelo Pydantic.
- Los repositorios devuelven las estructuras esperadas.
- La interfaz no depende de campos inexistentes.
- Los cambios opcionales tienen valores predeterminados.

## Pruebas de arquitectura

Buscar automáticamente o mediante revisión:

- Importaciones circulares.
- Consultas Supabase fuera de repositorios.
- Uso de Streamlit en reglas o modelos.
- Claves escritas en archivos.
- Duplicación de mapas de categorías.
- Aprobación automática desde el agente.
- Dependencias concretas difíciles de sustituir.

## Orden de ejecución

Ejecutar primero las pruebas más rápidas:

```bash
pytest tests/test_rules.py -q
pytest tests/test_models.py -q
pytest -q
```

Después:

- Pruebas de integración configuradas.
- Inicio de Streamlit.
- Casos manuales.

No afirmar que un comando pasó si no se ejecutó o no se observó su resultado.

## Revisión del diff

Ejecutar:

```bash
git diff --check
git diff
git status
```

Comprobar:

- Archivos inesperados.
- Claves.
- Cambios de formato masivos.
- Código comentado.
- Depuración.
- Dependencias no solicitadas.
- Migraciones destructivas.
- Cambios accidentales en contratos.

## Clasificación de fallos

### Falla causada por el cambio

- Corregir.
- Ejecutar de nuevo todas las pruebas relacionadas.

### Falla preexistente

- Documentarla con evidencia.
- No afirmar que la suite completa pasa.
- Evitar modificarla salvo que sea necesaria para la tarea.

### Falla ambiental

Ejemplos:

- Credenciales faltantes.
- Red no disponible.
- Supabase caído.

Acción:

- Explicar qué no pudo verificarse.
- Ejecutar pruebas locales equivalentes.
- No inventar resultados.

## Criterios para aceptar un refactor

Un refactor es válido únicamente cuando:

- Las pruebas anteriores pasan sin cambiar sus expectativas, salvo que exista un requerimiento nuevo.
- No cambia comportamiento observable.
- Reduce duplicación, acoplamiento o complejidad.
- Mantiene contratos.
- El diff no mezcla nuevas funciones innecesarias.

No debilitar pruebas para hacer pasar un refactor.

## Criterios para aceptar una función nueva

- Tiene al menos una prueba del caso normal.
- Tiene al menos una prueba de error o límite relevante.
- Conserva casos de regresión.
- Usa puntos de extensión existentes.
- No rompe el modo de respaldo.
- No salta revisión humana.
- Registra auditoría cuando corresponde.

## Formato de reporte final

```text
Resumen:
- ...

Pruebas ejecutadas:
- Comando: ...
  Resultado: ...

Casos manuales:
- ...

Regresiones comprobadas:
- ...

No verificado:
- ...

Riesgos pendientes:
- ...
```

## Prohibiciones

- No borrar pruebas porque fallen.
- No cambiar expectativas para ocultar una regresión.
- No usar `try/except` vacío.
- No ignorar errores de Supabase.
- No afirmar que el cambio es seguro sin pruebas.
- No ejecutar pruebas contra producción.
- No incluir credenciales en fixtures.
- No ampliar el alcance mientras existan fallos críticos.
