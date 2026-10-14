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

## Vacíos

- **No se encontró código abierto de ARClim ni del CR2** en GitHub. CR2 publica sus datos en el
  portal [DataClima](https://www.cr2.cl/eng/cr2-launches-dataclima-a-repository-of-platforms-and-databases-on-climate-conditions-in-chile/),
  y el paquete R `hydrotoolbox` lee los CSV del Explorador Climático del CR2
  ([viñeta](https://cran.csail.mit.edu/web/packages/hydrotoolbox/vignettes/cr2_cl.html)). Hay que
  escribir conectores propios.
- **CASEN:** no apareció un paquete mantenido. Se hará un conector propio con `survey`/`srvyr`.
- **Riesgo de transición para hogares:** no se encontró ninguna herramienta abierta. Esa parte se
  construye desde cero (`docs/metodologia_riesgo_poblacional.md`, sección 4).
- **Pendiente:** búsqueda dirigida de proyectos latinoamericanos (CEPAL, BID, universidades
  chilenas) cuando haya acceso al buscador de GitHub o con búsquedas web adicionales.
