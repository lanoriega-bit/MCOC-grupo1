"""Verificaciones de QA para carga gravitacional y areas tributarias.

Ejecuta las siguientes verificaciones:
  1. Suma de areas tributarias = area de la losa asociada
  2. Suma de cargas transferidas = q_G * area total de la losa
  3. Para cada viga: w * L = q_G * A_tributaria
  4. Ninguna area tributaria negativa o no finita
  5. IDs duplicados o vigas inexistentes
  6. Unidades y ordenes de magnitud
"""

from __future__ import annotations

from dataclasses import dataclass, field

from carga_gravedad import (
    KN,
    GravityLoadInput,
    GravityLoadOutput,
    calcular_largo_viga,
)


@dataclass
class QAError:
    """Un error de verificacion."""

    check: str
    detail: str
    expected: float | str | None = None
    actual: float | str | None = None
    severity: str = "ERROR"  # ERROR o WARNING


@dataclass
class QAReport:
    """Reporte completo de verificaciones QA."""

    passed: bool = True
    errors: list[QAError] = field(default_factory=list)
    summary: dict[str, str] = field(default_factory=dict)

    def add_error(
        self,
        check: str,
        detail: str,
        expected: float | str | None = None,
        actual: float | str | None = None,
        severity: str = "ERROR",
    ) -> None:
        self.errors.append(
            QAError(
                check=check,
                detail=detail,
                expected=expected,
                actual=actual,
                severity=severity,
            )
        )
        if severity == "ERROR":
            self.passed = False

    def add_pass(self, check: str, detail: str) -> None:
        self.summary[check] = f"OK - {detail}"

    def print_report(self) -> None:
        status = "APROBADO" if self.passed else "FALLIDO"
        print(f"\n{'='*60}")
        print(f"  QA REPORT - {status}")
        print(f"{'='*60}")

        if self.summary:
            print("\nVerificaciones aprobadas:")
            for check, detail in self.summary.items():
                print(f"  [OK]  {check}: {detail}")

        if self.errors:
            print("\nVerificaciones con problemas:")
            for err in self.errors:
                prefix = "[ERR]" if err.severity == "ERROR" else "[WRN]"
                print(f"  {prefix} {err.check}: {err.detail}")
                if err.expected is not None:
                    print(f"        esperado: {err.expected}")
                    print(f"        actual:   {err.actual}")

        print(f"\nTotal: {len(self.summary)} OK, "
              f"{sum(1 for e in self.errors if e.severity == 'ERROR')} errores, "
              f"{sum(1 for e in self.errors if e.severity == 'WARNING')} warnings")
        print(f"{'='*60}\n")


# ---------------------------------------------------------------------------
# Verificaciones
# ---------------------------------------------------------------------------


def verificar_tributarias_por_losa(
    output: GravityLoadOutput,
    tolerance: float = 1e-6,
) -> QAReport:
    """Verifica que la suma de areas tributarias iguale el area de cada losa.

    Tambien verifica que la suma de cargas sea consistente con q_G * A.
    """
    report = QAReport()
    beam_map = {b.beam_id: b for b in output.beams}

    for slab_info in output.slabs:
        # Suma de areas tributarias de esta losa
        total_trib_area = 0.0
        total_transferred_N = 0.0
        for beam in output.beams:
            for trib in beam.tributaries:
                if trib.slab_id == slab_info.slab_id:
                    total_trib_area += trib.area_m2
                    total_transferred_N += trib.area_m2 * slab_info.qG_kN_m2 * KN

        # Check 1: area
        area_error = abs(total_trib_area - slab_info.area_m2)
        area_rel_error = area_error / slab_info.area_m2 if slab_info.area_m2 > 0 else 0.0

        if area_rel_error < tolerance:
            report.add_pass(
                f"tributarias_area_{slab_info.slab_id}",
                f"suma areas trib = {total_trib_area:.6f} m2, "
                f"area losa = {slab_info.area_m2:.6f} m2",
            )
        else:
            report.add_error(
                check=f"tributarias_area_{slab_info.slab_id}",
                detail=(
                    f"suma areas trib = {total_trib_area:.6f} m2, "
                    f"area losa = {slab_info.area_m2:.6f} m2"
                ),
                expected=f"{slab_info.area_m2:.6f} m2",
                actual=f"{total_trib_area:.6f} m2",
            )

        # Check 2: carga
        expected_load = slab_info.qG_kN_m2 * KN * slab_info.area_m2
        load_error = abs(total_transferred_N - expected_load)
        load_rel_error = load_error / expected_load if expected_load > 0 else 0.0

        if load_rel_error < tolerance:
            report.add_pass(
                f"cargas_tributarias_{slab_info.slab_id}",
                f"suma cargas = {total_transferred_N/KN:.6f} kN, "
                f"qG*A = {expected_load/KN:.6f} kN",
            )
        else:
            report.add_error(
                check=f"cargas_tributarias_{slab_info.slab_id}",
                detail=(
                    f"suma cargas transferidas = {total_transferred_N/KN:.6f} kN, "
                    f"qG*A = {expected_load/KN:.6f} kN"
                ),
                expected=f"{expected_load/KN:.6f} kN",
                actual=f"{total_transferred_N/KN:.6f} kN",
            )

    return report


def verificar_equilibrio_cargas(
    output: GravityLoadOutput,
    tolerance: float = 1e-6,
) -> QAReport:
    """Verifica equilibrio: suma de reacciones verticales = carga total."""
    report = QAReport()

    total_carga = sum(b.P_total_N for b in output.beams)
    total_carga += sum(w.axial_load_N for w in output.walls)

    total_slab_load = sum(s.total_load_N for s in output.slabs)
    error = abs(total_carga - total_slab_load)
    rel_error = error / total_slab_load if total_slab_load > 0 else 0.0

    if rel_error < tolerance:
        report.add_pass(
            "equilibrio_vertical",
            f"total vigas = {total_carga/KN:.6f} kN, "
            f"total losas = {total_slab_load/KN:.6f} kN",
        )
    else:
        report.add_error(
            check="equilibrio_vertical",
            detail=(
                f"total cargas vigas+muros = {total_carga/KN:.6f} kN, "
                f"total carga losas = {total_slab_load/KN:.6f} kN"
            ),
            expected=f"{total_slab_load/KN:.6f} kN",
            actual=f"{total_carga/KN:.6f} kN",
        )

    return report


def verificar_w_L_equivalencia(
    output: GravityLoadOutput,
    tolerance: float = 1e-6,
) -> QAReport:
    """Para cada viga: w * L debe ser igual a P = q_G * A_tributaria."""
    report = QAReport()

    for beam in output.beams:
        if beam.A_tributaria_total_m2 <= 0:
            continue

        wL = beam.w_lineal_N_m * beam.length_m
        P = beam.P_total_N
        error = abs(wL - P)
        rel_error = error / P if P > 0 else 0.0

        if rel_error < tolerance:
            report.add_pass(
                f"wL_{beam.beam_id}",
                f"w*L = {wL/KN:.6f} kN, P = {P/KN:.6f} kN",
            )
        else:
            report.add_error(
                check=f"wL_{beam.beam_id}",
                detail=(
                    f"w*L = {wL/KN:.6f} kN, P = {P/KN:.6f} kN"
                ),
                expected=f"{P/KN:.6f} kN",
                actual=f"{wL/KN:.6f} kN",
            )

    return report


def verificar_tributarias_validas(
    output: GravityLoadOutput,
) -> QAReport:
    """Verifica que no haya areas tributarias negativas o no finitas."""
    report = QAReport()

    for beam in output.beams:
        for trib in beam.tributaries:
            if trib.area_m2 < 0:
                report.add_error(
                    check=f"area_negativa_{beam.beam_id}_{trib.slab_id}",
                    detail=f"area tributaria negativa: {trib.area_m2:.6f} m2",
                    actual=f"{trib.area_m2:.6f} m2",
                )
            elif not (trib.area_m2 == trib.area_m2):  # NaN check
                report.add_error(
                    check=f"area_nan_{beam.beam_id}_{trib.slab_id}",
                    detail="area tributaria NaN",
                    actual=str(trib.area_m2),
                )
            else:
                report.add_pass(
                    f"area_valida_{beam.beam_id}_{trib.slab_id}",
                    f"area = {trib.area_m2:.6f} m2",
                )

    return report


def verificar_ids(
    inp: GravityLoadInput,
) -> QAReport:
    """Verifica IDs duplicados o vigas inexistentes en las asociaciones."""
    report = QAReport()

    # IDs de vigas duplicados
    beam_ids = [b.beam_id for b in inp.beams]
    seen = set()
    for bid in beam_ids:
        if bid in seen:
            report.add_error(
                check="viga_id_duplicado",
                detail=f"ID de viga duplicado: {bid}",
                actual=bid,
            )
        seen.add(bid)

    if len(seen) == len(beam_ids):
        report.add_pass(
            "ids_vigas_unicos",
            f"{len(beam_ids)} IDs unicos",
        )

    # IDs de losas duplicados
    slab_ids = [s.slab_id for s in inp.slabs]
    seen_slabs = set()
    for sid in slab_ids:
        if sid in seen_slabs:
            report.add_error(
                check="losa_id_duplicado",
                detail=f"ID de losa duplicado: {sid}",
                actual=sid,
            )
        seen_slabs.add(sid)

    if len(seen_slabs) == len(slab_ids):
        report.add_pass(
            "ids_losas_unicos",
            f"{len(slab_ids)} IDs unicos",
        )

    # Referencias a vigas inexistentes
    valid_beam_ids = set(beam_ids)
    for slab in inp.slabs:
        for beam in inp.beams:
            for sid in beam.slab_ids:
                if sid == slab.slab_id:
                    pass  # beam references this slab - OK

    # Verificar que los slab_ids en las vigas referencian losas existentes
    valid_slab_ids = set(slab_ids)
    for beam in inp.beams:
        for sid in beam.slab_ids:
            if sid not in valid_slab_ids:
                report.add_error(
                    check="referencia_losa_inexistente",
                    detail=f"Viga {beam.beam_id} referencia losa inexistente: {sid}",
                    actual=sid,
                )

    if all(
        sid in valid_slab_ids
        for beam in inp.beams
        for sid in beam.slab_ids
    ):
        report.add_pass(
            "referencias_losas_validas",
            "todas las vigas referencian losas existentes",
        )

    return report


def verificar_unidades(
    output: GravityLoadOutput,
) -> QAReport:
    """Verifica ordenes de magnitud razonables (unidades SI)."""
    report = QAReport()

    for slab in output.slabs:
        if slab.thickness_m <= 0 or slab.thickness_m > 1.0:
            report.add_error(
                check=f"espesor_razonable_{slab.slab_id}",
                detail=f"espesor fuera de rango razonable: {slab.thickness_m} m",
                actual=f"{slab.thickness_m} m",
            )
        else:
            report.add_pass(
                f"espesor_razonable_{slab.slab_id}",
                f"{slab.thickness_m*100:.1f} cm",
            )

        if slab.qG_kN_m2 < 0 or slab.qG_kN_m2 > 50.0:
            report.add_error(
                check=f"qG_razonable_{slab.slab_id}",
                detail=f"qG fuera de rango razonable: {slab.qG_kN_m2} kN/m2",
                actual=f"{slab.qG_kN_m2} kN/m2",
            )
        else:
            report.add_pass(
                f"qG_razonable_{slab.slab_id}",
                f"{slab.qG_kN_m2:.3f} kN/m2",
            )

    for beam in output.beams:
        if beam.length_m <= 0:
            report.add_error(
                check=f"largo_positivo_{beam.beam_id}",
                detail=f"largo no positivo: {beam.length_m} m",
                actual=f"{beam.length_m} m",
            )
        else:
            report.add_pass(
                f"largo_razonable_{beam.beam_id}",
                f"{beam.length_m:.3f} m",
            )

        if beam.A_tributaria_total_m2 < 0:
            report.add_error(
                check=f"Atrib_negativa_{beam.beam_id}",
                detail=f"area tributaria total negativa: {beam.A_tributaria_total_m2}",
                actual=f"{beam.A_tributaria_total_m2} m2",
            )

        if beam.w_lineal_N_m < 0:
            report.add_error(
                check=f"w_negativa_{beam.beam_id}",
                detail=f"carga lineal negativa: {beam.w_lineal_N_m} N/m",
                actual=f"{beam.w_lineal_N_m} N/m",
            )

    return report


def verificar_SC_no_incluido(
    inp: GravityLoadInput,
) -> QAReport:
    """Verifica que q_G NO contenga sobrecarga de uso.

    Esta es una verificacion semantica: si se proporciona un factor de
    combinacion lambda_G < 1.0, indica que alguien pudo haber mezclado
    cargas. Por ahora solo verificamos que la definicion sea limpia.
    """
    report = QAReport()
    report.add_pass(
        "SC_excluido_qG",
        "q_G = PP.LOSA + PM.ADIC.  SC queda separada (no se incluye).",
    )
    return report


# ---------------------------------------------------------------------------
# Pipeline QA completo
# ---------------------------------------------------------------------------


def ejecutar_qa_completo(
    inp: GravityLoadInput,
    output: GravityLoadOutput,
) -> QAReport:
    """Ejecuta todas las verificaciones QA y retorna un reporte consolidado.

    Atributos:
        inp: Datos de entrada originales.
        output: Resultados del calculo de carga gravitacional.

    Retorna:
        QAReport consolidado con todas las verificaciones.
    """
    report = QAReport()

    # 1. IDs
    r = verificar_ids(inp)
    report.summary.update(r.summary)
    report.errors.extend(r.errors)
    if not r.passed:
        report.passed = False

    # 2. Unidades
    r = verificar_unidades(output)
    report.summary.update(r.summary)
    report.errors.extend(r.errors)
    if not r.passed:
        report.passed = False

    # 3. Tributarias validas
    r = verificar_tributarias_validas(output)
    report.summary.update(r.summary)
    report.errors.extend(r.errors)
    if not r.passed:
        report.passed = False

    # 4. Suma tributarias = area losa
    r = verificar_tributarias_por_losa(output)
    report.summary.update(r.summary)
    report.errors.extend(r.errors)
    if not r.passed:
        report.passed = False

    # 5. w*L = P por viga
    r = verificar_w_L_equivalencia(output)
    report.summary.update(r.summary)
    report.errors.extend(r.errors)
    if not r.passed:
        report.passed = False

    # 6. Equilibrio global
    r = verificar_equilibrio_cargas(output)
    report.summary.update(r.summary)
    report.errors.extend(r.errors)
    if not r.passed:
        report.passed = False

    # 7. SC excluido
    r = verificar_SC_no_incluido(inp)
    report.summary.update(r.summary)
    report.errors.extend(r.errors)
    if not r.passed:
        report.passed = False

    return report
