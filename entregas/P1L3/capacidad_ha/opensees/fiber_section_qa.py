"""Fiber Section y QA geometrico para una columna 70x70 de estudio.

Unidades SI en todo el modelo OpenSees:
- Longitud: m
- Fuerza: N
- Esfuerzo: Pa

La geometria 70x70 proviene del edificio real. La armadura y materiales son
hipotesis de laboratorio declaradas en datos/seccion_estudio.json.
"""

from __future__ import annotations

import math

import openseespy.opensees as ops

from section_model import (
    FIBER_SECTION_FIGURE_PATH,
    Bar,
    bar_area,
    build_bars_from_config,
    concrete_fiber_centers_from_config,
    create_fiber_section,
    load_config,
    pass_fail,
    plot_section,
    value,
)


def symmetry_pass(values: list[float], tol: float = 1.0e-10) -> bool:
    rounded = [round(v, 10) for v in values]
    return all(any(abs(other + value_) <= tol for other in rounded) for value_ in rounded)


def bars_inside_section(bars: list[Bar], b: float, h: float, diameter: float, tol: float = 1.0e-12) -> bool:
    radius = diameter / 2.0
    return all(abs(bar.y) + radius <= b / 2.0 + tol and abs(bar.z) + radius <= h / 2.0 + tol for bar in bars)


def bars_inside_valid_geometric_limits(bars: list[Bar], b: float, h: float, cover: float, diameter: float, tol: float = 1.0e-12) -> bool:
    radius = diameter / 2.0
    return all(abs(bar.y) + radius <= b / 2.0 - cover + tol and abs(bar.z) + radius <= h / 2.0 - cover + tol for bar in bars)


def main() -> None:
    config = load_config()
    b = float(value(config, "geometry", "b_m"))
    h = float(value(config, "geometry", "h_m"))
    cover = float(value(config, "geometry", "cover_m"))
    num_bars = int(value(config, "reinforcement", "num_bars"))
    diameter = float(value(config, "reinforcement", "bar_diameter_m"))
    nf_y = int(value(config, "fiber_discretization", "num_fibers_y"))
    nf_z = int(value(config, "fiber_discretization", "num_fibers_z"))

    bars = build_bars_from_config(config)
    concrete_fibers = concrete_fiber_centers_from_config(config)
    section_created = create_fiber_section(config, bars)
    plot_section(config, bars, concrete_fibers)

    ag = b * h
    as_total = sum(bar.area for bar in bars)
    rho = as_total / ag
    as_expected = 5890.0e-6
    rho_expected = 0.0120
    as_check = abs(as_total - as_expected) / as_expected <= 0.01
    rho_check = abs(rho - rho_expected) <= 0.0002
    symmetry_y = len(bars) == num_bars and symmetry_pass([bar.y for bar in bars])
    symmetry_z = len(bars) == num_bars and symmetry_pass([bar.z for bar in bars])
    inside_section = bars_inside_section(bars, b, h, diameter)
    inside_geometric_limits = bars_inside_valid_geometric_limits(bars, b, h, cover, diameter)
    valid_bar_coords = all(math.isfinite(bar.y) and math.isfinite(bar.z) and bar.area > 0.0 for bar in bars)

    print("=== FIBER SECTION QA ===")
    print(f"ID edificio: {value(config, 'building_column', 'json_id')}")
    print(f"Seccion: {b * 1000:.0f} x {h * 1000:.0f} mm")
    print(f"Origen geometria: {config['geometry']['b_m']['origin']} - {config['geometry']['b_m']['source']}")
    print(f"Armadura: {num_bars}Ø{diameter * 1000:.0f}")
    print(f"Origen armadura: {config['reinforcement']['num_bars']['origin']} - {config['reinforcement']['num_bars']['source']}")
    print()
    print(f"Ag = {ag:.6f} m2 = {ag * 1.0e6:.1f} mm2")
    print(f"Area barra = {bar_area(diameter):.8f} m2 = {bar_area(diameter) * 1.0e6:.1f} mm2")
    print(f"As = {as_total:.8f} m2 = {as_total * 1.0e6:.1f} mm2")
    print(f"rho = {rho:.6f} = {rho * 100.0:.3f} %")
    print(f"Check As ~= 5890 mm2: {pass_fail(as_check)}")
    print(f"Check rho ~= 1.20 %: {pass_fail(rho_check)}")
    print()
    print(f"Numero fibras hormigon = {len(concrete_fibers)} ({nf_y} x {nf_z})")
    print(f"Numero fibras acero = {len(bars)}")
    print()
    print(f"Simetria Y: {pass_fail(symmetry_y)}")
    print(f"Simetria Z: {pass_fail(symmetry_z)}")
    print(f"Barras dentro de seccion: {pass_fail(inside_section)}")
    print(f"Barras dentro de limites geometricos validos: {pass_fail(inside_geometric_limits)}")
    print(f"Coordenadas de barras validas: {pass_fail(valid_bar_coords)}")
    print(f"Fiber Section creada: {pass_fail(section_created)}")
    print()
    print(f"Figura: {FIBER_SECTION_FIGURE_PATH}")

    ops.wipe()


if __name__ == "__main__":
    main()
