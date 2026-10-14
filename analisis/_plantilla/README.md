# Plantilla de análisis

Para empezar un análisis nuevo:

```bash
cp -r analisis/_plantilla analisis/AAAA-MM_nombre_corto
```

Reglas:
- Un análisis **lee** `staging/` o `marts/` con `make pull` y nunca modifica `raw/`.
- Si produce datos que otros análisis van a reutilizar, el código pasa al paquete
  `src/climachile/` y el resultado se sube a `marts/`.
- Anota aquí arriba la pregunta, los datos usados (rutas del manifiesto) y la fecha.

## Pregunta

## Datos

| Ruta | Versión/fecha |
|---|---|

## Resultados
