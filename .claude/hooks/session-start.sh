#!/bin/bash
# Arranque de sesiones Claude Code en la nube: deja el entorno listo para trabajar.
# Idempotente y no interactivo. En el laptop no hace nada (ver docs/setup_local.md).
set -uo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}"
avisos=()
alcanza() { curl -sS -o /dev/null -m 10 "$1" 2>/dev/null; }

# 1. Herramientas de sistema.
# R se fija en la misma versión menor que renv.lock (4.5), desde el repositorio de CRAN
# para Ubuntu; el archivo de Ubuntu 24.04 solo trae R 4.3.
R_APT_VERSION=4.5.3-1.2404.0
if [ ! -f /etc/apt/sources.list.d/cran.list ] && alcanza https://cloud.r-project.org; then
  curl -fsSL https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc \
    -o /etc/apt/keyrings/cran.asc &&
  echo "deb [signed-by=/etc/apt/keyrings/cran.asc] https://cloud.r-project.org/bin/linux/ubuntu noble-cran40/" \
    >/etc/apt/sources.list.d/cran.list
fi
faltan=()
command -v rclone >/dev/null || faltan+=(rclone)
if [ "$(dpkg-query -W -f='${Version}' r-base-core 2>/dev/null)" != "$R_APT_VERSION" ]; then
  faltan+=("r-base-core=$R_APT_VERSION" "r-recommended=$R_APT_VERSION")
fi
# Librerías de sistema para sf/terra/units.
for p in libgdal-dev libproj-dev libgeos-dev libudunits2-dev libsqlite3-dev; do
  dpkg -s "$p" >/dev/null 2>&1 || faltan+=("$p")
done
if [ ${#faltan[@]} -gt 0 ]; then
  echo "Instalando: ${faltan[*]}"
  if ! (apt-get update -qq && DEBIAN_FRONTEND=noninteractive \
        apt-get install -y -qq --no-install-recommends --allow-downgrades "${faltan[@]}") \
        >/dev/null 2>&1; then
    avisos+=("no se pudo instalar ${faltan[*]} con apt")
  fi
fi

# 2. Quarto (se descarga de GitHub Releases; requiere ese dominio en la red del entorno).
QUARTO_VERSION=1.6.40
if ! command -v quarto >/dev/null; then
  deb="/tmp/quarto-${QUARTO_VERSION}.deb"
  url="https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.deb"
  if curl -fsSL -m 120 -o "$deb" "$url" && dpkg -i "$deb" >/dev/null 2>&1; then
    echo "Quarto ${QUARTO_VERSION} instalado"
  else
    avisos+=("Quarto no instalado: la red del entorno bloquea github.com/…/releases")
  fi
fi

# 3. Entorno Python (uv.lock).
if ! uv sync --quiet; then
  avisos+=("uv sync falló")
fi

# 4. Paquetes R (renv) solo si CRAN / Posit Package Manager son alcanzables.
if alcanza https://packagemanager.posit.co || alcanza https://cloud.r-project.org; then
  Rscript R/setup.R >/tmp/renv-setup.log 2>&1 || avisos+=("renv falló; ver /tmp/renv-setup.log")
else
  avisos+=("paquetes R no instalados: la red bloquea CRAN y Posit Package Manager")
fi

# 5. Google Drive vía rclone: el token llega como variable de entorno secreta.
if [ -n "${RCLONE_CONFIG_GDRIVE_TOKEN:-}" ] && [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  {
    echo "export RCLONE_CONFIG_GDRIVE_TYPE=drive"
    echo "export RCLONE_CONFIG_GDRIVE_SCOPE=drive.file"
  } >>"$CLAUDE_ENV_FILE"
  export RCLONE_CONFIG_GDRIVE_TYPE=drive RCLONE_CONFIG_GDRIVE_SCOPE=drive.file
else
  avisos+=("Drive sin configurar: falta la variable RCLONE_CONFIG_GDRIVE_TOKEN (ver docs/setup_nube.md)")
fi

echo "--- climachile: diagnóstico ---"
uv run --quiet climachile doctor || true
for a in "${avisos[@]}"; do echo "AVISO: $a"; done
exit 0
