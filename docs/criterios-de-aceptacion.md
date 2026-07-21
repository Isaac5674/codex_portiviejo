# Criterios de aceptación

## Definición de terminado

PortoReporta está listo para la demostración cuando cumple todos los criterios obligatorios.

## Aplicación

- [ ] Inicia con `streamlit run app.py`.
- [ ] No requiere tecnologías no documentadas.
- [ ] La navegación principal funciona.
- [ ] Los errores se muestran de forma comprensible.

## Entrada y análisis

- [ ] Se puede ingresar descripción.
- [ ] Se puede ingresar ubicación.
- [ ] Se validan campos vacíos.
- [ ] Se obtiene un resumen.
- [ ] Se obtiene una categoría válida.
- [ ] Se obtiene una prioridad válida.
- [ ] Se obtiene un área válida.
- [ ] Se obtiene una justificación.
- [ ] Se muestra información faltante.
- [ ] Se muestran señales de riesgo.
- [ ] La salida pasa por Pydantic.
- [ ] Se identifica el origen del análisis.

## Respaldo

- [ ] El sistema funciona sin la API de IA.
- [ ] El modo local se muestra claramente.
- [ ] El modo local produce una estructura válida.
- [ ] El fallo de IA no bloquea el flujo.

## Duplicados

- [ ] Se consultan candidatos en Supabase.
- [ ] Se compara categoría y ubicación.
- [ ] Se muestra similitud como sugerencia.
- [ ] La IA no confirma duplicados.

## Persistencia

- [ ] Supabase es la única base de datos.
- [ ] El cliente está centralizado.
- [ ] Las consultas están centralizadas.
- [ ] Se puede crear una solicitud.
- [ ] Se puede consultar una solicitud.
- [ ] Se pueden listar solicitudes.
- [ ] Se puede actualizar una solicitud.
- [ ] RLS está activado.
- [ ] No existen políticas anónimas públicas.
- [ ] No se muestra éxito ante una falla.

## Revisión humana

- [ ] El agente no aprueba.
- [ ] El operador puede aprobar.
- [ ] El operador puede modificar y aprobar.
- [ ] El operador puede rechazar.
- [ ] El operador puede solicitar información.
- [ ] El operador puede marcar posible duplicado.
- [ ] El motivo es obligatorio al modificar.

## Auditoría

- [ ] Se registra la creación.
- [ ] Se registra el análisis.
- [ ] Se registra el origen del análisis.
- [ ] Se registra la revisión humana.
- [ ] Se registran cambios.
- [ ] Se registra el motivo.
- [ ] Se puede consultar el historial.

## Seguridad

- [ ] `.env` no está en Git.
- [ ] No existen claves en el código.
- [ ] No existen claves en logs.
- [ ] La clave de Supabase solo se usa en servidor.
- [ ] No se almacenan datos personales innecesarios.
- [ ] La interfaz indica que es un prototipo.
- [ ] No se afirma integración municipal real.

## Pruebas

- [ ] Pasan pruebas de reglas.
- [ ] Pasan pruebas de modelos.
- [ ] Se probaron los cuatro casos de demostración.
- [ ] Se probó falla de IA.
- [ ] Se probó falla de Supabase.
- [ ] Se documentaron limitaciones conocidas.

## Regla final

Cuando todos los criterios estén marcados:

- No agregar funciones.
- Corregir únicamente defectos.
- Preparar la demostración.
- Crear un commit estable.
