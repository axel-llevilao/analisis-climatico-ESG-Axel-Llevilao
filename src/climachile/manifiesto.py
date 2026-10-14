"""Manifiesto de datos: registro versionado en git de lo que existe en Drive.

Cada fila describe un archivo de datos (ruta relativa a la caché, tamaño, sha256,
fecha y equipo que lo subió). Permite saber qué hay en Drive sin listarlo y
verificar que lo descargado es idéntico a lo que se subió.
"""

from __future__ import annotations

import csv
import hashlib
import platform
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

COLUMNAS = ("ruta", "bytes", "sha256", "actualizado_utc", "equipo")


@dataclass(frozen=True)
class Entrada:
    ruta: str
    bytes: int
    sha256: str
    actualizado_utc: str
    equipo: str


def sha256(archivo: Path, bloque: int = 8 * 1024 * 1024) -> str:
    """Hash por bloques: no carga el archivo completo en memoria."""
    h = hashlib.sha256()
    with archivo.open("rb") as f:
        while trozo := f.read(bloque):
            h.update(trozo)
    return h.hexdigest()


def archivos_bajo(data_dir: Path, ruta: str) -> list[Path]:
    objetivo = data_dir / ruta
    if objetivo.is_file():
        return [objetivo]
    if objetivo.is_dir():
        return sorted(p for p in objetivo.rglob("*") if p.is_file())
    return []


def leer(manifiesto: Path) -> dict[str, Entrada]:
    if not manifiesto.exists():
        return {}
    with manifiesto.open(newline="", encoding="utf-8") as f:
        return {
            fila["ruta"]: Entrada(**{**fila, "bytes": int(fila["bytes"])})
            for fila in csv.DictReader(f)
        }


def escribir(manifiesto: Path, entradas: dict[str, Entrada]) -> None:
    manifiesto.parent.mkdir(parents=True, exist_ok=True)
    with manifiesto.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNAS)
        w.writeheader()
        for ruta in sorted(entradas):
            w.writerow(asdict(entradas[ruta]))


def registrar(manifiesto: Path, data_dir: Path, archivos: Iterable[Path]) -> list[Entrada]:
    """Agrega o actualiza en el manifiesto las entradas de los archivos dados."""
    entradas = leer(manifiesto)
    ahora = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    equipo = platform.node() or "desconocido"
    nuevas = []
    for archivo in archivos:
        ruta = archivo.relative_to(data_dir).as_posix()
        e = Entrada(ruta, archivo.stat().st_size, sha256(archivo), ahora, equipo)
        previa = entradas.get(ruta)
        if previa and previa.sha256 == e.sha256:
            continue  # sin cambios: se conserva la fecha original
        entradas[ruta] = e
        nuevas.append(e)
    escribir(manifiesto, entradas)
    return nuevas


def verificar(manifiesto: Path, data_dir: Path, ruta: str) -> dict[str, list[str]]:
    """Compara los archivos locales bajo `ruta` con el manifiesto."""
    entradas = {k: v for k, v in leer(manifiesto).items() if k == ruta or k.startswith(ruta + "/")}
    resultado: dict[str, list[str]] = {"ok": [], "distinto": [], "faltante": [], "sin_registro": []}
    for r, e in entradas.items():
        local = data_dir / r
        if not local.exists():
            resultado["faltante"].append(r)
        elif sha256(local) != e.sha256:
            resultado["distinto"].append(r)
        else:
            resultado["ok"].append(r)
    for archivo in archivos_bajo(data_dir, ruta):
        r = archivo.relative_to(data_dir).as_posix()
        if r not in entradas:
            resultado["sin_registro"].append(r)
    return resultado
