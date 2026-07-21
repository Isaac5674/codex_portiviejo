---
name: proteger-arquitectura-modular
description: Mantiene la arquitectura modular, reutilizable y abierta a extensiones de PortoReporta al crear, mover, extender o refactorizar código. Úsala cuando se agreguen clases, funciones, módulos, reglas, proveedores o integraciones. No la uses para editar únicamente textos, comentarios o documentación.
---

# Proteger la arquitectura modular

## Propósito

Impedir que nuevas funciones mezclen responsabilidades, creen dependencias circulares o hagan que la interfaz, el agente, las reglas y Supabase queden acoplados entre sí.

La arquitectura debe permitir agregar capacidades con cambios localizados y verificables.

## Modelo mental

Cada capa responde una pregunta distinta:

```text
Interfaz:
¿Cómo interactúa el usuario?

Aplicación y agente:
¿Qué flujo se ejecuta?

Dominio y reglas:
¿Qué decisiones son válidas?

Repositorios:
¿Qué operaciones de persistencia necesita el sistema?

Supabase:
¿Cómo se ejecutan esas operaciones en la tecnología elegida?
```

Una capa no debe apropiarse de responsabilidades de otra.

## Límites arquitectónicos de PortoReporta

### `app.py`

Responsabilidad:

- Renderizar Streamlit.
- Recibir acciones del usuario.
- Mostrar resultados.
- Mantener estado de sesión.
- Invocar servicios o casos de uso.

No debe:

- Construir consultas de Supabase.
- Contener reglas de prioridad.
- Interpretar respuestas del modelo directamente.
- Duplicar validaciones de dominio.
- Contener claves.
- Decidir el área responsable.

### `src/agent.py`

Responsabilidad:

- Configurar y ejecutar el agente.
- Transformar la respuesta en un modelo validado.
- Coordinar herramientas autorizadas.
- Activar el modo de respaldo cuando corresponda.

No debe:

- Renderizar Streamlit.
- Crear el cliente de Supabase repetidamente.
- Contener SQL.
- Aprobar solicitudes.
- Saltarse modelos Pydantic.

### `src/models.py`

Responsabilidad:

- Definir contratos de datos.
- Validar categorías, prioridades y estados.
- Describir entradas y salidas.

No debe:

- Consultar Supabase.
- Mostrar interfaz.
- Ejecutar llamadas de IA.
- Contener efectos secundarios.

### `src/rules.py`

Responsabilidad:

- Contener reglas deterministas.
- Definir configuraciones del dominio.
- Evaluar señales de riesgo.
- Resolver áreas responsables.

No debe:

- Importar Streamlit.
- Importar el cliente de Supabase.
- Realizar llamadas de red.
- Escribir en la base de datos.

### `src/tools.py`

Responsabilidad:

- Exponer herramientas pequeñas al agente.
- Adaptar entradas validadas.
- Delegar la operación real a reglas, servicios o repositorios.

No debe:

- Convertirse en un segundo repositorio.
- Duplicar reglas.
- Mezclar varias acciones no relacionadas.
- Aceptar datos sin validación.

### `src/repositories.py`

Responsabilidad:

- Ofrecer operaciones de persistencia con nombres del dominio.
- Encapsular consultas a Supabase.
- Convertir errores técnicos en errores controlados.

No debe:

- Importar Streamlit.
- Decidir prioridades.
- Ejecutar llamadas a OpenAI.
- Formatear elementos visuales.
- Permitir nombres arbitrarios de tablas o columnas.

### `src/supabase_client.py`

Responsabilidad:

- Crear una única configuración de cliente.
- Validar variables de entorno.
- Proporcionar el cliente al repositorio.

No debe:

- Contener casos de uso.
- Exponer credenciales.
- Implementar reglas.
- Ejecutar consultas específicas del dominio.

## Regla de dirección de dependencias

Dirección permitida:

```text
app.py
  ↓
servicios o agent.py
  ↓
models.py / rules.py / tools.py
  ↓
repositories.py
  ↓
supabase_client.py
```

Dependencias prohibidas:

```text
rules.py → Streamlit
models.py → Supabase
repositories.py → Streamlit
supabase_client.py → agent.py
dominio → interfaz
```

Evitar dependencias circulares.

## Principio de responsabilidad única

Cada módulo, clase y función debe tener una razón principal para cambiar.

Señales de violación:

- Una función valida, consulta, decide y renderiza.
- Un archivo contiene reglas, consultas y elementos visuales.
- Cambiar Supabase obliga a modificar la interfaz.
- Cambiar una categoría obliga a editar cinco archivos.
- Una función tiene demasiados parámetros no relacionados.
- El nombre de una función necesita “y”.

Ante estas señales:

1. Identificar responsabilidades.
2. Separarlas por comportamiento.
3. Conservar contratos claros.
4. Añadir pruebas para cada unidad.

## Principio abierto-cerrado

El código debe estar abierto a nuevas capacidades y cerrado a modificaciones innecesarias.

### Aplicación en categorías

Incorrecto:

```python
if categoria == "AGUA":
    area = "Agua potable"
elif categoria == "BASURA":
    area = "Gestión ambiental"
elif categoria == "ALUMBRADO":
    area = "Alumbrado público"
```

Preferido:

```python
AREAS_POR_CATEGORIA = {
    "AGUA": "Agua potable",
    "BASURA": "Gestión ambiental",
    "ALUMBRADO": "Alumbrado público",
}
```

Una categoría nueva debe agregarse en un punto central y validado.

### Aplicación en proveedores de análisis

Definir un contrato común:

```python
from typing import Protocol

class AnalizadorReporte(Protocol):
    def analizar(self, descripcion: str, ubicacion: str):
        ...
```

Implementaciones posibles:

```text
AnalizadorOpenAI
AnalizadorPorReglas
```

La interfaz debe depender del contrato, no de una implementación concreta.

### Aplicación en detección de duplicados

Separar la política de similitud de la consulta de candidatos.

```text
Repositorio:
obtiene candidatos.

Detector:
calcula similitud.

Servicio:
coordina y devuelve sugerencias.
```

Así puede cambiarse el algoritmo sin reescribir la persistencia.

## Reutilización correcta

Reutilizar no significa crear una función genérica para todo.

Reutilizar cuando:

- Existe comportamiento repetido con el mismo significado.
- Hay un contrato estable.
- Dos consumidores necesitan la misma operación.
- La abstracción puede nombrarse claramente.

No abstraer cuando:

- Solo existe una coincidencia superficial.
- Los comportamientos cambiarán por razones diferentes.
- La abstracción requiere demasiadas banderas.
- El resultado sería más difícil de entender que la duplicación temporal.

## Inyección de dependencias sencilla

Preferir pasar dependencias de forma explícita.

Ejemplo:

```python
class ServicioSolicitudes:
    def __init__(self, repositorio, analizador):
        self.repositorio = repositorio
        self.analizador = analizador
```

Esto permite:

- Sustituir Supabase por un doble de prueba.
- Sustituir OpenAI por reglas.
- Probar sin red.
- Evitar variables globales ocultas.

No construir un contenedor complejo de dependencias para el MVP.

## Compatibilidad

Al extender código:

- Mantener nombres y tipos públicos existentes cuando sea razonable.
- Añadir parámetros opcionales al final.
- No cambiar formatos almacenados sin migración.
- No eliminar estados o categorías en uso.
- No renombrar columnas directamente en producción sin revisar consumidores.
- Añadir valores predeterminados cuando se incorporen campos no obligatorios.

## Proceso al crear una nueva funcionalidad

1. Identificar la capa propietaria.
2. Definir el contrato.
3. Revisar si existe un punto de extensión.
4. Implementar la lógica independiente.
5. Integrarla mediante composición.
6. Añadir persistencia solo si es necesaria.
7. Conectar la interfaz al final.
8. Ejecutar pruebas de unidad e integración.
9. Revisar dependencias y duplicación.

## Lista de revisión

Antes de finalizar:

- [ ] La interfaz no consulta Supabase directamente.
- [ ] Las reglas no conocen Streamlit ni Supabase.
- [ ] Los modelos no tienen efectos secundarios.
- [ ] El agente no aprueba solicitudes.
- [ ] Las consultas están centralizadas.
- [ ] Las nuevas variantes usan puntos de extensión.
- [ ] No existe lógica duplicada.
- [ ] No hay dependencia circular.
- [ ] Los nombres expresan intención.
- [ ] Las funciones tienen una responsabilidad principal.
- [ ] El cambio puede probarse sin ejecutar toda la aplicación.
- [ ] El modo de respaldo sigue funcionando.

## Criterio de éxito

Una modificación es arquitectónicamente aceptable cuando:

- El cambio se limita a los módulos responsables.
- Los consumidores dependen de contratos estables.
- Una variante nueva no exige reescribir el flujo central.
- Las pruebas pueden sustituir dependencias externas.
- El comportamiento anterior continúa funcionando.
