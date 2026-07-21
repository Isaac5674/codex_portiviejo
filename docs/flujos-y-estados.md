# Flujos y estados

## Flujo de creación

```text
Formulario
  ↓
Validación de entrada
  ↓
Análisis con IA
  ↓
¿Falló la IA?
  ├─ No → Validación Pydantic
  └─ Sí → Clasificación local por reglas
  ↓
Búsqueda de posibles duplicados
  ↓
Presentación del análisis
  ↓
Confirmación para crear expediente
  ↓
Inserción en Supabase
  ↓
Registro de auditoría
```

## Flujo de revisión

```text
Seleccionar solicitud
  ↓
Mostrar recomendación del agente
  ↓
Mostrar historial
  ↓
Operador decide
  ├─ Aprobar
  ├─ Modificar y aprobar
  ├─ Rechazar
  ├─ Solicitar información
  └─ Marcar posible duplicado
  ↓
Actualizar solicitud
  ↓
Registrar auditoría
  ↓
Mostrar resultado
```

## Estados permitidos

| Estado | Uso |
|---|---|
| `PENDIENTE_REVISION` | Expediente creado y aún no revisado |
| `REQUIERE_INFORMACION` | Faltan datos para una revisión adecuada |
| `APROBADA` | El operador aceptó la recomendación |
| `MODIFICADA_Y_APROBADA` | El operador cambió datos y aprobó |
| `RECHAZADA` | El operador rechazó el expediente |
| `POSIBLE_DUPLICADO` | Existe un caso candidato que debe evaluarse |

## Transiciones permitidas

| Desde | Hacia |
|---|---|
| Nuevo análisis | `PENDIENTE_REVISION` |
| Nuevo análisis incompleto | `REQUIERE_INFORMACION` |
| `PENDIENTE_REVISION` | `APROBADA` |
| `PENDIENTE_REVISION` | `MODIFICADA_Y_APROBADA` |
| `PENDIENTE_REVISION` | `RECHAZADA` |
| `PENDIENTE_REVISION` | `REQUIERE_INFORMACION` |
| `PENDIENTE_REVISION` | `POSIBLE_DUPLICADO` |
| `REQUIERE_INFORMACION` | `PENDIENTE_REVISION` |
| `POSIBLE_DUPLICADO` | `APROBADA` |
| `POSIBLE_DUPLICADO` | `MODIFICADA_Y_APROBADA` |
| `POSIBLE_DUPLICADO` | `RECHAZADA` |

## Transiciones prohibidas

- Crear directamente como `APROBADA`.
- Crear directamente como `RECHAZADA`.
- Cambiar de `RECHAZADA` a `APROBADA` sin una acción humana explícita y auditada.
- Cambiar estado silenciosamente.
- Modificar un caso revisado sin registrar motivo.

## Reglas de interfaz

- Mostrar siempre el estado actual.
- Identificar si el análisis provino de IA o reglas.
- Pedir motivo al modificar.
- Pedir confirmación antes de rechazar.
- No mostrar éxito si la auditoría falló.
- Permitir reintentar una operación fallida.
