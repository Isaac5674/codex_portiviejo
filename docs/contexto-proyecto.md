# Contexto del proyecto: PortoReporta

> Documento principal de contexto para Codex.  
> Ruta recomendada dentro del repositorio: `docs/contexto-proyecto.md`  
> Base de datos elegida: **Supabase (PostgreSQL administrado)**  
> No utilizar MySQL ni SQLite en este proyecto.

---

# 1. Nombre del proyecto

## PortoReporta

**Nombre descriptivo:**  
Agente inteligente para la clasificación, priorización y gestión trazable de solicitudes ciudadanas.

**Tipo de producto:**  
Prototipo funcional para una hackatón de cuatro horas.

**Reto elegido:**  
Agentes y automatización con propósito.

**ODS relacionados:**

- ODS 8: Trabajo decente y crecimiento económico.
- ODS 9: Industria, innovación e infraestructura.

---

# 2. Descripción general

PortoReporta es un sistema asistido por inteligencia artificial que recibe solicitudes ciudadanas escritas en lenguaje natural y las transforma en expedientes organizados.

El agente debe:

1. Leer la descripción del ciudadano.
2. Extraer la información importante.
3. Identificar la categoría del problema.
4. Proponer una prioridad.
5. Seleccionar el área responsable.
6. Detectar información faltante.
7. Buscar posibles casos duplicados.
8. Crear un expediente preliminar.
9. Enviar el caso a revisión humana.
10. Guardar cada decisión en Supabase.

La inteligencia artificial no toma la decisión final. Un operador humano debe aprobar, modificar o rechazar la recomendación.

---

# 3. Preguntas detonantes

## ¿Cuál es el problema que se busca resolver?

Muchas solicitudes ciudadanas llegan mediante mensajes, llamadas, formularios o redes sociales con información desordenada, incompleta o poco clara.

Ejemplos:

- “Hay una fuga desde ayer frente a la escuela”.
- “La calle está llena de huecos”.
- “No funciona la lámpara del parque”.
- “Hay basura acumulada cerca del mercado”.
- “Existe una alcantarilla abierta y alguien puede caerse”.

Antes de que una institución pueda atender estos reportes, una persona debe:

1. Leer el mensaje.
2. Comprender qué ocurrió.
3. Identificar la ubicación.
4. Clasificar el problema.
5. Estimar su prioridad.
6. Determinar el área responsable.
7. Revisar si falta información.
8. Registrar el caso.
9. Justificar la decisión.

Este trabajo manual consume tiempo, puede generar clasificaciones inconsistentes y dificulta conocer por qué se tomó cada decisión.

---

## ¿Qué se busca solucionar?

Se busca automatizar la etapa inicial de recepción, análisis y organización de solicitudes ciudadanas.

El sistema debe transformar un mensaje no estructurado en un expediente que contenga:

- Resumen del problema.
- Descripción original.
- Ubicación.
- Categoría.
- Prioridad propuesta.
- Área responsable.
- Información faltante.
- Señales de riesgo.
- Posibles duplicados.
- Justificación de la decisión.
- Estado del caso.
- Historial de acciones.

---

## ¿Cuál es el objetivo general?

Construir un agente inteligente que reciba una solicitud ciudadana escrita en lenguaje natural y la convierta en un caso organizado, priorizado, asignado y trazable, con revisión humana obligatoria antes de la decisión final.

---

## ¿Cuáles son los objetivos específicos?

1. Recibir la descripción y ubicación de un problema ciudadano.
2. Extraer los datos relevantes del mensaje.
3. Clasificar el reporte en una categoría predefinida.
4. Proponer una prioridad basada en riesgo e impacto.
5. Determinar el área responsable.
6. Detectar información faltante.
7. Buscar posibles reportes duplicados.
8. Crear un expediente preliminar.
9. Guardar el expediente en Supabase.
10. Permitir que un operador apruebe, modifique o rechace el caso.
11. Registrar todas las decisiones del agente y del operador.
12. Mostrar los casos en un panel.
13. Demostrar reducción del trabajo repetitivo.

---

## ¿A quién está dirigido?

### Ciudadanos

Personas que desean reportar problemas relacionados con servicios públicos, infraestructura o espacios comunitarios.

El prototipo debe permitirles escribir el problema de forma sencilla y proporcionar una ubicación o referencia.

### Operadores o funcionarios

Personas responsables de revisar y organizar solicitudes ciudadanas.

El sistema debe permitirles:

- Revisar la información extraída.
- Revisar la categoría propuesta.
- Revisar la prioridad propuesta.
- Cambiar el área responsable.
- Solicitar información adicional.
- Aprobar el caso.
- Modificar y aprobar el caso.
- Rechazar el caso.
- Marcar un posible duplicado.
- Consultar el historial de decisiones.

---

## ¿Quiénes se benefician?

- Ciudadanos.
- Instituciones municipales.
- Departamentos de servicios públicos.
- Equipos de atención ciudadana.
- Barrios y comunidades.
- Autoridades que necesiten analizar problemas recurrentes.

---

## ¿Dónde se aplicaría?

La narrativa inicial estará centrada en Portoviejo.

El diseño debe permitir posteriormente:

- Agregar nuevas ciudades.
- Agregar nuevas categorías.
- Cambiar áreas responsables.
- Incorporar instituciones adicionales.
- Añadir autenticación y roles.

El prototipo no representa una plataforma oficial del Municipio de Portoviejo y no debe afirmar que los reportes son enviados a una institución real.

---

## ¿Por qué es importante?

Porque automatiza tareas repetitivas como:

- Leer mensajes.
- Interpretar información.
- Clasificar solicitudes.
- Revisar si están completas.
- Asignarlas a un área.
- Registrar decisiones.

Esto puede reducir el tiempo de procesamiento inicial y mejorar la consistencia de la atención.

---

## ¿Qué hace diferente a PortoReporta?

PortoReporta no es únicamente un chatbot.

Un chatbot responde preguntas.

PortoReporta ejecuta un flujo completo:

```text
Reporte ciudadano
        ↓
Extracción de datos
        ↓
Validación
        ↓
Clasificación
        ↓
Evaluación de prioridad
        ↓
Asignación del área responsable
        ↓
Búsqueda de duplicados
        ↓
Creación del expediente
        ↓
Revisión humana
        ↓
Persistencia y auditoría en Supabase
```

---

## ¿Qué papel cumple la inteligencia artificial?

La inteligencia artificial debe:

- Interpretar lenguaje natural.
- Extraer datos relevantes.
- Resumir el problema.
- Proponer una categoría.
- Proponer una prioridad.
- Explicar la decisión.
- Detectar información faltante.
- Coordinar herramientas internas.

La IA no debe aprobar ni rechazar definitivamente un caso.

---

## ¿Qué papel cumple la persona?

La persona conserva la autoridad final.

El operador puede:

- Aprobar.
- Modificar.
- Rechazar.
- Solicitar información.
- Marcar como posible duplicado.

Toda acción humana debe almacenarse en el historial de auditoría.

---

## ¿Qué impacto se espera?

### Impacto operativo

- Menor tiempo de clasificación.
- Menos trabajo repetitivo.
- Mayor consistencia.
- Mejor organización.
- Historial verificable.

### Impacto social

- Mejor recepción de reportes.
- Mayor claridad en la atención.
- Mejor identificación de problemas urgentes.
- Mayor transparencia en las decisiones.

### Relación con los ODS

#### ODS 8

El sistema reduce tareas manuales repetitivas y ayuda a elevar la productividad de los equipos de atención.

#### ODS 9

El proyecto aplica innovación tecnológica y automatización a la gestión de servicios e infraestructura.

---

## ¿Cómo se medirá el resultado?

Durante la demostración se podrán mostrar:

- Número de reportes procesados.
- Reportes por categoría.
- Casos de prioridad alta.
- Casos pendientes.
- Casos aprobados.
- Casos modificados por humanos.
- Posibles duplicados.
- Historial de decisiones.

No deben inventarse porcentajes de mejora sin una medición real.

---

# 4. Alcance del MVP

El proyecto debe construirse en aproximadamente cuatro horas.

## Funciones obligatorias

1. Formulario para ingresar una solicitud.
2. Campo de descripción.
3. Campo de ubicación.
4. Botón para analizar el reporte.
5. Categoría sugerida.
6. Prioridad sugerida.
7. Área responsable sugerida.
8. Justificación.
9. Información faltante.
10. Búsqueda sencilla de duplicados.
11. Creación de expediente preliminar.
12. Persistencia en Supabase.
13. Panel de revisión humana.
14. Aprobación, modificación o rechazo.
15. Historial de auditoría.
16. Tabla de solicitudes registradas.

---

## Funciones opcionales

Implementar solamente si sobra tiempo:

- Filtros.
- Métricas simples.
- Exportación a CSV.
- Vista detallada.
- Mejoras visuales.
- Carga de imágenes mediante Supabase Storage.
- Autenticación básica con Supabase Auth.

---

## Funciones fuera del alcance

No implementar durante el MVP:

- Aplicación móvil.
- Integración con sistemas municipales.
- Mapas reales.
- WhatsApp.
- Correos.
- Geolocalización.
- Reconocimiento de imágenes.
- Microservicios.
- Despliegue complejo.
- Modelo de aprendizaje automático propio.
- Sistema completo de cuadrillas.
- Seguimiento operativo hasta la resolución física.
- Roles complejos.
- Dashboard estadístico avanzado.

---

# 5. Flujo principal

```text
Ciudadano ingresa descripción y ubicación
                    ↓
El agente analiza el mensaje
                    ↓
Extrae y valida información
                    ↓
Propone categoría, prioridad y área
                    ↓
Busca posibles duplicados en Supabase
                    ↓
Crea un expediente preliminar
                    ↓
Guarda el caso en Supabase
                    ↓
El operador revisa
                    ↓
Aprueba, modifica o rechaza
                    ↓
Se registra la decisión en auditoría
```

---

# 6. Categorías iniciales

| Código | Categoría | Área responsable |
|---|---|---|
| `AGUA` | Fuga o falta de agua | Agua potable |
| `BASURA` | Basura acumulada o recolección | Gestión ambiental |
| `ALUMBRADO` | Luminaria dañada | Alumbrado público |
| `VIALIDAD` | Huecos, calles o señalización | Obras públicas |
| `ALCANTARILLADO` | Alcantarillas y drenajes | Alcantarillado |
| `ESPACIO_PUBLICO` | Parques y espacios comunitarios | Espacios públicos |
| `OTRO` | Caso no reconocido | Atención ciudadana |

Las categorías deben mantenerse en una configuración central para evitar que estén repetidas en varios archivos.

---

# 7. Niveles de prioridad

## Alta

Cuando existe riesgo inmediato o afectación grave de un servicio esencial.

Ejemplos:

- Alcantarilla abierta.
- Poste caído.
- Cables expuestos.
- Riesgo de accidente.
- Cercanía a una escuela u hospital.
- Inundación.
- Fuga grande.
- Vía completamente bloqueada.
- Falta total de agua en un sector.

## Media

Cuando existe una afectación relevante sin peligro inmediato.

Ejemplos:

- Basura acumulada.
- Luminaria dañada.
- Hueco que dificulta el tránsito.
- Fuga pequeña.
- Parque deteriorado.

## Baja

Cuando el problema corresponde principalmente a mantenimiento.

Ejemplos:

- Césped alto.
- Pintura deteriorada.
- Daño estético.
- Solicitud general de mantenimiento.

La prioridad de la IA es siempre una recomendación.

---

# 8. Estados del caso

| Estado | Significado |
|---|---|
| `PENDIENTE_REVISION` | Falta revisión humana |
| `REQUIERE_INFORMACION` | Faltan datos importantes |
| `APROBADA` | El operador aprobó |
| `MODIFICADA_Y_APROBADA` | El operador modificó y aprobó |
| `RECHAZADA` | El operador rechazó |
| `POSIBLE_DUPLICADO` | Debe revisarse la similitud |

---

# 9. Información mínima requerida

Para crear un expediente preliminar se requiere:

- Descripción.
- Ubicación o referencia.

El agente también debe intentar obtener:

- Tipo de incidente.
- Tiempo aproximado.
- Riesgo mencionado.
- Personas o lugares afectados.
- Referencias adicionales.

Cuando falten datos, el agente no debe inventarlos.

Ejemplo:

```text
Información faltante:
- Ubicación más precisa.
- Referencia del lugar.
- Tiempo aproximado desde que comenzó el problema.
```

---

# 10. Diseño del agente

## Enfoque recomendado

Utilizar un agente coordinador con herramientas internas.

No es necesario construir varios agentes independientes durante el MVP.

## Responsabilidades del agente

1. Interpretar el mensaje.
2. Extraer datos.
3. Clasificar el problema.
4. Evaluar prioridad.
5. Asignar área responsable.
6. Detectar información faltante.
7. Consultar posibles duplicados.
8. Preparar el expediente.
9. Solicitar persistencia.
10. Devolver un resultado estructurado.

---

## Herramientas internas

### `obtener_area_responsable(categoria)`

Devuelve el área responsable según la categoría.

### `evaluar_prioridad(descripcion, ubicacion, categoria)`

Evalúa señales de riesgo y devuelve:

- Prioridad.
- Señales detectadas.
- Justificación.

### `buscar_posibles_duplicados(descripcion, ubicacion, categoria)`

Consulta casos existentes en Supabase y compara:

- Categoría.
- Ubicación.
- Palabras principales.
- Similitud textual.

Para el MVP se puede utilizar `difflib.SequenceMatcher`.

### `crear_borrador_solicitud(datos)`

Inserta una solicitud en Supabase.

### `actualizar_solicitud(id, cambios)`

Actualiza los datos revisados por el operador.

### `registrar_evento_auditoria(solicitud_id, actor, accion, detalle)`

Inserta un evento en la tabla de auditoría.

---

## Salida estructurada esperada

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
  "justificacion": "Se propone prioridad alta porque existe riesgo para peatones.",
  "posibles_duplicados": []
}
```

La salida debe validarse antes de guardarse.

---

# 11. Supervisión humana

La supervisión humana es obligatoria.

El agente nunca debe:

- Aprobar definitivamente.
- Rechazar definitivamente.
- Enviar el caso a una institución real.
- Inventar ubicación.
- Inventar datos.
- Declarar que el problema fue resuelto.
- Cambiar silenciosamente una decisión.

El operador debe poder:

- Aprobar.
- Modificar categoría.
- Modificar prioridad.
- Modificar área.
- Añadir un motivo.
- Rechazar.
- Marcar duplicado.

Cuando el operador modifica una recomendación, debe escribir un motivo.

---

# 12. Trazabilidad

Cada caso debe permitir reconstruir lo ocurrido.

El historial debe registrar:

- Momento de creación.
- Datos recibidos.
- Categoría propuesta.
- Prioridad propuesta.
- Justificación.
- Duplicados sugeridos.
- Acción del operador.
- Datos modificados.
- Motivo del cambio.
- Fecha y hora.

Ejemplo:

```text
10:02 — CIUDADANO — Envió un reporte.
10:02 — AGENTE — Clasificó el caso como ALCANTARILLADO.
10:02 — AGENTE — Propuso prioridad ALTA.
10:02 — AGENTE — Detectó riesgo de accidente.
10:05 — OPERADOR — Modificó el área responsable.
10:05 — OPERADOR — Aprobó el caso.
```

---

# 13. Herramientas y tecnologías

## Lenguaje

**Python 3.11 o superior**

Se utilizará un solo lenguaje para reducir configuración y tiempo de integración.

---

## Interfaz

**Streamlit**

Se utilizará para:

- Formulario ciudadano.
- Resultado del análisis.
- Panel de revisión.
- Tabla de solicitudes.
- Historial.
- Métricas simples.

No utilizar React ni un frontend separado en el MVP.

---

## Agente de inteligencia artificial

**OpenAI Agents SDK para Python**

Se utilizará para:

- Crear el agente coordinador.
- Definir herramientas.
- Ejecutar el agente.
- Obtener salida estructurada.
- Coordinar acciones.
- Mantener trazabilidad de las ejecuciones.

Variable requerida:

```text
OPENAI_API_KEY
```

---

## Validación de datos

**Pydantic**

Se utilizará para:

- Validar la salida del agente.
- Restringir categorías.
- Restringir prioridades.
- Evitar estructuras incompletas.
- Validar datos antes de enviarlos a Supabase.

---

## Variables de entorno

**python-dotenv**

Se utilizará para cargar las credenciales desde `.env`.

---

## Pruebas

**pytest**

Se utilizará para probar:

- Reglas de prioridad.
- Asignación de áreas.
- Validación de modelos.
- Creación de solicitudes.
- Registro de auditoría.
- Modo de respaldo sin IA.

---

# 14. Sistema de gestión de base de datos

## Tecnología elegida

**Supabase**

Supabase proporcionará una base de datos PostgreSQL administrada y una API para consultar e insertar datos desde Python.

No se utilizará MySQL ni SQLite.

---

## Cliente de Python

**supabase-py**

Paquete:

```text
supabase
```

Inicialización conceptual:

```python
import os
from supabase import Client, create_client

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_SECRET_KEY"]

supabase: Client = create_client(url, key)
```

La creación del cliente debe centralizarse en un solo archivo.

---

## Credenciales

Variables recomendadas:

```text
SUPABASE_URL=
SUPABASE_SECRET_KEY=
OPENAI_API_KEY=
APP_ENV=development
```

Dependiendo del proyecto de Supabase, la clave privada del servidor también podría aparecer como una clave heredada `service_role`.

Reglas:

- La clave secreta solo se usa en el servidor.
- Nunca debe exponerse en el navegador.
- Nunca debe escribirse dentro del código.
- Nunca debe subirse a Git.
- Nunca debe mostrarse en registros.
- El repositorio debe incluir únicamente `.env.example`.

---

## ¿Por qué Supabase?

- Utiliza PostgreSQL.
- No requiere instalar un servidor local.
- Permite inspeccionar tablas desde el panel.
- Ofrece persistencia remota.
- Facilita consultas desde Python.
- Permite agregar autenticación posteriormente.
- Permite agregar Storage posteriormente.
- Soporta políticas de seguridad a nivel de fila.
- Permite que varios integrantes consulten el mismo proyecto.

---

## Uso durante el MVP

La aplicación Streamlit se conectará a Supabase desde el servidor.

El navegador no debe conectarse directamente con una clave secreta.

Flujo:

```text
Navegador
    ↓
Aplicación Streamlit
    ↓
Cliente supabase-py
    ↓
Supabase
    ↓
PostgreSQL
```

---

# 15. Seguridad de Supabase

## Row Level Security

Las tablas del esquema `public` deben tener Row Level Security activado.

Para este MVP:

- No se permitirá acceso directo anónimo a las tablas.
- La aplicación Streamlit utilizará una clave secreta exclusivamente en el servidor.
- No se crearán políticas públicas de lectura o escritura.
- La autenticación de usuarios queda fuera del alcance inicial.

La clave secreta puede tener privilegios elevados y debe tratarse como una contraseña crítica.

---

## Reglas adicionales

- No almacenar datos personales innecesarios.
- No guardar cédulas.
- No guardar teléfonos.
- No guardar direcciones personales exactas.
- No registrar claves en auditoría.
- No mostrar excepciones completas al usuario.
- Validar todos los datos antes de insertarlos.
- Limitar los campos permitidos en las actualizaciones.
- No aceptar nombres de tabla enviados por el usuario.

---

# 16. Modelo de datos en Supabase

Supabase utilizará PostgreSQL.

## Tabla `solicitudes`

```sql
create table if not exists public.solicitudes (
    id bigint generated always as identity primary key,
    descripcion_original text not null,
    resumen text,
    ubicacion text not null,
    categoria text not null
        check (
            categoria in (
                'AGUA',
                'BASURA',
                'ALUMBRADO',
                'VIALIDAD',
                'ALCANTARILLADO',
                'ESPACIO_PUBLICO',
                'OTRO'
            )
        ),
    prioridad_agente text not null
        check (prioridad_agente in ('BAJA', 'MEDIA', 'ALTA')),
    prioridad_final text
        check (
            prioridad_final is null
            or prioridad_final in ('BAJA', 'MEDIA', 'ALTA')
        ),
    area_agente text not null,
    area_final text,
    justificacion_agente text not null,
    informacion_faltante jsonb not null default '[]'::jsonb,
    senales_riesgo jsonb not null default '[]'::jsonb,
    origen_analisis text not null default 'REGLAS'
        check (origen_analisis in ('IA', 'REGLAS')),
    estado text not null default 'PENDIENTE_REVISION'
        check (
            estado in (
                'PENDIENTE_REVISION',
                'REQUIERE_INFORMACION',
                'APROBADA',
                'MODIFICADA_Y_APROBADA',
                'RECHAZADA',
                'POSIBLE_DUPLICADO'
            )
        ),
    posible_duplicado_de bigint,
    creado_en timestamptz not null default now(),
    revisado_en timestamptz,
    revisor text,
    motivo_revision text,
    constraint solicitudes_posible_duplicado_fk
        foreign key (posible_duplicado_de)
        references public.solicitudes(id)
        on delete set null
);
```

---

## Tabla `auditoria`

```sql
create table if not exists public.auditoria (
    id bigint generated always as identity primary key,
    solicitud_id bigint not null,
    actor text not null
        check (actor in ('CIUDADANO', 'AGENTE', 'OPERADOR', 'SISTEMA')),
    accion text not null,
    detalle jsonb not null default '{}'::jsonb,
    creado_en timestamptz not null default now(),
    constraint auditoria_solicitud_fk
        foreign key (solicitud_id)
        references public.solicitudes(id)
        on delete cascade
);
```

---

## Índices recomendados

```sql
create index if not exists idx_solicitudes_estado
    on public.solicitudes (estado);

create index if not exists idx_solicitudes_categoria
    on public.solicitudes (categoria);

create index if not exists idx_solicitudes_prioridad
    on public.solicitudes (prioridad_agente);

create index if not exists idx_solicitudes_creado_en
    on public.solicitudes (creado_en desc);

create index if not exists idx_auditoria_solicitud_id
    on public.auditoria (solicitud_id);

create index if not exists idx_auditoria_creado_en
    on public.auditoria (creado_en);
```

---

## Activación de RLS

```sql
alter table public.solicitudes enable row level security;
alter table public.auditoria enable row level security;
```

Durante el MVP no se crearán políticas para usuarios anónimos.

La aplicación accederá desde el servidor mediante la clave secreta.

---

# 17. Operaciones de persistencia

Todas las operaciones deben centralizarse en un repositorio.

Funciones recomendadas:

```text
crear_solicitud(datos)
obtener_solicitudes()
obtener_solicitud_por_id(id)
actualizar_solicitud(id, cambios)
registrar_auditoria(datos)
obtener_auditoria_por_solicitud(id)
buscar_candidatos_duplicados(categoria, ubicacion)
```

No realizar consultas de Supabase directamente desde todas las pantallas.

---

## Ejemplo conceptual de inserción

```python
response = (
    supabase
    .table("solicitudes")
    .insert(datos)
    .execute()
)
```

---

## Ejemplo conceptual de consulta

```python
response = (
    supabase
    .table("solicitudes")
    .select("*")
    .order("creado_en", desc=True)
    .execute()
)
```

---

## Ejemplo conceptual de actualización

```python
response = (
    supabase
    .table("solicitudes")
    .update(cambios)
    .eq("id", solicitud_id)
    .execute()
)
```

---

# 18. Consistencia entre solicitud y auditoría

Cuando se cree o modifique una solicitud:

1. Ejecutar la operación principal.
2. Verificar que Supabase devolvió un registro.
3. Crear inmediatamente el evento de auditoría.
4. Si la auditoría falla, mostrar el error y no afirmar que la operación quedó completamente registrada.

Para una versión futura se puede utilizar una función PostgreSQL llamada mediante RPC para ejecutar solicitud y auditoría dentro de una sola transacción.

No es obligatorio construir esta función durante las cuatro horas si el flujo principal todavía no está terminado.

---

# 19. Arquitectura

```text
┌──────────────────────────────┐
│ Interfaz Streamlit           │
│ app.py                       │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│ Agente coordinador           │
│ src/agent.py                 │
└───────┬───────────┬──────────┘
        │           │
┌───────▼──────┐ ┌──▼────────────────┐
│ Reglas       │ │ Herramientas       │
│ src/rules.py │ │ src/tools.py       │
└───────┬──────┘ └─────────┬─────────┘
        │                  │
        └─────────┬────────┘
                  │
        ┌─────────▼──────────┐
        │ Repositorios       │
        │ src/repositories.py│
        └─────────┬──────────┘
                  │
        ┌─────────▼──────────┐
        │ Cliente Supabase   │
        │ src/supabase_client.py
        └─────────┬──────────┘
                  │
        ┌─────────▼──────────┐
        │ Supabase/PostgreSQL│
        └────────────────────┘
```

Principio:

> La IA interpreta y recomienda, las reglas validan, Supabase persiste y la persona decide.

---

# 20. Estructura del repositorio

```text
porto-reporta/
├── AGENTS.md
├── README.md
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── docs/
│   └── contexto-proyecto.md
│
├── src/
│   ├── __init__.py
│   ├── agent.py
│   ├── models.py
│   ├── rules.py
│   ├── tools.py
│   ├── supabase_client.py
│   └── repositories.py
│
├── supabase/
│   ├── schema.sql
│   └── seed.sql
│
└── tests/
    ├── test_rules.py
    └── test_models.py
```

---

## Responsabilidad de cada archivo

### `AGENTS.md`

Reglas generales para Codex:

- No ampliar el alcance.
- No exponer claves.
- Mantener supervisión humana.
- Ejecutar pruebas.
- Priorizar estabilidad.

### `docs/contexto-proyecto.md`

Este documento.

### `app.py`

Interfaz Streamlit y navegación.

### `src/agent.py`

Configuración y ejecución del agente.

### `src/models.py`

Modelos Pydantic.

### `src/rules.py`

Categorías, áreas y reglas de prioridad.

### `src/tools.py`

Herramientas que utiliza el agente.

### `src/supabase_client.py`

Creación centralizada del cliente Supabase.

### `src/repositories.py`

Consultas e inserciones.

### `supabase/schema.sql`

Creación de tablas, índices y RLS.

### `supabase/seed.sql`

Casos de demostración opcionales.

---

# 21. Dependencias

Contenido recomendado de `requirements.txt`:

```text
streamlit
openai-agents
pydantic
python-dotenv
pytest
supabase
```

No instalar conectores de MySQL ni usar `sqlite3`.

---

# 22. Variables de entorno

Contenido de `.env.example`:

```text
OPENAI_API_KEY=coloque_aqui_su_clave
SUPABASE_URL=https://su-proyecto.supabase.co
SUPABASE_SECRET_KEY=coloque_aqui_su_clave_secreta
APP_ENV=development
```

Contenido de `.gitignore`:

```text
.venv/
__pycache__/
.pytest_cache/
.env
*.pyc
.streamlit/secrets.toml
```

---

# 23. Pantallas del MVP

## Pantalla 1: Nuevo reporte

Campos:

- Descripción.
- Ubicación.
- Botón `Analizar reporte`.

## Pantalla 2: Resultado del agente

Mostrar:

- Resumen.
- Categoría.
- Prioridad.
- Área.
- Justificación.
- Señales de riesgo.
- Información faltante.
- Posibles duplicados.
- Botón `Crear expediente`.

## Pantalla 3: Revisión humana

Permitir:

- Cambiar categoría.
- Cambiar prioridad.
- Cambiar área.
- Añadir motivo.
- Aprobar.
- Rechazar.
- Marcar duplicado.

## Pantalla 4: Solicitudes

Mostrar:

- ID.
- Resumen.
- Categoría.
- Prioridad.
- Estado.
- Fecha.

## Pantalla 5: Historial

Seleccionar una solicitud y mostrar todas sus acciones.

---

# 24. Casos de demostración

## Caso 1: Prioridad alta

**Descripción:**

```text
Hay una alcantarilla sin tapa frente a la escuela del barrio San José. Desde ayer casi ocurre un accidente.
```

**Ubicación:**

```text
Barrio San José, frente a la escuela
```

Resultado esperado:

- Categoría: `ALCANTARILLADO`.
- Prioridad: `ALTA`.
- Área: Alcantarillado.
- Señales: escuela, alcantarilla abierta, riesgo de accidente.

---

## Caso 2: Información insuficiente

**Descripción:**

```text
Hay un hueco peligroso.
```

**Ubicación:**

```text
Sin especificar
```

Resultado esperado:

- Categoría: `VIALIDAD`.
- Estado sugerido: `REQUIERE_INFORMACION`.
- Solicitar ubicación más precisa.

---

## Caso 3: Prioridad media

**Descripción:**

```text
La luminaria del parque no funciona desde hace cuatro noches.
```

**Ubicación:**

```text
Parque del barrio Los Tamarindos
```

Resultado esperado:

- Categoría: `ALUMBRADO`.
- Prioridad: `MEDIA`.
- Área: Alumbrado público.

---

## Caso 4: Posible duplicado

Registrar:

```text
Existe una fuga de agua frente al mercado central.
```

Después:

```text
Se está desperdiciando agua en la calle del mercado.
```

El segundo caso debe mostrar el primero como posible duplicado, no como duplicado confirmado.

---

# 25. Modos de respaldo

## Falla de la API de IA

1. Intentar usar el agente.
2. Si falla, mostrar una advertencia.
3. Ejecutar clasificación por reglas.
4. Continuar el flujo.
5. Registrar que se utilizó el modo local.

Este respaldo es obligatorio.

---

## Falla de Supabase

Si Supabase no responde:

1. Mostrar un error claro.
2. No afirmar que el caso fue guardado.
3. Conservar temporalmente el análisis en `st.session_state`.
4. Permitir volver a intentar.
5. No sustituir silenciosamente Supabase por otra base de datos.
6. Opcionalmente permitir una demostración sin persistencia, indicando claramente el modo.

Supabase debe seguir siendo la única base de datos oficial del proyecto.

---

# 26. Planificación de cuatro horas

## 00:00–00:25 — Preparación

- Crear repositorio.
- Crear estructura.
- Crear entorno virtual.
- Instalar dependencias.
- Crear proyecto de Supabase.
- Configurar `.env`.
- Ejecutar Streamlit.

**Resultado obligatorio:** Streamlit inicia y el cliente de Supabase se conecta.

---

## 00:25–01:05 — Supabase y reglas

- Crear `schema.sql`.
- Ejecutar el SQL en Supabase.
- Confirmar tablas.
- Activar RLS.
- Implementar cliente.
- Implementar repositorios.
- Definir categorías.
- Implementar reglas de prioridad.

**Resultado obligatorio:** crear y listar una solicitud desde Python.

---

## 01:05–01:55 — Agente

- Crear modelos Pydantic.
- Configurar agente.
- Definir herramientas.
- Obtener salida estructurada.
- Implementar modo de respaldo sin IA.
- Conectar búsqueda de duplicados.

**Resultado obligatorio:** transformar un mensaje en un análisis válido.

---

## 01:55–02:45 — Interfaz

- Crear formulario.
- Mostrar análisis.
- Crear expediente.
- Crear panel de revisión.
- Mostrar tabla de solicitudes.
- Conectar operaciones con Supabase.

**Resultado obligatorio:** flujo completo desde reporte hasta revisión.

---

## 02:45–03:15 — Auditoría y pruebas

- Registrar eventos.
- Mostrar historial.
- Probar cambios humanos.
- Probar campos vacíos.
- Probar sin API.
- Probar error de Supabase.
- Ejecutar pruebas.

---

## 03:15–03:40 — Presentación visual

- Mejorar títulos.
- Ordenar pantallas.
- Añadir métricas simples.
- Preparar datos de demostración.
- Revisar textos.

---

## 03:40–04:00 — Preparación final

- Ensayar la demostración.
- Revisar README.
- Confirmar que `.env` no está en Git.
- Crear commit estable.
- No agregar nuevas funciones.
- No modificar la arquitectura durante los últimos diez minutos.

---

# 27. Criterios de aceptación

El proyecto se considera terminado cuando:

1. La aplicación inicia con `streamlit run app.py`.
2. La conexión con Supabase funciona.
3. Las tablas existen.
4. RLS está activado.
5. Se puede enviar un reporte.
6. Se obtiene un análisis estructurado.
7. Se muestra una categoría válida.
8. Se muestra una prioridad válida.
9. Se muestra una justificación.
10. Se indica información faltante.
11. Se buscan posibles duplicados.
12. El caso se guarda en Supabase.
13. El caso queda pendiente de revisión.
14. Un operador puede aprobar, modificar o rechazar.
15. Cada acción relevante queda en auditoría.
16. La aplicación funciona sin la API de IA mediante reglas.
17. La aplicación informa correctamente si Supabase falla.
18. Las solicitudes se muestran en una tabla.
19. Las pruebas principales pasan.
20. Ninguna clave está dentro del repositorio.

Cuando estos criterios se cumplan, no ampliar el alcance.

---

# 28. Métricas para la presentación

La interfaz puede mostrar:

- Total de solicitudes.
- Pendientes.
- Aprobadas.
- Rechazadas.
- Prioridad alta.
- Posibles duplicados.
- Solicitudes por categoría.

No crear gráficos complejos si el flujo principal todavía tiene errores.

---

# 29. Seguridad y privacidad

- No guardar cédulas.
- No guardar teléfonos.
- No guardar datos sensibles.
- No exponer claves.
- No subir `.env`.
- Utilizar RLS.
- Mantener la clave secreta solamente en el servidor.
- Validar categorías y estados.
- Registrar cambios.
- No permitir aprobación automática.
- No afirmar que los reportes llegan al municipio.
- No inventar datos.
- Mostrar claramente que es un prototipo.

---

# 30. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Falla OpenAI | Modo local basado en reglas |
| Falla Supabase | Reintento y modo temporal sin persistencia |
| Credenciales expuestas | `.env`, `.gitignore` y revisión final |
| Arquitectura excesiva | Mantener un solo agente y una sola aplicación |
| Proyecto parece chatbot | Mostrar herramientas, persistencia y auditoría |
| Prioridad arbitraria | Mostrar reglas y señales |
| Duplicado incorrecto | Presentarlo como sugerencia |
| Falta de tiempo | Terminar flujo antes de mejorar diseño |
| Codex agrega tecnologías | Restringirse a este documento |

---

# 31. Guion breve para el jurado

“PortoReporta recibe una solicitud ciudadana escrita en lenguaje natural y la transforma en un expediente estructurado. El agente identifica la categoría, propone una prioridad, asigna el área responsable, detecta información faltante y busca posibles duplicados. Después, una persona revisa la recomendación y decide si la aprueba, modifica o rechaza. Todos los casos y decisiones se almacenan en Supabase, lo que reduce trabajo repetitivo y mantiene una trazabilidad completa.”

---

# 32. Directrices para Codex

Codex debe:

1. Leer este documento completo.
2. No utilizar MySQL.
3. No utilizar SQLite.
4. Utilizar Supabase como única base de datos.
5. Crear el cliente de Supabase en un solo archivo.
6. Centralizar las consultas en repositorios.
7. No exponer claves.
8. No ampliar el alcance sin autorización.
9. Construir primero el flujo mínimo.
10. Mantener el modo de respaldo sin IA.
11. No permitir aprobación automática.
12. Registrar cada decisión.
13. Ejecutar pruebas después de cambios importantes.
14. No crear microservicios.
15. No separar frontend y backend.
16. No implementar autenticación hasta terminar el MVP.
17. Cuando se cumplan los criterios de aceptación, detener nuevas funciones.

---

# 33. Primera instrucción para Codex

```text
Lee docs/contexto-proyecto.md completo. Crea únicamente la estructura mínima definida en el documento. Configura Streamlit y Supabase usando variables de entorno. Implementa el cliente centralizado, los repositorios, el esquema SQL de solicitudes y auditoría, RLS, las categorías y las reglas de prioridad. No uses MySQL ni SQLite. Antes de integrar IA, demuestra que puedes crear, consultar y actualizar solicitudes en Supabase. Ejecuta pruebas y explica cómo iniciar la aplicación.
```

---

# 34. Segunda instrucción para Codex

```text
Lee nuevamente docs/contexto-proyecto.md. Integra el agente coordinador con OpenAI Agents SDK, salida estructurada mediante Pydantic y las herramientas definidas. Conecta el agente con los repositorios de Supabase. Mantén el modo local de respaldo cuando la API de IA falle. El agente no puede aprobar solicitudes. Implementa revisión humana, auditoría y búsqueda de posibles duplicados. Prueba los cuatro casos de demostración y corrige los errores encontrados.
```

---

# 35. Definición final del producto

PortoReporta será considerado un prototipo exitoso cuando pueda recibir un reporte ciudadano, convertirlo en un expediente estructurado, proponer una categoría y prioridad explicables, buscar posibles duplicados, guardar el caso en Supabase, someterlo a revisión humana y conservar el historial completo de decisiones.
