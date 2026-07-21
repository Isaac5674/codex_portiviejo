# Registro de decisiones técnicas

Este archivo evita que Codex reabra decisiones ya tomadas sin una razón válida.

## ADR-001: Streamlit como interfaz

**Estado:** Aceptada.

**Decisión:** Utilizar Streamlit para formulario, revisión, tablas e historial.

**Razón:** Reduce tiempo de desarrollo y mantiene un solo lenguaje.

**Consecuencia:** No crear un frontend separado durante el MVP.

## ADR-002: Supabase como única base de datos

**Estado:** Aceptada.

**Decisión:** Utilizar Supabase con PostgreSQL.

**Razón:** Persistencia remota, panel de administración, integración sencilla con Python y posibilidad de ampliar posteriormente.

**Consecuencia:** No utilizar MySQL, SQLite ni almacenamiento local como base oficial.

## ADR-003: Un agente coordinador

**Estado:** Aceptada.

**Decisión:** Utilizar un solo agente con herramientas internas.

**Razón:** Menor complejidad para una hackatón de cuatro horas.

**Consecuencia:** No crear arquitectura multiagente.

## ADR-004: Supervisión humana obligatoria

**Estado:** Aceptada.

**Decisión:** Toda recomendación debe ser revisada por un operador.

**Razón:** Reducir riesgo y mantener responsabilidad humana.

**Consecuencia:** El agente no puede aprobar ni rechazar.

## ADR-005: Salida estructurada con Pydantic

**Estado:** Aceptada.

**Decisión:** Validar resultados antes de persistir.

**Razón:** Evitar categorías, prioridades o estructuras inventadas.

**Consecuencia:** Una salida inválida debe corregirse o pasar al modo local.

## ADR-006: Duplicados como sugerencia

**Estado:** Aceptada.

**Decisión:** La similitud solo genera candidatos.

**Razón:** La similitud textual no confirma identidad.

**Consecuencia:** La confirmación es humana.

## ADR-007: Modo local obligatorio

**Estado:** Aceptada.

**Decisión:** Mantener clasificación por reglas cuando falle OpenAI.

**Razón:** La demo no debe depender totalmente de una API externa.

**Consecuencia:** Debe mostrarse el origen del análisis.

## Plantilla para nuevas decisiones

```text
## ADR-XXX: Título

Estado:
Fecha:
Decisión:
Contexto:
Razón:
Alternativas descartadas:
Consecuencias:
Archivos afectados:
Aprobado por:
```

No cambiar una decisión aceptada sin registrar una nueva ADR y obtener autorización humana.
