# Puesta en marcha en el laptop (Debian 13 + Positron)

Requisitos ya instalados: git, R, rclone, Quarto. Falta `uv` si no lo tienes:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 1. Clonar y preparar el entorno

```bash
git clone https://github.com/axel-llevilao/analisis-climatico-ESG-Axel-Llevilao.git
cd analisis-climatico-ESG-Axel-Llevilao
make setup-py      # crea .venv con uv (versiones fijadas en uv.lock)
make setup-r       # instala paquetes R con renv
```

La **primera vez**, `make setup-r` crea `renv.lock`. Commitéalo y súbelo
(`git add renv.lock renv/activate.R .Rprofile && git commit -m "build: renv.lock" && git push`).
Así quedan fijadas las mismas versiones de R en el laptop y en la nube.

## 2. Conectar Google Drive (una sola vez)

```bash
rclone config create gdrive drive scope drive.file
```

Se abre el navegador para autorizar con tu cuenta Google. El permiso `drive.file`
hace que rclone **solo vea los archivos que él mismo crea**. El resto de tu Drive
(documentos de clientes, fotos, etc.) queda fuera de su alcance.

Luego crea la carpeta del proyecto y comprueba:

```bash
rclone mkdir gdrive:climachile-data
make doctor
```

Consecuencia del permiso limitado: si arrastras un archivo a `climachile-data/`
desde la web de Drive, rclone **no lo verá**. Los datos se suben siempre con `make push`.

## 3. Habilitar Drive en las sesiones en la nube

Las sesiones en la nube necesitan el mismo token. Muéstralo con:

```bash
rclone config show gdrive
```

Copia el valor de `token` (el JSON completo entre llaves) y guárdalo como variable de
entorno del entorno en la nube. Instrucciones en [`setup_nube.md`](setup_nube.md).
**No lo pegues en el chat ni en ningún archivo del repo.**

## 4. Abrir en Positron

1. *File → Open Folder…* y elige la carpeta del repo.
2. Intérprete de Python: elige `.venv` (Positron lo detecta solo).
3. R: renv se activa solo al abrir la consola (vía `.Rprofile`).
4. Prueba en la consola R:

```r
source("R/climachile.R")
con <- cc_conectar()
```

## 5. Rutina diaria

```bash
git pull
make pull RUTA=marts/<tabla>      # solo lo que necesitas
# ... trabajo ...
make push RUTA=staging/<fuente>   # datos nuevos
git add -A && git commit -m "..." && git push
```

Si una sesión en la nube dejó un PR en GitHub, revísalo y mézclalo antes de hacer `git pull`.
