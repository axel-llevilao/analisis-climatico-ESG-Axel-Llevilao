# Puesta en marcha en la Steam Deck (SteamOS)

SteamOS es un sistema **inmutable**: no hay `apt`, no se usa `sudo` para instalar y todo lo
que se instala vive en el home (`/home/deck`). Por eso en la Deck el proyecto funciona distinto
que en el laptop con Debian:

| | Laptop (Debian) | Steam Deck |
|---|---|---|
| R | R 4.5 del sistema + **renv** (`renv.lock`) | R de **micromamba** (conda-forge), sin renv |
| Paquetes R | `make setup-r` | `micromamba install -n r r-<paquete>` |
| Python | `uv sync` | `uv sync` con Python administrado por uv |
| Herramientas | `apt` | entorno micromamba `herramientas` |

El `renv.lock` sigue siendo la referencia del proyecto (laptop y nube). **La Deck no lo modifica.**

## 1. Herramientas (una sola vez)

Requiere micromamba en `~/.local/bin` y el entorno `r` creado.

```bash
micromamba create -y -n herramientas -c conda-forge git gh uv rclone quarto make
for t in git gh uv uvx rclone quarto make; do
  printf '#!/usr/bin/env bash\nexec "%s/micromamba/envs/herramientas/bin/%s" "$@"\n' "$HOME" "$t" > ~/.local/bin/$t
  chmod +x ~/.local/bin/$t
done
for t in R Rscript; do
  printf '#!/usr/bin/env bash\nexec "%s/micromamba/envs/r/bin/%s" "$@"\n' "$HOME" "$t" > ~/.local/bin/$t
  chmod +x ~/.local/bin/$t
done
```

## 2. R sin renv

Paquetes de `DESCRIPTION`, desde conda-forge (ya compilados, con GDAL/PROJ incluidos):

```bash
micromamba install -y -n r -c conda-forge \
  r-dbi r-duckdb r-arrow r-dplyr r-tidyr r-readr r-sf r-terra \
  r-survey r-srvyr r-quarto r-shiny r-rprojroot
```

Desactivar renv **solo en la Deck** (no toca el repo):

```bash
echo 'RENV_CONFIG_AUTOLOADER_ENABLED=FALSE' >> ~/.Renviron
```

Con renv desactivado, R carga `~/.Rprofile`. Ahí deben fijarse las rutas de datos que necesitan
`sf`, `terra` y `units`, porque Positron abre R sin activar el entorno de micromamba:

```r
local({
  prefix <- normalizePath(file.path(R.home(), "..", ".."), mustWork = FALSE)
  fijar <- function(var, ruta) if (!nzchar(Sys.getenv(var)) && file.exists(ruta))
    do.call(Sys.setenv, setNames(list(ruta), var))
  fijar("PROJ_DATA", file.path(prefix, "share", "proj"))
  fijar("GDAL_DATA", file.path(prefix, "share", "gdal"))
  fijar("UDUNITS2_XML_PATH", file.path(prefix, "share", "udunits", "udunits2.xml"))
})
```

## 3. Python

```bash
cd ~/Projects/R/analisis-climatico-ESG-Axel-Llevilao
UV_PYTHON_PREFERENCE=only-managed uv sync --python 3.13
```

Se usa el Python que descarga uv (en el home) y no el de SteamOS, que cambia con cada actualización.

## 4. GitHub y Google Drive

```bash
gh auth login          # GitHub.com → HTTPS → Login with a web browser
gh auth setup-git
```

Drive, con el client ID y secret de la app `climachile-rclone` (ver `setup_local.md`, paso 2b).
Los valores se piden por teclado para que no queden en el historial:

```bash
read -rp "Client ID: " CID; read -rsp "Client secret: " CSEC; echo
rclone config create gdrive drive scope drive.file client_id "$CID" client_secret "$CSEC"
unset CID CSEC
make doctor
```

Hay que usar **el mismo client ID** de siempre: con `drive.file`, otro client ID no ve los datos.

## 5. Si copiaste el repo desde otro equipo

Copiar con un pendrive suele marcar todos los archivos como ejecutables, y git los muestra
como modificados. Para devolver los permisos originales:

```bash
git diff --summary | grep 'mode change 100644 => 100755' \
  | sed 's/^ mode change 100644 => 100755 //' | xargs -d '\n' chmod -x
git status --short   # debe quedar vacío
```

## 6. Positron

Abrir la carpeta del proyecto con *File → Open Folder…*. Positron debe tener en su
configuración `"positron.r.customBinaries": ["/home/deck/micromamba/envs/r/bin/R"]`.
Para Python, elegir **.venv** en el selector de intérpretes.

## Qué no hacer en la Deck

| No hagas | Por qué | En su lugar |
|---|---|---|
| `make setup-r`, `make setup` | Activan renv con R 4.5 de Debian | Sección 2 |
| `make r-actualizar`, `renv::snapshot()` | Reescriben `renv.lock` con versiones de la Deck | Agregar el paquete a `DESCRIPTION` y actualizar el lockfile desde el laptop o la nube |
| `sudo apt install ...`, `sudo pacman ...` | SteamOS no lo permite o lo borra al actualizar | `micromamba install` |

`make pull`, `make push`, `make ls`, `make check` y `make doctor` funcionan igual que en el laptop.

## Diagnóstico

| Síntoma | Solución |
|---|---|
| `✗ herramienta: R: no encontrada` | Sección 1 (accesos `R` y `Rscript` en `~/.local/bin`) |
| `there is no package called ...` | `micromamba install -n r r-<paquete>` |
| `sf`/`terra` avisan que no encuentran `proj.db` | Revisar el `~/.Rprofile` de la sección 2 |
| `.venv` roto tras actualizar SteamOS | Sección 3 |
| `Permission denied` al correr un comando de `~/.local/bin` | `chmod +x ~/.local/bin/<comando>` |
