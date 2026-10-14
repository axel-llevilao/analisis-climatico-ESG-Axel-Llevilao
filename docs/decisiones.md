# Registro de decisiones

Cada decisión tiene fecha, contexto, decisión, alternativas descartadas y consecuencias.
Las decisiones no se borran: si cambian, se agrega una nueva que reemplaza a la anterior.

---

## D-001 · Construir primero el flujo de trabajo, después el contenido
**Fecha:** 2026-10-13 · **Estado:** aprobada

**Contexto.** El proyecto abarca cinco módulos (riesgos, catálogo, poblacional,
revisión de GitHub, piloto), además de publicación web y protección de autoría.
Arrancar por el contenido sin una base de trabajo estable genera fricción y retrabajo.

**Decisión.** La fase 0 es solo el flujo de trabajo: repo, entorno reproducible,
almacenamiento de datos y sincronización entre laptop y nube. Los módulos se
construyen encima.

**Consecuencia.** El plan de 7 días se reprograma después de la fase 0.

---

## D-002 · Flujo híbrido: Positron en el laptop + Claude Code en la nube
**Fecha:** 2026-10-13 · **Estado:** aprobada

**Contexto.** Positron es una aplicación de escritorio. Las alternativas para usarlo
en la nube son Remote SSH a una VM ([docs](https://positron.posit.co/remote-ssh.html),
requiere una máquina persistente, de pago) y Dev Containers
([docs](https://positron.posit.co/dev-containers.html), experimental). No se encontró
soporte de Positron en GitHub Codespaces (NO VERIFICADO).

**Decisión.** Positron local para la exploración, la consola, los gráficos y la redacción.
Sesiones de Claude Code en la nube para las tareas largas o autónomas. Ambos lados
comparten GitHub (código) y Google Drive (datos).

**Descartadas.** VM con Remote SSH (costo; se reevalúa si el laptop queda corto).
Posit Workbench (producto empresarial de pago).

**Consecuencias.** El mismo entorno en los dos lados (uv.lock y renv.lock). Las sesiones
en la nube trabajan en ramas `claude/…` y entregan PRs; el laptop hace `git pull`
antes de trabajar.

---

## D-003 · Google Drive como almacén de datos, vía rclone con permiso `drive.file`
**Fecha:** 2026-10-13 · **Estado:** aprobada

**Contexto.** El usuario dispone de 5 TB en Google Drive (Google One). Drive es
durable, pero no sirve como disco de trabajo: no permite lectura parcial de Parquet
desde DuckDB y es lento con miles de archivos pequeños.

**Decisión.**
- Drive guarda los datos en `climachile-data/{raw,staging,marts,grids}`.
- Se trabaja sobre una caché local (`data/`, fuera de git) que se llena con
  `make pull` y se sube con `make push`.
- rclone usa el permiso `drive.file`: solo ve los archivos que él mismo creó.
  Así no tiene acceso al resto del Drive personal ni a documentos de clientes.

**Descartadas.** Montar Drive como disco (lento e inestable para análisis).
Permiso `drive` completo (expone todo el Drive). Google Cloud Storage (costo).

**Consecuencias.**
- Los archivos subidos a mano por la web de Drive no son visibles para rclone.
- El token de rclone vive en el laptop y como variable secreta del entorno en la nube.

---

## D-004 · Capas de datos, manifiesto versionado y no sobrescritura
**Fecha:** 2026-10-13 · **Estado:** aprobada

**Decisión.**
- **Capas:** `raw` (inmutable, tal como viene), `staging` (limpio, una tabla por
  fuente), `marts` (tablas integradas para análisis) y `grids` (grillas climáticas
  en NetCDF por variable × escenario × periodo, sin Zarr con miles de chunks).
- **Manifiesto:** `ref/manifiestos/manifiesto.csv` (ruta, bytes, sha256, fecha, equipo).
  Va en git y dice qué hay en Drive. `make pull` verifica los checksums contra él.
- **Sin sobrescritura:** `make push` usa `rclone --immutable` y falla si un archivo
  ya existe en Drive con otro contenido. Reemplazar exige `make push-forzar`.
  Nunca se usa `rclone sync` (que borra).
- **Formato tabular:** Parquet con particiones gruesas (p. ej. `anio=`).

**Consecuencia.** Las versiones nuevas de una fuente van en rutas nuevas
(`raw/<fuente>/<version>/`), no reemplazan a las anteriores.

---

## D-005 · Python para la ingesta y R para consumo y encuestas
**Fecha:** 2026-10-13 · **Estado:** propuesta por defecto (pendiente de confirmar)

**Decisión.** La lógica de ingesta, sincronización y marts vive en el paquete Python
`climachile` (gestionado con uv). R lee la misma caché con DuckDB/Arrow
(`R/climachile.R`) y se usa para encuestas (`survey`/`srvyr`), análisis espacial
(`sf`/`terra`) y Shiny. Así no se duplica la lógica.

---

## D-006 · Entorno de la nube preparado por un hook de arranque síncrono
**Fecha:** 2026-10-13 · **Estado:** aprobada

**Decisión.** `.claude/hooks/session-start.sh` instala lo que falte y diagnostica.
Es síncrono: la sesión espera a que termine, para evitar trabajar con un entorno
a medio instalar. Con todo ya instalado tarda unos segundos.

**Consecuencia.** Los paquetes R y las descargas de fuentes chilenas en la nube
dependen de que se amplíe la política de red del entorno (ver `docs/setup_nube.md`).

---

## D-007 · R 4.5 fijado en ambos lados y dependencias R explícitas
**Fecha:** 2026-10-13 · **Estado:** aprobada

**Contexto.** El laptop usa R 4.5 (Debian 13). Ubuntu 24.04 en la nube solo trae R 4.3,
sin los paquetes recomendados (`Matrix`). En el primer intento falló `survival` en la
nube y, en el laptop, `terra` por falta de PROJ/GDAL en el sistema.

**Decisión.**
- La nube instala R 4.5.3 desde el repositorio oficial de CRAN para Ubuntu.
- Los paquetes R se declaran en `DESCRIPTION`. renv usa el snapshot tipo `explicit`
  y `renv.lock` fija 92 paquetes.
- `R/setup.R` verifica las librerías de sistema y, si faltan, indica el `apt install`
  exacto antes de instalar nada.

---

## D-008 · Client ID propio de Google para rclone
**Fecha:** 2026-10-13 · **Estado:** aprobada (pendiente de ejecución por el usuario)

**Contexto.** rclone avisa que su client_id compartido de Google Drive se retira durante
2026 ([docs](https://rclone.org/drive/#making-your-own-client-id)). Con `drive.file`,
los archivos solo son visibles para el client_id que los creó.

**Decisión.** Crear un client_id propio (proyecto en Google Cloud, Desktop app,
scope `drive.file`, app publicada) **antes** de subir datos reales. El único archivo
creado con el client_id compartido es el de prueba: se borra y se vuelve a subir.

---

## D-009 · Procedimiento de riesgo con enfoque poblacional, a partir de la app "ESG Suite"
**Fecha:** 2026-10-14 · **Estado:** propuesta (en revisión)

**Contexto.** El usuario aportó una app corporativa de riesgo climático (React/Electron, "ESG
Suite / Climato Suite"). Se revisó su lógica de cálculo: los puntajes de amenaza por región son
estimaciones cualitativas (no datos de ARClim), el escalamiento por escenario usa elasticidades
sin fuente y las trayectorias de precio del carbono están escritas a mano.

**Decisión.** No reutilizar el código. Reutilizar su estructura conceptual: amenaza × exposición ×
vulnerabilidad, la tabla de calentamiento IPCC AR6 SPM.1, los escenarios NGFS Fase V, la
coherencia entre escenarios físicos y de transición, y el reporte del riesgo como métrica de
impacto. Todo se adapta a la comuna y a la población, con datos públicos. Detalle en
`docs/metodologia_riesgo_poblacional.md`.

**Consecuencias.** Los parámetros viven en un único `catalog/parametros.yaml`, cada uno con su
fuente y estado de verificación. La primera cadena a implementar es calor y salud.

---

## Pendientes (se decidirán más adelante)

- Caso piloto: A) calor extremo y población mayor (recomendado), B) estrés hídrico
  y sector sanitario, C) sequía y agricultura.
- Publicación web: sitio Quarto en GitHub Pages, repo público separado, salvaguardas
  antes de publicar.
- Autoría: commits firmados, releases con DOI en Zenodo, ORCID, `CITATION.cff`,
  licencias (código y contenidos), trailer `Co-Authored-By` en los commits.
- Escenarios: CMIP6 SSP1-2.6/SSP5-8.5; NGFS en una fase posterior.
- Cuenta en Copernicus CDS (ERA5).
