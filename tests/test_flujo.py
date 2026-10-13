"""Prueba de ida y vuelta: push a un 'Drive' simulado (carpeta local vía rclone) y pull."""

import shutil

import polars as pl
import pytest

from climachile import config, db, drive, manifiesto

requiere_rclone = pytest.mark.skipif(shutil.which("rclone") is None, reason="rclone no instalado")


def _cfg(tmp_path):
    return config.Config(raiz=tmp_path, data_dir=tmp_path / "data", remoto=str(tmp_path / "drive"))


def test_validar_ruta():
    assert config.validar_ruta("/raw/ine//censo/") == "raw/ine/censo"
    for mala in ("", "otros/x", "../raw", "raw/../../etc"):
        with pytest.raises(ValueError):
            config.validar_ruta(mala)


def test_manifiesto_detecta_cambios(tmp_path):
    cfg = _cfg(tmp_path)
    archivo = cfg.data_dir / "raw" / "f" / "a.txt"
    archivo.parent.mkdir(parents=True)
    archivo.write_text("hola")
    assert len(manifiesto.registrar(cfg.manifiesto, cfg.data_dir, [archivo])) == 1
    assert manifiesto.registrar(cfg.manifiesto, cfg.data_dir, [archivo]) == []  # sin cambios
    archivo.write_text("chao")
    assert manifiesto.verificar(cfg.manifiesto, cfg.data_dir, "raw/f")["distinto"] == [
        "raw/f/a.txt"
    ]


@requiere_rclone
def test_ida_y_vuelta(tmp_path):
    cfg = _cfg(tmp_path)
    destino = cfg.data_dir / "staging" / "prueba" / "anio=2024"
    destino.mkdir(parents=True)
    pl.DataFrame({"cut": ["13101", "16101"], "valor": [1.5, 2.0]}).write_parquet(
        destino / "p.parquet"
    )

    nuevas = drive.push(cfg, "staging/prueba")
    assert [e.ruta for e in nuevas] == ["staging/prueba/anio=2024/p.parquet"]

    # Otra "sesión": caché vacía, mismo manifiesto y mismo remoto.
    shutil.rmtree(cfg.data_dir)
    res = drive.pull(cfg, "staging/prueba")
    assert res["ok"] == ["staging/prueba/anio=2024/p.parquet"]
    assert not (res["distinto"] or res["faltante"])

    con = db.conectar(cfg)
    db.registrar_vista(con, "prueba", "staging/prueba", cfg)
    filas = con.sql("select cut, anio from prueba order by cut").fetchall()
    assert filas == [("13101", 2024), ("16101", 2024)]


@requiere_rclone
def test_push_no_sobrescribe(tmp_path):
    cfg = _cfg(tmp_path)
    archivo = cfg.data_dir / "raw" / "f" / "a.txt"
    archivo.parent.mkdir(parents=True)
    archivo.write_text("versión 1")
    drive.push(cfg, "raw/f")
    archivo.write_text("versión 2, distinta")
    with pytest.raises(drive.ErrorRclone):
        drive.push(cfg, "raw/f")
    drive.push(cfg, "raw/f", forzar=True)
    assert (tmp_path / "drive" / "raw" / "f" / "a.txt").read_text() == "versión 2, distinta"
