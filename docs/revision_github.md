# Revisión de repositorios abiertos (Módulo 4, versión preliminar)

**Fecha:** 2026-10-14 · **Foco:** herramientas reutilizables para el procedimiento de riesgo
climático **poblacional y comunal** (`docs/metodologia_riesgo_poblacional.md`).

## Cómo se hizo

- **Descubrimiento:** búsqueda web y proyectos conocidos del área. El buscador de GitHub no está
  disponible en las sesiones en la nube de este proyecto, así que puede haber repositorios
  relevantes que no aparecieron, sobre todo chilenos y latinoamericanos.
- **Verificación:** cada repositorio se clonó (solo metadatos). La **licencia** se leyó del archivo
  `LICENSE` o del campo `License` de `DESCRIPTION`, y la **actividad** es la fecha del último
  commit en la rama principal. Todo fue verificado el 2026-10-14.
- No se ejecutó código de ningún repositorio.

## Qué se puede reutilizar libremente

| Licencia | Se puede copiar o adaptar el código en trabajo de consultoría | Condición |
|---|---|---|
| MIT, Apache-2.0, BSD, CC0 | Sí, libremente | Mantener el aviso de copyright y la licencia (Apache, además, el archivo NOTICE si existe) |
| GPL-2/3 | Sí, se puede **usar** sin restricción, incluso en consultoría comercial | Si se **distribuye** software que incluye código GPL modificado, ese software debe publicarse como GPL. Usarlo como dependencia en análisis propios no obliga a nada |

Ninguno de los candidatos tiene una licencia que impida el uso comercial.

## Tabla comparativa

Abreviaturas: Py = Python · R = R.

### A. Amenaza climática (índices, regionalización, escenarios)

| Repositorio | Leng. | Licencia | Último commit | Qué hace | Uso para nosotros | Veredicto |
|---|---|---|---|---|---|---|
| [Ouranosinc/xclim](https://github.com/Ouranosinc/xclim) | Py | Apache-2.0 | 2026-10-13 | Más de 150 índices climáticos sobre xarray (olas de calor, días sobre umbral, SPI/SPEI, precipitación extrema); corrección de sesgo | Cálculo de la amenaza en la Ruta B (Paso F2) | **Reutilizar** (dependencia central) |
| [Ouranosinc/xscen](https://github.com/Ouranosinc/xscen) | Py | Apache-2.0 | 2026-10-08 | Flujo completo sobre xclim: catálogos de simulaciones, ensambles, deltas por horizonte | Orquestar el ensamble multi-modelo y los horizontes AR6 | **Adaptar** (evaluar si su complejidad se justifica) |
| [cerfacs-globc/icclim](https://github.com/cerfacs-globc/icclim) | Py | Apache-2.0 | 2026-10-06 | Índices ECA&D/ETCCDI | Alternativa a xclim | Descartar (redundante con xclim) |
| [monocongo/climate_indices](https://github.com/monocongo/climate_indices) | Py | BSD | 2026-10-12 | SPI, SPEI, PET, PDSI | Sequía, si xclim no alcanza | Referencia |
| [carbonplan/cmip6-downscaling](https://github.com/carbonplan/cmip6-downscaling) | Py | MIT | 2026-06-23 | Métodos de regionalización estadística de CMIP6 | Solo si hay que regionalizar por cuenta propia | Referencia |
| [pangeo-data/xESMF](https://github.com/pangeo-data/xESMF) | Py | MIT | 2026-09-08 | Re-grillado entre mallas | Llevar el clima a la malla de población | **Reutilizar** si hace falta |
| [ESMValGroup/ESMValTool](https://github.com/ESMValGroup/ESMValTool) | Py | Apache-2.0 | 2026-10-09 | Evaluación de modelos climáticos | Excesivo para un laptop de 16 GB | Descartar |
| [ropensci/chirps](https://github.com/ropensci/chirps) | R | MIT | 2026-06-23 | Acceso a precipitación CHIRPS | Precipitación observada (sequía) como complemento de CR2MET | Referencia |

### B. Agregación a comuna y ponderación por población

| Repositorio | Leng. | Licencia | Último commit | Qué hace | Uso para nosotros | Veredicto |
|---|---|---|---|---|---|---|
| [isciences/exactextract](https://github.com/isciences/exactextract) | Py/C++ | Apache-2.0 | 2026-10-13 | Estadística zonal exacta (celdas parciales), con **pesos** | Amenaza por comuna **ponderada por población** (Paso F2) | **Reutilizar** |
| [isciences/exactextractr](https://github.com/isciences/exactextractr) | R | Apache-2.0 | 2026-06-02 | Lo mismo en R; documenta la temperatura ponderada por población ([viñeta](https://isciences.r-universe.dev/exactextractr)) | Misma función desde Positron | **Reutilizar** |
| [regionmask/regionmask](https://github.com/regionmask/regionmask) | Py | MIT | 2026-10-08 | Máscaras de regiones sobre grillas xarray | Alternativa liviana para promedios por comuna | Referencia |
| [ks905383/xagg](https://github.com/ks905383/xagg) | Py | GPL-3.0 | 2025-04-08 | Agregación de grillas a polígonos con pesos | Hace lo mismo que exactextract | Descartar (exactextract es más activo y permisivo) |

### C. Exposición: población y territorio de Chile

| Repositorio | Leng. | Licencia | Último commit | Qué hace | Uso para nosotros | Veredicto |
|---|---|---|---|---|---|---|
| [pachadotdev/chilemapas](https://github.com/pachadotdev/chilemapas) | R | Apache-2.0 | 2026-09-16 | Mapas de comunas, provincias y regiones con códigos; el autor advierte que son **simplificados y sin validez legal** ([manual CRAN](https://search.r-project.org/CRAN/packages/chilemapas/chilemapas.pdf)) | Mapas para el informe y Shiny; cruce rápido por código comunal | **Reutilizar** (para visualizar, no para cálculos de área exacta) |
| [ropensci/censo2017](https://github.com/ropensci/censo2017) | R | CC0 | 2024-09-18 | Censo 2017 completo en una base local, revisado por rOpenSci ([blog](https://ropensci.org/blog/2022/10/19/censo2017-one-year-after/)) | Línea de comparación 2017; modelo para el conector del Censo 2024 | **Reutilizar** (2017) y **adaptar** (patrón para 2024) |
| [wpgp/wpgpDownloadR](https://github.com/wpgp/wpgpDownloadR) | R | GPL | 2018-12-02 | Descarga de grillas WorldPop | Grilla de población para ponderar | Descartar el paquete (abandonado); usar los datos WorldPop o GHSL directamente |

### D. Impacto en salud (calor)

| Repositorio | Leng. | Licencia | Último commit | Qué hace | Uso para nosotros | Veredicto |
|---|---|---|---|---|---|---|
| [gasparrini/dlnm](https://github.com/gasparrini/dlnm) | R | GPL (≥2) | 2025-04-17 | Modelos de rezagos distribuidos no lineales: el estándar para la relación temperatura-mortalidad | Estimar la curva de riesgo relativo con datos DEIS (Paso F6) | **Reutilizar** (paquete estable; usar como dependencia) |
| [onssoschi/climatehealth](https://github.com/onssoschi/climatehealth) | R | MIT | 2026-09-28 | Flujo completo clima-salud sobre dlnm: fracción y número atribuible, temperatura de mínima mortalidad ([guía](https://cran.r-universe.dev/climatehealth/doc/getting-started.html)) | **Mortalidad atribuible al calor por región o comuna** | **Reutilizar / adaptar** (candidato principal para la cadena calor-salud) |

### E. Riesgo físico con funciones de daño

| Repositorio | Leng. | Licencia | Último commit | Qué hace | Uso para nosotros | Veredicto |
|---|---|---|---|---|---|---|
| [CLIMADA-project/climada_python](https://github.com/CLIMADA-project/climada_python) | Py | GPL-3.0 | 2026-06-08 | Plataforma de riesgo amenaza × exposición × vulnerabilidad, con funciones de impacto y medidas de adaptación; trabaja también con **población** como exposición | Marco de referencia y fase 2 (inundación y calor con funciones de impacto) | **Adaptar** en fase 2; como referencia metodológica desde ya |
| [os-climate/physrisk](https://github.com/os-climate/physrisk) | Py | Apache-2.0 | 2026-10-04 | Riesgo físico de **activos financieros** | Orientado a carteras, no a población | Referencia (estructura de datos de amenazas) |
| [OasisLMF/OasisLMF](https://github.com/OasisLMF/OasisLMF) | Py | BSD-3 | 2026-09-30 | Modelos de catástrofe para seguros | Pérdidas aseguradas, no población | Descartar |
| [GFDRR/thinkhazard](https://github.com/GFDRR/thinkhazard) | Py | GPL-3.0 | 2026-10-05 | Plataforma web de screening de amenazas por unidad administrativa | Clasificación de amenaza por nivel (bajo/medio/alto) como referencia | Referencia |

### F. Escenarios y transición

| Repositorio | Leng. | Licencia | Último commit | Qué hace | Uso para nosotros | Veredicto |
|---|---|---|---|---|---|---|
| [IAMconsortium/pyam](https://github.com/IAMconsortium/pyam) | Py | Apache-2.0 | 2026-09-08 | Lee y manipula escenarios de modelos integrados (IAMC), incluida la conexión a las bases de datos de IIASA donde se publican los escenarios NGFS | **Descargar las trayectorias NGFS** (precio del carbono, energía, PIB) sin escribirlas a mano | **Reutilizar** |
| [ClimateImpactLab/dscim](https://github.com/ClimateImpactLab/dscim) | Py | Apache-2.0 | 2026-08-04 | Cálculo del costo social del carbono con funciones de daño sectoriales | Referencia metodológica de daños | Referencia |
| [2DegreesInvesting/r2dii.analysis](https://github.com/2DegreesInvesting/r2dii.analysis) | R | MIT | 2022-05-16 | Alineamiento de carteras de crédito con escenarios (PACTA) | Corporativo/financiero | Descartar |

## Recomendación

**Stack base para la primera cadena (calor y salud):**
1. `xclim`: índices de calor por escenario.
2. `exactextract` / `exactextractr`: amenaza por comuna ponderada por población.
3. `chilemapas` y `censo2017`: geometrías, códigos y población 2017. El Censo 2024 requiere un conector propio, siguiendo el patrón de `censo2017`.
4. `climatehealth` (sobre `dlnm`): mortalidad atribuible al calor.
5. `pyam`: trayectorias NGFS para el riesgo de transición.

**Fase 2:** CLIMADA para inundación e incendios con funciones de impacto sobre población.

**Descartados:** Oasis, r2dii, ESMValTool e icclim, por estar orientados a carteras o seguros, o por ser redundantes o excesivos para el hardware disponible.

## Segunda ronda: búsqueda desde el laptop (2026-10-14)

`make buscar-repos` ejecutó 20 búsquedas y devolvió **245 repositorios únicos**
(`catalog/repos_github.csv`). La mayoría no sirve: apps del tiempo, tareas de cursos y homónimos
de "ARClim". Se revisaron a fondo 20, clonándolos para ver la licencia, la fecha y el contenido.

**Importante sobre licencias:** un repositorio **sin licencia** no es de uso libre. Por defecto, su
autor conserva todos los derechos: se puede leer y aprender de él, pero no copiar su código. Sí se
pueden usar los **hechos** que documenta (por ejemplo, la dirección de un archivo público).

### Hallazgo principal: los indicadores comunales de ARClim se descargan directamente

El repositorio [Sud-Austral/DATA_ARCLIM](https://github.com/Sud-Austral/DATA_ARCLIM) (sin licencia)
muestra que ARClim publica un GeoJSON con las amenazas climáticas comunales en:

`https://arclim.mma.gob.cl/media//FeatureSets/comunas//clima/amenazas_comunas_annual.geojson`

Se descargó y revisó el 2026-10-14 **[V]**:
- **345 comunas** (polígonos), 3,9 MB;
- la clave `arclim_id` es el **CUT vigente**: 1401 = Pozo Almonte, y Ñuble aparece como región 16;
- **59 indicadores**, cada uno en tres versiones (`_present`, `_future`, `_delta`), entre ellos:
  - **calor:** `hot_days`, `summer_days`, `tropical_nights`, `hottest_day`,
    `warm_spell_duration_index_*`, `warm_nights_duration_index_*`;
  - **sequía:** `drought_periods`, `consecutive_dry_days`, `pr_sum`, `eto_mean`;
  - **precipitación extrema:** `maximum_daily_precipitation`, `number_of_heavy_precipitation_days`,
    `number_of_very_heavy_precipitation_days`, `total_from_extremely_wet_days`;
  - **otros:** frío, heladas, nieve, viento, humedad y radiación.

**Por verificar [NV]:** qué escenario y qué períodos definen "present" y "future" en esta versión
(algunos archivos de terceros mencionan `ssp585`, lo que sugiere CMIP6), las 346 comunas oficiales
frente a las 345 del archivo, y los términos de uso de los datos.

Con esto, la **Ruta A** de la metodología (indicadores ARClim comunales) es viable de inmediato
para la cadena calor-salud.

### Repositorios relevantes de la segunda ronda

| Repositorio | Leng. | Licencia | Último commit | Qué aporta | Veredicto |
|---|---|---|---|---|---|
| [bastianolea/territorial](https://github.com/bastianolea/territorial) | R | GPL-3.0 | 2026-10-08 | Limpieza de nombres de comunas, **actualización de CUT antiguos** (incluido el cambio por Ñuble) y macrozonas | **Reutilizar** (dependencia) para la tabla territorial |
| [bastianolea/poblador](https://github.com/bastianolea/poblador) | R | GPL-3.0 | 2026-08-12 | Población oficial: Censo 2017, Censo 2024, proyecciones y **pobreza comunal MIDESO** (ingresos y multidimensional) | **Reutilizar** para exposición y vulnerabilidad; contrastar con las fuentes oficiales |
| [pachadotdev/casen](https://github.com/pachadotdev/casen) | R | Apache-2.0 | 2022-06-21 | CASEN con diseño muestral complejo | Referencia (sin actividad reciente) |
| [fabiancarrilloh/casenHarmoniza](https://github.com/fabiancarrilloh/casenHarmoniza) | R | MIT | 2026-05-15 | Armonización de variables CASEN 2017, 2022 y 2024, con diccionarios y cifras de control | **Adaptar** |
| [klak1996/Download_data_cr2met](https://github.com/klak1996/Download_data_cr2met) | Py | MIT | 2025-09-17 | Descarga masiva de CR2MET v2.5_R1 | **Adaptar** para el conector CR2MET |
| [pachadotdev/censo2024-duckdb](https://github.com/pachadotdev/censo2024-duckdb) | R | sin licencia | 2025-12-06 | Censo 2024 en DuckDB, con correcciones | Referencia; pedir licencia al autor o hacer conector propio |
| [bastianolea/censo_2024](https://github.com/bastianolea/censo_2024) | R | sin licencia | 2025-07-27 | Tablas del Censo 2024 (edad, servicios básicos, discapacidad) | Referencia: muestra qué tabulados publica el INE |
| [zeliest/lancet_countdown_heatwave_2024](https://github.com/zeliest/lancet_countdown_heatwave_2024) | Py | sin licencia | 2024-09-03 | Indicador de **exposición de población a olas de calor** del Lancet Countdown (ERA5 + WorldPop/GPW) | **Referencia metodológica** clave para la cadena calor-salud |
| [maximilianstarp/EnergyPoverty](https://github.com/maximilianstarp/EnergyPoverty) | Py | MIT | 2026-03-12 | Simulación del efecto de precios de energía y políticas en la pobreza energética de hogares | **Adaptar** para el canal de costo energético de la transición |
| [MeldaS/FloodPop](https://github.com/MeldaS/FloodPop) | Py | MIT | 2021-06-02 | Población expuesta a inundación (global) | Referencia para la fase 2 |
| [GFDRR/rdl-standard](https://github.com/GFDRR/rdl-standard) | — | CC BY-SA 4.0 | 2026-07-13 | Estándar de metadatos para datos de riesgo | Referencia para el esquema de `catalog/` |
| [knxroot/bdcut-cl](https://github.com/knxroot/bdcut-cl) | SQL | sin licencia | 2020-08-25 | Códigos CUT de regiones, provincias y comunas | Descartar (desactualizado; usar `territorial` y la fuente oficial) |

Descartados en esta ronda: visualizadores temáticos (delincuencia, corrupción, elecciones), apps
del tiempo, proyectos de curso, modelos corporativos o de seguros con escenarios NGFS, y
repositorios homónimos de ARClim sin relación.

## Vacíos

- **ARClim no tiene código abierto oficial**, pero sus indicadores comunales se descargan directamente (ver arriba). Del CR2 no hay código oficial. CR2 publica sus datos en el
  portal [DataClima](https://www.cr2.cl/eng/cr2-launches-dataclima-a-repository-of-platforms-and-databases-on-climate-conditions-in-chile/),
  y el paquete R `hydrotoolbox` lee los CSV del Explorador Climático del CR2
  ([viñeta](https://cran.csail.mit.edu/web/packages/hydrotoolbox/vignettes/cr2_cl.html)). Hay que
  escribir conectores propios.
- **CASEN:** no apareció un paquete mantenido. Se hará un conector propio con `survey`/`srvyr`.
- **Riesgo de transición para hogares:** no se encontró ninguna herramienta abierta. Esa parte se
  construye desde cero (`docs/metodologia_riesgo_poblacional.md`, sección 4).
- **Pendiente:** búsqueda dirigida de proyectos latinoamericanos (CEPAL, BID, universidades
  chilenas) cuando haya acceso al buscador de GitHub o con búsquedas web adicionales.
