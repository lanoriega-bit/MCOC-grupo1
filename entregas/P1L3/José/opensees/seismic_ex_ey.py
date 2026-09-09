"""Sismo pseudo-estatico EX/EY para P1L2 (Integrante B).

Construye la informacion por piso (masa y centro de masa desde los
poligonos tributarios) y aplica las dos solicitaciones laterales
independientes EX y EY con un patron lateral parametrizado.

Trabaja en unidades SI: m, kN, N, Pa. Las cargas de losa vienen del
JSON de areas tributarias versionado en StreamingAssets.

Todos los parametros del enunciado quedan en PARAMETERS y pueden
sobrescribirse con un archivo JSON usando --config. De esa forma el
profesor puede entregar despues valores especificos (porcentaje de Q,
patron, corte basal) sin tocar el codigo.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

URL_TRIBUTARY = Path(__file__).resolve().parents[3] / "UnityViewer" / "Assets" / "StreamingAssets" / "tributary_areas.json"
UNITY_EXPORT = Path(__file__).resolve().parents[3] / "UnityViewer" / "Assets" / "StreamingAssets" / "seismic_ex_ey.json"
RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"

G = 9.81  # m/s2

DEFAULT_PARAMETERS = {
    "g": 9.81,
    "psi_G": 1.0,
    "psi_Q": 0.5,
    "qQ_kN_m2": 2.452,
    "base_shear_mode": "coefficient",
    "base_shear_coefficient": 0.10,
    "base_shear_EX_kN": None,
    "base_shear_EY_kN": None,
    "pattern": {
        "exponent_k": 1.0,
    },
    "accidental_eccentricity_ratio": 0.05,
    "levels_z_m": {
        "S1": 3.92,
        "P1": 7.88,
        "P2": 11.84,
        "P3": 15.80,
        "P4": 19.76,
    },
}

BUILDINGS = ("EDIFICIO_1", "EDIFICIO_2")


def polygon_centroid(polygon: list[dict]) -> tuple[float, float]:
    n = len(polygon)
    if n == 0:
        return 0.0, 0.0
    if n < 3:
        px = sum(pt["x"] for pt in polygon) / n
        py = sum(pt["y"] for pt in polygon) / n
        return px, py
    area2 = 0.0
    cx = 0.0
    cy = 0.0
    for i in range(n):
        x0, y0 = polygon[i]["x"], polygon[i]["y"]
        x1, y1 = polygon[(i + 1) % n]["x"], polygon[(i + 1) % n]["y"]
        cross = x0 * y1 - x1 * y0
        area2 += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    if abs(area2) < 1e-9:
        px = sum(pt["x"] for pt in polygon) / n
        py = sum(pt["y"] for pt in polygon) / n
        return px, py
    return cx / (3.0 * area2), cy / (3.0 * area2)


def polygon_centroid_area(polygon: list[dict]) -> tuple[float, float, float]:
    n = len(polygon)
    if n == 0:
        return 0.0, 0.0, 0.0
    if n < 3:
        px = sum(pt["x"] for pt in polygon) / n
        py = sum(pt["y"] for pt in polygon) / n
        return px, py, 0.0
    a2 = 0.0
    cx = 0.0
    cy = 0.0
    for i in range(n):
        x0, y0 = polygon[i]["x"], polygon[i]["y"]
        x1, y1 = polygon[(i + 1) % n]["x"], polygon[(i + 1) % n]["y"]
        cross = x0 * y1 - x1 * y0
        a2 += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    area = a2 / 2.0
    if abs(area) < 1e-9:
        px = sum(pt["x"] for pt in polygon) / n
        py = sum(pt["y"] for pt in polygon) / n
        return px, py, 0.0
    return cx / (6.0 * area), cy / (6.0 * area), area


def load_tributary(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_floors(tributary: dict, parameters: dict) -> dict[str, list[dict]]:
    qg = tributary["qG_kN_m2"]
    levels_z = parameters["levels_z_m"]
    floors_by_building: dict[str, list[dict]] = {b: [] for b in BUILDINGS}
    by_key: dict[tuple[str, str], list[dict]] = {}
    for area in tributary["areas"]:
        key = (area["building"], area["floor"])
        by_key.setdefault(key, []).append(area)

    area_by = {b: 0.0 for b in BUILDINGS}
    for building in BUILDINGS:
        area_by[building] = sum(a["area_m2"] for a in tributary["areas"] if a["building"] == building)

    for building in BUILDINGS:
        keys = sorted((k for k in by_key if k[0] == building), key=lambda k: levels_z.get(k[1], 0.0))
        for (b, floor) in keys:
            parts = by_key[(b, floor)]
            total_area = sum(p["area_m2"] for p in parts)
            cm_x = 0.0
            cm_y = 0.0
            for part in parts:
                cx, cy, area = polygon_centroid_area(part["polygon"])
                cm_x += area * cx
                cm_y += area * cy
            cm_x /= total_area
            cm_y /= total_area
            xs = [pt["x"] for part in parts for pt in part["polygon"]]
            ys = [pt["y"] for part in parts for pt in part["polygon"]]
            w_g = qg * total_area
            w_q = parameters["qQ_kN_m2"] * total_area
            w_simic = parameters["psi_G"] * w_g + parameters["psi_Q"] * w_q
            floors_by_building[building].append(
                {
                    "building": building,
                    "floor": floor,
                    "z_m": levels_z.get(floor, 0.0),
                    "area_m2": total_area,
                    "wG_kN": w_g,
                    "wQ_kN": w_q,
                    "w_seismic_kN": w_simic,
                    "mass_ton": w_simic / parameters["g"],
                    "cm_x": cm_x,
                    "cm_y": cm_y,
                    "Lx_m": max(xs) - min(xs),
                    "Ly_m": max(ys) - min(ys),
                }
            )
    return floors_by_building


def base_shear(building_name: str, total_w: float, parameters: dict) -> tuple[float | None, float | None]:
    mode = parameters["base_shear_mode"]
    if mode == "explicit":
        return parameters["base_shear_EX_kN"], parameters["base_shear_EY_kN"]
    c = parameters["base_shear_coefficient"]
    if c is None:
        return None, None
    return c * total_w, c * total_w


def distribute(v: float | None, floors: list[dict], parameters: dict) -> list[float]:
    if v is None:
        return [0.0] * len(floors)
    k = parameters["pattern"]["exponent_k"]
    denominator = sum(
        f["w_seismic_kN"] * (f["z_m"] ** k) for f in floors if (f["z_m"] ** k) > 0.0
    )
    if denominator <= 0.0:
        denom2 = sum(f["w_seismic_kN"] for f in floors)
        return [v * f["w_seismic_kN"] / denom2 for f in floors]
    return [v * (f["w_seismic_kN"] * (f["z_m"] ** k)) / denominator for f in floors]


def apply_case(floors: list[dict], forces: list[float], direction: str, parameters: dict) -> list[dict]:
    result = []
    ratio = parameters["accidental_eccentricity_ratio"]
    for f, fi in zip(floors, forces):
        perp = f["Ly_m"] if direction == "EX" else f["Lx_m"]
        e_acc = ratio * perp
        f_c = dict(f)
        f_c["F_kN"] = fi
        f_c["e_accidental_m"] = e_acc
        f_c["M_torsion_accidental_kNm"] = fi * e_acc
        result.append(f_c)
    return result


def story_shears(floors: list[dict]) -> list[float]:
    shear = 0.0
    shears = []
    for f in reversed(floors):
        shear += f["F_kN"]
        shears.append(shear)
    return list(reversed(shears))


def export_unity(verification: dict, qg_kN_m2: float) -> dict:
    rows = []
    for b in verification["buildings"]:
        for fe, fy in zip(b["floors_EX"], b["floors_EY"]):
            rows.append(
                {
                    "building": fe["building"],
                    "floor": fe["floor"],
                    "z_m": fe["z_m"],
                    "area_m2": fe["area_m2"],
                    "wG_kN": fe["wG_kN"],
                    "wQ_kN": fe["wQ_kN"],
                    "w_seismic_kN": fe["w_seismic_kN"],
                    "mass_ton": fe["mass_ton"],
                    "cm_x": fe["cm_x"],
                    "cm_y": fe["cm_y"],
                    "Lx_m": fe["Lx_m"],
                    "Ly_m": fe["Ly_m"],
                    "F_EX_kN": fe["F_kN"],
                    "F_EY_kN": fy["F_kN"],
                    "story_shear_EX_kN": fe["story_shear_EX_kN"],
                    "story_shear_EY_kN": fy["story_shear_EY_kN"],
                    "e_accidental_m": fe["e_accidental_m"],
                    "M_torsion_EX_kNm": fe["M_torsion_accidental_kNm"],
                    "M_torsion_EY_kNm": fy["M_torsion_accidental_kNm"],
                }
            )
    export = {
        "units": "m, kN, ton",
        "qG_kN_m2": qg_kN_m2,
        "psi_Q": verification["parameters"]["psi_Q"],
        "base_shear_coefficient": verification["parameters"]["base_shear_coefficient"],
        "buildings": verification["buildings"],
        "floors": rows,
    }
    UNITY_EXPORT.parent.mkdir(parents=True, exist_ok=True)
    UNITY_EXPORT.write_text(json.dumps(export, indent=2, ensure_ascii=False), encoding="utf-8")
    return export


def run(parameters: dict, tributary_path: Path) -> dict:
    tributary = load_tributary(tributary_path)
    floors_by_building = build_floors(tributary, parameters)
    buildings_out = []

    for building in BUILDINGS:
        floors = floors_by_building[building]
        total_w = sum(f["w_seismic_kN"] for f in floors)
        v_ex, v_ey = base_shear(building, total_w, parameters)

        fx = distribute(v_ex, floors, parameters)
        fy = distribute(v_ey, floors, parameters)

        floors_ex = apply_case(floors, fx, "EX", parameters)
        floors_ey = apply_case(floors, fy, "EY", parameters)

        shear_ex = story_shears(floors_ex)
        shear_ey = story_shears(floors_ey)
        for fe, se in zip(floors_ex, shear_ex):
            fe["story_shear_EX_kN"] = se
        for fe, se in zip(floors_ey, shear_ey):
            fe["story_shear_EY_kN"] = se

        sum_fx = sum(fx)
        sum_fy = sum(fy)
        cm_building_x = sum(f["w_seismic_kN"] * f["cm_x"] for f in floors) / total_w
        cm_building_y = sum(f["w_seismic_kN"] * f["cm_y"] for f in floors) / total_w

        buildings_out.append(
            {
                "building": building,
                "total_w_seismic_kN": total_w,
                "total_mass_ton": total_w / parameters["g"],
                "cm_x_m": cm_building_x,
                "cm_y_m": cm_building_y,
                "V_EX_kN": v_ex,
                "V_EY_kN": v_ey,
                "sum_F_EX_kN": sum_fx,
                "sum_F_EY_kN": sum_fy,
                "check_EX": abs(v_ex - sum_fx) < 1e-6 if v_ex is not None else None,
                "check_EY": abs(v_ey - sum_fy) < 1e-6 if v_ey is not None else None,
                "deformed_shape_sense_EX": "traslacion +X con rotacion de piso (torsion accidental)",
                "deformed_shape_sense_EY": "traslacion +Y con rotacion de piso (torsion accidental)",
                "floors_EX": floors_ex,
                "floors_EY": floors_ey,
            }
        )

    verification = {
        "model": "P1L2 sismo pseudo-estatico EX/EY",
        "units": "m, kN, ton",
        "source_tributary": str(tributary_path),
        "parameters": parameters,
        "buildings": buildings_out,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "seismic_ex_ey_verification.json").write_text(
        json.dumps(verification, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    export_unity(verification, tributary["qG_kN_m2"])
    return verification


def print_results(verification: dict) -> None:
    print("P1L2 - sismo pseudo-estatico EX/EY OK")
    for b in verification["buildings"]:
        name = b["building"]
        print(f"  {name}: W = {b['total_w_seismic_kN']:.2f} kN, masa = {b['total_mass_ton']:.2f} ton")
        print(f"    CM global = ({b['cm_x_m']:.2f}, {b['cm_y_m']:.2f}) m")
        print(f"    V_EX = {b['V_EX_kN']:.2f} kN, V_EY = {b['V_EY_kN']:.2f} kN")
        print(f"    check sumF=V -> EX: {b['check_EX']}, EY: {b['check_EY']}")
        for row in b["floors_EX"]:
            print(
                f"      {row['building'][-1]} {row['floor']:>2}: z={row['z_m']:.2f} A={row['area_m2']:.2f} "
                f"W={row['w_seismic_kN']:.1f} m={row['mass_ton']:.1f} CM=({row['cm_x']:.2f},{row['cm_y']:.2f}) "
                f"F={row['F_kN']:.1f} kN Q={row['story_shear_EX_kN']:.1f} kN Mt={row['M_torsion_accidental_kNm']:.1f} kNm"
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sismo pseudo-estatico EX/EY para P1L2")
    parser.add_argument("--config", help="JSON con sobrescritura de parametros")
    parser.add_argument("--tributary", type=Path, default=URL_TRIBUTARY, help="JSON tributario")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    parameters = dict(DEFAULT_PARAMETERS)
    if args.config:
        override = json.loads(Path(args.config).read_text(encoding="utf-8"))
        parameters.update(override)
    verification = run(parameters, args.tributary)
    print_results(verification)


if __name__ == "__main__":
    main()