# climachile — plataforma abierta de riesgo climático para Chile

Base reproducible para analizar riesgo climático físico y de transición en Chile
con datos públicos (INE, MMA/ARClim, CR2, DGA, SISS, Banco Central, entre otros)
y marcos internacionales (IPCC AR6, NGFS, TCFD/IFRS S2, NCG N°519 CMF).

**Estado:** fase 0, flujo de trabajo en la nube. Los módulos de contenido
(matriz de riesgos, catálogo de fuentes, módulo poblacional, piloto) vienen después.

## Cómo funciona

```
   Laptop (Positron)                         Nube (sesiones Claude Code)
   exploración, gráficos, redacción          tareas largas o autónomas
          │  git pull/push                             │
          └──────────────►  GitHub  ◄──────────────────┘   código, docs, manifiestos
          │  make pull/push                            │
          └──────────────►  Google Drive  ◄────────────┘   datos (raw/staging/marts/grids)
```

- **GitHub** guarda el código, la documentación y el **manifiesto** de los datos
  (`ref/manifiestos/manifiesto.csv`: qué archivos hay en Drive, con su sha256).
- **Google Drive** (carpeta `climachile-data/`) guarda los datos. Nunca van a git.
- **`data/`** es una caché local desechable. Se llena con `make pull`.

Regla de oro: lo que no está en GitHub o en Drive al cerrar una sesión en la nube, se pierde.

## Uso diario

```bash
git pull                                  # traer lo último
make pull RUTA=marts/panel_comunal        # bajar los datos que necesitas
# ... trabajar en Positron o pedirle a Claude ...
make push RUTA=staging/mi_fuente          # subir datos nuevos (no sobrescribe)
git add -A && git commit -m "..." && git push
```

Desde Python:

```python
from climachile import db
con = db.conectar()
db.registrar_vista(con, "panel", "marts/panel_comunal")
con.sql("select * from panel limit 5").pl()
```

Desde R:

```r
source("R/climachile.R")
con <- cc_conectar()
cc_vista(con, "panel", "marts/panel_comunal")
DBI::dbGetQuery(con, "select * from panel limit 5")
```

## Puesta en marcha

- En tu laptop: [`docs/setup_local.md`](docs/setup_local.md)
- En la nube: [`docs/setup_nube.md`](docs/setup_nube.md)
- **Uso diario: [`docs/guia_rapida.md`](docs/guia_rapida.md)**
- Decisiones de diseño: [`docs/decisiones.md`](docs/decisiones.md)
- **Metodología: [`docs/metodologia_riesgo_poblacional.md`](docs/metodologia_riesgo_poblacional.md)**

## Estructura

```
src/climachile/   paquete Python: config, manifiesto, sincronización con Drive, DuckDB
R/                funciones R para leer la caché (DuckDB/Parquet) y setup de renv
ref/              tablas pequeñas versionadas (manifiestos, territorio CUT)
catalog/          catálogo de fuentes (Módulo 2)
analisis/         análisis libres; copia analisis/_plantilla para empezar uno nuevo
docs/             documentación y decisiones
tests/            pruebas (incluye prueba de ida y vuelta con Drive simulado)
.claude/hooks/    script de arranque de las sesiones en la nube
data/             caché local de datos (ignorada por git)
```

## Capas de datos

| Capa | Contenido | Regla |
|---|---|---|
| `raw/<fuente>/<version>/` | tal como lo entrega la fuente | inmutable |
| `staging/<fuente>/` | limpio, tipado, con CUT vigente; Parquet | una tabla por fuente |
| `marts/<tabla>/` | tablas integradas para análisis (p. ej. panel CUT × año) | consumidas por análisis e informes |
| `grids/<fuente>/<escenario>/` | grillas climáticas recortadas a Chile (NetCDF) | archivos medianos, no miles de chunks |
