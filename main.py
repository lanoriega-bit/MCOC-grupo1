#!/usr/bin/env python3
"""Entrada única del laboratorio MCOC: uso cotidiano, sin recalcular física.

La configuración describe rutas, no duplica datos estructurales. Los validadores
siguen siendo dueños del QA; este archivo solamente los coordina. Para ampliar
el menú, añadir un comando en COMMANDS y su función, sin modificar los modelos.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "project_config.json"


def read_json(path: Path) -> dict:
    """UTF-8 con o sin BOM, también desde editores Windows."""
    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def project_path(relative: str) -> Path:
    """No permitir que una ruta de configuración escape del repositorio."""
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f"Ruta fuera del repositorio: {relative}")
    return path


def load_config() -> dict:
    config = read_json(CONFIG)
    if config.get("schema_version") != 1:
        raise ValueError("Versión de project_config.json no soportada")
    for name in ("geometry", "sections", "materials", "loads", "results",
                 "unity", "contract", "luis_reference"):
        path = project_path(config["paths"][name])
        if not path.exists():
            raise FileNotFoundError(f"Falta {name}: {path}")
    for script in config["validators"]:
        if not project_path(script).is_file():
            raise FileNotFoundError(script)
    return config


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def properties_match_export(config: dict) -> bool:
    """Comparar propiedades con el commit fuente declarado por el exportador.

    El manifiesto de análisis actual no guarda hashes separados de materiales
    y secciones. Usar su procedencia Git explícita, sin crear un fingerprint
    nuevo que pudiera certificar entradas no analizadas. Un clon sin ese commit
    queda REVIEW REQUIRED. Comparar JSON evita falsos positivos CRLF/LF.
    """
    contract = read_json(project_path(config["paths"]["contract"]))
    commit = contract["git_commit"]
    if len(commit) != 40 or any(c not in "0123456789abcdef" for c in commit):
        return False
    try:
        for name in ("sections", "materials"):
            relative = config["paths"][name]
            original = subprocess.check_output(["git", "show", f"{commit}:{relative}"],
                                               cwd=ROOT, stderr=subprocess.PIPE)
            if json.loads(original.decode("utf-8-sig")) != read_json(project_path(relative)):
                return False
    except (OSError, subprocess.CalledProcessError, ValueError):
        return False
    return True


def show_status(config: dict) -> int:
    """Resumen calculado desde CURRENT, nunca desde conteos hardcodeados.

    La identidad rápida no reemplaza validar. Falla de forma cerrada cuando las
    fuentes o el bundle ya no corresponden al análisis guardado.
    """
    paths = {key: project_path(value) for key, value in config["paths"].items()}
    model = read_json(paths["geometry"])
    contract = read_json(paths["contract"])
    manifest = read_json(paths["results"])
    counts = Counter(row["type"] for row in model["elements"])
    stream = paths["contract"].parent
    payload = project_path(str((stream / contract["payload_file"]).relative_to(ROOT)))
    checks = {
        "properties": properties_match_export(config),
        "geometry": contract["geometry_version"] == sha256(paths["geometry"]),
        "loads": contract["loads_version"] == sha256(paths["loads"]),
        "fe": contract["fe_version"] == hashlib.sha256(
            json.dumps(model["fe_topology"], sort_keys=True).encode()).hexdigest(),
        "viewer": contract["geometry_stream_sha256"] == sha256(stream / "model_viewer.json"),
        "payload": contract["payload_sha256"] == sha256(payload),
        "status": contract["status"] == "CURRENT_VERIFIED" and manifest["status"] == "PASS",
    }
    print("MCOC — MODELO CURRENT")
    print("Elementos físicos: " + ", ".join(f"{key}={value}" for key, value in sorted(counts.items())))
    print(f"Apoyos visuales: {len(model['supports'])}")
    print(f"Análisis: {manifest['analysis_version']}; casos: {', '.join(manifest['cases'])}")
    unresolved = manifest.get("load_contract", {}).get("unresolved_load_ids", [])
    print(f"Registros de cargas sin receptor: {len(unresolved)} (no incluidos)")
    print("Identidad rápida: " + ("PASS; ejecutar validar para QA completo" if all(checks.values())
          else "STALE / REVIEW REQUIRED: " + ", ".join(k for k, v in checks.items() if not v)))
    print("Capacidad y algunos materiales/losas: supuestos de laboratorio; consultar notas QA.")
    return 0 if all(checks.values()) else 1


def show_paths(config: dict) -> int:
    """Rutas completas para abrir archivos sin buscar entre entregas antiguas."""
    for name, relative in config["paths"].items():
        print(f"{name}: {project_path(relative)}")
    print("Cómo cambiar el código: docs/GUIA_USO_Y_CAMBIOS.md")
    return 0


def validate(config: dict) -> int:
    """Fuentes, FE, equilibrio, versiones, crosswalk y bundle vigente.

    No reconstruye geometría/cargas ni ejecuta OpenSees. El segundo validador
    actualiza solamente su informe QA. No se relanza Unity ni se cierra Play.
    """
    if not properties_match_export(config):
        print("FAIL: secciones/materiales difieren del commit fuente o falta su historia Git.")
        return 1
    sources = {name: project_path(config["paths"][name]) for name in
               ("geometry", "sections", "materials", "loads", "luis_reference")}
    before = {name: sha256(path) for name, path in sources.items()}
    for script in config["validators"]:
        print(f"\nVALIDANDO: {script}", flush=True)
        completed = subprocess.run([sys.executable, str(project_path(script))], cwd=ROOT)
        if completed.returncode != 0:
            print("FAIL: revisar el error; no se recalculó el modelo.")
            return completed.returncode
    if before != {name: sha256(path) for name, path in sources.items()}:
        print("FAIL: un validador modificó una fuente o referencia protegida.")
        return 1
    print("\nPASS: fuentes intactas y CURRENT compatible. No reemplaza compile/Play de Unity.")
    return 0


def open_unity(config: dict) -> int:
    """Reutilizar el lanzador oficial, sin mantener otra copia de Unity."""
    if sys.platform != "win32":
        print(f"Abrir con Unity Hub: {project_path(config['paths']['unity'])}")
        return 0
    return subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
                           "-File", str(ROOT / "Abrir_Unity.ps1")], cwd=ROOT).returncode


COMMANDS = {"estado": show_status, "rutas": show_paths, "validar": validate, "unity": open_unity}


def menu(config: dict) -> int:
    """Menú para quienes prefieren doble clic a escribir comandos."""
    choices = {str(index): name for index, name in enumerate(COMMANDS, 1)}
    while True:
        print("\nMCOC — MENÚ DEL PROYECTO")
        for key, name in choices.items():
            print(f"{key}. {name}")
        print("0. Salir")
        selected = input("Elige una opción: ").strip()
        if selected == "0":
            return 0
        if selected in choices:
            COMMANDS[choices[selected]](config)
        else:
            print("Opción no válida.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", default="estado", choices=[*COMMANDS, "menu"])
    args = parser.parse_args(argv)
    try:
        config = load_config()
        return menu(config) if args.command == "menu" else COMMANDS[args.command](config)
    except (OSError, ValueError, KeyError, EOFError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        print("Consulta docs/GUIA_USO_Y_CAMBIOS.md. No se recalcularon resultados.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
