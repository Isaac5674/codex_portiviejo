---
name: agente-trazable-supervisado
description: Diseña y modifica el agente de PortoReporta con salidas estructuradas, reglas deterministas, herramientas reutilizables, supervisión humana, fallback y auditoría.
---

# Agente trazable y supervisado

## Propósito

Usa esta skill al crear o modificar:

- el agente coordinador;
- sus instrucciones;
- sus herramientas;
- modelos de salida;
- reglas de prioridad;
- detección de información faltante;
- detección de duplicados;
- modo de respaldo;
- revisión humana;
- auditoría del flujo.

Su objetivo es impedir que la IA se convierta en una caja negra que invente datos o tome decisiones definitivas.

## Fuente de verdad

Lee:

1. `docs/contexto-proyecto.md`.
2. `src/agent.py`.
3. `src/models.py`.
4. `src/rules.py`.
5. `src/tools.py`.
6. `src/repositories.py`.
7. pruebas del agente y reglas.

## Principio central

> La IA interpreta y propone. Las reglas validan. Supabase persiste. La persona decide.

## Responsabilidades

### El agente puede

- interpretar descripción y ubicación;
- resumir;
- proponer categoría;
- proponer prioridad;
- identificar señales;
- detectar información faltante;
- invocar herramientas;
- preparar un borrador;
- explicar su recomendación.

### El agente no puede

- aprobar;
- rechazar definitivamente;
- declarar resolución;
- inventar ubicación;
- inventar tiempo o afectados;
- enviar una solicitud a una institución real;
- omitir auditoría;
- escribir directamente en tablas sin herramienta controlada;
- sustituir una validación crítica con una instrucción de prompt.

## Diseño recomendado

Usa un agente coordinador.

No crees múltiples agentes salvo que:

- existan responsabilidades realmente independientes;
- el beneficio sea mayor que la complejidad;
- el MVP ya funcione;
- exista una prueba clara de coordinación.

Para el MVP, funciones y herramientas especializadas son suficientes.

## Contrato de entrada

Debe incluir como mínimo:

```python
class ReporteEntrada(BaseModel):
    descripcion: str
    ubicacion: str
```

Validaciones recomendadas:

- texto no vacío;
- longitud máxima razonable;
- quitar espacios externos;
- no aceptar ubicaciones inventadas por el sistema.

## Contrato de salida

La salida del agente debe ser un modelo Pydantic, no texto libre.

Debe contener:

- resumen;
- categoría;
- prioridad;
- área responsable;
- ubicación;
- información faltante;
- señales de riesgo;
- justificación;
- posibles duplicados.

Ejemplo conceptual:

```python
class AnalisisReporte(BaseModel):
    resumen: str
    categoria: Categoria
    prioridad: Prioridad
    area_responsable: str
    ubicacion: str
    informacion_faltante: list[str]
    senales_riesgo: list[str]
    justificacion: str
    posibles_duplicados: list[DuplicadoCandidato]
```

No confíes en que el modelo obedecerá el formato sin validación.

## Separación entre IA y reglas

### IA

Adecuada para:

- comprensión semántica;
- resumen;
- identificación contextual;
- propuesta explicada.

### Reglas deterministas

Obligatorias para:

- valores permitidos;
- categoría-área;
- señales críticas;
- estados;
- transiciones;
- necesidad de revisión;
- campos obligatorios;
- fallback;
- límites de seguridad.

Una prioridad alta no debe depender exclusivamente de una frase generada por el modelo.

## Procedimiento de análisis

### 1. Validar entrada

Antes de llamar a la IA:

- valida descripción;
- valida ubicación;
- normaliza espacios;
- detecta valores como “sin especificar”;
- no envíes datos personales innecesarios.

### 2. Ejecutar el agente

La instrucción debe pedir:

- no inventar;
- conservar la descripción;
- usar valores permitidos;
- explicar señales;
- devolver estructura;
- señalar incertidumbre;
- no tomar decisión final.

### 3. Validar salida

Después de la llamada:

- valida con Pydantic;
- confirma categoría;
- recalcula área desde configuración;
- comprueba señales críticas con reglas;
- normaliza prioridad si contradice una regla obligatoria;
- conserva evidencia de la corrección;
- no guarde una salida inválida.

### 4. Buscar duplicados

Usa una herramienta que consulte candidatos en Supabase.

El agente no debe recibir toda la base.

Devuelve:

- id;
- resumen;
- ubicación;
- categoría;
- puntuación aproximada.

La salida debe decir “posible duplicado”, nunca “duplicado confirmado”.

### 5. Preparar borrador

El borrador debe conservar:

- recomendación original;
- explicación;
- señales;
- información faltante;
- estado de revisión.

### 6. Persistir mediante herramienta

El agente no consulta Supabase de manera arbitraria.

Usa una herramienta que delega al repositorio.

### 7. Registrar auditoría

Registra separadamente:

- recepción;
- análisis;
- prioridad propuesta;
- correcciones deterministas;
- duplicados sugeridos;
- creación de borrador;
- acción humana.

## Herramientas

Cada herramienta debe:

- tener una función específica;
- usar argumentos tipados;
- validar;
- devolver estructura serializable;
- limitar datos;
- manejar errores;
- evitar efectos secundarios ocultos;
- poder probarse sin ejecutar el agente.

### `obtener_area_responsable`

Debe ser determinista.

### `evaluar_prioridad`

Debe devolver:

```json
{
  "prioridad": "ALTA",
  "senales": [],
  "justificacion": ""
}
```

### `buscar_posibles_duplicados`

Debe devolver candidatos acotados.

### `crear_borrador_solicitud`

Debe validar y persistir mediante repositorio.

### `registrar_evento_auditoria`

Debe rechazar secretos y datos no serializables.

## Principio abierto-cerrado aplicado al agente

### Agregar una categoría

Debe extender:

- registro central;
- modelo;
- SQL;
- pruebas.

No debe requerir reescribir el agente.

### Agregar una señal de riesgo

Debe extender una colección de reglas:

```python
RISK_RULES = (
    RiskRule(...),
    RiskRule(...),
)
```

o una estructura equivalente.

No agregues condicionales dispersos en el prompt, la interfaz y el repositorio.

### Agregar una herramienta

Debe:

1. implementar la capacidad fuera del agente;
2. probarla;
3. crear un adaptador de herramienta;
4. registrarla;
5. añadir instrucciones mínimas de uso;
6. verificar que no amplía autoridad.

### Cambiar un modelo

Prefiere campos opcionales compatibles.

Si un campo es nuevo y obligatorio:

- define predeterminado o migración;
- actualiza fallback;
- actualiza persistencia;
- actualiza pruebas;
- prueba filas o respuestas anteriores.

## Fallback sin IA

El modo de respaldo es obligatorio.

Debe activar cuando:

- falta la clave;
- ocurre timeout;
- la API falla;
- la salida no valida;
- se supera un límite acordado.

El fallback debe:

- clasificar por reglas;
- asignar área;
- evaluar prioridad;
- detectar faltantes;
- buscar duplicados si Supabase funciona;
- marcar que el origen fue `FALLBACK_REGLAS`;
- permitir revisión humana;
- registrar la causa de forma segura.

No debe fingir que utilizó IA.

## Supervisión humana

Todo borrador debe iniciar en:

- `PENDIENTE_REVISION`, o
- `REQUIERE_INFORMACION`, o
- `POSIBLE_DUPLICADO`.

Solo el operador puede producir:

- `APROBADA`;
- `MODIFICADA_Y_APROBADA`;
- `RECHAZADA`.

Cuando modifica:

- categoría;
- prioridad;
- área;

debe indicar motivo.

La interfaz debe mostrar lado a lado o de forma identificable:

- propuesta del agente;
- decisión final.

No sobrescribas la propuesta original.

## Trazabilidad

Cada decisión debe responder:

- qué dato se usó;
- qué regla se activó;
- qué propuso el agente;
- qué corrigió el sistema;
- qué decidió el humano;
- cuándo ocurrió.

No registres razonamiento privado extenso. Registra evidencia y justificación operativa:

```json
{
  "categoria_propuesta": "ALCANTARILLADO",
  "prioridad_propuesta": "ALTA",
  "senales": ["alcantarilla abierta", "escuela"],
  "justificacion": "Riesgo de accidente en zona escolar"
}
```

## Manejo de incertidumbre

Cuando no existe evidencia suficiente:

- usa `OTRO`;
- agrega información faltante;
- evita prioridad alta salvo señal verificable;
- permite revisión;
- no complete datos con suposiciones.

## Pruebas mínimas

### Contratos

- salida válida;
- categoría inválida;
- lista vacía;
- ubicación faltante;
- serialización.

### Reglas

- caso de alcantarilla frente a escuela;
- luminaria dañada;
- hueco sin ubicación;
- categoría desconocida;
- señales contradictorias.

### Fallback

- API indisponible;
- salida inválida;
- clasificación local;
- auditoría del fallback.

### Autoridad

- el agente no puede aprobar;
- el agente no puede rechazar;
- una modificación humana requiere motivo;
- la recomendación original se conserva.

### Herramientas

- argumentos inválidos;
- respuesta vacía;
- error de repositorio;
- resultado serializable.

## Formato de salida obligatorio

```markdown
## Cambio del agente

## Contratos afectados

## Reglas deterministas involucradas

## Herramientas involucradas

## Supervisión humana

## Auditoría

## Fallback

## Pruebas

## Riesgos
```

## Lista de comprobación final

- [ ] La salida es estructurada.
- [ ] Pydantic valida la salida.
- [ ] No se inventan datos.
- [ ] Categoría, prioridad y estado son válidos.
- [ ] Las reglas críticas no dependen solo del prompt.
- [ ] El área se obtiene de configuración.
- [ ] El agente no aprueba ni rechaza.
- [ ] La persistencia pasa por herramientas y repositorios.
- [ ] El fallback funciona.
- [ ] La propuesta original se conserva.
- [ ] Las decisiones humanas requieren motivo cuando modifican.
- [ ] La auditoría registra evidencia operativa.
- [ ] Los duplicados son candidatos, no conclusiones.
- [ ] Se probaron regresiones.
