# Integración y despliegue

Esta guía prepara la integración del equipo y el despliegue posterior. No declara que PortoReporta esté desplegado: la aplicación todavía requiere los módulos del agente, Supabase e interfaz.

## Estado actual

| Componente | Estado | Responsable |
|---|---|---|
| Contratos, modelos y reglas locales | Disponible y probado | Integrante 1 |
| Agente, herramientas y fallback | Disponible e integrado | Integrante 2 |
| Supabase, RLS, repositorios y auditoría | Disponible e integrado | Integrante 3 |
| Streamlit, revisión humana y flujo completo | Disponible e integrado | Integrante 4 |
| Despliegue final | Configuración de Vercel preparada; falta autenticar, configurar secretos y verificar producción | Responsable de despliegue |

Al revisar la integración se alineó el trigger del esquema con el dominio: un
caso nuevo con candidatos puede iniciar como `POSIBLE_DUPLICADO`, sin que esto
confirme que los reportes sean iguales.

La suite local cubre los contratos, reglas, agente, herramientas, repositorios e
interfaz mediante dobles controlados. La conexión con un proyecto remoto de
Supabase, la aplicación de migraciones y una ejecución real de OpenAI requieren
credenciales de un entorno de prueba y no se consideran verificadas por las
pruebas locales.

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
- [ ] Se aplicó la migración `202607210001_permitir_posible_duplicado_inicial.sql` en Supabase.
- [ ] La aplicación inicia sin mostrar secretos.
- [ ] La revisión humana sigue siendo obligatoria.
- [ ] La falla de OpenAI activa el modo local visible.
- [ ] La falla de Supabase no se comunica como guardado exitoso.
- [ ] `pytest -q` pasa con los módulos integrados.
- [ ] Se prueba el flujo completo con datos ficticios, nunca con datos personales reales.

## Despliegue en Vercel

Vercel ejecuta Streamlit mediante la imagen declarada en `Dockerfile.vercel`.
El contenedor escucha en la variable `PORT` asignada por Vercel y no contiene
archivos `.env`, pruebas ni documentación.

1. Autenticar la CLI con `vercel login`.
2. Enlazar o crear el proyecto con `vercel link`.
3. Configurar `OPENAI_API_KEY`, `SUPABASE_URL`, `SUPABASE_SECRET_KEY` y
   `APP_ENV=production` como variables cifradas de producción.
4. Confirmar que la migración pendiente está aplicada en Supabase.
5. Ejecutar `vercel deploy --prod`.
6. Abrir la URL de producción y verificar inicio, creación, revisión humana,
   fallos visibles e historial.

El despliegue puede iniciar sin `OPENAI_API_KEY` usando reglas locales, pero
la creación y consulta de expedientes requieren las dos variables de Supabase.
Los secretos nunca deben agregarse al repositorio ni incorporarse a la imagen.
