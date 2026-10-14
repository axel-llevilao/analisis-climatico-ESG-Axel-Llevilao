# Guía rápida

Todo se hace desde `~/Documents/R/analisis-climatico-ESG-Axel-Llevilao`, abierto en
Positron con **File → Open Folder**. Los comandos `git` y `make` van en la terminal de
Positron (*Terminal → New Terminal*).

---

## Qué hacer y cuándo

### Al empezar a trabajar
```bash
git checkout main
git pull                              # trae lo último de GitHub
make pull RUTA=marts/<tabla>          # baja de Drive solo los datos que vas a usar
```

### Mientras trabajas (consola R)
```r
source("R/climachile.R")
con <- cc_conectar()
cc_vista(con, "x", "staging/<fuente>")
DBI::dbGetQuery(con, "select * from x limit 10")
```

### Al terminar
```bash
make push RUTA=<capa>/<lo_que_creaste>   # solo si generaste o agregaste datos
git status                               # REVISA que no aparezcan archivos de datos
git add -A
git commit -m "qué hiciste, en una línea"
git push
```

### Situaciones frecuentes

| Quiero… | Hago… |
|---|---|
| Empezar un análisis nuevo | `cp -r analisis/_plantilla analisis/AAAA-MM_nombre` |
| Usar un archivo que ya tengo en el laptop | Copiarlo a `data/raw/<fuente>/<version>/` y luego `make push RUTA=raw/<fuente>` |
| Saber qué hay en Drive | `make ls` o abrir `ref/manifiestos/manifiesto.csv` |
| Usar Python | Selector de intérpretes (arriba a la derecha) → **Python (.venv)**; o `uv run python script.py` |
| Agregar un paquete R | Añadirlo en `Imports:` de `DESCRIPTION` → `make r-actualizar` → commit |
| Agregar un paquete Python | `uv add <paquete>` → commit de `pyproject.toml` y `uv.lock` |
| Integrar algo que hizo Claude | Revisar el PR en GitHub → **Merge** → `git pull` |
| Algo no funciona | `make doctor` y pegarle la salida a Claude |
| Reinstalar el entorno | `make setup` |

---

## Qué NO hacer

| No… | Porque… |
|---|---|
| Abrir `~/Documents/R` en vez de la carpeta del proyecto | R arranca en el lugar equivocado y sin renv |
| Guardar datos fuera de `data/` | Podrían terminar en GitHub, que es público |
| Hacer `git add` sin mirar antes `git status` | Es la única forma de ver qué se va a publicar |
| Subir archivos a Drive arrastrándolos desde la web | rclone no los ve (permiso `drive.file`) |
| Borrar, renombrar o mover archivos en `climachile-data/` desde la web de Drive | Rompe el manifiesto y los análisis que dependen de esos archivos |
| Usar `make push-forzar` sin estar seguro | Reemplaza en Drive un archivo que ya existía |
| Modificar algo dentro de `data/raw/` | `raw` es el original de la fuente; las versiones nuevas van en una carpeta nueva |
| Instalar paquetes con `install.packages()` o `pip install` | No quedan registrados y la nube no los tendrá; usa `DESCRIPTION` o `uv add` |
| Trabajar con datos de clientes en este repo | El repo es público; los clientes van en otro repo privado |
| Pegar tokens o claves en el chat, en archivos o en commits | Dan acceso a tu Drive |

---

## Lo que no se toca nunca

Estos archivos y carpetas los mantiene el sistema (o Claude, cuando se lo pidas):

| Archivo o carpeta | Qué es |
|---|---|
| `renv.lock`, `renv/`, `.Rprofile` | Versiones exactas de los paquetes R |
| `uv.lock`, `.venv/` | Versiones exactas de los paquetes Python |
| `src/climachile/`, `R/climachile.R`, `R/setup.R` | Código de la plataforma |
| `Makefile`, `tests/` | Comandos y pruebas |
| `.claude/`, `.vscode/`, `.gitignore` | Arranque de la nube, configuración de Positron, protección de datos |
| `ref/manifiestos/manifiesto.csv` | Lo actualiza `make push`; solo se commitea, no se edita |
| `docs/index.html`, `docs/privacidad.html` | Páginas que exige Google para la app de Drive |
| `~/.config/rclone/rclone.conf` | Tus credenciales de Drive (fuera del proyecto) |
| La app `climachile-rclone` en console.cloud.google.com | Si se borra o se despublica, se corta el acceso a Drive |
| Las variables `RCLONE_CONFIG_GDRIVE_*` del entorno en claude.ai/code | Acceso de la nube a Drive |

Si crees que hay que cambiar algo de esta lista, pídeselo a Claude.

---

## Dónde va cada cosa

| Tipo de contenido | Carpeta | ¿Va a GitHub? | ¿Va a Drive? |
|---|---|---|---|
| Datos originales | `data/raw/<fuente>/<version>/` | No | Sí, con `make push` |
| Datos limpios (Parquet) | `data/staging/<fuente>/` | No | Sí, con `make push` |
| Tablas integradas | `data/marts/<tabla>/` | No | Sí, con `make push` |
| Tus análisis (código, `.qmd`, notas) | `analisis/<AAAA-MM_nombre>/` | Sí | No |
| Documentación | `docs/` | Sí | No |
| Tablas de referencia pequeñas | `ref/` | Sí | No |

---

## Si algo sale mal

| Síntoma | Solución |
|---|---|
| `cannot open file 'R/climachile.R'` | Abriste otra carpeta. File → Open Folder → la carpeta del proyecto |
| `Falta el paquete duckdb` | `make setup-r` |
| `make push` dice que el archivo ya existe | Es la protección contra sobrescritura. Usa otra carpeta de versión o, si es intencional, `make push-forzar` |
| `✗ acceso a Drive` | `rclone config reconnect gdrive:` y luego actualizar el token en la nube |
| `git pull` se queja de cambios locales | No fuerces nada; pégale el mensaje a Claude |
| Positron arranca en Python | Cierra esa consola y elige R en el selector de intérpretes |
