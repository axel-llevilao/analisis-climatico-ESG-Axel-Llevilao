# Puesta en marcha en el laptop (Debian 13 + Positron)

Requisitos ya instalados: git, R 4.5, rclone, Quarto y uv.

Librerías de sistema que necesitan los paquetes espaciales de R (`sf`, `terra`, `units`):

```bash
sudo apt install libgdal-dev libproj-dev libgeos-dev libudunits2-dev libsqlite3-dev
```

## 1. Clonar y preparar el entorno

```bash
cd ~/Documents/R
git clone https://github.com/axel-llevilao/analisis-climatico-ESG-Axel-Llevilao.git
cd analisis-climatico-ESG-Axel-Llevilao
make setup-py      # crea .venv con uv (versiones fijadas en uv.lock)
make setup-r       # instala paquetes R con renv
```

`make setup-r` instala exactamente las versiones fijadas en `renv.lock` (R 4.5,
binarios precompilados de Posit Package Manager). Los paquetes se declaran en
`DESCRIPTION`; para agregar uno, añádelo ahí y corre `make r-actualizar`.

## 2. Conectar Google Drive (una sola vez)

```bash
rclone config create gdrive drive scope drive.file   # luego sigue el paso 2b
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

## 2b. Client ID propio de Google (obligatorio desde 2026)

El client_id compartido de rclone para Google Drive se retira durante 2026
([rclone: Making your own client_id](https://rclone.org/drive/#making-your-own-client-id)).
Hay que crear uno propio. Es gratis y se hace una sola vez.

**Importante:** con el permiso `drive.file`, cada client_id solo ve los archivos que
**él mismo** creó. Lo creado con el client_id compartido deja de ser visible con el
nuevo. Por eso conviene cambiarlo **antes** de subir datos reales.

1. **Borrar los datos de prueba creados con el client_id viejo** (solo el archivo de prueba):
   ```bash
   rclone purge gdrive:climachile-data
   ```
2. **Crear el client_id** en https://console.cloud.google.com/ con tu cuenta Google:
   1. Crea un proyecto nuevo (por ejemplo `climachile`).
   2. *APIs y servicios → Habilitar APIs* → busca **Google Drive API** → *Habilitar*.
   3. *Google Auth Platform* (pantalla de consentimiento OAuth) → *Get started*:
      nombre `climachile-rclone`, tu correo como soporte, público **External**, tu
      correo como contacto → *Create*.
   4. *Data access* → *Add or remove scopes* → agrega
      `https://www.googleapis.com/auth/drive.file` → *Update* → *Save*.
   5. *Audience* → *Add users* → agrégate como usuario de prueba.
   6. *Overview* → *Create OAuth client* → tipo **Desktop app** → *Create*.
      Anota el **client ID** y el **client secret**.
   7. *Audience* → **Publish app**. Si la dejas en "Testing", el acceso expira cada
      7 días. Al conectar, Google mostrará una advertencia de "app no verificada":
      es normal para uso personal. Elige continuar.
3. **Reconfigurar rclone con el client_id nuevo**:
   ```bash
   rclone config update gdrive client_id TU_CLIENT_ID client_secret TU_CLIENT_SECRET
   rclone config reconnect gdrive:
   rclone mkdir gdrive:climachile-data
   make doctor
   ```
4. **Volver a subir el archivo de prueba** (sigue en tu caché local):
   ```bash
   make push-forzar RUTA=staging/prueba_flujo
   ```
5. **Actualizar la nube** (ver `setup_nube.md`): reemplaza `RCLONE_CONFIG_GDRIVE_TOKEN`
   por el token nuevo (`rclone config show gdrive`) y agrega dos variables más:
   ```
   RCLONE_CONFIG_GDRIVE_CLIENT_ID=TU_CLIENT_ID
   RCLONE_CONFIG_GDRIVE_CLIENT_SECRET=TU_CLIENT_SECRET
   ```

## 3. Habilitar Drive en las sesiones en la nube

Las sesiones en la nube necesitan el mismo token. Muéstralo con:

```bash
rclone config show gdrive
```

Copia el valor de `token` (el JSON completo entre llaves) y guárdalo como variable de
entorno del entorno en la nube. Instrucciones en [`setup_nube.md`](setup_nube.md).
**No lo pegues en el chat ni en ningún archivo del repo.**

## 4. Abrir en Positron

1. *File → Open Folder…* y elige `~/Documents/R/analisis-climatico-ESG-Axel-Llevilao`.
   Ábrelo siempre así: la consola arranca en la carpeta del proyecto y renv se activa
   solo (vía `.Rprofile`).
2. Arranca R. Python no arranca solo (`.vscode/settings.json`); cuando lo necesites,
   elige el intérprete `.venv` en el selector de intérpretes, arriba a la derecha.
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
