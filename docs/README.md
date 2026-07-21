# Documentación de PortoReporta

Esta carpeta contiene las reglas operativas y técnicas que deben leer Codex y cualquier otra inteligencia artificial antes de modificar el proyecto.

## Orden obligatorio de lectura

1. `contexto-proyecto.md`
2. `instrucciones-generales.md`
3. `alcance-mvp.md`
4. `arquitectura-y-responsabilidades.md`
5. `contratos-de-datos.md`
6. `reglas-de-negocio.md`
7. `flujos-y-estados.md`
8. `persistencia-supabase.md`
9. `seguridad-y-privacidad.md`
10. `manejo-de-errores.md`
11. `pruebas-y-casos-demo.md`
12. `criterios-de-aceptacion.md`
13. `plan-de-trabajo-codex.md`
14. `decisiones-tecnicas.md`
15. `glosario.md`
16. `integracion-y-despliegue.md`

## Jerarquía de autoridad

Cuando exista una contradicción, se debe respetar este orden:

1. Instrucción explícita del responsable humano en la conversación actual.
2. `docs/contexto-proyecto.md`.
3. `docs/instrucciones-generales.md`.
4. Documentos técnicos específicos dentro de `docs/`.
5. Código existente y pruebas automatizadas.
6. Suposiciones de la inteligencia artificial.

La inteligencia artificial no puede reemplazar una regla documentada con una suposición.

## Regla principal

> La IA interpreta y recomienda, las reglas validan, Supabase persiste y la persona decide.

## Actualización de documentación

Toda modificación que cambie alguno de estos elementos debe actualizar también la documentación correspondiente:

- Arquitectura.
- Esquema de Supabase.
- Categorías.
- Prioridades.
- Estados.
- Variables de entorno.
- Flujo de revisión humana.
- Criterios de aceptación.
- Dependencias.
- Comandos de ejecución.

No crear documentación ficticia sobre funciones que todavía no existen.

## Archivo existente que debes conservar

Copia tu documento principal actual como:

```text
docs/contexto-proyecto.md
```

No lo sustituí dentro de este paquete para evitar crear dos versiones diferentes de la fuente principal.
