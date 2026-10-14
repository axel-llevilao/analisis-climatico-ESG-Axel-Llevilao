"""Busca repositorios en GitHub con `gh` (en el laptop) y guarda un CSV para revisarlo.

Uso: make buscar-repos   (requiere `gh auth login` hecho una vez)
Entrada: catalog/busquedas_github.txt · Salida: catalog/repos_github.csv
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ENTRADA = RAIZ / "catalog" / "busquedas_github.txt"
SALIDA = RAIZ / "catalog" / "repos_github.csv"
CAMPOS = "fullName,stargazersCount,license,pushedAt,language,description,url"
POR_BUSQUEDA = 30


def buscar(consulta: str) -> list[dict]:
    cmd = [
        "gh",
        "search",
        "repos",
        *consulta.split(),
        "--sort",
        "stars",
        "--limit",
        str(POR_BUSQUEDA),
        "--json",
        CAMPOS,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"  aviso: falló '{consulta}': {res.stderr.strip()[:200]}", file=sys.stderr)
        return []
    return json.loads(res.stdout or "[]")


def main() -> int:
    consultas = [
        linea.strip()
        for linea in ENTRADA.read_text(encoding="utf-8").splitlines()
        if linea.strip() and not linea.lstrip().startswith("#")
    ]
    repos: dict[str, dict] = {}
    for c in consultas:
        print(f"buscando: {c}")
        for r in buscar(c):
            fila = repos.setdefault(
                r["fullName"],
                {
                    "repo": r["fullName"],
                    "estrellas": r.get("stargazersCount", 0),
                    "licencia": (r.get("license") or {}).get("key", ""),
                    "ultimo_push": (r.get("pushedAt") or "")[:10],
                    "lenguaje": r.get("language") or "",
                    "descripcion": " ".join((r.get("description") or "").split())[:300],
                    "url": r.get("url", ""),
                    "busquedas": [],
                },
            )
            fila["busquedas"].append(c)
    filas = sorted(repos.values(), key=lambda f: -int(f["estrellas"] or 0))
    for f in filas:
        f["busquedas"] = " | ".join(f["busquedas"])
    with SALIDA.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]) if filas else ["repo"])
        w.writeheader()
        w.writerows(filas)
    print(f"{len(filas)} repositorios únicos en {SALIDA.relative_to(RAIZ)}")
    return 0 if filas else 1


if __name__ == "__main__":
    sys.exit(main())
