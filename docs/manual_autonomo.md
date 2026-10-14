# Manual de operación: con y sin Claude

El proyecto **no depende de Claude para funcionar**. Todo vive en tres lugares que son tuyos:

| Pieza | Dónde vive | De qué depende |
|---|---|---|
| Código, documentación, catálogo, manifiesto | GitHub (`axel-llevilao/analisis-climatico-ESG-Axel-Llevilao`) | Tu cuenta GitHub |
| Datos | Google Drive, carpeta `climachile-data/` | Tu cuenta Google + la app `climachile-rclone` |
| Entorno de trabajo | Tu laptop: Positron, R + renv, Python + uv, rclone, Quarto | Nada externo; las versiones están fijadas en `renv.lock` y `uv.lock` |

## Dos modos, el mismo sistema

| | Con Claude (mientras pagues) | Sin Claude |
|---|---|---|
| Quién trabaja en `main` | Tú | Tú |
| Qué hace Claude | Trabaja en una rama `claude/...` en la nube y te deja un **PR** | — |
| Qué haces tú con eso | Revisas el PR en GitHub → **Merge** → `git pull` en el laptop | Nada: no llegan PR |
| Datos | Claude y tú usan el mismo Drive con `make pull/push` | Solo tú, igual que siempre |
| Revisión automática | Corre en cada PR de Claude y en cada push tuyo | Corre en cada push tuyo |

El paso de un modo al otro **no requiere cambiar nada**. Cuando dejes de pagar:
mezcla o cierra los PR abiertos de Claude (sección 1) y sigue trabajando en `main`.
Los archivos de la nube (`.claude/`, `docs/setup_nube.md`) no estorban; puedes dejarlos.

Mientras tengas Claude, conviene que todo lo que construya quede como **código que corres tú**
(`make ...`), no como pasos que solo él sabe hacer. Si alguna vez algo funciona solo cuando
Claude lo hace, pídele que lo convierta en un comando y lo documente aquí.

---

## 1. Git sin ayuda: trabaja directo en `main`

Tú trabajas siempre en `main`, sin ramas propias. Las ramas y los PR son solo de Claude.

### Ciclo de trabajo

```bash
git checkout main
git pull                       # 1. traer lo último de GitHub
# ... trabajar ...
git status                     # 2. MIRAR la lista: no deben aparecer datos
git add -A
git commit -m "qué hiciste"    # 3. guardar una versión
git push                       # 4. publicarla en GitHub
```

En Positron lo mismo se hace en el panel **Source Control** (ícono de ramas, barra izquierda):
escribes el mensaje, **Commit**, y luego **Sync Changes**.

### Errores típicos de git y cómo salir

| Situación | Qué hacer |
|---|---|
| Hiciste commit de un archivo de datos y **aún no** haces push | `git reset --soft HEAD~1`, luego `git restore --staged <archivo>`, mueve el archivo a `data/` y vuelve a hacer commit |
| Ya hiciste **push** de un archivo de datos | `git rm --cached <archivo>` → commit → push. Ojo: sigue en el historial público. Si era confidencial, considéralo expuesto |
| `git pull` dice *Your local changes would be overwritten* | `git stash` → `git pull` → `git stash pop` |
| `git push` dice *rejected (fetch first)* | Alguien (o tú desde otro equipo) subió algo antes: `git pull` y después `git push` |
| `git pull` dice *CONFLICT* | Abre el archivo en Positron: muestra los dos bloques en conflicto. Elige uno (*Accept Current / Incoming*), guarda, `git add <archivo>`, `git commit` |
| Quieres deshacer cambios no guardados en un archivo | `git restore <archivo>` |
| Quieres ver qué cambió | `git diff` (antes del add) o `git log --oneline -10` |
| Te perdiste | `git status` siempre dice dónde estás y qué hacer |

**Nunca uses** `git push --force`, `git reset --hard` ni `git clean -fd` si no sabes exactamente
qué borran.

### Los PR de Claude

Mientras uses Claude, su trabajo llega como PR desde una rama `claude/...`:

1. En GitHub → *Pull requests* → abre el PR. Mira la pestaña *Files changed* y que la
   revisión automática esté en ✓.
2. **Merge pull request** → *Confirm*.
3. En el laptop: `git checkout main` → `git pull`.

Si no quieres un PR, **Close**. Cuando dejes de pagar, mezcla o cierra los que queden.
Las ramas `claude/...` ya mezcladas se pueden borrar desde *Branches*.

---

## 2. Google Drive: cómo mantener la conexión viva

rclone usa **tu propia app de Google** (`climachile-rclone`, publicada). El acceso dura
indefinidamente salvo en estos casos:

| Causa | Síntoma | Solución |
|---|---|---|
| No usas rclone durante **6 meses** | `make doctor` → `✗ acceso a Drive` (`invalid_grant`) | `rclone config reconnect gdrive:` y autorizas en el navegador |
| Quitas el acceso en tu cuenta Google (*Seguridad → Apps de terceros*) | Igual al anterior | Igual al anterior |
| Borras o despublicas la app en console.cloud.google.com | `invalid_client` o el acceso expira cada 7 días | Vuelve a publicarla (*Audience → Publish app*); si la borraste, crea otra (`setup_local.md`, paso 2b) |

Con un `make pull` o `make push` cada pocos meses basta para que no caduque.

### Respaldo (hazlo una vez)

Guarda en tu gestor de contraseñas:

- el **client ID** y el **client secret** de la app (también se ven en
  console.cloud.google.com → proyecto `climachile` → *Clients*);
- la cuenta Google dueña del Drive.

**No guardes** `~/.config/rclone/rclone.conf` en el repo ni en Drive: contiene el token de acceso.

### Reglas que protegen los datos

- Los datos entran a Drive **solo** con `make push`. Lo que arrastres desde la web de Drive,
  rclone no lo ve (permiso `drive.file`).
- No borres ni renombres nada dentro de `climachile-data/` desde la web.
- `make push` nunca sobrescribe. Una versión nueva de una fuente va en una carpeta nueva
  (`raw/<fuente>/<version_nueva>/`).
- `make verificar RUTA=...` compara lo que tienes con el manifiesto (sha256).

---

## 3. Laptop nuevo o reinstalación

```bash
# 1. Sistema (Debian/Ubuntu)
sudo apt install git make rclone libgdal-dev libproj-dev libgeos-dev libudunits2-dev \
  libsqlite3-dev gdal-bin libabsl-dev libuv1-dev
# R 4.5, Quarto y uv: según sus sitios oficiales (r-project.org, quarto.org, docs.astral.sh/uv)

# 2. Proyecto
cd ~/Documents/R
git clone https://github.com/axel-llevilao/analisis-climatico-ESG-Axel-Llevilao.git
cd analisis-climatico-ESG-Axel-Llevilao
make setup

# 3. Drive, con el client ID y secret de tu gestor de contraseñas
rclone config create gdrive drive scope drive.file \
  client_id TU_CLIENT_ID client_secret TU_CLIENT_SECRET
make doctor

# 4. Git: identidad que no expone tu correo
git config --global user.name "Axel Llevilao"
git config --global user.email "80774967+axel-llevilao@users.noreply.github.com"
```

Al hacer `git push` la primera vez, GitHub pide autenticarte. Lo más simple es instalar
`gh` y correr `gh auth login`.

---

## 4. Agregar una fuente de datos nueva

1. **Descarga** el archivo original a `data/raw/<fuente>/<version>/`
   (por ejemplo `data/raw/siss/2024/`). `<version>` es el año o la fecha de publicación.
2. **Súbelo** a Drive: `make push RUTA=raw/<fuente>/<version>`.
3. **Regístrala** en `catalog/fuentes.yaml`: copia una entrada existente y completa URL,
   institución, cobertura, clave de unión (CUT), licencia y la fecha en que la verificaste.
4. **Límpiala** con un script (R o Python) en `analisis/` o `scripts/` que lea de `raw/` y
   escriba Parquet en `data/staging/<fuente>/`. Comprueba totales contra la cifra oficial.
5. `make push RUTA=staging/<fuente>`, y commit del script, del catálogo y del manifiesto.

Ejemplo mínimo en R para pasar un Excel a Parquet:

```r
x <- readxl::read_excel(cc_ruta("raw/siss/2024/archivo.xlsx"))   # requiere readxl en DESCRIPTION
dir.create(cc_ruta("staging/siss"), recursive = TRUE, showWarnings = FALSE)
arrow::write_parquet(x, cc_ruta("staging/siss/siss_2024.parquet"))
```

Las URLs ya verificadas están en `catalog/fuentes.yaml` y `docs/acceso_datos_estado.md`.

---

## 5. Paquetes y entorno

| Tarea | Comando |
|---|---|
| Agregar un paquete R | Añadirlo en `Imports:` de `DESCRIPTION` → `make r-actualizar` → commit de `DESCRIPTION` y `renv.lock` |
| Agregar un paquete Python | `uv add <paquete>` → commit de `pyproject.toml` y `uv.lock` |
| Actualizar todos los paquetes R | `Rscript -e 'renv::update(); renv::snapshot()'` (solo si lo necesitas; puede romper código) |
| Entorno R roto | `make setup-r` (reinstala según `renv.lock`) |
| Entorno Python roto | Borra `.venv/` y `make setup-py` |
| Revisar que el código funciona | `make check` |

Al actualizar R a una versión mayor (4.6, por ejemplo): `make setup-r` y, si falla,
`Rscript -e 'renv::snapshot()'` para refrescar el lockfile.

---

## 6. Revisión automática en GitHub

Cada `git push` dispara en GitHub la revisión `.github/workflows/check.yml`: instala el
proyecto en una máquina limpia y corre `make check` (lint + pruebas). Es gratis en repos
públicos.

- ✓ verde junto al commit (pestaña *Actions* o la lista de commits): todo bien.
- ✗ rojo: algo se rompió. Abre el detalle, lee el último error y corre `make check` en tu
  laptop para reproducirlo.

Esa revisión **no toca Drive** ni necesita claves.

---

## 7. Diagnóstico sin ayuda

Empieza siempre por:

```bash
make doctor
git status
```

| Mensaje | Causa | Solución |
|---|---|---|
| `✗ herramienta: rclone` (o R, quarto, uv) | No instalado o fuera del PATH | Instálalo (sección 3) |
| `✗ remoto rclone 'gdrive'` | rclone sin configurar | Sección 3, paso 3 |
| `✗ acceso a Drive` | Token caducado o revocado | `rclone config reconnect gdrive:` |
| `ya existe en el remoto` al hacer push | Protección contra sobrescritura | Carpeta de versión nueva, o `make push-forzar` si es intencional |
| `cannot open file 'R/climachile.R'` | Positron abrió otra carpeta | *File → Open Folder* → carpeta del proyecto |
| `there is no package called ...` | Paquete fuera de renv | Agrégalo a `DESCRIPTION` → `make r-actualizar` |
| `libproj.so...` / `libgdal...` | Faltan librerías de sistema | `sudo apt install` de la sección 3 |
| `ModuleNotFoundError` en Python | Entorno desactualizado | `make setup-py` |
| `make: command not found` | Falta make | `sudo apt install make` |

Para buscar un error en internet, copia la **última línea** del mensaje entre comillas.

---

## 8. Mantenimiento periódico

| Frecuencia | Tarea |
|---|---|
| Cada vez | `git status` antes de `git add` |
| Mensual | `make doctor` (mantiene vivo el token de Drive) |
| Cuando una fuente publica datos nuevos | Carpeta de versión nueva en `raw/`, actualiza `catalog/fuentes.yaml` (`verificado_el`) |
| Semestral | Revisa que la app `climachile-rclone` siga publicada en console.cloud.google.com |
| Al cambiar de laptop | Sección 3 |

---

## 9. Lo que nunca se hace

- Subir datos, tokens, claves o información de clientes a GitHub (el repo es **público**).
- Editar a mano `renv.lock`, `uv.lock` o `ref/manifiestos/manifiesto.csv`.
- Borrar o mover archivos de `climachile-data/` desde la web de Drive.
- Borrar la app `climachile-rclone` ni el proyecto `climachile` en Google Cloud.
- `git push --force`.
