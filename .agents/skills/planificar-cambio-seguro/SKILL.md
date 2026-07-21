---
name: planificar-cambio-seguro
description: Analiza y planifica cualquier cambio funcional, corrección, refactorización o integración antes de editar código en PortoReporta. Úsala cuando una tarea pueda afectar comportamiento existente, contratos, dependencias, datos o varios archivos. No la uses para cambios exclusivamente ortográficos o de documentación sin efecto técnico.
---

# Planificar un cambio seguro

## Propósito

Evitar modificaciones impulsivas que rompan funciones existentes, dupliquen lógica o acoplen nuevas capacidades a implementaciones concretas.

Antes de editar código, esta skill obliga a comprender:

- Qué comportamiento existe.
- Qué archivos y contratos participan.
- Qué depende del componente que se modificará.
- Qué extensión puede agregarse sin alterar innecesariamente código estable.
- Qué pruebas demostrarán que el cambio nuevo funciona y que lo anterior no se dañó.

## Principios obligatorios

1. Preservar el comportamiento existente salvo que el usuario solicite cambiarlo explícitamente.
2. Aplicar el principio abierto-cerrado:
   - Extender mediante nuevos componentes, estrategias, reglas o implementaciones.
   - Evitar editar cadenas crecientes de `if/elif`, funciones centrales o módulos estables cada vez que aparece un caso nuevo.
3. Reutilizar abstracciones existentes antes de crear alternativas paralelas.
4. Evitar duplicar lógica.
5. Mantener interfaces y contratos compatibles cuando sea razonable.
6. Hacer el cambio mínimo que resuelva el problema completo.
7. No introducir tecnologías, capas o patrones sin una necesidad concreta.
8. No comenzar a editar hasta terminar el análisis de impacto.

## Flujo obligatorio

### 1. Leer el contexto

Antes de proponer cambios:

1. Leer `AGENTS.md`.
2. Leer `docs/contexto-proyecto.md`.
3. Identificar otras instrucciones aplicables al directorio.
4. Revisar los archivos relacionados con la tarea.
5. Revisar pruebas existentes.
6. Revisar el estado de Git para no sobrescribir trabajo ajeno.

## 2. Definir el cambio

Expresar en una frase:

- Problema actual.
- Comportamiento deseado.
- Criterio observable de éxito.

Ejemplo:

```text
Problema: agregar una categoría obliga a modificar lógica repetida en varios archivos.
Comportamiento deseado: las categorías se registran en una sola configuración reutilizable.
Éxito: una categoría nueva se incorpora sin modificar la interfaz, el agente ni el repositorio.
```

## 3. Identificar contratos

Revisar qué datos entran y salen de los componentes afectados.

Buscar:

- Modelos Pydantic.
- Firmas de funciones.
- Valores enumerados.
- Estructuras JSON.
- Métodos públicos.
- Consultas a Supabase.
- Estados de solicitudes.
- Herramientas expuestas al agente.
- Datos esperados por Streamlit.
- Pruebas que describen el comportamiento.

No cambiar un contrato público sin:

1. Justificación.
2. Actualización de consumidores.
3. Pruebas.
4. Estrategia de compatibilidad o migración.

## 4. Construir el mapa de impacto

Antes de editar, elaborar una lista breve:

```text
Archivos que probablemente cambiarán:
- ...

Archivos que consumen ese comportamiento:
- ...

Riesgos:
- ...

Comportamientos anteriores que deben preservarse:
- ...

Pruebas necesarias:
- ...
```

## 5. Buscar un punto de extensión

Preferir, en este orden:

1. Agregar datos a una configuración central.
2. Añadir una implementación nueva detrás de una interfaz existente.
3. Agregar una estrategia o regla registrable.
4. Componer funciones pequeñas existentes.
5. Extender un modelo compatible.
6. Modificar una función estable solamente cuando no exista un punto de extensión razonable.

Ejemplos de buenos puntos de extensión para PortoReporta:

- Registro central de categorías.
- Mapa de áreas responsables.
- Estrategias de prioridad.
- Proveedores de análisis:
  - OpenAI.
  - Modo local por reglas.
- Repositorio de solicitudes.
- Repositorio de auditoría.
- Detectores de duplicados.

## 6. Elegir entre extensión y modificación

### Extender

Extender cuando:

- Se agrega una categoría.
- Se agrega una regla.
- Se agrega un nuevo proveedor.
- Se agrega una forma de exportación.
- Se agrega una nueva vista que consume servicios existentes.
- Se agrega una nueva validación independiente.

### Modificar

Modificar cuando:

- Existe un error en la implementación actual.
- El contrato actual no representa correctamente el dominio.
- La duplicación demuestra que falta una abstracción.
- Una regla central cambió por requerimiento.
- Mantener compatibilidad produciría un diseño más peligroso.

No aplicar abierto-cerrado de forma dogmática. Una abstracción incorrecta debe corregirse, no rodearse con más capas.

## 7. Definir el plan

El plan debe indicar:

1. Archivos a crear.
2. Archivos a modificar.
3. Contratos que se conservan.
4. Punto de extensión utilizado.
5. Pruebas nuevas o actualizadas.
6. Riesgos y mitigaciones.
7. Orden de implementación.

El plan debe ser proporcional al cambio. No crear un documento largo para una modificación pequeña.

## 8. Implementar por incrementos

Orden recomendado:

1. Prueba o criterio verificable.
2. Modelo o contrato.
3. Lógica de dominio.
4. Persistencia.
5. Integración.
6. Interfaz.
7. Documentación.

Después de cada incremento:

- Ejecutar la prueba más cercana.
- Revisar el diff.
- Confirmar que no apareció duplicación.

## 9. Revisar el diff

Antes de finalizar, comprobar:

- ¿Se modificaron archivos no relacionados?
- ¿Se repitió lógica existente?
- ¿Se añadió un `if` especial donde debía existir una extensión?
- ¿Se filtró una dependencia de Supabase hacia la interfaz o el dominio?
- ¿Se cambió un contrato sin actualizar consumidores?
- ¿Se eliminó comportamiento anterior?
- ¿Se dejaron comentarios temporales, claves o datos de prueba?
- ¿El cambio puede explicarse con claridad?

## Salida esperada

Antes de editar, presentar o registrar internamente:

```text
Objetivo:
...

Impacto:
...

Punto de extensión:
...

Archivos:
...

Pruebas:
...

Riesgos:
...
```

Después de editar:

```text
Cambio realizado:
...

Comportamiento preservado:
...

Pruebas ejecutadas:
...

Riesgos pendientes:
...
```

## Casos en los que debe detenerse

Detener la implementación y pedir una decisión cuando:

- Dos requisitos se contradicen.
- El cambio requiere romper un contrato público.
- Hace falta una credencial o servicio no disponible.
- No existe forma segura de migrar datos.
- Las pruebas existentes fallan antes del cambio.
- El cambio solicitado supera el alcance definido en `docs/contexto-proyecto.md`.
