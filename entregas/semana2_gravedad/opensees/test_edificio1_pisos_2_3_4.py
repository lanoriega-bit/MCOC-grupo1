"""Tests del pre-QA Edificio 1 para pisos 2, 3 y 4.

Valida que las observaciones reales quedan trazables y que el pipeline genera
StructuralModelInput una vez resueltas todas las ambiguedades de centroide/eje.
"""

from __future__ import annotations

from collections import Counter
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from adaptador_edificio1_cad import PENDING, RESOLVED  # noqa: E402
from catalogo_cargas_edificio1 import construir_catalogo_edificio1  # noqa: E402
from edificio1_pisos_2_3_4 import (  # noqa: E402
    PANEL_OBSERVATIONS,
    RealDataOutput,
    construir_datos_reales_pisos_2_3_4,
    report_to_dict,
)


PASS = 0
FAIL = 0
_OUTPUT: RealDataOutput | None = None


def report(test_name: str, condition: bool, detail: str = "") -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {test_name}" + (f" - {detail}" if detail else ""))
    else:
        FAIL += 1
        print(f"  [FAIL] {test_name}" + (f" - {detail}" if detail else ""))


def separator(title: str) -> None:
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def _build_output() -> RealDataOutput:
    global _OUTPUT
    if _OUTPUT is None:
        repo = Path(__file__).resolve().parents[3]
        _OUTPUT = construir_datos_reales_pisos_2_3_4("origin/main", repo)
    return _OUTPUT


def test_A_observaciones_trazables() -> None:
    separator("A. Observaciones trazables")
    floor_counts = Counter(obs.floor for obs in PANEL_OBSERVATIONS)
    report("74 paneles observados", len(PANEL_OBSERVATIONS) == 74)
    report("Piso 2 tiene 22 paneles", floor_counts["2"] == 22)
    report("Piso 3 tiene 25 paneles", floor_counts["3"] == 25)
    report("Piso 4 tiene 27 paneles", floor_counts["4"] == 27)
    report("source_label unicos", len({obs.source_label for obs in PANEL_OBSERVATIONS}) == 74)
    report("slab_id unicos", len({obs.slab_id for obs in PANEL_OBSERVATIONS}) == 74)


def test_B_espesores_especiales() -> None:
    separator("B. Espesores especiales")
    p3 = {obs.slab_number: obs.thickness_cm for obs in PANEL_OBSERVATIONS if obs.floor == "3"}
    p4 = {obs.slab_number: obs.thickness_cm for obs in PANEL_OBSERVATIONS if obs.floor == "4"}
    report("P3 311/312/322/323 e=12", all(p3[n] == 12 for n in [311, 312, 322, 323]))
    report("P3 324 queda e=15", p3[324] == 15)
    report("P4 415/416/425/426 e=12", all(p4[n] == 12 for n in [415, 416, 425, 426]))


def test_C_referencias_catalogo() -> None:
    separator("C. Referencias al catalogo")
    catalog = construir_catalogo_edificio1()
    load_ids = {obs.load_type_id for obs in PANEL_OBSERVATIONS if obs.load_type_id is not None}
    pending_without_load = [obs for obs in PANEL_OBSERVATIONS if obs.load_status == PENDING and obs.load_type_id is None]
    resolved_with_load = [obs for obs in PANEL_OBSERVATIONS if obs.load_status == RESOLVED and obs.load_type_id is not None]
    report("load_type_id existen", load_ids.issubset(catalog.surface_loads))
    report("observaciones pendientes no inventan carga", len(pending_without_load) == sum(1 for obs in PANEL_OBSERVATIONS if obs.load_status == PENDING))
    report("observaciones resueltas tienen carga", len(resolved_with_load) == sum(1 for obs in PANEL_OBSERVATIONS if obs.load_status == RESOLVED))


def test_D_pre_qa_genera_modelo() -> None:
    separator("D. Pre-QA genera StructuralModelInput")
    output = _build_output()
    report("gestiona StructuralModelInput", output.model is not None)
    report("gravity_ready true", output.report.gravity_ready)
    report("64 losas/bahia tras colapso (17 sub-paneles de 74 -> 7 bahias)", output.report.counts["observed_panels"] == 64)
    report("64 paneles/bahia resueltos", output.report.counts["resolved_panels"] == 64)
    report("64 losas estructurales generadas", output.report.counts["structural_model_slabs"] == 64)
    report("180 vigas estructurales generadas", output.report.counts["structural_model_beams"] == 180)
    report("pisos 2/3/4 con paneles resueltos", all(output.report.floor_status[f]["resolved_panels"] == output.report.floor_status[f]["observed_panels"] for f in ["2", "3", "4"]))
    bay_members = sum(1 for p in output.report.panels if p.member_slab_ids)
    report(f"7 sub-paneles agrupados en bahias (metadata)", bay_members == 7)


def test_E_reporte_serializable_y_pendientes() -> None:
    separator("E. Reporte serializable y pendientes")
    output = _build_output()
    payload = report_to_dict(output.report)
    json.dumps(payload)
    pending_by_type = Counter(item["item_type"] for item in payload["pending"])
    report("dict serializable", isinstance(payload, dict))
    report("sin pendientes de panel", pending_by_type["panel_losa"] == 0)
    report("pendientes de openings por piso", pending_by_type["openings_piso"] == 3)
    report("notas declaran no OCR", any("No se usa OCR" in note for note in payload["notes"]))


def main() -> None:
    print("\n" + "=" * 70)
    print("  VALIDACION PRE-QA EDIFICIO 1 PISOS 2, 3 Y 4")
    print("=" * 70)
    test_A_observaciones_trazables()
    test_B_espesores_especiales()
    test_C_referencias_catalogo()
    test_D_pre_qa_genera_modelo()
    test_E_reporte_serializable_y_pendientes()
    print(f"\n{'='*70}")
    print(f"  RESUMEN PRE-QA:  {PASS} PASARON,  {FAIL} FALLARON")
    print(f"{'='*70}\n")
    if FAIL > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
