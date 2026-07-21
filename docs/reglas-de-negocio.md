# Reglas de negocio

## 1. Mapeo de categorías

| Categoría | Área responsable |
|---|---|
| `AGUA` | Agua potable |
| `BASURA` | Gestión ambiental |
| `ALUMBRADO` | Alumbrado público |
| `VIALIDAD` | Obras públicas |
| `ALCANTARILLADO` | Alcantarillado |
| `ESPACIO_PUBLICO` | Espacios públicos |
| `OTRO` | Atención ciudadana |

El mapeo debe existir en una sola fuente central dentro del código.

## 2. Clasificación

La clasificación debe usar la descripción y la ubicación.

Ejemplos de señales:

- `AGUA`: fuga, tubería, sin agua, desperdicio de agua.
- `BASURA`: basura, desechos, recolección, botadero.
- `ALUMBRADO`: lámpara, luminaria, poste sin luz, oscuridad.
- `VIALIDAD`: hueco, bache, calle dañada, señalización.
- `ALCANTARILLADO`: alcantarilla, drenaje, sumidero, aguas servidas.
- `ESPACIO_PUBLICO`: parque, cancha, juegos, área comunitaria.
- `OTRO`: ninguna categoría alcanza evidencia suficiente.

La IA puede proponer una categoría, pero las reglas deben validar que sea permitida.

## 3. Prioridad

### Alta

Aplicar cuando existe evidencia de:

- Riesgo inmediato.
- Posible accidente.
- Cables expuestos.
- Poste caído.
- Alcantarilla abierta.
- Inundación.
- Vía bloqueada.
- Fuga grande.
- Falta total de agua.
- Cercanía a escuela u hospital combinada con peligro.
- Afectación grave a un servicio esencial.

### Media

Aplicar cuando existe:

- Afectación relevante.
- Problema persistente.
- Dificultad de tránsito.
- Luminaria dañada.
- Basura acumulada.
- Fuga pequeña.
- Deterioro que requiere atención, sin riesgo inmediato.

### Baja

Aplicar cuando se trata principalmente de:

- Mantenimiento.
- Césped alto.
- Pintura deteriorada.
- Daño estético.
- Solicitud general sin afectación urgente.

## 4. Información faltante

El agente debe marcar información faltante cuando:

- La ubicación es genérica.
- La ubicación dice `Sin especificar`.
- La descripción no indica qué ocurrió.
- No existe referencia del lugar.
- No se puede distinguir la categoría.
- La gravedad depende de un dato no proporcionado.

No se debe inventar:

- Dirección.
- Barrio.
- Fecha.
- Tiempo transcurrido.
- Cantidad de afectados.
- Existencia de peligro.
- Institución cercana.

## 5. Posibles duplicados

Un resultado puede ser marcado como posible duplicado cuando coinciden:

- Categoría.
- Zona o referencia de ubicación.
- Palabras principales.
- Similitud textual suficiente.

Reglas:

- Nunca confirmar automáticamente un duplicado.
- Mostrar el identificador del caso candidato.
- Mostrar una razón de similitud.
- Permitir decisión humana.
- Evitar comparar contra casos completamente ajenos por categoría.

## 6. Estado inicial

- Usar `PENDIENTE_REVISION` cuando existe información mínima.
- Usar `REQUIERE_INFORMACION` cuando faltan datos críticos.
- Usar `POSIBLE_DUPLICADO` solo como estado de revisión, no como confirmación definitiva.

## 7. Revisión humana

El operador puede:

- Aprobar.
- Modificar y aprobar.
- Rechazar.
- Solicitar información.
- Marcar posible duplicado.

Cuando modifica una recomendación, el motivo es obligatorio.

## 8. Auditoría

Registrar como mínimo:

- Creación del reporte.
- Análisis del agente.
- Origen del análisis.
- Categoría propuesta.
- Prioridad propuesta.
- Riesgos detectados.
- Posibles duplicados.
- Creación del expediente.
- Cambios humanos.
- Motivo del cambio.
- Estado final de la revisión.

## 9. Prohibiciones

- No enviar reportes a entidades reales.
- No declarar un caso resuelto.
- No declarar una emergencia oficial.
- No calcular porcentajes de mejora sin medición.
- No ocultar que una clasificación provino del modo local.

## 10. Implementación determinista actual

Las reglas públicas viven en `src/rules.py` y no realizan llamadas de red, persistencia ni operaciones de interfaz.

### Fuente central de categorías y áreas

- `Categoria`, `AreaResponsable` y `AREA_POR_CATEGORIA` se definen una sola vez en `src/models.py`.
- `obtener_area_responsable(categoria)` utiliza ese mapeo y rechaza categorías no autorizadas.
- Las señales de clasificación se agrupan en `SENALES_POR_CATEGORIA` dentro de `src/rules.py`.

### Clasificación local

`clasificar_reporte(descripcion, ubicacion)`:

1. Valida ambos campos mediante `EntradaReporte`.
2. Normaliza mayúsculas, acentos y puntuación únicamente para buscar señales.
3. Cuenta señales distintas de cada categoría en la descripción y la ubicación.
4. Devuelve `OTRO` cuando ninguna categoría tiene evidencia.

Cuando dos categorías obtienen la misma puntuación, se utiliza este orden estable de desempate:

```text
ALCANTARILLADO → AGUA → BASURA → ALUMBRADO → VIALIDAD → ESPACIO_PUBLICO
```

El orden favorece señales más específicas y evita, por ejemplo, que la palabra `parque` cambie un reporte de luminaria a `ESPACIO_PUBLICO`.

### Evaluación de prioridad

`evaluar_prioridad(descripcion, ubicacion, categoria)` aplica la siguiente precedencia:

1. `ALTA` cuando detecta una señal documentada de riesgo o afectación grave.
2. `BAJA` cuando detecta únicamente mantenimiento o deterioro estético.
3. `MEDIA` cuando existe una afectación reconocida sin peligro inmediato.
4. `BAJA` para un caso `OTRO` sin evidencia de urgencia.

La cercanía a una escuela u hospital solo refuerza prioridad alta cuando también existe una señal de peligro. El nombre del lugar por sí solo no convierte el reporte en urgente.

La función devuelve `EvaluacionPrioridad`; sus señales y justificación explican la recomendación. Nunca cambia el estado ni toma una decisión de revisión.

### Información faltante

`identificar_informacion_faltante(descripcion, ubicacion, categoria)` informa únicamente ausencias comprobables:

- Solicita ubicación o referencia más precisa para expresiones explícitamente insuficientes como `Sin especificar`.
- Solicita tipo de incidente o una descripción más específica cuando la categoría es `OTRO`.

No inventa barrio, dirección, duración, personas afectadas ni peligro.

### Fallback local

`analizar_reporte_local(descripcion, ubicacion)` compone las funciones anteriores y devuelve un `AnalisisReporte` válido con:

- categoría y área coherentes;
- prioridad y justificación deterministas;
- información faltante comprobable;
- `posibles_duplicados` vacío, porque su búsqueda pertenece a persistencia;
- `origen_analisis` igual a `REGLAS`.

El resumen local es extractivo: conserva la primera oración o un prefijo literal de la descripción. No agrega hechos ausentes del reporte.
