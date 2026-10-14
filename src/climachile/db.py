"""Acceso a los datos de la caché local con DuckDB (lectura lazy, sin cargar todo en RAM).

Uso típico en Positron o en un análisis:

    from climachile import db
    con = db.conectar()
    db.registrar_vista(con, "panel", "marts/panel_comunal")
    con.sql("select region, sum(poblacion) from panel group by 1").pl()
"""

from __future__ import annotations

import re

import duckdb

from .config import Config, cargar, validar_ruta


def conectar(cfg: Config | None = None, memoria_max: str = "6GB") -> duckdb.DuckDBPyConnection:
    """Conexión en memoria con límite de RAM y spill a disco en la caché local."""
    cfg = cfg or cargar()
    tmp = cfg.data_dir / ".duckdb_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"SET memory_limit = '{memoria_max}'")
    con.execute(f"SET temp_directory = '{tmp.as_posix()}'")
    return con


def registrar_vista(
    con: duckdb.DuckDBPyConnection, nombre: str, ruta: str, cfg: Config | None = None
) -> None:
    """Crea una vista sobre todos los Parquet bajo `ruta` (con particiones hive)."""
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nombre):
        raise ValueError(f"Nombre de vista inválido: {nombre!r}")
    cfg = cfg or cargar()
    base = cfg.data_dir / validar_ruta(ruta)
    patron = str(base) if base.is_file() else f"{base}/**/*.parquet"
    patron = patron.replace("'", "''")
    con.execute(
        f"CREATE OR REPLACE VIEW {nombre} AS "
        f"SELECT * FROM read_parquet('{patron}', hive_partitioning = true)"
    )
