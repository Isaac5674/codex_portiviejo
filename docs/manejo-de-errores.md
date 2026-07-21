# Manejo de errores y modos de respaldo

## Principio

Un fallo debe ser visible, comprensible y recuperable. El sistema no debe fingir éxito.

## Falla de OpenAI

Comportamiento obligatorio:

1. Capturar la excepción.
2. Mostrar una advertencia.
3. Ejecutar el modo local basado en reglas.
4. Validar la salida local.
5. Marcar `origen_analisis` como `REGLAS`.
6. Registrar el uso del modo local si el expediente se guarda.
7. Continuar el flujo sin aprobación automática.

No hacer:

- Mostrar una respuesta inventada como si viniera de IA.
- Ocultar que se usó el respaldo.
- Reintentar indefinidamente.
- Bloquear toda la aplicación.

## Falla de Supabase

Comportamiento obligatorio:

1. Mostrar un error claro.
2. No afirmar que el expediente fue guardado.
3. Mantener el análisis temporalmente en `st.session_state`.
4. Permitir reintento.
5. Mantener Supabase como base oficial.
6. Diferenciar modo de demostración sin persistencia.

No hacer:

- Guardar silenciosamente en SQLite.
- Guardar silenciosamente en JSON.
- Mostrar un ID inventado.
- Crear una falsa auditoría local como si fuera oficial.

## Falla de validación

Cuando Pydantic rechace la salida:

1. Registrar el error técnico sin secretos.
2. Intentar normalizar únicamente valores seguros.
3. Si no se puede validar, usar reglas locales.
4. Mostrar una explicación sencilla.
5. No persistir una estructura inválida.

## Falla de auditoría

Si la solicitud se guardó pero la auditoría falló:

- Informar que la trazabilidad quedó incompleta.
- No declarar la operación totalmente finalizada.
- Permitir reintentar el evento.
- Evitar repetir la operación principal si ya se confirmó.

## Falla de búsqueda de duplicados

- Continuar con el análisis.
- Mostrar que la búsqueda no estuvo disponible.
- No marcar automáticamente un duplicado.
- Registrar el fallo si se crea el expediente.

## Mensajes recomendados

### IA no disponible

```text
El análisis con IA no está disponible. Se utilizó el modo local basado en reglas.
```

### Supabase no disponible

```text
No fue posible guardar el expediente en Supabase. El análisis se conserva temporalmente para volver a intentarlo.
```

### Auditoría incompleta

```text
La solicitud fue actualizada, pero no se pudo completar el registro de auditoría. Reintente antes de continuar.
```

## Pruebas de fallos

Deben existir pruebas o validaciones manuales para:

- API de IA sin clave.
- API de IA con error.
- Supabase sin variables.
- Supabase con error de red.
- Respuesta vacía de Supabase.
- Salida inválida del agente.
- Auditoría fallida.
- Campos vacíos.
- Ubicación insuficiente.
