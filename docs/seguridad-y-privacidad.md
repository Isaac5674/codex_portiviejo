# Seguridad y privacidad

## Datos que no deben almacenarse

- Cédulas.
- Contraseñas.
- Claves API.
- Tokens.
- Teléfonos, salvo autorización futura.
- Correos personales, salvo autorización futura.
- Direcciones residenciales exactas innecesarias.
- Datos médicos.
- Información financiera.
- Fotografías de documentos.
- Información personal no necesaria para el reporte.

## Secretos

Los secretos deben existir únicamente en `.env` o en el sistema de secretos del entorno.

Archivos permitidos en Git:

- `.env.example`
- Documentación de nombres de variables.

Archivos prohibidos en Git:

- `.env`
- `.streamlit/secrets.toml`
- Copias de claves.
- Capturas con claves.
- Logs con tokens.

## Presentación del producto

La interfaz debe mostrar que:

- Es un prototipo.
- No es una plataforma oficial.
- No envía reportes a instituciones reales.
- La prioridad es una recomendación.
- Un operador humano toma la decisión final.

## Validación

- Validar longitud mínima de descripción.
- Validar ubicación.
- Validar enumeraciones.
- Escapar o mostrar como texto las entradas.
- No ejecutar contenido proporcionado por el ciudadano.
- No construir SQL con cadenas del usuario.
- No permitir actualizaciones arbitrarias.

## Registros y errores

Los logs no deben contener:

- Claves.
- Variables completas de entorno.
- Encabezados de autorización.
- Datos personales innecesarios.
- Respuestas completas de servicios cuando incluyan secretos.

Los mensajes al usuario deben:

- Explicar el problema.
- Evitar trazas completas.
- Evitar nombres internos sensibles.
- Indicar si la operación puede reintentarse.

## Revisión de seguridad antes de la demo

- [ ] `.env` no está versionado.
- [ ] `.gitignore` incluye secretos.
- [ ] No existen claves en el historial visible.
- [ ] RLS está activado.
- [ ] No hay políticas anónimas públicas.
- [ ] La clave secreta solo se usa en servidor.
- [ ] La interfaz indica que es un prototipo.
- [ ] No se guardan datos sensibles.
- [ ] Las actualizaciones usan lista blanca.
- [ ] No existe aprobación automática.
