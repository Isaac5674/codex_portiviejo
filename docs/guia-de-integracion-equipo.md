# Guía de integración entre integrantes

Esta guía evita que cada módulo replique reglas o cambie contratos sin coordinación. El análisis sigue siendo una recomendación: la decisión final siempre corresponde a una persona operadora.

## Contrato estable del dominio

Los módulos de IA, persistencia e interfaz reciben y producen datos mediante los contratos de `src.models`.

```python
from src.models import AnalisisReporte, EntradaReporte
from src.rules import analizar_reporte_local, determinar_estado_inicial
```

`EntradaReporte` recibe únicamente `descripcion` y `ubicacion`. Antes de analizar o guardar un reporte, la interfaz debe validarlo con este modelo.

`AnalisisReporte` usa estos campos obligatorios:

| Campo | Uso para la integración |
|---|---|
| `resumen` | Texto breve del incidente sin inventar hechos. |
| `categoria` | Valor de `Categoria`; determina el área. |
| `prioridad` | Recomendación de `Prioridad`, nunca una aprobación. |
| `area_responsable` | Debe coincidir con la categoría. |
| `ubicacion` | Valor entregado por el ciudadano, sin completar datos faltantes. |
| `informacion_faltante` | Datos que debe solicitar o mostrar la interfaz. |
| `senales_riesgo` | Evidencia usada para explicar la prioridad. |
| `justificacion` | Explicación verificable de la recomendación. |
| `posibles_duplicados` | Candidatos; nunca una confirmación automática. |
| `origen_analisis` | `IA` o `REGLAS`, visible para el operador. |

El contrato rechaza campos adicionales y valores no autorizados. No se deben crear enumeraciones paralelas ni convertir los estados a cadenas libres en otros módulos.

## Acuerdo por integrante

### Integrante 2: agente y herramientas

1. Validar toda salida de IA construyendo `AnalisisReporte`.
2. Si OpenAI falla o la salida es inválida, usar `analizar_reporte_local(descripcion, ubicacion)`.
3. Mantener `origen_analisis` como `IA` solo para una salida de IA validada y como `REGLAS` en el fallback.
4. No aprobar, rechazar ni confirmar duplicados.

Prueba mínima: simular una falla del proveedor y comprobar que el fallback entrega un `AnalisisReporte` válido.

### Integrante 3: Supabase y auditoría

1. Recibir un `AnalisisReporte` validado, no un diccionario arbitrario de la interfaz.
2. Persistir las recomendaciones en campos separados de las decisiones humanas: `prioridad` en `prioridad_agente`, `area_responsable` en `area_agente` y `justificacion` en `justificacion_agente`.
3. Conservar `origen_analisis`, señales, faltantes y candidatos de duplicado para trazabilidad según el esquema acordado.
4. Devolver candidatos como `PosibleDuplicado`; no establecer un duplicado como confirmado desde el repositorio.

Prueba mínima: confirmar la respuesta de Supabase y luego la auditoría; si la auditoría falla, informar trazabilidad incompleta sin repetir la operación principal.

### Integrante 4: Streamlit e integración visible

1. Validar el formulario con `EntradaReporte` antes de invocar al agente.
2. Mostrar categoría, prioridad, área, justificación, faltantes, señales, candidatos y origen del análisis.
3. Obtener el estado inicial con `determinar_estado_inicial(analisis.informacion_faltante, analisis.posibles_duplicados)`.
4. Mantener la aprobación, modificación, rechazo, solicitud de información y marca de posible duplicado como acciones humanas explícitas.

Prueba mínima: comprobar que un reporte con ubicación `Sin especificar` queda en `REQUIERE_INFORMACION` y que un candidato no se presenta como duplicado confirmado.

## Secuencia de integración

1. Ejecutar `pytest -q` antes de unir un módulo.
2. Integrante 2 integra y prueba agente/fallback contra el contrato de dominio.
3. Integrante 3 integra repositorios y auditoría con datos de análisis validados.
4. Integrante 4 conecta interfaz, agente y repositorios, sin duplicar reglas.
5. Ejecutar la suite completa y los cuatro casos de demostración.
6. Solo después de completar los criterios de aceptación, preparar el despliegue.

## Regla para cambios de contrato

Si se necesita cambiar una enumeración, un campo de `AnalisisReporte`, un estado o el mapeo categoría-área, no se modifica unilateralmente. Se debe actualizar de forma coordinada el modelo, las reglas, el esquema, repositorios, agente, interfaz, documentación y pruebas. Mientras el MVP está en integración, se prefieren cambios aditivos y compatibles.

