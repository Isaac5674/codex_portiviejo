# Pruebas y casos de demostración

## Estrategia

Las pruebas deben enfocarse en las partes con mayor riesgo:

1. Reglas.
2. Modelos.
3. Persistencia.
4. Auditoría.
5. Respaldo sin IA.
6. Flujo de revisión.

## Pruebas unitarias mínimas

### Reglas

- Clasifica fuga como `AGUA`.
- Clasifica basura como `BASURA`.
- Clasifica luminaria como `ALUMBRADO`.
- Clasifica hueco como `VIALIDAD`.
- Clasifica alcantarilla como `ALCANTARILLADO`.
- Devuelve `OTRO` cuando no existe evidencia.
- Asigna área correcta.
- Detecta prioridad alta por riesgo.
- Detecta prioridad media por afectación.
- Detecta prioridad baja por mantenimiento.

### Modelos

- Acepta categorías válidas.
- Rechaza categorías inventadas.
- Acepta prioridades válidas.
- Rechaza prioridades inventadas.
- Exige justificación.
- Convierte listas vacías correctamente.
- Rechaza salida incompleta.

### Repositorios

- Crea solicitud.
- Obtiene solicitud.
- Lista solicitudes.
- Actualiza campos permitidos.
- Rechaza campos no permitidos.
- Registra auditoría.
- Obtiene historial.
- Maneja respuesta vacía.

## Casos de demostración

### Caso 1: riesgo alto

Descripción:

```text
Hay una alcantarilla sin tapa frente a la escuela del barrio San José. Desde ayer casi ocurre un accidente.
```

Ubicación:

```text
Barrio San José, frente a la escuela
```

Esperado:

- Categoría `ALCANTARILLADO`.
- Prioridad `ALTA`.
- Área `Alcantarillado`.
- Señales de escuela, abertura y accidente.
- Estado inicial `PENDIENTE_REVISION`.

### Caso 2: información insuficiente

Descripción:

```text
Hay un hueco peligroso.
```

Ubicación:

```text
Sin especificar
```

Esperado:

- Categoría `VIALIDAD`.
- Información faltante de ubicación.
- Estado `REQUIERE_INFORMACION`.

### Caso 3: prioridad media

Descripción:

```text
La luminaria del parque no funciona desde hace cuatro noches.
```

Ubicación:

```text
Parque del barrio Los Tamarindos
```

Esperado:

- Categoría `ALUMBRADO`.
- Prioridad `MEDIA`.
- Área `Alumbrado público`.

### Caso 4: posible duplicado

Caso existente:

```text
Existe una fuga de agua frente al mercado central.
```

Caso nuevo:

```text
Se está desperdiciando agua en la calle del mercado.
```

Esperado:

- Mostrar el caso existente como candidato.
- No confirmar automáticamente el duplicado.
- Permitir revisión humana.

## Pruebas manuales antes de la demo

- [ ] `streamlit run app.py` inicia.
- [ ] El formulario valida campos.
- [ ] La IA produce salida estructurada.
- [ ] El modo local funciona sin API.
- [ ] Un expediente se guarda en Supabase.
- [ ] El expediente aparece en la tabla.
- [ ] Un operador puede aprobar.
- [ ] Un operador puede modificar y aprobar.
- [ ] Un operador puede rechazar.
- [ ] El historial muestra cada acción.
- [ ] El error de Supabase no muestra éxito.
- [ ] No aparecen claves en pantalla.
