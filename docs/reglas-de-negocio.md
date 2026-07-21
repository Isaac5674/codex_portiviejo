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
