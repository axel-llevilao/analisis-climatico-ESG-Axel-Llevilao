# Inicializa (o restaura) el entorno R del proyecto con renv.
# Se ejecuta con `make setup-r`. Se puede repetir sin problema.
# La primera vez crea renv.lock: commitéalo.

# Los paquetes se declaran en el archivo DESCRIPTION (campo Imports).

# --- 1. Librerías de sistema que necesitan sf/terra/units (binarios de Posit) ---------------
if (Sys.info()[["sysname"]] == "Linux") {
  libs <- c(PROJ = "libproj.so", GDAL = "libgdal.so", GEOS = "libgeos_c.so",
            UDUNITS = "libudunits2.so")
  cache <- tryCatch(system("ldconfig -p", intern = TRUE), error = function(e) character(0))
  faltan <- names(libs)[!vapply(libs, function(l) any(grepl(l, cache, fixed = TRUE)), logical(1))]
  if (length(cache) > 0 && length(faltan) > 0) {
    stop(
      "Faltan librerías de sistema: ", paste(faltan, collapse = ", "), ".\n",
      "Instálalas y vuelve a correr `make setup-r`:\n\n",
      "  sudo apt install libgdal-dev libproj-dev libgeos-dev libudunits2-dev libsqlite3-dev\n",
      call. = FALSE
    )
  }
}

# --- 2. Repositorio: binarios precompilados de Posit Package Manager -------------------------
# La URL lleva el nombre de la distribución (trixie en Debian 13, noble en Ubuntu 24.04).
codigo <- if (file.exists("/etc/os-release")) {
  os <- readLines("/etc/os-release", warn = FALSE)
  sub("^VERSION_CODENAME=", "", grep("^VERSION_CODENAME=", os, value = TRUE))
} else character(0)
options(repos = c(CRAN = if (length(codigo) == 1 && nzchar(codigo)) {
  sprintf("https://packagemanager.posit.co/cran/__linux__/%s/latest", codigo)
} else {
  "https://packagemanager.posit.co/cran/latest"
}))

# --- 3. renv ---------------------------------------------------------------------------------
if (!requireNamespace("renv", quietly = TRUE)) {
  install.packages("renv")
}

if (file.exists("renv.lock")) {
  # repos explícito: el lockfile guarda la URL del equipo que lo creó (otra distro).
  renv::restore(repos = getOption("repos"), prompt = FALSE)
} else {
  if (!file.exists("renv/activate.R")) {
    renv::init(bare = TRUE, restart = FALSE)
  } else {
    renv::load()
  }
  renv::settings$snapshot.type("explicit")
  renv::install(prompt = FALSE)          # instala lo declarado en DESCRIPTION
  renv::snapshot(prompt = FALSE)
  message("renv.lock creado: commitéalo para fijar versiones en todos los equipos.")
}
