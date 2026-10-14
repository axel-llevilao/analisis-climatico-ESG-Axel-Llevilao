"""Rutas y configuración del proyecto.

Los valores se leen, en orden de prioridad, desde variables de entorno, desde el
archivo `.env` en la raíz del repo y, si no están, desde los valores por defecto.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

# Capas permitidas en la caché local y en Drive (datos + literatura de referencia).
CAPAS = ("raw", "staging", "marts", "grids", "referencias")

REMOTO_POR_DEFECTO = "gdrive:climachile-data"


def raiz_repo(desde: Path | None = None) -> Path:
    """Busca hacia arriba la carpeta que contiene `pyproject.toml`."""
    actual = (desde or Path.cwd()).resolve()
    for carpeta in (actual, *actual.parents):
        if (carpeta / "pyproject.toml").exists() and (carpeta / "src" / "climachile").exists():
            return carpeta
    # Fallback: ubicación del paquete instalado en modo editable (src/climachile/config.py).
    return Path(__file__).resolve().parents[2]


def _leer_env(ruta: Path) -> dict[str, str]:
    valores: dict[str, str] = {}
    if not ruta.exists():
        return valores
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        valores[clave.strip()] = valor.strip().strip('"').strip("'")
    return valores


@dataclass(frozen=True)
class Config:
    raiz: Path
    data_dir: Path
    remoto: str

    @property
    def manifiesto(self) -> Path:
        return self.raiz / "ref" / "manifiestos" / "manifiesto.csv"


def cargar(desde: Path | None = None) -> Config:
    raiz = raiz_repo(desde)
    env = _leer_env(raiz / ".env")

    def valor(clave: str, defecto: str) -> str:
        return os.environ.get(clave) or env.get(clave) or defecto

    data_dir = Path(valor("CLIMACHILE_DATA_DIR", str(raiz / "data"))).expanduser()
    remoto = valor("CLIMACHILE_REMOTE", REMOTO_POR_DEFECTO).rstrip("/")
    return Config(raiz=raiz, data_dir=data_dir, remoto=remoto)


def validar_ruta(ruta: str) -> str:
    """Normaliza una ruta relativa de datos y verifica que parta en una capa válida.

    Ejemplos válidos: ``raw/ine_censo_2024``, ``marts/panel_comunal/anio=2024``.
    """
    limpia = PurePosixPath(ruta.strip().strip("/"))
    partes = limpia.parts
    if not partes or limpia.is_absolute() or ".." in partes:
        raise ValueError(f"Ruta inválida: {ruta!r}. Usa una ruta relativa, p. ej. raw/<fuente>.")
    if partes[0] not in CAPAS:
        raise ValueError(f"La ruta debe partir con una capa {CAPAS}, no con {partes[0]!r}.")
    return str(limpia)
