# Funciones R para trabajar con la caché de datos del proyecto desde Positron.
#
# Uso:
#   source("R/climachile.R")
#   con <- cc_conectar()
#   cc_vista(con, "panel", "marts/panel_comunal")
#   DBI::dbGetQuery(con, "select * from panel limit 10")
#
# La ingesta y la sincronización con Drive se hacen desde Python/Makefile
# (`make pull RUTA=...`); R solo consume los Parquet de la caché local.

cc_raiz <- function(desde = getwd()) {
  actual <- normalizePath(desde, mustWork = TRUE)
  repeat {
    if (file.exists(file.path(actual, "pyproject.toml")) &&
        dir.exists(file.path(actual, "src", "climachile"))) {
      return(actual)
    }
    padre <- dirname(actual)
    if (identical(padre, actual)) stop("No encontré la raíz del repo climachile.")
    actual <- padre
  }
}

cc_leer_env <- function(raiz = cc_raiz()) {
  ruta <- file.path(raiz, ".env")
  if (!file.exists(ruta)) return(list())
  lineas <- trimws(readLines(ruta, warn = FALSE))
  lineas <- lineas[nzchar(lineas) & !startsWith(lineas, "#") & grepl("=", lineas)]
  claves <- trimws(sub("=.*$", "", lineas))
  valores <- trimws(sub("^[^=]*=", "", lineas))
  valores <- gsub("^['\"]|['\"]$", "", valores)
  stats::setNames(as.list(valores), claves)
}

cc_data_dir <- function(raiz = cc_raiz()) {
  desde_entorno <- Sys.getenv("CLIMACHILE_DATA_DIR", unset = "")
  if (nzchar(desde_entorno)) return(path.expand(desde_entorno))
  env <- cc_leer_env(raiz)
  if (!is.null(env$CLIMACHILE_DATA_DIR)) return(path.expand(env$CLIMACHILE_DATA_DIR))
  file.path(raiz, "data")
}

cc_ruta <- function(ruta) {
  capas <- c("raw", "staging", "marts", "grids")
  ruta <- gsub("^/+|/+$", "", ruta)
  if (!(strsplit(ruta, "/")[[1]][1] %in% capas) || grepl("\\.\\.", ruta)) {
    stop("La ruta debe partir con una capa: ", paste(capas, collapse = ", "))
  }
  file.path(cc_data_dir(), ruta)
}

cc_conectar <- function(memoria_max = "6GB") {
  if (!requireNamespace("duckdb", quietly = TRUE)) {
    stop("Falta el paquete duckdb. Ejecuta `make setup-r` (instala con renv).")
  }
  tmp <- file.path(cc_data_dir(), ".duckdb_tmp")
  dir.create(tmp, recursive = TRUE, showWarnings = FALSE)
  con <- DBI::dbConnect(duckdb::duckdb())
  DBI::dbExecute(con, sprintf("SET memory_limit = '%s'", memoria_max))
  DBI::dbExecute(con, sprintf("SET temp_directory = '%s'", tmp))
  con
}

cc_vista <- function(con, nombre, ruta) {
  stopifnot(grepl("^[A-Za-z_][A-Za-z0-9_]*$", nombre))
  base <- cc_ruta(ruta)
  patron <- if (file.exists(base) && !dir.exists(base)) base else file.path(base, "**", "*.parquet")
  patron <- gsub("'", "''", patron)
  DBI::dbExecute(con, sprintf(
    "CREATE OR REPLACE VIEW %s AS SELECT * FROM read_parquet('%s', hive_partitioning = true)",
    nombre, patron
  ))
  invisible(nombre)
}
