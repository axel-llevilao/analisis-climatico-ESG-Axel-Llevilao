# Puesta en marcha en la nube (sesiones Claude Code)

Las sesiones corren en contenedores Ubuntu 24.04 **efímeros**. Al abrir una sesión,
`.claude/hooks/session-start.sh` deja el entorno listo:

1. instala rclone y R desde el archivo de Ubuntu si faltan;
2. instala Quarto (fijado en 1.6.40) desde GitHub Releases;
3. crea el entorno Python con `uv sync`;
4. instala paquetes R con renv, **si la red lo permite**;
5. configura rclone para Drive si existe el secreto `RCLONE_CONFIG_GDRIVE_TOKEN`;
6. corre `climachile doctor` e imprime avisos.

El hook es idempotente y no detiene la sesión si algo falla: solo deja avisos.

## Configuración que solo puedes hacer tú

Se hace en el menú del entorno, en la barra de título de la sesión → **Edit**.
Las sesiones nuevas toman los cambios.

### 1. Acceso a red

Estado verificado el 2026-10-13 con la política actual:

| Host | Para qué | Estado |
|---|---|---|
| pypi.org, files.pythonhosted.org | paquetes Python | permitido |
| archive.ubuntu.com | R base, rclone | permitido |
| github.com (releases) | Quarto | permitido |
| www.googleapis.com, oauth2.googleapis.com | Google Drive | permitido |
| cloud.r-project.org, packagemanager.posit.co | paquetes R | **bloqueado** |
| *.gob.cl, *.cl (INE, datos.gob.cl, etc.) | fuentes de datos chilenas | **bloqueado** |
| rclone.org, zenodo.org | documentación, publicación | **bloqueado** |

Opciones en *Network access*:
- **Acceso completo** (recomendado para este proyecto, que consulta decenas de portales públicos).
- **Limitado** con *Allow package managers* marcado y estos dominios agregados:
  `cloud.r-project.org`, `packagemanager.posit.co`, `*.gob.cl`, `*.cl`,
  `rclone.org`, `zenodo.org` (o cada dominio por separado si la configuración no admite
  comodines). Cada fuente nueva requerirá agregar su dominio.

Documentación: https://code.claude.com/docs/en/cloud-environments#network-access

### 2. Secreto de Google Drive

En **Environment variables** (o *Network secrets*, si tu versión de la app lo ofrece):

```
RCLONE_CONFIG_GDRIVE_TOKEN={"access_token":"...","token_type":"Bearer","refresh_token":"...","expiry":"..."}
```

El valor es el `token` que muestra `rclone config show gdrive` en tu laptop
(ver [`setup_local.md`](setup_local.md), paso 3). El hook agrega por su cuenta
`TYPE=drive` y `SCOPE=drive.file`.

Notas:
- rclone renueva el token de acceso en cada sesión con el `refresh_token`. Si deja de
  funcionar (por ejemplo, porque revocaste el acceso en tu cuenta Google), repite el paso 3.
- Para revocar el acceso en cualquier momento: cuenta Google → Seguridad →
  Conexiones con apps de terceros → rclone.

## Verificar

En una sesión nueva:

```bash
make doctor
```

Todo debe aparecer con ✓, incluido "acceso a Drive".
