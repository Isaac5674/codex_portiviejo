# Plan de trabajo para Codex

## Forma de trabajo

Codex debe completar tareas pequeñas, verificables y ordenadas. No debe intentar construir todo el proyecto en una sola modificación.

## Fase 1: estructura y configuración

Objetivos:

- Crear estructura mínima.
- Configurar entorno.
- Crear `.env.example`.
- Crear `.gitignore`.
- Crear `requirements.txt`.
- Confirmar que Streamlit inicia.

Verificación:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Fase 2: modelos y reglas

Objetivos:

- Crear enumeraciones.
- Crear modelos Pydantic.
- Crear mapeo categoría-área.
- Crear reglas de prioridad.
- Crear modo local.

Verificación:

```bash
pytest tests/test_models.py tests/test_rules.py -q
```

## Fase 3: Supabase

Objetivos:

- Crear esquema.
- Activar RLS.
- Crear cliente centralizado.
- Crear repositorios.
- Probar creación, consulta y actualización.
- Probar auditoría.

Condición para continuar:

> No integrar IA hasta demostrar persistencia funcional.

## Fase 4: agente

Objetivos:

- Configurar OpenAI Agents SDK.
- Exigir salida estructurada.
- Crear herramientas autorizadas.
- Validar con Pydantic.
- Integrar respaldo local.

Condición para continuar:

> El agente debe producir un análisis válido sin guardar todavía decisiones finales.

## Fase 5: interfaz

Objetivos:

- Formulario.
- Resultado.
- Creación del expediente.
- Tabla.
- Revisión humana.
- Historial.

## Fase 6: errores y pruebas

Objetivos:

- Probar sin IA.
- Probar sin Supabase.
- Probar salida inválida.
- Probar auditoría.
- Probar cuatro casos de demostración.

## Fase 7: cierre

Objetivos:

- Revisar criterios de aceptación.
- Revisar secretos.
- Preparar datos de demo.
- Corregir textos.
- Detener nuevas funciones.

## Formato de cada tarea para Codex

```text
Objetivo:
Archivos permitidos:
Restricciones:
Comportamiento esperado:
Pruebas obligatorias:
Criterio de terminado:
```

## Prompt recomendado: implementación de una tarea

```text
Lee docs/README.md, docs/contexto-proyecto.md y el documento técnico relacionado. Implementa únicamente la tarea indicada. No cambies arquitectura, esquema, dependencias ni alcance salvo autorización explícita. Antes de editar, identifica los archivos afectados. Después de editar, ejecuta las pruebas relacionadas e informa archivos modificados, comandos ejecutados, resultados y limitaciones reales.
```

## Prompt recomendado: corrección de error

```text
Reproduce primero el error. Identifica la causa raíz con evidencia. Aplica el cambio mínimo necesario. No reescribas componentes no relacionados. Agrega o ajusta una prueba que falle antes del cambio y pase después. Ejecuta las pruebas relacionadas y documenta cualquier riesgo restante.
```

## Prompt recomendado: revisión final

```text
No agregues funciones. Revisa criterios de aceptación, seguridad, variables de entorno, RLS, auditoría, modo local y los cuatro casos de demostración. Corrige solo defectos verificables. Ejecuta pruebas. Informa claramente qué está listo y qué limitaciones permanecen.
```
