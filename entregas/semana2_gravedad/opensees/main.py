"""Pipeline principal: calculo de gravedad + QA + exportacion.

Uso:
    python main.py

Este script orquesta el pipeline completo:
  1. Recibe datos de entrada (losas, vigas, muros)
  2. Calcula carga gravitacional y areas tributarias
  3. Ejecuta verificaciones QA
  4. Exporta JSON para Unity
"""

from __future__ import annotations

from pathlib import Path

from carga_gravedad import (
    GravityLoadInput,
    GravityLoadOutput,
    calcular_cargas_gravitacionales,
)
from exportar_unity import exportar_gravedad_json
from qa_verificaciones import ejecutar_qa_completo


def ejecutar_pipeline(
    inp: GravityLoadInput,
    results_dir: Path,
    qa_required: bool = True,
) -> GravityLoadOutput:
    """Ejecuta el pipeline completo de carga gravitacional.

    Atributos:
        inp: Datos de entrada (losas, vigas, muros).
        results_dir: Directorio donde guardar resultados.
        qa_required: Si True, falla si QA no pasa.

    Retorna:
        GravityLoadOutput con resultados.

    Excepciones:
        RuntimeError: Si QA falla y qa_required es True.
    """
    # 1. Calcular
    output = calcular_cargas_gravitacionales(inp)

    # 2. QA
    report = ejecutar_qa_completo(inp, output)
    report.print_report()

    if qa_required and not report.passed:
        raise RuntimeError("QA fallo. Revisar reporte arriba.")

    # 3. Exportar
    json_path = results_dir / "tributarias.json"
    exportar_gravedad_json(output, json_path)
    print(f"JSON exportado a: {json_path}")

    # 4. Resumen
    _print_resumen(output)

    return output


def _print_resumen(output: GravityLoadOutput) -> None:
    print("\n--- Resumen por losa ---")
    for slab in output.slabs:
        print(
            f"  {slab.slab_id} (piso {slab.floor_id}): "
            f"A={slab.area_m2:.2f} m2, "
            f"t={slab.thickness_m*100:.0f} cm, "
            f"PP={slab.pp_kN_m2:.3f} kN/m2, "
            f"PM={slab.pm_kN_m2:.3f} kN/m2, "
            f"qG={slab.qG_kN_m2:.3f} kN/m2, "
            f"W={slab.total_load_N/1000:.3f} kN"
        )

    print("\n--- Resumen por viga ---")
    for beam in output.beams:
        print(
            f"  {beam.beam_id}: "
            f"L={beam.length_m:.3f} m, "
            f"Atrib={beam.A_tributaria_total_m2:.3f} m2, "
            f"qG={beam.qG_kN_m2:.3f} kN/m2, "
            f"P={beam.P_total_N/1000:.3f} kN, "
            f"w={beam.w_lineal_N_m/1000:.3f} kN/m"
        )

    if output.walls:
        print("\n--- Muros ---")
        for wall in output.walls:
            print(
                f"  {wall.wall_id}: "
                f"P={wall.axial_load_N/1000:.3f} kN"
            )


if __name__ == "__main__":
    print("Usar test_dos_panos.py para el ejemplo de prueba.")
    print("O importar ejecutar_pipeline desde otro script.")
