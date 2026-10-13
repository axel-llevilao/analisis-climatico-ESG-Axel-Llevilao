"""Sincronización de la caché local de datos con Google Drive vía rclone.

Reglas:
- `push` nunca sobrescribe en Drive un archivo existente con contenido distinto
  (usa `rclone --immutable`); para reemplazar hay que pedirlo explícitamente.
- `pull` y `push` copian, nunca borran (no se usa `rclone sync`).
- Todo `push` actualiza el manifiesto versionado en git.
"""

from __future__ import annotations

import json
import shutil
import subprocess

from . import manifiesto
from .config import Config, validar_ruta


class ErrorRclone(RuntimeError):
    pass


def _rclone(*args: str, capturar: bool = False) -> subprocess.CompletedProcess[str]:
    if shutil.which("rclone") is None:
        raise ErrorRclone("rclone no está instalado. Ver docs/setup_local.md o docs/setup_nube.md.")
    try:
        return subprocess.run(["rclone", *args], check=True, text=True, capture_output=capturar)
    except subprocess.CalledProcessError as e:
        detalle = (e.stderr or "").strip() if capturar else ""
        raise ErrorRclone(
            f"rclone {' '.join(args[:1])} falló (código {e.returncode}). {detalle}"
        ) from e


def _destino(cfg: Config, ruta: str) -> str:
    return f"{cfg.remoto}/{ruta}"


def nombre_remoto(cfg: Config) -> str | None:
    """`gdrive:climachile-data` -> `gdrive`; rutas locales (tests) -> None."""
    if ":" in cfg.remoto and not cfg.remoto.startswith("/"):
        return cfg.remoto.split(":", 1)[0]
    return None


def es_directorio_remoto(cfg: Config, ruta: str) -> bool:
    salida = _rclone("lsjson", "--stat", _destino(cfg, ruta), capturar=True).stdout
    return bool(json.loads(salida).get("IsDir"))


def push(cfg: Config, ruta: str, forzar: bool = False) -> list[manifiesto.Entrada]:
    ruta = validar_ruta(ruta)
    local = cfg.data_dir / ruta
    if not local.exists():
        raise FileNotFoundError(f"No existe {local}")
    opciones = [] if forzar else ["--immutable"]
    comando = "copyto" if local.is_file() else "copy"
    _rclone(comando, str(local), _destino(cfg, ruta), *opciones, "--stats-one-line", "-v")
    return manifiesto.registrar(
        cfg.manifiesto, cfg.data_dir, manifiesto.archivos_bajo(cfg.data_dir, ruta)
    )


def pull(cfg: Config, ruta: str) -> dict[str, list[str]]:
    ruta = validar_ruta(ruta)
    local = cfg.data_dir / ruta
    if es_directorio_remoto(cfg, ruta):
        local.mkdir(parents=True, exist_ok=True)
        _rclone("copy", _destino(cfg, ruta), str(local), "--stats-one-line", "-v")
    else:
        local.parent.mkdir(parents=True, exist_ok=True)
        _rclone("copyto", _destino(cfg, ruta), str(local), "--stats-one-line", "-v")
    return manifiesto.verificar(cfg.manifiesto, cfg.data_dir, ruta)


def listar(cfg: Config, ruta: str = "") -> str:
    destino = _destino(cfg, validar_ruta(ruta)) if ruta else cfg.remoto
    return _rclone("lsf", "-R", "--max-depth", "3", destino, capturar=True).stdout


def diagnostico(cfg: Config) -> list[tuple[str, bool, str]]:
    """Revisa herramientas y conexión. Devuelve (chequeo, ok, detalle)."""
    res: list[tuple[str, bool, str]] = []
    for herramienta in ("rclone", "R", "quarto", "uv", "git"):
        ruta = shutil.which(herramienta)
        res.append((f"herramienta: {herramienta}", ruta is not None, ruta or "no encontrada"))
    res.append(("caché local", True, str(cfg.data_dir)))
    if shutil.which("rclone") is None:
        return res
    nombre = nombre_remoto(cfg)
    if nombre:
        remotos = _rclone("listremotes", capturar=True).stdout.split()
        configurado = f"{nombre}:" in remotos
        res.append(
            (
                f"remoto rclone '{nombre}'",
                configurado,
                "configurado" if configurado else "falta configurar (ver docs)",
            )
        )
        if not configurado:
            return res
    try:
        _rclone("lsf", "--max-depth", "1", cfg.remoto, capturar=True)
        res.append(("acceso a Drive", True, cfg.remoto))
    except ErrorRclone as e:
        res.append(("acceso a Drive", False, str(e)[:200]))
    return res
