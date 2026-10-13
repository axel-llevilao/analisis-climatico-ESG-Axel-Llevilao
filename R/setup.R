# Inicializa (o restaura) el entorno R del proyecto con renv.
# Se ejecuta con `make setup-r`. La primera vez crea renv.lock: commitéalo.

paquetes <- c(
  "DBI", "duckdb", "arrow",      # acceso a Parquet/DuckDB
  "dplyr", "tidyr", "readr",     # manipulación
  "sf", "terra",                 # espacial
  "survey", "srvyr",             # encuestas con diseño muestral
  "quarto", "shiny", "rprojroot" # informes y visualización
)

if (!requireNamespace("renv", quietly = TRUE)) {
  install.packages("renv", repos = "https://cloud.r-project.org")
}

# Binarios precompilados de Posit Package Manager (mucho más rápido en Linux):
# la URL lleva el nombre de la distribución (p. ej. trixie en Debian 13, noble en Ubuntu 24.04).
codigo <- if (file.exists("/etc/os-release")) {
  os <- readLines("/etc/os-release", warn = FALSE)
  sub("^VERSION_CODENAME=", "", grep("^VERSION_CODENAME=", os, value = TRUE))
} else character(0)
options(repos = c(CRAN = if (length(codigo) == 1 && nzchar(codigo)) {
  sprintf("https://packagemanager.posit.co/cran/__linux__/%s/latest", codigo)
} else {
  "https://packagemanager.posit.co/cran/latest"
}))

if (file.exists("renv.lock")) {
  # repos explícito: el lockfile guarda la URL del equipo que lo creó (otra distro).
  renv::restore(repos = getOption("repos"), prompt = FALSE)
} else {
  renv::init(bare = TRUE, restart = FALSE)
  renv::install(paquetes, prompt = FALSE)
  renv::snapshot(packages = paquetes, prompt = FALSE)
  message("renv.lock creado: commitéalo para fijar versiones en todos los equipos.")
}
