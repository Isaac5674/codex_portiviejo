# Alcance del MVP

## Objetivo del MVP

Demostrar un flujo completo y trazable que convierta un reporte ciudadano en un expediente preliminar, lo almacene en Supabase y lo someta a revisión humana.

## Flujo mínimo obligatorio

1. El ciudadano ingresa una descripción.
2. El ciudadano ingresa una ubicación o referencia.
3. El sistema analiza el reporte.
4. El sistema devuelve un resultado estructurado.
5. El sistema propone categoría, prioridad y área.
6. El sistema indica información faltante.
7. El sistema busca posibles duplicados.
8. El usuario crea el expediente.
9. El expediente se guarda en Supabase.
10. El operador revisa el expediente.
11. El operador aprueba, modifica o rechaza.
12. La acción queda registrada en auditoría.
13. El sistema permite consultar solicitudes e historial.

## Funciones obligatorias

- Formulario de reporte.
- Análisis con IA.
- Modo local de respaldo.
- Validación Pydantic.
- Persistencia en Supabase.
- Revisión humana.
- Auditoría.
- Lista de solicitudes.
- Historial por solicitud.
- Detección básica de posibles duplicados.
- Manejo visible de errores.

## Funciones opcionales

Solo implementar cuando el flujo obligatorio esté estable:

- Filtros.
- Métricas simples.
- Exportación CSV.
- Vista detallada mejorada.
- Datos de demostración.
- Mejoras visuales.
- Supabase Storage.
- Supabase Auth básica.

## Fuera del alcance

- Integración municipal real.
- Aplicación móvil.
- Mapas.
- GPS.
- WhatsApp.
- Correos.
- Reconocimiento de imágenes.
- Autenticación compleja.
- Roles avanzados.
- Gestión de cuadrillas.
- Seguimiento hasta resolución física.
- Microservicios.
- Dashboard analítico avanzado.
- Modelo de IA entrenado por el equipo.

## Regla de priorización

Ante falta de tiempo, aplicar este orden:

1. Flujo completo.
2. Persistencia.
3. Revisión humana.
4. Auditoría.
5. Respaldo sin IA.
6. Pruebas.
7. Claridad visual.
8. Funciones opcionales.

## Regla de cambio de alcance

Todo nuevo requerimiento debe responder:

- ¿Es obligatorio para demostrar el problema?
- ¿Puede completarse sin romper el flujo actual?
- ¿Existe tiempo para probarlo?
- ¿Requiere una nueva dependencia?
- ¿Modifica el esquema?
- ¿Introduce un servicio externo?

Si una respuesta implica riesgo, el cambio debe aplazarse.
