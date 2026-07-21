# Integración y despliegue

Esta guía prepara la integración del equipo y el despliegue posterior. No declara que PortoReporta esté desplegado: la aplicación todavía requiere los módulos del agente, Supabase e interfaz.

## Estado actual

| Componente | Estado | Responsable |
|---|---|---|
| Contratos, modelos y reglas locales | Disponible y probado | Integrante 1 |
| Agente y herramientas | Disponible y probado | Integrante 2 |
| Supabase, RLS, repositorios y auditoría | Disponible y probado | Integrante 3 |
| Streamlit, revisión humana y flujo completo | Pendiente de integración | Integrante 4 |
| Despliegue final | Bloqueado hasta completar criterios de aceptación | Responsable de despliegue |

## Preparación local

Requiere Python 3.11 o superior.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

En Linux o macOS:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Completar únicamente el archivo local `.env`:

```text
OPENAI_API_KEY=
SUPABASE_URL=
SUPABASE_SECRET_KEY=
APP_ENV=development
```

No colocar valores reales en `.env.example`, documentación, pruebas, commits o registros.

## Contrato que deben consumir los demás integrantes

El Integrante 1 expone:

```python
from src.models import AnalisisReporte, EntradaReporte
from src.rules import analizar_reporte_local, determinar_estado_inicial
```

- El Integrante 2 debe validar la salida de IA con `AnalisisReporte` y ejecutar `analizar_reporte_local(descripcion, ubicacion)` cuando la IA falle.
- El Integrante 3 debe adaptar los campos de `AnalisisReporte` a los nombres persistidos documentados: `prioridad` → `prioridad_agente`, `area_responsable` → `area_agente` y `justificacion` → `justificacion_agente`.
- El Integrante 4 debe validar el formulario con `EntradaReporte` y usar `determinar_estado_inicial(...)` al preparar el expediente.

Ningún integrante debe duplicar enumeraciones, categorías, áreas o reglas de prioridad fuera de `src/models.py` y `src/rules.py`.

La [guía de integración entre integrantes](guia-de-integracion-equipo.md) detalla los campos estables, responsabilidades y pruebas mínimas de cada entrega.

## Verificaciones antes de integrar

Ejecutar primero las pruebas de dominio:

```bash
pytest tests/test_models.py -q
pytest tests/test_rules.py -q
pytest tests/test_demo_cases.py -q
```

Después de integrar los otros módulos:

```bash
pytest -q
streamlit run app.py
```

Comprobar manualmente:

1. Reporte de alcantarilla abierta cerca de una escuela: categoría `ALCANTARILLADO`, prioridad `ALTA` y revisión humana.
2. Reporte de hueco con ubicación `Sin especificar`: `REQUIERE_INFORMACION`.
3. Luminaria dañada: categoría `ALUMBRADO` y prioridad `MEDIA`.
4. Falla de OpenAI: el resultado continúa con `origen_analisis` igual a `REGLAS`.
5. Falla de Supabase: no se muestra éxito ni se inventa un identificador.

## Lista previa al despliegue

No desplegar hasta que todos los criterios de [`criterios-de-aceptacion.md`](criterios-de-aceptacion.md) estén verificados.

- [ ] `requirements.txt` instala las dependencias en un entorno limpio.
- [ ] `.env` no aparece en `git status`.
- [ ] Las variables reales se configuran solo en el servicio de despliegue.
- [ ] La clave secreta de Supabase se usa únicamente del lado servidor.
- [ ] RLS está activo y no existen políticas anónimas públicas.
- [ ] La aplicación inicia sin mostrar secretos.
- [ ] La revisión humana sigue siendo obligatoria.
- [ ] La falla de OpenAI activa el modo local visible.
- [ ] La falla de Supabase no se comunica como guardado exitoso.
- [ ] `pytest -q` pasa con los módulos integrados.
- [ ] Se prueba el flujo completo con datos ficticios, nunca con datos personales reales.

## Procedimiento de despliegue

La plataforma de despliegue todavía no está definida. Cuando se elija una, mantener el mismo flujo:

1. Crear un entorno separado del desarrollo.
2. Instalar desde `requirements.txt`.
3. Configurar las cuatro variables de entorno sin subir un archivo `.env`.
4. Verificar la conexión a Supabase desde el servidor, no desde el navegador.
5. Ejecutar la suite de pruebas y las comprobaciones manuales anteriores.
6. Publicar solo una versión que supere la lista previa.
7. Conservar el commit estable anterior para revertir si falla una verificación.

No configurar despliegue, claves ni conectividad real hasta que el Integrante 4 entregue y valide la integración del flujo completo.
