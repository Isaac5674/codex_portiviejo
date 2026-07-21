# Contratos de datos

## Objetivo

Definir estructuras estables entre la interfaz, el agente, las reglas y Supabase.

## Enumeraciones autorizadas

### Categorías

- `AGUA`
- `BASURA`
- `ALUMBRADO`
- `VIALIDAD`
- `ALCANTARILLADO`
- `ESPACIO_PUBLICO`
- `OTRO`

### Prioridades

- `BAJA`
- `MEDIA`
- `ALTA`

### Estados

- `PENDIENTE_REVISION`
- `REQUIERE_INFORMACION`
- `APROBADA`
- `MODIFICADA_Y_APROBADA`
- `RECHAZADA`
- `POSIBLE_DUPLICADO`

### Actores de auditoría

- `CIUDADANO`
- `AGENTE`
- `OPERADOR`
- `SISTEMA`

## Entrada mínima del reporte

```json
{
  "descripcion": "Hay una alcantarilla sin tapa frente a la escuela.",
  "ubicacion": "Barrio San José, frente a la escuela"
}
```

Reglas:

- `descripcion` no puede estar vacía.
- `ubicacion` no puede estar vacía.
- Valores como `Sin especificar` deben tratarse como información insuficiente.
- No se deben agregar datos personales innecesarios.

## Salida estructurada del análisis

```json
{
  "resumen": "Alcantarilla sin tapa frente a una escuela",
  "categoria": "ALCANTARILLADO",
  "prioridad": "ALTA",
  "area_responsable": "Alcantarillado",
  "ubicacion": "Barrio San José, frente a la escuela",
  "informacion_faltante": [],
  "senales_riesgo": [
    "alcantarilla abierta",
    "cercanía a una escuela",
    "riesgo de accidente"
  ],
  "justificacion": "Se propone prioridad alta por riesgo para peatones.",
  "posibles_duplicados": [],
  "origen_analisis": "IA"
}
```

## Reglas del contrato

- La categoría debe pertenecer a la lista autorizada.
- La prioridad debe pertenecer a la lista autorizada.
- El área debe corresponder a la categoría.
- `informacion_faltante` debe ser una lista.
- `senales_riesgo` debe ser una lista.
- `posibles_duplicados` debe ser una lista.
- `justificacion` no puede estar vacía.
- `origen_analisis` debe ser `IA` o `REGLAS`.
- La salida debe validarse antes de persistirse.

## Expediente preliminar

Un expediente nuevo debe iniciar con:

```json
{
  "estado": "PENDIENTE_REVISION",
  "prioridad_final": null,
  "area_final": null,
  "revisado_en": null,
  "revisor": null,
  "motivo_revision": null
}
```

Cuando falte información crítica, puede iniciar con:

```json
{
  "estado": "REQUIERE_INFORMACION"
}
```

## Cambio humano

```json
{
  "solicitud_id": 123,
  "accion": "MODIFICAR_Y_APROBAR",
  "categoria_final": "VIALIDAD",
  "prioridad_final": "ALTA",
  "area_final": "Obras públicas",
  "motivo_revision": "Se observó riesgo de accidente vehicular.",
  "revisor": "Operador demo"
}
```

## Campos actualizables

Desde la revisión humana solo se pueden modificar campos expresamente permitidos:

- `categoria`
- `prioridad_final`
- `area_final`
- `estado`
- `revisado_en`
- `revisor`
- `motivo_revision`
- `posible_duplicado_de`

No aceptar un diccionario arbitrario del usuario para actualizar cualquier columna.

## Compatibilidad

Todo cambio en un contrato requiere actualizar:

- Modelos Pydantic.
- Reglas.
- Repositorios.
- Interfaz.
- Pruebas.
- Documentación.
- Esquema SQL, cuando corresponda.

## Implementación actual del contrato de dominio

La fuente ejecutable de estos contratos es `src/models.py`.

### Enumeraciones

| Clase | Valores |
|---|---|
| `Categoria` | `AGUA`, `BASURA`, `ALUMBRADO`, `VIALIDAD`, `ALCANTARILLADO`, `ESPACIO_PUBLICO`, `OTRO` |
| `AreaResponsable` | Agua potable, Gestión ambiental, Alumbrado público, Obras públicas, Alcantarillado, Espacios públicos, Atención ciudadana |
| `Prioridad` | `BAJA`, `MEDIA`, `ALTA` |
| `EstadoSolicitud` | `PENDIENTE_REVISION`, `REQUIERE_INFORMACION`, `APROBADA`, `MODIFICADA_Y_APROBADA`, `RECHAZADA`, `POSIBLE_DUPLICADO` |
| `ActorAuditoria` | `CIUDADANO`, `AGENTE`, `OPERADOR`, `SISTEMA` |
| `OrigenAnalisis` | `IA`, `REGLAS` |

`AREA_POR_CATEGORIA` es la única correspondencia ejecutable entre categoría y área. El modelo de análisis rechaza un área válida que no corresponda a la categoría indicada.

### Modelos Pydantic

#### `EntradaReporte`

- Requiere `descripcion` y `ubicacion` como textos no vacíos.
- Elimina espacios exteriores y combina espacios consecutivos.
- Conserva el contenido proporcionado; no completa ni inventa datos.
- Acepta `Sin especificar` como texto de entrada, pero las reglas lo identifican como ubicación insuficiente.

#### `PosibleDuplicado`

```json
{
  "solicitud_id": 123,
  "similitud": 0.84,
  "razon": "Misma categoría y referencia de ubicación"
}
```

- `solicitud_id` debe ser un entero positivo.
- `similitud` debe estar entre `0.0` y `1.0`.
- `razon` no puede estar vacía.
- Este modelo representa un candidato; no confirma que dos solicitudes sean duplicadas.

#### `EvaluacionPrioridad`

Contiene `prioridad`, `senales_riesgo` y `justificacion`. Representa una recomendación determinista, no una decisión humana.

#### `AnalisisReporte`

Es el contrato compartido por el análisis con IA y el fallback local. Exige todos los campos de la salida estructurada, aplica valores predeterminados independientes para sus listas y rechaza campos adicionales.

Reglas adicionales:

- `resumen`, `ubicacion` y `justificacion` no pueden estar vacíos.
- Las listas de texto no pueden contener elementos vacíos.
- `area_responsable` debe corresponder a `categoria` mediante `AREA_POR_CATEGORIA`.
- Los candidatos de `posibles_duplicados` se validan mediante `PosibleDuplicado`.
- El fallback local siempre establece `origen_analisis` como `REGLAS`.

Los modelos no importan Streamlit, OpenAI, Supabase, repositorios ni servicios externos.
