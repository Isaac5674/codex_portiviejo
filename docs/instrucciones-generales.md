# Instrucciones generales para Codex

## 1. Propósito

Este documento define cómo debe trabajar Codex dentro de PortoReporta para evitar decisiones inventadas, cambios de alcance, dependencias innecesarias y comportamientos no autorizados.

Codex debe leer este archivo antes de crear, editar, eliminar o reorganizar código.

---

## 2. Principios obligatorios

1. No inventar requisitos.
2. No ampliar el alcance del MVP.
3. No cambiar tecnologías sin autorización.
4. No afirmar que una función existe sin comprobar el código.
5. No afirmar que una prueba pasó sin ejecutarla.
6. No afirmar que un registro fue guardado sin verificar la respuesta de Supabase.
7. No inventar datos faltantes del ciudadano.
8. No aprobar ni rechazar solicitudes automáticamente.
9. No exponer secretos.
10. No presentar PortoReporta como una plataforma oficial del Municipio de Portoviejo.
11. No introducir una base de datos alternativa.
12. No ocultar fallos detrás de resultados simulados.
13. No modificar archivos no relacionados con la tarea actual.
14. No reemplazar código funcional por una arquitectura más compleja.
15. No añadir funciones opcionales antes de completar el flujo principal.

---

## 3. Fuente de verdad

Antes de implementar una tarea, Codex debe consultar:

- `docs/contexto-proyecto.md`.
- El documento técnico relacionado con la tarea.
- El código existente.
- Las pruebas existentes.
- El esquema SQL vigente.

Si dos fuentes se contradicen, Codex debe aplicar la jerarquía definida en `docs/README.md`.

---

## 4. Protocolo cuando falta información

Cuando un requisito no esté documentado:

1. No inventar una respuesta definitiva.
2. Buscar primero una regla equivalente en la documentación.
3. Elegir la opción más simple que mantenga el alcance.
4. Marcar la decisión como una suposición temporal.
5. Evitar cambios irreversibles.
6. Pedir autorización humana únicamente cuando la decisión afecte:
   - El esquema de base de datos.
   - La arquitectura.
   - La seguridad.
   - El alcance.
   - Las dependencias.
   - Las reglas de prioridad.
   - Los estados del caso.
   - La experiencia principal de demostración.

Para detalles menores de implementación, utilizar la alternativa más simple y documentarla.

---

## 5. Tecnologías permitidas

### Permitidas

- Python 3.11 o superior.
- Streamlit.
- OpenAI Agents SDK para Python.
- Pydantic.
- Supabase.
- PostgreSQL administrado por Supabase.
- `supabase-py`.
- `python-dotenv`.
- `pytest`.
- Biblioteca estándar de Python.
- `difflib.SequenceMatcher` para duplicados en el MVP.

### No permitidas sin autorización

- React.
- Vue.
- Angular.
- Next.js.
- FastAPI.
- Flask.
- Django.
- MySQL.
- SQLite.
- MongoDB.
- Firebase.
- Redis.
- Docker como requisito obligatorio.
- Microservicios.
- Colas de mensajes.
- Modelos propios de aprendizaje automático.
- Servicios externos adicionales.
- Nuevos frameworks de agentes.

---

## 6. Restricciones de alcance

Codex no debe implementar durante el MVP:

- Aplicación móvil.
- Mapas reales.
- Geolocalización.
- WhatsApp.
- Correo electrónico.
- Integración con sistemas municipales.
- Reconocimiento de imágenes.
- Autenticación compleja.
- Roles avanzados.
- Dashboard avanzado.
- Seguimiento de cuadrillas.
- Resolución física del problema.
- Notificaciones reales.
- Despliegue complejo.

Las funciones opcionales solo pueden iniciarse después de cumplir todos los criterios de aceptación.

---

## 7. Reglas de implementación

### Antes de editar

Codex debe:

1. Identificar los archivos involucrados.
2. Explicar brevemente qué cambiará.
3. Revisar las interfaces públicas que podrían verse afectadas.
4. Revisar las pruebas relacionadas.
5. Evitar reescrituras completas si una modificación pequeña es suficiente.

### Durante la edición

Codex debe:

- Mantener responsabilidades separadas.
- Evitar consultas directas a Supabase desde múltiples pantallas.
- Mantener categorías y áreas en una configuración central.
- Validar salidas del agente con Pydantic.
- Manejar errores de API y base de datos.
- Registrar eventos de auditoría.
- Evitar valores mágicos duplicados.
- Usar nombres claros en español o mantener el estilo ya existente.
- No imprimir claves, tokens ni objetos completos de configuración.

### Después de editar

Codex debe:

1. Ejecutar las pruebas relacionadas.
2. Ejecutar una validación manual mínima del flujo afectado.
3. Informar qué archivos cambió.
4. Informar qué pruebas ejecutó.
5. Informar cualquier limitación pendiente.
6. No declarar éxito total si existe una falla conocida.

---

## 8. Reglas para respuestas de Codex

Cada entrega debe incluir:

- Resumen de cambios.
- Archivos modificados.
- Comandos ejecutados.
- Resultado de pruebas.
- Riesgos o pendientes reales.
- Instrucciones para verificar el cambio.

Codex no debe usar frases como:

- “Todo funciona” sin evidencia.
- “La base de datos quedó configurada” sin comprobar conexión.
- “Las pruebas pasan” sin ejecutarlas.
- “El municipio recibirá el reporte”.
- “El problema fue resuelto”.
- “El caso es definitivamente duplicado”.

---

## 9. Reglas de seguridad

- Nunca escribir secretos dentro del código.
- Nunca subir `.env`.
- Nunca mostrar `SUPABASE_SECRET_KEY`.
- Nunca mostrar `OPENAI_API_KEY`.
- Nunca registrar credenciales en auditoría.
- Nunca enviar la clave secreta al navegador.
- Nunca crear políticas públicas de lectura o escritura para el MVP.
- Nunca almacenar datos personales innecesarios.
- Nunca confiar en valores enviados por el usuario para seleccionar tablas o columnas.

---

## 10. Reglas de IA y supervisión humana

La IA puede:

- Interpretar.
- Extraer.
- Resumir.
- Clasificar.
- Recomendar prioridad.
- Recomendar área.
- Detectar información faltante.
- Sugerir duplicados.
- Explicar su recomendación.

La IA no puede:

- Aprobar.
- Rechazar.
- Confirmar duplicados.
- Declarar una emergencia oficial.
- Enviar información a instituciones reales.
- Inventar una ubicación.
- Inventar personas afectadas.
- Inventar fechas.
- Inventar métricas.
- Cambiar una decisión humana.

---

## 11. Regla de detención

Cuando todos los criterios de aceptación estén cumplidos:

1. No agregar nuevas funciones.
2. Corregir únicamente errores.
3. Mejorar textos o presentación sin cambiar el flujo.
4. Preparar demostración.
5. Crear un commit estable.
6. Evitar cambios de arquitectura.

---

## 12. Lista de verificación anti-alucinación

Antes de responder o modificar código, Codex debe comprobar:

- [ ] ¿La tarea está documentada?
- [ ] ¿Estoy usando la tecnología autorizada?
- [ ] ¿Estoy creando una función fuera del alcance?
- [ ] ¿Estoy inventando un dato?
- [ ] ¿Estoy afirmando algo que no verifiqué?
- [ ] ¿Estoy cambiando el esquema sin autorización?
- [ ] ¿Estoy exponiendo una credencial?
- [ ] ¿Estoy eliminando la revisión humana?
- [ ] ¿Estoy sustituyendo Supabase?
- [ ] ¿Estoy agregando complejidad innecesaria?
- [ ] ¿Ejecuté las pruebas relacionadas?
- [ ] ¿Documenté las limitaciones reales?
