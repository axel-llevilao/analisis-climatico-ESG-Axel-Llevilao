"""Línea de comandos: `uv run climachile <comando>` (o vía `make`)."""

from __future__ import annotations

import argparse
import sys

from . import config, drive, manifiesto


def _imprimir_verificacion(res: dict[str, list[str]]) -> bool:
    print(f"  ok: {len(res['ok'])}")
    for clave in ("distinto", "faltante", "sin_registro"):
        for r in res[clave]:
            print(f"  {clave}: {r}")
    return not (res["distinto"] or res["faltante"])


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="climachile", description=__doc__)
    sub = p.add_subparsers(dest="comando", required=True)
    sub.add_parser("doctor", help="revisa herramientas y acceso a Drive")
    s = sub.add_parser("pull", help="baja desde Drive a la caché local")
    s.add_argument("ruta")
    s = sub.add_parser("push", help="sube desde la caché local a Drive")
    s.add_argument("ruta")
    s.add_argument("--forzar", action="store_true", help="permite reemplazar archivos existentes")
    s = sub.add_parser("ls", help="lista lo que hay en Drive")
    s.add_argument("ruta", nargs="?", default="")
    s = sub.add_parser("verificar", help="compara la caché local con el manifiesto")
    s.add_argument("ruta")
    a = p.parse_args(argv)

    cfg = config.cargar()
    try:
        if a.comando == "doctor":
            todo_ok = True
            for nombre, ok, detalle in drive.diagnostico(cfg):
                print(f"{'✓' if ok else '✗'} {nombre}: {detalle}")
                todo_ok &= ok
            return 0 if todo_ok else 1
        if a.comando == "pull":
            return 0 if _imprimir_verificacion(drive.pull(cfg, a.ruta)) else 1
        if a.comando == "push":
            nuevas = drive.push(cfg, a.ruta, forzar=a.forzar)
            print(f"Manifiesto: {len(nuevas)} entradas nuevas o actualizadas en {cfg.manifiesto}")
            if nuevas:
                print("Recuerda commitear ref/manifiestos/manifiesto.csv")
            return 0
        if a.comando == "ls":
            print(drive.listar(cfg, a.ruta), end="")
            return 0
        if a.comando == "verificar":
            ruta = config.validar_ruta(a.ruta)
            return (
                0
                if _imprimir_verificacion(manifiesto.verificar(cfg.manifiesto, cfg.data_dir, ruta))
                else 1
            )
    except (drive.ErrorRclone, ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
